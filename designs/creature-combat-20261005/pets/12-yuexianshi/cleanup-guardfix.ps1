param([switch]$Execute)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$validation = Get-Content -LiteralPath (Join-Path $taskRoot 'technical-validation.json') -Raw | ConvertFrom-Json
if ($validation.status -ne 'passed' -or $validation.presentFrames -ne 68) { throw '68 final frames must pass technical validation.' }
$plan = Get-Content -LiteralPath (Join-Path $taskRoot 'cleanup-guardfix-plan.json') -Raw | ConvertFrom-Json
$cacheRoot = [IO.Path]::GetFullPath('C:\Users\luyua\.codex\generated_images')
$inputRoot = [IO.Path]::GetFullPath((Join-Path $taskRoot 'repair-inputs'))
if ($plan.count -lt 20 -or $plan.count -gt 150) { throw 'Unexpected repair cleanup count.' }
$checked = @()
foreach ($entry in $plan.items) {
  $targetPath = [IO.Path]::GetFullPath($entry.path)
  $parentPath = [IO.Path]::GetDirectoryName($targetPath)
  if ([IO.Path]::GetExtension($targetPath) -ne '.png') { throw 'Only PNG pixels can be removed.' }
  if ($entry.kind -eq 'native') {
    if ([IO.Path]::GetDirectoryName($parentPath) -ne $cacheRoot -or [IO.Path]::GetFileName($targetPath) -notlike 'exec-*.png') { throw "Invalid native scope: $targetPath" }
  } elseif ($entry.kind -eq 'input') {
    if ($parentPath -ne $inputRoot) { throw "Invalid input scope: $targetPath" }
  } else { throw 'Unknown cleanup kind.' }
  if (-not (Test-Path -LiteralPath $targetPath)) { throw "Missing planned image: $targetPath" }
  if ((Get-Item -LiteralPath $targetPath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse targets are forbidden.' }
  if ((Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "Hash changed: $targetPath" }
  foreach ($record in $entry.records) {
    $recordPath = [IO.Path]::GetFullPath((Join-Path $taskRoot $record))
    if (-not $recordPath.StartsWith($taskRoot + [IO.Path]::DirectorySeparatorChar) -or -not (Test-Path -LiteralPath $recordPath)) { throw 'Missing or unscoped provenance.' }
  }
  $checked += $entry
}
if (-not $Execute) { Write-Output "Verified exact scope, hashes and provenance for $($checked.Count) repair images; no deletion."; exit }
foreach ($entry in $checked) { Remove-Item -LiteralPath $entry.path -Force }
$report = [pscustomobject]@{completedAt=[DateTime]::UtcNow.ToString('o');deletedCount=$checked.Count;items=$checked;recursiveDeletion=$false;preserved='Final 68 PNGs, current original identity/style references, final previews and all provenance text'}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskRoot 'cleanup-guardfix.json') -Encoding utf8
Write-Output "Removed $($checked.Count) exact recorded repair images; final assets and provenance retained."
