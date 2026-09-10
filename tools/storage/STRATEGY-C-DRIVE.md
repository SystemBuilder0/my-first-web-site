# C 드라이브 저장공간 전략

작성 2026-09-09 · 실측 반영 2026-09-10 · 대상: Windows, 다중 드라이브 워크스테이션

---

## 1. 현재 상태 진단 (실측)

| 항목 | 수치 |
|---|---|
| C: 전체 용량 | **930.9GB** |
| C: 여유 공간 | **29.39GB** |
| **여유율** | **약 3.2%** |
| 안전 기준 | 15~20% (140~186GB) |
| **부족분** | **약 111~157GB** |

### 이 PC의 결정적 조건 — 다른 드라이브에 여유가 많습니다

| 드라이브 | 이름 | 전체 | 여유 | 역할 |
|---|---|---|---|---|
| **C:** | | 930.9GB | **29.39GB** | 시스템 — 포화 |
| D: | SSD_WORK | 1863GB | 134.08GB | 작업용 SSD |
| E: | HDD_samples | 1863GB | 129.1GB | 샘플 보관 |
| F: | HDD | 1863GB | 129.88GB | 일반 보관 |
| **H:** | **SSD업무** | **1863GB** | **492.51GB** | **⭐ 이전 목적지 1순위** |
| I: | | 465.1GB | 14.38GB | 거의 참 |

**H:에 492GB가 비어 있고 SSD입니다.** 이 조건 때문에 전략의 무게중심이 바뀝니다.

> **단일 드라이브 PC라면** "무엇을 지울까"가 문제입니다. 지우면 되돌릴 수 없어 판단이 무겁습니다.
> **이 PC는** "무엇을 옮길까"가 문제입니다. 옮기면 원본이 그대로 남으므로 **판단이 가볍고 회수량이 큽니다.**
> 따라서 아래 3축 중 **축 2(옮긴다)가 1순위**이고, 축 1(비운다)은 보조 수단입니다.

### 왜 "불편"이 아니라 "위험"인가

1. **Windows 기능 업데이트 불가** — 대형 업데이트는 임시 공간 포함 약 20GB를 요구합니다. 지금은 업데이트가 실패하거나 아예 시작되지 않습니다.
2. **SSD 쓰기 성능 저하** — SSD는 빈 블록이 부족하면 쓰기 전 지우기(write amplification)가 늘어 체감 속도가 떨어집니다. 10% 미만부터 뚜렷해집니다.
3. **페이지 파일 확장 실패** — 메모리 압박 시 페이지 파일이 커져야 하는데 자리가 없어 앱이 강제 종료될 수 있습니다.
4. **정리 작업 자체가 실패** — DISM 정리, 압축 해제, 대용량 복사가 모두 임시 공간을 씁니다. **여유가 없으면 정리조차 실패합니다.** 이것이 아래 순서를 반드시 지켜야 하는 이유입니다.

### 목표를 3단계로 나눕니다

| 단계 | 목표 여유 | 의미 | 예상 소요 |
|---|---|---|---|
| **A. 응급** | 50GB | 정리·이동 작업을 안전하게 돌릴 수 있는 최소선 | 30분 |
| **B. 안정** | 100GB | 일상 사용 + 기능 업데이트 가능 | 1~2시간 |
| **C. 안전** | 186GB (20%) | 성능 회복 + 여유 확보 | 반나절 |

C: 여유는 현재 29.39GB이므로 A까지 약 21GB, C까지 약 157GB가 더 필요합니다.

---

## 2. 전략의 3축

용량 문제는 "지우기" 하나로 안 풀립니다. 성격이 다른 세 가지를 구분해야 합니다.

```
   ┌─────────────────────────────────────────────────┐
   │  축 1. 비운다   — 재생성 가능한 것을 삭제        │
   │       캐시, 임시파일, 로그, 업데이트 잔재        │
   │       → 판단 불필요, 즉시 실행 가능              │
   ├─────────────────────────────────────────────────┤
   │  축 2. 옮긴다   — 지우면 안 되는 것을 재배치 ★1순위│
   │       영상, 사진, 설치파일, 완료 프로젝트        │
   │       → 이 PC는 H:에 492GB 여유. 목적지 확보됨    │
   ├─────────────────────────────────────────────────┤
   │  축 3. 막는다   — 다시 차오르지 않게 구조 변경   │
   │       캐시 경로 이전, 저장 공간 센서, 온디맨드   │
   │       → 이걸 안 하면 3개월 뒤 똑같아집니다       │
   └─────────────────────────────────────────────────┘
```

