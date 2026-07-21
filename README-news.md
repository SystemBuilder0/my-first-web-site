# 뉴스 자동화 시스템 안내

## 이게 뭔가요

매일 아침 GitHub Actions가 자동으로 실행되어, 관심 분야(AI 시장 / AI 활용 / 로보틱스 / 바이오 /
유튜브·SNS) RSS 피드에서 최신 기사를 모은 뒤, **분야별로 가장 중요한 기사 딱 1건씩만 골라
2~3문장으로 요약하고 원문 링크를 붙여, 하루 치를 하나의 문서로** Notion에 올립니다.
여러 기사를 하나하나 열어볼 필요 없이, 그날의 브리핑 문서 하나만 열면 5개 분야 핵심이
한 화면에 다 보입니다.

파이프라인은 두 단계로 나뉩니다.

1. **수집 (`scripts/collect.py`, AI 미사용)** — RSS 피드를 읽어 최근 기사 후보를 모으고,
   중복을 제거해 `data/archive/YYYY-MM-DD.json`에 원본(제목/출처/주제/발행일/링크/짧은
   본문 발췌)을 저장합니다. 선택적으로 각 기사를 "뉴스 자동화" DB(백엔드 원본 아카이브,
   사람이 직접 볼 화면 아님)에도 한 줄씩 남깁니다.
2. **요약 (`scripts/summarize.py`, Claude Haiku 사용)** — 1번에서 모인 후보들을 분야별로
   묶어, 각 분야마다 "가장 중요도가 높은 기사 1건"을 고르고 2~3문장 한국어 요약을 만들도록
   Claude Haiku에게 맡깁니다(하루 5번, 저비용 모델). 다섯 분야를 하나로 합쳐 "뉴스 브리핑"
   Notion 데이터베이스에 그날 문서 1개로 올립니다. 이게 실제로 매일 아침 보게 될 화면입니다.

이 구조에서 AI(유료 토큰)가 쓰이는 지점은 2단계, 하루 5번의 짧은 요약 호출뿐입니다.
수집·중복제거·정리는 전부 코드로만 처리합니다.

## Notion 구조

- **뉴스 브리핑** (사람이 보는 화면): 하루 = 문서 1개. 제목 "YYYY-MM-DD 뉴스 브리핑",
  본문에 5개 분야 헤더 아래 핵심 기사 제목·요약·출처 링크가 순서대로 들어있습니다.
  기본 뷰가 날짜 내림차순 정렬이라 최신 문서가 맨 위에 옵니다.
- **뉴스 자동화** (백엔드 원본 아카이브, 선택 사항): 수집 단계에서 스친 모든 기사가
  한 줄씩 쌓이는 곳. 요약이 실제로 어떤 후보들 중에서 골라졌는지 검증하고 싶을 때만
  들여다보면 됩니다. 평소에 열어볼 필요는 없습니다.

## 최초 1회 수동 준비 (이것만 사람이 해야 함)

1. https://www.notion.so/my-integrations 에서 "internal integration"을 하나 생성합니다.
2. 생성된 Integration의 **Internal Integration Secret(토큰)** 을 복사해둡니다.
3. Notion에서 "뉴스 브리핑" 데이터베이스가 있는 페이지(및 "뉴스 자동화" 페이지)로 이동해
   우측 상단 `...` → `연결 추가(Add connections)`에서 방금 만든 Integration을 공유합니다.
   이 단계를 빠뜨리면 Integration이 토큰은 유효해도 해당 데이터베이스에 접근하지 못합니다.
4. https://console.anthropic.com 에서 API 키를 하나 발급받습니다 (요약 단계에서 사용).
5. GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret에서
   아래 두 개를 등록합니다.
   - `NOTION_TOKEN`: 2번에서 복사한 토큰
   - `ANTHROPIC_API_KEY`: 4번에서 발급받은 키

이후로는 완전 자동입니다.

## 로컬에서 미리 테스트하기 (dry-run)

토큰/API 키 없이 실행하면 실제로 아무 곳에도 쓰지 않고, 콘솔에 "이렇게 만들어질 것이다"만
출력합니다.

```bash
pip install -r requirements.txt

# 1단계: RSS 수집 (dry-run)
python scripts/collect.py

# 2단계: 오늘 수집된 아카이브를 바탕으로 브리핑 생성 (dry-run)
python scripts/summarize.py
```

`NOTION_TOKEN`이 없으면 자동으로 dry-run 모드로 동작합니다. `ANTHROPIC_API_KEY`가 없으면
`summarize.py`는 AI 판단 없이 분야별 첫 번째 후보를 그대로 보여줍니다(실제 운영에서는
항상 키가 설정되어 있어야 합니다).

실제로 반영하려면 두 값을 모두 설정한 뒤 실행합니다.

```bash
export NOTION_TOKEN="secret_xxx..."
export ANTHROPIC_API_KEY="sk-ant-xxx..."
python scripts/collect.py
python scripts/summarize.py
```

수집 기간을 바꾸고 싶다면 `DAYS_BACK` 환경변수를(기본 2일), 특정 날짜의 브리핑을 다시
만들고 싶다면 `DIGEST_DATE` 환경변수를(기본 오늘) 설정하면 됩니다.

```bash
DAYS_BACK=5 python scripts/collect.py
DIGEST_DATE=2026-07-20 python scripts/summarize.py
```

## 자동 실행 스케줄 & 수동 실행

- 매일 한국시간(KST) 오전 7시에 자동 실행됩니다 (`.github/workflows/news.yml`,
  cron은 UTC 기준이라 `0 22 * * *`로 등록되어 있습니다 = KST 07:00).
- GitHub Actions는 부하 상황에 따라 예약된 cron 실행이 몇 분 정도 지연될 수 있습니다.
  정확히 07:00:00에 실행되지 않아도 정상입니다.
- 필요할 때 즉시 실행하고 싶다면, GitHub 저장소의 Actions 탭 → "Daily News Collection"
  워크플로우 → 우측의 **Run workflow** 버튼으로 언제든 수동 실행할 수 있습니다.
- 실행이 끝나면 새로 수집된 기사가 있을 경우 `data/` 폴더 변경사항이 자동으로 커밋·푸시됩니다.
