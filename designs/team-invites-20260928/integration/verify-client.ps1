[CmdletBinding()]
param([Parameter(Mandatory=$true)][ValidateSet('EditMode','PlayMode','Capture','Build')][string]$Mode)
$ErrorActionPreference = 'Stop'
$clientRoot = 'E:\work\mmorpg-client'
$editorExe = 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe'
$qaRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../qa'))
New-Item -ItemType Directory -Path $qaRoot -Force | Out-Null
$runName = $Mode.ToLowerInvariant() + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
$logPath = Join-Path $qaRoot ($runName + '.log')
$resultPath = Join-Path $qaRoot ($runName + '.xml')
$arguments = @('-batchmode','-force-d3d11','-projectPath',('"'+$clientRoot+'"'),'-logFile',('"'+$logPath+'"'))
switch ($Mode) {
    'EditMode' { $arguments += @('-runTests','-testPlatform','EditMode','-testFilter','MmorpgClient.Tests.EditMode.Tianyong.Team;MmorpgClient.Tests.EditMode.Social','-testResults',('"'+$resultPath+'"')) }
    'PlayMode' { $arguments += @('-runTests','-testPlatform','PlayMode','-testFilter','MmorpgClient.Tests.PlayMode.Team','-testResults',('"'+$resultPath+'"')) }
    'Capture' { $arguments += @('-quit','-executeMethod','TeamInvitationVerification.CaptureAll') }
    'Build' { $arguments += @('-quit','-executeMethod','MmorpgClient.Editor.CrossZoneVerifyBuild.Build','-crossZoneOut','E:/work/tmp/wuxing-team-invites-player-20260928') }
}
$process = Start-Process -FilePath $editorExe -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output ('Unity ' + $Mode + ' pid=' + $process.Id + ' log=' + $logPath)
$timer = [Diagnostics.Stopwatch]::StartNew()
while (-not $process.WaitForExit(30000)) {
    Write-Output ('Unity ' + $Mode + ' 已运行 ' + [int]$timer.Elapsed.TotalSeconds + ' 秒')
    if ($timer.Elapsed.TotalMinutes -ge 30) { throw ('Unity 检查超过 30 分钟，请检查进程 ' + $process.Id) }
}
$process.Refresh()
$report = [ordered]@{ mode=$Mode; exitCode=$process.ExitCode; log=$logPath; elapsedSeconds=[int]$timer.Elapsed.TotalSeconds; completedAt=[DateTime]::UtcNow.ToString('o') }
if ($Mode -in @('EditMode','PlayMode') -and (Test-Path -LiteralPath $resultPath)) {
    [xml]$xml = Get-Content -LiteralPath $resultPath -Raw
    $run = $xml.'test-run'
    $report.tests = [ordered]@{ result=$run.result; total=$run.total; passed=$run.passed; failed=$run.failed; skipped=$run.skipped; path=$resultPath }
}
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $qaRoot ($runName + '.json')) -Encoding utf8
$report | ConvertTo-Json -Depth 5
if ($process.ExitCode -ne 0) { exit 1 }
if ($Mode -in @('EditMode','PlayMode') -and (-not $report.tests -or $report.tests.result -ne 'Passed')) { exit 1 }
