$ErrorActionPreference = 'Stop'
$serverRoot = 'E:/work/xuanming-server-mmo'
$msbuild = 'D:/Program Files/Microsoft Visual Studio/18/Enterprise/MSBuild/Current/Bin/MSBuild.exe'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $PSScriptRoot "scene-build-$stamp.log"
$before = (Get-FileHash -LiteralPath (Join-Path $serverRoot 'bin/scene.exe')).Hash
$start = [Diagnostics.ProcessStartInfo]::new($msbuild)
$start.UseShellExecute = $false
$start.CreateNoWindow = $true
$start.RedirectStandardOutput = $true
$start.RedirectStandardError = $true
$start.WorkingDirectory = $serverRoot
$start.Environment.Clear()
foreach ($pair in [Environment]::GetEnvironmentVariables('Process').GetEnumerator()) {
    $key = if ($pair.Key -ieq 'PATH') { 'Path' } else { $pair.Key.ToUpperInvariant() }
    $start.Environment[$key] = [string]$pair.Value
}
foreach ($argument in @(
    (Join-Path $serverRoot 'game.sln'), '/t:cpp\nodes\scene', '/m:1', '/nr:false', '/nologo', '/v:minimal',
    '/p:Configuration=Debug', '/p:Platform=x64', '/p:PostBuildEventUseInBuild=false',
    "/p:ForceImportAfterCppTargets=$(Join-Path $PSScriptRoot 'isolated-node-output.targets')",
    '/fl', "/flp:logfile=$log;verbosity=normal;encoding=UTF-8"
)) { $start.ArgumentList.Add($argument) }
$process = [Diagnostics.Process]::new()
$process.StartInfo = $start
[void]$process.Start()
$stdout = $process.StandardOutput.ReadToEndAsync()
$stderr = $process.StandardError.ReadToEndAsync()
while (-not $process.WaitForExit(30000)) { Write-Output "Scene 构建进行中；日志：$log" }
$stdout.Result | Set-Content -LiteralPath "$log.stdout.txt" -Encoding utf8
$stderr.Result | Set-Content -LiteralPath "$log.stderr.txt" -Encoding utf8
$after = (Get-FileHash -LiteralPath (Join-Path $serverRoot 'bin/scene.exe')).Hash
if ($before -ne $after) { throw '运行目录的 Scene 产物发生非预期变化' }
$summary = [ordered]@{ exitCode = $process.ExitCode; log = $log; deployedBinaryUnchanged = ($before -eq $after) }
if ($process.ExitCode -eq 0) {
    $exe = Join-Path $PSScriptRoot 'build/scene/scene.exe'
    if (-not (Test-Path -LiteralPath $exe)) { throw '未生成隔离目录中的 Scene 产物' }
    $summary.exe = $exe
    $summary.sha256 = (Get-FileHash -LiteralPath $exe).Hash.ToLowerInvariant()
}
$summary | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'scene-build-result.json') -Encoding utf8
$summary | ConvertTo-Json
if ($process.ExitCode -ne 0) {
    Select-String -LiteralPath $log -Pattern 'error [A-Z]+[0-9]+|错误 [A-Z]+[0-9]+' | Select-Object -First 12 | ForEach-Object Line
}
exit $process.ExitCode
