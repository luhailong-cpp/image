param([Parameter(Mandatory=$true)][ValidateSet('workspace','host_generated_images')][string]$Scope)
$ErrorActionPreference='Stop'
$taskRec=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskExpected='D:\luyuan\wuxingqitan\image\qdao_original_roster_v14_hd\recovery-20260921'
if($taskRec -ne $taskExpected){throw 'Unexpected task root'}
$taskOut=Join-Path $taskRec '14-delivery-preview'
$taskPlan=Get-Content -Raw -LiteralPath (Join-Path $taskOut 'source-cleanup-plan.json') | ConvertFrom-Json
$taskQA=Get-Content -Raw -LiteralPath (Join-Path $taskOut 'qa-summary.json') | ConvertFrom-Json
if(!$taskQA.offlineApproved -or $taskQA.assets.Count -ne 136){throw 'Final offline acceptance is missing'}
foreach($taskAsset in $taskQA.assets){
 $taskAssetPath=Join-Path (Join-Path $taskOut 'assets') $taskAsset.file
 if((Get-FileHash -LiteralPath $taskAssetPath -Algorithm SHA256).Hash -ne $taskAsset.sha256){throw "Final asset changed: $taskAssetPath"}
}
$taskEvidence=Join-Path $taskOut 'provenance.json'
$taskProv=Get-Content -Raw -LiteralPath $taskEvidence | ConvertFrom-Json
if($taskProv.summary.selectedSlots -ne 136 -or $taskProv.summary.issues.Count -ne 0){throw 'Consolidated evidence is incomplete'}
$taskAllowed=@('14-generation','14-reference','14-work-E-SE','14-work-W-NW','14-work-NE','14-delivery-preview\review-temp') | ForEach-Object {[IO.Path]::GetFullPath((Join-Path $taskRec $_))+'\'}
$taskHostRoot='C:\Users\Administrator\.codex\generated_images\'
$taskCandidates=@($taskPlan.entries | Where-Object {$_.scope -eq $Scope})
foreach($taskItem in $taskCandidates){
 $taskPath=[IO.Path]::GetFullPath($taskItem.absolutePath)
 if($Scope -eq 'workspace'){
  $taskInside=$false
  foreach($taskDir in $taskAllowed){if($taskPath.StartsWith($taskDir,[StringComparison]::OrdinalIgnoreCase)){$taskInside=$true}}
  if(!$taskInside){throw "Outside named character temporary directories: $taskPath"}
 }else{
  if(!$taskPath.StartsWith($taskHostRoot,[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($taskPath) -notmatch '^exec-[0-9a-f-]+\.png$' -or !$taskItem.matchesAtLeastOneArchivedRawSHA256){throw "Unproven host original: $taskPath"}
 }
 if([IO.Path]::GetExtension($taskPath) -notin @('.png','.jpg','.jpeg')){throw 'Unexpected non-image candidate'}
 if(Test-Path -LiteralPath $taskPath){if((Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash -ne $taskItem.sha256){throw "Candidate changed; nothing deleted in this batch: $taskPath"}}
}
$taskLog=Join-Path $taskOut ('cleanup-'+$Scope+'.jsonl')
$taskRemoved=0;$taskAbsent=0
foreach($taskItem in $taskCandidates){
 $taskPath=[IO.Path]::GetFullPath($taskItem.absolutePath)
 if(Test-Path -LiteralPath $taskPath){Remove-Item -LiteralPath $taskPath -Force;$taskRemoved++;$taskResult='deleted'}else{$taskAbsent++;$taskResult='already-absent'}
 if(Test-Path -LiteralPath $taskPath){throw "Deletion failed: $taskPath"}
 [ordered]@{path=$taskPath;sha256=$taskItem.sha256;scope=$Scope;result=$taskResult;at=[DateTimeOffset]::UtcNow.ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath $taskLog -Encoding utf8
}
[ordered]@{scope=$Scope;removed=$taskRemoved;alreadyAbsent=$taskAbsent;preservedFinalAssets=136;provenanceSHA256=(Get-FileHash -LiteralPath $taskEvidence -Algorithm SHA256).Hash} | ConvertTo-Json -Compress
