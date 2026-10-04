$ErrorActionPreference='Stop'
$base='D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl/staging/direction-alignment-20261004'
$count=0
foreach($direction in @('SW','NE')){
 $dir=Join-Path $base "run-$direction"
 foreach($recordFile in Get-ChildItem -LiteralPath $dir -Filter '*.png.generation.json'){
  $record=Get-Content -Raw -LiteralPath $recordFile.FullName | ConvertFrom-Json
  $stem=$recordFile.Name -replace '\.png\.generation\.json$',''
  $req=Get-Content -Raw -LiteralPath (Join-Path $dir "$stem.request.json") | ConvertFrom-Json
  $refs=@()
  $i=0
  foreach($p in $req.parameters.referenced_image_paths){
   $role=if($i -eq 0){'edit_target_original_Moon_Shadow_frame'}elseif($p -match '09_bamboo_archer_girl'){'direction_projection_reference_only_same_direction_phase'}elseif($p -match 'designs[/\\]jubaozhai-ui'){'approved_primary_painted_style_reference'}else{'Moon_Shadow_identity_direction_continuity_reference_only'}
   $refs+=@{path=$p;role=$role;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower()}
   $i++
  }
  $record.references=$refs
  $editSource=@{path=$refs[0].path;sha256=$refs[0].sha256;generationRecord=($refs[0].path+'.generation.json');role=$refs[0].role}
  $record | Add-Member -NotePropertyName editSource -NotePropertyValue $editSource -Force
  $record | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $recordFile.FullName -Encoding utf8
  $count++
 }
}
[pscustomobject]@{normalizedRecords=$count;directions=@('SW','NE')} | ConvertTo-Json -Compress

