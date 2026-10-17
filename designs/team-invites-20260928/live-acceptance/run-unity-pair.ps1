[CmdletBinding()]
param(
    [string]$PlayerPath = 'E:/work/tmp/wuxing-team-invites-player-20260929/mmorpg.exe',
    [string]$ServerRoot = 'E:/work/xuanming-server-mmo',
    [int]$TimeoutSeconds = 600
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $PlayerPath -PathType Leaf)) { throw '请先构建邀请验收客户端。' }
$runId = [Guid]::NewGuid().ToString('N').Substring(0,16)
$runDir = Join-Path $PSScriptRoot ('unity-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + $runId)
New-Item -ItemType Directory -Path $runDir | Out-Null
$devPassword = $env:LOGIN_DEV_PASSWORD_SHARED_SECRET
if (-not $devPassword) {
    # 沿用服务器一键启动的开发凭据来源，只放进子进程环境。
    $localConfig = Get-Content -LiteralPath (Join-Path $ServerRoot 'robot/etc/robot.yaml') -Raw
    $match = [regex]::Match($localConfig, '(?m)^password:\s*"([^"\r\n]+)"')
    if (-not $match.Success) { throw '本地开发登录凭据未配置。' }
    $devPassword = $match.Groups[1].Value
    $localConfig = $null
    $match = $null
}
if ($devPassword -match '[\s"]') { throw '现有自动登录参数解析器不支持此凭据格式。' }
$processes = @()
$timer = [Diagnostics.Stopwatch]::StartNew()
try {
    foreach ($role in @('member','leader')) {
        $start = [Diagnostics.ProcessStartInfo]::new()
        $start.FileName = $PlayerPath
        $start.WorkingDirectory = Split-Path -Parent $PlayerPath
        $start.UseShellExecute = $false
        $start.WindowStyle = [Diagnostics.ProcessWindowStyle]::Hidden
        $start.RedirectStandardOutput = $true
        $start.RedirectStandardError = $true
        foreach ($arg in @('-screen-fullscreen','0','-screen-width','1920','-screen-height','1080',
            '-teamVerifyMode',$role,'-teamVerifyDir',$runDir,'-teamVerifyRun',$runId,
            '-logFile',(Join-Path $runDir ($role + '.log')))) { $start.ArgumentList.Add($arg) }
        $account = 'robot_tui_' + $runId + '_' + $role
        $start.Environment['MMORPG_AUTOPILOT_ARGS'] = "-gateway http://127.0.0.1:8081 -zone 1 -account $account -password $devPassword -loginTimeout 90 -logTag $role"
        $process = [Diagnostics.Process]::Start($start)
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        $processes += [pscustomobject]@{role=$role;process=$process;account=$account;stdout=$stdout;stderr=$stderr}
        Write-Output "已启动隔离验收客户端：$role，PID $($process.Id)"
    }
    $devPassword = $null
    $lastReport = 0
    while (@($processes | Where-Object { -not $_.process.HasExited }).Count) {
        if ($timer.Elapsed.TotalSeconds -ge $TimeoutSeconds) { throw '双客户端验收超时。' }
        if ($timer.Elapsed.TotalSeconds - $lastReport -ge 30) {
            $lastReport = [int]$timer.Elapsed.TotalSeconds
            Write-Output "双客户端验收已运行 $lastReport 秒，证据目录：$runDir"
        }
        Start-Sleep -Milliseconds 500
    }
    $verdicts = foreach ($entry in $processes) {
        $entry.stdout.GetAwaiter().GetResult() | Set-Content -LiteralPath (Join-Path $runDir ($entry.role + '.stdout.log')) -Encoding utf8
        $entry.stderr.GetAwaiter().GetResult() | Set-Content -LiteralPath (Join-Path $runDir ($entry.role + '.stderr.log')) -Encoding utf8
        $log = Get-Content -LiteralPath (Join-Path $runDir ($entry.role + '.log')) -Raw
        $clientReportPath = Join-Path $runDir ($runId + '-' + $entry.role + '-report.json')
        $clientReport = if (Test-Path -LiteralPath $clientReportPath) { Get-Content -LiteralPath $clientReportPath -Raw | ConvertFrom-Json } else { $null }
        $passed = $entry.process.ExitCode -eq 0 -and $log -match '\[TeamVerify\].*RESULT=PASS' -and $clientReport.result -eq 'PASS'
        [ordered]@{ role=$entry.role; processId=$entry.process.Id; exitCode=$entry.process.ExitCode; passed=$passed }
    }
    $report = [ordered]@{runId=$runId;directory=$runDir;player=$PlayerPath;completedAt=[DateTime]::UtcNow.ToString('o');clients=@($verdicts)}
    $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $runDir 'pair-result.json') -Encoding utf8
    $report | ConvertTo-Json -Depth 5
    if (@($verdicts | Where-Object { -not $_.passed }).Count) { throw "双客户端验收失败，请查看 $runDir" }
} finally {
    $devPassword = $null
    foreach ($entry in $processes) {
        if (-not $entry.process.HasExited) { $entry.process.Kill() }
        $entry.process.Dispose()
    }
}
