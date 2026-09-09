# Windows 11/10 디스크 정리 명령어 레퍼런스

## 전제 상황

- C 드라이브(시스템 드라이브) 512GB SSD, 현재 여유 공간 8GB (여유율 1.6%)
- 목표: 여유 공간 100GB 이상 확보
- 사용 환경: 개발자 PC (Node.js / Python 사용, WSL 사용 가능성 있음)

## 문서 사용 시 주의사항

- 이 문서의 명령어는 실제 PowerShell/명령 프롬프트에서 이 세션이 직접 실행 검증한 것이 아닙니다(이 작업 환경에는 Windows/PowerShell이 없습니다). Microsoft 공식 문서 및 실제 존재가 확인된 cmdlet/명령만 실었으며, 확신이 서지 않는 부분은 각 항목에 "(확실하지 않음 — 실행 전 확인 필요)"로 표시했습니다.
- 명령을 실행하기 전에 **관리자 권한 여부**, **대상 경로가 실제로 존재하는지**를 먼저 확인하시기 바랍니다.
- 위험도가 "위험"인 항목(WinSxS, DriverStore, pagefile.sys, hiberfil.sys)은 전용 도구(DISM, pnputil, 설정 앱)를 거치지 않고 직접 파일을 지우면 시스템 손상으로 이어질 수 있습니다.
- 되돌릴 수 없는 작업(휴지통 비우기, 이벤트 로그 삭제, 복원 지점 삭제, `docker system prune -a --volumes` 등) 전에는 정말 필요 없는 데이터인지 다시 한번 확인하세요.

---

## 요약 표

