$ErrorActionPreference='Stop'
$snapshot=Join-Path $PSScriptRoot 'baseline-source'
$msbuild='D:/Program Files/Microsoft Visual Studio/18/Enterprise/MSBuild/Current/Bin/MSBuild.exe'
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss'
$log=Join-Path $PSScriptRoot "baseline-build-$stamp.log"
$deployed='E:/work/xuanming-server-mmo/bin/scene.exe'
$before=(Get-FileHash -LiteralPath $deployed).Hash
$start=[Diagnostics.ProcessStartInfo]::new($msbuild)
$start.UseShellExecute=$false;$start.CreateNoWindow=$true
$start.RedirectStandardOutput=$true;$start.RedirectStandardError=$true
$start.WorkingDirectory=$snapshot
$start.Environment.Clear()
foreach($pair in [Environment]::GetEnvironmentVariables('Process').GetEnumerator()) {
    $key=if($pair.Key -ieq 'PATH'){'Path'}else{$pair.Key.ToUpperInvariant()}
    $start.Environment[$key]=[string]$pair.Value
}
foreach($argument in @((Join-Path $snapshot 'game.sln'),'/t:cpp\libs\services\gate;cpp\libs\services\battle;cpp\nodes\scene','/m:1','/nr:false','/nologo','/v:minimal','/p:Configuration=Debug','/p:Platform=x64','/p:PostBuildEventUseInBuild=false','/fl',"/flp:logfile=$log;verbosity=normal;encoding=UTF-8")) { $start.ArgumentList.Add($argument) }
$process=[Diagnostics.Process]::new();$process.StartInfo=$start;[void]$process.Start()
$stdout=$process.StandardOutput.ReadToEndAsync();$stderr=$process.StandardError.ReadToEndAsync()
while(-not $process.WaitForExit(30000)){Write-Output "隔离基线 Scene 构建中；日志：$log"}
$stdout.Result|Set-Content -LiteralPath "$log.stdout.txt" -Encoding utf8
$stderr.Result|Set-Content -LiteralPath "$log.stderr.txt" -Encoding utf8
$after=(Get-FileHash -LiteralPath $deployed).Hash
if($before -ne $after){throw '运行目录 Scene 发生非预期变化'}
$summary=[ordered]@{revision='1ad634443d4d5028075d6b7e839b434018bfb0e8';exitCode=$process.ExitCode;log=$log;deployedBinaryUnchanged=$true}
if($process.ExitCode -eq 0){
    $exe=Join-Path $snapshot 'build/cpp/nodes/scene.exe'
    if(-not(Test-Path -LiteralPath $exe)){throw '未产出 Scene'}
    $summary.exe=$exe;$summary.sha256=(Get-FileHash -LiteralPath $exe).Hash.ToLowerInvariant()
}
$summary|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'baseline-build-result.json') -Encoding utf8
$summary|ConvertTo-Json
if($process.ExitCode -ne 0){Select-String -LiteralPath $log -Pattern 'error [A-Z]+[0-9]+|错误 [A-Z]+[0-9]+'|Select-Object -First 12|ForEach-Object Line}
exit $process.ExitCode
