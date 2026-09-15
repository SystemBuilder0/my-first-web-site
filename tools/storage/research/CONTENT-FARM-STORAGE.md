# "유튜브 공장" / AI 영상 자동화 파이프라인의 저장공간 관리 실사례 조사

조사 시점: 2026년 9월. 가격·정책은 모두 이 시점 기준이며, 변동 가능성이 있으므로 실제 도입 전 각 공식 가격 페이지에서 재확인 권장.

조사 방법 한계 고지: 이번 조사 환경에서는 WebSearch(검색+요약)만 가능했고, 개별 URL 원문을 직접 열어보는 WebFetch는 네트워크 정책상 차단되어 있었다(Backblaze, Cloudflare 공식 문서, n8n.io, 각종 가격비교 블로그 등 대부분 도메인 접속 불가). 단, GitHub raw 콘텐츠는 예외적으로 접근 가능해 오픈소스 저장소 1건은 원문을 직접 확인했다. 나머지는 WebSearch가 반환한 요약과 인용문에 의존했으므로, 표시된 출처 URL을 통해 원문 재확인을 권장한다.

---

## 요약 (핵심 발견)

1. **"유튜브 공장" 저장 인프라를 상세히 공개한 신뢰할 만한 1차 자료는 거의 없다.** 검색되는 콘텐츠 대부분이 코스/템플릿 판매용 마케팅 페이지(Gumroad 등)이며, 저장공간 관리 자체를 다룬 실사례 글은 매우 드물다. 이는 이번 조사의 중요한 발견이자 한계다.
2. 실제로 확인되는 소규모~중규모 운영 패턴은 **"로컬 폴더 구조(슬러그별 디렉터리) + FFmpeg 로컬 렌더링 + n8n/API로 업로드"** 조합이 많고, 클라우드 오브젝트 스토리지를 처음부터 전제하는 사례는 상대적으로 적다. 오픈소스 자동화 도구(`yt-faceless-automation`)의 실제 코드가 이를 보여준다.
3. 22개 채널을 굴리는 실제 사례(Fiffig Productions, VideoNest 기반)가 확인되며 "격일 500개 영상 발행" 규모에서는 다채널을 1급 시민으로 다루는 인프라가 필요하다고 언급되지만, 스토리지 세부 구성은 공개되지 않았다.
4. AI 영상 생성(Runway/Pika/Kling 등)과 TTS(ElevenLabs) 쪽은 **API 결과물의 로컬 보관 기간·자동 삭제 정책에 대한 구체적 공개 정보를 찾지 못했다** — 각 서비스 공식 문서 직접 확인이 필요한 영역으로 남겨둔다.
5. 클라우드 오브젝트 스토리지 3사(R2/B2/S3) 가격은 검색 결과 다수가 일치된 수치를 보고했다: R2 표준 스토리지 약 $15.36/TB/월 + egress 무료, B2 약 $6/TB/월 + 3배 egress 무료(또는 Overdrive $15/TB 무제한), S3 표준 약 $23/TB/월(50TB 이하 구간) + egress 최대 $90/TB. 이 격차, 특히 egress 정책 차이가 "영상 파일을 자주 재생/재다운로드하는" 워크플로에서 실질적 비용 차이를 만든다는 서술이 여러 출처에서 반복됐다.
6. **retention(자동 정리) 자동화의 실제 구현 사례는 n8n 템플릿 마켓플레이스에서 명확히 확인된다** — "Cloudflare R2 파일 중 14일 지난 것을 매일 자동 삭제 + 텔레그램 알림" 템플릿이 실존한다. FFmpeg/렌더링 파이프라인 쪽은 범용적으로 `find -mtime +N -delete` 방식의 cron 정리가 표준적으로 언급된다.
7. 로컬 HDD가 TB당 순수 저장 비용은 가장 싸지만(감가상각 기준), NAS는 초기비용 회수에 1~3년 걸리고, 클라우드는 용량이 작을 때(2TB 미만) 유리하다는 일반 비교가 여러 출처에서 나온다. 다만 이 비교들은 "영상 자동화 파이프라인" 전용이 아니라 일반 소비자/사무용 스토리지 비교 글이라는 점에 유의해야 한다(간접 적용).

---

## 1. 다채널 대량 운영(faceless YouTube automation) 실사례

### 1-1. 확인된 것

