$ErrorActionPreference = 'Stop'
$tilePath = 'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel_20261005\lanxian_day\r08_c10'
$tileResolved = (Resolve-Path -LiteralPath $tilePath).Path
if ($tileResolved -ne $tilePath) { throw 'Unexpected tile root resolution' }
$tilePrefix = $tileResolved.TrimEnd('\') + '\'
$selectedPath = Join-Path $tileResolved 'selected'
$selectedPrefix = $selectedPath + '\'
$corePath = Join-Path $selectedPath 'core4096.png'
$extendedPath = Join-Path $selectedPath 'extended4326.png'
if ((Get-FileHash -LiteralPath $corePath -Algorithm SHA256).Hash.ToLower() -ne 'bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f') { throw 'Selected core hash mismatch' }
if ((Get-FileHash -LiteralPath $extendedPath -Algorithm SHA256).Hash.ToLower() -ne '2d4552bb7fa01baeb6fc0ac759360a50a08b9a90f65b285536a88947356e9e6e') { throw 'Selected extended hash mismatch' }
$delivery = Get-Content -Raw -LiteralPath (Join-Path $selectedPath 'delivery.manifest.json') | ConvertFrom-Json
if (-not $delivery.qualifiedComplete4KCandidate) { throw 'Selection checks did not qualify candidate' }
$activePaths = @((Join-Path $tileResolved 'west-repair\v3\core4096.png'), (Join-Path $tileResolved 'west-repair\v3\extended4326.png'))
$reparseItems = @(Get-ChildItem -LiteralPath $tileResolved -Recurse -Force | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 })
if ($reparseItems.Count -ne 0) { throw 'Reparse point in tile; cleanup stopped' }
$deleteRecords = @()
$keepRecords = @()
foreach ($file in @(Get-ChildItem -LiteralPath $tileResolved -Recurse -File -Filter '*.png')) {
    $resolved = (Resolve-Path -LiteralPath $file.FullName).Path
    if (-not $resolved.StartsWith($tilePrefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Out-of-scope path: $resolved" }
    $selectedKeep = $resolved.StartsWith($selectedPrefix,[StringComparison]::OrdinalIgnoreCase)
    $activeKeep = $activePaths -contains $resolved
    $maskKeep = $file.Name -match '(?i)(mask|weight|changed-pixels)'
    $record = [ordered]@{ file=$resolved; sha256=(Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLower(); bytes=$file.Length }
    if ($selectedKeep -or $activeKeep -or $maskKeep) {
        $record['reason'] = if ($selectedKeep) {'All selected artifacts retained'} elseif ($activeKeep) {'Active r09 source dependency; exact WESTv3 image retained'} else {'Technical support/alpha/change/taper mask retained'}
        $keepRecords += [pscustomobject]$record
    } else {
        $record['reason'] = 'Superseded original, trial, processing image, guide or QA board; selected final verified and provenance records retained under user retention preference'
        $deleteRecords += [pscustomobject]$record
    }
}
$recordSnapshot = @()
foreach ($file in @(Get-ChildItem -LiteralPath $tileResolved -Recurse -File | Where-Object { $_.Extension -ne '.png' -and -not $_.FullName.StartsWith($selectedPrefix,[StringComparison]::OrdinalIgnoreCase) })) {
    $recordSnapshot += [pscustomobject]@{ file=$file.FullName; sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLower(); bytes=$file.Length }
}
$manifestPath = Join-Path $selectedPath 'cleanup.manifest.json'
$audit = [ordered]@{
    schemaVersion=1; createdAtUtc=[DateTime]::UtcNow.ToString('o'); mode='Authorized in-tile PNG cleanup after verified selection'; state='planned'; resolvedAllowedRoot=$tileResolved;
    authorization='Parent explicitly instructed cleanup under user2026-09-23 retention preference; preserve selected all, technical masks, WESTv3 active core/extended, all JSON/TXT/PY/NPY/NPZ';
    safety=[ordered]@{allAbsoluteTargetsResolvedInsideExactTile=$true;reparsePointsPresent=$false;recursiveDirectoryDeletion=$false;outsideTileDeletion=$false;otherTileDeletion=$false};
    selectedCoreSha256='bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f'; selectedExtendedSha256='2d4552bb7fa01baeb6fc0ac759360a50a08b9a90f65b285536a88947356e9e6e';
    deletedFiles=$deleteRecords; retainedPngFiles=$keepRecords; preservedNonPngFilesOutsideSelected=$recordSnapshot;
    plannedDeleteCount=$deleteRecords.Count;plannedDeleteBytes=($deleteRecords | Measure-Object -Property bytes -Sum).Sum; deletedCount=0
}
$audit | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $manifestPath -Encoding utf8
$deletedCount = 0
foreach ($record in $deleteRecords) {
    $target = (Resolve-Path -LiteralPath $record.file).Path
    if (-not $target.StartsWith($tilePrefix,[StringComparison]::OrdinalIgnoreCase) -or $target.StartsWith($selectedPrefix,[StringComparison]::OrdinalIgnoreCase) -or $activePaths -contains $target) { throw 'Deletion scope changed after plan' }
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLower() -ne $record.sha256) { throw "Target changed after plan: $target" }
    Remove-Item -LiteralPath $target -Force
    $deletedCount++
}
foreach ($record in $keepRecords + $recordSnapshot) {
    if (-not (Test-Path -LiteralPath $record.file -PathType Leaf)) { throw "Preserved artifact missing: $($record.file)" }
    if ((Get-FileHash -LiteralPath $record.file -Algorithm SHA256).Hash.ToLower() -ne $record.sha256) { throw "Preserved artifact changed: $($record.file)" }
}
$remaining = @(Get-ChildItem -LiteralPath $tileResolved -Recurse -File -Filter '*.png')
if ($remaining.Count -ne $keepRecords.Count) { throw 'Unexpected remaining PNG set' }
$audit.state='completed';$audit.deletedCount=$deletedCount;$audit['completedAtUtc']=[DateTime]::UtcNow.ToString('o');$audit['remainingPngCount']=$remaining.Count;$audit['retainedAllHashesVerified']=$true;$audit['preservedNonPngCount']=$recordSnapshot.Count
$audit | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $manifestPath -Encoding utf8
[pscustomobject]@{state=$audit.state;deletedCount=$deletedCount;deletedBytes=$audit.plannedDeleteBytes;remainingPngCount=$remaining.Count;preservedNonPngCount=$recordSnapshot.Count;manifest=$manifestPath} | ConvertTo-Json
