# Claude → ChatGPT 컨텍스트 이전 가이드

작성: 2026-09-11 (Claude Code 세션 "Claude 대화 내용 ChatGPT로 이전")
대상: 장준혁님. Claude 구독을 해지하고 ChatGPT(및 Codex)로 옮기면서, 지금까지의 대화·작업·원칙을 그대로 이어받게 하는 절차.

## 0. 결론 먼저

**자동으로 옮겨진 것 (이 폴더에 이미 들어 있음)**

| 파일 | 내용 | 출처 |
|---|---|---|
| `00-context-summary.md` | 전체 맥락 한 장 요약. ChatGPT에 가장 먼저 읽힐 파일 | 아래 모든 원천을 종합 |
| `01-branches-summary.md` | GitHub `my-first-web-site` 저장소의 Claude 작업 브랜치 14개 요약 (2026-07-20 ~ 09-10) | GitHub |
| `02-claude-code-sessions-timeline.md` | Claude Code 세션 32개 타임라인 (제목·모델·산출물 위치·마지막 상태) | Claude Code 세션 목록 |
| `04-astro-sprint-summary.md` | ASTRO SPRINT 프로젝트 현재 상태·결정 18건·기술 스택·복구 프롬프트 | 구글드라이브 `docs/WORKLOG.md` 등 |
| `05-agents-management-summary.md` | 1인 에이전트 컴퍼니 OS(`agents-management` 저장소) 구조·직원 18명·Claude 종속 지점 10곳 | GitHub |
| `AGENTS.md` | 작업 원칙 9개 조항을 ChatGPT/Codex용으로 손질한 판 | `CLAUDE.md` |
| `03-chatgpt-custom-instructions.md` | ChatGPT 맞춤 설정·메모리 시드·프로젝트 지침에 붙여 넣을 텍스트 | 이 작업에서 작성 |
| `tools/convert_claude_export.py` | claude.ai 데이터 내보내기(zip/json) → 마크다운 변환기 | 이 작업에서 작성·테스트 |
| `tools/convert_claude_code_transcripts.py` | 내 PC의 Claude Code 세션 기록(JSONL) → 마크다운 변환기 | 이 작업에서 작성·테스트 |

**자동으로 옮길 수 없어서 장준혁님이 직접 해야 하는 것 (해지 전에)**

1. claude.ai 웹/앱의 일반 대화 전체 → 설정에서 데이터 내보내기 (2단계)
2. 내 PC에 남은 Claude Code 로컬 세션 기록 12개 → 변환 스크립트 실행 (3단계)
3. ChatGPT 쪽 설정 3층(맞춤 설정·메모리·프로젝트) 채우기 (4단계)
4. 매일 새벽 4시에 Claude를 호출하는 `agents-management` 자동화를 Codex/OpenAI API로 교체 (5단계)

이 세션(클라우드 컨테이너)에서는 claude.ai 대화 원문과 PC의 로컬 기록에 접근할 수 없다. 실제로 확인한 결과다: 컨테이너의 `~/.claude/projects/`에는 이 세션 기록 1개뿐이었고, claude.ai 대화를 읽는 API나 도구는 이 환경에 없다. 그래서 1·2번은 스크립트를 만들어 두는 것까지가 이 세션이 할 수 있는 최대치였다.

## 1. 컨텍스트가 어디에 있었나 (실제 조회 결과)

