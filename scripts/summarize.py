"""Daily digest script (stage 2 of 2).

Reads today's raw archive (data/archive/YYYY-MM-DD.json, produced by
collect.py), groups the candidate articles by topic, and for each topic
asks Claude Haiku to pick the single most important story and write a
short Korean summary grounded only in the provided title/snippet. The five
picks are assembled into one consolidated digest and pushed as a single
page into the "뉴스 브리핑" Notion database (one page per day, not one row
per article) via the Notion REST API.

This is the only step in the pipeline that spends LLM credits, and it runs
once per day as a small batch (5 short calls), which is why a cheap model
(Haiku) is used here instead of anywhere in collect.py.

If ANTHROPIC_API_KEY is unset, runs in "dry-run" mode: picks the first
candidate per topic without AI judgment or summarization, and labels it
clearly as such. If NOTION_TOKEN is unset, prints the digest instead of
pushing to Notion.
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = REPO_ROOT / "data" / "archive"

NOTION_API_VERSION = "2022-06-28"
NOTION_PAGES_URL = "https://api.notion.com/v1/pages"
DEFAULT_BRIEF_DATABASE_ID = "d3c78e13b47d4b9e8d99acabd700d929"

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
SUMMARIZER_MODEL = "claude-haiku-4-5-20251001"

# Topic order and display labels, matching feeds.yaml's five categories.
TOPIC_DISPLAY = [
    ("AI 시장", "🤖"),
    ("AI 활용", "💡"),
    ("로보틱스", "🦾"),
    ("바이오", "🧬"),
    ("유튜브·SNS", "📱"),
]


# --- Loading today's candidates -------------------------------------------


def load_archive(run_date: str) -> list[dict]:
    archive_file = ARCHIVE_DIR / f"{run_date}.json"
    if not archive_file.exists():
        return []
    with archive_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def group_by_topic(articles: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {topic: [] for topic, _ in TOPIC_DISPLAY}
    for article in articles:
        if article.get("topic") in grouped:
            grouped[article["topic"]].append(article)
    return grouped


# --- Picking + summarizing the top story per topic ------------------------


def build_prompt(topic: str, candidates: list[dict]) -> str:
    candidate_lines = []
    for i, c in enumerate(candidates, 1):
        candidate_lines.append(
            f"{i}. 제목: {c['title']}\n   출처: {c['source']}\n"
            f"   내용 일부: {c.get('snippet', '') or '(요약 없음)'}\n   링크: {c['link']}"
        )
    candidates_block = "\n".join(candidate_lines)

    return f"""다음은 '{topic}' 분야의 오늘 수집된 후보 기사 목록이다.

{candidates_block}

이 중에서 가장 중요도(파급력·화제성·업계에 미치는 영향)가 높은 기사 딱 1건을 골라라.
그리고 그 기사의 핵심 내용을 한국어 2~3문장으로, 제공된 제목과 내용 일부에 근거해서만
간결하게 요약해라. 없는 사실을 지어내지 마라.

