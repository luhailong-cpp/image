$ErrorActionPreference = 'Stop'
$serverRoot = 'E:\work\xuanming-server-mmo'
$nextExecutable = Join-Path $PSScriptRoot 'friend-invites.exe'
$verification = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'verification-server.json') -Raw | ConvertFrom-Json
if ($verification.test.exitCode -ne 0 -or $verification.vet.exitCode -ne 0 -or $verification.build.exitCode -ne 0) { throw '后端验证未通过，不能启用。' }
if ((Get-FileHash -LiteralPath $nextExecutable -Algorithm SHA256).Hash -ne $verification.build.sha256) { throw '新程序与测试记录不符。' }
$running = @(Get-CimInstance Win32_Process -Filter "Name = 'friend.exe'")
if ($running.Count -gt 0) { throw '已有好友服务运行，停止替换以免打断其他任务。' }
if (Get-NetTCPConnection -State Listen -LocalPort 50400 -ErrorAction SilentlyContinue) { throw '好友服务端口已被占用，停止启动。' }
& (Join-Path $PSScriptRoot 'apply.ps1') -Repository server
if (-not $?) { throw '服务端源码同步失败。' }
$targetExecutable = Join-Path $serverRoot 'bin/go_services/friend.exe'
$backupPath = $null
if ((Test-Path -LiteralPath $targetExecutable) -and
    (Get-FileHash -LiteralPath $targetExecutable -Algorithm SHA256).Hash -ne $verification.build.sha256) {
    $backupRoot = Join-Path $serverRoot ('run/backups/team-invites-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    $backupPath = Join-Path $backupRoot 'friend.exe'
    Copy-Item -LiteralPath $targetExecutable -Destination $backupPath
}
Copy-Item -LiteralPath $nextExecutable -Destination $targetExecutable -Force
$env:KAFKA_COMMAND_TOPIC_PARTITIONS = '256'
$env:KAFKA_COMMAND_TOPIC_GENERATION = '2'
& pwsh -NoProfile -File (Join-Path $serverRoot 'tools/scripts/dev_tools.ps1') -Command go-svc-start-exe -GoServices friend -TierReadySeconds 30
if ($LASTEXITCODE -ne 0) { throw ('好友服务启动失败；原程序备份：' + $backupPath) }
$pidFile = Join-Path $serverRoot 'run/pids/go_services.pid.json'
$record = (Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json).friend
if (-not $record) { throw '启动后没有好友服务进程记录。' }
$friendProcess = Get-Process -Id $record.Pid -ErrorAction Stop
$contractPath = Join-Path $serverRoot 'run/pids/kafka_command_contract.json'
$contracts = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json -AsHashtable
$contracts['friend'] = @{ProcessId=$friendProcess.Id;StartTimeUtcTicks=[string]$friendProcess.StartTime.ToUniversalTime().Ticks;Generation=2;Partitions=256}
$contracts | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $contractPath -Encoding utf8
$result = [ordered]@{ processId=$friendProcess.Id; executable=$targetExecutable; sha256=(Get-FileHash -LiteralPath $targetExecutable -Algorithm SHA256).Hash; backup=$backupPath; deployedAt=[DateTime]::UtcNow.ToString('o'); port=$record.Port }
$result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'local-friend-deployment.json') -Encoding utf8
$result | ConvertTo-Json
