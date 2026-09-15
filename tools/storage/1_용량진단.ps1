# =====================================================================
#  C 드라이브 용량 진단
#  이 파일은 "보기만" 합니다. 아무것도 지우거나 바꾸지 않습니다.
#  결과는 바탕화면에 "용량진단결과.txt" 로 저장되고 자동으로 열립니다.
# =====================================================================

$ErrorActionPreference = 'SilentlyContinue'
$ProgressPreference    = 'SilentlyContinue'

$바탕화면 = [Environment]::GetFolderPath('Desktop')
if (-not $바탕화면) { $바탕화면 = $env:USERPROFILE }
$결과파일 = Join-Path $바탕화면 '용량진단결과.txt'
$줄 = New-Object System.Collections.Generic.List[string]

function 쓰기 { param([string]$글 = '') ; $줄.Add($글) ; Write-Host $글 }
function GB { param([double]$바이트) ; '{0,8:N1} GB' -f ($바이트 / 1GB) }
function 폴더크기 {
    param([string]$경로)
    if (-not (Test-Path -LiteralPath $경로)) { return -1 }
    [double]((Get-ChildItem -LiteralPath $경로 -Recurse -Force -File |
              Measure-Object -Property Length -Sum).Sum)
}

Write-Host ''
Write-Host '  진단을 시작합니다. 10~20분 걸립니다.'   -ForegroundColor Cyan
Write-Host '  이 창을 닫지 말고 그냥 두세요.'          -ForegroundColor Cyan
Write-Host '  다 끝나면 메모장이 저절로 열립니다.'      -ForegroundColor Cyan
Write-Host ''

쓰기 "용량 진단 결과"
쓰기 ("검사한 날짜: " + (Get-Date -Format 'yyyy-MM-dd HH:mm'))
쓰기 ''

# ---------------------------------------------------------------- 1. 드라이브
쓰기 '=============================================================='
쓰기 ' 1. 드라이브별 남은 공간'
쓰기 '=============================================================='
foreach ($d in (Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3')) {
    if (-not $d.Size) { continue }
    $비율 = $d.FreeSpace / $d.Size * 100
    $표시 = if ($비율 -lt 10) { '  <-- 위험' } elseif ($비율 -lt 20) { '  <-- 주의' } else { '' }
    쓰기 ('{0,-4} {1,-14} 전체 {2}   남음 {3}  ({4:N1}%){5}' -f `
        $d.DeviceID, $d.VolumeName, (GB $d.Size), (GB $d.FreeSpace), $비율, $표시)
}

# ---------------------------------------------------------------- 2. 영상 캐시
Write-Host '  [1/4] 영상 편집 프로그램 캐시를 확인하는 중...' -ForegroundColor DarkGray
쓰기 ''
쓰기 '=============================================================='
쓰기 ' 2. 영상 편집 프로그램이 만든 임시파일 (가장 유력한 범인)'
쓰기 '=============================================================='
$캐시목록 = [ordered]@{
    'DaVinci Resolve (내 문서)'   = "$env:USERPROFILE\Movies\DaVinci Resolve"
    'DaVinci Resolve (설정)'      = "$env:APPDATA\Blackmagic Design\DaVinci Resolve"
    'DaVinci Resolve (공용)'      = "C:\ProgramData\Blackmagic Design\DaVinci Resolve"
    'Premiere 미디어 캐시'        = "$env:APPDATA\Adobe\Common\Media Cache"
    'Premiere 미디어 캐시 파일'   = "$env:APPDATA\Adobe\Common\Media Cache Files"
    'Adobe 임시파일'              = "$env:LOCALAPPDATA\Temp\Adobe"
}
$캐시합계 = 0.0
foreach ($이름 in $캐시목록.Keys) {
    $크기 = 폴더크기 $캐시목록[$이름]
    if ($크기 -lt 0) { 쓰기 ('{0,-30} {1}' -f $이름, '     (없음)') }
    else { $캐시합계 += $크기 ; 쓰기 ('{0,-30} {1}   {2}' -f $이름, (GB $크기), $캐시목록[$이름]) }
}
쓰기 ('{0,-30} {1}' -f '>> 캐시 합계', (GB $캐시합계))

# ---------------------------------------------------------------- 3. 큰 폴더
Write-Host '  [2/4] C 드라이브 폴더 크기를 재는 중... (제일 오래 걸립니다)' -ForegroundColor DarkGray
쓰기 ''
쓰기 '=============================================================='
쓰기 ' 3. C 드라이브에서 자리를 많이 차지하는 폴더'
쓰기 '=============================================================='
Get-ChildItem 'C:\' -Directory -Force | ForEach-Object {
    [pscustomobject]@{ 바이트 = [double](폴더크기 $_.FullName); 경로 = $_.FullName }
} | Sort-Object 바이트 -Descending | Select-Object -First 15 | ForEach-Object {
    쓰기 ('{0}   {1}' -f (GB $_.바이트), $_.경로)
}

# ---------------------------------------------------------------- 4. 영상 폴더
Write-Host '  [3/4] 영상 작업 폴더를 찾는 중...' -ForegroundColor DarkGray
쓰기 ''
쓰기 '=============================================================='
쓰기 ' 4. 영상 작업으로 보이는 폴더'
쓰기 '=============================================================='
$찾은폴더 = Get-ChildItem 'C:\' -Directory -Recurse -Force |
  Where-Object { $_.Name -match '비디오|video|오토메이션|automation|유튜브|youtube|factory|팩토리|공장|렌더|render' } |
  Select-Object -First 25
if ($찾은폴더) {
    foreach ($f in $찾은폴더) { 쓰기 ('{0}   {1}' -f (GB (폴더크기 $f.FullName)), $f.FullName) }
} else { 쓰기 '   (이름으로는 못 찾았습니다. 위 3번 목록을 보세요.)' }

# ---------------------------------------------------------------- 5. 큰 파일
Write-Host '  [4/4] 큰 파일을 찾는 중...' -ForegroundColor DarkGray
쓰기 ''
쓰기 '=============================================================='
쓰기 ' 5. 1GB 넘는 큰 파일 (최대 30개)'
쓰기 '=============================================================='
Get-ChildItem 'C:\' -Recurse -Force -File |
  Where-Object { $_.Length -gt 1GB } |
  Sort-Object Length -Descending | Select-Object -First 30 | ForEach-Object {
    쓰기 ('{0}   {1:yyyy-MM-dd}   {2}' -f (GB $_.Length), $_.LastWriteTime, $_.FullName)
}

쓰기 ''
쓰기 '=============================================================='
쓰기 ' 끝났습니다. 이 파일 전체를 복사해서 Claude 에게 붙여넣으세요.'
쓰기 '=============================================================='

$줄 -join [Environment]::NewLine | Out-File -FilePath $결과파일 -Encoding utf8 -Width 500
Write-Host ''
Write-Host "  완료! 결과 파일: $결과파일" -ForegroundColor Green
Start-Process notepad.exe $결과파일
