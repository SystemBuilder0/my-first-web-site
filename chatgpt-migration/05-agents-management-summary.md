# agents-management 저장소 인수인계 요약
(작성 기준일: 2026-09-11, 저장소 경로: `/home/user/agents-management`, GitHub `SystemBuilder0/agents-management` private)

---

## 1. 이 저장소가 무엇인가

장준혁 대표(1인 창업자, 유튜브 2채널 + 디지털 제품 사업)의 회사 전체를 굴리는 **"1인 에이전트 컴퍼니 OS"**다. 핵심 철학은 "진실의 원천은 파일이고, 웹앱은 그 위에 얹힌 뷰"라는 것 — DB가 없고 회사의 모든 상태(목표·전략·트랙·직원·산출물·승인)가 저장소 안의 마크다운/JSON 파일로 존재하며, 모든 변경은 git 커밋으로 남는다. "직원"은 사람이 아니라 `.claude/skills/<slug>/SKILL.md` 한 장이고, 이 파일을 **Claude Code CLI**가 헤드리스로 실행해 산출물을 만든다. 매일 새벽 GitHub Actions가 대표의 PC 전원과 무관하게 직원들을 자동 실행하고 결과를 저장소에 커밋 → 대표가 PC를 켜면 git pull로 받아 로컬 대시보드(Express+React, `127.0.0.1:4321`)에서 확인한다.

### 폴더 구조

```
company/          회사의 상태 — 목표(goals), 전략(initiatives), 트랙(tracks), 프로젝트(projects),
                   시스템(systems), 산출물(outputs), 실행로그(runs), 승인함(approvals),
                   품질점수(quality), 라이브러리(library), 계획(plan), KPI(kpis), 책임영역(aor.md),
                   체크포인트(checkpoints), 오늘할일(today), 로드맵(roadmap.md), 자동화지도(factory)
.claude/skills/    "직원" 18명. SKILL.md 한 장 = 한 명(YAML frontmatter + 절차 본문)
runtime/           결정공간 — 세기·계산·스케줄·비용 집계. 모델을 부르지 않는 순수 Node 스크립트
apps/dashboard/    뷰이자 조작 표면 (Express 서버 + Vite/React 프런트)
collector/         뉴스·레퍼런스 원자료 수집기 (Python, LLM 미사용, 결정론적)
docs/              cloud-runner.md (GitHub Actions 클라우드 설정 절차)
.github/workflows/ daily-briefing.yml — 무인 실행 워크플로
```

---

## 2. 회사 정의

**비전**: "에이전트 직원들을 고용해 대기업을 능가하는 1인 유니콘이 된다." (`company/company.md`)
**메인 골**: "트래픽을 모으는 기계를 만든다. 제품도 광고도 그 기계가 돌기 시작한 뒤에 붙는다." — 순서: ① 영상 공장 v1(심리톡톡 완전자동화, 지금 여기) → ② 공장 복제(채널 증식) → ③ 트래픽 수익화(외주 광고 먼저 → 자기 제품).

### 장기 목표 (수치, `company/goals/`)

| 목표 | target | current | 진행률 | horizon |
|---|---|---|---|---|
| 연 수익 (`annual-revenue.md`) | 100,000,000원 (2026년말) → 10억(2027) → 100억(2028) | 4,144,710원 | **4%** | 2026-12-31 |
| 총 구독자 (`subscribers.md`) | 250,000명 (심리10만/퍼스널5만/해외10만) | 26,100명 (전량 심리톡톡 `@심리_톡톡`) | **10.4%** | 2026-12-31 (2026-09-08 기록 기준) |

퍼스널·해외 채널은 아직 미개설(0명). 8/31 주간 경영 리뷰 기준 현재 속도로는 두 목표 모두 연말 도달 불가능 판정(수익 약 45배, 구독자 약 55배 속도 부족).

### 이니셔티브 (전략, `company/initiatives/`, 5개)