**축 1만 하면 반드시 재발합니다.** 지금까지 8GB까지 온 것 자체가 축 3이 없었다는 증거입니다.

---

## 3. Phase 0 — 응급 확보 (30분, 판단 불필요)

> **순서를 지키세요.** 아래는 "확실히 확보되는 것 → 임시공간을 쓰는 것" 순입니다.
> 여유 8GB 상태에서 DISM부터 돌리면 실패합니다.

### 0-0. 관리자 권한 확인 — 이걸 먼저 하세요 (건너뛰지 마세요)

Phase 0의 대부분은 관리자 권한이 없으면 **조용히 또는 오류와 함께 실패합니다.**
`-EA SilentlyContinue`가 붙어 있어 실패해도 화면에 안 나오는 경우가 있으니, 반드시 먼저 확인합니다.

**여는 법:** `Win` 키 → `powershell` 입력 → **`Ctrl+Shift+Enter`**

**확인:**
```powershell
if (([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  Write-Host "관리자 확인됨 - 진행하세요" -ForegroundColor Green
} else {
  Write-Host "관리자 아님 - 중단하고 다시 여세요" -ForegroundColor Red
}
```

빠른 육안 확인법: 창 제목에 "관리자"가 붙고, 시작 경로가 `C:\Users\<이름>`이 아니라 `C:\Windows\system32`입니다.

**권한 없이 실행하면 나타나는 증상 (실제 사례):**

| 증상 | 실제 원인 |
|---|---|
| `powercfg /h off` → `예기치 않은 오류(0x65b)` | 권한 부족 (1순위 원인) |
| `Stop-Service wuauserv` → `서비스를 열 수 없습니다` | 권한 부족 — 가장 확실한 신호 |
| `Windows\Temp` 삭제했는데 용량이 안 줄어듦 | 권한 부족으로 조용히 실패 |

### 0-1. 시작 전 상태 기록

```powershell
Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" |
  Select-Object @{n='여유GB';e={[math]::Round($_.FreeSpace/1GB,2)}},
                @{n='전체GB';e={[math]::Round($_.Size/1GB,2)}}
```

### 0-2. 최대 절전 모드 해제 — 회수량이 큰 편이지만, **먼저 파일이 있는지 확인하세요**

```powershell
# 확인은 powercfg로 하세요 (아래 주의사항 참고)
powercfg /a
```

> **주의 — `Get-Item`으로 시스템 파일 존재를 판단하지 마세요.**
> `pagefile.sys`와 `hiberfil.sys`는 시스템이 배타적으로 잠그고 있어
> 관리자 권한에서도 `Get-Item`이 실패합니다. `-ErrorAction SilentlyContinue`가 붙어 있으면
> **오류 없이 아무것도 출력하지 않으므로 "파일이 없다"로 오독하기 쉽습니다.**
> 실제로 이 과정에서 `pagefile.sys`(9.5GB)가 존재하는데 없다고 잘못 판단한 사례가 있었습니다.
> 올바른 확인 방법:
> ```powershell
> powercfg /a                                    # 최대 절전 모드 상태
> Get-CimInstance Win32_PageFileUsage |
>   Format-Table Name, AllocatedBaseSize -AutoSize   # 페이지 파일 실제 크기(MB)
> ```

`hiberfil.sys`가 없거나 `powercfg /a`가 "최대 절전 모드를 사용할 수 없습니다"라고 하면
**이미 꺼져 있는 것이므로 이 단계는 건너뜁니다.** 회수량은 0입니다.
(가상 머신 플랫폼/Hyper-V가 켜져 있거나, 이전에 끈 PC에서 흔합니다.)

파일이 존재할 때만:
```powershell
powercfg /h off
```

