<#
.SYNOPSIS
    Windows 저장공간 긴급 확보 스크립트

.DESCRIPTION
    기본은 시뮬레이션(-WhatIf 성격)입니다. 각 항목이 얼마나 확보되는지 "보여주기만" 하고
    아무것도 지우지 않습니다. 실제 실행하려면 -Execute 를 붙이세요.
    -Execute 를 붙여도 항목마다 Y/N 을 물어봅니다 (-Yes 로 생략 가능).

    삭제하지 않고 "목록만" 보고하는 항목: 다운로드 폴더 큰 파일, node_modules, WSL vhdx.
    이것들은 판단이 필요해서 자동 삭제 대상에서 뺐습니다.

.PARAMETER Execute
    실제로 정리를 수행합니다. 없으면 시뮬레이션.

.PARAMETER Yes
    항목별 확인 프롬프트를 생략합니다 (-Execute 와 함께 쓸 때만 의미 있음).

.PARAMETER ResetBase
    DISM 구성 요소 정리 시 /ResetBase 를 추가합니다.
    더 많이 확보되지만 기존 업데이트 제거(롤백)가 불가능해집니다. 기본 꺼짐.

.EXAMPLE
    # 1단계: 뭐가 얼마나 나오는지 확인만
    powershell -ExecutionPolicy Bypass -File .\Free-DiskSpace.ps1

.EXAMPLE
    # 2단계: 관리자 PowerShell 에서 실제 실행
    powershell -ExecutionPolicy Bypass -File .\Free-DiskSpace.ps1 -Execute
#>
#Requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$Execute,
    [switch]$Yes,
    [switch]$ResetBase
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

# ------------------------------------------------------------------ 공통
function Format-Size {
    param([double]$Bytes)
    if     ($Bytes -ge 1TB) { '{0:N2} TB' -f ($Bytes / 1TB) }
    elseif ($Bytes -ge 1GB) { '{0:N2} GB' -f ($Bytes / 1GB) }
    elseif ($Bytes -ge 1MB) { '{0:N1} MB' -f ($Bytes / 1MB) }
    else                    { '{0:N0} KB' -f ($Bytes / 1KB) }
}

function Get-PathBytes {
    param([string]$Path)
    if (-not $Path -or -not (Test-Path -LiteralPath $Path -ErrorAction SilentlyContinue)) { return 0.0 }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $item) { return 0.0 }
    if (-not $item.PSIsContainer) { return [double]$item.Length }
    $m = Get-ChildItem -LiteralPath $Path -Recurse -Force -File -ErrorAction SilentlyContinue |
         Measure-Object -Property Length -Sum
    return [double]($m.Sum)
}

