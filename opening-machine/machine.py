#!/usr/bin/env python3
"""벤치마크 오프닝 머신: 채널 발굴 -> 수치 수집 -> 통계 선정.

표준 라이브러리만 사용합니다. YouTube Data API v3 키는
환경변수 YT_API_KEY로 주거나, 클라우드 세션처럼 프록시가 키를 주입하는 환경이면 비워 둬도 됩니다.

사용법 (프로젝트 이름 = config/<이름>.json):
  python machine.py discover simritoktok   # 1단계: 검색으로 후보 채널 수집
  python machine.py collect  simritoktok   # 2단계: 채널·영상 수치 수집
  python machine.py score    simritoktok   # 3단계: 채널 선정 + 아웃라이어 영상 선정
  python machine.py all      simritoktok   # 1~3단계 연속 실행

산출물은 data/<이름>/ 아래에 저장됩니다.
"""
import csv
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://www.googleapis.com/youtube/v3/"
ROOT = os.path.dirname(os.path.abspath(__file__))
QUOTA = {"search": 100, "channels": 1, "playlistItems": 1, "videos": 1}
quota_used = 0


# ---------------------------------------------------------------- API
def api(endpoint, **params):
    global quota_used
    params = {k: v for k, v in params.items() if v is not None}
    url = API + endpoint + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url)
    # 키는 헤더로 보냄. 프록시 주입 환경에서는 자리표시 값이 실제 키로 바뀜.
    req.add_header("X-Goog-Api-Key", os.environ.get("YT_API_KEY", "injected-by-proxy"))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                quota_used += QUOTA.get(endpoint, 1)
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code in (500, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"[API 오류] {endpoint} {e.code}: {body[:400]}")
    raise SystemExit("[API 오류] 재시도 초과")


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


