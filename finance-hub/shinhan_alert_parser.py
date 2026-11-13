"""finance-hub-daily-collect 4단계: [신한알림] 외화(USD) 입출금 문자 파서.

메일 1통(메시지 단위)의 본문과 수신 시각을 받아 거래 1건 또는 건너뜀/보류 사유를 돌려준다.
계좌번호는 결과에 넣지 않는다.
"""
import re
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

# [Web발신] 신한11/13-13:08 180*425426[USD] 입금 0.01 잔액 3,357.71 장준혁
PATTERN = re.compile(
    r"신한\s*(?P<mm>\d{1,2})/(?P<dd>\d{1,2})-(?P<hh>\d{1,2}):(?P<mi>\d{2})\s+"
    r"\S*\[USD\]\s+"
    r"(?P<dir>입금|출금)\s+(?P<amt>[\d,]+(?:\.\d+)?)\s+"
    r"잔액\s+(?P<bal>-?[\d,]+(?:\.\d+)?)"
)


def normalize(body: str) -> str:
    """<br/> 등 태그와 연속 공백을 한 칸 공백으로."""
    text = re.sub(r"<[^>]+>", " ", body or "")
    return re.sub(r"\s+", " ", text).strip()


def resolve_year(mm: int, dd: int, received_kst: datetime) -> int:
    """연도 = 메일 수신일 연도. 거래월이 수신월보다 크면(12월 거래, 1월 수신) 전년도."""
    year = received_kst.year
    if mm > received_kst.month:
        year -= 1
    return year


def dedupe_key(dt: datetime, direction: str, amount: float, balance: float) -> str:
    return f"shinhan-usd|{dt:%Y-%m-%dT%H:%M}|{direction}|{abs(amount):.2f}|{balance:.2f}"


def parse(body: str, received_utc: datetime):
    """반환: ("skip", 사유) | ("hold", 사유) | ("ok", dict)."""
    text = normalize(body)
    if not text:
        return ("skip", "본문 비어 있음(테스트 메일)")
    if "[USD]" not in text:
        return ("skip", "[USD] 없음(테스트 메일)")
    m = PATTERN.search(text)
    if not m:
        return ("hold", f"형식 불일치 — 적재 안 함: {text[:80]}")
    received_kst = received_utc.astimezone(KST)
    mm, dd = int(m["mm"]), int(m["dd"])
    year = resolve_year(mm, dd, received_kst)
    dt = datetime(year, mm, dd, int(m["hh"]), int(m["mi"]), tzinfo=KST)
    direction = m["dir"]
    amount = float(m["amt"].replace(",", ""))
    if direction == "출금":
        amount = -amount
    balance = float(m["bal"].replace(",", ""))
    return ("ok", {
        "거래": f"외화 {direction} {abs(amount):.2f} USD",
        "날짜": dt.isoformat(),
        "계좌": "신한 외화(USD)",
        "방향": direction,
        "금액": amount,
        "통화": "USD",
        "잔액": balance,
        "출처": "알림",
        "분류": "미분류",
        "원본ID": dedupe_key(dt, direction, amount, balance),
    })