- **오픈소스 저장소 `collij22/yt-faceless-automation`** (GitHub, 실제 코드 확인함): Claude 서브에이전트 + n8n + Python 3.12 + FFmpeg 기반 파이프라인. 스토리지 구조는 전부 **로컬 파일 시스템** 기준이다.
  - `content/{slug}/script.md`, `content/{slug}/audio.wav`(또는 `.mp3`), `assets/`, `content/{slug}/final.mp4` 등 슬러그(작업 단위)별 로컬 디렉터리에 산출물을 쌓는 구조.
  - 클라우드 스토리지(S3/R2/Drive)를 기본 아키텍처로 명시하지 않았고, n8n 웹훅으로 TTS/업로드를 연동하는 정도.
  - 출처: https://raw.githubusercontent.com/collij22/yt-faceless-automation/main/README.md (GitHub 원문 직접 확인)

- **Fiffig Productions 사례** (VideoNest 블로그에서 언급): 22개 채널을 운영하며 격일로 최대 500개 영상을 발행한다고 소개됨. "22개 채널을 다루려면 다채널 운영을 애프터소트가 아니라 1급 설계 요소로 취급하는 인프라가 필요하다"는 서술이 있으나, **스토리지 백엔드(로컬/클라우드 여부, 용량, 보존 기간)는 이 글에서 구체적으로 공개되지 않았다.**
  - 출처: https://videonest.co/blog/how-to-manage-multiple-youtube-channels/

- **n8n 기반 파이프라인 일반 패턴** (여러 가이드에서 반복 확인): 토픽을 구글시트에 넣으면 → GPT가 스크립트 생성 → 영상 렌더링 API 호출 → 렌더 상태 폴링 → 완성된 MP4 다운로드 → 유튜브 업로드. 저장 연동 지점으로 "Google Drive, Dropbox, S3 bucket, 또는 로컬 업로드 폴더" 중 택1이 언급됨 — 즉 **클라우드/로컬 선택은 운영자 재량이며 업계 표준이 하나로 수렴돼 있지 않다.**
  - 출처: https://dev.to/grewup/n8n-workflow-that-auto-creates-and-uploads-youtube-videos-while-you-sleep-8dp , https://agentforeverything.com/n8n-youtube-automation/

- **초보자용 가이드의 일반적 권고**: "처음엔 클라우드 툴로 시작하고, 월 50개 이상 영상을 만들고 수익이 하드웨어 비용을 정당화할 때 로컬 AI 영상 생성 셋업으로 전환하라"는 조언이 확인됨. Minio를 로컬 PC나 VPS에 컨테이너로 띄워 S3 호환 퍼블릭 버킷을 직접 운영하는 방식도 언급됨.
  - 출처: (WebSearch 요약, 원문 미확인) autoclips.app 계열 가이드 — **신뢰도 낮음(마케팅성 가이드 페이지), 구체적 수치·사례 근거 없이 일반론 서술.**

### 1-2. 신뢰도 판단

- 검색 상위에 뜨는 "faceless youtube automation" 관련 페이지의 절반 이상이 **Gumroad 판매 페이지, 유료 코스 랜딩페이지, SEO 목적의 "완벽 가이드" 블로그**였다. 이들은 저장공간 관리를 실질적으로 다루지 않거나, 다뤄도 검증되지 않은 일반론 수준이다.
- "Noah Morris"라는 이름이 "20개 이상 채널, 누적 20억 조회수"로 언급되는 사례가 나왔으나, 이는 vidiq 블로그의 소개 문구이며 **본인이 직접 스토리지 운영 방식을 밝힌 인터뷰나 1차 자료를 찾지 못했다.** 출처 미확인 수준으로 분류.
- 결론: **"유튜브 공장 운영자가 스토리지를 어떻게 관리하는지"를 구체적 수치(디스크 용량, 비용, 삭제 주기)와 함께 공개한 신뢰할 만한 실사례는 이번 조사에서 발견하지 못했다.** 이는 정보가 없다기보다, 이 정보가 공개적으로 잘 문서화되지 않는 영역이라는 뜻으로 보인다.

---

## 2. AI 영상 파이프라인의 저장공간 특성

- **중간 산출물이 최종본보다 커지는 이유**: 업스케일 전 프레임을 무손실/저손실 포맷(PNG 시퀀스, ProRes 등)으로 저장한 뒤 나중에 압축해서 배포하는 것이 권장되는 워크플로로 확인된다. "먼저 압축 코덱으로 업스케일하면 압축 아티팩트가 화질 개선 효과를 상쇄한다"는 이유 때문에, 프로덕션 단계에서는 무손실 중간 포맷을 쓰고 이게 최종 파일보다 훨씬 크다.
  - 출처: (WebSearch 요약, 원문 미확인) 관련 AI 업스케일 가이드류 — 구체적 배율 수치(예: "N배 커진다")는 확인하지 못했다. **정성적 서술만 확인, 정량적 수치는 출처 미확인.**

