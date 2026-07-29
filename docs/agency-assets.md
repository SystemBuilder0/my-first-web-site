# Frame & Mortar — 실행 자산 팩 (로컬 SMB 니치 확정본)

작성일: 2026-07-29
상위 문서: `docs/ad-agency-3h-plan.md`
오늘 목표: **내일 앉자마자 바로 발송할 수 있는 완전 세팅 상태**
(= 포트폴리오 4편 + 웹사이트 + 리드 리스트 + 도메인 신청 + 메일 템플릿)

---

## 1. 확정 사항

| 항목 | 확정 내용 |
|------|-----------|
| 니치 | 미국 **로컬 SMB**, 아래 4개 버티컬 |
| 브랜드명 | **Frame & Mortar** |
| 도메인 | **frameandmortar.com** (1순위) / kesslerandwren.com (2순위) |
| 1차 타깃 도시 | **Scottsdale, AZ** (2순위: Santa Monica, CA) |
| 가격 포지션 | $500~1,500 / 편 |

### 1-1. 브랜드명 근거
"brick and mortar"는 미국에서 **오프라인 로컬 사업체**를 뜻하는 관용어입니다. 여기에 frame(영상 프레임)을 붙여 **Frame & Mortar** = "오프라인 가게를 위한 영상". 콜드메일을 받은 로컬 사장이 회사명만 보고 "우리 같은 가게 전문이구나"를 즉시 인지합니다.

원본 영상은 미국식 인명 조합(CCCA)을 권했지만, 그건 **고급 컨설팅 포지션**일 때 유효합니다. 우리 타깃은 로컬 자영업자라 인명 조합보다 **직관적 의미**가 전환에 유리하다고 판단했습니다. 인명 조합을 원하시면 2순위 `kesslerandwren.com`으로 바로 전환 가능합니다.

### 1-2. 도메인 가용성 확인 방법 (한계 명시)
RDAP(whois) 조회는 이 환경의 네트워크 정책상 차단돼 있어, **DNS 응답 코드로 1차 선별**했습니다.
- NXDOMAIN → 미등록 **가능성 높음**
- A레코드 존재 → 등록됨(확정)

⚠️ DNS 방식은 **등록됐지만 네임서버가 없는 도메인**을 미등록으로 오판할 수 있습니다. **최종 확인은 레지스트라 결제 화면에서** 이뤄집니다.

1차 선별 통과 후보: `frameandmortar` / `kesslerandwren` / `pikeandmercer` / `thornburycreative` / `halloranmedia` / `cardinalcut` / `brightlotstudio` / `vantagerowmedia` / `brightcurbmedia` / `redmapleadv` / `reelandrowe`

### 1-3. 버티컬 4개와 선정 근거
원본 영상은 레스토랑과 짐을 예시로 썼습니다. 그런데 **레스토랑은 마진이 얇아 영상 광고비 지출 여력이 낮습니다.** 반면 med spa·치과는 시술 객단가가 높아 광고 예산이 실제로 존재합니다.

그래서 **영상에서 검증된 2종 + 지불여력 높은 2종**으로 배분했습니다.

| # | 버티컬 | 포트폴리오 배정 | 선정 이유 |
|---|--------|----------------|-----------|
| 1 | Med spa / 에스테틱 클리닉 | 1편 | 시술 객단가 높음 → 광고 예산 존재. before/after 비주얼 수요 큼 |
| 2 | 치과 (임플란트·교정) | 1편 | 동일. 신규환자 1명의 LTV가 커서 영상 ROI 설득이 쉬움 |
| 3 | 부티크 짐 / 피트니스 | 1편 | 영상 04:11에서 실제 검증된 케이스 |
| 4 | 레스토랑 (BBQ·캐주얼) | 1편 | 영상 03:35에서 실제 검증된 케이스 |

→ 4편으로 **4개 버티컬을 커버**하므로, 리드 리스트도 4갈래로 뽑아 각 업체에 **"당신 업종 샘플"**을 붙여 보낼 수 있습니다. 단일 니치보다 리스트 확보 규모가 커서 3시간 작업에 유리합니다.

