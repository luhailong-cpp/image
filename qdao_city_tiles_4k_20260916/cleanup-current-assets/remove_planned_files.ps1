$ErrorActionPreference = 'Stop'
$CityCleanupDir = [System.IO.Path]::GetFullPath($PSScriptRoot)
$CityArtRoot = [System.IO.Path]::GetFullPath((Join-Path $CityCleanupDir '..'))
$CityExpectedRoot = [System.IO.Path]::GetFullPath('D:\luyuan\wuxingqitan\image\qdao_city_tiles_4k_20260916')
if ($CityArtRoot -ne $CityExpectedRoot) { throw 'Unexpected cleanup root' }
$CityPlanFile = Join-Path $CityCleanupDir 'cleanup-plan-final.json'
$CityPlanHash = (Get-FileHash -LiteralPath $CityPlanFile -Algorithm SHA256).Hash.ToLowerInvariant()
$CityPlan = Get-Content -LiteralPath $CityPlanFile -Raw | ConvertFrom-Json
if ([System.IO.Path]::GetFullPath($CityPlan.scopeRoot) -ne $CityArtRoot) { throw 'Plan root differs' }
$CityReceiptFile = Join-Path $CityCleanupDir 'deletion-receipt.json'
$CityLogFile = Join-Path $CityCleanupDir 'deleted-files.jsonl'
if ((Test-Path -LiteralPath $CityReceiptFile) -or (Test-Path -LiteralPath $CityLogFile)) { throw 'Cleanup already attempted; inspect receipt instead of repeating' }
$CityPrefix = $CityArtRoot + [System.IO.Path]::DirectorySeparatorChar
$CityCheckedDirectories = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
function Assert-CityFile([string]$CityValue, [string]$CityExpectedSha) {
    $CityFull = [System.IO.Path]::GetFullPath($CityValue)
    if (-not $CityFull.StartsWith($CityPrefix, [System.StringComparison]::OrdinalIgnoreCase)) { throw "Out-of-scope path: $CityFull" }
    $CityItem = Get-Item -LiteralPath $CityFull -Force
    if ($CityItem.PSIsContainer -or ($CityItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) { throw "Not a plain file: $CityFull" }
    $CityParent = $CityItem.Directory
    while ($CityParent -and $CityParent.FullName.StartsWith($CityArtRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        if ($CityCheckedDirectories.Add($CityParent.FullName) -and ($CityParent.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) { throw "Reparse directory: $($CityParent.FullName)" }
        $CityParent = $CityParent.Parent
    }
    $CityActual = (Get-FileHash -LiteralPath $CityFull -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($CityActual -ne $CityExpectedSha) { throw "File changed since plan: $CityFull" }
    return $CityFull
}
$CityKept = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($CityGuard in $CityPlan.guardInputs) { $null = Assert-CityFile $CityGuard.file $CityGuard.sha256 }
foreach ($CityEntry in $CityPlan.keep) {
    $CityPath = Assert-CityFile $CityEntry.file $CityEntry.sha256
    $null = $CityKept.Add($CityPath)
}
$CityAllowedExtensions = @('.png','.jpg','.jpeg','.webp','.tif','.tiff','.bmp','.gif','.npy','.npz','.zip')
foreach ($CityEntry in $CityPlan.delete) {
    $CityPath = [System.IO.Path]::GetFullPath($CityEntry.file)
    if (-not $CityPath.StartsWith($CityPrefix,[System.StringComparison]::OrdinalIgnoreCase)) { throw "Delete path outside root: $CityPath" }
    if ($CityKept.Contains($CityPath) -or [System.IO.Path]::GetExtension($CityPath).ToLowerInvariant() -notin $CityAllowedExtensions) { throw "Protected or unsupported delete path: $CityPath" }
}
$CityDeletedCount = 0
$CityDeletedBytes = [long]0
$CityFailure = $null
$CityStarted = [DateTime]::UtcNow.ToString('o')
$CityWriter = [System.IO.StreamWriter]::new($CityLogFile, $false, [System.Text.UTF8Encoding]::new($false))
try {
    foreach ($CityEntry in $CityPlan.delete) {
        $CityPath = Assert-CityFile $CityEntry.file $CityEntry.sha256
        Remove-Item -LiteralPath $CityPath -Force
        if (Test-Path -LiteralPath $CityPath) { throw "Deletion did not complete: $CityPath" }
        $CityWriter.WriteLine(($CityEntry | ConvertTo-Json -Compress -Depth 5))
        $CityWriter.Flush()
        $CityDeletedCount += 1
        $CityDeletedBytes += [long]$CityEntry.bytes
        if ($CityDeletedCount % 250 -eq 0) { Write-Output "Deleted $CityDeletedCount planned obsolete files" }
    }
} catch {
    $CityFailure = $_.Exception.Message
} finally {
    $CityWriter.Dispose()
    $CityReceipt = [ordered]@{
        schemaVersion = 1
        startedAtUtc = $CityStarted
        finishedAtUtc = [DateTime]::UtcNow.ToString('o')
        status = $(if ($CityFailure) { 'partial_failure' } else { 'completed' })
        authorization = 'Explicit user instruction to delete originals and rollback versions'
        scopeRoot = $CityArtRoot
        plan = $CityPlanFile
        planSha256 = $CityPlanHash
        deletedFiles = $CityDeletedCount
        deletedBytes = $CityDeletedBytes
        retainedFiles = $CityPlan.keep.Count
        noBackupCopiesCreated = $true
        metadataPreserved = $true
        error = $CityFailure
    }
    $CityReceipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $CityReceiptFile -Encoding utf8
    $CityReceipt | ConvertTo-Json -Compress -Depth 6
}
if ($CityFailure) { throw $CityFailure }