| 이니셔티브 | 상태 | 관련 트랙 |
|---|---|---|
| `video-factory-v1` (영상 공장 v1) | active, priority 1, horizon **2026-09-07(이미 지남)** | psychology-channel-automation |
| `agent-org-expansion` (에이전트 조직 확장) | active, priority 2 | psychology-channel-automation 외 3개 |
| `factory-replication` (공장 복제) | planned — video-factory-v1 완성 전 착수 안 함 | personal-brand-channel 외 4개 |
| `traffic-monetization` (트래픽 수익화) | planned — 공장 복제 후 착수 | adsense-monetization-infra, channel-linked-product |
| `constellation-full-loop` (별자리 완주) | archived (2026-08-31, "제품은 트래픽 다음" 순서로 보류) | constellation-product-launch, channel-linked-product |

### 트랙 (`company/tracks/`, 13개 — 파일 스캔 기준 최신 상태)

| 트랙 | 목적 (한 줄) | 상태 |
|---|---|---|
| psychology-channel-automation | 심리톡톡 기획~업로드준비 완전 자동화 | **active** (priority 1) |
| morning-briefing-pm-assistant | 매일 아침 브리핑 + PM 비서 | **active** (priority 2) |
| news-auto-collector | 콘텐츠 소재용 뉴스 자동 수집기 | **active** (priority 3, 사실상 100% 완성) |
| adsense-monetization-infra | 채널별 애드센스 계정 분리·수익화 인프라 | backlog |
| global-longform-channel | 해외 롱폼(유튜브·뉴스레터) | backlog |
| global-shortform-channel | 해외 숏폼 SNS 진출 | backlog |
| mass-shorts-automation | 심리 니치 밖 대중 쇼츠 자동화 | backlog |
| personal-brand-channel | 대표 개인 개성 채널 | backlog |
| sns-multi-channel-distribution | SNS 7계정 동시 배포 | backlog |
| constellation-product-launch | 별자리 디지털 제품 완주(배포→광고→데이터) | **archived** (제품은 로드맵 7단계, 트래픽 우선) |
| channel-linked-product | 채널별 타겟 제품 연결 | archived (동일 사유) |
| ai-conversation-psych-service | AI 대화데이터 기반 심리 분석 서비스 | archived (동일 사유) |
| product-dev-loop-iteration | 제품개발 루프 자체의 표준화 | archived (동일 사유) |

주의: 루트 `CHECKPOINT.md`(2026-08-31 작성)는 "트랙 13개, 활성 5"라 적혀 있으나, 실제 파일 상태(2026-09 기준)는 **활성 3개 + 신규 archived 4개**로 바뀌어 있다. CHECKPOINT.md가 최신 상태를 반영하지 못하고 있다 (§5 참고).

### KPI (`company/kpis/`, 3개 — CLAUDE.md는 5~6개를 규정하나 현재 3개뿐)

| KPI | metric | target/current | 역-지표(counter) |
|---|---|---|---|
| weekly-uploads (주간 업로드 편수) | 편/주 | target 2 / current 0 | 수익화 제한·검열 발생 건수 (target 0) |
| subscriber-growth (주간 순증 구독자) | 명/주 | target 미설정 / current 0 | 조회수 대비 구독 전환율 (미설정) |
| automation-rate / founder-touchpoints (대표 개입 작업 수) | 건/편 | target 0 / current **미측정**(제작 과정 미문서화) | 자동 산출물 재작업률 |

### 책임영역(AoR, `company/aor.md`)

한 영역 = DRI(스킬 파일) 1명 원칙. 가장 큰 구멍: **`video-production`(영상 제작) 영역에 담당자가 없음** — 메인 골의 핵심인데 비어 있음. `agent-ops`(에이전트 운영)도 대표가 직접 담당. 진짜 SPOF로 재정의된 것: 인증 토큰 만료, 대표 자신, GitHub Actions 의존, YouTube 계정 단일화(정책위반시 전멸) — "사람의 부재"가 아니라 이 4가지.

---