- **ComfyUI 등 로컬 생성 파이프라인의 임시파일 누적 문제는 실제로 존재하고, 커뮤니티 대응 도구가 나와 있다**:
  - `ComfyUI-TempFileDeleter`라는 커스텀 노드가 실제 GitHub에 존재하며, "반복 실행 시 임시파일이 쌓여 저장공간을 잠식하므로 주기적으로 지워야 한다"는 문제의식을 명시.
    - 출처: https://github.com/neeltheninja/ComfyUI-TempFileDeleter
  - 대안으로 임시 디렉터리를 심볼릭 링크로 시스템 `/tmp`(별도 관리되는 영역)로 돌리는 방식도 확인됨.
    - 출처: (WebSearch 요약) comfyai.run 문서

- **FFmpeg 기반 자동화의 임시파일 누적**: FFmpeg 등 렌더링 프로세스가 `/tmp`에 임시파일을 남기고 이게 쌓여 디스크가 가득 차 에러를 일으키는 문제가 실제로 보고됨. 대응은 `find /tmp -type f -mtime +7 -user <user> -execdir rm -- {} \;` 같은 **cron 기반 주기 삭제**가 표준적으로 제시된다.
  - 출처: https://curationexperts.github.io/recipes/every_project/cleanup_temp_files.html

- **대규모(엔터프라이즈급) AI 영상 생성의 저장 규모**: "원본 촬영본, 프레임 단위 학습 데이터, 모델 체크포인트, 최종 렌더가 주 단위로 수백 테라바이트에 달할 수 있다"는 서술이 확인됨(대형 조직/파운데이션 모델 학습 맥락이며, 개인/소규모 유튜브 자동화와는 스케일이 다름 — 참고용으로만 인용).
  - 출처: Backblaze 관련 블로그 (WebSearch 요약, 원문 직접 열람 실패 — 네트워크 정책상 backblaze.com 접속 차단)

- **렌더 캐시 전략**: "동일한 요청이 다시 들어오면 재렌더링하지 않고 캐시된 결과를 서빙"하는 방식이 비용 절감에 유효하다는 일반 원칙이 확인됨. ElevenLabs TTS 자동화 패턴에서도 "콘텐츠 해시로 캐싱해 동일한 대사를 중복 생성하지 않는다"는 구체적 권장 패턴이 확인됨.
  - 출처: (WebSearch 요약) webfuse.com ElevenLabs 치트시트류

---

## 3. 클라우드 우선 전략 (비용표 포함)

**주의**: 아래 가격은 모두 WebSearch가 반환한 요약 수치이며, 원문 공식 페이지(Cloudflare, Backblaze, AWS)는 이번 세션 네트워크 정책상 직접 열람이 차단되어 재검증하지 못했다. 여러 독립 출처(가격비교 사이트)에서 반복적으로 같은 숫자가 나왔고, 이는 실제 공개된 Cloudflare/Backblaze/AWS 공식 가격과도 부합하는 값들이라 신뢰도는 높은 편이나, **실제 계약 전 공식 페이지에서 최종 확인이 필요하다.**

| 서비스 | 표준 스토리지 (TB/월) | Infrequent/저빈도 (TB/월) | Egress(인터넷 반출) | 비고 |
|---|---|---|---|---|
| Cloudflare R2 | 약 $15.36 ($0.015/GB) | 약 $10.24 ($0.01/GB) | **$0 (무료, 무제한, 무비율제한)** | Class A(쓰기) $4.50/백만건, Class B(읽기) $0.36/백만건. 무료 티어 10GB + 월 100만 Class A/1000만 Class B |
| Backblaze B2 | 약 $6.90~$6 ($0.006~0.0069/GB) | — | 월 저장량의 3배까지 무료, 초과분 $0.01/GB | Cloudflare/Fastly/bunny.net 등 파트너 CDN 경유 시 무제한 무료 egress(Bandwidth Alliance). B2 Overdrive는 $15/TB에 무제한 무료 egress |
| AWS S3 Standard | 약 $23 (50TB 이하 구간, $0.023/GB) | 이후 구간 $22~$21/TB로 체감 | 월 100GB 무료 이후 $0.09/GB(약 $90/TB), 물량 늘수록 $0.085→$0.07→$0.05/GB로 체감 | 리전별 상이(위 수치는 US East 기준) |