# ---------------------------------------------------------------- 유틸
def load_cfg(name):
    with open(os.path.join(ROOT, "config", f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


def data_dir(name):
    d = os.path.join(ROOT, "data", name)
    os.makedirs(d, exist_ok=True)
    return d


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def iso_seconds(d):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    dd, h, mi, s = (int(x or 0) for x in m.groups())
    return dd * 86400 + h * 3600 + mi * 60 + s


def parse_time(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def hangul_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum("가" <= c <= "힣" for c in letters) / len(letters)


# ---------------------------------------------------------------- 1단계
def discover(name):
    cfg, out = load_cfg(name), data_dir(name)
    s = cfg["search"]
    after = (datetime.now(timezone.utc) - timedelta(days=s["published_within_days"])).strftime("%Y-%m-%dT%H:%M:%SZ")
    hits = {}  # channel_id -> {title, queries:set, hit_count}
    for q in s["queries"]:
        for dur in s["video_duration"]:
            token = None
            for _ in range(s["pages_per_query"]):
                r = api("search", part="snippet", q=q, type="video", maxResults=50,
                        regionCode=s["region_code"], relevanceLanguage=s["relevance_language"],
                        videoDuration=dur, publishedAfter=after, pageToken=token)
                for it in r.get("items", []):
                    cid = it["snippet"]["channelId"]
                    h = hits.setdefault(cid, {"title": it["snippet"]["channelTitle"], "queries": [], "hit_count": 0})
                    h["hit_count"] += 1
                    if q not in h["queries"]:
                        h["queries"].append(q)
                token = r.get("nextPageToken")
                if not token:
                    break
        print(f"  검색 '{q}' 완료, 누적 후보 채널 {len(hits)}개, 사용 쿼터 {quota_used}")
    for handle in cfg.get("seed_handles", []):
        r = api("channels", part="id,snippet", forHandle=handle.lstrip("@"))
        for it in r.get("items", []):
            hits.setdefault(it["id"], {"title": it["snippet"]["title"], "queries": ["seed"], "hit_count": 0})
    for cid in cfg.get("seed_channel_ids", []):
        hits.setdefault(cid, {"title": "(seed)", "queries": ["seed"], "hit_count": 0})
    for cid in cfg.get("exclude_channel_ids", []) + cfg.get("own_channel_ids", []):
        hits.pop(cid, None)
    save_json(os.path.join(out, "candidates.json"), hits)
    print(f"[1단계 완료] 후보 채널 {len(hits)}개 -> candidates.json (쿼터 {quota_used})")


# ---------------------------------------------------------------- 2단계
def collect(name):
    cfg, out = load_cfg(name), data_dir(name)
    f = cfg["channel_filter"]
    cands = load_json(os.path.join(out, "candidates.json"))
    ids = list(cands)
    channels = {}
    for group in chunks(ids, 50):
        r = api("channels", part="snippet,statistics,contentDetails", id=",".join(group), maxResults=50)
        for it in r.get("items", []):
            st = it["statistics"]
            channels[it["id"]] = {
                "id": it["id"],
                "title": it["snippet"]["title"],
                "handle": it["snippet"].get("customUrl", ""),
                "subscribers": int(st.get("subscriberCount", 0)) if not st.get("hiddenSubscriberCount") else 0,
                "total_views": int(st.get("viewCount", 0)),
                "video_count": int(st.get("videoCount", 0)),
                "uploads": it["contentDetails"]["relatedPlaylists"]["uploads"],
                "search_hits": cands[it["id"]]["hit_count"],
                "search_queries": cands[it["id"]]["queries"],
            }
    # 구독자 범위로 1차 컷 (쿼터 절약)
    pre = [c for c in channels.values() if f["min_subscribers"] <= c["subscribers"] <= f["max_subscribers"]]
    print(f"  구독자 범위 통과 {len(pre)}/{len(channels)}")
    need = cfg["video_window"]["per_channel_recent_long_videos"]
    videos = {}
    for n, ch in enumerate(pre, 1):
        vid_ids, token = [], None
        for _ in range(4):  # 최근 업로드 최대 200개까지 훑어 롱폼 확보
            r = api("playlistItems", part="contentDetails", playlistId=ch["uploads"], maxResults=50, pageToken=token)
            vid_ids += [it["contentDetails"]["videoId"] for it in r.get("items", [])]
            token = r.get("nextPageToken")
            if not token or len(vid_ids) >= need * 3:
                break
        long_found = []
        for group in chunks(vid_ids, 50):
            r = api("videos", part="snippet,statistics,contentDetails", id=",".join(group), maxResults=50)
            for it in r.get("items", []):
                secs = iso_seconds(it["contentDetails"].get("duration"))
                st = it.get("statistics", {})
                v = {
                    "id": it["id"], "channel_id": ch["id"], "title": it["snippet"]["title"],
                    "published": it["snippet"]["publishedAt"], "seconds": secs,
                    "views": int(st.get("viewCount", 0)), "likes": int(st.get("likeCount", 0)),
                    "comments": int(st.get("commentCount", 0)),
                    "lang": it["snippet"].get("defaultAudioLanguage", ""),
                }
                if secs >= f["long_video_min_seconds"]:
                    long_found.append(v)
            if len(long_found) >= need:
                break
        for v in sorted(long_found, key=lambda x: x["published"], reverse=True)[:need]:
            videos[v["id"]] = v
        if n % 10 == 0:
            print(f"  채널 {n}/{len(pre)} 수집, 쿼터 {quota_used}")
    save_json(os.path.join(out, "channels.json"), channels)
    save_json(os.path.join(out, "videos.json"), videos)
    print(f"[2단계 완료] 채널 {len(channels)}개, 롱폼 영상 {len(videos)}개 (쿼터 {quota_used})")


# ---------------------------------------------------------------- 3단계
def score(name):
    cfg, out = load_cfg(name), data_dir(name)
    f, sel, win = cfg["channel_filter"], cfg["selection"], cfg["video_window"]
    lex = cfg["topic_lexicon"]
    channels = load_json(os.path.join(out, "channels.json"))
    videos = load_json(os.path.join(out, "videos.json"))
    now = datetime.now(timezone.utc)
    by_ch = {}
    for v in videos.values():
        by_ch.setdefault(v["channel_id"], []).append(v)

    rows, rejected = [], []
    for cid, vs in by_ch.items():
        ch = channels[cid]
        vs.sort(key=lambda x: x["published"], reverse=True)
        titles = [v["title"] for v in vs]
        mature = [v for v in vs if (now - parse_time(v["published"])).days >= win["min_age_days"]]
        reasons = []
        if not f["min_subscribers"] <= ch["subscribers"] <= f["max_subscribers"]:
            reasons.append(f"구독자 {ch['subscribers']} 범위 밖")
        if len(vs) < f["min_long_videos"]:
            reasons.append(f"롱폼 {len(vs)}편<{f['min_long_videos']}")
        last_days = (now - parse_time(vs[0]["published"])).days
        if last_days > f["max_days_since_last_upload"]:
            reasons.append(f"마지막 업로드 {last_days}일 전")
        hr = statistics.mean(hangul_ratio(t) for t in titles)
        if hr < f["min_hangul_title_ratio"]:
            reasons.append(f"한글 비율 {hr:.2f}")
        rel = sum(any(w in t for w in lex) for t in titles) / len(titles)
        if rel < f["min_topic_relevance"]:
            reasons.append(f"주제 적합도 {rel:.2f}")
        if len(mature) < 10:
            reasons.append(f"30일 경과 영상 {len(mature)}편")
        if reasons:
            rejected.append({"channel": ch["title"], "id": cid, "reasons": "; ".join(reasons)})
            continue
        med = statistics.median(v["views"] for v in mature)
        for v in mature:
            v["outlier"] = round(v["views"] / med, 2) if med else 0
            age = max((now - parse_time(v["published"])).days, 1)
            v["views_per_day"] = round(v["views"] / age, 1)
        outs = [v["outlier"] for v in mature]
        rate3 = sum(o >= sel["a_tier_min_outlier"] for o in outs) / len(outs)
        top = max(outs)
        reach = med / ch["subscribers"] if ch["subscribers"] else 0
        # 채널 점수: 평소 체급(중앙 조회수, 로그) + 터뜨리는 빈도 + 구독자 대비 도달 + 주제 적합도
        ch_score = (math.log10(max(med, 1)) / 6) * 0.35 + min(rate3 / 0.2, 1) * 0.30 \
            + min(reach / 0.3, 1) * 0.15 + min(rel / 0.8, 1) * 0.20
        rows.append({
            "channel": ch["title"], "handle": ch["handle"], "id": cid, "subscribers": ch["subscribers"],
            "long_videos": len(vs), "median_views": int(med), "outlier_rate_3x": round(rate3, 3),
            "max_outlier": top, "median_per_sub": round(reach, 3), "topic_relevance": round(rel, 2),
            "hangul_ratio": round(hr, 2), "search_hits": ch["search_hits"], "score": round(ch_score, 4),
            "_mature": mature,
        })
    rows.sort(key=lambda r: r["score"], reverse=True)
    chosen = rows[: sel["top_channels"]]

    a_tier, c_tier = [], []
    for r in chosen:
        mature = r["_mature"]
        on_topic = [v for v in mature if any(w in v["title"] for w in lex)]  # 영상 단위 주제 필터
        good = [v for v in on_topic if v["outlier"] >= sel["a_tier_min_outlier"] and v["views"] >= sel["a_tier_min_views"]]
        good.sort(key=lambda v: v["outlier"], reverse=True)
        bad = sorted((v for v in on_topic if v["outlier"] <= sel["c_tier_max_outlier"]), key=lambda v: v["outlier"])
        for tier, src, cap in (("A", good, sel["a_tier_max_per_channel"]), ("C", bad, sel["c_tier_per_channel"])):
            for v in src[:cap]:
                row = {"tier": tier, "channel": r["channel"], "video_id": v["id"], "title": v["title"],
                       "views": v["views"], "outlier": v["outlier"], "views_per_day": v["views_per_day"],
                       "like_rate": round(v["likes"] / v["views"], 4) if v["views"] else 0,
                       "comment_rate": round(v["comments"] / v["views"], 5) if v["views"] else 0,
                       "seconds": v["seconds"], "published": v["published"][:10],
                       "url": f"https://www.youtube.com/watch?v={v['id']}"}
                (a_tier if tier == "A" else c_tier).append(row)
    a_tier.sort(key=lambda x: x["outlier"], reverse=True)

    def write_csv(path, recs):
        if not recs:
            open(path, "w").close()
            return
        cols = [k for k in recs[0] if not k.startswith("_")]
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(recs)

    write_csv(os.path.join(out, "channels_ranked.csv"), rows)
    write_csv(os.path.join(out, "channels_rejected.csv"), rejected)
    write_csv(os.path.join(out, "videos_A_outliers.csv"), a_tier)
    write_csv(os.path.join(out, "videos_C_contrast.csv"), c_tier)
    with open(os.path.join(out, "video_ids_for_transcripts.txt"), "w", encoding="utf-8") as fh:
        for v in a_tier + c_tier:
            fh.write(f"{v['tier']}\t{v['video_id']}\n")
    print(f"[3단계 완료] 통과 채널 {len(rows)}개 중 상위 {len(chosen)}개 선정, 탈락 {len(rejected)}개")
    print(f"  A급(아웃라이어) {len(a_tier)}편, C급(대조) {len(c_tier)}편")
    print("  -> channels_ranked.csv, videos_A_outliers.csv, videos_C_contrast.csv, video_ids_for_transcripts.txt")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("discover", "collect", "score", "all"):
        print(__doc__)
        sys.exit(1)
    cmd, proj = sys.argv[1], sys.argv[2]
    steps = {"discover": [discover], "collect": [collect], "score": [score], "all": [discover, collect, score]}[cmd]
    for step in steps:
        step(proj)
    print(f"총 사용 쿼터 약 {quota_used} 유닛 (기본 일일 한도 10,000)")
