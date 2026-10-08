# Prepared only. Run after root has selected the reviewed candidate and explicitly
# authorized execution. Never deletes outside this exact tile or recurses a delete.
$ErrorActionPreference = 'Stop'
$tilePath = 'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel_20261005\lanxian_day\r09_c09'
$pythonPath = 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$tileResolved = (Resolve-Path -LiteralPath $tilePath).Path
if (-not $tileResolved.Equals($tilePath,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected tile root resolution' }
$tilePrefix = $tileResolved.TrimEnd('\') + '\'
$selectedPath = Join-Path $tileResolved 'selected'
$selectedPrefix = $selectedPath + '\'
$manifestPath = Join-Path $selectedPath 'cleanup.manifest.json'
$verificationPath = Join-Path $selectedPath 'cleanup-verification.json'
$retiredPath = Join-Path $selectedPath 'retired-source-paths.json'
$helperPath = Join-Path $selectedPath 'verify_cleanup.py'
foreach ($reserved in @($manifestPath,$verificationPath,$retiredPath)) {
    if (Test-Path -LiteralPath $reserved) { throw "Refusing to overwrite existing cleanup evidence: $reserved" }
}
function Assert-NoReparseAncestors([string]$path) {
    $entry = Get-Item -LiteralPath $path -Force
    while ($null -ne $entry) {
        if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse point: $($entry.FullName)" }
        $entry = if ($entry.PSIsContainer) { $entry.Parent } else { $entry.Directory }
    }
}
Assert-NoReparseAncestors $tileResolved
function Get-SafeTileFiles {
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($tileResolved)
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($entry in @(Get-ChildItem -LiteralPath $directory -Force)) {
            if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse point in tile: $($entry.FullName)" }
            $resolved = (Resolve-Path -LiteralPath $entry.FullName).Path
            if (-not $resolved.StartsWith($tilePrefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Out-of-scope item: $resolved" }
            if ($entry.PSIsContainer) { $pending.Push($resolved) } else { $entry }
        }
    }
}
function Read-Preflight {
    $raw = & $pythonPath $helperPath --stage preflight
    if ($LASTEXITCODE -ne 0) { throw 'Selection/root QA/consumer preflight failed' }
    return ($raw | ConvertFrom-Json)
}
$allFiles = @(Get-SafeTileFiles)
$preflight = Read-Preflight
$activePaths = @($preflight.activeReferences | ForEach-Object { (Resolve-Path -LiteralPath $_.file).Path })
$deleteRecords = @()
$keepRecords = @()
$recordSnapshot = @()
foreach ($file in $allFiles) {
    $resolved = (Resolve-Path -LiteralPath $file.FullName).Path
    $record = [ordered]@{file=$resolved;sha256=(Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLower();bytes=$file.Length}
    if ($file.Extension -ine '.png') { $recordSnapshot += [pscustomobject]$record; continue }
    $selectedKeep = $resolved.StartsWith($selectedPrefix,[StringComparison]::OrdinalIgnoreCase)
    $activeKeep = $activePaths -contains $resolved
    $maskKeep = $file.Name -match '(?i)(mask|weight|changed-pixels)' -or $file.DirectoryName -match '(?i)[\\/](masks?|weights?)[\\/]?'
    if ($selectedKeep -or $activeKeep -or $maskKeep) {
        $record['reason'] = if ($selectedKeep) {'All selected files retained'} elseif ($activeKeep) {'Current unfinished consumer input retained'} else {'Technical mask/weight/change-support image retained'}
        $keepRecords += [pscustomobject]$record
    } else {
        $record['reason'] = 'Superseded in-tile native/reference/guide/candidate/QA PNG; selected final verified, original textual provenance retained'
        $deleteRecords += [pscustomobject]$record
    }
}
$audit = [ordered]@{
    schemaVersion=2;createdAtUtc=[DateTime]::UtcNow.ToString('o');state='planned';resolvedAllowedRoot=$tileResolved;
    authorization='Authorized project retention preference: keep selected art, technical masks, actual current references, and all nonPNG records. Execute only after root selects and authorizes this prepared script.';
    safety=[ordered]@{resolvedExactTileOnly=$true;reparsePointsPresent=$false;recursiveDeletion=$false;outsideTileDeletion=$false;hostGeneratedImageDeletion=$false};
    preflight=$preflight;activeProtectedPaths=$activePaths;deletedFiles=$deleteRecords;retainedPngFiles=$keepRecords;preservedNonPngFiles=$recordSnapshot;
    plannedDeleteCount=$deleteRecords.Count;plannedDeleteBytes=($deleteRecords | Measure-Object -Property bytes -Sum).Sum;deletedCount=0;
    historicalReferencePolicy='Retired original paths and SHA256 remain provenance, not live-file claims. All existing nonPNG files including delivery and QA remain byte-identical. See retired-source-paths.json and cleanup-verification.json after completion.'
}
$audit | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $manifestPath -Encoding utf8
try {
    # Recheck live dependencies and selected art immediately before any deletion.
    $latest = Read-Preflight
    if ($latest.delivery.sha256 -ne $preflight.delivery.sha256 -or $latest.rootQa.sha256 -ne $preflight.rootQa.sha256) { throw 'Selection changed after cleanup plan' }
    $latestActive = @($latest.activeReferences | ForEach-Object { (Resolve-Path -LiteralPath $_.file).Path })
    foreach ($record in $deleteRecords) {
        if ($latestActive -contains $record.file) { throw "New current dependency after plan: $($record.file)" }
    }
    foreach ($record in $deleteRecords) {
        $target = (Resolve-Path -LiteralPath $record.file).Path
        Assert-NoReparseAncestors $target
        if (-not $target.StartsWith($tilePrefix,[StringComparison]::OrdinalIgnoreCase) -or $target.StartsWith($selectedPrefix,[StringComparison]::OrdinalIgnoreCase) -or $latestActive -contains $target -or [IO.Path]::GetExtension($target) -ine '.png') { throw "Deletion scope changed: $target" }
        if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLower() -ne $record.sha256) { throw "Target changed after plan: $target" }
        Remove-Item -LiteralPath $target -Force
        $audit.deletedCount++
    }
    foreach ($record in $keepRecords + $recordSnapshot) {
        if (-not (Test-Path -LiteralPath $record.file -PathType Leaf)) { throw "Preserved artifact missing: $($record.file)" }
        if ((Get-FileHash -LiteralPath $record.file -Algorithm SHA256).Hash.ToLower() -ne $record.sha256) { throw "Preserved artifact changed: $($record.file)" }
    }
    $remaining = @(Get-SafeTileFiles | Where-Object { $_.Extension -ieq '.png' })
    if ($remaining.Count -ne $keepRecords.Count) { throw 'Unexpected remaining PNG set' }
    $audit.state='completed'
    $audit['completedAtUtc']=[DateTime]::UtcNow.ToString('o')
    $audit['remainingPngCount']=$remaining.Count
    $audit['preservedNonPngCount']=$recordSnapshot.Count
    $audit['allProtectedHashesVerified']=$true
    $audit | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $manifestPath -Encoding utf8
    $retired = [ordered]@{schemaVersion=1;tile='r09_c09';recordedAtUtc=[DateTime]::UtcNow.ToString('o');cleanupManifest=$manifestPath;interpretation='Each listed PNG path is retired and absent after verified selection. Its original hash remains historical source evidence; retained original text records are not promises that these images still exist.';files=@($deleteRecords | ForEach-Object {[pscustomobject]@{file=$_.file;sha256=$_.sha256;bytes=$_.bytes;existsAfterCleanup=$false;status='retired_after_verified_selection'}})}
    $retired | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $retiredPath -Encoding utf8
    $verificationRaw = & $pythonPath $helperPath --stage post
    if ($LASTEXITCODE -ne 0) { throw 'Independent post-cleanup verification failed' }
    $verificationRaw | Set-Content -LiteralPath $verificationPath -Encoding utf8
    [pscustomobject]@{state=$audit.state;deletedCount=$audit.deletedCount;deletedBytes=$audit.plannedDeleteBytes;retainedPngCount=$remaining.Count;preservedNonPngCount=$recordSnapshot.Count;manifest=$manifestPath;verification=$verificationPath} | ConvertTo-Json
} catch {
    $audit.state='failed_or_partial_cleanup'
    $audit['failureAtUtc']=[DateTime]::UtcNow.ToString('o')
    $audit['error']=$_.Exception.Message
    $audit | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $manifestPath -Encoding utf8
    throw
}