| # | 대상 | 경로 | 512GB 기준 통상 크기 | 위험도 | 복구 가능성 | 관리자 권한 |
|---|---|---|---|---|---|---|
| 1 | hiberfil.sys (최대 절전 모드) | `C:\hiberfil.sys` | RAM의 약 40~75% (예: RAM 16GB → 6~12GB) | 주의 | 자동 재생성 (다시 켜면 생성) | 필요 |
| 2 | pagefile.sys (페이지 파일) | `C:\pagefile.sys` | 2~16GB (RAM·설정에 따라 가변) | 위험 | 자동 재생성 (재부팅 시) | 필요 |
| 3 | %TEMP% / Windows\Temp | `%TEMP%`, `C:\Windows\Temp` | 2~8GB (개발 도구 사용 시 더 클 수 있음) | 안전 | 자동 재생성 | %TEMP%는 불필요 / Windows\Temp는 필요 |
| 4 | 휴지통 | 각 드라이브의 `$Recycle.Bin` | 수GB~수십GB (사용자 설정에 따름) | 주의 | 비우기 전까지만 개별 복구 가능, 비우면 복구 불가 | 불필요 |
| 5 | Windows Update 다운로드 캐시 | `C:\Windows\SoftwareDistribution\Download` | 1~10GB (누적 시 20GB+) | 안전 | 자동 재다운로드 | 필요 |
| 6 | WinSxS / 구성 요소 저장소 | `C:\Windows\WinSxS` | 5~15GB | 위험 (직접 삭제 금지, DISM 경유만) | 부분적 (ResetBase 이후 이전 버전 제거는 복구 불가) | 필요 |
| 7 | Windows.old | `C:\Windows.old` | 10~30GB | 안전 (단, 롤백 옵션 상실 유의) | 삭제 후 복구 불가 (그 전엔 이전 버전 롤백 가능) | 필요 |
| 8 | 시스템 복원 / 섀도 복사본 | `System Volume Information` (직접 접근 불가, vssadmin 경유) | 2~10GB (사용자 설정 한도 내) | 주의 | 삭제한 복원 지점은 복구 불가 | 필요 |
| 9 | 배달 최적화 캐시 | `C:\Windows\SoftwareDistribution\DeliveryOptimization` | 1~5GB | 안전 | 자동 재생성/재다운로드 | 필요 |
| 10 | 크래시 덤프 / Memory.dmp | `C:\Windows\Memory.dmp`, `C:\Windows\Minidump`, `%LOCALAPPDATA%\CrashDumps` | Memory.dmp는 RAM과 비슷(수GB~수십GB), Minidump는 각 수백KB | 안전 | 복구 불필요 (문제 재발 시 재생성) | Memory.dmp/Minidump는 필요, CrashDumps는 대체로 불필요 |
| 11 | 다운로드 폴더 | `%USERPROFILE%\Downloads` | 매우 가변 (개발자는 5~50GB+ 가능) | 주의 (직접 검토 필요) | 재다운로드 가능한 것도 있고 불가한 것도 있음 | 불필요 |
| 12 | node_modules 등 프로젝트 잔재 | 각 프로젝트 폴더 하위 `node_modules`, `dist`, `build`, `.next`, `target`, `__pycache__`, `.venv` 등 | 프로젝트당 200MB~2GB, 누적 시 수십GB | 안전 | 자동 재생성 (재설치 명령으로) | 불필요 |
| 13 | npm/pip/nuget/gradle/maven/yarn 캐시 | 아래 상세 섹션 참고 | 항목별 1~10GB, 합계 5~30GB | 안전 | 자동 재다운로드 | 불필요 |
| 14 | WSL ext4.vhdx | `%LOCALAPPDATA%\Packages\<배포판>\LocalState\ext4.vhdx` (또는 `%LOCALAPPDATA%\wsl\<GUID>\ext4.vhdx`) | 5~50GB+ (thin-provisioned, 자동 축소 안 됨) | 주의 | 압축 자체는 데이터 손실 없음 | 일부 단계에서 필요 |
| 15 | Docker Desktop 데이터 | `%LOCALAPPDATA%\Docker`, WSL2 기반 시 `%LOCALAPPDATA%\Docker\wsl\data\ext4.vhdx` | 5~60GB+ | 주의 | 이미지는 재다운로드 가능, 볼륨 데이터는 복구 불가 | 대체로 불필요 |
| 16 | 브라우저 캐시 (Chrome/Edge) | `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache`, `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache` | 각 0.5~5GB | 안전 | 자동 재생성 | 불필요 |
| 17 | OneDrive 로컬 동기화 파일 | `%USERPROFILE%\OneDrive` | 계정 사용량에 따라 수GB~수백GB | 주의 (삭제 아닌 "공간 확보"로 처리) | 온디맨드 기능으로 재다운로드 가능 | 불필요 |
| 18 | Windows 검색 인덱스 | `C:\ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb` | 0.5~5GB | 주의 (재인덱싱 동안 성능 저하) | 자동 재생성(재인덱싱) | 필요 |
| 19 | 이벤트 로그 | `C:\Windows\System32\winevt\Logs\*.evtx` | 합계 0.5~2GB | 주의 (진단 이력 상실) | 삭제 후 복구 불가 | 필요 |
| 20 | 폰트/드라이버 저장소 (DriverStore) | `C:\Windows\System32\DriverStore\FileRepository` | 3~10GB | 위험 (직접 삭제 절대 금지, pnputil 경유만) | 제조사 재설치로만 복구 | 필요 |

---

## 1. hiberfil.sys (최대 절전 모드)

**확인 명령**
```powershell
Get-Item -Path C:\hiberfil.sys -Force -ErrorAction SilentlyContinue | Select-Object Name, Length
```
PowerShell에서 접근이 안 보이면, 관리자 권한 명령 프롬프트에서 `dir C:\hiberfil.sys /a` 로 확인합니다.

**정리 명령** (관리자 PowerShell/CMD)
```powershell
powercfg /hibernate off
```
최대 절전 모드와 "빠른 시작"을 함께 끄며 `hiberfil.sys` 파일 자체를 제거합니다. 완전히 끄지 않고 크기만 줄이려면:
```powershell
powercfg /hibernate /size 40
```
(0~100 사이의 퍼센트로 RAM 대비 크기를 조정, Windows 8 이상 지원)

**되돌리는 법**
```powershell
powercfg /hibernate on
```
파일이 다시 생성되고 최대 절전 모드/빠른 시작이 복원됩니다.

