#!/usr/bin/env python3
"""4단계: 선정된 영상의 자막을 받아 오프닝(앞 60초)과 전문을 저장합니다.

대표님 PC에서 실행합니다. 클라우드 서버 IP는 YouTube가 자막 요청을 자주 막습니다.
  pip install youtube-transcript-api
  python transcripts.py simritoktok

입력: data/<이름>/video_ids_for_transcripts.txt (3단계 산출물)
출력: data/<이름>/transcripts/<video_id>.json, data/<이름>/openings.jsonl
자막이 없는 영상은 missing_transcripts.txt에 남깁니다 (나중에 Whisper로 처리).
"""
import json
import os
import sys
import time

from youtube_transcript_api import YouTubeTranscriptApi

OPENING_SECONDS = 60
ROOT = os.path.dirname(os.path.abspath(__file__))


def main(name):
    d = os.path.join(ROOT, "data", name)
    tdir = os.path.join(d, "transcripts")
    os.makedirs(tdir, exist_ok=True)
    with open(os.path.join(d, "video_ids_for_transcripts.txt"), encoding="utf-8") as f:
        items = [line.strip().split("\t") for line in f if line.strip()]
    api = YouTubeTranscriptApi()
    missing = []
    with open(os.path.join(d, "openings.jsonl"), "w", encoding="utf-8") as out:
        for n, (tier, vid) in enumerate(items, 1):
            path = os.path.join(tdir, f"{vid}.json")
            try:
                if os.path.exists(path):
                    with open(path, encoding="utf-8") as f:
                        snippets = json.load(f)["snippets"]
                else:
                    fetched = api.fetch(vid, languages=["ko"])
                    snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump({"video_id": vid, "snippets": snippets}, f, ensure_ascii=False)
                    time.sleep(1.5)  # 차단 방지용 간격
                opening = " ".join(s["text"] for s in snippets if s["start"] < OPENING_SECONDS)
                out.write(json.dumps({"tier": tier, "video_id": vid, "opening_60s": opening}, ensure_ascii=False) + "\n")
                print(f"[{n}/{len(items)}] {tier} {vid} OK")
            except Exception as e:  # 자막 없음, 차단 등
                missing.append(f"{tier}\t{vid}\t{type(e).__name__}")
                print(f"[{n}/{len(items)}] {tier} {vid} 실패: {type(e).__name__}")
    with open(os.path.join(d, "missing_transcripts.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(missing))
    print(f"완료: 성공 {len(items) - len(missing)}편, 실패 {len(missing)}편")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
