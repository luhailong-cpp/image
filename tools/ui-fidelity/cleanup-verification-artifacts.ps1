param([switch]$Apply)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath('E:\work\image')
$groups=@(
 @('designs/social-ui-v1/fidelity-20261016/qa/baseline','designs/social-ui-v1/fidelity-20261016/qa/final',8),
 @('docs/ui-fidelity-20261016/native/attributes','designs/attribute-panels/fidelity-20261016/qa/native',10),
 @('docs/ui-fidelity-20261016/native/channels','designs/scene-select-ui-v1/fidelity-20261016/qa/native',22),
 @('docs/ui-fidelity-20261016/native/world-travel','designs/world-map-original-20260925/fidelity-20261016/qa/native',18),
 @('docs/ui-fidelity-20261016/native/jubaozhai','designs/jubaozhai-ui/fidelity-20261016/qa/native',20),
 @('designs/gameplay-ui/fidelity-20261016/qa/native','designs/gameplay-ui/fidelity-20261016/qa/post-final-polish',26),
 @('designs/gameplay-ui/fidelity-20261016/qa/post-visual-fixes','designs/gameplay-ui/fidelity-20261016/qa/post-final-polish',26)
)
$files=@();$replacementChecks=@()
foreach($group in $groups){
 $obsolete=[IO.Path]::GetFullPath((Join-Path $workspace $group[0]))
 $replacement=[IO.Path]::GetFullPath((Join-Path $workspace $group[1]))
 if(-not $obsolete.StartsWith($workspace+'\',[StringComparison]::OrdinalIgnoreCase)-or -not $replacement.StartsWith($workspace+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Cleanup path escapes the authorized image workspace'}
 if(-not(Test-Path -LiteralPath $obsolete)){continue}
 if((Get-Item -LiteralPath $obsolete).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Refuse cleanup through a reparse point'}
 $current=@(Get-ChildItem -LiteralPath $replacement -File -Filter '*.png')
 if($current.Count -lt $group[2]){throw "Current native screenshots incomplete: $replacement"}
 $replacementChecks+=[pscustomobject]@{directory=$replacement;actualCount=$current.Count;minimumCount=$group[2]}
 foreach($file in Get-ChildItem -LiteralPath $obsolete -File -Filter '*.png'){
  $resolved=[IO.Path]::GetFullPath($file.FullName)
  if(-not $resolved.StartsWith($obsolete+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected cleanup file location'}
  if($file.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Refuse cleanup of linked images'}
  $files+=[pscustomobject]@{path=$resolved;sha256=(Get-FileHash -LiteralPath $resolved).Hash.ToLowerInvariant();bytes=$file.Length;supersededBy=$replacement}
 }
}
if($Apply){foreach($file in $files){Remove-Item -LiteralPath $file.path}}
$report=[pscustomobject]@{checkedAtUtc=[DateTime]::UtcNow.ToString('O');status=$(if($Apply){'removed-superseded-native-screenshots'}else{'plan-only'});scope='Temporary native verification images only. Approved design art, final native evidence, production assets, source, generation records and text reports are retained.';removedCount=$(if($Apply){$files.Count}else{0});candidateCount=$files.Count;replacementChecks=$replacementChecks;files=$files}
$report|ConvertTo-Json -Depth 7|Set-Content -LiteralPath (Join-Path $workspace 'docs/ui-fidelity-20261016/obsolete-screenshot-cleanup.json') -Encoding utf8
Write-Output "UI_SCREENSHOT_CLEANUP apply=$Apply candidates=$($files.Count)"
