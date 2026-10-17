param(
    [ValidateSet('Tests','Capture')][string]$Mode = 'Tests',
    [string]$ClientRoot = 'E:/work/mmorpg-client'
)
$ErrorActionPreference = 'Stop'
if ([IO.Path]::GetFullPath($ClientRoot).TrimEnd('\','/') -ne 'E:\work\mmorpg-client') {
    throw 'Verification is scoped to E:/work/mmorpg-client.'
}
if (Test-Path -LiteralPath (Join-Path $ClientRoot 'Temp/UnityLockfile')) {
    throw 'An editor owns this project. It was left running; verification did not start.'
}
$unity = 'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe'
$log = Join-Path $PSScriptRoot ("client-unity-$($Mode.ToLowerInvariant()).log")
$arguments = @('-batchmode', '-projectPath', ('"' + $ClientRoot + '"'), '-logFile', ('"' + $log + '"'))
if ($Mode -eq 'Tests') {
    $results = Join-Path $PSScriptRoot 'client-unity-tests.xml'
    $arguments += @('-nographics', '-runTests', '-testPlatform', 'EditMode',
        '-testFilter', 'MmorpgClient.Tests.EditMode.Battle.SkillClientTests;MmorpgClient.Tests.EditMode.Battle.SkillManaReplayTests;MmorpgClient.Tests.EditMode.Battle.SkillResourceTests;MmorpgClient.Tests.EditMode.Battle.TurnPlanTests',
        '-testResults', ('"' + $results + '"'))
} else {
    $arguments += @('-executeMethod', 'ClassSkillUiVerification.CaptureAll', '-quit')
}
$startedUtc = [DateTime]::UtcNow;
$process = Start-Process -FilePath $unity -ArgumentList $arguments -WindowStyle Hidden -PassThru -Wait
Write-Output "Unity $Mode exited $($process.ExitCode). Log: $log"
if ($process.ExitCode -ne 0) { exit $process.ExitCode }
if ($Mode -eq 'Tests') {
    if (-not (Test-Path -LiteralPath $results)) { throw 'Unity did not create a test result file.' }
    if ((Get-Item -LiteralPath $results).LastWriteTimeUtc -lt $startedUtc) { throw 'Unity test results were not updated during this run.' }
    [xml]$report = Get-Content -Raw -LiteralPath $results
    $summary = $report.'test-run'
    Write-Output "Unity EditMode: result=$($summary.result) total=$($summary.total) passed=$($summary.passed) failed=$($summary.failed)"
    if ($summary.result -ne 'Passed') { exit 1 }
} else {
    $complete = Join-Path (Split-Path $PSScriptRoot) 'qa/native-capture-complete.txt'
    if (-not (Test-Path -LiteralPath $complete)) { throw 'Unity did not confirm capture completion.' }
    if ((Get-Item -LiteralPath $complete).LastWriteTimeUtc -lt $startedUtc) { throw 'Capture completion marker is stale.' }
    Get-Content -LiteralPath $complete
}
