$ErrorActionPreference = 'Stop'
$tileScope = [System.IO.Path]::GetFullPath($PSScriptRoot)
$planFile = Join-Path $tileScope 'cleanup-plan.json'
$plan = Get-Content -LiteralPath $planFile -Raw | ConvertFrom-Json
$selectedFile = Join-Path $tileScope 'selected-v2/delivery.manifest.json'
$selected = Get-Content -LiteralPath $selectedFile -Raw | ConvertFrom-Json
if (-not $selected.qualifiedComplete4KCandidate) { throw 'Selected local qualification missing' }
$coreOutput = $selected.outputs.'core4096.png'
if ((Get-FileHash -LiteralPath $coreOutput.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $coreOutput.sha256) { throw 'Final selected hash mismatch' }
$approvedPaths = @()
foreach ($entry in $plan.deleteAfterVerifiedCombinedSelection) {
    $resolvedPath = [System.IO.Path]::GetFullPath($entry.path)
    if (-not $resolvedPath.StartsWith($tileScope + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) { throw "Outside task: $resolvedPath" }
    if ([System.IO.Path]::GetExtension($resolvedPath) -ne '.png') { throw 'Only listed PNGs permitted' }
    if ($entry.referenceStatus.currentCompositionInput) { throw "Active dependency: $resolvedPath" }
    if (@($entry.referenceStatus.activeReferencesFound).Count -ne 0) { throw "Active references: $resolvedPath" }
    if ((Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "Changed source: $resolvedPath" }
    $approvedPaths += [pscustomobject]@{ path=$resolvedPath; sha256=$entry.sha256; reason=$entry.reason; metadataRetained=$true }
}
foreach ($entry in $approvedPaths) { Remove-Item -LiteralPath $entry.path -Force }
$report = [pscustomobject]@{ completedAtUtc=[DateTime]::UtcNow.ToString('o'); scope=$tileScope; deletedPngCount=$approvedPaths.Count; deleted=$approvedPaths; sourcePlan=$planFile; verifiedSelected=$coreOutput; historicalImageReferencesIntentionallyUnavailable=$true; imageBackupsCreated=$false; metadataRemoved=$false }
$report | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath (Join-Path $tileScope 'cleanup-executed.json') -Encoding utf8
Write-Output "Deleted $($approvedPaths.Count) superseded PNGs; generation and provenance records retained."