## 3. 에이전트("직원") 목록 — `.claude/skills/` 18개

`x-status` 기준 **현재(2026-09-11) 실제 상태** (2026-08-31 CHECKPOINT.md의 "활성 6명"과 다름 — 이후 사용량 최적화 등을 이유로 3개가 paused로 바뀜):

| slug | 직함 | 티어 | 상태 | 스케줄(cron) | 산출물 경로 |
|---|---|---|---|---|---|
| news-collector | 뉴스 수집가 | haiku | **active** | `0 7 * * *` (매일, order 10) | `company/outputs/{date}/news-collector/` |
| planner | 플래너 | sonnet | **active** | `0 7 * * 1` (매주 월, order 20) | `company/plan/` |
| morning-briefing | 아침 브리핑 비서 | sonnet | **active** | `0 7 * * *` (매일, order 30) | `company/outputs/{date}/morning-briefing/` |
| checkpoint | 체크포인트(안전저장) | sonnet | **active** | 없음(수동, `/checkpoint`) | `company/checkpoints/` |
| project-manager | 프로젝트 매니저 | sonnet | paused | `0 7 * * *` (order 40, 원래 월요일 취지) | `company/outputs/{date}/project-manager/` |
| proxy-ceo | 대리경영 CEO | opus | paused | `0 7 * * *` (order 50) | `company/outputs/{date}/proxy-ceo/` |
| librarian | 사서 | haiku | paused | `0 7 * * *` (order 60, 원래 일요일 취지) | `company/outputs/{date}/librarian/` |
| ai-designer | AI 디자이너 | sonnet | draft | null | `company/outputs/{date}/ai-designer/` |
| constellation-app-builder | 별자리 앱 빌더 | sonnet | draft(수동전용) | null | `company/outputs/{date}/constellation-app-builder/` |
| email-assistant | 이메일 비서 | sonnet | draft | null | `company/outputs/{date}/email-assistant/` |
| marketing-manager | 마케팅 담당 | sonnet | draft | null | `company/outputs/{date}/marketing-manager/` |
| product-strategist | 제품개발 전략가 | opus | draft | null | `company/outputs/{date}/product-strategist/` |
| reference-hunter | 레퍼런스 헌터 | sonnet | draft | null (원래 일요일 아침 취지) | `company/outputs/{date}/reference-hunter/` |
| script-postprocessor | 대본 후처리사 | sonnet | draft | null | `company/outputs/{date}/script-postprocessor/` |
| shorts-uploader | 쇼츠 업로더 | haiku | draft | `0 10 * * *` | `company/outputs/{date}/shorts-uploader/` |
| sns-manager | SNS 관리자 | sonnet | draft | `0 9 * * *` | `company/outputs/{date}/sns-manager/` |
| strategy-planner | 전략 기획가 | opus | draft | null | `company/outputs/{date}/strategy-planner/` |
| translator | 번역가 | sonnet | draft | null | `company/outputs/{date}/translator/` |

**입력**: 대부분 `company/outputs/{date}/_input/packet.json`(뉴스/브리핑 계열, `runtime/brief-input.mjs`가 사전 생성) 또는 `node runtime/checkpoint.mjs --json`(트랙/목표 계열, 판단 근거로 강제) 또는 앞 단계 직원의 산출물(script-postprocessor→ai-designer 등 체인). **출력**: 전부 `company/outputs/YYYY-MM-DD/<slug>/` 아래 마크다운 파일.

되돌릴 수 없는 액션(외부 발행·전송·결제·대량삭제)은 어떤 직원도 직접 실행하지 않고 `company/approvals/pending/<id>.md`를 만들고 멈춘다(승인 계약, CLAUDE.md §8). 헤드리스 실행 중 판단이 갈리면 질문하지 않고 기본값으로 진행 후 산출물의 "## 확인이 필요한 것" 섹션에 근거를 남긴다(CLAUDE.md §2 — 2026-08-28 product-strategist가 질문만 하고 $0.70 낭비한 사고가 근거).

