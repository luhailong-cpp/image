$ErrorActionPreference = 'Stop'
$scopeRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path.TrimEnd('\')
$scopePrefix = $scopeRoot + '\'
$planPath = Join-Path $scopeRoot 'cleanup-plan.json'
$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if ([IO.Path]::GetFullPath($plan.scopeRoot).TrimEnd('\') -ne $scopeRoot) { throw 'Scope mismatch' }
$keepPaths = @{}
foreach ($entry in $plan.mustKeep) {
    $full = [IO.Path]::GetFullPath($entry.path)
    if (-not $full.StartsWith($scopePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw "Keep outside scope: $full" }
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw "Required file missing: $full" }
    if ((Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "Required file changed: $full" }
    $keepPaths[$full.ToLowerInvariant()] = $true
}
$verified = @()
foreach ($entry in $plan.proposedDelete) {
    $full = [IO.Path]::GetFullPath($entry.path)
    if (-not $full.StartsWith($scopePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw "Delete outside scope: $full" }
    if ($full -match '[\\/]vendor[\\/]') { throw 'Vendor protected' }
    if ($keepPaths.ContainsKey($full.ToLowerInvariant())) { throw 'Keep/delete overlap' }
    if ([IO.Path]::GetExtension($full) -notin @('.png','.npy')) { throw 'Only reviewed pixel/processing files may be removed' }
    $item = Get-Item -LiteralPath $full
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "Not a regular file: $full" }
    if ($item.Length -ne $entry.bytes) { throw "Size changed: $full" }
    if ((Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "Hash changed: $full" }
    $verified += $entry
}
$deleted = @()
foreach ($entry in $verified) {
    Remove-Item -LiteralPath $entry.path
    if (Test-Path -LiteralPath $entry.path) { throw "Removal did not complete: $($entry.path)" }
    $deleted += $entry
}
foreach ($entry in $plan.currentCandidates) {
    if ((Get-FileHash -LiteralPath $entry.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw 'Current candidate changed during cleanup' }
}
$receipt = [ordered]@{
    schemaVersion = 1
    completedAtUtc = [DateTime]::UtcNow.ToString('o')
    authorization = 'User AGENTS.md material-retention instruction confirmed 2026-09-23; raw, rejected and intermediate images may be removed after current artifacts and references are verified.'
    scopeRoot = $scopeRoot
    planSha256 = (Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant()
    status = 'completed'
    deletedFiles = $deleted.Count
    deletedBytes = ($deleted | Measure-Object -Property bytes -Sum).Sum
    currentCandidatesVerifiedAfter = $plan.currentCandidates
    currentCandidateCount = 4
    allPlannedKeepFilesVerifiedBefore = $plan.mustKeep.Count
    nativeOriginalsDeleted = @($deleted | Where-Object category -eq 'integrated_native_original').Count
    sourceRecordsPreserved = $true
    sourcePixelsAvailableForReplay = $false
    imageBackupsCreated = $false
    outsideScopeModified = $false
    deleted = $deleted
}
$receipt | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $scopeRoot 'cleanup-receipt.json') -Encoding utf8
[pscustomobject]$receipt | Select-Object status,deletedFiles,deletedBytes,currentCandidateCount,nativeOriginalsDeleted | ConvertTo-Json
