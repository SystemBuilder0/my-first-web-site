# 대형 유튜버·전문 영상 제작자의 스토리지 문제 해결 실사례 조사

조사일: 2026-09-15 (모든 가격·사양은 이 시점 기준 웹 검색 결과)
조사 방법: WebSearch로 확인된 내용만 기재. 이번 조사 환경에서는 WebFetch(개별 페이지 원문 열람)가 네트워크 정책상 전체 도메인에서 차단되어 있어(`EGRESS_BLOCKED`), 모든 근거는 WebSearch가 반환한 검색결과 스니펫과 그 출처 URL에 기반함. 원문 전체를 직접 열람하지 못했다는 점을 감안하고 읽을 것. 스니펫 내용과 실제 원문이 다를 가능성은 낮지만 0은 아님.

---

## 요약 (핵심 발견)

1. **최상위권(LTT급)은 페타바이트 단위 자체 서버를 자체 구축한다.** Linus Tech Tips(Linus Media Group)는 3.6PB 아카이브 서버(TrueNAS, 270개 드라이브), 그리고 KIOXIA와 협업한 100만 달러(1.2M 달러 이상) 규모의 페타바이트급 올플래시 서버를 실제로 운영 중이다. 다만 이는 "회사"에 가까운 대형 미디어 그룹 사례이며 개인 유튜버의 표준은 아니다.
2. **중형 채널(구독자 수십만~100만대)은 수십~수백 TB NAS가 표준.** ServeTheHome(패트릭 케네디)은 스튜디오용 360TB 올플래시(Solidigm SSD 기반) NAS를 구축했고, 유튜버 Mark Ellis는 Synology DS1522+ NAS + 14TB 외장 백업 + 클라우드(Synology C2)로 3-2-1 규칙을 실천한다.
3. **RAID는 백업이 아니다**라는 원칙이 업계 공통으로 반복 강조된다. Peter McKinnon의 48TB RAID 6 구성 사례에서도, RAID는 드라이브 고장에는 강하지만 실수 삭제·바이러스에는 무력하다는 점이 지적된다.
4. **프록시 워크플로는 저장공간을 90~95% 절감**하는 표준 관행이며, Premiere Pro·DaVinci Resolve 모두 내장 기능으로 지원한다. 다만 미디어 캐시/최적화 미디어 자체가 다시 수십~수백GB를 잡아먹으므로 별도 관리가 필요하다.
5. **3-2-1 백업 규칙(원본 1 + 백업 2, 그중 1은 오프사이트)**은 Netflix 등 대형 제작사의 표준 계약 요구사항으로, 원본 촬영본(OCF)에 대해 명시적으로 적용된다.
6. **LTO 테이프는 여전히 대용량 장기 보관의 최저 비용 매체**(TB당 약 5~6달러, 수명 30년 이상)로, Pixar 등 스튜디오가 최종본뿐 아니라 중간 산출물까지 테이프에 아카이브한다. 클라우드 아카이브(S3 Glacier Deep Archive, GCS Archive)는 월 단위로는 더 저렴해 보여도(TB당 약 1~1.2달러) 최소 보관 기간(180일~365일)과 인출 비용이 별도로 붙는다.
7. **원본 푸티지 보관 기간은 업계 표준이 없다.** 계약사에 따라 30일~2년까지 다양하며, "계약서에 명시가 없으면 결국 삭제된다"는 것이 업계 관행으로 확인된다.

---

## 1. 실사례

### 1-1. Linus Tech Tips / Linus Media Group — 페타바이트급 자체 서버
- **누구**: Linus Tech Tips (Linus Media Group, 대형 테크 유튜브 채널)
- **규모**:
  - 아카이브 서버: **3.6PB(3,600TB)**, TrueNAS 기반 단일 컨트롤러 NAS, 드라이브 약 270개(여러 벤더에서 무상 제공받은 드라이브·인클로저 조합)
  - "백만 달러 서버": KIOXIA CM6 시리즈 PCIe 4.0 U.3 SSD를 중심으로 한 **페타바이트급 올플래시 클러스터**, 총 비용 100만~120만 달러 이상
  - "$1,000,000 Computer": 페타바이트 이상의 NVMe 스토리지 클러스터, 속도 100GB/s 이상 (전력·발열 문제로 서버실 에어컨이 감당 못할 정도)
  - "Petabyte Project" 시리즈: 기존 페타바이트 서버가 완전히 가득 차 "Petabyte Project is FULL!"이라는 후속 에피소드로 증설 진행