---

## 4. 런타임 동작 — Claude 종속 지점 전부

### 4-1. Claude를 실제로 호출하는 지점 (가장 중요)

**`runtime/run-agent.mjs` 62~100번째 줄**이 유일한 호출부다.

```js
// runtime/run-agent.mjs:64-82  claude 실행파일 경로 해석
function resolveClaudeBin() {
  if (process.env.CLAUDE_BIN && fs.existsSync(process.env.CLAUDE_BIN)) return process.env.CLAUDE_BIN;
  // ... `which`/`where claude` 로 탐색, 없으면 'claude' / 'claude.cmd'
}

// runtime/run-agent.mjs:92-100
const prompt = `/${agent.slug}`;           // 항상 ASCII 슬래시 명령
const claudeBin = resolveClaudeBin();
const args = [
  '-p', prompt,
  '--output-format', 'json',
  '--model', agent.tier,                   // SKILL.md의 x-tier: haiku|sonnet|opus (별칭, 정확 모델ID 아님)
  '--permission-mode', 'bypassPermissions',
];
if (agent.budgetUsd) args.push('--max-budget-usd', String(agent.budgetUsd));
```

실제 실행은 197~205번째 줄에서 Windows는 `cmd.exe /d /s /c "<line>"`으로, 그 외는 `spawn(claudeBin, args)`로 한다(Windows `claude.cmd`를 Node가 직접 spawn 못 하는 EINVAL 문제 회피). 실행 결과 JSON에서 `usage`, `modelUsage`, `costUsd`, `sessionId`, `numTurns`, `result`를 파싱해 `company/runs/YYYY-MM-DD/<runId>.json`에 기록한다(178~275번째 줄 부근). 인증 실패 시 `claude setup-token`을 안내한다(177~179번째 줄).

`runtime/run-due.mjs`(오늘 예정 직원 일괄 실행, 순서 보장)와 `runtime/sync-schedules.mjs`(SKILL.md의 `x-schedule` → OS 스케줄러 등록)는 이 `run-agent.mjs`를 감싸는 오케스트레이션 레이어이며 자체적으로 claude를 부르지 않는다.

### 4-2. GitHub Actions 스케줄 (`.github/workflows/daily-briefing.yml`)

- `cron: '0 19 * * *'` (UTC) = 04:00 KST 매일 1회. `workflow_dispatch`로 수동 실행도 가능.
- 스텝: 체크아웃 → 인증수단 확인 → Node 22/Python 3.12 세팅 → `npm ci` + **`npm install -g @anthropic-ai/claude-code`**(전역 설치) + pip 패키지 → `.env` 준비(YouTube 키) → `python collector/collect.py` → `node runtime/fetch-subscribers.mjs` → `node runtime/brief-input.mjs` → **`node runtime/run-due.mjs`**(여기서 claude CLI가 실제 호출됨) → git commit & push.
- 커밋 저자: `agents-os bot <junhyukjang1998@gmail.com>`.

### 4-3. 필요한 환경변수 (이름만, 값은 절대 미포함)

| 변수 | 용도 | 어디서 읽나 |
|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code 구독 토큰(무인 인증) — CI에서 동작 확인됨, 추가 과금 없음 | GitHub Secret, `daily-briefing.yml` env |
| `ANTHROPIC_API_KEY` | 위 토큰 대체용(종량 과금) | GitHub Secret, `daily-briefing.yml` env(폴백) |
| `YOUTUBE_API_KEY` | 유튜브 아웃라이어 스코어링(현재 미발급 상태) | GitHub Secret → `collector/.env`, `collector/collect.py` |
| `CLAUDE_BIN` | 로컬에서 claude 실행파일 경로 강제 지정(선택) | `runtime/run-agent.mjs:65` |
| `PORT` | 대시보드 서버 포트(기본 4321) | `apps/dashboard/server.mjs`, `runtime/make-launcher.mjs` |
| `TZ` | Asia/Seoul 고정 | `daily-briefing.yml` |