- **예상 회수: `hiberfil.sys`의 실제 크기** (통상 RAM의 40~75%. 단, 파일이 없으면 0)
- 되돌리기: `powercfg /h on`
- 부작용: "빠른 시작"과 최대 절전이 꺼집니다. 데스크톱이면 사실상 손해 없습니다. 노트북에서 절전 후 완전 복원을 쓰신다면 나중에 다시 켜세요.

### 0-3. 휴지통 비우기

```powershell
# 먼저 크기 확인
(Get-ChildItem 'C:\$Recycle.Bin' -Recurse -Force -File -ErrorAction SilentlyContinue |
  Measure-Object Length -Sum).Sum / 1GB

# 확인 후 비우기 (되돌릴 수 없습니다)
Clear-RecycleBin -Force -ErrorAction SilentlyContinue
```

- **예상 회수: 0~20GB** (오래 안 비웠다면 큽니다)
- 위 크기가 0.1GB 미만이면 건너뛰세요. 비울 게 없으면 `Clear-RecycleBin`이
  `지정된 파일을 찾을 수 없습니다` 오류를 내는데, **무해합니다** (그래서 `-ErrorAction SilentlyContinue`를 붙였습니다).

### 0-4. 임시 파일

```powershell
Remove-Item "$env:TEMP\*"            -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:SystemRoot\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
```

- **예상 회수: 2~10GB**
- 사용 중인 파일은 자동으로 건너뜁니다. 오류 메시지가 나와도 정상입니다.

### 0-5. Windows 업데이트 캐시

```powershell
Stop-Service wuauserv -Force
Remove-Item "$env:SystemRoot\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service wuauserv
```

- **예상 회수: 1~8GB** · 필요하면 Windows가 다시 받습니다

### 0-6. 중간 점검

```powershell
Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" |
  Select-Object @{n='여유GB';e={[math]::Round($_.FreeSpace/1GB,2)}}
```

**여기서 30GB를 넘겼으면 목표 A 달성입니다.** 넘겼을 때만 다음으로 가세요.

### 0-7. DISM 구성 요소 정리 (여유 30GB 확보 후에만)

```powershell
Dism.exe /Online /Cleanup-Image /StartComponentCleanup
```

- **예상 회수: 3~10GB** · 소요 10~25분 · 진행 중 다른 작업 해도 됩니다
- `/ResetBase`를 붙이면 더 확보되지만 **기존 업데이트 제거(롤백)가 불가능해집니다.** 급하지 않으면 붙이지 마세요.

### Phase 0 예상 합계

| 항목 | 예상 |
|---|---|
| 최대 절전 모드 | 0 또는 6~48GB (파일 존재 여부에 따라 전부 아니면 전무) |
| 휴지통 | 0~20GB |
| 임시 파일 | 0.3~10GB |
| 업데이트 캐시 | 0~8GB |
| DISM | 3~10GB |
| **합계** | **0.5~80GB** |

> **편차가 큰 이유:** 위 항목은 "있으면 크고 없으면 0"인 성격입니다.
> 실제 사례로, RAM 64GB 장비인데 최대 절전 모드가 이미 꺼져 있고 업데이트 캐시도
> 비어 있어 **Phase 0 전체 회수량이 1GB 미만**이었던 경우가 있습니다.
> **그러니 Phase 0을 다 돌린 뒤에도 부족하면, 추측을 멈추고 Phase 1의 실측(1-1)으로 바로 넘어가세요.**
> Phase 0은 "싸고 빠른 것부터"일 뿐, 용량 문제의 답이라는 보장은 없습니다.

### 0-8. Phase 0으로 부족했다면 — `C:\Windows\Installer` 확인

```powershell
$s=(Get-ChildItem "$env:SystemRoot\Installer" -Recurse -Force -File -EA SilentlyContinue |
    Measure-Object Length -Sum).Sum
"Installer: {0:N2} GB" -f ($s/1GB)
```

10GB를 넘는 경우가 드물지 않습니다(주로 Office, Visual Studio, Adobe, SQL Server).

**이 폴더는 절대 직접 삭제하면 안 됩니다.** 설치된 프로그램의 MSI/패치 원본이라
지우면 제거·복구·업데이트가 깨지고 되돌리기 어렵습니다.