**주의사항**
- 최대 절전 모드를 사용하는 노트북이라면 끄기 전에 사용 여부를 확인하세요.
- "빠른 시작"도 함께 꺼지므로 부팅 속도가 약간 느려질 수 있습니다.

---

## 2. pagefile.sys (페이지 파일)

**확인 명령**
```powershell
Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage
```

**정리 명령**
표준적이고 안전한 방법은 GUI입니다: 설정 → 시스템 → 정보 → 고급 시스템 설정 → 성능 "설정" → 고급 탭 → 가상 메모리 "변경". 여기서 "자동으로 관리"를 해제하고 사용자 지정 크기로 줄일 수 있습니다.

PowerShell로 조정하려면(재부팅 후 적용, 사전에 반드시 백업/확인):
```powershell
$pf = Get-CimInstance Win32_PageFileSetting
Set-CimInstance -InputObject $pf -Property @{ InitialSize = 2048; MaximumSize = 4096 }
```
(확실하지 않음 — 환경에 따라 재부팅이 필요할 수 있으며, 페이지 파일이 자동 관리 상태면 `Win32_PageFileSetting` 결과가 비어 있을 수 있습니다. 이 경우 GUI 사용을 권장합니다.)

**되돌리는 법**
GUI에서 "자동으로 관리"를 다시 체크하면 시스템 기본값으로 복귀합니다.

**주의사항**
- `pagefile.sys`는 직접 삭제할 수 없으며(사용 중 파일), 반드시 위 설정 경로로만 크기를 조정합니다.
- 지나치게 줄이면 메모리 부족 시 시스템 불안정, 일부 앱 오류, 크래시 덤프 생성 불가 등의 문제가 생길 수 있습니다.
- RAM이 충분히 크지 않다면(예: 16GB 미만) 완전히 끄지 말고 크기만 조정하는 것을 권장합니다.

---

## 3. %TEMP% / Windows\Temp

**확인 명령**
```powershell
Get-ChildItem $env:TEMP -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
Get-ChildItem C:\Windows\Temp -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
```

**정리 명령**
```powershell
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
```
(두 번째 명령은 관리자 권한 필요)

**되돌리는 법**
없음 — 임시 파일이므로 필요 시 해당 프로그램이 다시 생성합니다.

**주의사항**
- 실행 중인 프로그램이 사용 중인 파일은 삭제가 실패할 수 있습니다(정상 동작이며 무시해도 됩니다).
- 삭제 중 오류가 나도 스크립트를 멈추지 말고 `-ErrorAction SilentlyContinue`로 건너뛰도록 합니다.

---

## 4. 휴지통

**확인 명령**
```powershell
$shell = New-Object -ComObject Shell.Application
$bin = $shell.NameSpace(0xA)
"{0:N2} GB" -f (($bin.Items() | Measure-Object -Property Size -Sum).Sum / 1GB)
```

**정리 명령**
```powershell
Clear-RecycleBin -DriveLetter C -Force
```
(PowerShell 5.1 이상, Windows 10/11 기본 포함)

**되돌리는 법**
비우기 전이라면 휴지통에서 개별 파일을 "복원"할 수 있습니다. `Clear-RecycleBin` 실행 후에는 복구 불가합니다(복구 프로그램으로도 보장되지 않음).

**주의사항**
- 되돌릴 수 없는 작업이므로 정말 필요 없는 항목만 남아있는지 확인 후 실행하세요.

---

## 5. Windows Update 다운로드 캐시

**확인 명령**
```powershell
Get-ChildItem "C:\Windows\SoftwareDistribution\Download" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
```

**정리 명령** (관리자 PowerShell)
```powershell
Stop-Service -Name wuauserv -Force
Stop-Service -Name bits -Force
Remove-Item "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service -Name bits
Start-Service -Name wuauserv
```

**되돌리는 법**
Windows Update가 필요 시 자동으로 다시 다운로드합니다.

**주의사항**
- 업데이트 설치가 진행 중일 때는 서비스 중지가 실패할 수 있습니다. 완료 후 다시 시도하세요.

---

## 6. WinSxS / 구성 요소 저장소

