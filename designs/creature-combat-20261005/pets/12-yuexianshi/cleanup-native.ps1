param([switch]$Execute)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$validation = Get-Content -LiteralPath (Join-Path $taskRoot 'technical-validation.json') -Raw | ConvertFrom-Json
if ($validation.status -ne 'passed' -or $validation.presentFrames -ne 68) { throw 'Final technical validation must pass for all68 before cleanup.' }
$plan = Get-Content -LiteralPath (Join-Path $taskRoot 'cleanup-plan.json') -Raw | ConvertFrom-Json
$cacheBase = [IO.Path]::GetFullPath('C:\Users\luyua\.codex\generated_images')
$allowedIds = @('01a10bb6-4e59-76c1-94bb-a58739163335','01a10bb8-6c88-7051-bbfb-ef639e3e935c','01a10bb8-c107-7471-9102-b8d378d2f0a6','01a10bb9-18c6-78d1-805d-30c6562481ee')
if ($plan.count -lt 68 -or $plan.count -gt 128) { throw 'Unexpected source-image count.' }
$checkedItems = @()
foreach ($entry in $plan.items) {
  $targetPath = [IO.Path]::GetFullPath($entry.path)
  $parentPath = [IO.Path]::GetDirectoryName($targetPath)
  $parentId = [IO.Path]::GetFileName($parentPath)
  if ([IO.Path]::GetDirectoryName($parentPath) -ne $cacheBase -or $parentId -notin $allowedIds) { throw "Unscoped source: $targetPath" }
  if ([IO.Path]::GetExtension($targetPath) -ne '.png' -or [IO.Path]::GetFileName($targetPath) -notlike 'exec-*.png') { throw 'Only recorded tool PNG outputs can be removed.' }
  if (Test-Path -LiteralPath $targetPath) {
    $sourceItem = Get-Item -LiteralPath $targetPath
    if ($sourceItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point is not allowed.' }
    if ((Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "Source hash changed: $targetPath" }
  }
  $checkedItems += [pscustomobject]@{path=$targetPath;sha256=$entry.sha256;records=$entry.records;existed=(Test-Path -LiteralPath $targetPath)}
}
if (-not $Execute) { Write-Output "Verified exact scope and hashes for $($checkedItems.Count) native PNG files; no deletion performed."; exit }
foreach ($entry in $checkedItems) {
  if ($entry.existed) { Remove-Item -LiteralPath $entry.path -Force }
}
$report = [pscustomobject]@{completedAt=[DateTime]::UtcNow.ToString('o');policy='User-confirmed final-assets-only retention from2026-09-23';deletedCount=@($checkedItems | Where-Object existed).Count;items=$checkedItems;preserved='68 runtime PNGs, previews, source/receipt text, original Image identity/style references';recursiveDeletion=$false}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskRoot 'cleanup.json') -Encoding utf8
Write-Output "Deleted $($report.deletedCount) exact recorded native PNG files; no directories or cross-task references removed."
