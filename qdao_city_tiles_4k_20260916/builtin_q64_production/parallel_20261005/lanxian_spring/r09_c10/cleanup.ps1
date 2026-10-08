$ErrorActionPreference = 'Stop'
$tileRoot = [System.IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\')
$expectedRoot = [System.IO.Path]::GetFullPath('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_spring/r09_c10').TrimEnd('\')
if ($tileRoot -ne $expectedRoot) { throw 'Unexpected cleanup scope' }
$review = Get-Content -Raw -LiteralPath (Join-Path $tileRoot 'qa-north-independent/final-review.json') | ConvertFrom-Json
if ($review.status -ne 'pass_within_reviewed_scope') { throw 'Independent final review has not passed' }
$manifest = Get-Content -Raw -LiteralPath (Join-Path $tileRoot 'selected/delivery.manifest.json') | ConvertFrom-Json
if (-not $manifest.qualifiedComplete4KCandidate) { throw 'Final delivery not qualified' }
$keep = @('selected\core4096.png','selected\extended4326.png','selected\preview1254.png','selected\surface-mask4326.png','masks\southwest-alpha1254.png','masks\northwest-alpha1254.png')
$preserved = @()
foreach ($relative in $keep) {
 $target = [System.IO.Path]::GetFullPath((Join-Path $tileRoot $relative))
 if (-not $target.StartsWith($tileRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)) { throw 'Keep path outside tile' }
 $preserved += [ordered]@{file=$target;sha256=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLower();bytes=(Get-Item -LiteralPath $target).Length}
}
$toDelete = @()
foreach ($item in (Get-ChildItem -LiteralPath $tileRoot -Filter '*.png' -File -Recurse)) {
 $resolved = [System.IO.Path]::GetFullPath($item.FullName)
 if (-not $resolved.StartsWith($tileRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)) { throw 'Delete path outside tile' }
 $relative = $resolved.Substring($tileRoot.Length+1)
 if ($keep -notcontains $relative) { $toDelete += [ordered]@{file=$resolved;sha256=(Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLower();bytes=$item.Length;reason='Superseded source snapshot, native edit input/output, composite or QA crop; final exported and checked, complete text evidence retained.'} }
}
$record = [ordered]@{createdAtUtc=[DateTime]::UtcNow.ToString('o');scope=$tileRoot;validatedAbsoluteScope=$true;deletedPngCount=$toDelete.Count;deleted=$toDelete;preserved=$preserved;externalDayNorthAndGeneratedImagesUntouched=$true;historicalPathsAreProvenanceNotLiveDependencies=$true;allTextRecordsPreserved=$true}
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $tileRoot 'selected/cleanup.manifest.json') -Encoding utf8
foreach ($item in $toDelete) { Remove-Item -LiteralPath $item.file -Force }
foreach ($item in $preserved) { if ((Get-FileHash -LiteralPath $item.file -Algorithm SHA256).Hash.ToLower() -ne $item.sha256) { throw 'Preserved artifact changed' } }
[ordered]@{deletedPngCount=$toDelete.Count;preservedPngCount=$preserved.Count;preservedHashesVerified=$true} | ConvertTo-Json
