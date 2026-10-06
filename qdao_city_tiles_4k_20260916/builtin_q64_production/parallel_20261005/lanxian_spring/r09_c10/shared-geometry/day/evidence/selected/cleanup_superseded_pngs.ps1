$ErrorActionPreference = 'Stop'
$tilePath = 'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel_20261005\lanxian_day\r09_c10'
$tileResolved = (Resolve-Path -LiteralPath $tilePath).Path
if ($tileResolved -ne $tilePath) { throw 'Unexpected tile root resolution' }
$tilePrefix = $tileResolved.TrimEnd('\') + '\'
$selectedPath = Join-Path $tileResolved 'selected'
$selectedPrefix = $selectedPath + '\'
$corePath = Join-Path $selectedPath 'core4096.png'
$extendedPath = Join-Path $selectedPath 'extended4326.png'
if ((Get-FileHash -LiteralPath $corePath -Algorithm SHA256).Hash.ToLower() -ne '0cefa2ece52b708f6b7021bfa878d466451cc1a0fd337cc9679754e949686c8b') { throw 'Selected core hash mismatch' }
if ((Get-FileHash -LiteralPath $extendedPath -Algorithm SHA256).Hash.ToLower() -ne '9f4279c1fec0ff91aa62fcb21e2fcb3e78ca021266732ed6096adb9338e341f5') { throw 'Selected extended hash mismatch' }
$delivery = Get-Content -Raw -LiteralPath (Join-Path $selectedPath 'delivery.manifest.json') | ConvertFrom-Json
if (-not $delivery.qualifiedComplete4KCandidate) { throw 'Selection checks did not qualify candidate' }
$consumers = Get-Content -Raw -LiteralPath (Join-Path $selectedPath 'external-consumer-audit.json') | ConvertFrom-Json
$activePaths = @($consumers.references | Where-Object { $_.exists } | ForEach-Object { (Resolve-Path -LiteralPath $_.file).Path })
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
        $record['reason'] = if ($selectedKeep) {'Selected game/preview artifact retained'} elseif ($activeKeep) {'Existing external consumer record references this exactPNG; retained'} else {'Existing technical support/alpha/change/taper mask retained'}
        $keepRecords += [pscustomobject]$record
    } else {
        $record['reason'] = 'Superseded native, candidate, regional reference, guide or QA PNG; selected byte-identical final verified and text provenance retained under user retention preference'
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
    authorization='Parent explicitly instructed r09_c10 cleanup under user2026-09-23 retention preference; keep selected all, existing external-consumer PNG, existing masks and every nonPNG record/data file';
    safety=[ordered]@{allAbsoluteTargetsResolvedInsideExactTile=$true;reparsePointsPresent=$false;recursiveDirectoryDeletion=$false;outsideTileDeletion=$false;r08C10WESTv3Deletion=$false};
    selectedCoreSha256='0cefa2ece52b708f6b7021bfa878d466451cc1a0fd337cc9679754e949686c8b'; selectedExtendedSha256='9f4279c1fec0ff91aa62fcb21e2fcb3e78ca021266732ed6096adb9338e341f5';
    externalProtectedPaths=$activePaths;deletedFiles=$deleteRecords;retainedPngFiles=$keepRecords;preservedNonPngFilesOutsideSelected=$recordSnapshot;
    plannedDeleteCount=$deleteRecords.Count;plannedDeleteBytes=($deleteRecords | Measure-Object -Property bytes -Sum).Sum;deletedCount=0
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
