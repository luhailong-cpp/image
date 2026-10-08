# Run only after the parent reviews this exact plan and sets parentApprovedForExecution=true.
$ErrorActionPreference = 'Stop'
$planPath = Join-Path $PSScriptRoot 'cleanup-plan.json'
$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if ($plan.parentApprovedForExecution -ne $true) { throw 'Cleanup plan has not been reviewed for execution.' }
$scope = (Resolve-Path -LiteralPath $plan.allowedAbsoluteDirectory).Path.TrimEnd('\')
$expected = (Resolve-Path -LiteralPath $PSScriptRoot).Path.TrimEnd('\')
if ($scope -cne $expected) { throw 'Cleanup scope must be this exact tile folder.' }
$prefix = $scope + '\'
$manifest = $plan.selectedManifest
if ((Get-FileHash -LiteralPath $manifest.file -Algorithm SHA256).Hash.ToLowerInvariant() -cne $manifest.sha256) { throw 'Selected manifest changed.' }
foreach ($item in @($plan.preserve) + @($plan.preserveTechnicalFields)) {
    $resolved = (Resolve-Path -LiteralPath $item.file).Path
    if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Preserved path escaped tile.' }
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -cne $item.sha256) { throw "Retained image changed: $resolved" }
}
$targets = @()
foreach ($item in $plan.delete) {
    $resolved = (Resolve-Path -LiteralPath $item.file).Path
    if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Delete path escaped tile.' }
    if ((Get-Item -LiteralPath $resolved).PSIsContainer) { throw 'Directories cannot be deleted.' }
    if ([IO.Path]::GetExtension($resolved).ToLowerInvariant() -eq '.npz') {
        $oldFieldPrefix = (Join-Path $scope 'assembly_bounded_v1') + '\'
        if (-not $resolved.StartsWith($oldFieldPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Only superseded bounded_v1 NPZ fields can be deleted.' }
    } elseif ([IO.Path]::GetExtension($resolved).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.webp','.tif','.tiff')) { throw 'Only listed rasters or obsolete bounded_v1 NPZ can be deleted.' }
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -cne $item.sha256) { throw "Delete target changed: $resolved" }
    $targets += [pscustomobject]@{file=$resolved;sha256=$item.sha256}
}
# All targets were resolved, bounded and hash checked before the first removal.
$removed = @()
foreach ($item in $targets) {
    Remove-Item -LiteralPath $item.file
    if (Test-Path -LiteralPath $item.file) { throw "Delete failed: $($item.file)" }
    $removed += $item
}
foreach ($item in @($plan.preserve) + @($plan.preserveTechnicalFields)) {
    if ((Get-FileHash -LiteralPath $item.file -Algorithm SHA256).Hash.ToLowerInvariant() -cne $item.sha256) { throw "Post-cleanup retained image changed: $($item.file)" }
}
[pscustomobject]@{schemaVersion=1;completedAtUtc=[DateTime]::UtcNow.ToString('o');status='executed';deletedCount=$removed.Count;deleted=$removed;preservedCount=$plan.preserve.Count;allPreservedHashesVerified=$true;textRecordsUntouched=$true;outsideTileUntouched=$true;planSha256=(Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant()} | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'cleanup-executed.json') -Encoding utf8