- **구성**: TrueNAS 소프트웨어, 다수 벤더(Seagate, KIOXIA 등) 협찬 하드웨어, EPYC 서버 플랫폼
- **출처**:
  - https://www.truenas.com/blog/linus-tech-tips-uses-truenas-again/
  - https://blog-us.kioxia.com/post/2022/06/06/behind-the-scenes-linus-tech-tips-and-the-million-dollar-server
  - https://blog.seagate.com/business/linus-tech-tips-want-petabyte-system/
  - https://linustechtips.com/topic/1221334-petabyte-storage-done-right/
  - https://linustechtips.com/topic/1158509-deploying-another-petabyte-of-storage/
  - https://linustechtips.com/topic/1249401-linus-media-groups-server-room/
- **비고**: LTT는 개인 유튜버가 아니라 다수 채널·직원을 둔 미디어 회사이며, 다수 하드웨어를 협찬받는 특수 사례다. 일반 개인 유튜버의 참고선이라기보다 "최상위 극단값" 사례로 봐야 한다.

### 1-2. ServeTheHome (패트릭 케네디) — 스튜디오용 360TB 올플래시 NAS
- **누구**: ServeTheHome (서버·엔터프라이즈 하드웨어 전문 유튜브 채널, 구독자 100만 돌파 시점 언급)
- **규모**: **360TB**, 전량 SSD(올플래시) 구성
- **구성**: Solidigm D5-P5336 30.72TB U.2 SSD 다수, QNAP NAS 플랫폼, AMD/NVIDIA 파트, 100Gbps 네트워크로 편집 워크스테이션에 직결
- **선택 이유**: HDD보다 밀도 높은 SSD 채택으로 소음(HDD 스핀업 소음) 제거, 100Gbps 네트워크 대역폭을 충분히 활용하기 위함
- **맥락**: 매달 인코딩 후 압축 상태로도 1TB 이상의 영상 프로젝트가 쌓이는 것이 증설 계기로 언급됨
- **출처**:
  - https://www.servethehome.com/building-new-sth-studio-nas-storage-qnap-solidigm-amd-nvidia/
  - https://www.youtube.com/watch?v=dfx_nJ9uyBw

### 1-3. Mark Ellis (유튜버) — Synology NAS + 클라우드 3-2-1 실천 사례
- **누구**: Mark Ellis Reviews (테크 리뷰 유튜버)
- **구성**: Synology **DS1522+** NAS를 메인 스토리지 겸 Time Machine 백업 대상으로 사용, **Synology C2** 클라우드 백업 서비스로 오프사이트 백업, NAS에 물린 **14TB 외장 드라이브**를 Hyper Backup으로 자동 백업
- **의의**: 개인/1인 유튜버 규모에서 3-2-1 규칙(로컬 NAS + 외장 드라이브 + 클라우드)을 실제로 적용한 구체적 사례
- **출처**: https://markellisreviews.com/tech-tips-guides/how-i-backup-everything-as-a-youtuber-synology-ds1522-nas-review/

### 1-4. Peter McKinnon — RAID 6 48TB (2018년 기준, 출처 오래됨 주의)
- **누구**: Peter McKinnon (사진·영상 크리에이터, 대형 유튜브 채널)
- **규모**: 드라이브 6개로 구성된 **48TB RAID 6(더블 패리티)** 어레이. 이동용으로는 Samsung SSD T3 사용
- **원칙**: RAID는 디스크 2개까지 고장나도 버티지만, 실수 삭제나 바이러스로 인한 데이터 손실은 막지 못하므로 RAID를 백업으로 삼지 말라는 업계 통설이 함께 언급됨
- **출처**: https://x.com/petermckinnon/status/1013417103007739904 (2018년 게시물 기반 정보로, 현재 세팅과 다를 수 있음 — 정보 최신성 낮음, 명시)

