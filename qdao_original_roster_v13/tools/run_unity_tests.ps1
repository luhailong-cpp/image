param([Parameter(Mandatory=$true)][ValidateSet('EditMode','PlayMode')][string]$Platform,[Parameter(Mandatory=$true)][string]$Run,[Parameter(Mandatory=$true)][string]$InputSnapshot,[Parameter(Mandatory=$true)][string]$Project,[Parameter(Mandatory=$true)][string]$Editor,[ValidateRange(30,7200)][int]$TimeoutSeconds=1800,[string]$Scope='Original roster client verification; actual runtime observations determine the loaded identities and versions, without granting artwork approval')
$ErrorActionPreference='Stop'
$v13Project=[IO.Path]::GetFullPath($Project)
$v13Root=Split-Path -Parent $PSScriptRoot
$v13Workspace=Split-Path -Parent (Split-Path -Parent $v13Root)
if (-not $v13Project.StartsWith($v13Workspace + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unity project must be inside this repository workspace.' }
if ($Run -notmatch '^[a-zA-Z0-9][a-zA-Z0-9_.-]*$') { throw 'Run must be a single new evidence directory name.' }
$v13Evidence=Join-Path (Join-Path $v13Root 'runtime-validation') $Run
$v13Editor=[IO.Path]::GetFullPath($Editor)
if (-not (Test-Path -LiteralPath $v13Editor -PathType Leaf)) { throw 'Unity Editor executable does not exist.' }
if (Test-Path -LiteralPath (Join-Path $v13Project 'Temp/UnityLockfile')) { throw 'Unity project is already open; do not replace its editor.' }
New-Item -ItemType Directory -Path $v13Evidence -Force | Out-Null
$v13Stem=$Platform.ToLowerInvariant()
$v13Xml=Join-Path $v13Evidence ($v13Stem+'.xml')
$v13Log=Join-Path $v13Evidence ($v13Stem+'.log')
if ((Test-Path -LiteralPath $v13Xml) -or (Test-Path -LiteralPath $v13Log)){throw 'Choose a new run name to retain previous evidence.'}
$v13Filter=if($Platform -eq 'EditMode'){'MmorpgClient.Tests.EditMode.Tianyong.Qdao;MmorpgClient.Tests.EditMode.Battle.BattleRosterAppearanceTests'}else{'MmorpgClient.Tests.PlayMode.Qdao'}
$v13Arguments=@('-batchmode','-force-d3d11','-projectPath',('"'+$v13Project+'"'),'-runTests','-testPlatform',$Platform,'-testFilter',$v13Filter,'-testResults',('"'+$v13Xml+'"'),'-logFile',('"'+$v13Log+'"'))
$env:QDAO_ROSTER_CAPTURE_DIR=Join-Path $v13Evidence 'city-captures'
if (-not (Test-Path -LiteralPath $InputSnapshot -PathType Leaf)) { throw 'Input snapshot does not exist.' }
$env:QDAO_ROSTER_INPUT_SNAPSHOT=[IO.Path]::GetFullPath($InputSnapshot)
$v13SnapshotData=Get-Content -LiteralPath $env:QDAO_ROSTER_INPUT_SNAPSHOT -Raw | ConvertFrom-Json
if ([IO.Path]::GetFullPath($v13SnapshotData.project) -ne $v13Project) { throw 'Input snapshot belongs to another Unity project.' }
$v13SnapshotSha=(Get-FileHash -LiteralPath $env:QDAO_ROSTER_INPUT_SNAPSHOT -Algorithm SHA256).Hash.ToLowerInvariant()
$v13Start=[DateTime]::UtcNow
$v13Process=Start-Process -FilePath $v13Editor -ArgumentList $v13Arguments -WindowStyle Hidden -PassThru
[ordered]@{started_utc=$v13Start.ToString('o');pid=$v13Process.Id;project=$v13Project;platform=$Platform;filter=$v13Filter;arguments=$v13Arguments;capture_directory=$env:QDAO_ROSTER_CAPTURE_DIR;input_snapshot=$env:QDAO_ROSTER_INPUT_SNAPSHOT;input_snapshot_sha256=$v13SnapshotSha;scope=$Scope} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $v13Evidence ($v13Stem+'-launch.json')) -Encoding utf8
Write-Output ('V13_TEST_STARTED '+$Platform+' PID '+$v13Process.Id)
$v13TimedOut=$false
while(-not $v13Process.WaitForExit(10000)){
    Write-Output ('V13_TEST_RUNNING '+$Platform+' '+[int]([DateTime]::UtcNow-$v13Start).TotalSeconds+'s')
    if (([DateTime]::UtcNow-$v13Start).TotalSeconds -ge $TimeoutSeconds) {
        $v13TimedOut=$true
        $v13Process.Kill()
        $v13Process.WaitForExit()
        break
    }
}
$v13Process.Refresh()
[ordered]@{exit_code=$v13Process.ExitCode;timed_out=$v13TimedOut;finished_utc=[DateTime]::UtcNow.ToString('o');xml_exists=(Test-Path -LiteralPath $v13Xml);log=$v13Log} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $v13Evidence ($v13Stem+'-completion.json')) -Encoding utf8
Write-Output ('V13_TEST_EXIT '+$Platform+' '+$v13Process.ExitCode)
if ($v13TimedOut -or -not (Test-Path -LiteralPath $v13Xml)) { exit 1 }
[xml]$v13Results=Get-Content -LiteralPath $v13Xml -Raw
if ($v13Results.'test-run'.result -ne 'Passed' -or [int]$v13Results.'test-run'.total -eq 0) { exit 1 }
exit $v13Process.ExitCode