### 4-4. Claude 종속 지점 전수 목록 (마이그레이션 시 손대야 할 곳)

1. **`runtime/run-agent.mjs`** — claude CLI 직접 호출부(위 4-1). ChatGPT/Codex로 바꾸려면 이 파일의 `resolveClaudeBin()`, `args` 배열, 출력 JSON 파싱(`usage`/`modelUsage`/`costUsd` 필드명이 Claude Code 고유 스키마)을 전부 교체해야 함.
2. **`x-tier: haiku|sonnet|opus`** — 18개 SKILL.md 전체의 frontmatter 필드. `--model` 플래그에 그대로 들어감. 모델 별칭이 Anthropic 체계.
3. **`.github/workflows/daily-briefing.yml`** — `npm install -g @anthropic-ai/claude-code`, `CLAUDE_CODE_OAUTH_TOKEN`/`ANTHROPIC_API_KEY` 환경변수, `claude --version` 헬스체크.
4. **`.claude/skills/<slug>/SKILL.md` 자체가 Claude Code의 "Skill" 개념**(frontmatter로 이름·설명·트리거를 선언하면 Claude Code가 `/slug`로 호출)이다. 다른 에이전트 프레임워크는 이 파일 포맷과 로딩 방식을 모른다 — 프롬프트 내용 자체(절차 지시문)는 이식 가능하지만 "메타데이터로 자동 등록되는 슬래시 명령" 메커니즘은 Claude Code 고유.
5. **`CLAUDE.md`(루트)** — 세션(대화형·헤드리스) 전체에 적용되는 프로젝트 규약. Claude Code가 세션 시작 시 자동으로 읽는 파일이라는 전제로 설계됨(다른 도구는 이 파일을 자동으로 읽지 않음).
6. **프롬프트 관례** `/<slug>`(예: `/checkpoint`, `/news-collector`) — Claude Code의 커스텀 슬래시 명령 문법.
7. **`runtime/lib.mjs`의 비용 추정 로직**(444번째 줄 부근 `TIER_GUESS = { haiku: 0.05, sonnet: 0.4, opus: 1.5 }`, 그 외에는 claude CLI가 돌려주는 실측 `costUsd`를 그대로 합산) — Claude 요금 구조 전제.
8. **`apps/dashboard/server.mjs`의 `/api/continue`**(약 628번째 줄) — 대시보드에서 "Claude Code에서 이어가기"용 명령 문자열을 만들어주는 텍스트 생성기. 실제 API 호출은 아니지만 사용자 워크플로 관례가 Claude Code 전제.
9. **MCP 설정**: 저장소 안에 `.mcp.json`이나 `.claude/settings.json` 등 MCP 서버 설정 파일은 **존재하지 않음**(검색 결과 없음). 단 `email-assistant/SKILL.md`가 "헤드리스에서 쓸 수 있는 도구는 WebSearch, WebFetch, 파일 읽기/쓰기, Bash, obsidian MCP뿐이고 Gmail·캘린더 MCP는 연결돼 있지 않다"고 명시 — MCP 연결 자체는 세션(대화형 Claude Code) 레벨 설정이라 이 저장소 파일에는 없지만 SKILL.md 절차가 그 가용성을 전제로 쓰여 있다.
10. **`company/library/claude-api-model-lifecycle.md`, `claude-api-sdk-stability.md`, `claude-code-opus5-migration.md`, `claude-fable-5-1-pricing.md`, `claude-commerce-agents-2026-09.md`** 등 라이브러리 노트 다수가 Claude/Anthropic 모델 수명주기·가격 변경을 추적하는 내용 — 데이터 성격이라 코드는 아니지만 "Claude 가격/모델이 바뀌면 비용 추정이 흔들린다"는 이 시스템의 리스크를 보여줌.

