param([Parameter(Mandatory=$true)][string]$Id,[Parameter(Mandatory=$true)][ValidateSet('prepare','success','failure')][string]$Phase,[string]$Source)
$ErrorActionPreference = 'Stop'
$recordDir = Split-Path -Parent $PSCommandPath
$characterDir = Split-Path -Parent (Split-Path -Parent $recordDir)
$recordPath = Join-Path $recordDir ($Id + '.generation.json')
$clockNow = [TimeZoneInfo]::ConvertTime([DateTimeOffset]::UtcNow,[TimeZoneInfo]::FindSystemTimeZoneById('Eastern Standard Time')).ToString('o')
if($Phase -eq 'prepare'){
 $request = Get-Content -Raw (Join-Path $recordDir ($Id+'.request.json')) | ConvertFrom-Json
 $parts = $Id.Split('-')
 $record = [ordered]@{slot=('attack/'+$parts[1]+'/'+$parts[2]);attemptedAt=$clockNow;timezone='America/New_York';generatedAt=$null;tool='image_gen.imagegen';route='builtin';configSnapshot=(Get-Content -Raw 'D:/work/image/config/image-generation.json' | ConvertFrom-Json);submittedParameters=@{model=$null;quality=$null};actualModel=$null;actualQuality=$null;unverifiedReason='宿主管理，工具无 model/quality 选择器；实际型号与质量未确认。';references=@();request=('provenance/attack/'+$Id+'.request.json');prompt=('provenance/attack/'+$Id+'.prompt.txt');status='request-prepared';root=@{x=512;y=942;canvas=1024;pivot=@(0.5,0.08)}}
 $roles=@('严格方向、侧面相机与全局人物比例参考','原始角色身份、服装和持琴细节','已确认主要画法参考')
 $i=0;foreach($ref in $request.referenced_image_paths){$record.references += [ordered]@{file=$ref;sha256=(Get-FileHash -LiteralPath $ref -Algorithm SHA256).Hash.ToLower();role=$roles[$i]};$i++}
}else{
 $record=Get-Content -Raw $recordPath | ConvertFrom-Json
 $record | Add-Member -Force -NotePropertyName completedAt -NotePropertyValue $clockNow
 if($Phase -eq 'success'){
  $parts=$Id.Split('-');$destinationRelative='staging/attack/'+$parts[1]+'-'+$parts[2]+'-'+$parts[3]+'.png'
  $destination=Join-Path $characterDir $destinationRelative
  Copy-Item -LiteralPath $Source -Destination $destination
  $hint=Get-Content -Raw (Join-Path $recordDir ($Id+'.output-hint.json')) | ConvertFrom-Json
  [ordered]@{image_url=('data:image/png;base64,'+[Convert]::ToBase64String([System.IO.File]::ReadAllBytes($destination)));output_hint=$hint.output_hint} | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $recordDir ($Id+'.result.json')) -Encoding utf8NoBOM
  Add-Type -AssemblyName System.Drawing
  $img=[System.Drawing.Image]::FromFile($destination)
  $record.generatedAt=$clockNow;$record.status='generated-pending-visual-review'
  $record | Add-Member -Force -NotePropertyName file -NotePropertyValue $destinationRelative
  $record | Add-Member -Force -NotePropertyName sha256 -NotePropertyValue (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower()
  $record | Add-Member -Force -NotePropertyName native -NotePropertyValue @{width=$img.Width;height=$img.Height;format='PNG';pixelFormat=$img.PixelFormat.ToString()}
  $record | Add-Member -Force -NotePropertyName hostOutput -NotePropertyValue $Source
  $record | Add-Member -Force -NotePropertyName evidence -NotePropertyValue @{receipt=('provenance/attack/'+$Id+'.result.json');receiptPreservation='Tool-returned image_url reconstructed from tool-saved PNG bytes; output_hint retained exactly.';reportedModel=$null;reportedQuality=$null}
  $img.Dispose()
 }else{
  $record.status='failed-no-image-generated'
  $record | Add-Member -Force -NotePropertyName failure -NotePropertyValue ((Get-Content -Raw (Join-Path $recordDir ($Id+'.result.json')) | ConvertFrom-Json).error)
  $record | Add-Member -Force -NotePropertyName evidence -NotePropertyValue @{receipt=('provenance/attack/'+$Id+'.result.json')}
 }
}
$record | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $recordPath -Encoding utf8NoBOM
[ordered]@{id=$Id;status=$record.status;file=$record.file;sha256=$record.sha256;native=$record.native} | ConvertTo-Json -Depth 4

