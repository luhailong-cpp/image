param(
    [switch]$Execute,
    [string]$ExpectedPlanSha256
)
# Default is validation only. This preparation turn authorizes NO deletion.
# Invoke -Execute only after explicit later authorization for this reviewed r09_c15 list.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$TileRoot = [IO.Path]::GetFullPath('D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel_20261005\penglai_mid_autumn\r09_c15')
$ProductionRoot = Split-Path -Parent $TileRoot
$PlanPath = Join-Path $TileRoot 'retention-plan.json'
$LogPath = Join-Path $TileRoot 'retention-log.json'
function Hash-File([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Assert-InsideTile([string]$Path) {
    $absolute = [IO.Path]::GetFullPath($Path)
    if (-not $absolute.StartsWith($TileRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Target outside exact r09_c15 scope: $Path" }
    if ($absolute -ne $Path) { throw "Plan paths must already be normalized absolute paths: $Path" }
    $cursor = $absolute
    while ($cursor -ne $TileRoot) {
        if (Test-Path -LiteralPath $cursor) {
            $entry = Get-Item -LiteralPath $cursor
            if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Link/reparse target refused: $cursor" }
        }
        $cursor = Split-Path -Parent $cursor
    }
    return $absolute
}
function Get-Strings($Value) {
    if ($null -eq $Value) { return }
    if ($Value -is [string]) { $Value; return }
    if ($Value -is [System.Collections.IDictionary]) { foreach ($v in $Value.Values) { Get-Strings $v }; return }
    if ($Value -is [PSCustomObject]) { foreach ($p in $Value.PSObject.Properties) { Get-Strings $p.Value }; return }
    if ($Value -is [System.Collections.IEnumerable]) { foreach ($v in $Value) { Get-Strings $v } }
}
function Save-Json([string]$Path, $Value) {
    $json = ConvertTo-Json -InputObject $Value -Depth 100
    [IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
}
$Plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json -AsHashtable
if (((Get-Item -LiteralPath $TileRoot).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Tile root is a link/reparse point; refuse execution.' }
$PlanSha = Hash-File $PlanPath
if ($Execute -and ([string]::IsNullOrEmpty($ExpectedPlanSha256) -or $ExpectedPlanSha256.ToLowerInvariant() -ne $PlanSha)) { throw 'Execution requires the exact reviewed plan SHA256.' }
if ($Plan.root -ne $TileRoot) { throw 'Wrong plan root.' }
if (Test-Path -LiteralPath $LogPath) { throw 'An execution ledger already exists. Refuse an automatic retry; inspect its actual state first.' }
$ManifestPath = Join-Path $TileRoot 'output\manifest.json'
$GenerationPath = $Plan.final.file + '.generation.json'
foreach ($anchor in @($Plan.final, $Plan.finalManifest, $Plan.currentCandidateGeneration, $Plan.scopedReview, $Plan.executionScript)) {
    if ((Hash-File $anchor.file) -ne $anchor.sha256) { throw "Authoritative anchor changed: $($anchor.file)" }
}
foreach ($anchor in $Plan.protectedExternalSources) {
    if ((Hash-File $anchor.file) -ne $anchor.sha256) { throw "Protected external source changed: $($anchor.file)" }
}
$Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json -AsHashtable
$Generation = Get-Content -LiteralPath $GenerationPath -Raw | ConvertFrom-Json -AsHashtable
if (-not $Manifest.scopedLocalSeamsPassed -or -not $Manifest.completePixelCoverage) { throw 'Final coverage and scoped QA are required.' }
if ($Manifest.sha256 -ne $Plan.final.sha256 -or $Generation.sha256 -ne $Plan.final.sha256) { throw 'Candidate provenance mismatch.' }
$RemoveSet = @{}
foreach ($item in $Plan.remove) {
    $path = Assert-InsideTile $item.file
    if ([IO.Path]::GetExtension($path).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.npy','.pyc')) { throw "Text or unsupported deletion target: $path" }
    if ($RemoveSet.ContainsKey($path.ToLowerInvariant())) { throw "Duplicate target: $path" }
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing/changed target, refusing retry: $path" }
    $entry = Get-Item -LiteralPath $path
    if ($entry.Length -ne $item.bytes -or (Hash-File $path) -ne $item.sha256) { throw "Target changed: $path" }
    $RemoveSet[$path.ToLowerInvariant()] = $item.sha256
}
foreach ($item in $Plan.keep) {
    $path = Assert-InsideTile $item.file
    if ($RemoveSet.ContainsKey($path.ToLowerInvariant())) { throw "Keep/remove collision: $path" }
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Kept file missing: $path" }
    $entry = Get-Item -LiteralPath $path
    if ($entry.Length -ne $item.bytes -or (Hash-File $path) -ne $item.sha256) { throw "Kept file changed: $path" }
}
# Rescan external JSON references just before execution; never traverse the unrelated blocked tile or tools.
$ScanDirs = @($ProductionRoot) + @(Get-ChildItem -LiteralPath $ProductionRoot -Directory | Where-Object { $_.FullName -ne $TileRoot -and $_.Name -notin @('tools','r10_c13') } | ForEach-Object { $_.FullName })
$ExternalFiles = @(Get-ChildItem -LiteralPath $ProductionRoot -File -Filter '*.json')
foreach ($dir in $ScanDirs | Select-Object -Skip 1) { $ExternalFiles += @(Get-ChildItem -LiteralPath $dir -File -Filter '*.json' -Recurse) }
foreach ($record in $ExternalFiles) {
    $raw = Get-Content -LiteralPath $record.FullName -Raw
    if ($raw -notmatch 'r09_c15') { continue }
    $doc = $raw | ConvertFrom-Json -AsHashtable
    $historical = @($Plan.historicalExternalReferenceExemptions | Where-Object { $_.record.file -eq $record.FullName })
    if ($historical.Count -gt 0) {
        if ($historical.Count -ne 1 -or (Hash-File $record.FullName) -ne $historical[0].record.sha256) { throw "Historical-only reference changed: $($record.FullName)" }
        continue
    }
    foreach ($value in Get-Strings $doc) {
        $normalized = $value.Replace('/','\').ToLowerInvariant()
        if ($RemoveSet.ContainsKey($normalized)) { throw "External reference now uses a proposed removal: $($record.FullName) -> $value" }
    }
}
# New in-tile in-flight inputs or edits require a new reviewed plan, not a silent deletion.
foreach ($path in Get-ChildItem -LiteralPath $TileRoot -File -Filter '*.request.json' -Recurse) {
    $known = @($Plan.keep | Where-Object { $_.file -eq $path.FullName })
    if ($known.Count -ne 1 -or $known[0].sha256 -ne (Hash-File $path.FullName)) { throw "New/changed request since planning: $($path.FullName)" }
}
if (-not $Execute) {
    [PSCustomObject]@{ status='validated_only_no_files_deleted'; planSha256=$PlanSha; keepCount=$Plan.keep.Count; proposedRemovalCount=$Plan.remove.Count; proposedRemovalBytes=$Plan.summary.removeBytes; externalRecordsRescanned=$ExternalFiles.Count } | ConvertTo-Json
    return
}
# File operations stay in PowerShell and use exact literal paths; no recursive removal, directories, glob deletes, or alternate shell.
$HistoryDir = Join-Path $TileRoot 'retention-text-history'
if (Test-Path -LiteralPath $HistoryDir) { throw 'History location already exists; do not overwrite or automatically retry.' }
New-Item -Path $HistoryDir -ItemType Directory | Out-Null
Copy-Item -LiteralPath $ManifestPath -Destination (Join-Path $HistoryDir 'manifest.before-retention.json')
Copy-Item -LiteralPath $GenerationPath -Destination (Join-Path $HistoryDir 'candidate.generation.before-retention.json')
$Removed = [System.Collections.Generic.List[object]]::new()
$StartedAt = [DateTime]::UtcNow.ToString('o')
function Mark-Retired($Value, $ActualRetired) {
    if ($Value -is [System.Collections.IDictionary]) {
        if ($Value.Contains('file') -and $Value.Contains('sha256')) {
            $key = ([string]$Value.file).Replace('/','\').ToLowerInvariant()
            if ($ActualRetired.ContainsKey($key) -and $ActualRetired[$key] -eq $Value.sha256) {
                $Value['retiredAfterExport']=$true; $Value['sourceImageAvailable']=$false
                $Value['sourceFileLifecycle']='historical_pixels_removed_after_final_export'
                $Value['runtimeDependency']=$false; $Value['retentionLog']=$LogPath
            }
        }
        foreach ($k in @($Value.Keys)) { Mark-Retired $Value[$k] $ActualRetired }
    } elseif ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]) {
        foreach ($v in $Value) { Mark-Retired $v $ActualRetired }
    }
}
function Save-ExecutionState([string]$Status,[string]$Failure) {
    $actual=@{};foreach ($x in $Removed) { $actual[$x.file.ToLowerInvariant()]=$x.sha256 }
    $ledger=[ordered]@{ startedAt=$StartedAt; recordedAt=[DateTime]::UtcNow.ToString('o'); root=$TileRoot; plan=@{file=$PlanPath;sha256=$PlanSha}; final=$Plan.final; status=$Status; removed=@($Removed.ToArray()); plannedRemovalCount=$Plan.remove.Count; preserveAllTextRecords=$true; retainedFileSnapshotsAtPlanPreparation=$Plan.keep; externalHostImagesNotTouched=$true; immutableNativeAssemblyNotModified=$true; failure=$Failure }
    if ($Removed.Count -gt 0) {
        Mark-Retired $Generation $actual
        $Generation['retentionLog']=$LogPath
        $Generation['sourcePolicy']='Historical image references are availability-qualified by retention-log.json; current runtime dependency is the final PNG.'
        Save-Json $GenerationPath $Generation
        Mark-Retired $Manifest $actual
        $Manifest['sourceRecordsHistoricalAfterRetention']=$true; $Manifest['retentionLog']=$LogPath
        $Manifest['runtimeDependencies']=@($Plan.final)
        $Manifest['sourcePolicy']='Only entries recorded as actually retired in retention-log.json are unavailable. Original native assembly and dated generation records are immutable history; all text evidence remains.'
        $Manifest['currentCandidateGeneration']=@{file=$GenerationPath;sha256=(Hash-File $GenerationPath)}
        Save-Json $ManifestPath $Manifest
    }
    $ledger['currentMetadata']=@(@{file=$GenerationPath;sha256=(Hash-File $GenerationPath)},@{file=$ManifestPath;sha256=(Hash-File $ManifestPath)})
    $ledger['historicalTextRecords']=@(@{file=(Join-Path $HistoryDir 'candidate.generation.before-retention.json');sha256=$Plan.currentCandidateGeneration.sha256},@{file=(Join-Path $HistoryDir 'manifest.before-retention.json');sha256=$Plan.finalManifest.sha256})
    Save-Json $LogPath $ledger
}
Save-ExecutionState 'executing_exact_reviewed_list' ''
try {
    foreach ($item in $Plan.remove) {
        $path = Assert-InsideTile $item.file
        if ((Hash-File $path) -ne $item.sha256 -or (Get-Item -LiteralPath $path).Length -ne $item.bytes) { throw "Target changed after preflight: $path" }
        Remove-Item -LiteralPath $path
        if (Test-Path -LiteralPath $path) { throw "Removal did not complete: $path" }
        $Removed.Add([ordered]@{file=$path;sha256=$item.sha256;bytes=$item.bytes;reason=$item.reason;retiredAfterExport=$true;sourceImageAvailable=$false;runtimeDependency=$false;retiredAt=[DateTime]::UtcNow.ToString('o')})
        Save-ExecutionState 'executing_exact_reviewed_list' ''
    }
    if ((Hash-File $Plan.final.file) -ne $Plan.final.sha256) { throw 'Final image changed unexpectedly.' }
    Save-ExecutionState 'retired_after_final_export_and_scoped_QA' ''
} catch {
    Save-ExecutionState 'stopped_after_error_no_automatic_retry' $_.Exception.Message
    throw
}
[PSCustomObject]@{status='retired_after_final_export_and_scoped_QA';removedCount=$Removed.Count;finalSha256=$Plan.final.sha256;ledger=$LogPath} | ConvertTo-Json

