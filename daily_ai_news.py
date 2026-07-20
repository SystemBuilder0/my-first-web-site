"""매일 전날 AI 최신 동향 뉴스를 모아 핵심만 요약해 이메일로 보내는 스크립트.

GitHub Actions에서 매일 아침 8시(KST)에 실행되도록 스케줄링되어 있다.
(.github/workflows/daily-ai-news.yml 참고)
"""

import os
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

import feedparser

FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "https://blog.google/technology/ai/rss/",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
]

LOOKBACK_HOURS = int(os.environ.get("LOOKBACK_HOURS", "30"))
MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "15"))
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")


def collect_recent_entries():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    entries = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            print(f"[warn] failed to fetch {url}: {exc}")
            continue
        for entry in feed.entries:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if not published:
                continue
            published_dt = datetime(*published[:6], tzinfo=timezone.utc)
            if published_dt < cutoff:
                continue
            entries.append(
                {
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "source": feed.feed.get("title", url),
                    "published": published_dt,
                }
            )
    entries.sort(key=lambda e: e["published"], reverse=True)
    return entries[:MAX_ITEMS]


def build_prompt(entries):
    lines = []
    for e in entries:
        lines.append(f"- 제목: {e['title']}\n  출처: {e['source']}\n  링크: {e['link']}\n  내용 일부: {e['summary']}")
    articles_block = "\n".join(lines)
    return (
        "다음은 지난 24~30시간 동안 발행된 AI 관련 뉴스 기사 목록이다.\n"
        "이 기사들을 바탕으로 오늘 아침에 읽을 'AI 최신 동향 요약'을 한국어로 작성해줘.\n"
        "요구사항:\n"
        "1. 중복되거나 비슷한 내용은 하나로 묶어서 정리.\n"
        "2. 중요도가 높은 소식부터 5~10개의 핵심 항목으로 정리.\n"
        "3. 각 항목은 '- **제목**: 1~2문장 핵심 요약 (출처, 링크)' 형식.\n"
        "4. 마지막에 전체를 2~3문장으로 요약하는 '오늘의 한줄 정리' 섹션 추가.\n"
        "5. 군더더기 표현 없이 핵심만 간결하게.\n\n"
        f"기사 목록:\n{articles_block}"
    )


def summarize_with_claude(entries):
    from anthropic import Anthropic

    client = Anthropic()
    prompt = build_prompt(entries)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if hasattr(block, "text"))


def fallback_summary(entries):
    lines = ["## 지난 24~30시간 AI 뉴스 (자동 요약 실패, 원문 목록으로 대체)\n"]
    for e in entries:
        lines.append(f"- **{e['title']}** ({e['source']}) - {e['link']}")
    return "\n".join(lines)


def send_email(subject, body):
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    to_email = os.environ.get("TO_EMAIL", gmail_address)

    if not gmail_address or not gmail_app_password:
        print("[info] GMAIL_ADDRESS / GMAIL_APP_PASSWORD 시크릿이 없어 이메일 발송을 건너뜁니다.")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = to_email

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [to_email], msg.as_string())
    print(f"[info] 이메일 발송 완료: {to_email}")
    return True


def main():
    entries = collect_recent_entries()
    if not entries:
        body = "지난 24~30시간 동안 새로 수집된 AI 뉴스가 없습니다."
    else:
        try:
            body = summarize_with_claude(entries)
        except Exception as exc:
            print(f"[warn] Claude 요약 실패, 원문 목록으로 대체: {exc}")
            body = fallback_summary(entries)

    today = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    subject = f"[AI 뉴스 요약] {today}"

    print(body)

    os.makedirs("news", exist_ok=True)
    out_path = os.path.join("news", f"{today}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# {subject}\n\n{body}\n")
    print(f"[info] 요약 저장: {out_path}")

    send_email(subject, body)


if __name__ == "__main__":
    main()
