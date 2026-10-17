param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9-]+$')][string]$Label, [switch]$BuildOnly)
$ErrorActionPreference = 'Stop'
$package = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../integration'))
$client = 'E:/work/mmorpg-client'
$relative = 'Assets/Scripts/App/DevTeamInvitationDriver.cs'
Copy-Item -LiteralPath (Join-Path "$package/client" $relative) -Destination (Join-Path $client $relative) -Force
$buildLog = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../qa/build-$Label.log"))
$output = 'E:/work/tmp/wuxing-team-invites-player-20260929'
$process = Start-Process -FilePath 'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe' -ArgumentList @(
    '-batchmode','-force-d3d11','-quit','-projectPath',$client,
    '-executeMethod','MmorpgClient.Editor.CrossZoneVerifyBuild.Build','-crossZoneOut',$output,'-logFile',$buildLog
) -WindowStyle Hidden -PassThru
$timer = [Diagnostics.Stopwatch]::StartNew()
Write-Output "Unity build PID=$($process.Id), log=$buildLog"
while (-not $process.WaitForExit(30000)) {
    Write-Output "Unity build continuing: $([int]$timer.Elapsed.TotalSeconds)s"
    if ($timer.Elapsed.TotalMinutes -ge 20) { throw 'Unity 构建超过 20 分钟，请检查本次进程。' }
}
$process.Refresh()
if ($process.ExitCode -ne 0) { throw "Unity 构建失败：$buildLog" }
Select-String -LiteralPath $buildLog -Pattern '\[CrossZoneVerifyBuild\] result=' | ForEach-Object Line
if (-not $BuildOnly) { & (Join-Path $PSScriptRoot 'run-unity-pair.ps1') -PlayerPath "$output/mmorpg.exe" }