**절대 탐색기나 `Remove-Item`으로 이 폴더의 내용을 직접 삭제하지 마세요.** 하드링크 구조로 되어 있어 겉보기 크기와 실제 디스크 사용량이 다르며, 임의 삭제 시 Windows 업데이트/복구/DISM 자체가 손상될 수 있습니다. 반드시 DISM을 통해서만 정리합니다.

**확인 명령** (관리자, 폴더 크기 합산보다 정확)
```powershell
Dism.exe /Online /Cleanup-Image /AnalyzeComponentStore
```
출력의 "구성 요소 저장소 정리 권장" 여부와 실제 크기를 확인합니다.

**정리 명령** (관리자)
```powershell
Dism.exe /Online /Cleanup-Image /StartComponentCleanup
```
더 적극적으로 이전 버전을 완전히 제거하려면(용량은 더 확보되지만 되돌릴 수 없음):
```powershell
Dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase
```

**되돌리는 법**
`/StartComponentCleanup`만 실행한 경우 시스템 동작에는 영향 없습니다. `/ResetBase`를 사용하면 그 시점 이전의 업데이트를 "제거"하는 옵션 자체가 사라지며 되돌릴 수 없습니다.

**주의사항**
- `/ResetBase` 실행 후에는 최근 설치한 누적 업데이트를 제거(롤백)할 수 없게 됩니다. 업데이트가 안정적으로 동작 중일 때만 사용하세요.
- WinSxS 폴더 자체의 "표시상 크기"는 실제 디스크 점유량보다 훨씬 크게 보일 수 있습니다(하드링크 때문).

---

## 7. Windows.old

**확인 명령**
```powershell
Get-ChildItem "C:\Windows.old" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
```

**정리 명령**
`Windows.old`는 특수 권한(ACL)으로 보호되어 있어 `Remove-Item`으로 지우면 일부 파일에서 권한 오류가 날 수 있습니다. 표준 방법은 디스크 정리 도구입니다.
```powershell
cleanmgr.exe
```
실행 후 "시스템 파일 정리" 버튼을 누르고 "이전 Windows 설치" 항목을 체크하여 정리합니다. (또는 설정 → 시스템 → 저장공간 → 임시 파일에서 "이전 Windows 설치 항목" 선택)

**되돌리는 법**
`Windows.old`가 남아있고 업그레이드 후 10일이 지나지 않았다면 설정 → 시스템 → 복구 → "이전 버전의 Windows로 되돌리기"로 롤백할 수 있습니다. 이 폴더를 지우면 해당 옵션 자체가 사라져 롤백이 불가능합니다.

**주의사항**
- 업그레이드 직후라 마음이 바뀔 수 있다면 며칠 더 유지 후 정리하는 것을 권장합니다.

---

## 8. 시스템 복원 / 섀도 복사본

**확인 명령** (관리자)
```powershell
vssadmin list shadowstorage
vssadmin list shadows
```

**정리 명령** (관리자)
```powershell
vssadmin delete shadows /for=C: /all
```
저장 공간 한도 자체를 줄이려면:
```powershell
vssadmin resize shadowstorage /for=C: /on=C: /maxsize=5GB
```
시스템 보호 기능 자체를 끄려면 시스템 속성 → "시스템 보호" 탭 → 구성에서 보호를 해제합니다(즉시 관련 공간 반환).

**되돌리는 법**
삭제한 복원 지점/섀도 복사본은 복구할 수 없습니다. 새 복원 지점은 다음 명령으로 다시 만들 수 있습니다(향후 대비용):
```powershell
Checkpoint-Computer -Description "수동 생성" -RestorePointType MODIFY_SETTINGS
```

**주의사항**
- 시스템에 문제가 생겼을 때 되돌릴 수단이 사라지므로, 최근에 큰 변경(드라이버 설치 등)을 했다면 신중히 판단하세요.

---

## 9. 배달 최적화 캐시

**확인 명령**
```powershell
Get-ChildItem "C:\Windows\SoftwareDistribution\DeliveryOptimization" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
```

**정리 명령** (관리자)
```powershell
Delete-DeliveryOptimizationCache -Force
```
(Windows 10/11에 기본 포함된 DeliveryOptimization 모듈의 cmdlet)
또는 설정 → Windows 업데이트 → 고급 옵션 → 배달 최적화 → 고급 옵션에서 "정리" 버튼 사용.

