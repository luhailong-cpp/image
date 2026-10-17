[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Executable,
    [Parameter(Mandatory=$true)][string]$ExpectedSha256,
    [int]$ExpectedProcessId = 46076
)
$ErrorActionPreference = 'Stop'
$serverRoot = 'E:\work\xuanming-server-mmo'
$target = Join-Path $serverRoot 'bin/scene.exe'
$oldHash = 'F39344F361DD975497AA0340D1C6E6DCF78204B293A950FE54E61092046073F1'
$nextHash = (Get-FileHash -LiteralPath $Executable -Algorithm SHA256).Hash
if ($nextHash -ne $ExpectedSha256) { throw '新场景服与构建证据不一致。' }
if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $oldHash) { throw '运行场景服已变化，停止替换。' }
$pidsPath = Join-Path $serverRoot 'run/pids/cpp_nodes.pid.json'
$pids = Get-Content -LiteralPath $pidsPath -Raw | ConvertFrom-Json -AsHashtable
$scenes = @($pids.Keys | Where-Object { $_ -match '(^|_)scene(_|$)' })
if ($scenes.Count -ne 1 -or $scenes[0] -ne 'z1_scene' -or $pids['z1_scene'] -ne $ExpectedProcessId) { throw '场景服进程清单与本轮启动不一致。' }
$process = Get-Process -Id $ExpectedProcessId -ErrorAction Stop
if ($process.Path -ne $target -or $process.StartTime -lt [datetime]'2026-10-01T09:39:00') { throw '场景服不是本轮启动的进程。' }
if (@(Get-NetTCPConnection -LocalPort 10000 -State Established -ErrorAction SilentlyContinue).Count -gt 0) { throw 'Gate 仍有玩家连接，暂不重启场景服。' }
$backupRoot = Join-Path $serverRoot ('run/backups/team-invites-scene-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backupRoot | Out-Null
Copy-Item -LiteralPath $target -Destination (Join-Path $backupRoot 'scene.exe')
$previousEnvironment = @{}
foreach ($key in @('PATH','KAFKA_COMMAND_TOPIC_PARTITIONS','KAFKA_COMMAND_TOPIC_GENERATION','RPC_PORT','SCENE_RUN_MODE')) {
    $previousEnvironment[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
}
$devTools = Join-Path $serverRoot 'tools/scripts/dev_tools.ps1'
$contractPath = Join-Path $serverRoot 'run/pids/kafka_command_contract.json'
function Start-VerifiedScene {
    & pwsh -NoProfile -File $devTools -Command cpp-node-start -CppNodes scene -GateCount 0 -SceneCount 1 -BattleCount 0 -Zone 1 -NodeIp loopback | Out-Host
    if ($LASTEXITCODE -ne 0) { throw '场景服启动器返回失败。' }
    $nodePids = Get-Content -LiteralPath $pidsPath -Raw | ConvertFrom-Json -AsHashtable
    $node = Get-Process -Id $nodePids['z1_scene'] -ErrorAction Stop
    if ($node.Path -ne $target) { throw '新场景服路径不一致。' }
    if (-not (Get-NetTCPConnection -State Listen -OwningProcess $node.Id -ErrorAction SilentlyContinue)) { throw '新场景服没有监听端口。' }
    $contracts = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json -AsHashtable
    $contracts['scene'] = @{ProcessId=$node.Id;StartTimeUtcTicks=[string]$node.StartTime.ToUniversalTime().Ticks;Generation=2;Partitions=256}
    $contracts | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $contractPath -Encoding utf8
    return $node.Id
}
try {
    $env:PATH = (Join-Path $serverRoot 'third_party/grpc/install_vs2026_dbg/bin') + ';' + $env:PATH
    $env:KAFKA_COMMAND_TOPIC_PARTITIONS = '256'
    $env:KAFKA_COMMAND_TOPIC_GENERATION = '2'
    $env:RPC_PORT = $null
    $env:SCENE_RUN_MODE = 'dev'
    & pwsh -NoProfile -File $devTools -Command cpp-node-stop -CppNodes scene
    if ($LASTEXITCODE -ne 0) { throw '原场景服停止失败。' }
    $process.WaitForExit(10000) | Out-Null
    if (-not $process.HasExited) { throw '原场景服未退出。' }
    Copy-Item -LiteralPath $Executable -Destination $target -Force
    $newProcessId = Start-VerifiedScene
    $result = [ordered]@{
        deployedAt=[DateTime]::UtcNow.ToString('o'); processId=$newProcessId;
        executable=$target; sha256=$nextHash; backup=(Join-Path $backupRoot 'scene.exe');
        sourceBaseline='1ad634443d4d5028075d6b7e839b434018bfb0e8';
        sourceValidation='993 project source checksums match the previously deployed PDB; only AOI notification fix applied';
        patch='Notify existing stationary observers on reverse AOI create/destroy';
        scope='Local zone 1 Scene only, Gate had no established player connection'
    }
    $result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'scene-aoi-deployment.json') -Encoding utf8
    $result | ConvertTo-Json -Depth 4
} finally {
    foreach ($key in $previousEnvironment.Keys) { [Environment]::SetEnvironmentVariable($key, $previousEnvironment[$key], 'Process') }
}
