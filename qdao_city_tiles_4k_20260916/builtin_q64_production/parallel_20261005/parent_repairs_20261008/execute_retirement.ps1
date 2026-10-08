$ErrorActionPreference = 'Stop'
$repairRoot = (Resolve-Path -LiteralPath $PSScriptRoot).ProviderPath.TrimEnd('\')
$repairCurrent = (Resolve-Path -LiteralPath (Join-Path $repairRoot 'current')).ProviderPath.TrimEnd('\')
$proposalPath = Join-Path $repairRoot 'cleanup-proposal.json'
$proposal = Get-Content -LiteralPath $proposalPath -Raw | ConvertFrom-Json
$retirementPath = Join-Path $repairRoot 'retirement.json'
if (Test-Path -LiteralPath $retirementPath) { throw 'Retirement already recorded; do not rerun deletion.' }
$migrationPath = Join-Path $repairRoot 'migration-verification.json'
$migration = Get-Content -LiteralPath $migrationPath -Raw | ConvertFrom-Json
if ($migration.checks.Count -ne 5 -or $migration.imageFilesCreated -ne 0 -or $migration.branchPNGsRequiredAfterPreparation -ne $false) { throw 'Migration verification is incomplete.' }
if ((Get-FileHash -LiteralPath (Join-Path $repairRoot 'migration-manifest.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $migration.manifestSha256) { throw 'Migration manifest hash mismatch.' }
if ((Get-FileHash -LiteralPath (Join-Path $repairRoot 'rebase_current.py') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $migration.scriptSha256) { throw 'Migration script hash mismatch.' }
$pythonExe = 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonExe (Join-Path $repairRoot 'rebase_current.py')
if ($LASTEXITCODE -ne 0) { throw 'Retained-input reconstruction failed.' }
& $pythonExe (Join-Path $repairRoot 'scan_retirement_references.py')
if ($LASTEXITCODE -ne 0) { throw 'External reference scan found references or errors; nothing deleted.' }
$scan = Get-Content -LiteralPath (Join-Path $repairRoot 'external-reference-scan.json') -Raw | ConvertFrom-Json
if ($scan.matches.Count -ne 0 -or $scan.errors.Count -ne 0) { throw 'External reference scan is not clear.' }

$targets = @()
foreach ($item in $proposal.conditionalRetirement.items) {
    $resolved = (Resolve-Path -LiteralPath $item.file).ProviderPath
    if (-not $resolved.StartsWith($repairRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw ('Outside owned root: ' + $resolved) }
    if ($resolved.StartsWith($repairCurrent + '\', [StringComparison]::OrdinalIgnoreCase)) { throw ('Protected current: ' + $resolved) }
    if ([IO.Path]::GetExtension($resolved) -ne '.png') { throw ('Not PNG: ' + $resolved) }
    $cursor = Get-Item -LiteralPath $resolved
    while ($cursor.FullName -ne $repairRoot) {
        if (($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw ('Reparse point not allowed: ' + $cursor.FullName) }
        if ($cursor -is [IO.DirectoryInfo]) { $cursor = $cursor.Parent } else { $cursor = $cursor.Directory }
        if ($null -eq $cursor) { throw 'Cannot establish owned ancestor.' }
    }
    $hash = (Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant()
    $size = (Get-Item -LiteralPath $resolved).Length
    if ($hash -ne $item.sha256 -or $size -ne $item.bytes) { throw ('Target identity changed: ' + $resolved) }
    $targets += [PSCustomObject]@{ file=$resolved; sha256=$hash; bytes=$size; category=$item.category; branch=$item.branch }
}
if ($targets.Count -ne 47) { throw 'Unexpected proposal count.' }

$protectedPaths = @{}
Get-ChildItem -LiteralPath $repairCurrent -Recurse -File | ForEach-Object { $protectedPaths[$_.FullName] = 'current' }
$textExtensions = @('.json','.md','.py','.ps1','.txt','.yaml','.yml','.toml')
Get-ChildItem -LiteralPath $repairRoot -Recurse -File | Where-Object { $_.Extension -in $textExtensions } | ForEach-Object { $protectedPaths[$_.FullName] = 'retained_text' }
foreach ($item in $proposal.retainForNow.items) { $protectedPaths[$item.file] = 'migration_context_or_mask' }
foreach ($item in $proposal.protectedExternalSourceInputs) { $protectedPaths[$item.file] = 'external_source_not_owned' }
$protected = @()
foreach ($path in ($protectedPaths.Keys | Sort-Object)) {
    $protected += [PSCustomObject]@{ file=$path; sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant(); bytes=(Get-Item -LiteralPath $path).Length; purpose=$protectedPaths[$path] }
}
$receipt = [ordered]@{ status='deletion_in_progress'; startedAt=[DateTime]::UtcNow.ToString('o'); scope=$repairRoot;
    authority='User retention preference 2026-09-23; parent confirmed current files and exact QA transfer. Only conditionalRetirement PNGs in original proposal.';
    proposalSha256=(Get-FileHash -LiteralPath $proposalPath -Algorithm SHA256).Hash.ToLowerInvariant();
    externalScanAt=$scan.at; externalScanFileCount=$scan.scannedFileCount; externalMatches=0; externalNonRuntimeMatches=$scan.nonRuntimeMatches.Count;
    migrationVerification=$migrationPath; imageBackupCreated=$false; removed=@(); protectedBefore=$protected;
    currentPNGChanged=$false; childTaskModified=$false; outsideOwnedDirectoryDeleted=$false;
    historicalReferencePolicy='Removed PNG paths in unchanged provenance/QA records are historical identities, not live runtime dependencies. See per-file removed entries. Current and all historical text remain hash-identical. Use rebase_current.py; historical build/integration scripts are retired.' }
function Write-Receipt {
    $receipt | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $retirementPath -Encoding utf8
}
Write-Receipt
foreach ($item in $targets) {
    $resolved = (Resolve-Path -LiteralPath $item.file).ProviderPath
    if (-not $resolved.StartsWith($repairRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or $resolved.StartsWith($repairCurrent + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Path changed before deletion.' }
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw 'SHA changed before deletion.' }
    Remove-Item -LiteralPath $resolved -Force
    if (Test-Path -LiteralPath $resolved) { throw ('Deletion did not complete: ' + $resolved) }
    $receipt.removed += [PSCustomObject]@{ file=$resolved; sha256=$item.sha256; bytes=$item.bytes; category=$item.category; branch=$item.branch; deletedAt=[DateTime]::UtcNow.ToString('o'); imageRetained=$false; runtimeDependency=$false; historicalIdentityOnly=$true; replacedBy='current selected PNGs / exact current QA and migration-manifest.json' }
    Write-Receipt
}
$verified = @()
foreach ($item in $protected) {
    $actual = (Get-FileHash -LiteralPath $item.file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $item.sha256) { throw ('Protected file changed: ' + $item.file) }
    $verified += $item.file
}
$receipt.status = 'completed'
$receipt['completedAt'] = [DateTime]::UtcNow.ToString('o')
$receipt['deletedCount'] = $receipt.removed.Count
$receipt['deletedBytes'] = ($receipt.removed | Measure-Object -Property bytes -Sum).Sum
$receipt['protectedVerifiedUnchangedCount'] = $verified.Count
$receipt['allProtectedUnchanged'] = $true
Write-Receipt
$receipt | Select-Object status, deletedCount, deletedBytes, protectedVerifiedUnchangedCount, allProtectedUnchanged | ConvertTo-Json