Microsoft가 지원하는 축소 방법은 **안 쓰는 프로그램을 정상 절차로 제거하는 것**뿐입니다
(설정 → 앱 → 설치된 앱). 제거하면 해당 캐시도 함께 정리됩니다.
고아 패치 파일만 선별하는 서드파티 도구가 있으나 Microsoft 지원 대상이 아니므로
다른 수단을 모두 쓴 뒤에 마지막으로 검토하세요.

---

## 4. Phase 1 — 큰 덩어리 회수 (1~2시간, 판단 필요)

여기부터는 **무엇을 지울지 사람이 정해야 합니다.** 자동 삭제하지 마세요.

### 1-1. 어디에 몰려 있는지부터 본다

```powershell
cd <저장소>\tools\storage
powershell -ExecutionPolicy Bypass -File .\Get-StorageReport.ps1
```

바탕화면에 리포트가 생깁니다. **1·2단계 폴더 Top 25**를 보면 범인이 바로 보입니다.

### 1-2. 개발자 환경의 3대 용량 범인

| 대상 | 통상 크기 | 조치 |
|---|---|---|
| **WSL `ext4.vhdx`** | 20~100GB | 아래 별도 설명 — **가장 흔한 함정** |
| **Docker Desktop** | 10~60GB | `docker system prune -a --volumes` (실행 전 내용 확인) |
| **`node_modules` 누적** | 프로젝트당 0.3~2GB | 안 쓰는 프로젝트 것만 삭제 (`npm install`로 복구) |

**WSL vhdx가 함정인 이유:** WSL 안에서 파일을 지워도 `.vhdx` 파일 크기는 **줄어들지 않습니다.** 명시적으로 압축해야 합니다.

```powershell
# 1) 크기 확인 — 설치 방식에 따라 위치가 다르므로 세 곳을 모두 봅니다
#    스토어 설치 → Packages\ / 독립 실행형 wsl.exe 설치 → wsl\ / Docker → Docker\
@("$env:LOCALAPPDATA\Packages", "$env:LOCALAPPDATA\wsl", "$env:LOCALAPPDATA\Docker") |
  Where-Object { Test-Path $_ } |
  ForEach-Object { Get-ChildItem $_ -Filter '*.vhdx' -Recurse -Force -EA SilentlyContinue } |
  Select-Object @{n='GB';e={[math]::Round($_.Length/1GB,1)}}, FullName

# 2) WSL 종료
wsl --shutdown

# 3) 압축 (diskpart — Hyper-V 없이도 됨)
diskpart
#   select vdisk file="C:\Users\<사용자>\AppData\Local\Packages\...\ext4.vhdx"
#   attach vdisk readonly
#   compact vdisk
#   detach vdisk
#   exit
```

> `Optimize-VHD`도 있지만 Hyper-V 모듈이 설치돼 있어야 합니다. 없으면 위 diskpart를 쓰세요.

### 1-3. 패키지 매니저 캐시

```powershell
# 크기 확인부터
'pip','npm','.nuget','.gradle','.m2' | ForEach-Object {
  $p = switch ($_) {
    'pip'     { "$env:LOCALAPPDATA\pip\Cache" }
    'npm'     { "$env:APPDATA\npm-cache" }
    '.nuget'  { "$env:USERPROFILE\.nuget\packages" }
    '.gradle' { "$env:USERPROFILE\.gradle\caches" }
    '.m2'     { "$env:USERPROFILE\.m2\repository" }
  }
  $s = (Get-ChildItem $p -Recurse -Force -File -EA SilentlyContinue | Measure-Object Length -Sum).Sum
  '{0,-9} {1,8:N2} GB  {2}' -f $_, ($s/1GB), $p
}
```

**예상 합계: 5~30GB.** 전부 재다운로드로 복구됩니다.

### 1-4. 다운로드 폴더 — 지우지 말고 옮기세요

설치 파일(.exe/.msi/.zip)은 대부분 다시 받을 수 있지만, 받기 어려운 것도 섞여 있습니다.
**전부 외장/D:로 옮긴 뒤 필요할 때 꺼내 쓰는 방식**이 안전합니다.

