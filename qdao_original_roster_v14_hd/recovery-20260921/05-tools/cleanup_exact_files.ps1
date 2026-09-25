param([ValidateSet('internal','external')][string]$Scope='internal')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath('D:\luyuan\wuxingqitan\image')
$taskRecovery=Join-Path $taskRoot 'qdao_original_roster_v14_hd\recovery-20260921'
$taskFinal=Join-Path $taskRecovery '05-delivery-preview\final'
$taskPlan=Get-Content -Raw -LiteralPath (Join-Path $taskRecovery '05-audit\CLEANUP-EXECUTION-MANIFEST.json') | ConvertFrom-Json
$taskManifestFile=Join-Path $taskFinal 'manifest.json'
if((Get-FileHash -LiteralPath $taskManifestFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskPlan.final_manifest_sha256){throw 'Final manifest changed'}
$taskFinalManifest=Get-Content -Raw -LiteralPath $taskManifestFile | ConvertFrom-Json
if(-not $taskFinalManifest.offline_accepted -or $taskFinalManifest.files.Count -ne 136){throw 'Final package not accepted/complete'}
foreach($taskFrame in $taskFinalManifest.files){
 $taskFramePath=Join-Path (Join-Path $taskFinal 'runtime') $taskFrame.path
 if((Get-FileHash -LiteralPath $taskFramePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskFrame.sha256){throw ('Final frame mismatch: '+$taskFrame.path)}
}
$taskEntries=@($taskPlan.$Scope)
$taskAllowed=if($Scope -eq 'internal'){$taskRoot+'\'}else{'C:\Users\Administrator\.codex\generated_images\'}
$taskVerified=@()
foreach($taskEntry in $taskEntries){
 $taskPath=[IO.Path]::GetFullPath($taskEntry.path)
 if(-not $taskPath.StartsWith($taskAllowed,[StringComparison]::OrdinalIgnoreCase)){throw ('Out of scope: '+$taskPath)}
 if($taskPath.StartsWith($taskFinal+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Attempt to delete final'}
 if([IO.Path]::GetExtension($taskPath).ToLowerInvariant() -notin @('.png','.gif','.webp','.jpg','.jpeg')){throw 'Only enumerated image files may be removed'}
 $taskItem=Get-Item -LiteralPath $taskPath
 if($taskItem.PSIsContainer -or ($taskItem.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Not a regular file'}
 if((Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskEntry.sha256){throw ('Source changed: '+$taskPath)}
 $taskVerified += $taskEntry
}
$taskDeleted=[Collections.Generic.List[object]]::new()
foreach($taskEntry in $taskVerified){
 Remove-Item -LiteralPath $taskEntry.path -Force
 if(Test-Path -LiteralPath $taskEntry.path){throw ('Delete failed: '+$taskEntry.path)}
 $taskDeleted.Add($taskEntry)
}
$taskResult=[ordered]@{character='05_celestial_musician_girl';scope=$Scope;completedAt=[DateTime]::UtcNow.ToString('o');deletedFiles=$taskDeleted.Count;deletedBytes=($taskDeleted | Measure-Object -Property bytes -Sum).Sum;directoriesDeleted=0;textRecordsDeleted=0;otherCharactersTouched=$false;finalManifestSha256=$taskPlan.final_manifest_sha256;files=$taskDeleted}
$taskResultPath=Join-Path $taskRecovery ('05-audit\CLEANUP-RESULT-'+$Scope+'.json')
[IO.File]::WriteAllText($taskResultPath,($taskResult|ConvertTo-Json -Depth 100),[Text.UTF8Encoding]::new($false))
[pscustomobject]$taskResult | Select-Object character,scope,deletedFiles,deletedBytes,directoriesDeleted,textRecordsDeleted | ConvertTo-Json