인증/실행 방식이 Claude Code CLI(`-p`, `--output-format json`, `--permission-mode bypassPermissions`)에 강하게 결합돼 있어, ChatGPT/Codex로 교체 시 **run-agent.mjs 하나가 유일한 진입점**이라는 점은 유리한 설계(다른 곳은 전부 이 파일이 반환하는 표준화된 `record` 객체만 소비함)이나, SKILL.md 파일들이 "Claude Code가 파일을 읽고 절차대로 행동한다"는 실행 모델(도구 호출 능력, Bash/파일 I/O 내장) 자체를 전제로 쓰여 있어 프롬프트 이식만으로는 부족하고 실행 하네스(파일 읽기/쓰기, git, bash 실행 권한)를 동등하게 갖춘 러너가 필요하다.

---

## 5. 최신 상태 (2026-09-11 기준)

### 돌아가고 있는 것

- GitHub Actions 무인 실행이 매일 04:00 KST에 돎(`daily-briefing.yml`). 2026-08-30, 08-31에 실제 성공 기록 확인(`company/runs/`).
- 뉴스 수집(news-collector, 매일) → 아침 브리핑(morning-briefing, 매일) 체인이 active로 정상 가동 중. 2026-09-11 브리핑도 정상 생성됨(비용 $0.7529, 신규 뉴스 242건 수집).
- 구독자 자동 추적(`fetch-subscribers.mjs`, YouTube API 키 없이 채널 페이지 파싱) — 26,100명(2026-09-08 최신 기록).
- 라이브러리 축적이 꾸준히 진행 중 — `LIBRARY.md` 최종 갱신 2026-09-10, 총 45개 노트, 충돌 발견 시 `conflict:` 블록으로 해소하는 패턴이 실제로 작동함(예: gpt-5-pricing-strategy-2026.md).
- planner(월간/주간 계획)도 active로 매주 월요일 도는 중 — `company/plan/2026-09.md`, `2026-W37.md` 존재.

### 미완이고 막힌 것 (핵심 병목)

- **`video-factory-v1`(영상 공장 v1) 이니셔티브 마감이 2026-09-07이었는데 이미 지남.** 첫 마일스톤 "제작 과정 단계별 분해 → `company/factory/coverage.md` 문서화"가 **8일 이상 연속 미착수** — 8단계 전부 ⬜(미파악) 상태로 정지. 2026-09-11 아침 브리핑도 "5일째 이월"로 이 문제를 최상단에 재차 지목함.
- 근본 원인: `coverage.md`는 "대표가 실제 제작 순서를 알려줘야 채울 수 있다"고 명시돼 있어 **에이전트가 대신 조사할 수 없고 대표의 직접 입력이 유일한 해결책**. 이후 마일스톤(노드 정의, 검열 변주 규칙, 파이프라인 재현, 무인 1편 완주, 주 2편 발행)이 전부 이 한 항목에 연쇄적으로 막혀 있음.
- YouTube Data API 키 미발급 — `news-auto-collector`의 아웃라이어 스코어링이 계속 `rss_fallback` 모드로 정체(대표가 5분이면 풀 수 있는 항목으로 여러 번 지목됨, 아직 미해결).
- 별자리 MVP 범위(운세/궁합 중 1개) 미확정 — 제품 트랙들이 여기 막혀 있었으나, 2026-08-31 이후 "메인 골이 트래픽 기계로 확정"되며 관련 트랙 4개(constellation-product-launch, channel-linked-product, ai-conversation-psych-service, product-dev-loop-iteration)가 **archived로 전환**됨(제품은 나중 순서라는 판단).
- 아바타 캐릭터 시안 3종 미확정 — 브리핑·PM이 독립적으로 같은 병목으로 지목했었음(8/31 리뷰 기준. 담당 직원 `ai-designer`가 draft라 실행 주체 자체가 없다는 구조적 문제도 지적됨).
- `project-manager`, `proxy-ceo`, `librarian` 세 직원이 (8/31 CHECKPOINT 시점엔 active였으나) 현재는 **paused**로 바뀌어 있음 — 스케줄에 걸려 있어도 `x-status: draft` 또는 `paused`면 스케줄 실행을 건너뛴다(`run-agent.mjs:57-59`). CHECKPOINT.md·최신 브리핑 사이에 정보 차이가 있으므로 인수인계 시 **`node runtime/checkpoint.mjs` 재실행으로 실제 상태를 다시 집계**해야 함(루트 CHECKPOINT.md는 2026-08-31에서 멈춰 있어 최신이 아님. 저장소 안 `company/checkpoints/`의 최신 파일도 2026-08-29로 더 오래됨).