```powershell
# 500MB 이상 파일만 목록으로 확인
Get-ChildItem "$env:USERPROFILE\Downloads" -Recurse -File |
  Where-Object Length -gt 500MB |
  Sort-Object Length -Descending |
  Select-Object @{n='GB';e={[math]::Round($_.Length/1GB,2)}}, LastWriteTime, Name
```

---

## 5. Phase 2 — 구조 개편 (재발 방지 · 이게 핵심)

Phase 0~1은 시간이 지나면 원상복구됩니다. 아래를 해야 끝납니다.

### 2-1. 캐시 경로를 C: 밖으로 이전

다른 드라이브(D: 또는 외장)가 있다면 **이것 하나가 가장 효과적입니다.**

이 PC는 **H: (여유 492GB, SSD)** 를 캐시 목적지로 씁니다.

```powershell
New-Item -ItemType Directory -Path 'H:\cache' -Force | Out-Null

[Environment]::SetEnvironmentVariable('PIP_CACHE_DIR',    'H:\cache\pip',   'User')
[Environment]::SetEnvironmentVariable('NPM_CONFIG_CACHE', 'H:\cache\npm',   'User')
[Environment]::SetEnvironmentVariable('GRADLE_USER_HOME', 'H:\cache\gradle','User')
[Environment]::SetEnvironmentVariable('NUGET_PACKAGES',   'H:\cache\nuget', 'User')
# AI 모델을 쓰신다면 (모델 파일이 수십 GB로 커집니다)
[Environment]::SetEnvironmentVariable('HF_HOME',          'H:\cache\hf',    'User')

# 확인 (새 터미널에서)
Get-ChildItem Env: | Where-Object Name -match 'CACHE|GRADLE_USER_HOME|NUGET_PACKAGES|HF_HOME'
```

HDD인 E:/F:는 캐시 목적지로 쓰지 마세요. 빌드·설치 속도가 크게 느려집니다.

적용하려면 새 터미널을 열어야 합니다. 이전 캐시 폴더는 확인 후 삭제하세요.

### 2-2. 저장 공간 센서 켜기

**설정 → 시스템 → 저장 공간 → 저장 공간 센서 → 켜기**

- 임시 파일 자동 삭제
- 휴지통: 30일 지난 항목 삭제
- 다운로드: 30일 이상 열지 않은 파일 삭제 ← 이건 취향에 따라 끄셔도 됩니다

Windows 기본 기능이라 별도 프로그램이 필요 없습니다.

### 2-3. OneDrive는 "파일 온디맨드"로

OneDrive 폴더 우클릭 → **여유 공간 확보**. 클라우드에만 두고 필요할 때 내려받습니다.
사진·문서가 많다면 수십 GB가 회수됩니다.

### 2-4. 프로젝트 배치 규칙 정하기

```
C:\dev\        ← 지금 작업 중인 프로젝트만 (3~5개)
H:\work\       ← 진행 중이지만 자주 안 여는 것 (SSD라 속도 손해 적음)
F:\archive\    ← 완료된 프로젝트 (node_modules 지우고 이동, HDD로 충분)
GitHub         ← 코드는 어차피 여기 있습니다. 로컬 사본은 언제든 버려도 됩니다
```

**드라이브별 용도 배분 (이 PC 기준)**

| 드라이브 | 종류 | 여유 | 맡길 것 |
|---|---|---|---|
| C: | SSD | 29GB | OS, 설치 프로그램, 진행 중 프로젝트만 |
| H: | SSD | 492GB | 캐시, 대용량 작업 데이터, 가상디스크 |
| D: | SSD | 134GB | 현재 작업물 (이미 용도가 있어 보임) |
| E:/F: | HDD | 129GB씩 | 아카이브, 영상 원본, 백업 |
| I: | | 14GB | 여유 없음 — 목적지로 부적합 |

---

## 6. Phase 3 — 그래도 186GB에 못 미치면

**이 PC는 하드웨어 증설이 필요 없습니다.** 다른 드라이브에 1TB 이상 여유가 있으므로,
부족하다면 아직 옮기지 않은 것이 남아 있다는 뜻입니다. 남은 수단은 이렇습니다.