**되돌리는 법**
필요 시 자동으로 다시 캐시가 쌓입니다.

**주의사항**
- 특별히 없음. 안전한 정리 대상입니다.

---

## 10. 크래시 덤프 / Memory.dmp

**확인 명령**
```powershell
Get-Item "C:\Windows\Memory.dmp" -ErrorAction SilentlyContinue | Select-Object Length
Get-ChildItem "C:\Windows\Minidump" -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
Get-ChildItem "$env:LOCALAPPDATA\CrashDumps" -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
```

**정리 명령** (Memory.dmp, Minidump는 관리자 필요)
```powershell
Remove-Item "C:\Windows\Memory.dmp" -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\Minidump\*" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\CrashDumps\*" -Force -ErrorAction SilentlyContinue
```
향후 커널 덤프 자체를 만들지 않게 하려면: 제어판 → 시스템 → 고급 시스템 설정 → "시작 및 복구" 설정에서 "쓰기 디버깅 정보"를 "(없음)"으로 변경합니다(설정 앱 경유, 레지스트리 직접 수정은 권장하지 않음).

**되돌리는 법**
없음(디버깅 목적 파일이라 복구가 필요하지 않으며, 문제가 재발하면 다시 생성됩니다).

**주의사항**
- 최근 블루스크린(BSOD) 원인을 분석해야 한다면 지우기 전에 필요 여부를 확인하세요.

---

## 11. 다운로드 폴더

**확인 명령**
```powershell
Get-ChildItem "$env:USERPROFILE\Downloads" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum

# 큰 파일 상위 20개
Get-ChildItem "$env:USERPROFILE\Downloads" -Recurse -Force -ErrorAction SilentlyContinue |
  Sort-Object Length -Descending | Select-Object -First 20 FullName, @{n='MB';e={[math]::Round($_.Length/1MB,1)}}
```

**정리 명령**
자동 일괄 삭제 스크립트는 권장하지 않습니다. 위 명령으로 큰 파일 목록을 뽑아 직접 검토 후 필요 없는 것만 삭제하세요(탐색기에서 삭제하면 휴지통을 거칩니다).

**되돌리는 법**
휴지통을 거쳐 삭제했다면 휴지통 비우기 전까지 복원 가능합니다.

**주의사항**
- 설치 프로그램(exe/msi), ISO, 압축 해제한 소스 등은 재다운로드 가능한지 확인 후 지우는 것이 안전합니다.
- 이 폴더는 절대 자동화 스크립트로 통째로 비우지 마세요.

---

## 12. node_modules 등 프로젝트 잔재

**확인 명령**
개발 폴더 경로를 좁혀서 실행하는 것을 권장합니다(전체 드라이브 탐색은 느립니다).
```powershell
Get-ChildItem -Path "C:\Users\<사용자명>\projects" -Filter node_modules -Recurse -Directory -Force -ErrorAction SilentlyContinue |
  ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    [PSCustomObject]@{ Path = $_.FullName; SizeGB = [math]::Round($size/1GB,2) }
  } | Sort-Object SizeGB -Descending
```

**정리 명령**
```powershell
Remove-Item -Recurse -Force "C:\경로\프로젝트명\node_modules"
```
같은 방식으로 `dist`, `build`, `.next`, `target`, `__pycache__`, `.venv` 등도 개별 확인 후 삭제합니다. (서드파티 정리 유틸(npkill 등)은 이 문서에서 직접 검증하지 않았으므로 추천하지 않으며, 표준적인 `Remove-Item` 방식을 권장합니다.)

**되돌리는 법**
해당 프로젝트 폴더에서 패키지 매니저로 재설치하면 복원됩니다.
```powershell
npm install   # 또는 yarn install / pnpm install
```

**주의사항**
- 현재 사용하지 않는 오래된 프로젝트인지 확인 후 삭제하세요. `git status`로 커밋 안 된 변경사항이 없는지도 확인이 필요합니다.

---

## 13. npm / pip / nuget / gradle / maven / yarn 캐시

