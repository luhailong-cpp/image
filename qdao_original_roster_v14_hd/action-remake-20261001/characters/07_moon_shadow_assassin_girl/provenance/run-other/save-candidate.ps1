param([string]$Frame,[string]$Source,[string]$ReviewNote)
$ErrorActionPreference='Stop'
$taskRoot='D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl'
if ($Frame -notmatch '^(N|NE|SE|S|SW|W|NW)-\d\d$') { throw 'invalid run slot' }
$direction,$index=$Frame.Split('-')
$dst=Join-Path $taskRoot ('staging/run/'+$direction+'/'+$index+'.png')
New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
if(Test-Path -LiteralPath $dst) { throw 'existing candidate: do not overwrite' }
Copy-Item -LiteralPath $Source -Destination $dst
Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile($dst)
$size=@{width=$img.Width;height=$img.Height;format=$img.PixelFormat.ToString()}
$img.Dispose()
$req=Get-Content -Raw -LiteralPath (Join-Path $taskRoot ('provenance/run-other/'+$Frame+'.request.json')) | ConvertFrom-Json
$refRecords=@()
foreach($ref in $req.referenced_image_paths) { $refRecords += @{path=$ref;sha256=(Get-FileHash -LiteralPath $ref -Algorithm SHA256).Hash.ToLower()} }
$record=[ordered]@{
file=('staging/run/'+$direction+'/'+$index+'.png')
sha256=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLower()
generatedAt=[DateTimeOffset]::UtcNow.ToString('o')
timeNote='工具未披露生成时间；此为回执成功后本地落盘时间。'
width=$size.width;height=$size.height;format='PNG RGBA'
tool='image_gen.imagegen';route='builtin'
configSnapshot=(Get-Content -Raw -LiteralPath 'D:/work/image/config/image-generation.json' | ConvertFrom-Json)
submittedParameters=@{model=$null;quality=$null;transparent_background=$req.transparent_background;referenced_image_paths=$req.referenced_image_paths;promptFile=('provenance/run-other/'+$Frame+'.prompt.txt')}
actualModel=$null;actualQuality=$null
unverifiedReason='宿主管理，工具未开放 model/quality 参数，且未披露实际型号或画质。'
evidence=@{receipt=('provenance/run-other/'+$Frame+'.receipt.txt');outputNativePath=$Source;toolResultFields=@('image_url','output_hint')}
prompt=('provenance/run-other/'+$Frame+'.prompt.txt')
references=$refRecords
review=@{static='candidate';notes=$ReviewNote;dynamic='pending'}
destinationState='native candidate; parent exports 1024 fixed canvas'
}
$record | ConvertTo-Json -Depth 15 | Set-Content -Encoding utf8 -LiteralPath ($dst+'.generation.json')
[PSCustomObject]@{file=$record.file;sha256=$record.sha256;width=$record.width;height=$record.height;generatedAt=$record.generatedAt} | ConvertTo-Json

