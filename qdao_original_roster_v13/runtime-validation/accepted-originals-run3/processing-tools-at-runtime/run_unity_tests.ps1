param([Parameter(Mandatory=$true)][ValidateSet('EditMode','PlayMode')][string]$Platform,[string]$Run='contract-run1',[Parameter(Mandatory=$true)][string]$InputSnapshot,[string]$Project='E:\work\tmp\qdao-original-verify-20260917',[string]$Scope='Original roster client verification; actual runtime observations determine the loaded identities and versions, without granting artwork approval')
$ErrorActionPreference='Stop'
$v13Project=[IO.Path]::GetFullPath($Project)
$v13Evidence=Join-Path 'E:\work\image\qdao_original_roster_v13\runtime-validation' $Run
$v13Editor='C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe'
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
while(-not $v13Process.WaitForExit(10000)){Write-Output ('V13_TEST_RUNNING '+$Platform+' '+[int]([DateTime]::UtcNow-$v13Start).TotalSeconds+'s')}
$v13Process.Refresh()
[ordered]@{exit_code=$v13Process.ExitCode;finished_utc=[DateTime]::UtcNow.ToString('o');xml_exists=(Test-Path -LiteralPath $v13Xml);log=$v13Log} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $v13Evidence ($v13Stem+'-completion.json')) -Encoding utf8
Write-Output ('V13_TEST_EXIT '+$Platform+' '+$v13Process.ExitCode)
exit $v13Process.ExitCode