- 출처:
  - R2: https://mecanik.dev/en/posts/cloudflare-r2-pricing-explained-real-costs-vs-s3-and-backblaze/ , https://egresscost.com/cloudflare/ , https://themedev.net/blog/cloudflare-r2-pricing/ (모두 WebSearch 요약, 3개 이상 출처가 동일 숫자로 수렴)
  - B2: https://www.backblaze.com/cloud-storage/pricing (WebSearch 요약), https://leanopstech.com/blog/backblaze-b2-pricing-2026/ , https://comparebestai.com/tools/backblaze-b2
  - S3: https://filebase.com/blog/aws-s3-pricing-in-2026-what-youll-actually-pay/ , https://www.cloudzero.com/blog/s3-pricing/

### R2 무료 egress가 영상 워크플로에서 갖는 의미

- 영상 자동화 파이프라인은 특성상 "렌더 → 업로드 → (필요시) 재다운로드해서 후처리/재검토 → 재업로드"처럼 **같은 파일을 여러 번 오가며 처리**하는 경우가 흔하다. S3처럼 반출(egress)에 과금하는 구조에서는 이 반복 다운로드 자체가 누적 비용이 되지만, R2는 반출이 무료이므로 "다운로드해서 재작업하는" 패턴에서 비용 예측이 단순해진다는 서술이 다수 출처에서 공통적으로 강조됐다.
- B2도 파트너 CDN(Cloudflare 등) 경유 시 무료 반출이 가능해 유사한 이점을 제공한다는 서술이 확인됨.
- 다만 이 "의미"에 대한 서술은 대부분 R2/B2를 홍보하는 성격의 비교 블로그에서 나온 것이라, **객관적 3자 검증이라기보다는 벤더 우호적 프레이밍일 가능성**을 감안해야 한다.

### "로컬은 작업 중인 것만, 완료본은 즉시 업로드 후 로컬 삭제" 패턴

- 이 패턴 자체를 명시적으로 "이렇게 운영한다"고 밝힌 실사례 인터뷰는 발견하지 못했다.
- 다만 이 패턴을 구현하는 **실제 자동화 템플릿**은 확인된다 (섹션 4 참조: n8n R2 auto-cleanup 템플릿).
- 일반적인 영상 프로덕션 워크플로 가이드(MASV, OWC 등 영상 업계 스토리지 블로그)에서도 "워치 폴더로 업로드 완료 후 로컬 파일을 삭제할 수 있으나, 반드시 사본이지 원본이 아님을 확인해야 한다"는 주의사항이 반복적으로 나온다 — 이는 유튜브 자동화 특화 내용은 아니고 일반 영상 업계 가이드다.
  - 출처: https://massive.io/workflow/back-up-and-video-storage-workflow/ (WebSearch 요약)

---

## 4. 자동 정리(retention) 구현 사례

- **가장 구체적이고 신뢰도 높은 실사례: n8n 워크플로 템플릿 마켓플레이스**
  - "Auto-cleanup of Cloudflare R2 files older than 2 weeks (+ Telegram notifications)" — 매일 스케줄로 실행, R2 버킷에 S3 호환 API로 접속, 14일 지난 파일을 필터링해 삭제, 삭제할 때마다 텔레그램 알림 전송. **이건 실제 배포 가능한 템플릿으로 마켓플레이스에 등록되어 있다.**
    - 출처: https://n8n.io/workflows/4418-auto-cleanup-of-cloudflare-r2-files-older-than-2-weeks-telegram-notifications/ (WebFetch 직접 열람은 차단되어 WebSearch 요약에 의존)
  - "Automate workflow & credentials backup to S3 with retention management" — S3 백업을 하되 설정 가능한 보존 기간(기본 31일) 이후 자동 삭제. 유튜브 영상 파일용은 아니고 n8n 자체 백업용이지만, **동일한 "스케줄 + 나이 필터링 + 삭제" 패턴**을 보여주는 실사례.
    - 출처: https://n8n.io/workflows/6436-automate-workflow-and-credentials-backup-to-s3-with-retention-management/

- **범용 cron 기반 정리**: `find <dir> -type f -mtime +N -delete` 패턴이 FFmpeg/임시파일 정리 커뮤니티 글에서 표준적으로 제시됨. n8n 커뮤니티 포럼에서도 "30분마다 파일을 다운로드해서 업로드하는데 10MB 넘는 파일이 쌓여 디스크 부족 에러가 난다"는 실제 문제 제기 스레드가 있고, 해결책은 "업로드 후 다운로드한 파일을 삭제하라"는 것.
  - 출처: https://community.n8n.io/t/delete-downloaded-files-in-workflow-after-ran/33043