### 1-4. 도시 선정
**Scottsdale, AZ 1순위.** med spa·에스테틱 업체 밀집도가 높은 지역으로 알려져 있고, 소득 수준이 높습니다.
> ⚠️ 정직하게 밝히면, "LA보다 에이전시 경쟁이 덜하다"는 건 제 추정이며 확인된 데이터가 아닙니다. 반응률이 안 나오면 2순위 Santa Monica로 즉시 전환하십시오.

**시차 주의**: Scottsdale은 MST(UTC-7, 애리조나는 서머타임 미적용) → **한국시간 -16시간**.
콜드메일은 수신자 현지 **화~목 오전 8~10시** 도착이 가장 좋습니다 = **한국시간 자정~새벽 2시**.
→ 내일 아침에 직접 보내지 마시고 **예약 발송**을 쓰십시오. (2-4 참조)

---

## 2. 실행 자산

### 2-1. 포트폴리오 영상 프롬프트 4종

프롬프트 규격은 영상 02:39(실패) vs 03:11(성공) 대조에서 도출했습니다.
**공통 규칙**: ① 구체적 업종·상호 명시 ② 매체 명시 ③ **텍스트 오버레이 최소화**(로고 글자 깨짐 회피) ④ **인물 손 클로즈업 회피**(손 왜곡 회피)

```
[1] MED SPA
A 15-second premium TV commercial for "Lumen Aesthetics", a modern med spa.
Slow cinematic push-ins on a bright minimalist treatment room, soft natural
light, clean white and warm beige palette, close-up of glowing healthy skin
texture, calm confident atmosphere. No on-screen text. No visible hands.

[2] DENTAL
A 15-second TV commercial for "Northgate Dental", a modern dental clinic.
Bright airy clinic interior, sleek modern chairs, warm welcoming reception,
a confident natural smile in soft focus, blue and white clinical palette,
trustworthy premium feel. No on-screen text. No close-up hands.

[3] BOUTIQUE GYM
A 15-second TV commercial for "Ironline Strength", a boutique strength gym.
Dramatic low-key lighting, chalk dust in shafts of light, heavy barbell
plates, wide gym shots with strong silhouettes, gritty energetic pacing,
deep contrast. No on-screen text. Avoid close-ups of hands and faces.

[4] RESTAURANT
A 15-second TV commercial for "Smoke & Oak", a local BBQ restaurant.
Slow-motion macro shots of smoked brisket being sliced, glistening sauce,
rising smoke, warm rustic wood interior, golden hour light, appetizing
and inviting. No on-screen text. No visible hands.
```

**모델·해상도 선택 (실측 크레딧 기준)**

| 모델 | 설정 | 크레딧/편 |
|------|------|-----------|
| Marketing Studio | 1080p 15s | 150 |
| Seedance 2.0 | 1080p 10s | 90 |
| Seedance 2.0 | 720p 10s | 45 |
| Seedance 2.0 Mini | 720p 10s | 25 |
| Kling 3.0 (pro) | 10s | 25 |

→ **권장 전략**: 저가 모델(Kling 3.0 pro / Seedance Mini, 25크레딧)로 **컨셉을 먼저 검증**하고, 통과한 컷만 고품질로 재생성. 첫 시도부터 150크레딧을 쓰면 재시도 여력이 사라집니다.
→ PLUS 1,000크레딧 기준 예산 배분: 검증 8회(200) + 고품질 4편(600) + 이미지·로고(200) = 1,000

### 2-2. 웹사이트 구조

핵심 원칙 (영상 05:37): **"비주얼을 파는 회사인데 사이트가 허접하면 아무도 돈을 안 낸다."**

| 섹션 | 내용 |
|------|------|
| Hero | "TV-quality video ads for local businesses — without the TV budget." + CTA |
| Portfolio | **영상 4편** (버티컬 라벨: Med Spa / Dental / Fitness / Restaurant) |
| How it works | 1) 15분 통화 2) 3일 내 초안 3) 무제한 수정 1회 4) 납품 |
| Pricing | Starter $500 (1편) / Studio $1,200 (3편) / Monthly $1,500 (월 4편) |
| Why us | "전통 에이전시 $3,000~6,000 → 우리는 그 1/4 가격, 5일 내 납품" |
| Contact | 이메일 + 문의 폼 |