### 1-5. Casey Neistat — 폴더 구조 기반 아카이빙 (스토리지 하드웨어 정보는 확인 불가)
- **누구**: Casey Neistat (브이로그 선구자 유튜버)
- **확인된 내용**: 촬영 푸티지를 연도 → 월 → 일 순서로 폴더 구조화하고, 카메라별로 폴더를 나눠 시간순으로 정리. 매일 4~8시간을 편집에 투입한다고 언급됨
- **확인 안 된 내용**: 실제 하드웨어(NAS/RAID 용량, TB 규모, 비용)에 대한 구체적 수치는 이번 검색으로 확인하지 못함 — **출처 미확인**
- **출처**: https://www.youtube.com/watch?v=pzGDWePw9tE , https://www.youtube.com/watch?v=fBWDXh2nIsc , https://medium.com/@razgulyaev/how-to-organize-your-files-like-casey-neistat-ben-brown-and-sara-dietschy-8eadc4e2e5c8

### 1-6. MKBHD — 신뢰도 낮은 출처 (참고용)
- **확인된 내용(신뢰도 낮음)**: 강력한 NVMe 기반 워크스테이션, 프록시 워크플로 사용, macOS + Final Cut Pro 선호(렌더 시간 이유)라는 서술이 검색되었으나, 출처가 Quora 답변으로 **1차 출처가 아니며 구체적 TB 수치·장비 모델은 확인되지 않음**
- **판단**: 이 항목은 신뢰도가 낮아 "실사례"보다는 "떠도는 설명" 수준으로 취급해야 함. 구체적 스토리지 규모 관련 1차 출처는 이번 조사에서 찾지 못함 — **출처 미확인**
- **출처(참고, 신뢰도 낮음)**: https://www.quora.com/What-video-editing-software-is-used-by-mkbhd

---

## 2. 프록시 워크플로(Proxy Workflow) 상세

- **저장공간 절감 효과**: 프록시 워크플로 적용 시 **90~95% 저장공간 절감**이 일반적. 예: 4K 원본 대신 1080p H.264(8~10Mbps)로 프록시를 만들면 원본 대비 약 3~4GB 수준으로 축소됨.
  - 출처: https://www.video-editor.com/blog/proxy-workflow-edit-4k (WebSearch 스니펫 기준)
- **Premiere Pro**: 프록시 토글을 원클릭으로 전환 가능 — 색보정·디테일 확인 시 원본으로, 편집 시 프록시로 즉시 전환.
  - 출처: https://elements.tv/blog/everything-you-need-to-know-about-the-proxy-workflow-in-adobe-premiere-pro/
- **DaVinci Resolve**: `File > Project Settings > Master Settings > Optimized Media and Render Cache`에서 프록시 해상도/포맷을 지정. 클립 선택 후 우클릭 → "Generate Proxy Media"로 생성. **Resolve에서는 Optimized Media와 Proxy Media가 별개의 시스템**임에 유의 (Proxy Media가 전통적 의미의 저해상도 대체본).
  - 출처: https://elements.tv/blog/everything-you-need-to-know-about-the-proxy-workflow-in-davinci-resolve/ , https://support.emerson.edu/hc/en-us/articles/21709341718299-Creating-Proxies-in-Resolve
- **코덱 선택 기준**: 편집 반응성(스크러빙)이 중요하면 **ProRes Proxy**, 저장공간/이동성이 중요하면 **H.264**가 실용적 선택.
  - 출처: https://jonnyelwyn.co.uk/film-and-video-editing/proxy-workflows-for-your-nle/ (WebSearch 스니펫 기준, 원문 미열람)

---

## 3. 캐시/미디어 캐시 관리 상세

### Premiere Pro Media Cache
- 일반적으로 **50~150GB**까지 커지며, 프로젝트를 닫아도 내부 드라이브에 남아있고 Adobe가 자동으로 잘 정리하지 않음.
- 기본 설정상 캐시가 **90GB**를 넘으면 오래된 캐시 파일을 자동 삭제하도록 되어 있으나, 4K 작업·다수 프로젝트를 다루면 이보다 훨씬 커지는 사례가 실사용자 보고로 확인됨(개별 사례: 39GB, 45GB, 52.5GB 등).
- 관리법: Media Cache 환경설정에서 용량 제한 또는 자동 삭제 옵션 설정 가능.
- 출처: https://community.adobe.com/t5/premiere-pro-discussions/premiere-media-cache-location-has-a-mind-of-its-own/td-p/9928211 , https://www.gurusoftware.com/how-to-clear-the-adobe-premiere-pro-cache-2024-guide/ , https://community.adobe.com/t5/premiere-pro-discussions/eating-up-my-disk-space/m-p/9274063/highlight/true