- **GitHub Actions의 아티팩트 보존 정책**: `actions/upload-artifact`의 `retention-days` 파라미터로 개별 아티팩트 보존 기간을 지정 가능(기본 90일, 조직 설정으로 변경 가능). 오래된 아티팩트를 API로 지우는 서드파티 액션(Marketplace "Delete Artifacts")도 존재. 이는 영상 자동화 전용은 아니지만, "GitHub Actions에서 영상 산출물을 아티팩트로 잠깐 보관했다가 정리"하는 파이프라인에 그대로 적용 가능한 실제 기능이다.
  - 출처: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts

- **Zapier/Make**: "Dropbox 파일을 지정 기간 후 자동 삭제", "14일 지난 파일을 삭제해 백업을 깔끔하게 유지"하는 자동화가 가능하다는 서술은 확인되나, 유튜브 영상 자동화에 특화된 구체적 공개 템플릿(레시피 ID 등)까지는 확인하지 못했다. 일반론 수준.
  - 출처: https://zapier.com/blog/organize-files-with-automation/ (WebSearch 요약)

---

## 5. 비용 비교표 (TB당 비용, 2026년 9월 기준)

| 방식 | 초기/월 비용 (TB당) | 특징 | 신뢰도 |
|---|---|---|---|
| 로컬 외장 HDD | 4TB $100~140, 5TB $120~150 (일회성 구매) → 감가상각하면 TB당 연 비용 최저 | 백업/이중화 없음, 관리 인건비 별도, 물리적 장애 위험 | 중간 (가격비교 사이트 출처, 일반 소비자향) |
| NAS (2-bay, 8TB×2 미러) | 초기 $600~700, 실사용 8TB | 8TB를 클라우드로 하면 월 $16~56이므로 1~3년이면 하드웨어비 회수 | 중간 |
| NAS (4-bay, 8TB×4) | 초기 약 $1,200 | RAID5 약 24TB, RAID6 약 16TB 가용 | 중간 |
| Cloudflare R2 | 약 $15.36/TB/월 (표준) | egress 무료 | 중간~높음 (복수 출처 수렴, 공식 페이지 직접 재검증은 못함) |
| Backblaze B2 | 약 $6~6.9/TB/월 | 3배 무료 egress, 파트너 CDN 경유 시 무제한 무료 | 중간~높음 |
| AWS S3 Standard | 약 $23/TB/월 (50TB 이하) | egress 최대 $90/TB, 3사 중 가장 비쌈 | 중간~높음 |

**해석**: 순수 저장 비용만 보면 로컬 HDD가 압도적으로 싸지만, 이는 이중화·백업·관리 인건비를 뺀 수치다. "다운로드/재작업이 잦은 영상 자동화 워크플로"에서는 egress 비용까지 합산해야 진짜 총비용이 나오는데, 이 지점에서 S3 대비 R2/B2가 유리하다는 서술이 여러 출처에서 일관되게 나타난다. 다만 "몇 TB 이상이면 어느 쪽이 항상 유리하다"는 손익분기점 계산은 이번 조사에서 유튜브 자동화 파이프라인 전용으로 산출된 자료를 찾지 못했다 — 일반 소비자/사무용 스토리지 비교 자료를 참고값으로만 인용한 것임을 밝힌다.

---

## 6. 신뢰도 낮은 정보 목록 (마케팅성 주장 등)