⚠️ 영상 06:08의 함정: 레퍼런스 사이트를 그대로 쓰면 **웹 제작사 포트폴리오**가 박힙니다. 포트폴리오 자리는 반드시 **우리 영상 4편**으로 교체해야 합니다.

### 2-3. 콜드메일 템플릿 (CAN-SPAM 준수)

```
Subject: quick idea for {{BusinessName}}

Hi {{FirstName}},

I came across {{BusinessName}} while looking at {{City}} {{Vertical}} —
your {{SpecificDetail}} stood out.

One thing I noticed: your site leads with photos, not video. For
{{Vertical}} that usually costs conversions, since people want to see
the space and the result before they book.

We make TV-quality 15-second ads for local businesses. Here's one we
made for a {{Vertical}}: {{PortfolioLink}}

Traditional agencies charge $3,000-6,000 for this. We're $500, delivered
in 5 days.

Worth a 15-minute call this week?

Best,
{{YourName}}
Frame & Mortar
{{PhysicalAddress}}

Unsubscribe: {{UnsubscribeLink}}
```

**CAN-SPAM 필수 3요소 체크**
- [x] 발신자 신원 명확 (이름 + 회사명)
- [x] **유효한 실제 우편 주소** ← ⚠️ 아직 미확보. 한국 주소도 무방하나 **실재하는 주소**여야 합니다
- [x] 수신거부 링크
- [x] 오해 소지 있는 제목 없음 ("quick idea for ~"는 내용과 일치)

### 2-4. 내일 아침 실행 순서 (도메인 워밍업 준수)

| 일자 | 발송량 | 비고 |
|------|--------|------|
| 1일차 | **5통** | 예약 발송, 현지 화~목 오전 8~10시 도착 |
| 2일차 | 6~8통 | |
| 3일차 | 10~12통 | |
| 4일차 이후 | +20%/일 | 반송률·응답률 보고 조절 |

❗ **도메인 산 직후 대량발송은 절대 금지**입니다 (영상 09:55). 스팸함에 꽂히면 전환율이 아니라 **도달률 자체가 0**이 되는데, 발신자는 그 사실을 모릅니다.

---

## 3. 미해결 / 사용자 확인 필요

| # | 항목 | 상태 |
|---|------|------|
| 1 | Higgsfield PLUS 결제 | ⏳ 결제 후 `balance`로 확인 → 영상 생성 착수 |
| 2 | CAN-SPAM용 실제 우편 주소 | ❗ 필요 |
| 3 | 발신자 영문 이름 | ❗ 필요 (예: Jun Jang) |
| 4 | 도메인 레지스트라 결제 | 사용자 직접 (카드 필요) |
| 5 | Google Workspace 트라이얼 | 사용자 직접 |

---

## 4. 이 환경의 제약 (실행으로 확인)

| 제약 | 확인 방법 | 영향 |
|------|-----------|------|
| curl 아웃바운드 대부분 차단 | example.com/yelp.com/bing.com 모두 000 | **리드 자동 스크래핑 불가** → 검색·페치 도구로 건별 수집 |
| RDAP(whois) 차단 | rdap.verisign.com 403 | 도메인 가용성은 DNS로 1차 선별만 |
| Yelp 페치 차단 | HTTP 403 | 리드 소스에서 Yelp 제외, 업체 자사 사이트 직접 조회 |
| Gmail 발송 도구 없음 | 도구 목록 확인 | 초안까지만 자동, 발송은 수동/예약 |
| DNS 조회는 가능 | getaddrinfo 정상 | 도메인 1차 선별에 활용 |

→ 결론: **리드 목표를 200개가 아니라 40~60개로 잡는 것이 현실적입니다.** 1일차 발송량이 5통이므로, 60개면 약 2주치 물량입니다. 개수보다 필터 정확도가 중요합니다.
