param([switch]$Execute)
$ErrorActionPreference='Stop'
$expansionRoot=[IO.Path]::GetFullPath($PSScriptRoot)
$selectedRoot=[IO.Path]::GetFullPath((Join-Path $expansionRoot 'child-selected'))
$selected=Get-Content -LiteralPath (Join-Path $selectedRoot 'current-selection.json') -Raw | ConvertFrom-Json
foreach($entry in $selected.candidates){
  if(-not(Test-Path -LiteralPath $entry.file -PathType Leaf)){throw "Selected asset missing: $($entry.file)"}
  if((Get-FileHash -LiteralPath $entry.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw 'Selected asset hash mismatch'}
}
$retired=@(Get-ChildItem -LiteralPath $expansionRoot -Recurse -File | Where-Object { $_.Extension.ToLowerInvariant() -in @('.png','.jpg','.jpeg','.webp','.npy','.npz') -and -not $_.FullName.StartsWith($selectedRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) })
$entries=@($retired | ForEach-Object { [ordered]@{file=$_.FullName;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant();bytes=$_.Length} })
$protected=@(Get-ChildItem -LiteralPath $selectedRoot -Recurse -File | ForEach-Object { [ordered]@{file=$_.FullName;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()} })
$plan=[ordered]@{createdAt=[DateTimeOffset]::UtcNow.ToString('o');root=$expansionRoot;reason='Child completed same coordinate with better accepted geometry; parent alternatives not selected. User2026-09-23 authorizes deleting unused originals/rejects/intermediates after current output and references verified.';selectedFile=(Join-Path $selectedRoot 'current-selection.json');status='planned';retiredCount=$entries.Count;retired=$entries;protected=$protected;outsideFilesModified=$false;modelPromptReceiptTextPreserved=$true}
$receipt=Join-Path $expansionRoot 'retirement.json'
$plan|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $receipt -Encoding utf8
if(-not $Execute){Write-Output "Planned $($entries.Count) unselected image/data removals; $($protected.Count) selected files protected.";exit}
foreach($entry in $entries){
  $resolvedPath=[IO.Path]::GetFullPath($entry.file)
  if(-not $resolvedPath.StartsWith($expansionRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Removal target outside EXP'}
  if($resolvedPath.StartsWith($selectedRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Removal target is protected'}
  if((Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw 'Removal target changed'}
}
Remove-Item -LiteralPath @($entries | ForEach-Object {$_.file}) -Force
foreach($entry in $protected){if((Get-FileHash -LiteralPath $entry.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw 'Protected file changed'}}
$plan.status='executed';$plan.completedAt=[DateTimeOffset]::UtcNow.ToString('o');$plan.protectedHashesUnchanged=$true
$plan|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $receipt -Encoding utf8
Write-Output "Retired $($entries.Count) unselected image/data files. Protected selected files unchanged."