function Get-FreeBytes {
    param([string]$Drive = $env:SystemDrive)
    $d = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$($Drive.TrimEnd('\'))'" -ErrorAction SilentlyContinue
    if ($d) { [double]$d.FreeSpace } else { 0.0 }
}

$currentIdentity  = [Security.Principal.WindowsIdentity]::GetCurrent()
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
$script:IsAdmin   = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

function Confirm-Step {
    param([string]$Name)
    if (-not $Execute) { return $false }
    if ($Yes)          { return $true }
    $a = Read-Host "  >> '$Name' 실행할까요? (y/N)"
    return ($a -match '^(y|Y)')
}

function Show-Step {
    param([int]$No, [string]$Name, [double]$EstBytes, [string]$Note = '')
    Write-Host ''
    Write-Host ("[{0}] {1}" -f $No, $Name) -ForegroundColor Cyan
    if ($EstBytes -gt 0) { Write-Host ("     확보 예상: {0}" -f (Format-Size $EstBytes)) -ForegroundColor Yellow }
    else                 { Write-Host  '     확보 예상: 없음 (해당 없음 또는 이미 비어 있음)' -ForegroundColor DarkGray }
    if ($Note) { Write-Host "     $Note" -ForegroundColor DarkGray }
}

function Remove-Contents {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -ErrorAction SilentlyContinue)) { return }
    Get-ChildItem -LiteralPath $Path -Force -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# ------------------------------------------------------------------ 시작
$sysDrive  = $env:SystemDrive
$freeStart = Get-FreeBytes $sysDrive

Write-Host ''
Write-Host ('=' * 72)
Write-Host '  Windows 저장공간 긴급 확보'
Write-Host ('=' * 72)
Write-Host ("  시각        : {0}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-Host ("  시스템 드라이브: {0}  현재 여유 {1}" -f $sysDrive, (Format-Size $freeStart))
Write-Host ("  관리자 권한 : {0}" -f $(if ($script:IsAdmin) { '예' } else { '아니오  << 일부 항목 건너뜀' }))
Write-Host ("  모드        : {0}" -f $(if ($Execute) { '실제 실행' } else { '시뮬레이션 (아무것도 지우지 않음)' })) `
    -ForegroundColor $(if ($Execute) { 'Red' } else { 'Green' })
if (-not $script:IsAdmin) {
    Write-Host '  → 관리자 PowerShell 에서 실행하면 확보량이 크게 늘어납니다.' -ForegroundColor Yellow
}

$estTotal = 0.0

# ------------------------------------------------------------------ 1. 최대 절전 모드
$hib = Get-PathBytes "$sysDrive\hiberfil.sys"
$estTotal += $hib
Show-Step 1 '최대 절전 모드 해제 (powercfg /h off)' $hib `
    '주의: 노트북 "절전 후 복원"과 빠른 시작이 꺼집니다. 되돌리기: powercfg /h on'
if ($hib -gt 0 -and $script:IsAdmin -and (Confirm-Step '최대 절전 모드 해제')) {
    & powercfg /h off
    Write-Host '     완료' -ForegroundColor Green
} elseif ($hib -gt 0 -and -not $script:IsAdmin) {
    Write-Host '     건너뜀 (관리자 권한 필요)' -ForegroundColor DarkYellow
}

# ------------------------------------------------------------------ 2. 임시 파일
$tmpUser = Get-PathBytes $env:TEMP
$tmpWin  = Get-PathBytes "$env:SystemRoot\Temp"
$estTotal += ($tmpUser + $tmpWin)
Show-Step 2 '임시 파일 정리 (%TEMP% + Windows\Temp)' ($tmpUser + $tmpWin) `
    ("사용자 {0} / 시스템 {1}. 사용 중인 파일은 자동으로 건너뜁니다." -f (Format-Size $tmpUser), (Format-Size $tmpWin))
if (($tmpUser + $tmpWin) -gt 0 -and (Confirm-Step '임시 파일 정리')) {
    Remove-Contents $env:TEMP
    if ($script:IsAdmin) { Remove-Contents "$env:SystemRoot\Temp" }
    Write-Host '     완료' -ForegroundColor Green
}

# ------------------------------------------------------------------ 3. 휴지통
$bin = Get-PathBytes "$sysDrive\`$Recycle.Bin"
$estTotal += $bin
Show-Step 3 '휴지통 비우기' $bin '되돌릴 수 없습니다. 필요한 파일이 없는지 먼저 확인하세요.'
if ($bin -gt 0 -and (Confirm-Step '휴지통 비우기')) {
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue
    Write-Host '     완료' -ForegroundColor Green
}

# ------------------------------------------------------------------ 4. Windows 업데이트 캐시
$wu = Get-PathBytes "$env:SystemRoot\SoftwareDistribution\Download"
$estTotal += $wu
Show-Step 4 'Windows 업데이트 다운로드 캐시' $wu '안전합니다. 필요하면 Windows 가 다시 받습니다.'
if ($wu -gt 0 -and $script:IsAdmin -and (Confirm-Step 'Windows 업데이트 캐시 정리')) {
    Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
    Remove-Contents "$env:SystemRoot\SoftwareDistribution\Download"
    Start-Service wuauserv -ErrorAction SilentlyContinue
    Write-Host '     완료' -ForegroundColor Green
} elseif ($wu -gt 0 -and -not $script:IsAdmin) {
    Write-Host '     건너뜀 (관리자 권한 필요)' -ForegroundColor DarkYellow
}

# ------------------------------------------------------------------ 5. 배달 최적화 / 크래시 덤프
$doPath = "$env:SystemRoot\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization"
$do     = Get-PathBytes $doPath
$dumps  = (Get-PathBytes "$env:LOCALAPPDATA\CrashDumps") + (Get-PathBytes "$env:SystemRoot\Memory.dmp")
$estTotal += ($do + $dumps)
Show-Step 5 '배달 최적화 캐시 + 크래시 덤프' ($do + $dumps) `
    ("배달최적화 {0} / 덤프 {1}. 둘 다 지워도 안전합니다." -f (Format-Size $do), (Format-Size $dumps))
if (($do + $dumps) -gt 0 -and (Confirm-Step '배달 최적화 캐시 + 덤프 정리')) {
    if ($script:IsAdmin) {
        Remove-Contents $doPath
        Remove-Item -LiteralPath "$env:SystemRoot\Memory.dmp" -Force -ErrorAction SilentlyContinue
    }
    Remove-Contents "$env:LOCALAPPDATA\CrashDumps"
    Write-Host '     완료' -ForegroundColor Green
}

# ------------------------------------------------------------------ 6. 개발 도구 캐시
$devCaches = [ordered]@{
    'pip'   = "$env:LOCALAPPDATA\pip\Cache"
    'npm'   = "$env:APPDATA\npm-cache"
    '.npm'  = "$env:USERPROFILE\.npm"
    'nuget' = "$env:USERPROFILE\.nuget\packages"
    'gradle'= "$env:USERPROFILE\.gradle\caches"
    'maven' = "$env:USERPROFILE\.m2\repository"
    'yarn'  = "$env:LOCALAPPDATA\Yarn\Cache"
}
$devTotal = 0.0
$devLines = @()
foreach ($k in $devCaches.Keys) {
    $b = Get-PathBytes $devCaches[$k]
    if ($b -gt 0) { $devTotal += $b; $devLines += ('       {0,-7} {1,12}  {2}' -f $k, (Format-Size $b), $devCaches[$k]) }
}
$estTotal += $devTotal
Show-Step 6 '개발 도구 캐시 (pip / npm / nuget / gradle / maven / yarn)' $devTotal `
    '다시 받으면 복구됩니다. 오프라인 빌드가 필요하면 건너뛰세요.'
$devLines | ForEach-Object { Write-Host $_ -ForegroundColor DarkGray }
if ($devTotal -gt 0 -and (Confirm-Step '개발 도구 캐시 정리')) {
    foreach ($k in $devCaches.Keys) { Remove-Contents $devCaches[$k] }
    Write-Host '     완료' -ForegroundColor Green
}

# ------------------------------------------------------------------ 7. DISM 구성 요소 정리
Show-Step 7 'DISM 구성 요소 저장소 정리 (WinSxS)' 0 `
    ("10~20분 소요. 사전 크기 측정 불가. ResetBase={0}" -f $ResetBase)
if ($ResetBase) {
    Write-Host '     경고: /ResetBase 는 기존 업데이트 롤백을 불가능하게 만듭니다.' -ForegroundColor Red
}
if ($script:IsAdmin -and (Confirm-Step 'DISM 구성 요소 정리')) {
    if ($ResetBase) { & Dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase }
    else            { & Dism.exe /Online /Cleanup-Image /StartComponentCleanup }
    Write-Host '     완료' -ForegroundColor Green
} elseif (-not $script:IsAdmin) {
    Write-Host '     건너뜀 (관리자 권한 필요)' -ForegroundColor DarkYellow
}

# ------------------------------------------------------------------ 8. 시스템 복원 할당량
Show-Step 8 '시스템 복원(섀도 복사본) 할당량 5% 로 축소' 0 `
    '기존 복원 지점 일부가 삭제될 수 있습니다. 복원 기능 자체는 유지됩니다.'
if ($script:IsAdmin) {
    $cur = & cmd.exe /c "vssadmin list shadowstorage /for=$sysDrive" 2>&1
    $cur | Where-Object { $_ -match '용량|Space|Bytes' } | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }
    if (Confirm-Step '시스템 복원 할당량 축소') {
        & cmd.exe /c "vssadmin resize shadowstorage /for=$sysDrive /on=$sysDrive /maxsize=5%"
        Write-Host '     완료' -ForegroundColor Green
    }
} else {
    Write-Host '     건너뜀 (관리자 권한 필요)' -ForegroundColor DarkYellow
}

# ------------------------------------------------------------------ 9~11. 보고만 (삭제 안 함)
Write-Host ''
Write-Host ('-' * 72)
Write-Host '  아래는 판단이 필요해서 자동 삭제하지 않습니다. 목록만 보여드립니다.' -ForegroundColor Magenta
Write-Host ('-' * 72)

# 9. 다운로드 폴더 큰 파일
Write-Host ''
Write-Host '[9] 다운로드 폴더 큰 파일 Top 15' -ForegroundColor Cyan
$dl = Get-ChildItem -LiteralPath "$env:USERPROFILE\Downloads" -Recurse -Force -File -ErrorAction SilentlyContinue |
      Sort-Object Length -Descending | Select-Object -First 15
if ($dl) {
    $dlTotal = (Get-ChildItem -LiteralPath "$env:USERPROFILE\Downloads" -Recurse -Force -File -ErrorAction SilentlyContinue |
                Measure-Object Length -Sum).Sum
    Write-Host ("     폴더 전체: {0}" -f (Format-Size ([double]$dlTotal))) -ForegroundColor Yellow
    $dl | ForEach-Object { Write-Host ('       {0,12}  {1:yyyy-MM-dd}  {2}' -f (Format-Size $_.Length), $_.LastWriteTime, $_.Name) }
    Write-Host '     → 설치 파일(.exe/.msi/.zip)은 아카이브 드라이브로 옮기세요.' -ForegroundColor DarkGray
} else { Write-Host '     (없음)' -ForegroundColor DarkGray }

# 10. node_modules 등 프로젝트 잔재
Write-Host ''
Write-Host '[10] 프로젝트 잔재 (node_modules / .venv / target / build) Top 15' -ForegroundColor Cyan
$junkNames = @('node_modules','.venv','venv','target','build','dist','.next','__pycache__')
$junk = Get-ChildItem -LiteralPath $env:USERPROFILE -Directory -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $junkNames -contains $_.Name } | Select-Object -First 300
if ($junk) {
    $sized = foreach ($j in $junk) {
        [pscustomobject]@{ Bytes = (Get-PathBytes $j.FullName); Path = $j.FullName }
    }
    $jt = ($sized | Measure-Object Bytes -Sum).Sum
    Write-Host ("     합계: {0} ({1}개 폴더)" -f (Format-Size ([double]$jt)), $sized.Count) -ForegroundColor Yellow
    $sized | Sort-Object Bytes -Descending | Select-Object -First 15 |
        ForEach-Object { Write-Host ('       {0,12}  {1}' -f (Format-Size $_.Bytes), $_.Path) }
    Write-Host '     → 안 쓰는 프로젝트의 것만 삭제하세요. npm install / pip install 로 복구됩니다.' -ForegroundColor DarkGray
} else { Write-Host '     (없음)' -ForegroundColor DarkGray }

# 11. WSL / 가상디스크
Write-Host ''
Write-Host '[11] 가상디스크 (WSL ext4.vhdx 등)' -ForegroundColor Cyan
$vhd = Get-ChildItem -LiteralPath "$env:LOCALAPPDATA\Packages" -Filter '*.vhdx' -Recurse -Force -ErrorAction SilentlyContinue
if ($vhd) {
    $vhd | ForEach-Object { Write-Host ('       {0,12}  {1}' -f (Format-Size $_.Length), $_.FullName) }
    Write-Host '     → 안에서 파일을 지워도 이 크기는 안 줄어듭니다. 압축 필요:' -ForegroundColor DarkGray
    Write-Host '       wsl --shutdown   후   Optimize-VHD -Path <경로> -Mode Full   (Hyper-V 모듈 필요)' -ForegroundColor DarkGray
    Write-Host '       또는 diskpart:  select vdisk file="<경로>"  →  attach vdisk readonly  →  compact vdisk  →  detach vdisk' -ForegroundColor DarkGray
} else { Write-Host '     (없음)' -ForegroundColor DarkGray }

# ------------------------------------------------------------------ 마무리
$freeEnd = Get-FreeBytes $sysDrive
Write-Host ''
Write-Host ('=' * 72)
if ($Execute) {
    Write-Host ("  실행 전 여유 : {0}" -f (Format-Size $freeStart))
    Write-Host ("  실행 후 여유 : {0}" -f (Format-Size $freeEnd))
    Write-Host ("  확보량       : {0}" -f (Format-Size ($freeEnd - $freeStart))) -ForegroundColor Green
} else {
    Write-Host ("  시뮬레이션 결과 — 자동 정리 항목 확보 예상 합계: {0}" -f (Format-Size $estTotal)) -ForegroundColor Yellow
    Write-Host '  실제로 실행하려면 관리자 PowerShell 에서 -Execute 를 붙이세요:' -ForegroundColor Cyan
    Write-Host '    powershell -ExecutionPolicy Bypass -File .\Free-DiskSpace.ps1 -Execute' -ForegroundColor Cyan
}
Write-Host ('=' * 72)
Write-Host ''
Write-Host '재발 방지: 설정 → 시스템 → 저장 공간 → "저장 공간 센서" 켜기' -ForegroundColor DarkCyan
Write-Host '그리고 STORAGE-GUIDE.md 의 2-2(캐시 위치 이전) 를 적용하세요.' -ForegroundColor DarkCyan
