$ErrorActionPreference = 'Stop'
$taskManifest = Join-Path $PSScriptRoot 'cleanup_20261005/manifest.json'
$taskData = Get-Content -LiteralPath $taskManifest -Raw | ConvertFrom-Json
$taskBoundary = [IO.Path]::GetFullPath($taskData.rootBoundary).TrimEnd('\') + '\'
$taskManifestHash = (Get-FileHash -LiteralPath $taskManifest -Algorithm SHA256).Hash.ToLowerInvariant()
$taskTextBefore = @()
foreach ($taskScope in $taskData.strictScope) {
    $taskTextBefore += Get-ChildItem -LiteralPath $taskScope -Recurse -File | Where-Object { $_.Extension -in '.json','.txt','.md','.py','.ps1' } | ForEach-Object { [PSCustomObject]@{file=$_.FullName;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()} }
}
if ((Get-FileHash -LiteralPath $taskData.parentCurrentWork.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskData.parentCurrentWork.sha256) { throw 'Parent checkpoint changed; rebuild plan before deletion.' }
if ((Get-FileHash -LiteralPath $taskData.currentSelection.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskData.currentSelection.sha256) { throw 'Current six-tile selection changed.' }
foreach ($taskEntry in @($taskData.currentArtifactsProtected) + @($taskData.protectedReferencedSources)) {
    if ((Get-FileHash -LiteralPath $taskEntry.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskEntry.sha256) { throw "Protected artifact changed: $($taskEntry.file)" }
}
foreach ($taskEntry in $taskData.deleteCandidates) {
    $taskTarget = [IO.Path]::GetFullPath($taskEntry.absolutePath)
    if (-not $taskTarget.StartsWith($taskBoundary,[StringComparison]::OrdinalIgnoreCase)) { throw "Outside boundary: $taskTarget" }
    $taskAllowed = $false
    foreach ($taskScope in $taskData.strictScope) { if ($taskTarget.StartsWith(([IO.Path]::GetFullPath($taskScope).TrimEnd('\')+'\'),[StringComparison]::OrdinalIgnoreCase)) { $taskAllowed=$true } }
    if (-not $taskAllowed -or [IO.Path]::GetExtension($taskTarget) -ne '.png') { throw "Outside explicit PNG scope: $taskTarget" }
    if ((Get-FileHash -LiteralPath $taskTarget -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskEntry.sha256) { throw "Deletion candidate changed: $taskTarget" }
}
$taskDeleted=@()
foreach ($taskEntry in $taskData.deleteCandidates) {
    Remove-Item -LiteralPath $taskEntry.absolutePath -Force
    if (Test-Path -LiteralPath $taskEntry.absolutePath) { throw "Deletion verification failed: $($taskEntry.absolutePath)" }
    $taskDeleted += [PSCustomObject]@{file=$taskEntry.absolutePath;sha256=$taskEntry.sha256;bytes=$taskEntry.bytes;existsAfter=$false}
}
$taskKept=@()
foreach ($taskEntry in @($taskData.currentArtifactsProtected) + @($taskData.protectedReferencedSources)) {
    $taskVerifiedHash=(Get-FileHash -LiteralPath $taskEntry.file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($taskVerifiedHash -ne $taskEntry.sha256) { throw "Protected artifact mismatch after deletion: $($taskEntry.file)" }
    $taskKept += [PSCustomObject]@{file=$taskEntry.file;sha256=$taskVerifiedHash;verifiedUnchanged=$true}
}
foreach ($taskEntry in $taskTextBefore) { if ((Get-FileHash -LiteralPath $taskEntry.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskEntry.sha256) { throw "Text evidence changed: $($taskEntry.file)" } }
$taskReceipt=[ordered]@{completedAtUtc=[DateTime]::UtcNow.ToString('o');status='completed_verified';manifest=$taskManifest;manifestSha256=$taskManifestHash;deletedCount=$taskDeleted.Count;deletedBytes=($taskDeleted|Measure-Object -Property bytes -Sum).Sum;deleted=$taskDeleted;protectedArtifactsVerified=$taskKept;retainedReferencedSources=$taskData.protectedReferencedSources;textEvidencePreservedCount=$taskTextBefore.Count;allTextEvidenceUnchanged=$true;parentPointerModified=$false;parallelDirectoriesModified=$false;hostCacheModified=$false;imageBackupsCreated=$false;scope='Only superseded adjacent-qa PNGs and explicitly rejected size-probe PNGs. All other c08/c07/c09 directories untouched.';historicalReferenceMeaning='Per-image source records and historical inventory snapshots are retained as evidence of earlier pixels. Listed deleted images no longer exist; preserved hashes do not imply current readability.'}
$taskReceiptPath=Join-Path $PSScriptRoot 'cleanup_20261005/receipt.json'
$taskReceipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $taskReceiptPath -Encoding utf8
[PSCustomObject]@{receipt=$taskReceiptPath;deletedCount=$taskDeleted.Count;deletedBytes=$taskReceipt.deletedBytes;protectedVerified=$taskKept.Count;textEvidencePreserved=$taskTextBefore.Count} | ConvertTo-Json