| 선택지 | 회수량 | 비고 |
|---|---|---|
| **대형 앱 이동** | 5~30GB | 설정 → 앱 → 설치된 앱 → 이동 (지원하는 앱만) |
| **페이지 파일을 H:로 이동** | 9.5GB | 아래 주의사항 참고 |
| 시스템 복원 축소 | 5~20GB | `vssadmin resize shadowstorage /for=C: /on=C: /maxsize=5%` |
| `C:\Windows\Installer` 축소 | 최대 15GB | 안 쓰는 프로그램 정상 제거로만 (0-8절 참고) |
| 안 쓰는 프로그램 제거 | 가변 | Installer 캐시도 함께 정리되어 효과가 이중입니다 |

### 페이지 파일 이동에 대해

현재 `C:\pagefile.sys`가 9.5GB를 씁니다. 다중 드라이브 PC이므로 H:로 옮길 수 있습니다.

- **설정 경로:** 시스템 속성 → 고급 → 성능 설정 → 고급 → 가상 메모리 변경
- C:는 "페이지 파일 없음", H:는 "시스템이 관리하는 크기"로 설정 후 **재부팅**
- **주의:** C:에 페이지 파일이 전혀 없으면 시스템 크래시 덤프를 생성하지 못합니다.
  블루스크린 원인 분석이 필요한 상황이라면 C:에 최소 크기(예: 2GB)를 남기세요.
- RAM이 63.9GB로 넉넉해 실사용 영향은 작을 것으로 보이나, 체감 문제가 생기면 되돌리세요.

---

## 7. 유지 루틴

| 주기 | 할 일 |
|---|---|
| 자동 | 저장 공간 센서 (설정 한 번이면 끝) |
| 월 1회 | `Get-StorageReport.ps1 -Quick` 실행, 여유 60GB 밑이면 대응 |
| 분기 1회 | 전체 스캔 + 아카이브 이동 + WSL vhdx 압축 |
| 프로젝트 종료 시 | `node_modules` 삭제 후 D:로 이동 |

---

## 8. 절대 하지 말 것

| 금지 | 이유 | 대신 |
|---|---|---|
| `hiberfil.sys` / `pagefile.sys` 직접 삭제 | 시스템 파일. 삭제 안 되거나 부팅 문제 | `powercfg /h off` / 가상 메모리 설정 |
| `C:\Windows\WinSxS` 수동 삭제 | 시스템 손상 → 복구 불가 | `Dism /Online /Cleanup-Image /StartComponentCleanup` |
| `DriverStore` 수동 삭제 | 드라이버 전멸 위험 | `pnputil /enum-drivers` 후 선별 제거 |
| 정체불명 "PC 최적화" 프로그램 | 광고웨어인 경우 많음 | Windows 기본 도구로 충분 |
| 여유 8GB에서 DISM부터 실행 | 임시 공간 부족으로 실패 | Phase 0 순서 준수 |
| 리포트 안 보고 일괄 삭제 | 정작 큰 놈은 안 지워짐 | 항상 실측 → 큰 것부터 |

---

## 9. 지금 바로 할 순서 (요약)

> 이 PC는 다른 드라이브에 1TB 넘는 여유가 있습니다.
> **지울 것을 찾느라 시간 쓰지 말고, 옮길 것을 찾으세요.**

1. 관리자 PowerShell 열기 (0-0절 권한 확인)
2. **실측 먼저** — C: 1단계 폴더 용량 스캔 (1-1절). 901GB가 어디 있는지부터 봅니다
3. 큰 것부터 H:로 이동 (축 2). 지우는 게 아니라 옮기는 것이므로 판단이 가볍습니다
4. WSL vhdx / Docker 디스크 확인 및 압축 (1-2절)
5. **캐시 경로를 H:로 이전** (2-1절) ← 재발 방지의 핵심
6. 저장 공간 센서 켜기 (2-2절)
7. 여유 50GB를 넘긴 뒤에만 `Dism ... /StartComponentCleanup`
8. 그래도 부족하면 페이지 파일 H: 이동 + 안 쓰는 프로그램 제거 (6절)

항목별 세부 명령어(20개 대상 × 확인/정리/복구/주의)는 같은 폴더의 `CLEANUP-REFERENCE.md`,
자동화 스크립트는 `Free-DiskSpace.ps1`(기본 시뮬레이션), 진단은 `Get-StorageReport.ps1`을 참고하세요.
