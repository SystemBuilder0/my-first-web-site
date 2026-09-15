# =====================================================================
#  C 드라이브 용량 진단
#  이 파일은 "보기만" 합니다. 아무것도 지우거나 바꾸지 않습니다.
#  결과는 바탕화면에 "용량진단결과.txt" 로 저장되고 자동으로 열립니다.
# =====================================================================

$ErrorActionPreference = 'SilentlyContinue'
$ProgressPreference    = 'SilentlyContinue'

$desktop = [Environment]::GetFolderPath('Desktop')
if (-not $desktop) { $desktop = $env:USERPROFILE }
$outFile = Join-Path $desktop '용량진단결과.txt'
$lines   = New-Object System.Collections.Generic.List[string]

function Add-Line { param([string]$Text = '') ; $lines.Add($Text) ; Write-Host $Text }
function Fmt-GB   { param([double]$Bytes)    ; '{0,8:N1} GB' -f ($Bytes / 1GB) }
function Get-Size {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return -1 }
    [double]((Get-ChildItem -LiteralPath $Path -Recurse -Force -File |
              Measure-Object -Property Length -Sum).Sum)
}

Write-Host ''
Write-Host '  진단을 시작합니다. 10~20분 걸립니다.'   -ForegroundColor Cyan
Write-Host '  이 창을 닫지 말고 그냥 두세요.'         -ForegroundColor Cyan
Write-Host '  다 끝나면 메모장이 저절로 열립니다.'     -ForegroundColor Cyan
Write-Host ''

Add-Line '용량 진단 결과'
Add-Line ('검사한 날짜: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm'))
Add-Line ('사용자 계정: ' + $env:USERNAME + '   컴퓨터: ' + $env:COMPUTERNAME)
Add-Line ''