**경로**
- npm: `%APPDATA%\npm-cache` (실제 경로는 `npm config get cache`로 확인)
- yarn (Classic): `%LOCALAPPDATA%\Yarn\Cache` 하위 (정확한 경로는 `yarn cache dir`로 확인)
- pip: `%LOCALAPPDATA%\pip\Cache` (정확한 경로는 `pip cache dir`로 확인)
- NuGet: 전역 패키지 `%USERPROFILE%\.nuget\packages`, HTTP 캐시 `%LOCALAPPDATA%\NuGet\v3-cache`
- Gradle: `%USERPROFILE%\.gradle\caches`
- Maven: `%USERPROFILE%\.m2\repository`

**확인 명령**
```powershell
npm cache verify
pip cache info
yarn cache dir
dotnet nuget locals all --list

# gradle, maven은 캐시 크기 조회 전용 명령이 따로 없어 폴더 크기로 확인합니다 (확실하지 않음 — 버전별 차이 가능)
Get-ChildItem "$env:USERPROFILE\.gradle\caches" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum
Get-ChildItem "$env:USERPROFILE\.m2\repository" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum
```

**정리 명령**
```powershell
npm cache clean --force
pip cache purge
yarn cache clean
dotnet nuget locals all --clear
```
Gradle (데몬을 먼저 종료해야 파일 잠금 문제가 없습니다):
```powershell
gradle --stop
Remove-Item -Recurse -Force "$env:USERPROFILE\.gradle\caches"
```
Maven은 전용 정리 명령이 없어 리포지토리 폴더를 직접 삭제합니다:
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.m2\repository"
```

**되돌리는 법**
각 패키지 매니저가 다음 빌드/설치 시 필요한 만큼 자동으로 다시 받습니다.

**주의사항**
- 오프라인 환경에서 빌드해야 하는 프로젝트가 있다면, 해당 의존성을 다시 받을 수 있는 인터넷 연결이 있는지 먼저 확인하세요.
- NuGet은 nuget.exe(클래식 CLI)를 쓰는 경우 옵션 표기가 `-list`, `-clear`(단일 하이픈)로 다릅니다. 위 명령은 dotnet CLI(`dotnet nuget ...`, 이중 하이픈) 기준입니다.

---

## 14. WSL ext4.vhdx

**확인 명령**
```powershell
wsl --list --verbose
```
표시된 배포판명을 바탕으로 `%LOCALAPPDATA%\Packages\` 하위(Microsoft Store로 설치한 경우) 또는 `%LOCALAPPDATA%\wsl\` 하위(독립 실행형 `wsl.exe`로 설치한 경우, 폴더명이 GUID)에서 `ext4.vhdx` 파일을 찾아 크기를 확인합니다. 설치 방식에 따라 위치가 다르므로 직접 탐색이 필요합니다.
```powershell
Get-Item "<찾은 ext4.vhdx 경로>" | Select-Object Length
```

**정리 명령 — 방법 A (Hyper-V 모듈 필요)**
```powershell
wsl --shutdown
Optimize-VHD -Path "<ext4.vhdx 경로>" -Mode Full
```
`Optimize-VHD`는 **Hyper-V PowerShell 모듈**에 포함되어 있으며, Hyper-V 기능이 활성화되어 있어야 사용할 수 있습니다(Windows Home 에디션 등 Hyper-V가 없는 환경에서는 사용 불가). 사전에 다음으로 확인하세요:
```powershell
Get-Command Optimize-VHD -ErrorAction SilentlyContinue
```
결과가 없으면 방법 B를 사용합니다.

**정리 명령 — 방법 B (Hyper-V 없이, diskpart 사용)**
```powershell
wsl --shutdown
diskpart
```
diskpart 프롬프트 안에서:
```
select vdisk file="<ext4.vhdx 경로>"
attach vdisk readonly
compact vdisk
detach vdisk
exit
```

**되돌리는 법**
압축(compact)은 빈 공간만 회수하는 작업으로 데이터 손실이 없습니다. 되돌릴 필요가 없습니다.

**주의사항**
- 반드시 `wsl --shutdown`으로 WSL을 완전히 종료한 뒤 작업하세요. 실행 중에 작업하면 실패하거나 파일이 손상될 수 있습니다.
- 작업 도중 강제 종료(전원 차단 등)하지 마세요.

---

## 15. Docker Desktop 데이터

**확인 명령**
```powershell
docker system df
```
(이미지, 컨테이너, 로컬 볼륨, 빌드 캐시별 사용량을 보여줍니다)

**정리 명령**
```powershell
docker system prune          # 중지된 컨테이너, 미사용 네트워크, dangling 이미지 등 (볼륨 제외, 비교적 안전)
docker system prune -a --volumes   # 사용하지 않는 이미지 전체 + 미사용 볼륨까지 삭제 (되돌릴 수 없음)
```
Docker Desktop 자체 데이터 디스크 이미지를 줄이려면 Docker Desktop 설정 → Resources → Advanced에서 디스크 이미지 크기를 확인/축소하거나, Troubleshoot 메뉴의 "Clean / Purge data"를 사용합니다.

**되돌리는 법**
삭제된 이미지는 `docker pull`로 재다운로드 가능합니다. 볼륨에 저장된 데이터(DB 데이터 등)는 백업이 없다면 복구할 수 없습니다.

**주의사항**
- `--volumes` 옵션은 실제 애플리케이션 데이터(DB 볼륨 등)를 지울 수 있습니다. 실행 전 `docker volume ls`로 어떤 볼륨이 있는지 반드시 확인하세요.

---

## 16. 브라우저 캐시 (Chrome / Edge)

**확인 명령**
```powershell
Get-ChildItem "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum
```

**정리 명령**
브라우저를 완전히 종료한 뒤 실행합니다.
```powershell
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache\*" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache\*" -ErrorAction SilentlyContinue
```
또는 각 브라우저의 설정 → 개인정보 및 보안 → "인터넷 사용 기록 삭제"에서 "캐시된 이미지 및 파일"만 선택하는 방법이 더 안전합니다(프로필 손상 위험이 적음).

**되돌리는 법**
필요 없음 — 다시 방문하면 캐시가 재생성됩니다.

**주의사항**
- 브라우저가 실행 중인 상태에서 강제로 삭제하면 파일 잠금으로 실패하거나 프로필이 손상될 수 있습니다. 반드시 완전히 종료 후 진행하세요.

---

## 17. OneDrive 로컬 동기화 파일

**확인 명령**
```powershell
Get-ChildItem "$env:USERPROFILE\OneDrive" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
```

**정리 명령**
OneDrive는 일반 파일처럼 삭제하면 클라우드에서도 삭제될 위험이 있으므로, **"파일 온디맨드(Files On-Demand)"** 기능을 이용해 로컬 사본만 지우는 방식을 사용해야 합니다.
1. OneDrive 설정(트레이 아이콘 → 설정 → 설정 탭)에서 "공간 절약을 위해 파일을 사용할 때 다운로드" 옵션이 켜져 있는지 확인
2. 탐색기에서 OneDrive 폴더의 파일/폴더를 우클릭 → **"공간 확보(Free up space)"**

자동화된 안전한 PowerShell 명령은 확인되지 않아 (확실하지 않음 — GUI 사용 권장) GUI 조작을 권장합니다.

**되돌리는 법**
"공간 확보"된 파일은 온라인 전용 상태가 되며, 더블클릭하면 자동으로 다시 다운로드됩니다.

**주의사항**
- 온디맨드 기능이 꺼져 있으면 "공간 확보" 메뉴 자체가 동작하지 않을 수 있습니다. 먼저 설정을 확인하세요.

---

## 18. Windows 검색 인덱스 (Windows.edb)

**확인 명령**
```powershell
Get-Item "C:\ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb" -Force -ErrorAction SilentlyContinue | Select-Object Length
```

**정리 명령** (관리자)
```powershell
Stop-Service -Name WSearch -Force
Remove-Item "C:\ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb" -Force -ErrorAction SilentlyContinue
Start-Service -Name WSearch
```
더 안전한 방법: 설정 → 개인 정보 및 보안 → 검색 → "고급 인덱싱 옵션" → "고급" 탭 → "다시 빌드" 버튼(GUI 경유, Windows 버전별로 메뉴 위치가 다를 수 있습니다).

**되돌리는 법**
직접적인 복구는 아니지만, 서비스 재시작 시 자동으로 재인덱싱이 시작됩니다(파일 수에 따라 수십 분~수 시간 소요).

**주의사항**
- 재인덱싱이 끝날 때까지 파일 검색 결과가 불완전할 수 있습니다.

---

## 19. 이벤트 로그

**확인 명령**
```powershell
Get-WinEvent -ListLog * -ErrorAction SilentlyContinue |
  Sort-Object FileSize -Descending |
  Select-Object -First 20 LogName, @{n='SizeMB';e={[math]::Round($_.FileSize/1MB,1)}}
