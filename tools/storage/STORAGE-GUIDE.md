# 저장공간 관리 가이드 (Windows 기준)

저장공간 부족은 "가끔 청소"로는 안 잡힙니다. **다시 안 차오르게 만드는 구조**를 잡아야 합니다.
아래는 원인 → 구조 → 루틴 순서입니다.

---

## 0. 먼저 실측한다

추측으로 지우면 정작 큰 놈은 그대로 남습니다. 같은 폴더의 진단 스크립트를 먼저 돌리세요.

```powershell
# 빠른 점검 (1~2분) — 알려진 캐시/임시파일 위주
powershell -ExecutionPolicy Bypass -File .\Get-StorageReport.ps1 -Quick

# 전체 점검 (5~40분) — 큰 폴더/큰 파일까지
powershell -ExecutionPolicy Bypass -File .\Get-StorageReport.ps1
```

읽기 전용이라 아무것도 지우지 않습니다. 바탕화면에 `storage-report_날짜.txt` 가 생깁니다.

**이미 용량이 부족한 상태라면** 정리 스크립트를 씁니다. 기본이 시뮬레이션이라 그냥 돌려도 안전합니다.

```powershell
# 1단계: 뭐가 얼마나 나오는지 보기만 (삭제 없음)
powershell -ExecutionPolicy Bypass -File .\Free-DiskSpace.ps1

# 2단계: 관리자 PowerShell 에서 실제 실행 (항목마다 y/N 확인)
powershell -ExecutionPolicy Bypass -File .\Free-DiskSpace.ps1 -Execute
```

---

## 1. 용량이 차는 원인은 대개 이 5가지

| 유형 | 대표 경로 | 특징 |
|---|---|---|
| **캐시류** | `%TEMP%`, `%LOCALAPPDATA%\pip\Cache`, `npm-cache`, 브라우저 캐시 | 지워도 안전. 대신 **또 찹니다** → 자동화 대상 |
| **개발 잔재** | `node_modules`, `.venv`, `target`, `build`, `dist` | 프로젝트당 수백 MB~수 GB. 재생성 가능 |
| **가상디스크** | WSL `ext4.vhdx`, Docker, VM 이미지 | **한번 커지면 안에서 지워도 파일 크기가 안 줄어듦** |
| **아카이브** | 영상/사진/설치파일/다운로드 | 지우면 안 되는 것들 → **이동** 대상 |
| **OS 예약** | `hiberfil.sys`, `pagefile.sys`, 시스템 복원 | 직접 삭제 금지. **설정으로** 줄이는 것 |

---

## 2. 구조 잡기 — "다시 안 차오르게"

### 2-1. 티어를 나눈다 (가장 중요)

시스템 드라이브(C:)를 **작업 공간이 아니라 프로그램 공간**으로만 씁니다.

```
C:  OS + 설치 프로그램 + 현재 진행 중인 프로젝트만        ← 여유 20% 이상 사수
D:/G:  아카이브 (완료 프로젝트, 영상 원본, 설치파일 보관)
클라우드  문서/설정/코드 (Drive, OneDrive, GitHub)
```

C: 여유 20%는 성능 문제이기도 합니다. SSD는 여유 공간이 적으면 쓰기 속도가 떨어집니다.

### 2-2. 캐시 위치를 데이터 드라이브로 옮긴다

C:가 계속 차는 주범입니다. 환경변수로 한 번만 바꾸면 끝납니다.

```powershell
# 예시 — D:\cache 로 몰아두기 (경로는 본인 환경에 맞게)
[Environment]::SetEnvironmentVariable('PIP_CACHE_DIR', 'D:\cache\pip', 'User')
[Environment]::SetEnvironmentVariable('NPM_CONFIG_CACHE', 'D:\cache\npm', 'User')
[Environment]::SetEnvironmentVariable('HF_HOME', 'D:\cache\huggingface', 'User')   # AI 모델 쓸 경우
```

> 적용 후 새 터미널을 열어야 반영됩니다. 기존 캐시 폴더는 옮긴 뒤 삭제.

### 2-3. 큰 파일은 "지우기"가 아니라 "옮기기"

영상 원본, 설치 파일, 완료된 프로젝트는 삭제 후회가 큽니다.
아카이브 드라이브에 **날짜 폴더**로 옮기고, 6개월 뒤 다시 판단하세요.

```
G:\archive\2026-09\  ← 이번 달 밀어넣기
```

### 2-4. OS 예약 영역 조정 (효과 큼, 되돌리기 쉬움)

| 항목 | 조치 | 회수 용량 |
|---|---|---|
| 최대 절전 모드 | `powercfg /h off` (관리자) | RAM 크기의 약 40~75%. 32GB면 15~24GB |
| 시스템 복원 | 시스템 속성 → 시스템 보호 → 최대 사용량 5% 이하 | 수 GB~수십 GB |
| 페이지 파일 | 데이터 드라이브로 이동 | RAM 크기급 |

> 최대 절전 모드를 끄면 "빠른 시작"도 꺼집니다. 노트북에서 절전 후 복원을 쓰신다면 유지하세요.

### 2-5. WSL / Docker 가상디스크는 별도 관리

`ext4.vhdx`는 안에서 파일을 지워도 **자동으로 안 줄어듭니다.** 명시적으로 압축해야 합니다.

```powershell
wsl --shutdown
# 그 후 diskpart 또는 Optimize-VHD 로 compact
```

Docker는 `docker system prune -a` (사용 중이지 않은 이미지/볼륨 정리 — 실행 전 내용 확인 필수).

---

## 3. 루틴 (자동화)

| 주기 | 할 일 | 방법 |
|---|---|---|
| 자동 | 임시파일 / 휴지통 / 다운로드 30일 지난 것 | **저장소 센서** 켜기 (설정 → 시스템 → 저장 공간 → 저장 공간 센서) |
| 월 1회 | 진단 스크립트 `-Quick` 실행 | 작업 스케줄러 등록 |
| 분기 1회 | 전체 스캔 + 아카이브 이동 | 수동 |
| 상시 | C: 여유 20% 미만이면 알림 | 아래 참고 |

**저장 공간 센서**가 가장 가성비 좋습니다. Windows 기본 기능이고, 켜두면 임시파일과 휴지통·다운로드를 알아서 정리합니다.

---

## 4. 절대 하지 말 것

- `hiberfil.sys` / `pagefile.sys` / `swapfile.sys` **직접 삭제** → 설정으로 끄세요
- `C:\Windows\WinSxS` 수동 삭제 → `Dism /Online /Cleanup-Image /StartComponentCleanup` 만 사용
- 정체 모를 "청소 프로그램" 설치 → Windows 기본 도구(디스크 정리, 저장 공간 센서)로 충분
- 확인 없는 일괄 삭제 → 반드시 **먼저 리포트를 읽고**, 큰 것부터 하나씩

---

## 5. 지금 당장 급하다면 (순서대로)

1. `powercfg /h off` — 보통 가장 큰 한 방 (관리자 권한)
2. 저장 공간 센서 켜고 "지금 정리 실행"
3. `%TEMP%` + 휴지통 비우기
4. 다운로드 폴더에서 설치 파일(.exe/.msi/.zip) 아카이브로 이동
5. 안 쓰는 프로젝트의 `node_modules` / `.venv` 삭제 (재설치로 복구 가능)
6. 시스템 복원 최대 사용량 5%로 축소