### DaVinci Resolve Optimized Media / Render Cache
- 4K 프로젝트에서 스마트 캐시를 몇 시간 돌리면 CacheClip 폴더(Render Cache)만으로 **20~40GB** 누적.
- 동일 프로젝트에서 2시간 분량 타임라인을 ProRes 422 HQ로 트랜스코드한 Optimized Media는 **200~400GB**까지 도달.
- Render Cache(CacheClip), Optimized Media, Proxy Media, Gallery Still, Fusion 노드 캐시가 **모두 별개 폴더에 각각 사본을 기록**하며, 어느 것도 자동으로 정리되지 않음.
- 기본 저장 위치는 `Preferences > Media Storage`에 등록된 첫 번째 스크래치 디스크.
- 출처: https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=175845 , https://davinciresolve21.com/blog/davinci-resolve-cache-files-filling-up-hard-drive , https://beginnersapproach.com/davinci-resolve-optimized-media/

### 스크래치 디스크를 OS 드라이브와 분리하는 이유
- 단일 드라이브 구성에서는 OS 로그 읽기, 애플리케이션 바이너리 로드, 대용량 임시 캐시 파일 쓰기가 동시에 몰려 대역폭이 분산되고, 이로 인해 시스템 랙·재생 끊김·렌더링 중 멈춤 현상이 발생.
- 전용 스크래치 디스크는 이 무거운 쓰기 작업을 격리해 메인 시스템 드라이브가 OS·앱 구동에만 집중하도록 함.
- SSD 수명(TBW, Terabytes Written) 관점에서도 유리 — 영상 편집은 수백GB의 렌더 파일을 만들었다가 곧 삭제하는 식으로 SSD를 소모시키는 워크로드이므로, 메인 SSD 대신 별도 스크래치 디스크에 부담을 분산시키는 것이 SSD 수명 연장에 도움.
- 4K 이상 고해상도 작업에서는 아무리 빠른 SSD라도 캐시/스크래치를 별도 드라이브에 두는 것이 여전히 권장됨.
- 출처: https://www.howtogeek.com/stop-destroying-your-main-ssd-why-you-might-still-need-a-scratch-disk-in-2026/

---

## 4. 티어드 스토리지 / 백업 구조

### 3-2-1 백업 규칙 (영상 업계 적용)
- 원칙: **3개 사본, 2개의 다른 매체, 1개는 오프사이트**.
- 영상 제작 워크플로에 대입하면:
  - **1차(온라인 작업본)**: NVMe/SSD 또는 SAN 등 고성능 로컬 스토리지 — 매일 쓰는 작업 볼륨
  - **2차(니어라인/로컬 백업)**: 검증된 촬영본을 RAID 어레이나 LTO 테이프로 미러링해 로컬 이중화
  - **3차(오프사이트)**: S3, Wasabi, B2 등 클라우드 버킷으로 전송
- **Netflix**를 포함한 대형 제작사들이 원본 촬영본(OCF, Original Camera Footage) 보호를 위해 이 3-2-1 규칙을 계약상 요구사항으로 채택하고 있음.
- 출처: https://massive.io/content-security/3-2-1-backup-rule/ , https://masv.io/blog/3-2-1-backup-rule

### 계층 구조 (일반적 패턴)
1. **작업용(핫)**: NVMe SSD — 현재 편집 중인 프로젝트, 프록시 포함
2. **니어라인(웜)**: NAS/HDD RAID — 최근 완료 프로젝트, 검증된 원본 백업
3. **아카이브(콜드)**: LTO 테이프 또는 클라우드 아카이브 — 장기 보관, 접근 빈도 낮음

