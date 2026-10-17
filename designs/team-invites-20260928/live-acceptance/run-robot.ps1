param([string]$ServerRoot = 'E:/work/xuanming-server-mmo', [ValidateSet('acceptance','unity-cleanup')][string]$Mode = 'acceptance', [ValidateSet('fcf7df80745d4021','d342a978cc8f456b')][string]$CleanupRun = 'fcf7df80745d4021')
$ErrorActionPreference = 'Stop'
$oldPassword = $env:LOGIN_DEV_PASSWORD_SHARED_SECRET
$oldCleanupRun = $env:TEAM_INVITES_CLEANUP_RUN
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$binary = if ($Mode -eq 'unity-cleanup') { 'team-invites-cleanup.exe' } else { 'team-invites-robot.exe' }
$log = Join-Path $PSScriptRoot $(if ($Mode -eq 'unity-cleanup') { "cleanup-$CleanupRun-$stamp.log" } else { "result-$stamp.log" })
try {
    if ($Mode -eq 'unity-cleanup') { $env:TEAM_INVITES_CLEANUP_RUN = $CleanupRun }
    if (-not $env:LOGIN_DEV_PASSWORD_SHARED_SECRET) {
        # 与仓库 start_game.ps1 完全相同：只读已有本地配置并继承给进程，不回显。
        $localConfig = Get-Content -LiteralPath (Join-Path $ServerRoot 'robot/etc/robot.yaml') -Raw
        $passwordMatch = [regex]::Match($localConfig, '(?m)^password:\s*"([^"\r\n]+)"')
        if (-not $passwordMatch.Success) { throw '本地开发登录密码未配置。' }
        $env:LOGIN_DEV_PASSWORD_SHARED_SECRET = $passwordMatch.Groups[1].Value
        $localConfig = $null
        $passwordMatch = $null
    }
    Push-Location $PSScriptRoot
    try {
        & (Join-Path $PSScriptRoot $binary) -c (Join-Path $PSScriptRoot 'robot.yaml') 2>&1 | Tee-Object -FilePath $log
        $result = $LASTEXITCODE
    } finally { Pop-Location }
    if ($result -ne 0) { throw "真实组队邀请验收失败，退出码 $result，日志 $log" }
    Write-Output "真实组队邀请验收通过，日志 $log"
} finally {
    $env:LOGIN_DEV_PASSWORD_SHARED_SECRET = $oldPassword
    $env:TEAM_INVITES_CLEANUP_RUN = $oldCleanupRun
}