### 다음 할 일로 명시된 것 (루트 CHECKPOINT.md·최신 브리핑 종합)

1. `coverage.md` 문서화 완료 — 대표의 실제 제작 순서 입력이 유일한 해결책(최우선, 계속 이월 중).
2. 뉴스 수집가의 캐시 읽기량(700K~1,000K 토큰, packet 25배) 원인 규명 — 실행 로그 분석 필요.
3. `proxy-ceo`·`project-manager`도 packet 방식(토큰 절감)으로 전환 — 아직 미적용.
4. YouTube Data API 키 발급(대표 액션).
5. 품질 9축에 실제 영상 점수 입력 — 현재 시드 1건뿐이라 추이 판단 불가.

---

## 6. 핵심 결정·규칙 (CLAUDE.md·company.md 요약)

1. **파일이 진실**: DB 없음, 웹앱은 뷰일 뿐, 모든 변경은 git 커밋.
2. **직원 = SKILL.md 한 장**, frontmatter 계약(`name/description/x-title/x-team/x-tier/x-status/x-schedule/x-triggers/x-order/x-outputs`)을 반드시 지킨다.
3. **헤드리스는 질문 못 함** — 판단이 갈리면 기본값으로 진행하고 근거를 산출물의 "## 확인이 필요한 것" 섹션에 남긴다. 산출물은 무조건 쓴다("할 일 없음"이어도). 되돌릴 수 없는 액션만 예외(승인함行).
4. **메인 골 우선순위 고정**: 영상 공장 v1 → 공장 복제 → 트래픽 수익화. 순서를 뒤집지 않음. 새 작업은 "트래픽 기계를 앞당기는가"로 판단, 아니면 backlog.
5. **AoR 원칙**: 한 영역 = 담당자(SKILL.md) 1명만. 공동 책임 금지. 백업 경로(수동 대체) 명시 필수.
6. **KPI 5~6개 상한 + 역-지표 필수** — 지표 하나만 보면 그 지표에 유리하게만 행동하게 됨(예: 업로드 편수 ↔ 검열 발생 건수).
7. **정보 계층**: 비전(company.md) → 장기목표(goals, 수치) → 전략(initiatives, 마일스톤) → 트랙(tracks) → 프로젝트(projects). target 없으면 진행률을 지어내지 않고 null 반환. 목표↔전략 연결의 유일한 진실은 `initiative.goal` 필드.
8. **산출물 위치 표준**: 에이전트 산출물 `company/outputs/YYYY-MM-DD/<slug>/`, 실행로그 `company/runs/`(러너 자동 기록, 수기 금지), 오늘 할 일 `company/today/`, 라이브러리 `company/library/<slug>.md`.
9. **승인 계약**: 외부 발행·전송·결제·대량삭제·force push는 에이전트가 직접 안 함 → `company/approvals/pending/<id>.md` 생성 후 멈춤. 대표 승인 시 `approved/`로 이동하고 `on_approve` 명령 실행.
10. **잠재/결정 분리**: 모델=판단·글쓰기·요약, 스크립트=세기·계산·진행률·상태전이. 진행률·개수는 절대 모델 눈대중 금지, 파일 스캔 값만 사용.
11. **스킬 승격 루프**: 같은 작업을 두 번 손으로 하면 스킬로 승격.
12. **라이브러리 위생**: 모든 사실에 출처(`source:`), 충돌 시 덮어쓰지 않고 `conflict:` 블록 병기. 가지치기는 librarian 담당.
13. **개수는 하드코딩 금지** — 트랙 수·직원 수·목표 수는 파일 스캔으로 도출.
14. **세션 연속성**: `CHECKPOINT.md`가 복구 문서, 새 세션은 이걸 최우선으로 읽는다. 큰 작업 후 `/checkpoint`로 갱신.
15. **토큰 계측은 모델 호출 없이**: `usageReport()`가 claude CLI가 반환하는 `usage`/`modelUsage`를 합산만 함.
16. **회사 운영 원칙**(company.md): 채용 대신 시스템화, 나만의 정보 라이브러리(퍼스널 AGI 근거), 작업의 스킬 승격, 가려운 곳을 파는 제품. 대표가 직접 지키는 유일한 규칙은 "주 2회 영상 업로드".

