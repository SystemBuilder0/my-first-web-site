# Claude Code 세션 타임라인 (2026-07-19 ~ 2026-09-11)

Claude Code Remote 세션 목록 API로 2026-09-11에 조회한 결과다. 총 32개 세션.
"클라우드"는 claude.ai 웹/iOS에서 실행되어 결과가 GitHub 브랜치로 푸시된 세션,
"로컬"은 장준혁님 컴퓨터에서 Claude Code CLI(Remote Control)로 실행되어 기록이
`C:\Users\<이름>\.claude\projects\` 에 JSONL로 남아 있는 세션이다.
로컬 세션의 대화 원문은 이 환경에서 읽을 수 없으므로, `tools/convert_claude_code_transcripts.py`로 직접 변환해야 한다.

| 시작일 | 제목 | 종류 | 모델 | 산출물 위치 / 마지막 상태 |
|---|---|---|---|---|
| 2026-07-19 | 노션 프로젝트 관리 시스템 기획 | 클라우드 | Sonnet 5 | 브랜치 `claude/notion-project-management-planning-hr1zrq`. Notion DB 스키마 재설계, 수식·차트 뷰 추가 중 |
| 2026-07-20 | 일일 AI 뉴스 요약 프로그램 | 클라우드 | Sonnet 5 | 브랜치 `claude/daily-ai-news-summary-85xsr2`. 카드형 홈페이지 + 뉴스 목록/상세 페이지. GitHub Pages 배포 여부 미결 |
| 2026-07-21 | Claude 작업 원칙 문서 | 클라우드 | Sonnet 5 | 브랜치 `claude/working-principles-doc-cli7pu`. 지금의 CLAUDE.md 원형 작성 |
| 2026-07-21 | 음성 인식 타이핑 시스템 | 클라우드 | Opus 5 | 브랜치 `claude/voice-typing-system-0mx79n`. 실시간 스트리밍 모드 README까지, 실행 결과 보고서(Word) 작성 완료. 구글드라이브 `my-first-web-site-claude-voice-typing-system-0mx79n` 폴더에도 사본 있음 |
| 2026-07-21 | 1년 정량적 목표 및 사업 계획 | 클라우드 | Sonnet 5 | 브랜치 `claude/one-year-quantitative-goals-a8ftlg`. 패스트파이브 전화상담 체크리스트 6개 섹션 |
| 2026-07-21 | 뉴스 자동화 시스템 기획 | 클라우드 | Sonnet 5 | 브랜치 `claude/news-automation-planning-smrdpv`. Notion 샘플 생성(2026-07-22), 아카이브 JSON 저장 |
| 2026-07-23 | 사업 계획 및 관계 목표 가이드 | 클라우드 | Opus 4.8 | 브랜치 `claude/business-relationship-goals-l59133`. "무료 미끼→이메일→판매" 자동화 배선도 vs 첫 유닛(불안 워크북) 제작 순서 선택 대기 |
| 2026-07-25 | AI 시대 제품 전략: 수요 추출과 자동화 | 클라우드 | Opus 5 | 브랜치 `claude/ai-product-strategy-automation-lxcp67`. STEP 0 측정 시트 vs STEP 1 실행 매뉴얼 선택 대기 |
| 2026-07-27 | 분산형 사업 시스템 구축 | 클라우드 | Opus 5 | 브랜치 `claude/distributed-business-system-czr2ux`. 텍스트 기반 크리에이터 플라이휠(쓰레드→검증→유튜브/제품), 텍스트 플랫폼을 탐색 엔진으로 재정의 |
| 2026-07-27 | Claude 워크플로우 자동화 | 클라우드 | Opus 5 | 브랜치 `claude/workflow-automation-setup-4vbmyg`. iCloud→Google 캘린더 이전 4가지 방법 |
| 2026-07-27 | 옵시디언 연결 방법 | 클라우드 | Opus 5 | 브랜치 `claude/obsidian-connection-fu2nq1`. 구글드라이브 동기화 2가지 방식 문서화 |
| 2026-07-27 | 하이퍼프레임과 리모션 영상 제작 | 클라우드 | Sonnet 5 | 브랜치 `claude/hyperframe-lemotion-video-sk5tzh`. 동료용 대화 요약 .txt 내보냄 |
| 2026-07-28 | 광고대행 에이전시 3시간 설계 | 클라우드 | Opus 5 | 브랜치 `claude/ad-agency-3hour-plan-jj405l`. 파일럿 영상 완성, 미국 사업 주소 설정 조사. 무제한 모드(웹) vs Mini 모델 계속 선택 대기 |
| 2026-08-04 | 궁합 서비스 개발 내용 추적 | 클라우드 | Opus 5 | 브랜치 `claude/compatibility-service-tracking-bi2h7v`. 사라진 대화 기록 조사, 보존 정책이 원인으로 추정 |
| 2026-08-05 | Claude 코드 프로젝트 재구성 | 클라우드 | Opus 5 | 브랜치 `claude/claude-code-project-rebuild-1fnzc9` (26파일, 1만 줄). Fable 5 전략 심사: 성장 루프를 제품 사양으로 승격하는 조건부 통과 |
| 2026-08-05 | 커플 진단 제품 전략 심사 | 클라우드 | Fable 5 | 브랜치 `claude/couple-diagnosis-strategy-review-ltqhhy`. `docs/05_인수인계_HANDOFF.md` 작성 |
| 2026-08-06 | 서양 점성술 서비스 전략 수립 | 클라우드 | Fable 5 | 브랜치 `claude/western-astrology-strategy-g5x0v3`. 영미권 서양 점성술 피벗 확정, 검증 결과, 인수인계 프롬프트. 이후 ASTRO SPRINT 프로젝트로 이어짐(구글드라이브) |
| 2026-08-21 | 5일 디자인 스프린트 작업 공간 세팅 | 로컬 | Opus 5 | 로컬 기록만 존재 |
| 2026-08-27 | Video automation project setup | 로컬 | Opus 5 | 로컬 기록만 존재 |
| 2026-08-28 | 1인 에이전트 컴퍼니 OS (3개 세션, ~09-10) | 로컬 | Fable 5 / Opus 5 | 저장소 `SystemBuilder0/agents-management`. 마지막 상태: rebase 진행 중, 커밋되지 않은 변경 있음(2026-09-10 22:26 기준) |
| 2026-08-28 | 영상 제작 자동화 대시보드 | 로컬 | Fable 5 | 로컬 기록만 존재 (~09-10) |
| 2026-08-29 | Personal AGI with Obsidian and Ulysses data | 로컬 | Opus 5 | `agents-management` 저장소 관련 |
| 2026-09-01 | 옵시디언 노트 구조화 | 로컬 | Opus 5 | `agents-management` 저장소, main 브랜치 |
| 2026-09-03 | 옵시디언 볼트 에이전트 구축 | 로컬 | Sonnet 5 | `agents-management` 저장소. 미푸시 커밋 2개, 작업 트리 변경 있음(2026-09-03 기준) |
| 2026-09-03 | Personal workout logger app | 로컬 | Opus 5 | 로컬 기록만 존재 |
| 2026-09-06 | YouTube Studio 28일 분석 데이터 | 로컬 | Opus 5 | 로컬 기록만 존재 |
| 2026-09-07 | 컴퓨터 저장공간 관리 | 클라우드 | Opus 5 | 브랜치 `claude/storage-management-gd4ohf`. 931GB C: 드라이브 + 여분 드라이브 기준 이동 계획. ③④ 진단 결과 대기 |
| 2026-09-07 | 옵시디언 콘텐츠 아이디어 정렬 | 클라우드 | Opus 5 | 브랜치 `claude/obsidian-content-ideas-ranking-vexyew`. 12개 카테고리 아이디어 목록, 심리톡톡 + 신규 3채널 동시 런칭 스펙, 미채택 20개 보관 |
| 2026-09-07 | AI 에이전트 OS 폴더 구축 | 클라우드 | Opus 5 | 브랜치 `claude/ai-agent-os-setup-8s2xow`. 골격 커밋(46c4974), 인터뷰 질문(비즈니스 기둥·주 목적·브랜드 보이스·첫 스킬) 답변 대기 |
| 2026-09-07 | 4개 채널 자동화 시스템 구축 및 폴더 정리 | 로컬 | Fable 5.1 | 로컬 기록만 존재 (~09-09) |
| 2026-09-09 | AI 시대 미래 시나리오 영상 | 로컬 | Fable 5.1 | 로컬 기록만 존재 |
| 2026-09-11 | Claude 대화 내용 ChatGPT로 이전 | 클라우드 | Fable 5.1 | 이 문서 묶음 (브랜치 `claude/migrate-context-to-chatgpt-c4ulwf`) |

## 주의

- 위 표의 브랜치 중 일부(`claude/obsidian-content-ideas-ranking-vexyew`, `claude/ai-agent-os-setup-8s2xow`)는 2026-09-11 현재 `origin`에 존재하지 않는다. 세션이 푸시하지 못했거나 삭제된 것으로 보인다. 세션 화면에서 직접 확인이 필요하다.
- 2026-07-19 이전의 claude.ai 일반 대화(코딩 아닌 채팅)는 이 목록에 없다. 그것은 claude.ai 설정의 데이터 내보내기로만 받을 수 있다.