```

**정리 명령** (관리자)
```powershell
wevtutil el | ForEach-Object { wevtutil cl "$_" }
```
개별 로그만 지우려면 이벤트 뷰어(`eventvwr.msc`)에서 해당 로그 우클릭 → "로그 지우기"를 사용합니다.

**되돌리는 법**
없음 — 삭제한 로그는 복구할 수 없습니다.

**주의사항**
- 최근 오류나 장애를 분석해야 할 상황이라면 지우기 전에 필요한 로그를 내보내기(Export)해 두세요.

---

## 20. 폰트/드라이버 저장소 (DriverStore)

**절대 `C:\Windows\System32\DriverStore\FileRepository` 폴더의 파일/하위폴더를 탐색기나 `Remove-Item`으로 직접 삭제하지 마세요.** 현재 사용 중인 드라이버 파일까지 삭제되면 장치 인식 불가, 부팅 실패 등으로 이어질 수 있습니다. 반드시 `pnputil` 또는 설정 앱의 "임시 파일 정리" 기능을 거쳐야 합니다.

**확인 명령** (관리자)
```powershell
Get-ChildItem "C:\Windows\System32\DriverStore\FileRepository" -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum
pnputil /enum-drivers
```

**정리 명령** (관리자)
```powershell
pnputil /enum-drivers
```
목록에서 더 이상 필요 없는 이전 버전 드라이버(`oemXX.inf` 형태)를 확인한 뒤, 해당 항목만 선별하여 제거합니다.
```powershell
pnputil /delete-driver oem10.inf /uninstall
```
현재 사용 중인 드라이버까지 강제로 지우는 `/force` 옵션은 장치 오작동 위험이 있으므로 신중히 사용하세요.

또는 설정 → 시스템 → 저장공간 → 임시 파일에서 "장치 드라이버 패키지" 항목만 선택하여 정리하면, 현재 사용 중이지 않은 이전 버전만 자동으로 선별되어 상대적으로 안전합니다.

**되돌리는 법**
삭제한 드라이버가 나중에 필요해지면 제조사 웹사이트에서 다시 다운로드해 설치해야 합니다.

**주의사항**
- 그래픽카드, 칩셋 등 핵심 드라이버는 여러 버전이 함께 보관되어 있을 수 있으니, 현재 정상 동작 중인 드라이버까지 지우지 않도록 `pnputil /enum-drivers` 출력에서 버전과 게시 이름을 신중히 확인하세요.

---

## 우선순위 참고 (여유 8GB → 목표 100GB+)

> **실행 순서는 이 문서가 아니라 `STRATEGY-512GB.md`를 따르세요.**
> 여유 8GB 상태에서는 DISM 등 임시 공간을 쓰는 작업이 실패하므로,
> 확실히 회수되는 항목으로 30GB를 먼저 확보한 뒤에 실행해야 합니다.
> 이 문서는 "각 항목을 어떻게 다루는가"의 레퍼런스입니다.

일반적으로 위험도 "안전" 항목(3, 5, 9, 10, 12, 13, 16)과 "주의"이지만 개발자 환경에서 부피가 큰 항목(11 다운로드, 14 WSL, 15 Docker)을 먼저 정리하는 것이 효율적입니다. "위험" 항목(2, 6, 20)과 pagefile/hiberfil은 반드시 전용 도구·설정 경로로만 처리하세요.
