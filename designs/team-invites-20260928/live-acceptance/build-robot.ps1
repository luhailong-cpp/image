param([string]$ServerRoot = 'E:/work/xuanming-server-mmo', [ValidateSet('acceptance','unity-cleanup')][string]$Mode = 'acceptance')
$ErrorActionPreference = 'Stop'
$robotRoot = Join-Path $ServerRoot 'robot'
$stage = Join-Path $PSScriptRoot $(if ($Mode -eq 'unity-cleanup') { 'cleanup-overlay' } else { 'overlay' })
$entrypoint = if ($Mode -eq 'unity-cleanup') { 'RunTeamInvitesCleanup' } else { 'RunTeamInvitesAcceptance' }
$binary = if ($Mode -eq 'unity-cleanup') { 'team-invites-cleanup.exe' } else { 'team-invites-robot.exe' }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
$utf8 = [Text.UTF8Encoding]::new($false)
$main = [IO.File]::ReadAllText((Join-Path $robotRoot 'main.go'))
if (-not $main.Contains('RunTeamSmoke(cfg)')) { throw 'main.go 的 team-smoke 入口发生变化。' }
$main = $main.Replace('RunTeamSmoke(cfg)', ('if err := ' + $entrypoint + '(cfg); err != nil { zap.L().Error("TEAM_INVITES_ACCEPTANCE_FAIL", zap.Error(err)); _ = zap.L().Sync(); os.Exit(1) }'))
[IO.File]::WriteAllText((Join-Path $stage 'main.go'), $main, $utf8)
$team = [IO.File]::ReadAllText((Join-Path $robotRoot 'team_smoke_scenario.go'))
$match = 'func teamSmokeIsTeamRequest(messageId uint32) bool {'
if (-not $team.Contains($match)) { throw '组队收包函数发生变化。' }
$team = $team.Replace($match, $match + "`n if messageId == game.SceneAttributeClientPlayerGetAttributePanelMessageId { return true }`n if friendSmokeIsFriendMessage(messageId) && messageId != game.ClientPlayerFriendNotifyFriendEventMessageId { return true }")
# Gate 的按秒窗口用严格 > 驱逐旧记录，119 的 1 次/秒必须跨过两个整秒。
$team = $team.Replace('teamSmokeRequestSpacing = 400 * time.Millisecond', 'teamSmokeRequestSpacing = 2100 * time.Millisecond')
if ($Mode -eq 'unity-cleanup') {
    $connect = 'gc, err := connectAndVerify(host, port, account, tokenPayload, tokenSig)'
    if (-not $team.Contains($connect)) { throw 'Gate 连接函数发生变化。' }
    $team = $team.Replace($connect, 'if host != "127.0.0.1" { return nil, fmt.Errorf("cleanup requires local IPv4 gate") }' + "`n`t" + $connect)
}
[IO.File]::WriteAllText((Join-Path $stage 'team_smoke_scenario.go'), $team, $utf8)
$login = [IO.File]::ReadAllText((Join-Path $robotRoot 'login.go'))
$match = '// 2. Create player if needed'
if (-not $login.Contains($match)) { throw '登录函数发生变化。' }
$loginGuard = if ($Mode -eq 'unity-cleanup') {
    'if len(lr.Players) != 1 { return fmt.Errorf("cleanup requires one existing character; creation is prohibited") }; if err := cleanupUnityCheckIdentity(gc.Account, lr.Players[0].GetPlayer().GetPlayerId()); err != nil { return err }'
} else {
    'if len(lr.Players) != 0 { return fmt.Errorf("isolated acceptance requires a brand-new account; refusing existing characters") }'
}
$login = $login.Replace($match, $loginGuard + "`n`t" + $match)
[IO.File]::WriteAllText((Join-Path $stage 'login.go'), $login, $utf8)
$replace = @{}
foreach ($file in @('main.go','team_smoke_scenario.go','login.go')) { $replace[(Join-Path $robotRoot $file)] = Join-Path $stage $file }
$replace[(Join-Path $robotRoot 'team_invites_acceptance.go')] = Join-Path $PSScriptRoot 'team_invites_acceptance.go'
if ($Mode -eq 'unity-cleanup') { $replace[(Join-Path $robotRoot 'team_invites_cleanup.go')] = Join-Path $PSScriptRoot 'team_invites_cleanup.go' }
$overlayPath = Join-Path $PSScriptRoot $(if ($Mode -eq 'unity-cleanup') { 'cleanup-overlay.json' } else { 'overlay.json' })
[IO.File]::WriteAllText($overlayPath, (@{Replace=$replace} | ConvertTo-Json -Depth 4), $utf8)
$toolRoot = 'C:/Users/luyua/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.26.5.windows-amd64/bin'
$env:GOCACHE = 'E:/work/image/.cache/go-build'
$env:GOTMPDIR = 'E:/work/image/.cache/go-tmp'
$env:GOTOOLCHAIN = 'local'
$env:GOWORK = 'off'
& (Join-Path $toolRoot 'gofmt.exe') -w (Join-Path $PSScriptRoot 'team_invites_acceptance.go') (Join-Path $stage 'main.go') (Join-Path $stage 'team_smoke_scenario.go') (Join-Path $stage 'login.go')
if ($LASTEXITCODE -ne 0) { throw 'gofmt 失败。' }
Push-Location $robotRoot
try {
    & (Join-Path $toolRoot 'go.exe') build -buildvcs=false -mod=readonly "-overlay=$overlayPath" -o (Join-Path $PSScriptRoot $binary) .
    if ($LASTEXITCODE -ne 0) { throw '独立机器人构建失败。' }
} finally { Pop-Location }
Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $PSScriptRoot $binary) | Select-Object Path,Hash
