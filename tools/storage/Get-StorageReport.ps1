<#
.SYNOPSIS
    Windows 저장공간 진단 리포트 생성기 (읽기 전용 - 아무것도 삭제하지 않음)

.DESCRIPTION
    드라이브별 여유공간, 용량 큰 폴더 / 파일, 알려진 "공간 먹는 항목"을 한 번에 조사해
    텍스트 리포트로 저장합니다. 삭제 / 이동 / 설정변경은 일절 하지 않습니다.

.PARAMETER Drives
    조사할 드라이브. 생략 시 로컬 고정 디스크 전부. 예: -Drives C:,G:

.PARAMETER Quick
    전체 재귀 스캔을 생략하고 드라이브 요약 + 사용자 프로필 + 알려진 항목만 조사.
    (전체 스캔은 디스크 크기에 따라 5~40분 걸릴 수 있음)

.PARAMETER MinFileSizeMB
    "큰 파일" 목록에 넣을 최소 크기. 기본 200MB.

.PARAMETER OutputPath
    리포트 저장 경로. 기본 바탕화면의 storage-report_<날짜시각>.txt

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\Get-StorageReport.ps1 -Quick
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\Get-StorageReport.ps1 -Drives C:
#>
#Requires -Version 5.1
[CmdletBinding()]
param(
    [string[]]$Drives,
    [switch]$Quick,
    [int]$TopFolders    = 25,
    [int]$TopFiles      = 30,
    [int]$MinFileSizeMB = 200,
    [string]$OutputPath
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

# ---------------------------------------------------------------- 출력 헬퍼
$script:Lines = New-Object System.Collections.Generic.List[string]
function Write-Line {
    param([string]$Text = '')
    $script:Lines.Add($Text)
    Write-Host $Text
}
function Write-Head {
    param([string]$Text)
    Write-Line ''
    Write-Line ('=' * 78)
    Write-Line "  $Text"
    Write-Line ('=' * 78)
}
function Format-Size {
    param([double]$Bytes)
    if     ($Bytes -ge 1TB) { '{0,9:N2} TB' -f ($Bytes / 1TB) }
    elseif ($Bytes -ge 1GB) { '{0,9:N2} GB' -f ($Bytes / 1GB) }
    elseif ($Bytes -ge 1MB) { '{0,9:N1} MB' -f ($Bytes / 1MB) }
    else                    { '{0,9:N0} KB' -f ($Bytes / 1KB) }
}

# ---------------------------------------------------------------- 대상 드라이브
if (-not $Drives -or $Drives.Count -eq 0) {
    $Drives = @(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty DeviceID)
}
$Drives = $Drives | ForEach-Object { ($_.TrimEnd('\')).ToUpper() } |
          Where-Object { $_ -match '^[A-Z]:$' } | Select-Object -Unique

if (-not $OutputPath) {
    $stamp      = Get-Date -Format 'yyyyMMdd_HHmmss'
    $desktop    = [Environment]::GetFolderPath('Desktop')
    if (-not $desktop) { $desktop = $env:USERPROFILE }
    $OutputPath = Join-Path $desktop "storage-report_$stamp.txt"
}

Write-Line "저장공간 진단 리포트"
Write-Line "생성 시각 : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Line "컴퓨터    : $env:COMPUTERNAME / 사용자: $env:USERNAME"
Write-Line "모드      : $(if ($Quick) { 'Quick (전체 재귀 스캔 생략)' } else { 'Full (전체 재귀 스캔)' })"
Write-Line "대상      : $($Drives -join ', ')"

# ---------------------------------------------------------------- 1. 드라이브 요약
Write-Head '1. 드라이브별 용량'
Write-Line ('{0,-6} {1,-14} {2,12} {3,12} {4,12} {5,7}' -f '드라이브','볼륨','전체','사용','여유','여유%')
Write-Line ('-' * 78)
foreach ($d in $Drives) {
    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$d'" -ErrorAction SilentlyContinue
    if (-not $disk) { Write-Line ("{0,-6} (정보 없음)" -f $d); continue }
    $total = [double]$disk.Size
    $free  = [double]$disk.FreeSpace
    $used  = $total - $free
    $pct   = if ($total -gt 0) { $free / $total * 100 } else { 0 }
    $flag  = if ($pct -lt 10) { '  <<< 위험' } elseif ($pct -lt 20) { '  << 주의' } else { '' }
    Write-Line ('{0,-6} {1,-14} {2} {3} {4} {5,6:N1}%{6}' -f `
        $d, $disk.VolumeName, (Format-Size $total), (Format-Size $used), (Format-Size $free), $pct, $flag)
}

# ---------------------------------------------------------------- 2. 알려진 공간 먹는 항목
Write-Head '2. 알려진 "공간 먹는 항목" 점검'

function Get-PathSize {
    param([string]$Path)
    if (-not $Path) { return $null }
    if (-not (Test-Path -LiteralPath $Path -ErrorAction SilentlyContinue)) { return $null }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $item) { return $null }
    if ($item.PSIsContainer) {
        $m = Get-ChildItem -LiteralPath $Path -Recurse -Force -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum
        return [pscustomobject]@{ Path = $Path; Bytes = [double]($m.Sum); Count = [int]$m.Count }
    }
    return [pscustomobject]@{ Path = $Path; Bytes = [double]$item.Length; Count = 1 }
}

$targets = [ordered]@{
    '사용자 임시파일 (%TEMP%)'      = $env:TEMP
    'Windows 임시파일'              = "$env:SystemRoot\Temp"
    'Windows 업데이트 캐시'         = "$env:SystemRoot\SoftwareDistribution\Download"
    'Windows.old (이전 OS)'         = "$env:SystemDrive\Windows.old"
    '최대 절전 모드 파일'           = "$env:SystemDrive\hiberfil.sys"
    '페이지 파일'                   = "$env:SystemDrive\pagefile.sys"
    '휴지통'                        = "$env:SystemDrive\`$Recycle.Bin"
    '다운로드 폴더'                 = "$env:USERPROFILE\Downloads"
    '설치 패키지 캐시'              = "$env:LOCALAPPDATA\Package Cache"
    'pip 캐시'                      = "$env:LOCALAPPDATA\pip\Cache"
    'npm 캐시'                      = "$env:APPDATA\npm-cache"
    'npm 홈 캐시 (.npm)'            = "$env:USERPROFILE\.npm"
    'Gradle 캐시'                   = "$env:USERPROFILE\.gradle"
    'Maven 캐시'                    = "$env:USERPROFILE\.m2"
    'NuGet 캐시'                    = "$env:USERPROFILE\.nuget"
    '홈 .cache'                     = "$env:USERPROFILE\.cache"
    'Docker Desktop 데이터'         = "$env:LOCALAPPDATA\Docker"
    'Chrome 캐시'                   = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"
    'Edge 캐시'                     = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache"
    'OneDrive 폴더'                 = "$env:USERPROFILE\OneDrive"
    'Claude Code 프로젝트 이력'     = "$env:USERPROFILE\.claude"
}

Write-Line ('{0,-32} {1,12}  {2}' -f '항목','크기','경로')
Write-Line ('-' * 78)
$hogTotal = 0.0
foreach ($k in $targets.Keys) {
    $r = Get-PathSize $targets[$k]
    if ($null -eq $r) {
        Write-Line ('{0,-32} {1,12}  {2}' -f $k, '(없음)', $targets[$k])
    } else {
        $hogTotal += $r.Bytes
        Write-Line ('{0,-32} {1}  {2}' -f $k, (Format-Size $r.Bytes), $r.Path)
    }
}
Write-Line ('-' * 78)
Write-Line ('{0,-32} {1}' -f '위 항목 합계', (Format-Size $hogTotal))

# WSL 가상디스크 (있을 때만)
$wsl = Get-ChildItem -Path "$env:LOCALAPPDATA\Packages" -Filter 'ext4.vhdx' -Recurse -Force -ErrorAction SilentlyContinue
if ($wsl) {
    Write-Line ''
    Write-Line 'WSL 가상디스크 (ext4.vhdx) — 한 번 커지면 자동으로 줄지 않음:'
    foreach ($v in $wsl) { Write-Line ('  {0}  {1}' -f (Format-Size $v.Length), $v.FullName) }
}

# 섀도 복사본 / 시스템 복원 (관리자 권한 필요)
Write-Line ''
Write-Line '시스템 복원 / 섀도 복사본 할당량 (관리자 권한 필요):'
$vss = & cmd.exe /c 'vssadmin list shadowstorage' 2>&1
if ($LASTEXITCODE -eq 0 -and $vss) {
    $vss | Where-Object { $_ -match '\S' } | Select-Object -Skip 3 | ForEach-Object { Write-Line "  $_" }
} else {
    Write-Line '  (조회 실패 — 관리자 권한으로 다시 실행하면 나옵니다)'
}

# 개발 프로젝트 잔재
Write-Line ''
Write-Line '개발 프로젝트 잔재 (node_modules / venv / target / build) — 사용자 폴더 기준:'
$junkNames = @('node_modules','.venv','venv','__pycache__','target','.next','dist','build')
$junk = Get-ChildItem -LiteralPath $env:USERPROFILE -Directory -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $junkNames -contains $_.Name } |
        Select-Object -First 400
if ($junk) {
    $junkSized = foreach ($j in $junk) {
        $m = Get-ChildItem -LiteralPath $j.FullName -Recurse -Force -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum
        [pscustomobject]@{ Bytes = [double]($m.Sum); Path = $j.FullName }
    }
    $junkTotal = ($junkSized | Measure-Object -Property Bytes -Sum).Sum
    $junkSized | Sort-Object Bytes -Descending | Select-Object -First 20 |
        ForEach-Object { Write-Line ('  {0}  {1}' -f (Format-Size $_.Bytes), $_.Path) }
    Write-Line ('  {0,-11}  합계 {1}개 폴더' -f (Format-Size $junkTotal), $junkSized.Count)
} else {
    Write-Line '  (없음)'
}

# ---------------------------------------------------------------- 3. 전체 스캔
if (-not $Quick) {
    $minBytes = [double]$MinFileSizeMB * 1MB

    foreach ($d in $Drives) {
        $root = "$d\"
        Write-Head "3. 전체 스캔 : $root  (시간이 걸립니다)"
        Write-Host "  스캔 중... ($root)" -ForegroundColor DarkGray

        $lvl1     = @{}
        $lvl2     = @{}
        $bigFiles = New-Object System.Collections.Generic.List[object]
        $sw       = [System.Diagnostics.Stopwatch]::StartNew()
        $seen     = 0

        Get-ChildItem -LiteralPath $root -Recurse -Force -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            $seen++
            $len = [double]$_.Length
            if ($len -ge $minBytes) { $bigFiles.Add($_) }

            $dir = $_.DirectoryName
            if ($dir -and $dir.Length -gt $root.Length) {
                $parts = $dir.Substring($root.Length).Split('\')
                $k1 = $root + $parts[0]
                if ($lvl1.ContainsKey($k1)) { $lvl1[$k1] += $len } else { $lvl1[$k1] = $len }
                if ($parts.Count -ge 2) {
                    $k2 = $root + $parts[0] + '\' + $parts[1]
                    if ($lvl2.ContainsKey($k2)) { $lvl2[$k2] += $len } else { $lvl2[$k2] = $len }
                }
            }
        }
        $sw.Stop()
        Write-Line ("스캔 완료: 파일 {0:N0}개 / {1:N1}분" -f $seen, $sw.Elapsed.TotalMinutes)

        Write-Line ''
        Write-Line "[$root 1단계 폴더]"
        $lvl1.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First $TopFolders |
            ForEach-Object { Write-Line ('  {0}  {1}' -f (Format-Size $_.Value), $_.Key) }

        Write-Line ''
        Write-Line "[$root 2단계 폴더 Top $TopFolders]"
        $lvl2.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First $TopFolders |
            ForEach-Object { Write-Line ('  {0}  {1}' -f (Format-Size $_.Value), $_.Key) }

        Write-Line ''
        Write-Line "[$root ${MinFileSizeMB}MB 이상 큰 파일 Top $TopFiles] (총 $($bigFiles.Count)개)"
        $bigFiles | Sort-Object Length -Descending | Select-Object -First $TopFiles | ForEach-Object {
            Write-Line ('  {0}  {1:yyyy-MM-dd}  {2}' -f (Format-Size $_.Length), $_.LastWriteTime, $_.FullName)
        }

        Write-Line ''
        Write-Line "[$root 확장자별 용량 Top 15]"
        $bigFiles | Group-Object Extension |
            Select-Object Name, @{n='Bytes';e={($_.Group | Measure-Object Length -Sum).Sum}}, Count |
            Sort-Object Bytes -Descending | Select-Object -First 15 |
            ForEach-Object {
                $ext = if ($_.Name) { $_.Name } else { '(없음)' }
                Write-Line ('  {0}  {1,-10} {2,5}개' -f (Format-Size $_.Bytes), $ext, $_.Count)
            }
    }
} else {
    Write-Head '3. 전체 스캔 : 건너뜀 (-Quick)'
    Write-Line '전체 스캔을 하려면 -Quick 없이 다시 실행하세요.'
}

# ---------------------------------------------------------------- 마무리
Write-Head '주의사항'
Write-Line '- 이 스크립트는 읽기 전용입니다. 아무 파일도 삭제/이동하지 않았습니다.'
Write-Line '- OneDrive "온라인 전용" 파일은 크기가 표시돼도 실제 디스크는 거의 안 씁니다.'
Write-Line '- 권한 없는 폴더는 조용히 건너뜁니다 (관리자 권한으로 실행하면 더 정확).'
Write-Line '- hiberfil.sys / pagefile.sys 는 OS가 관리하는 파일입니다. 직접 지우지 마세요.'

try {
    $dir = Split-Path -Parent $OutputPath
    if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $script:Lines -join [Environment]::NewLine | Out-File -FilePath $OutputPath -Encoding utf8
    Write-Host ''
    Write-Host "리포트 저장됨: $OutputPath" -ForegroundColor Green
} catch {
    Write-Host "리포트 저장 실패: $($_.Exception.Message)" -ForegroundColor Red
}