Add-Line '=============================================================='
Add-Line ' 1. 드라이브별 남은 공간'
Add-Line '=============================================================='
foreach ($d in (Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3')) {
    if (-not $d.Size) { continue }
    $pct  = $d.FreeSpace / $d.Size * 100
    $mark = if ($pct -lt 10) { '  <-- 위험' } elseif ($pct -lt 20) { '  <-- 주의' } else { '' }
    Add-Line ('{0,-4} {1,-14} 전체 {2}   남음 {3}  ({4:N1}%){5}' -f `
        $d.DeviceID, $d.VolumeName, (Fmt-GB $d.Size), (Fmt-GB $d.FreeSpace), $pct, $mark)
}

Write-Host '  [1/5] 영상 편집 프로그램 캐시를 확인하는 중...' -ForegroundColor DarkGray
Add-Line ''
Add-Line '=============================================================='
Add-Line ' 2. 지금 로그인한 계정의 영상 편집 캐시'
Add-Line '=============================================================='
$caches = [ordered]@{
    'Resolve (내 문서)'     = "$env:USERPROFILE\Movies\DaVinci Resolve"
    'Resolve (설정)'        = "$env:APPDATA\Blackmagic Design\DaVinci Resolve"
    'Resolve (공용)'        = "C:\ProgramData\Blackmagic Design\DaVinci Resolve"
    'Premiere 미디어캐시'   = "$env:APPDATA\Adobe\Common\Media Cache"
    'Premiere 캐시파일'     = "$env:APPDATA\Adobe\Common\Media Cache Files"
    'Adobe 임시파일'        = "$env:LOCALAPPDATA\Temp\Adobe"
}
$cacheTotal = 0.0
foreach ($k in $caches.Keys) {
    $sz = Get-Size $caches[$k]
    if ($sz -lt 0) { Add-Line ('{0,-22} {1}' -f $k, '     (없음)') }
    else { $cacheTotal += $sz ; Add-Line ('{0,-22} {1}   {2}' -f $k, (Fmt-GB $sz), $caches[$k]) }
}
Add-Line ('{0,-22} {1}' -f '>> 캐시 합계', (Fmt-GB $cacheTotal))

Write-Host '  [2/5] 계정별 사용량을 확인하는 중...' -ForegroundColor DarkGray
Add-Line ''
Add-Line '=============================================================='
Add-Line ' 3. 계정별 사용량 (이 PC는 계정이 여러 개입니다)'
Add-Line '=============================================================='
$profiles = Get-ChildItem 'C:\Users' -Directory -Force |
            Where-Object { $_.Name -notmatch '^(Public|Default|All Users|Default User)$' }
foreach ($u in $profiles) {
    Add-Line ('{0}   {1}' -f (Fmt-GB (Get-Size $u.FullName)), $u.FullName)
}

Add-Line ''
Add-Line '  -- 계정별 영상 캐시 / 다운로드 --'
foreach ($u in $profiles) {
    Add-Line ''
    Add-Line ('  [' + $u.Name + ' 계정]')
    $perUser = [ordered]@{
        'Resolve(내문서)'     = ($u.FullName + '\Movies\DaVinci Resolve')
        'Resolve(설정)'       = ($u.FullName + '\AppData\Roaming\Blackmagic Design\DaVinci Resolve')
        'Premiere 캐시'       = ($u.FullName + '\AppData\Roaming\Adobe\Common\Media Cache')
        'Premiere 캐시파일'   = ($u.FullName + '\AppData\Roaming\Adobe\Common\Media Cache Files')
        'Adobe 임시'          = ($u.FullName + '\AppData\Local\Temp\Adobe')
        '다운로드'            = ($u.FullName + '\Downloads')
        '바탕화면'            = ($u.FullName + '\Desktop')
        '문서'                = ($u.FullName + '\Documents')
        '비디오'              = ($u.FullName + '\Videos')
    }
    foreach ($k in $perUser.Keys) {
        $sz = Get-Size $perUser[$k]
        if ($sz -lt 0) { Add-Line ('    {0,-20} {1}' -f $k, '     (없음)') }
        else           { Add-Line ('    {0,-20} {1}' -f $k, (Fmt-GB $sz)) }
    }
}

Write-Host '  [3/5] C 드라이브 폴더 크기를 재는 중... (제일 오래 걸립니다)' -ForegroundColor DarkGray
Add-Line ''
Add-Line '=============================================================='
Add-Line ' 4. C 드라이브에서 자리를 많이 차지하는 폴더'
Add-Line '=============================================================='
Get-ChildItem 'C:\' -Directory -Force | ForEach-Object {
    [pscustomobject]@{ Bytes = [double](Get-Size $_.FullName); Path = $_.FullName }
} | Sort-Object Bytes -Descending | Select-Object -First 15 | ForEach-Object {
    Add-Line ('{0}   {1}' -f (Fmt-GB $_.Bytes), $_.Path)
}

Write-Host '  [4/5] 영상 작업 폴더를 찾는 중...' -ForegroundColor DarkGray
Add-Line ''
Add-Line '=============================================================='
Add-Line ' 5. 영상 작업으로 보이는 폴더'
Add-Line '=============================================================='
$pattern = '비디오|video|오토메이션|automation|유튜브|youtube|factory|팩토리|공장|렌더|render'
$found = Get-ChildItem 'C:\' -Directory -Recurse -Force |
         Where-Object { $_.Name -match $pattern } | Select-Object -First 25
if ($found) {
    foreach ($f in $found) { Add-Line ('{0}   {1}' -f (Fmt-GB (Get-Size $f.FullName)), $f.FullName) }
} else { Add-Line '   (이름으로는 못 찾았습니다. 위 4번 목록을 보세요.)' }

Write-Host '  [5/5] 큰 파일을 찾는 중...' -ForegroundColor DarkGray
Add-Line ''
Add-Line '=============================================================='
Add-Line ' 6. 1GB 넘는 큰 파일 (최대 30개)'
Add-Line '=============================================================='
Get-ChildItem 'C:\' -Recurse -Force -File |
  Where-Object { $_.Length -gt 1GB } |
  Sort-Object Length -Descending | Select-Object -First 30 | ForEach-Object {
    Add-Line ('{0}   {1:yyyy-MM-dd}   {2}' -f (Fmt-GB $_.Length), $_.LastWriteTime, $_.FullName)
}

Add-Line ''
Add-Line '=============================================================='
Add-Line ' 끝났습니다. 이 파일 전체를 복사해서 Claude 에게 붙여넣으세요.'
Add-Line '=============================================================='

$lines -join [Environment]::NewLine | Out-File -FilePath $outFile -Encoding utf8 -Width 500
Write-Host ''
Write-Host ('  완료! 결과 파일: ' + $outFile) -ForegroundColor Green
Start-Process notepad.exe $outFile