- **Gumroad 판매 페이지들** (`agentcircle.gumroad.com`, `drophustlee.gumroad.com`, `rediseautotube.gumroad.com`, `jamesking21.gumroad.com` 등): "완전 자동화", "잠자는 동안 수익 창출" 류 문구가 반복되나 스토리지 운용 세부사항은 전무. 판매 목적 콘텐츠로 분류, 사실관계 검증 불가.
- **"Noah Morris — 20개 이상 채널, 20억 뷰"** (vidiq 블로그 인용): 1차 인터뷰나 본인 발언을 확인하지 못함. 과장 가능성 있는 소개 문구로 취급, **출처 미확인** 수준.
- **"YouTube Automation 코스/에이전시" 관련 사기 경고**: Reddit·Trustpilot·미디엄 등에서 "Grow Channels($6,800 코스)를 MLM 컬트라 부른다", "NYT 조사에서 $155,000 손실 사례" 등이 언급됐으나, 이는 이번 조사 주제(스토리지)와 직접 관련은 없고 **"유튜브 공장" 업계 전반의 신뢰도를 가늠하는 맥락 정보**로만 참고할 것. 코스 판매 사업자들의 마케팅과 실제 운영 후기는 명확히 구분해서 읽어야 한다는 사용자 요청에 부합하는 근거로 남겨둠.
- **"Minio를 로컬 PC/VPS에 띄워 처음부터 확장 가능한 스토리지로 쓰라"는 조언, "월 50개 영상 이상이면 로컬 전환"** 같은 수치: 출처가 마케팅성 "완벽 가이드" 블로그(autoclips.app류)이며, 실측 근거나 사례 링크가 없는 일반론. **신뢰도 낮음.**
- **중간 산출물이 "최종본보다 훨씬 커진다"는 정성적 주장의 구체적 배율(예: 10배, 100배)**: 이번 조사에서 정량적 수치를 제시하는 출처를 찾지 못했다. 정성적 방향성만 확인, 배율 수치는 쓰지 않았다.
- **대형 조직 AI 영상 학습 파이프라인이 "주당 수백 TB"**라는 Backblaze발 서술: 이는 파운데이션 모델 학습/대형 스튜디오 맥락으로 보이며, 개인·소규모 유튜브 자동화 운영자 스케일과는 다르다. 문맥을 오인해 일반 유튜브 자동화 운영자에게 그대로 적용하면 과장이 된다 — 원 출처(backblaze.com)를 직접 열람하지 못해 정확한 맥락 확인이 안 된 상태다.

---

## 7. 참고 링크 목록

### 다채널 운영
- https://raw.githubusercontent.com/collij22/yt-faceless-automation/main/README.md (GitHub, 원문 직접 확인)
- https://videonest.co/blog/how-to-manage-multiple-youtube-channels/
- https://dev.to/grewup/n8n-workflow-that-auto-creates-and-uploads-youtube-videos-while-you-sleep-8dp
- https://agentforeverything.com/n8n-youtube-automation/
- https://community.n8n.io/t/automation-for-youtube-long-video-creation-from-scratch-to-upload/282010
- https://gpt-lab.eu/youtube-automation-llm-n8n/
- https://vidiq.com/blog/post/start-youtube-automation-channel/

### AI 영상 파이프라인/임시파일
- https://github.com/neeltheninja/ComfyUI-TempFileDeleter
- https://comfyai.run/documentation/TempCleaner
- https://curationexperts.github.io/recipes/every_project/cleanup_temp_files.html
- https://www.backblaze.com/blog/three-hidden-costs-in-ai-video-storage/ (직접 열람 실패, WebSearch 요약만)
- https://www.backblaze.com/blog/scaling-generative-ai-video-depends-on-your-data-egress-strategy/ (직접 열람 실패, WebSearch 요약만)

### 클라우드 가격
- https://mecanik.dev/en/posts/cloudflare-r2-pricing-explained-real-costs-vs-s3-and-backblaze/
- https://egresscost.com/cloudflare/
- https://themedev.net/blog/cloudflare-r2-pricing/
- https://www.backblaze.com/cloud-storage/pricing
- https://leanopstech.com/blog/backblaze-b2-pricing-2026/
- https://filebase.com/blog/aws-s3-pricing-in-2026-what-youll-actually-pay/
- https://www.cloudzero.com/blog/s3-pricing/

### Retention 자동화 실사례
- https://n8n.io/workflows/4418-auto-cleanup-of-cloudflare-r2-files-older-than-2-weeks-telegram-notifications/
- https://n8n.io/workflows/6436-automate-workflow-and-credentials-backup-to-s3-with-retention-management/
- https://community.n8n.io/t/delete-downloaded-files-in-workflow-after-ran/33043
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts
- https://zapier.com/blog/organize-files-with-automation/

### 로컬/NAS 비교
- https://www.techverdict.io/articles/nas-vs-cloud-storage-2026
- https://www.slashgear.com/1933381/nas-vs-cloud-storage-which-is-cheaper/
- https://tuskbackup.com/blog/cheapest-storage-per-gb-2026

### 업계 신뢰도 관련(맥락 참고용)
- https://medium.com/@harmonyglobalservices1/i-evaluated-david-omaris-youtube-mastery-course-these-were-the-red-flags-that-made-me-step-back-9c92b0017f03
- https://www.directai.app/blog/is-youtube-automation-legit
