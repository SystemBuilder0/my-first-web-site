#!/usr/bin/env python3
"""claude.ai 데이터 내보내기(conversations.json)를 ChatGPT에 올리기 좋은 마크다운으로 변환한다.

사용법:
    python convert_claude_export.py <conversations.json 또는 내보내기 zip> [--out 출력폴더] [--max-kb 400]

동작:
  1. 대화 1건 = 마크다운 파일 1개 (YYYY-MM-DD_제목.md) 를 out/conversations/ 에 만든다.
  2. 전체 대화를 시간순으로 이어 붙인 뭉치 파일(all-conversations-001.md, -002.md ...)을
     --max-kb 크기 단위로 쪼개서 out/bundles/ 에 만든다. ChatGPT 프로젝트에는 이 뭉치 파일을 올린다.
  3. 목차(index.md)에 날짜·제목·메시지 수를 정리한다.

내보내기 파일의 정확한 스키마는 시점마다 바뀔 수 있어, 알려진 키 이름을 여러 개 시도하는 방식으로 관대하게 파싱한다.
파싱이 안 되는 항목은 건너뛰고 마지막에 개수를 보고한다.
"""
import argparse
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def load_conversations(path: Path):
    """json 파일 또는 zip 안의 conversations.json 을 읽어 리스트를 돌려준다."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.endswith("conversations.json")]
            if not names:
                sys.exit("zip 안에 conversations.json 이 없습니다.")
            raw = zf.read(names[0]).decode("utf-8")
    else:
        raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if isinstance(data, dict):
        # 일부 형식은 {"conversations": [...]} 로 감싸져 있다
        for key in ("conversations", "data", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    return data


def first(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def parse_time(value):
    if not value:
        return None
    if isinstance(value, (int, float)):
        # 초 또는 밀리초 epoch
        ts = value / 1000 if value > 1e11 else value
        return datetime.fromtimestamp(ts)
    s = str(value).replace("Z", "+00:00")
    for fmt in (None, "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.fromisoformat(s) if fmt is None else datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def message_text(msg: dict) -> str:
    """메시지 본문을 문자열로 뽑는다. text 필드가 없으면 content 블록을 합친다."""
    text = first(msg, "text", "content_text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    parts = []
    content = msg.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                t = block.get("type")
                if t in (None, "text") and block.get("text"):
                    parts.append(block["text"])
                elif t == "tool_use":
                    parts.append(f"[도구 호출: {block.get('name', '')}]")
                elif t == "tool_result":
                    parts.append("[도구 결과 생략]")
    # 첨부 파일 이름도 남긴다
    for att in msg.get("attachments", []) or []:
        name = att.get("file_name") or att.get("name")
        if name:
            parts.append(f"[첨부: {name}]")
    return "\n".join(p for p in parts if p).strip()


def sender_label(msg: dict) -> str:
    s = (first(msg, "sender", "role", default="") or "").lower()
    if s in ("human", "user"):
        return "사용자"
    if s in ("assistant", "claude", "ai"):
        return "Claude"
    return s or "?"


def safe_name(title: str, limit=60) -> str:
    title = re.sub(r"[\\/:*?\"<>|\r\n]+", " ", title).strip()
    title = re.sub(r"\s+", " ", title)
    return (title[:limit] or "untitled").strip()


def render(conv: dict):
    title = first(conv, "name", "title", default="(제목 없음)")
    created = parse_time(first(conv, "created_at", "createdAt", "create_time"))
    updated = parse_time(first(conv, "updated_at", "updatedAt", "update_time"))
    msgs = first(conv, "chat_messages", "messages", default=[]) or []
    msgs = sorted(msgs, key=lambda m: (parse_time(first(m, "created_at", "create_time")) or datetime.min))
    lines = [f"# {title}", ""]
    meta = []
    if created:
        meta.append(f"시작: {created:%Y-%m-%d %H:%M}")
    if updated:
        meta.append(f"마지막: {updated:%Y-%m-%d %H:%M}")
    meta.append(f"메시지 {len(msgs)}개")
    lines.append("_" + " · ".join(meta) + "_")
    lines.append("")
    for m in msgs:
        body = message_text(m)
        if not body:
            continue
        lines.append(f"**{sender_label(m)}:**")
        lines.append("")
        lines.append(body)
        lines.append("")
        lines.append("---")
        lines.append("")
    return title, created, len(msgs), "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="conversations.json 또는 내보내기 zip")
    ap.add_argument("--out", default="claude-export-md")
    ap.add_argument("--max-kb", type=int, default=400, help="뭉치 파일 1개 최대 크기(KB)")
    args = ap.parse_args()

    convs = load_conversations(Path(args.source))
    out = Path(args.out)
    (out / "conversations").mkdir(parents=True, exist_ok=True)
    (out / "bundles").mkdir(parents=True, exist_ok=True)

    rendered = []
    skipped = 0
    for conv in convs:
        try:
            title, created, n, md = render(conv)
        except Exception as e:  # noqa: BLE001
            skipped += 1
            print(f"건너뜀: {e}", file=sys.stderr)
            continue
        if n == 0:
            skipped += 1
            continue
        rendered.append((created or datetime.min, title, n, md))

    rendered.sort(key=lambda r: r[0])
    index = ["# Claude 대화 목차", "", "| 날짜 | 제목 | 메시지 수 | 파일 |", "|---|---|---|---|"]
    used = set()
    for created, title, n, md in rendered:
        date = created.strftime("%Y-%m-%d") if created != datetime.min else "unknown"
        base = f"{date}_{safe_name(title)}"
        name = base
        i = 2
        while name in used:
            name = f"{base}_{i}"
            i += 1
        used.add(name)
        (out / "conversations" / f"{name}.md").write_text(md, encoding="utf-8")
        index.append(f"| {date} | {title} | {n} | conversations/{name}.md |")
    (out / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    # 뭉치 파일
    limit = args.max_kb * 1024
    bundle, size, k = [], 0, 1
    def flush():
        nonlocal bundle, size, k
        if bundle:
            (out / "bundles" / f"all-conversations-{k:03d}.md").write_text("\n\n".join(bundle), encoding="utf-8")
            k += 1
            bundle, size = [], 0
    for _, _, _, md in rendered:
        b = len(md.encode("utf-8"))
        if size + b > limit and bundle:
            flush()
        bundle.append(md)
        size += b
    flush()

    print(f"대화 {len(rendered)}건 변환, {skipped}건 건너뜀 → {out.resolve()}")
    print(f"뭉치 파일 {k-1}개 (bundles/), 개별 파일 {len(rendered)}개 (conversations/), 목차 index.md")


if __name__ == "__main__":
    main()
