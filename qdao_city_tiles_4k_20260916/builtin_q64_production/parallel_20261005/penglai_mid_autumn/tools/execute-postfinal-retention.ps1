param(
    [Parameter(Mandatory=$true)][ValidateSet('r09_c14','r10_c14')][string]$Tile,
    [switch]$Execute,
    [string]$ExpectedPlanSha256
)
# Default validates only. Root must authorize this exact tile/plan hash before -Execute.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$ProductionRoot=[IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$TileRoot=[IO.Path]::GetFullPath((Join-Path $ProductionRoot $Tile))
$PlanPath=Join-Path $TileRoot 'retention-postfinal-plan.json'
$LogPath=Join-Path $TileRoot 'retention-postfinal-log.json'
$ResultPath=Join-Path $TileRoot 'retention-postfinal-result.json'
$HistoryDir=Join-Path $TileRoot 'retention-postfinal-text-history'
function Hash-File([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Assert-InsideTile([string]$Path){
    $absolute=[IO.Path]::GetFullPath($Path)
    if($absolute -ne $Path -or -not $absolute.StartsWith($TileRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Outside normalized exact tile scope: $Path"}
    $cursor=$absolute
    while($true){
        if(Test-Path -LiteralPath $cursor){if(((Get-Item -LiteralPath $cursor).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw "Reparse/link refused: $cursor"}}
        if($cursor -eq $TileRoot){break};$cursor=Split-Path -Parent $cursor
    };return $absolute
}
function Save-Json([string]$Path,$Value){
    [IO.File]::WriteAllText($Path,(ConvertTo-Json -InputObject $Value -Depth 100)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
}
function Get-Strings($Value){
    if($null -eq $Value){return}
    if($Value -is [string]){$Value;return}
    if($Value -is [System.Collections.IDictionary]){foreach($v in $Value.Values){Get-Strings $v};return}
    if($Value -is [System.Collections.IEnumerable]){foreach($v in $Value){Get-Strings $v}}
}
function Get-LiveJson([string]$Root){
    $queue=[System.Collections.Generic.Queue[string]]::new();$queue.Enqueue($Root)
    while($queue.Count -gt 0){
        $dir=$queue.Dequeue()
        foreach($entry in Get-ChildItem -LiteralPath $dir -Force){
            if(($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){continue}
            if($entry.PSIsContainer){
                if($entry.FullName -eq $TileRoot -or $entry.Name -in @('r10_c13','tools','native','guides','repairs','qa','evidence') -or $entry.Name -match 'history'){continue}
                $queue.Enqueue($entry.FullName)
            }elseif($entry.Extension -eq '.json' -and ($entry.Name -in @('plan.json','preparation.json','manifest.json','progress.json','index.json') -or $entry.Name -match 'delivery')){$entry}
        }
    }
}
function Get-CurrentStrings($Doc,[string]$Name){
    if($Name -eq 'manifest.json'){
        foreach($k in @('file','currentNeighbors','runtimeDependencies','currentDesign','currentDesigns')){if($Doc.Contains($k)){Get-Strings $Doc[$k]}}
        if($Doc.Contains('qa')){foreach($q in $Doc.qa){if($q -is [System.Collections.IDictionary] -and $q.Contains('file')){$q.file}}}
    }else{Get-Strings $Doc}
}
if(Test-Path -LiteralPath $LogPath){throw 'Tile ledger already exists; inspect journal and actual state, never automatically retry.'}
if(Test-Path -LiteralPath $HistoryDir){throw 'Tile TEXT history already exists; inspect state, never overwrite.'}
$Plan=Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json -AsHashtable
$PlanSha=Hash-File $PlanPath
if($Plan.tile -ne $Tile -or $Plan.root -ne $TileRoot){throw 'Plan tile/root mismatch.'}
if($Execute -and ([string]::IsNullOrEmpty($ExpectedPlanSha256) -or $ExpectedPlanSha256.ToLowerInvariant() -ne $PlanSha)){throw 'Execute requires exact reviewed plan SHA.'}
if($Plan.executionScript.file -ne $PSCommandPath -or (Hash-File $PSCommandPath) -ne $Plan.executionScript.sha256){throw 'Executor differs from reviewed plan.'}
$null=Assert-InsideTile $Plan.final.file
foreach($v in $Plan.anchors){if((Hash-File $v.file) -ne $v.sha256){throw "Current anchor changed: $($v.file)"}}
$ManifestPath=Join-Path $TileRoot 'output\manifest.json';$GenerationPath=$Plan.final.file+'.generation.json';$CurrentPlanPath=Join-Path $TileRoot 'plan.json'
$Manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json -AsHashtable
$Generation=Get-Content -LiteralPath $GenerationPath -Raw | ConvertFrom-Json -AsHashtable
$CurrentPlan=Get-Content -LiteralPath $CurrentPlanPath -Raw | ConvertFrom-Json -AsHashtable
if($Manifest.scopedLocalSeamsPassed -ne $true -or $Manifest.completePixelCoverage -ne $true -or $Manifest.sha256 -ne $Plan.final.sha256 -or $Generation.sha256 -ne $Plan.final.sha256){throw 'Exact exported final and current scoped QA required.'}
$RemoveSet=@{};$KnownBinary=@{}
foreach($item in $Plan.remove){
    $path=Assert-InsideTile $item.file
    if([IO.Path]::GetExtension($path).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.npy','.pyc')){throw "Text/directory/unsupported target: $path"}
    $key=$path.ToLowerInvariant();if($RemoveSet.ContainsKey($key)){throw 'Duplicate removal target.'}
    if(-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -ne $item.bytes -or (Hash-File $path) -ne $item.sha256){throw "Removal target changed/missing: $path"}
    $RemoveSet[$key]=$item.sha256;$KnownBinary[$key]=$true
}
foreach($item in $Plan.keep){
    $path=Assert-InsideTile $item.file;$key=$path.ToLowerInvariant()
    if($RemoveSet.ContainsKey($key) -or (Hash-File $path) -ne $item.sha256){throw "Kept file changed/collision: $path"};$KnownBinary[$key]=$true
}
foreach($p in Get-ChildItem -LiteralPath $TileRoot -File -Recurse){
    if($p.Extension.ToLowerInvariant() -in @('.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.npy','.pyc') -and -not $KnownBinary.ContainsKey($p.FullName.ToLowerInvariant())){throw "New unreviewed binary/in-flight output: $($p.FullName)"}
}
$Requests=@(Get-ChildItem -LiteralPath $TileRoot -File -Filter '*.request.json' -Recurse)
if($Requests.Count -ne $Plan.requestInventory.Count){throw 'Request inventory changed.'}
foreach($v in $Plan.requestInventory){if((Hash-File $v.file) -ne $v.sha256){throw "New/changed generation request: $($v.file)"}}
# Every dated acquisition/review/source TEXT remains; this is not a runtime reference scan.
foreach($v in $Plan.textInventory){if((Hash-File $v.file) -ne $v.sha256){throw "Preserved TEXT changed after review: $($v.file)"}}
$Prior=@()
if($null -ne $Plan.priorRetentionLedger){
    $p=Assert-InsideTile $Plan.priorRetentionLedger.file
    if((Hash-File $p) -ne $Plan.priorRetentionLedger.sha256){throw 'Prior retirement ledger changed.'}
    $Prior=@((Get-Content -LiteralPath $p -Raw | ConvertFrom-Json -AsHashtable).removed)
    foreach($r in $Prior){$q=Assert-InsideTile $r.file;if($r.retiredAfterExport -ne $true -or $r.sourceImageAvailable -ne $false -or (Test-Path -LiteralPath $q)){throw 'Prior completed retirement is not factual.'}}
}
$External=@(Get-LiveJson (Split-Path -Parent $ProductionRoot))
foreach($record in $External){
    $doc=Get-Content -LiteralPath $record.FullName -Raw | ConvertFrom-Json -AsHashtable
    foreach($v in Get-CurrentStrings $doc $record.Name){
        $key=$v.Replace('/','\').ToLowerInvariant()
        if($RemoveSet.ContainsKey($key)){throw "Actual current external consumer: $($record.FullName) -> $v"}
    }
}
if(-not $Execute){[PSCustomObject]@{status='validated_read_only';tile=$Tile;planSha256=$PlanSha;removeCount=$Plan.remove.Count;removeBytes=$Plan.summary.removeBytes;keepCount=$Plan.keep.Count;currentExternalDocumentsScanned=$External.Count;priorRetiredCount=$Prior.Count;deletedFiles=0}|ConvertTo-Json;return}
New-Item -Path $HistoryDir -ItemType Directory | Out-Null
foreach($pair in @(@($ManifestPath,'manifest.before-retention.json'),@($GenerationPath,'candidate.generation.before-retention.json'),@($CurrentPlanPath,'plan.before-retention.json'))){Copy-Item -LiteralPath $pair[0] -Destination (Join-Path $HistoryDir $pair[1])}
$Removed=[System.Collections.Generic.List[object]]::new();$Started=[DateTime]::UtcNow.ToString('o');$script:JournalFailed=$false
function Save-Ledger([string]$Status,[string]$Failure,$Intent){
    $ledger=[ordered]@{startedAt=$Started;recordedAt=[DateTime]::UtcNow.ToString('o');tile=$Tile;root=$TileRoot;plan=@{file=$PlanPath;sha256=$PlanSha};final=$Plan.final;status=$Status;priorRetentionLedger=$Plan.priorRetentionLedger;previousRetiredCount=$Prior.Count;newRemovedCount=$Removed.Count;removed=@($Prior)+@($Removed.ToArray());plannedNewRemovalCount=$Plan.remove.Count;nextRemovalIntent=$Intent;failure=$Failure;allTextPreserved=$true;historicalAssemblyUnchanged=$Plan.assembly;metadataPaths=@($ManifestPath,$GenerationPath,$CurrentPlanPath);historyDirectory=$HistoryDir}
    try{Save-Json $LogPath $ledger}catch{$script:JournalFailed=$true;throw}
}
function Mark-Retired($Value,$Map){
    if($Value -is [System.Collections.IDictionary]){
        if($Value.Contains('file') -and $Value.Contains('sha256')){$k=([string]$Value.file).Replace('/','\').ToLowerInvariant();if($Map.ContainsKey($k) -and $Map[$k] -eq $Value.sha256){$Value['retiredAfterExport']=$true;$Value['sourceImageAvailable']=$false;$Value['sourceFileLifecycle']='historical_pixels_removed_after_final_export';$Value['runtimeDependency']=$false;$Value['retentionLog']=$LogPath}}
        foreach($k in @($Value.Keys)){Mark-Retired $Value[$k] $Map}
    }elseif($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]){foreach($v in $Value){Mark-Retired $v $Map}}
}
Save-Ledger 'executing_exact_reviewed_list' '' $null
$Failure=''
try{
    foreach($item in $Plan.remove){
        $path=Assert-InsideTile $item.file
        if((Hash-File $path) -ne $item.sha256 -or (Get-Item -LiteralPath $path).Length -ne $item.bytes){throw "Target changed after preflight: $path"}
        Save-Ledger 'executing_exact_reviewed_list' '' $item
        Remove-Item -LiteralPath $path
        if(Test-Path -LiteralPath $path){throw "Removal did not complete: $path"}
        $Removed.Add([ordered]@{file=$path;sha256=$item.sha256;bytes=$item.bytes;reason=$item.reason;retiredAfterExport=$true;sourceImageAvailable=$false;runtimeDependency=$false;retiredAt=[DateTime]::UtcNow.ToString('o')})
        Save-Ledger 'executing_exact_reviewed_list' '' $null
    }
}catch{
    if($script:JournalFailed){throw 'Ledger write failed; stopped with no further deletions. Inspect last durable nextRemovalIntent and actual files; do not rerun.'}
    $Failure=$_.Exception.Message
}
$Status=if($Failure){'stopped_after_error_no_automatic_retry'}else{'retired_after_final_export_and_scoped_QA'}
Save-Ledger $Status $Failure $null
# Ledger is stable before metadata hashes reference it; no circular manifest/ledger SHA.
$Actual=@{};foreach($r in @($Prior)+@($Removed.ToArray())){$Actual[$r.file.ToLowerInvariant()]=$r.sha256}
$LedgerRef=@{file=$LogPath;sha256=(Hash-File $LogPath)}
Mark-Retired $Generation $Actual;$Generation['retentionLog']=$LogPath;$Generation['retentionRecord']=$LedgerRef;$Generation['sourcePolicy']='Final is runtime. All retired intermediate image/field references are historical and resolved by this tile-local actual-retirement ledger; acquisition TEXT is immutable.';Save-Json $GenerationPath $Generation
Mark-Retired $CurrentPlan $Actual;$CurrentPlan['processingInputsHistoricalAfterExport']=$true;$CurrentPlan['retentionLog']=$LogPath;$CurrentPlan['retentionRecord']=$LedgerRef;$CurrentPlan['currentExportedFinal']=$Plan.final;Save-Json $CurrentPlanPath $CurrentPlan
Mark-Retired $Manifest $Actual;$Manifest['retentionLog']=$LogPath;$Manifest['retentionRecord']=$LedgerRef;$Manifest['sourceRecordsHistoricalAfterRetention']=$true;$Manifest['sourcePolicy']='Only actual completed retired entries are unavailable; historical image/field/selection sources remain recorded as TEXT, final/current design/current QA and actual runtime dependencies stay available.';$Manifest['runtimeDependencies']=@($Plan.final);$Manifest['currentCandidateGeneration']=@{file=$GenerationPath;sha256=(Hash-File $GenerationPath)};$Manifest['plan']=@{file=$CurrentPlanPath;sha256=(Hash-File $CurrentPlanPath)}
if($Manifest.Contains('currentAppliedRepair') -and $Manifest.currentAppliedRepair.Contains('currentCandidateGeneration')){$Manifest.currentAppliedRepair['currentCandidateGeneration']=$Manifest.currentCandidateGeneration}
Save-Json $ManifestPath $Manifest
if((Hash-File $Plan.final.file) -ne $Plan.final.sha256 -or (Hash-File $Plan.assembly.file) -ne $Plan.assembly.sha256){throw 'Protected final or immutable assembly changed.'}
foreach($v in $Plan.keep){if((Hash-File $v.file) -ne $v.sha256){throw 'Protected current image changed.'}}
Save-Json $ResultPath ([ordered]@{completedAt=[DateTime]::UtcNow.ToString('o');status=$Status;newRemovedCount=$Removed.Count;priorRetiredCount=$Prior.Count;ledger=$LedgerRef;final=$Plan.final;manifest=@{file=$ManifestPath;sha256=(Hash-File $ManifestPath)};generation=@{file=$GenerationPath;sha256=(Hash-File $GenerationPath)};currentPlan=@{file=$CurrentPlanPath;sha256=(Hash-File $CurrentPlanPath)};immutableAssemblyUnchanged=$Plan.assembly;failure=$Failure})
if($Failure){throw $Failure}
[PSCustomObject]@{status=$Status;tile=$Tile;newRemovedCount=$Removed.Count;ledger=$LogPath;result=$ResultPath;finalSha256=$Plan.final.sha256}|ConvertTo-Json
