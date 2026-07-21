# CLAUDE.md를 저장할 때마다 자동으로 git add/commit/push 하는 감시 스크립트 (Windows PowerShell)
#
# 사용법:
#   1. 이 리포지토리를 로컬 PC에 git clone 해둔다.
#   2. PowerShell에서 리포지토리 루트로 이동 후 실행:
#        powershell -ExecutionPolicy Bypass -File .\scripts\watch-and-sync-claude-md.ps1
#   3. 실행 중인 상태로 CLAUDE.md를 메모장 등으로 수정하고 저장하면,
#      몇 초 뒤 자동으로 commit + push 됩니다.
#   4. 종료하려면 Ctrl+C.

$ErrorActionPreference = "Stop"

$repoRoot = git rev-parse --show-toplevel
Set-Location $repoRoot

$targetFile = "CLAUDE.md"
$debounceSeconds = 3
$lastChange = Get-Date 0

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $repoRoot
$watcher.Filter = $targetFile
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite
$watcher.EnableRaisingEvents = $true

Write-Host "CLAUDE.md 변경 감시를 시작합니다. 저장하면 자동으로 push됩니다. (Ctrl+C로 종료)"

Register-ObjectEvent $watcher Changed -Action {
    $script:lastChange = Get-Date
} | Out-Null

while ($true) {
    Start-Sleep -Seconds 1
    if ((Get-Date 0) -ne $lastChange -and ((Get-Date) - $lastChange).TotalSeconds -ge $debounceSeconds) {
        $lastChange = Get-Date 0

        $status = git status --porcelain -- $targetFile
        if ($status) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] CLAUDE.md 변경 감지 -> commit & push"
            git add $targetFile
            git commit -m "Update CLAUDE.md ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
            git push
            Write-Host "  -> push 완료"
        }
    }
}
