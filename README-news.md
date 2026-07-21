# 뉴스 자동화 시스템 안내

## 이게 뭔가요

매일 아침 GitHub Actions가 자동으로 실행되어, 미리 등록해둔 RSS 피드(`feeds.yaml`)에서
최근 기사(기본 2일 이내)를 가져온 뒤 중복을 제거하고, 새 기사만 Notion 데이터베이스에
한 줄씩 자동으로 추가합니다. AI/LLM은 사용하지 않으며, 단순 수집·정리·기록만 합니다.

수집된 기사는 다음 두 곳에 남습니다.

- Notion 데이터베이스: 제목/출처/주제/발행일/링크/수집일 컬럼으로 정리된 행
- 저장소 내 `data/archive/YYYY-MM-DD.json`: 그날 새로 수집한 기사 원본 기록
- `data/seen_urls.json`: 중복 방지를 위해 이미 처리한 링크 목록 (최근 500개 유지)

## 최초 1회 수동 준비 (이것만 사람이 해야 함)

1. https://www.notion.so/my-integrations 에서 "internal integration"을 하나 생성합니다.
2. 생성된 Integration의 **Internal Integration Secret(토큰)** 을 복사해둡니다.
3. Notion에서 "뉴스 자동화" 데이터베이스가 있는 페이지로 이동해 우측 상단 `...` →
   `연결 추가(Add connections)`에서 방금 만든 Integration을 공유(연결)합니다.
   이 단계를 빠뜨리면 Integration이 토큰은 유효해도 해당 데이터베이스에 접근하지 못합니다.
4. GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret에서
   이름을 `NOTION_TOKEN`으로, 값은 2번에서 복사한 토큰으로 등록합니다.

이후로는 완전 자동입니다.

## 로컬에서 미리 테스트하기 (dry-run)

토큰 없이 실행하면 Notion에 실제로 쓰지 않고, "이렇게 추가했을 것이다"만 출력합니다.

```bash
pip install -r requirements.txt
python scripts/collect.py
```

`NOTION_TOKEN` 환경변수가 없으면 자동으로 dry-run 모드로 동작합니다. 실제로 Notion에
기록하려면 토큰을 설정한 뒤 실행하면 됩니다.

```bash
export NOTION_TOKEN="secret_xxx..."
python scripts/collect.py
```

수집 기간을 바꾸고 싶다면 `DAYS_BACK` 환경변수를 설정하면 됩니다 (기본값 2일).

```bash
DAYS_BACK=5 python scripts/collect.py
```

## 자동 실행 스케줄 & 수동 실행

- 매일 한국시간(KST) 오전 7시에 자동 실행됩니다 (`.github/workflows/news.yml`,
  cron은 UTC 기준이라 `0 22 * * *`로 등록되어 있습니다 = KST 07:00).
- GitHub Actions는 부하 상황에 따라 예약된 cron 실행이 몇 분 정도 지연될 수 있습니다.
  정확히 07:00:00에 실행되지 않아도 정상입니다.
- 필요할 때 즉시 실행하고 싶다면, GitHub 저장소의 Actions 탭 → "Daily News Collection"
  워크플로우 → 우측의 **Run workflow** 버튼으로 언제든 수동 실행할 수 있습니다.
- 실행이 끝나면 새로 수집된 기사가 있을 경우 `data/` 폴더 변경사항이 자동으로 커밋·푸시됩니다.