### LTO 테이프가 대형 제작사에서 쓰이는 이유
- **수명**: 적절히 보관 시 **30년 이상**(자료에 따라 30~50년) 데이터 보존 가능.
- **비용 효율**: 디스크 대비 TB당 비용이 훨씬 저렴하며, 클라우드처럼 매달 청구되는 구독료가 없음.
- **에어갭**: 오프라인 매체이므로 랜섬웨어·바이러스 등 네트워크 기반 위협으로부터 격리됨.
- **대용량**: LTO-9는 18TB(네이티브), LTO-10은 30~40TB(네이티브)까지 지원 — 영화 한 편에서 수백TB~페타바이트급 원본이 나오는 것을 감안하면 압축적 보관 수단.
- **실사례**: **Pixar Animation Studios**는 최종 완성작뿐 아니라 모든 애니메이션 프레임, 셰이더, 오디오 테이크까지 LTO 테이프에 아카이빙해 향후 복원·재개봉에 대비.
- 출처: https://wolfcrow.com/what-is-lto-and-what-has-it-got-to-do-with-video/ , https://webuyuseditequipment.net/blog/the-reel-deal-lto-tape-storage-in-the-motion-picture-industry/ , https://blocksandfiles.com/2025/11/13/lto10-upgrade/ (LTO-10 40TB 관련, 원문 미열람·스니펫 기준)

### "언제 무엇을 지우는가" 판단 기준
- **업계 표준 없음**: 원본 촬영본 보관 기간에 대한 통일된 표준은 존재하지 않으며, 계약/회사 정책별로 상이함.
  - 예: 어느 제작사는 납품 후 **30일**만 보관
  - 카네기멜론대 미디어 서비스는 최종 영상 납품 후 **6개월** 뒤 원본·프로젝트 파일 삭제(강의 녹화 기준), 크리에이티브 프로덕션은 **12개월**까지 보관 허용
  - 일부 스튜디오는 프로젝트 종료 후 **최대 2년**까지 아카이브해 클라이언트가 재사용 여부를 결정할 시간을 줌
- **삭제의 경제적 근거**: 일반적 프로젝트 하나가 200GB~1,000GB를 차지하며, 스토리지가 실질 비용이므로 계약서에 별도 명시가 없으면 결국 삭제되는 것이 관행.
- **권장사항**: 계약 시점에 보관 기간을 문서화하고, 장기 아카이빙 비용을 별도로 확인할 것.
- 출처: https://www.cmu.edu/computing/services/comm-collab/media-services/retention.html , (일반 업계 관행) https://blog.frame.io/2023/02/06/digital-video-film-archive-project/ 관련 검색 스니펫

---

## 5. 장비·서비스별 비교 (2026년 9월 기준, 확인된 범위)

### NAS
| 제품 | 구성 | 가격(확인 시점) | 출처 |
|---|---|---|---|
| Synology DS1825+ (8베이) | 16TB IronWolf Pro ×8 + 10GbE 카드, RAID 6 시 96TB 가용 | 약 $3,200 (드라이브·네트워크 카드 포함, 디스크리스 본체는 별도가 더 낮음) | 검색 스니펫 기준(출처 사이트: pctechkits.com류 리뷰 사이트, 1차 출처 아님 — 가격 신뢰도 중간) |
| Synology/QNAP/UGREEN 4베이 플래그십 | — | 대략 $620~$700 선에서 상호 경쟁(약 $60 이내 차이) | tech-insider.org, needtoknowit.com.au (SEO형 비교 사이트, 신뢰도 중간) |
| UGREEN DXP4800 Pro | — | 약 A$1,149.99(호주 기준) | needtoknowit.com.au |
| UGREEN NASync DXP2800~DXP6800 Pro | 2베이~6베이 | 약 $400~$1,200 (아마존 AU) | needtoknowit.com.au |

**주의**: NAS 가격 정보의 출처(pctechkits.com, tech-insider.org, needtoknowit.com.au 등)는 전문 미디어가 아닌 리뷰/비교 콘텐츠 사이트로, 1차 출처(제조사 공식 가격)는 아님. 실제 구매 전 Synology/QNAP/UGREEN 공식 스토어에서 재확인 필요.