---

## 7. 라이브러리 (`company/library/`)

`LIBRARY.md`가 색인 역할을 하는 "재사용 가능한 사실·정책 저장소"다(총 45개 노트, 2026-09-10 최종 갱신). news-collector가 매일, librarian이 매주(현재 paused) 채우고 정리한다. 카테고리는 API/플랫폼 정책, 툴/인프라, 시장 트렌드·철학, 경쟁정보 4갈래. 각 노트는 `source:`(URL/인용) 필드 필수, 색인에 🟢정상/🟡출처미상/🔴충돌/⚪가지치기대기 상태 표시. 정보가 충돌하면 기존 파일을 덮어쓰지 않고 `conflict:` 블록(field/this_note_claimed/other_note/resolved/resolution)을 추가해 이력을 남긴다 — 실제로 `gpt-5-pricing-strategy-2026.md`가 Claude Sonnet 5 가격 관련 서술이 `claude-api-model-lifecycle.md`와 충돌했다가 librarian이 원출처 재확인 후 해소한 사례가 있음.

**대표 항목 5개**:
1. **`great-ceo-within-infrastructure.md`** — 『실리콘밸리 스타트업 플레이북』 4부(19~23장) 요약. 이 회사의 AoR·SPOF·KPI 규칙(CLAUDE.md §4,5)의 직접 출처.
2. **`claude-api-model-lifecycle.md`** — Claude 모델 지원종료 일정(Haiku 4.5 10/15 종료 등), Sonnet 5 가격 9/1 50% 인상, breaking API 변경사항. 비용 추정·모델 선택에 직결.
3. **`youtube-monetization-2026-update.md`** — 유튜브 파트너 프로그램 요건 강화(2027-02-01부터 8천시간 또는 쇼츠 2천만뷰), 조회수 집계 방식 변경. video-factory-v1의 "AI 검열 통과" 합격기준 근거.
4. **`ai-workflow-design-philosophy.md`** — "경쟁우위는 모델이 아니라 워크플로우 설계"라는 트렌드 요약, 대표의 1인 회사 OS 철학과 직접 연결.
5. **`gpt-5-pricing-strategy-2026.md`** — GPT-5.6 가격 전략(경쟁사 동향 추적 사례이자, 위에서 설명한 conflict 해소 프로세스의 실제 사례).

---

## 부록 — 확인해 둘 파일 경로

- 루트 규약/복구: `/home/user/agents-management/CLAUDE.md`, `/home/user/agents-management/CHECKPOINT.md`, `/home/user/agents-management/README.md`
- Claude 호출 핵심: `/home/user/agents-management/runtime/run-agent.mjs` (62~275번째 줄)
- 오케스트레이션: `/home/user/agents-management/runtime/run-due.mjs`, `/home/user/agents-management/runtime/sync-schedules.mjs`
- 무인 실행 워크플로: `/home/user/agents-management/.github/workflows/daily-briefing.yml`
- 직원 정의: `/home/user/agents-management/.claude/skills/*/SKILL.md` (18개)
- 최신 정체 증거: `/home/user/agents-management/company/factory/coverage.md`, `/home/user/agents-management/company/outputs/2026-09-11/morning-briefing/briefing.md`
