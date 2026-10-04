$taskRoot='D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl'
$oldPath=Join-Path $taskRoot 'staging/run/W/09.png'
$oldRec=Get-Content -Raw -LiteralPath ($oldPath+'.generation.json') | ConvertFrom-Json
$oldRec.disposition='superseded image removed after v2 copied; metadata retained'
$oldRec | ConvertTo-Json -Depth 15 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $taskRoot 'provenance/run-other/W-09-v1.generation.json')
$req=Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'provenance/run-other/W-09-retry2.request.json') | ConvertFrom-Json
$refRecords=@()
foreach($ref in $req.referenced_image_paths) {$refRecords+=@{path=$ref;sha256=(Get-FileHash -LiteralPath $ref -Algorithm SHA256).Hash.ToLower()}}
Copy-Item -LiteralPath 'C:/Users/luyua/.codex/generated_images/01a0fd04-2aeb-7e22-828d-c5d3ce3ef143/exec-b6ff0548-a157-4bad-a788-0907270ab8be.png' -Destination $oldPath -Force
$oldRec.sha256=(Get-FileHash -LiteralPath $oldPath -Algorithm SHA256).Hash.ToLower()
$oldRec.generatedAt=[DateTimeOffset]::UtcNow.ToString('o')
$oldRec.prompt='provenance/run-other/W-09-retry2.prompt.txt'
$oldRec.submittedParameters.promptFile=$oldRec.prompt
$oldRec.submittedParameters.referenced_image_paths=$req.referenced_image_paths
$oldRec.references=$refRecords
$oldRec.evidence.receipt='provenance/run-other/W-09-retry2.receipt.txt'
$oldRec.evidence.outputNativePath='C:/Users/luyua/.codex/generated_images/01a0fd04-2aeb-7e22-828d-c5d3ce3ef143/exec-b6ff0548-a157-4bad-a788-0907270ab8be.png'
$oldRec.review.notes='修正后前景白袖向前覆盖胸腹，后景手臂向后；近腿向后、远腿向前，反向配合成立；身份/双刀静态可读，完整序列及动态尚待验收。'
$oldRec.disposition='selected current unique native candidate'
$oldRec | ConvertTo-Json -Depth 15 | Set-Content -Encoding utf8 -LiteralPath ($oldPath+'.generation.json')
$oldRec | Select-Object file,sha256,generatedAt,width,height | ConvertTo-Json