### DAS / 외장 RAID
| 제품 | 구성 | 가격(확인 시점: 2026-07-29 언급) | 출처 |
|---|---|---|---|
| Promise Pegasus32 R4 | 16TB(4×4TB), Thunderbolt 3/USB32, 하드웨어 RAID 0/1/1E/5/6 | 약 $1,899 (스트리트 프라이스, 3년 보증) | thepostflow.com (스니펫 기준) |
| OWC ThunderBay 8 (DIY, 디스크리스) | 최대 192TB, 최대 2546MB/s | $750부터 시작(디스크 별매) | eshop.macsales.com 관련 스니펫 |
| LaCie 2big Dock | 32TB, HDD 2개 포함, 하드웨어 RAID | 완제품(드라이브 동봉) | 검색 스니펫 기준, 정확한 가격 미확인 |

### 클라우드 아카이브 (TB당 월 비용)
| 서비스 | 가격(2026년 기준) | 최소 보관 기간 | 비고 | 출처 |
|---|---|---|---|---|
| Backblaze B2 (표준) | $6.95/TB/월 | — | 3배 저장량까지 무료 이그레스, 초과 시 $0.01/GB | https://www.backblaze.com/cloud-storage/pricing |
| Backblaze B2 Overdrive | $15/TB/월 | — | 무제한 무료 이그레스, 고성능 티어 | 검색 스니펫(leanopstech.com 등) |
| Wasabi Hot Cloud Storage | $7.99/TB/월 (2026-07-01부터, 이전 $6.99) | 통상 90일(단, 이번 조사에서 미세부 확인 못함 — 최소보관일수는 별도 확인 필요) | 가격이 2026년 중 인상됨 | https://docs.wasabi.com/docs/may-2026-wasabi-pricing |
| AWS S3 Glacier Deep Archive | 약 $1/TB/월($0.00099/GB) | **180일** | 미달 시에도 180일치 요금 청구, 대량 인출은 $0.0025/GB(최대 48시간 소요) | 검색 스니펫(usage.ai, leanopstech.com 등) |
| Google Cloud Storage Archive | 약 $1.2/TB/월(리전, $0.0012/GB), 멀티리전은 $2.4/TB/월 | **365일** | 인출 시 별도 과금 | 검색 스니펫(nops.io, cloudzero.com 등) |

**주의**: 클라우드 가격 관련 출처 다수가 3rd-party 비교/블로그 사이트로, 공식 가격 페이지(Backblaze·Wasabi는 공식 문서 확인됨)를 제외하면 신뢰도가 중간 수준. AWS·GCP는 공식 페이지(aws.amazon.com/s3/storage-classes/glacier/, cloud.google.com/storage/pricing) 직접 열람은 이번 조사에서 WebFetch 차단으로 하지 못했고, 검색 스니펫으로만 확인함 — 실제 계약 전 공식 페이지 재확인 강력 권장.

### LTO 테이프
| 항목 | 수치 | 출처 |
|---|---|---|
| LTO-9 카트리지 (18TB 네이티브) | 약 $87~90 (TB당 약 $5) | 검색 스니펫(makeuseof.com, ltoworld.com 등) |
| LTO-9 드라이브 | 약 $3,000~7,000+ | 검색 스니펫(HPE 공식 스토어 $7,179.37 언급 포함) |
| LTO-10 | 30TB 또는 40TB(네이티브) | https://blocksandfiles.com/2025/11/13/lto10-upgrade/ (스니펫 기준) |

---

## 6. 참고 링크 목록 (전체)

**실사례**
- https://www.truenas.com/blog/linus-tech-tips-uses-truenas-again/
- https://blog-us.kioxia.com/post/2022/06/06/behind-the-scenes-linus-tech-tips-and-the-million-dollar-server
- https://blog.seagate.com/business/linus-tech-tips-want-petabyte-system/
- https://linustechtips.com/topic/1221334-petabyte-storage-done-right/
- https://linustechtips.com/topic/1158509-deploying-another-petabyte-of-storage/
- https://linustechtips.com/topic/1249401-linus-media-groups-server-room/
- https://www.servethehome.com/building-new-sth-studio-nas-storage-qnap-solidigm-amd-nvidia/
- https://www.youtube.com/watch?v=dfx_nJ9uyBw
- https://markellisreviews.com/tech-tips-guides/how-i-backup-everything-as-a-youtuber-synology-ds1522-nas-review/
- https://x.com/petermckinnon/status/1013417103007739904
- https://www.youtube.com/watch?v=pzGDWePw9tE
- https://www.youtube.com/watch?v=fBWDXh2nIsc
- https://medium.com/@razgulyaev/how-to-organize-your-files-like-casey-neistat-ben-brown-and-sara-dietschy-8eadc4e2e5c8
- https://www.quora.com/What-video-editing-software-is-used-by-mkbhd (신뢰도 낮음)

