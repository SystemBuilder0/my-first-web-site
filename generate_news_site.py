"""news/*.md 요약 파일들로부터 뉴스 목록 페이지와 상세 페이지(HTML)를 생성한다.

daily_ai_news.py 가 news/YYYY-MM-DD.md 를 새로 만들 때마다 이 스크립트를 실행해
news/index.html (최신순 목록) 과 news/YYYY-MM-DD.html (상세 페이지) 을 갱신한다.
"""

import glob
import os
import re

import markdown as md

NEWS_DIR = "news"

PAGE_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="../styles.css" />
</head>
<body>
  <main>
    <a class="back-link" href="index.html">&larr; 목록으로</a>
    <article class="news-detail">
{body}
    </article>
  </main>
</body>
</html>
"""

INDEX_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI 최신 뉴스</title>
  <link rel="stylesheet" href="../styles.css" />
</head>
<body>
  <header class="site-header">
    <h1>AI 최신 뉴스</h1>
    <p class="subtitle">날짜별 AI 동향 요약, 최신순</p>
  </header>
  <main>
    <a class="back-link" href="../index.html">&larr; 홈으로</a>
{list_html}
  </main>
</body>
</html>
"""

LINK_RE = re.compile(r"(?<![\(\[])(https?://\S+)")
TRAILING_PUNCT_RE = re.compile(r"[)\].,;:!?]+$")


def linkify(text):
    def replace(m):
        url = m.group(1)
        trailing_match = TRAILING_PUNCT_RE.search(url)
        trailing = trailing_match.group(0) if trailing_match else ""
        if trailing:
            url = url[: -len(trailing)]
        return f"[{url}]({url}){trailing}"

    return LINK_RE.sub(replace, text)


def extract_title(md_text, fallback):
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return fallback


def load_entries():
    entries = []
    for path in sorted(glob.glob(os.path.join(NEWS_DIR, "*.md"))):
        date = os.path.splitext(os.path.basename(path))[0]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        entries.append({"date": date, "text": text})
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def render_detail(entry):
    title = extract_title(entry["text"], entry["date"])
    html_body = md.markdown(linkify(entry["text"]), extensions=["nl2br", "sane_lists"])
    out_path = os.path.join(NEWS_DIR, f"{entry['date']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(PAGE_TEMPLATE.format(title=title, body=html_body))


def render_index(entries):
    if not entries:
        list_html = '    <p class="news-empty">아직 등록된 뉴스가 없습니다.</p>'
    else:
        items = []
        for e in entries:
            title = extract_title(e["text"], e["date"])
            items.append(
                f'      <li><a href="{e["date"]}.html">'
                f'<div class="news-date">{e["date"]}</div>'
                f'<div class="news-title">{title}</div>'
                f"</a></li>"
            )
        list_html = '    <ul class="news-list">\n' + "\n".join(items) + "\n    </ul>"

    out_path = os.path.join(NEWS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE.format(list_html=list_html))


def main():
    os.makedirs(NEWS_DIR, exist_ok=True)
    entries = load_entries()
    for entry in entries:
        render_detail(entry)
    render_index(entries)
    print(f"[info] {len(entries)}개의 뉴스 페이지 생성 완료")


if __name__ == "__main__":
    main()
