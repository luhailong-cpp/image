param([string]$Frame,[string]$Attempt,[string]$Source,[string]$ReviewNote)
$ErrorActionPreference='Stop'
$taskRoot='D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl'
if($Frame -notmatch '^(N|NE|SE|S|SW|W|NW)-\d\d$') {throw 'invalid frame'}
$direction,$index=$Frame.Split('-')
$dst=Join-Path $taskRoot ('staging/run/'+$direction+'/'+$index+'.png')
$prefix=$Frame+'-'+$Attempt
$req=Get-Content -Raw -LiteralPath (Join-Path $taskRoot ('provenance/run-other/'+$prefix+'.request.json')) | ConvertFrom-Json -AsHashtable
$refs=@()
foreach($ref in $req.referenced_image_paths) {$refs+=@{path=$ref;sha256=(Get-FileHash -LiteralPath $ref -Algorithm SHA256).Hash.ToLower()}}
$editTarget=$null
if(Test-Path -LiteralPath $dst) {
 $oldRec=Get-Content -Raw -LiteralPath ($dst+'.generation.json') | ConvertFrom-Json -AsHashtable
 $oldRec.disposition='superseded image removed after corrected image copied; text provenance retained'
 $archive='provenance/run-other/'+$Frame+'-prior-to-'+$Attempt+'.generation.json'
 $oldRec | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $taskRoot $archive) -Encoding utf8
 $editTarget=@{sha256=$oldRec.sha256;generationRecord=$archive;note='previous candidate replaced by targeted AI correction'}
}
New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
Copy-Item -LiteralPath $Source -Destination $dst -Force
Add-Type -AssemblyName System.Drawing
$im=[System.Drawing.Bitmap]::FromFile($dst)
$w=$im.Width;$h=$im.Height;$pixelFormat=$im.PixelFormat.ToString();$im.Dispose()
$record=[ordered]@{
file=('staging/run/'+$direction+'/'+$index+'.png');sha256=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLower()
generatedAt=[DateTimeOffset]::UtcNow.ToString('o');timeNote='工具未披露生成时间；成功回执后本机落盘时间。';width=$w;height=$h;format='PNG RGBA'
tool='image_gen.imagegen';route='builtin';configSnapshot=(Get-Content -Raw 'D:/work/image/config/image-generation.json' | ConvertFrom-Json)
submittedParameters=@{model=$null;quality=$null;transparent_background=$true;promptFile=('provenance/run-other/'+$prefix+'.prompt.txt');referenced_image_paths=$req.referenced_image_paths}
actualModel=$null;actualQuality=$null;unverifiedReason='宿主管理，工具未开放 model/quality 参数，且未披露实际型号或画质。'
evidence=@{receipt=('provenance/run-other/'+$prefix+'.receipt.txt');outputNativePath=$Source;toolResultFields=@('image_url','output_hint')}
prompt=('provenance/run-other/'+$prefix+'.prompt.txt');references=$refs;editTarget=$editTarget
review=@{static='candidate';notes=$ReviewNote;dynamic='pending'};destinationState='native candidate; parent exports 1024 fixed canvas'
}
$record | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath ($dst+'.generation.json') -Encoding utf8
[PSCustomObject]@{file=$record.file;sha256=$record.sha256;width=$w;height=$h;pixelFormat=$pixelFormat} | ConvertTo-Json