**프록시/캐시**
- https://elements.tv/blog/everything-you-need-to-know-about-the-proxy-workflow-in-adobe-premiere-pro/
- https://elements.tv/blog/everything-you-need-to-know-about-the-proxy-workflow-in-davinci-resolve/
- https://support.emerson.edu/hc/en-us/articles/21709341718299-Creating-Proxies-in-Resolve
- https://jonnyelwyn.co.uk/film-and-video-editing/proxy-workflows-for-your-nle/
- https://www.video-editor.com/blog/proxy-workflow-edit-4k
- https://community.adobe.com/t5/premiere-pro-discussions/premiere-media-cache-location-has-a-mind-of-its-own/td-p/9928211
- https://www.gurusoftware.com/how-to-clear-the-adobe-premiere-pro-cache-2024-guide/
- https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=175845
- https://davinciresolve21.com/blog/davinci-resolve-cache-files-filling-up-hard-drive
- https://beginnersapproach.com/davinci-resolve-optimized-media/
- https://www.howtogeek.com/stop-destroying-your-main-ssd-why-you-might-still-need-a-scratch-disk-in-2026/

**백업/티어/보관**
- https://massive.io/content-security/3-2-1-backup-rule/
- https://masv.io/blog/3-2-1-backup-rule
- https://wolfcrow.com/what-is-lto-and-what-has-it-got-to-do-with-video/
- https://webuyuseditequipment.net/blog/the-reel-deal-lto-tape-storage-in-the-motion-picture-industry/
- https://blocksandfiles.com/2025/11/13/lto10-upgrade/
- https://www.cmu.edu/computing/services/comm-collab/media-services/retention.html
- https://blog.frame.io/2023/02/06/digital-video-film-archive-project/

**가격/장비 비교**
- https://www.backblaze.com/cloud-storage/pricing
- https://docs.wasabi.com/docs/may-2026-wasabi-pricing
- https://aws.amazon.com/s3/storage-classes/glacier/ (스니펫 기준, 원문 미열람)
- https://cloud.google.com/storage/pricing (스니펫 기준, 원문 미열람)
- https://thepostflow.com/post-production/data-management-and-storage/thunderbolt-das-raid-roundup/
- https://eshop.macsales.com/shop/thunderbay-8/thunderbolt-3
- https://pctechkits.com/best-8-bay-nas-for-video-editors/
- https://tech-insider.org/synology-vs-qnap-vs-ugreen-nas-2026/
- https://needtoknowit.com.au/blog/qnap-vs-ugreen-nas-australia/
- https://ltoworld.com/collections/desktop-lto-tape-drives/lto-9
- https://www.makeuseof.com/lto-tape-stores-data-for-5-per-terabyte-heres-why-you-cant-buy-it/

---

## 조사의 한계 (정직한 보고)

- 이 조사 환경에서는 **WebFetch(URL 원문 열람)가 모든 도메인에서 차단**되어 있어(`EGRESS_BLOCKED`), 원문 기사를 직접 읽지 못하고 **WebSearch가 반환한 요약 스니펫**에 의존했다. 스니펫은 검색 엔진이 원문에서 추출·요약한 것이므로, 숫자나 맥락이 원문과 미세하게 다를 가능성을 배제할 수 없다.
- NAS·DAS 가격 비교표의 상당수 출처는 1차 소스(제조사 공식 페이지)가 아니라 리뷰/비교 콘텐츠 사이트이며, 그중 일부(wu-ftpd.org, requiemforadream.com, markus-hagner-photography.com 등)는 사이트명과 콘텐츠 주제가 불일치해 SEO 목적의 애그리게이터일 가능성이 있다. 이런 출처는 표에 명시적으로 "신뢰도 중간"이라 표기했다.
- MKBHD, Casey Neistat의 구체적 하드웨어 스펙(TB, 장비 모델, 비용)은 신뢰할 만한 1차 출처를 찾지 못해 "출처 미확인"으로 남겨두었다.
