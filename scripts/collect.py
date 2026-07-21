"""Daily news collection script.

Reads RSS feeds listed in feeds.yaml, keeps only articles published within
the last N days (DAYS_BACK, default 2), deduplicates against a repo-committed
state file (data/seen_urls.json), archives each day's newly collected
articles under data/archive/YYYY-MM-DD.json, and pushes each new article as
a page into a Notion database via the Notion REST API.

If the NOTION_TOKEN environment variable is not set, the script runs in
"dry-run" mode: it still parses feeds, dedupes, and writes the local state
files, but skips the actual Notion API calls and instead prints what it
would have sent. This makes local testing possible without credentials.

No LLM/AI is used anywhere in this script.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import feedparser
import requests
import yaml

# --- Configuration -----------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
FEEDS_FILE = REPO_ROOT / "feeds.yaml"
SEEN_URLS_FILE = REPO_ROOT / "data" / "seen_urls.json"
ARCHIVE_DIR = REPO_ROOT / "data" / "archive"

NOTION_API_VERSION = "2022-06-28"
NOTION_PAGES_URL = "https://api.notion.com/v1/pages"
DEFAULT_DATABASE_ID = "72e48124a9fc49819fff9dcc69c9c61b"

MAX_SEEN_URLS = 500

VALID_TOPICS = {"AI 시장", "AI 활용", "로보틱스", "바이오", "유튜브·SNS"}


# --- Feed loading & parsing ----------------------------------------------


def load_feeds() -> list[dict]:
    """Load the list of feed configs from feeds.yaml."""
    with FEEDS_FILE.open("r", encoding="utf-8") as f:
        feeds = yaml.safe_load(f) or []

    for feed in feeds:
        if feed.get("topic") not in VALID_TOPICS:
            raise ValueError(
                f"Invalid topic '{feed.get('topic')}' for feed {feed.get('url')}. "
                f"Must be one of {sorted(VALID_TOPICS)}."
            )
    return feeds


def entry_published_date(entry) -> str:
    """Return the entry's published date as YYYY-MM-DD, falling back to today."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6]).strftime("%Y-%m-%d")
    return date.today().isoformat()


def fetch_articles(feed_config: dict, cutoff_date: date) -> list[dict]:
    """Parse a single feed and return articles published on/after cutoff_date."""
    parsed_feed = feedparser.parse(feed_config["url"])
    articles = []

    for entry in parsed_feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        published = entry_published_date(entry)
        published_dt = datetime.strptime(published, "%Y-%m-%d").date()
        if published_dt < cutoff_date:
            continue

        articles.append(
            {
                "title": title,
                "link": link,
                "source": feed_config["source"],
                "topic": feed_config["topic"],
                "published": published,
            }
        )

    return articles


# --- Deduplication state --------------------------------------------------


def load_seen_urls() -> list[str]:
    if not SEEN_URLS_FILE.exists():
        return []
    try:
        with SEEN_URLS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_seen_urls(seen_urls: list[str]) -> None:
    # Bound growth: keep only the most recently added entries.
    trimmed = seen_urls[-MAX_SEEN_URLS:]
    SEEN_URLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SEEN_URLS_FILE.open("w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


# --- Archiving -------------------------------------------------------------


def append_to_archive(articles: list[dict], run_date: str) -> None:
    """Append this run's new articles to today's archive file."""
    if not articles:
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_file = ARCHIVE_DIR / f"{run_date}.json"

    existing = []
    if archive_file.exists():
        try:
            with archive_file.open("r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing = []

    existing.extend(articles)

    with archive_file.open("w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


# --- Notion integration ------------------------------------------------


def build_notion_payload(article: dict, database_id: str, collected_date: str) -> dict:
    return {
        "parent": {"database_id": database_id},
        "properties": {
            "제목": {"title": [{"text": {"content": article["title"]}}]},
            "출처": {"select": {"name": article["source"]}},
            "주제": {"select": {"name": article["topic"]}},
            "발행일": {"date": {"start": article["published"]}},
            "링크": {"url": article["link"]},
            "수집일": {"date": {"start": collected_date}},
        },
    }


def push_to_notion(article: dict, token: str, database_id: str, collected_date: str) -> bool:
    """POST a single article to Notion. Returns True on success."""
    payload = build_notion_payload(article, database_id, collected_date)
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(NOTION_PAGES_URL, headers=headers, json=payload, timeout=15)
    except requests.RequestException as exc:
        print(f"  [ERROR] Notion request failed for '{article['title']}': {exc}")
        return False

    if response.status_code != 200:
        print(
            f"  [ERROR] Notion API returned {response.status_code} for "
            f"'{article['title']}': {response.text[:300]}"
        )
        return False

    return True


# --- Main pipeline -------------------------------------------------------


def main() -> None:
    days_back = int(os.environ.get("DAYS_BACK", "2"))
    notion_token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID", DEFAULT_DATABASE_ID)
    dry_run = not notion_token

    today = date.today()
    cutoff_date = today - timedelta(days=days_back)
    collected_date = today.isoformat()

    if dry_run:
        print("[DRY RUN] NOTION_TOKEN not set - Notion API calls will be skipped.\n")

    feeds = load_feeds()
    seen_urls = load_seen_urls()
    seen_urls_set = set(seen_urls)

    new_articles: list[dict] = []
    skipped_count = 0
    error_count = 0
    feeds_processed = 0

    for feed_config in feeds:
        print(f"Fetching: {feed_config['source']} ({feed_config['url']})")
        try:
            articles = fetch_articles(feed_config, cutoff_date)
        except Exception as exc:  # noqa: BLE001 - keep the run going on any parse error
            print(f"  [ERROR] Failed to fetch/parse feed: {exc}")
            error_count += 1
            continue

        feeds_processed += 1

        for article in articles:
            if article["link"] in seen_urls_set:
                skipped_count += 1
                continue

            if dry_run:
                print(f"  [WOULD ADD] {article['title']} ({article['link']})")
            else:
                success = push_to_notion(article, notion_token, database_id, collected_date)
                if not success:
                    error_count += 1
                    continue
                print(f"  [ADDED] {article['title']}")

            new_articles.append(article)
            seen_urls_set.add(article["link"])
            seen_urls.append(article["link"])

    save_seen_urls(seen_urls)
    append_to_archive(new_articles, collected_date)

    print("\n--- Summary ---")
    print(f"Feeds processed: {feeds_processed}/{len(feeds)}")
    print(f"New articles added: {len(new_articles)}")
    print(f"Duplicates skipped: {skipped_count}")
    print(f"Errors: {error_count}")
    if dry_run:
        print("Mode: DRY RUN (set NOTION_TOKEN to actually push to Notion)")


if __name__ == "__main__":
    main()
