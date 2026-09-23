param([switch]$HostOnly)
$ErrorActionPreference='Stop'
$final06=[IO.Path]::GetFullPath($PSScriptRoot)
$root06=[IO.Path]::GetFullPath('D:\luyuan\wuxingqitan\image')
$plan06=Get-Content -LiteralPath (Join-Path $final06 'cleanup-plan.json') -Raw | ConvertFrom-Json
$verify06=Get-Content -LiteralPath (Join-Path $final06 'verification.json') -Raw | ConvertFrom-Json
$review06=Get-Content -LiteralPath (Join-Path $final06 'offline-review.json') -Raw | ConvertFrom-Json
if(-not $verify06.all_checks_passed -or -not $verify06.legacy_final_copies_ai_restored -or $review06.status -ne 'passed_offline'){throw 'Final restored delivery has not passed all required reviews.'}
$currentManifest06=(Get-FileHash -LiteralPath (Join-Path $final06 'manifest.json') -Algorithm SHA256).Hash.ToLowerInvariant()
if($currentManifest06 -ne $verify06.manifest_sha256 -or $currentManifest06 -ne $review06.manifest_sha256){throw 'Review does not bind the current manifest.'}
$removed06=@()
if($HostOnly){
 $hostRoot06=[IO.Path]::GetFullPath('C:\Users\Administrator\.codex\generated_images')
 foreach($item06 in $plan06.host_generated_image_files){
  $p06=[IO.Path]::GetFullPath($item06.path)
  if(-not $p06.StartsWith($hostRoot06+'\',[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetExtension($p06) -ne '.png'){throw "Host path out of allowed exact scope: $p06"}
  if(Test-Path -LiteralPath $p06){
   if(((Get-FileHash -LiteralPath $p06 -Algorithm SHA256).Hash.ToLowerInvariant()) -ne $item06.sha256){throw "Host source changed: $p06"}
  }
 }
 foreach($item06 in $plan06.host_generated_image_files){
  $p06=[IO.Path]::GetFullPath($item06.path)
  if(Test-Path -LiteralPath $p06){Remove-Item -LiteralPath $p06 -Force; $removed06+=$item06}
 }
 $report06=@{status='completed';scope='exact hash-matched 06 host-generated PNGs';removed_count=$removed06.Count;removed_bytes=($removed06 | Measure-Object -Property bytes -Sum).Sum;files=$removed06;completed_at_utc=[DateTime]::UtcNow.ToString('o')}
 $report06 | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $final06 'host-cleanup-result.json') -Encoding utf8
}else{
 $allowed06=@{}
 foreach($item06 in $plan06.files){$allowed06[[IO.Path]::GetFullPath($item06.path)]=$item06}
 foreach($dir06 in $plan06.directories){
  $p06=[IO.Path]::GetFullPath($dir06)
  if(-not $p06.StartsWith($root06+'\',[StringComparison]::OrdinalIgnoreCase) -or $final06.StartsWith($p06+'\',[StringComparison]::OrdinalIgnoreCase) -or $p06 -eq $root06 -or $p06 -eq $final06){throw "Directory outside scoped workspace or containing delivery: $p06"}
  if($p06 -notmatch '(\\06-[^\\]+$|\\06_thunder_caster_boy(\\(source|processing|review))?$)'){throw "Not a 06-only directory: $p06"}
  if(-not (Test-Path -LiteralPath $p06)){continue}
  $entries06=@(Get-Item -LiteralPath $p06)+@(Get-ChildItem -LiteralPath $p06 -Recurse -Force)
  foreach($entry06 in $entries06){
   if(($entry06.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw "Reparse point in deletion scope: $($entry06.FullName)"}
   if($entry06.PSIsContainer){continue}
   $entryPath06=[IO.Path]::GetFullPath($entry06.FullName)
   if(-not $allowed06.ContainsKey($entryPath06)){throw "Uninventoried new file, possible concurrent work: $entryPath06"}
   if(((Get-FileHash -LiteralPath $entryPath06 -Algorithm SHA256).Hash.ToLowerInvariant()) -ne $allowed06[$entryPath06].sha256){throw "File changed since final inventory: $entryPath06"}
  }
 }
 foreach($dir06 in $plan06.directories){
  $p06=[IO.Path]::GetFullPath($dir06)
  if(Test-Path -LiteralPath $p06){Remove-Item -LiteralPath $p06 -Recurse -Force; $removed06+=$p06}
 }
 $report06=@{status='completed';scope='06-only workspace production intermediates';removed_directory_count=$removed06.Count;removed_file_count=$plan06.file_count;removed_bytes=$plan06.bytes;directories=$removed06;original_24_512_files_preserved=$true;final_136_pngs_preserved=$true;completed_at_utc=[DateTime]::UtcNow.ToString('o')}
 $report06 | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $final06 'cleanup-result.json') -Encoding utf8
}
$report06 | Select-Object status,scope,removed_count,removed_file_count,removed_bytes | ConvertTo-Json
