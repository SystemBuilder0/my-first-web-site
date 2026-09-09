# C 드라이브 저장공간 전략 — 512GB / 여유 8GB

작성: 2026-09-09 · 대상: Windows, C: 512GB 단일 시스템 드라이브

---

## 1. 현재 상태 진단

| 항목 | 수치 |
|---|---|
| 전체 용량 | 512GB (NTFS 포맷 후 실사용 약 476GB) |
| 여유 공간 | 8GB |
| **여유율** | **약 1.7%** |
| 안전 기준 | 15~20% (71~95GB) |
| **부족분** | **약 63~87GB** |

### 왜 "불편"이 아니라 "위험"인가

1. **Windows 기능 업데이트 불가** — 대형 업데이트는 임시 공간 포함 약 20GB를 요구합니다. 지금은 업데이트가 실패하거나 아예 시작되지 않습니다.
2. **SSD 쓰기 성능 저하** — SSD는 빈 블록이 부족하면 쓰기 전 지우기(write amplification)가 늘어 체감 속도가 떨어집니다. 10% 미만부터 뚜렷해집니다.
3. **페이지 파일 확장 실패** — 메모리 압박 시 페이지 파일이 커져야 하는데 자리가 없어 앱이 강제 종료될 수 있습니다.
4. **정리 작업 자체가 실패** — DISM 정리, 압축 해제, 대용량 복사가 모두 임시 공간을 씁니다. **여유가 없으면 정리조차 실패합니다.** 이것이 아래 순서를 반드시 지켜야 하는 이유입니다.

### 목표를 3단계로 나눕니다

| 단계 | 목표 여유 | 의미 | 예상 소요 |
|---|---|---|---|
| **A. 응급** | 30GB | 정리 작업을 안전하게 돌릴 수 있는 최소선 | 30분 |
| **B. 안정** | 60GB | 일상 사용 + 업데이트 가능 | 1~2시간 |
| **C. 안전** | 95GB (20%) | 성능 회복 + 여유 확보 | 반나절 |

---

## 2. 전략의 3축

용량 문제는 "지우기" 하나로 안 풀립니다. 성격이 다른 세 가지를 구분해야 합니다.

```
   ┌─────────────────────────────────────────────────┐
   │  축 1. 비운다   — 재생성 가능한 것을 삭제        │
   │       캐시, 임시파일, 로그, 업데이트 잔재        │
   │       → 판단 불필요, 즉시 실행 가능              │
   ├─────────────────────────────────────────────────┤
   │  축 2. 옮긴다   — 지우면 안 되는 것을 재배치     │
   │       영상, 사진, 설치파일, 완료 프로젝트        │
   │       → 목적지 필요 (외장/D:/클라우드)           │
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

모두 **관리자 PowerShell**에서 실행합니다. (시작 → `powershell` 우클릭 → 관리자 권한으로 실행)

### 0-1. 시작 전 상태 기록

```powershell
Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" |
  Select-Object @{n='여유GB';e={[math]::Round($_.FreeSpace/1GB,2)}},
                @{n='전체GB';e={[math]::Round($_.Size/1GB,2)}}
```

### 0-2. 최대 절전 모드 해제 — **단일 최대 회수량**

```powershell
powercfg /h off
```

- **예상 회수: RAM 용량의 약 40~75%** (RAM 16GB → 6~12GB, 32GB → 13~24GB)
- 되돌리기: `powercfg /h on`
- 부작용: "빠른 시작"과 최대 절전이 꺼집니다. 데스크톱이면 사실상 손해 없습니다. 노트북에서 절전 후 완전 복원을 쓰신다면 나중에 다시 켜세요.

### 0-3. 휴지통 비우기

```powershell
# 먼저 크기 확인
(Get-ChildItem 'C:\$Recycle.Bin' -Recurse -Force -File -ErrorAction SilentlyContinue |
  Measure-Object Length -Sum).Sum / 1GB

# 확인 후 비우기 (되돌릴 수 없습니다)
Clear-RecycleBin -Force
```

- **예상 회수: 0~20GB** (오래 안 비웠다면 큽니다)

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
| 최대 절전 모드 | 6~24GB |
| 휴지통 | 0~20GB |
| 임시 파일 | 2~10GB |
| 업데이트 캐시 | 1~8GB |
| DISM | 3~10GB |
| **합계** | **12~72GB** |

편차가 큰 이유는 RAM 용량과 휴지통 상태에 따라 달라지기 때문입니다.

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

```powershell
[Environment]::SetEnvironmentVariable('PIP_CACHE_DIR',    'D:\cache\pip',   'User')
[Environment]::SetEnvironmentVariable('NPM_CONFIG_CACHE', 'D:\cache\npm',   'User')
[Environment]::SetEnvironmentVariable('GRADLE_USER_HOME', 'D:\cache\gradle','User')
[Environment]::SetEnvironmentVariable('NUGET_PACKAGES',   'D:\cache\nuget', 'User')
# AI 모델을 쓰신다면 (모델 파일이 수십 GB로 커집니다)
[Environment]::SetEnvironmentVariable('HF_HOME',          'D:\cache\hf',    'User')
```

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
C:\dev\      ← 지금 작업 중인 프로젝트만 (3~5개)
D:\archive\  ← 완료된 프로젝트 (node_modules 지우고 이동)
GitHub       ← 코드는 어차피 여기 있습니다. 로컬 사본은 언제든 버려도 됩니다
```

---

## 6. Phase 3 — 그래도 95GB에 못 미치면

여기까지 했는데 부족하면 **데이터 자체가 512GB에 안 맞는 것**입니다. 선택지는 셋입니다.

| 선택지 | 비용 | 회수량 | 비고 |
|---|---|---|---|
| **외장 SSD 1TB 추가** | 10~15만원 | 무제한 | 가장 확실. 아카이브 전용으로 |
| **내장 NVMe 추가** | 10~20만원 | 무제한 | 노트북은 슬롯 여유 확인 필요 |
| 대형 앱 이동 | 0원 | 5~30GB | 설정 → 앱 → 해당 앱 → 이동 (일부만 지원) |
| 시스템 복원 축소 | 0원 | 5~20GB | `vssadmin resize shadowstorage /for=C: /on=C: /maxsize=5%` |

> 페이지 파일을 다른 드라이브로 옮기는 방법도 있지만, **단일 드라이브 시스템에서는 불가능**하고 성능 저하 위험이 있어 권하지 않습니다.

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

1. 관리자 PowerShell 열기
2. `powercfg /h off` ← 여기서 대부분 한숨 돌립니다
3. 휴지통 크기 확인 후 비우기
4. `%TEMP%` + Windows 업데이트 캐시 삭제
5. **여유 30GB 넘겼는지 확인** → 넘었으면 `Dism ... /StartComponentCleanup`
6. `Get-StorageReport.ps1` 실행해서 진짜 범인 찾기
7. WSL vhdx / Docker / node_modules 처리
8. **저장 공간 센서 켜기 + 캐시 경로 이전** ← 이걸 해야 끝납니다

항목별 세부 명령어(20개 대상 × 확인/정리/복구/주의)는 같은 폴더의 `CLEANUP-REFERENCE.md`,
자동화 스크립트는 `Free-DiskSpace.ps1`(기본 시뮬레이션), 진단은 `Get-StorageReport.ps1`을 참고하세요.
