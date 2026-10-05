$ErrorActionPreference='Stop'
$baseDir=[IO.Path]::GetFullPath('D:\work\image\designs\creature-combat-20261005\pets\03-shuangtuan')
$sourceDir=[IO.Path]::GetFullPath((Join-Path $baseDir 'source\attack'))
$allowedPrefix=$sourceDir.TrimEnd('\')+'\'
$recordDir=Join-Path $baseDir 'records\attack'
$sourceItems=@(Get-ChildItem -LiteralPath $sourceDir -File -Recurse)
$records=@()
$deletedItems=@()
$finalSha=@()
$retention='Native source removed after final 1024 RGBA, prompt, receipt, SHA and active references were verified, under AGENTS.md 2026-09-23 retention policy. Generation evidence and native SHA retained; default host output and shared identity/style references untouched.'
if($sourceItems.Count -ne 24){throw "Expected exactly 24 source files, found $($sourceItems.Count)"}
foreach($entry in $sourceItems){
  $resolved=[IO.Path]::GetFullPath((Resolve-Path -LiteralPath $entry.FullName).Path)
  if(-not $resolved.StartsWith($allowedPrefix,[StringComparison]::OrdinalIgnoreCase)){throw "Out-of-scope deletion target: $resolved"}
  if($entry.Extension -ne '.png'){throw "Non-PNG source: $resolved"}
  if(($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw "Reparse point: $resolved"}
}
foreach($direction in @('E','W')){
  foreach($index in 1..12){
    $frame='{0:D2}' -f $index
    $recordPath=Join-Path $recordDir "$direction\$frame.generation.json"
    $record=Get-Content -Raw -LiteralPath $recordPath | ConvertFrom-Json
    $finalPath=Join-Path $baseDir $record.file
    $expectedFinal=Join-Path $baseDir "runtime\attack\$direction\$frame.png"
    if([IO.Path]::GetFullPath($finalPath) -ne [IO.Path]::GetFullPath($expectedFinal)){throw "Unexpected final path"}
    $hash=(Get-FileHash -LiteralPath $finalPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if($hash -ne $record.sha256){throw "Final SHA mismatch: $finalPath"}
    if($record.width -ne 1024 -or $record.height -ne 1024 -or $record.mode -ne 'RGBA'){throw "Invalid final dimensions/mode"}
    $finalSha+=$hash
    $promptPath=Join-Path $baseDir $record.prompt
    if(-not (Test-Path -LiteralPath $promptPath -PathType Leaf)){throw "Missing prompt: $promptPath"}
    foreach($evidence in $record.evidence){
      if(-not (Test-Path -LiteralPath (Join-Path $baseDir $evidence) -PathType Leaf)){throw "Missing evidence: $evidence"}
    }
    $receiptPath=Join-Path $recordDir "$direction\$frame.receipt.json"
    $receipt=Get-Content -Raw -LiteralPath $receiptPath | ConvertFrom-Json
    if(-not $receipt.output_hint -or $receipt.returnedKeys -notcontains 'image_url'){throw "Incomplete image receipt"}
    foreach($reference in $record.references){
      $refPath=$reference.path
      if(-not [IO.Path]::IsPathRooted($refPath)){$refPath=Join-Path $baseDir $refPath}
      if(-not (Test-Path -LiteralPath $refPath -PathType Leaf)){throw "Missing active reference: $refPath"}
    }
    $nativePath=[IO.Path]::GetFullPath((Join-Path $baseDir $record.native.file))
    if(-not $nativePath.StartsWith($allowedPrefix,[StringComparison]::OrdinalIgnoreCase)){throw "Native out of deletion scope"}
    $nativeHash=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if($nativeHash -ne $record.native.sha256 -or $nativeHash -ne $record.derivedFrom.sha256){throw "Native SHA mismatch"}
    $records+=[pscustomobject]@{path=$recordPath;record=$record;nativePath=$nativePath;nativeHash=$nativeHash}
    $deletedItems+=[pscustomobject]@{file=$record.native.file;absolutePath=$nativePath;sha256=$nativeHash;bytes=(Get-Item -LiteralPath $nativePath).Length;final=$record.file;finalSha256=$hash}
  }
}
if(@($finalSha|Select-Object -Unique).Count -ne 24){throw 'Duplicate final SHA'}
if(@($deletedItems.absolutePath|Select-Object -Unique).Count -ne 24){throw 'Duplicate native target'}
foreach($entry in $sourceItems){
  if($deletedItems.absolutePath -notcontains $entry.FullName){throw "Unaccounted source file: $($entry.FullName)"}
}
foreach($entry in $records){
  foreach($property in @('native','derivedFrom')){
    $obj=$entry.record.$property
    $obj|Add-Member -NotePropertyName deleted -NotePropertyValue $true -Force
    $obj|Add-Member -NotePropertyName retention -NotePropertyValue $retention -Force
    $obj|Add-Member -NotePropertyName cleanupRecord -NotePropertyValue 'qa/attack/cleanup.json' -Force
  }
  foreach($reference in $entry.record.references){
    $refPath=$reference.path
    if(-not [IO.Path]::IsPathRooted($refPath)){$refPath=Join-Path $baseDir $refPath}
    $refFull=[IO.Path]::GetFullPath($refPath)
    $match=@($deletedItems|Where-Object {$_.absolutePath -eq $refFull})
    if($match.Count -gt 0){
      $reference|Add-Member -NotePropertyName sha256 -NotePropertyValue $match[0].sha256 -Force
      $reference|Add-Member -NotePropertyName deleted -NotePropertyValue $true -Force
      $reference|Add-Member -NotePropertyName retention -NotePropertyValue $retention -Force
    }
  }
  $entry.record|ConvertTo-Json -Depth 100|Set-Content -LiteralPath $entry.path -Encoding utf8
}
foreach($item in $deletedItems){Remove-Item -LiteralPath $item.absolutePath}
$remaining=@(Get-ChildItem -LiteralPath $sourceDir -File -Recurse)
if($remaining.Count -ne 0){throw 'Source files remain after cleanup'}
foreach($entry in $records){
  $record=Get-Content -Raw -LiteralPath $entry.path | ConvertFrom-Json
  $hash=(Get-FileHash -LiteralPath (Join-Path $baseDir $record.file) -Algorithm SHA256).Hash.ToLowerInvariant()
  if($hash -ne $record.sha256){throw 'Final modified during cleanup'}
}
$cleanup=[ordered]@{
  status='complete'
  completedAt=[DateTimeOffset]::UtcNow.ToString('o')
  scope=$sourceDir
  validation=[ordered]@{finals=24;uniqueFinalSha256=24;generationRecords=24;prompts=24;receipts=24;sourceHashesMatched=$true;activeReferencesVerified=$true;finalsUnchangedAfterDeletion=$true;remainingSourceImages=0}
  policy=$retention
  removed=$deletedItems
  removedCount=$deletedItems.Count
  removedBytes=($deletedItems|Measure-Object -Property bytes -Sum).Sum
  externalOrDefaultHostFilesDeleted=$false
  runtimeFilesDeleted=$false
}
$cleanup|ConvertTo-Json -Depth 100|Set-Content -LiteralPath (Join-Path $baseDir 'qa\attack\cleanup.json') -Encoding utf8
[pscustomobject]@{status=$cleanup.status;removed=$cleanup.removedCount;bytes=$cleanup.removedBytes;remainingSources=$remaining.Count;finals=24;records=24}|ConvertTo-Json