| 원천 | 규모 | 해지 후 | 이 폴더에 반영 |
|---|---|---|---|
| claude.ai 일반 대화 (채팅) | 2026-07 이전 것 포함, 개수 미확인 | 계정을 **삭제**하지 않는 한 무료 계정으로 계속 열람 가능. 단 대화 보관 정책으로 사라진 사례가 이미 있었음(8/4 세션 "궁합 서비스 개발 내용 추적") | ✗ 직접 내보내기 필요 |
| Claude Code 클라우드 세션 (claude.ai/code, iOS) | 20개 | 세션 화면은 남지만 컨테이너는 사라짐. 산출물은 GitHub 브랜치에 있음 | ✓ 브랜치 요약 + 타임라인 |
| Claude Code 로컬 세션 (PC, Remote Control) | 12개 | PC의 `C:\Users\<이름>\.claude\projects\`에 JSONL로 남아 있음. 해지와 무관하게 파일은 유지됨 | ✗ 변환 스크립트만 제공 |
| GitHub `SystemBuilder0/my-first-web-site` | 브랜치 15개, 문서 약 1만 9천 줄 | 내 소유. 유지됨 | ✓ |
| GitHub `SystemBuilder0/agents-management` | 마크다운 637KB, 직원(스킬) 18개, 매일 자동 실행 | 내 소유. 유지되지만 **Claude 호출부가 죽음** | ✓ |
| 구글드라이브 ASTRO SPRINT 폴더 | docs 29개, WORKLOG 84KB, AGENTS.md(Codex용, 9/7 변환 완료) | 내 소유. 유지됨 | ✓ |
| Notion (사업 PM 대시보드, 할일, 일일 기록, 뉴스 자동화 DB) | — | 내 소유. 유지됨 | 참조만 |
| Claude 메모리(claude.ai 기억 기능), 프로젝트 지식, 아티팩트 | 미확인 | 해지 시 기능 접근이 제한될 수 있음 | ✗ 2단계에서 함께 내보내기 |
| Claude 루틴(예약 실행) | **0개** (실제 조회 결과) | 해당 없음 | — |

## 2. claude.ai 대화 내보내기 → 변환 → 업로드

1. claude.ai 웹 → 프로필 → **설정 → 개인정보(Privacy) → 데이터 내보내기(Export data)**. 몇 분~몇 시간 뒤 가입 메일(junhyukjang1998@gmail.com)로 다운로드 링크가 온다. zip 안에 `conversations.json`(대화 전체), `projects.json`(프로젝트·지식 파일), `users.json`이 들어 있다. (파일 구성은 Anthropic이 바꿀 수 있으므로 압축을 풀어 실제 파일명을 확인한다.)
2. 메모리 기능을 켜 두었다면, 해지 전에 Claude와 새 대화를 열어 아래 프롬프트를 보내고 결과 코드블록을 `claude-memory-export.md`로 저장한다. (ChatGPT의 메모리 가져오기 화면이 요구하는 것과 같은 형식이다.)

   ```
   내 저장된 메모리와 과거 대화에서 나에 대해 학습한 맥락을 전부 내보내 줘. 특히 지시와 선호는 내 표현 그대로 보존해.
   순서: 1. 지시(앞으로 지키라고 한 규칙) 2. 정체성 3. 경력 4. 프로젝트(프로젝트당 한 항목: 무엇인지, 현재 상태, 핵심 결정) 5. 선호.
   각 항목은 [YYYY-MM-DD] - 내용 형식으로 한 줄씩, 오래된 순. 날짜 모르면 [unknown]. 전체를 코드블록 하나로 감싸고, 끝에 이것이 전부인지 남은 게 있는지 말해 줘.
   ```

3. 변환 (Python 3.8 이상이면 됨. 추가 설치 없음):

   ```
   python tools/convert_claude_export.py "다운로드받은파일.zip" --out claude-export-md
   ```

   결과: `claude-export-md/index.md`(목차), `conversations/`(대화별 파일), `bundles/all-conversations-001.md …`(400KB 단위 뭉치). ChatGPT 프로젝트에는 **bundles 폴더의 파일들**을 올린다. 뭉치 하나가 너무 크다고 거부되면 `--max-kb 200`으로 다시 만든다.

4. 변환 전에 zip 안 `projects.json`을 열어 보고, Claude 프로젝트에 올려 두었던 지식 파일이 있으면 그 원본도 따로 챙긴다.

## 3. PC의 Claude Code 로컬 기록 변환

Remote Control로 PC에서 돌린 12개 세션(옵시디언 볼트 에이전트, 4개 채널 자동화, 영상 제작 자동화 대시보드, AI 시대 미래 시나리오 영상, Personal workout logger, YouTube Studio 분석 등. 목록은 `02-…timeline.md`)은 PC에만 기록이 있다.

```
python tools/convert_claude_code_transcripts.py --root "C:\Users\<사용자이름>\.claude\projects" --out claude-code-md
```

결과 구조는 2단계와 같다(`index.md`, `sessions/<프로젝트폴더>/…`, `bundles/all-sessions-001.md …`). 도구 호출과 파일 출력은 `[도구: 이름]` 한 줄로 축약되고, 사용자 발화와 Claude 답변 텍스트만 남는다. 이 스크립트는 이 세션의 실제 JSONL로 테스트했다.

또한 PC의 `~/.claude/CLAUDE.md`(전역 원칙 파일)와 프로젝트별 `CLAUDE.md`, `.claude/skills/`, `.claude/agents/` 폴더가 있으면 함께 복사해 둔다. Codex는 같은 위치의 `AGENTS.md`를 읽으므로 파일명만 바꿔 두면 된다.

## 4. ChatGPT 설정 채우기

`03-chatgpt-custom-instructions.md`에 붙여 넣을 텍스트가 전부 있다. 순서:

1. **맞춤 설정** 4칸 채우기 (A절).
2. 새 대화에서 **메모리 시드 프롬프트** 보내기 (B절). 2~3회로 나눠 보내고, 설정 → 메모리 관리에서 저장 확인.
3. **프로젝트 "장준혁 컨텍스트"** 만들고 이 폴더의 문서 6개 + 2·3단계에서 만든 bundles 파일 업로드 (C절).
4. 프로젝트 안에서 C절의 첫 대화 프롬프트로 "요약해서 보여줘" → 틀린 부분 정정 → "정정을 메모리에 저장해".

Codex(CLI·클라우드)를 Claude Code 대신 쓸 계획이면, 각 저장소 루트에 `AGENTS.md`를 둔다. `my-first-web-site`용은 이 폴더의 `AGENTS.md`를 루트로 복사하면 되고, ASTRO SPRINT 폴더에는 9/7에 이미 `AGENTS.md`가 있다. `agents-management`는 5단계 참조.

## 5. agents-management 자동화 교체 (해지 전에 반드시)

`.github/workflows/daily-briefing.yml`이 매일 04:00 KST에 `npm install -g @anthropic-ai/claude-code`를 하고 `CLAUDE_CODE_OAUTH_TOKEN`으로 Claude를 호출한다. **해지하면 이 토큰이 무효가 되어 워크플로가 매일 실패한다.**

교체 지점은 `05-agents-management-summary.md` 4절에 줄 번호까지 정리돼 있다. 요점:

- 유일한 호출부는 `runtime/run-agent.mjs`의 `resolveClaudeBin()`과 `args` 배열(`claude -p /<slug> --output-format json --model <tier> --permission-mode bypassPermissions`). 이것을 `codex exec` 또는 OpenAI API 호출로 바꾸고, 결과 JSON 파싱(`usage`, `modelUsage`, `costUsd`, `sessionId`)을 새 응답 형식에 맞춘다.
- 18개 `SKILL.md`의 `x-tier: haiku|sonnet|opus`를 OpenAI 모델명으로 매핑하는 표 하나를 `runtime/lib.mjs`에 둔다. `TIER_GUESS` 비용 상수도 같이 고친다.
- 워크플로에서 Claude Code 설치·헬스체크 스텝을 Codex CLI 설치로 바꾸고, GitHub Secret에 `OPENAI_API_KEY`를 넣는다.
- `/<slug>` 슬래시 명령 관례는 Claude Code 고유다. Codex에서는 SKILL.md 본문을 프롬프트로 직접 넘기는 방식으로 바꿔야 한다.
- 당장 교체가 어렵다면 워크플로를 먼저 **비활성화**(Actions 탭 → 워크플로 → Disable)해서 실패 알림이 매일 오는 것을 막는다.

이 교체는 이 세션에서 하지 않았다. 이유: 이 컨테이너에 Codex CLI와 OpenAI 키가 없어 실행 검증을 할 수 없고, 검증 없는 코드를 자동 실행되는 저장소에 밀어 넣는 것은 원칙 2(검증 후 완료 선언)에 어긋난다.

## 6. 해지 전 체크리스트

- [ ] 2단계 데이터 내보내기 요청 → 메일 도착 → zip 보관 (드라이브에도 복사)
- [ ] 메모리 내보내기 프롬프트 실행 → 결과 저장
- [ ] Claude 프로젝트에 올린 지식 파일 원본 확보
- [ ] Claude Code 클라우드 세션 중 미푸시 작업 확인: `옵시디언 콘텐츠 아이디어 정렬`(9/7)과 `AI 에이전트 OS 폴더 구축`(9/7) 세션의 브랜치가 origin에 없다. claude.ai/code에서 두 세션을 열어 결과를 복사하거나 푸시한다.
- [ ] `1인 에이전트 컴퍼니 OS` 로컬 세션(9/10 22:26 기준 rebase 진행 중, 미커밋 변경 있음)과 `옵시디언 볼트 에이전트 구축`(미푸시 커밋 2개) → PC에서 `git status`로 확인 후 커밋·푸시
- [ ] 3단계 로컬 기록 변환
- [ ] 4단계 ChatGPT 설정
- [ ] 5단계 워크플로 교체 또는 비활성화
- [ ] Claude 데스크톱/CLI에 저장된 MCP 설정(`claude mcp list`)이 있으면 목록을 메모 (Codex의 `~/.codex/config.toml`에 같은 서버를 등록할 수 있다)
- [ ] 마지막으로 구독 해지. **계정 삭제는 하지 않는다** (대화 열람 권한이 남아 있어야 나중에 빠진 것을 찾을 수 있다)

## 7. 한계와 확실하지 않은 것

- claude.ai 내보내기 zip의 정확한 파일 구성과 JSON 키 이름은 시점에 따라 바뀔 수 있다. 변환 스크립트는 알려진 키 이름을 여러 개 시도하도록 관대하게 짰지만, 실행해서 "대화 0건"이 나오면 `conversations.json`의 첫 항목을 열어 키 이름을 확인하고 스크립트의 `first(...)` 호출부에 추가하면 된다.
- ChatGPT의 맞춤 설정 글자 수, 프로젝트당 파일 수, 파일 크기 제한은 이 세션에서 실측하지 못했다. 화면의 안내를 따른다.
- 이 폴더의 요약 문서 4개(01·02·04·05)는 원본을 실제로 읽은 하위 에이전트(Sonnet 5)가 작성하고 상위 모델이 검토했다. 원본과 다른 부분을 발견하면 원본이 맞다.
- 이 폴더의 사본은 구글드라이브 `ChatGPT 이전 팩 (2026-09-11)` 폴더에도 올려 두었다. GitHub 브랜치 `claude/migrate-context-to-chatgpt-c4ulwf`와 내용이 같다.