다음 JSON 형식으로만 답하라 (다른 텍스트 없이):
{{"title": "<선택한 기사의 원제목>", "summary": "<2~3문장 한국어 요약>", "source": "<출처>", "link": "<링크>"}}
"""


def call_haiku(prompt: str, api_key: str) -> dict | None:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    body = {
        "model": SUMMARIZER_MODEL,
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=body, timeout=30)
    except requests.RequestException as exc:
        print(f"  [ERROR] Anthropic request failed: {exc}")
        return None

    if response.status_code != 200:
        print(f"  [ERROR] Anthropic API returned {response.status_code}: {response.text[:300]}")
        return None

    try:
        text = response.json()["content"][0]["text"]
        return json.loads(text)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        print(f"  [ERROR] Could not parse Haiku response: {exc}")
        return None


def pick_and_summarize(topic: str, candidates: list[dict], api_key: str | None) -> dict | None:
    if not candidates:
        return None

    if not api_key:
        top = candidates[0]
        return {
            "title": top["title"],
            "summary": f"[dry-run: AI 요약 없음] {top.get('snippet', '')[:200]}",
            "source": top["source"],
            "link": top["link"],
        }

    prompt = build_prompt(topic, candidates)
    picked = call_haiku(prompt, api_key)
    if picked is None:
        # Fall back to the first candidate rather than dropping the topic.
        top = candidates[0]
        return {
            "title": top["title"],
            "summary": f"[요약 실패, 원문 확인 필요] {top.get('snippet', '')[:200]}",
            "source": top["source"],
            "link": top["link"],
        }
    return picked


# --- Building the Notion page -------------------------------------------


def text_block(content: str, bold: bool = False, link: str | None = None) -> dict:
    rich_text = {"type": "text", "text": {"content": content}}
    if link:
        rich_text["text"]["link"] = {"url": link}
    if bold:
        rich_text["annotations"] = {"bold": True}
    return rich_text


def build_children_blocks(picks: dict[str, dict | None], run_date: str) -> list[dict]:
    blocks: list[dict] = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [text_block(f"{run_date} · 분야별 핵심 뉴스 1건씩 · 자동 요약")]
            },
        },
        {"object": "block", "type": "divider", "divider": {}},
    ]

    for topic, emoji in TOPIC_DISPLAY:
        pick = picks.get(topic)
        blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [text_block(f"{emoji} {topic}")]},
            }
        )

        if pick is None:
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [text_block("오늘 수집된 기사가 없습니다.")]},
                }
            )
            continue

        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [text_block(pick["title"], bold=True)]},
            }
        )
        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [text_block(pick["summary"])]},
            }
        )
        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        text_block(f"출처: {pick['source']} · "),
                        text_block("원문 보기", link=pick["link"]),
                    ]
                },
            }
        )
        blocks.append({"object": "block", "type": "divider", "divider": {}})

    return blocks


def push_digest_to_notion(
    picks: dict[str, dict | None], run_date: str, token: str, database_id: str
) -> bool:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "제목": {"title": [{"text": {"content": f"{run_date} 뉴스 브리핑"}}]},
            "날짜": {"date": {"start": run_date}},
        },
        "children": build_children_blocks(picks, run_date),
    }

    try:
        response = requests.post(NOTION_PAGES_URL, headers=headers, json=payload, timeout=15)
    except requests.RequestException as exc:
        print(f"[ERROR] Notion request failed: {exc}")
        return False

    if response.status_code != 200:
        print(f"[ERROR] Notion API returned {response.status_code}: {response.text[:300]}")
        return False

    return True


def print_digest(picks: dict[str, dict | None], run_date: str) -> None:
    print(f"\n=== {run_date} 뉴스 브리핑 (dry-run 미리보기) ===\n")
    for topic, emoji in TOPIC_DISPLAY:
        pick = picks.get(topic)
        print(f"{emoji} {topic}")
        if pick is None:
            print("  (오늘 수집된 기사 없음)\n")
            continue
        print(f"  {pick['title']}")
        print(f"  {pick['summary']}")
        print(f"  출처: {pick['source']} · {pick['link']}\n")


# --- Main ------------------------------------------------------------------


def main() -> None:
    run_date = os.environ.get("DIGEST_DATE", date.today().isoformat())
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    notion_token = os.environ.get("NOTION_TOKEN")
    brief_database_id = os.environ.get("NOTION_BRIEF_DATABASE_ID", DEFAULT_BRIEF_DATABASE_ID)

    articles = load_archive(run_date)
    if not articles:
        print(f"No archived articles found for {run_date} (data/archive/{run_date}.json).")
        return

    grouped = group_by_topic(articles)

    picks: dict[str, dict | None] = {}
    for topic, _ in TOPIC_DISPLAY:
        candidates = grouped.get(topic, [])
        print(f"Summarizing topic: {topic} ({len(candidates)} candidates)")
        picks[topic] = pick_and_summarize(topic, candidates, anthropic_key)

    if not anthropic_key:
        print("\n[DRY RUN] ANTHROPIC_API_KEY not set - skipping AI selection/summary.")

    if notion_token:
        success = push_digest_to_notion(picks, run_date, notion_token, brief_database_id)
        print("Digest pushed to Notion." if success else "Failed to push digest to Notion.")
    else:
        print("\n[DRY RUN] NOTION_TOKEN not set - printing digest instead of pushing.")
        print_digest(picks, run_date)


if __name__ == "__main__":
    main()
