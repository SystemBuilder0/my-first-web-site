#!/usr/bin/env python3
"""Claude Code 로컬 세션 기록(~/.claude/projects/**/*.jsonl)을 마크다운으로 변환한다.

Claude Code(CLI·데스크톱·Remote Control)로 내 컴퓨터에서 돌린 세션은 이 폴더에 JSONL 로 남는다.
  Windows: C:\\Users\\<이름>\\.claude\\projects\\
  macOS/Linux: ~/.claude/projects/

사용법:
    python convert_claude_code_transcripts.py [--root ~/.claude/projects] [--out claude-code-md] [--max-kb 400]

동작:
  세션(jsonl) 1개 = 마크다운 1개. 사용자 발화와 Claude 답변 텍스트만 남기고,
  도구 호출은 "[도구: 이름]" 한 줄로 축약한다(코드·명령 출력은 너무 길어서 뺀다).
  프로젝트 폴더별로 묶고, 전체를 뭉치 파일로도 만든다.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path


def extract_text(content):
    if isinstance(content, str):
        return content.strip()
    parts = []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            t = block.get("type")
            if t == "text" and block.get("text"):
                parts.append(block["text"])
            elif t == "tool_use":
                parts.append(f"[도구: {block.get('name', '')}]")
            elif t == "tool_result":
                # 도구 결과는 생략 (대부분 파일 내용·명령 출력)
                continue
    return "\n".join(parts).strip()


def convert_session(path: Path):
    lines, first_ts, last_ts, count, summary = [], None, None, 0, None
    with path.open(encoding="utf-8", errors="replace") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                continue
            typ = rec.get("type")
            if typ == "summary" and rec.get("summary"):
                summary = rec["summary"]
                continue
            if typ not in ("user", "assistant"):
                continue
            msg = rec.get("message") or {}
            text = extract_text(msg.get("content"))
            if not text or text.startswith("<command-name>") or text.startswith("<local-command"):
                continue
            ts = rec.get("timestamp")
            try:
                dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00")) if ts else None
            except ValueError:
                dt = None
            if dt:
                first_ts = first_ts or dt
                last_ts = dt
            who = "사용자" if typ == "user" else "Claude"
            lines.append(f"**{who}:**\n\n{text}\n\n---\n")
            count += 1
    if count == 0:
        return None
    title = summary or path.stem
    head = [f"# {title}", ""]
    meta = [f"세션 파일: {path.name}"]
    if first_ts:
        meta.append(f"시작: {first_ts:%Y-%m-%d %H:%M}")
    if last_ts:
        meta.append(f"마지막: {last_ts:%Y-%m-%d %H:%M}")
    meta.append(f"메시지 {count}개")
    head.append("_" + " · ".join(meta) + "_")
    head.append("")
    return first_ts, title, count, "\n".join(head + lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--out", default="claude-code-md")
    ap.add_argument("--max-kb", type=int, default=400)
    args = ap.parse_args()

    root = Path(args.root).expanduser()
    if not root.exists():
        raise SystemExit(f"폴더가 없습니다: {root}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    results = []
    for jsonl in sorted(root.rglob("*.jsonl")):
        project = jsonl.parent.name or "root"
        r = convert_session(jsonl)
        if not r:
            continue
        first_ts, title, count, md = r
        results.append((first_ts or datetime.min, project, title, count, md, jsonl))

    results.sort(key=lambda r: r[0])
    index = ["# Claude Code 세션 목차", "", "| 날짜 | 프로젝트 | 제목 | 메시지 | 파일 |", "|---|---|---|---|---|"]
    for i, (ts, project, title, count, md, src) in enumerate(results, 1):
        date = ts.strftime("%Y-%m-%d") if ts != datetime.min else "unknown"
        proj_dir = out / "sessions" / project.replace("/", "_")
        proj_dir.mkdir(parents=True, exist_ok=True)
        name = f"{date}_{i:03d}.md"
        (proj_dir / name).write_text(md, encoding="utf-8")
        index.append(f"| {date} | {project} | {title[:60]} | {count} | sessions/{proj_dir.name}/{name} |")
    (out / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    (out / "bundles").mkdir(exist_ok=True)
    limit, bundle, size, k = args.max_kb * 1024, [], 0, 1
    for *_, md, _src in results:
        b = len(md.encode("utf-8"))
        if size + b > limit and bundle:
            (out / "bundles" / f"all-sessions-{k:03d}.md").write_text("\n\n".join(bundle), encoding="utf-8")
            k += 1
            bundle, size = [], 0
        bundle.append(md)
        size += b
    if bundle:
        (out / "bundles" / f"all-sessions-{k:03d}.md").write_text("\n\n".join(bundle), encoding="utf-8")
    print(f"세션 {len(results)}개 변환 → {out.resolve()} (뭉치 {k}개)")


if __name__ == "__main__":
    main()
