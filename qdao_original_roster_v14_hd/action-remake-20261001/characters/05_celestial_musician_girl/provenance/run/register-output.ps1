param([string]$Id,[string]$HostPath,[string]$ReturnedAt,[string]$PoseNote)
$ErrorActionPreference='Stop'
$base='D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/05_celestial_musician_girl'
$direction=$Id.Substring(0,1)
$frame=$Id.Substring(1,2)
$version=$Id.Substring(4)
$destination=$base+'/staging/run/'+$direction+'/'+$frame+'-'+$version+'.native.png'
$provenance=$base+'/provenance/run/'+$Id
New-Item -ItemType Directory -Force -Path ($base+'/staging/run/'+$direction) | Out-Null
Copy-Item -LiteralPath $HostPath -Destination $destination
Add-Type -AssemblyName System.Drawing
$im=[System.Drawing.Bitmap]::new($destination)
$request=Get-Content -LiteralPath ($provenance+'.request.json') -Raw | ConvertFrom-Json
$refs=@()
foreach($p in $request.referenced_image_paths){$refs+=@{path=$p;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}}
$record=[ordered]@{
file=$destination;sha256=(Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant();generatedAt=$ReturnedAt;width=$im.Width;height=$im.Height;format='PNG';mode='RGBA';tool='image_gen.imagegen';route='builtin'
configSnapshot=(Get-Content -LiteralPath 'D:/work/image/config/image-generation.json' -Raw | ConvertFrom-Json)
submittedParameters=@{model=$null;quality=$null;request=($provenance+'.request.json')}
actualModel=$null;actualQuality=$null;unverifiedReason='宿主管理，工具未开放model/quality选择器且未返回型号质量'
evidence=@{receipt=($provenance+'.receipt.json');hostPath=$HostPath};prompt=($provenance+'.prompt.txt');references=$refs
visualReview=@{viewed=$true;status='candidate_requires_sequence_verification';identity='保留紫发莲冠与双手持琴';pose=$PoseNote;edges='头冠/发丝仍可见细杂色边，待多背景复核';finalVisualPassed=$false}
root=@{referenceCanvas=@(1024,1024);x=512;groundY=942;perFrameFit=$false}
}
$im.Dispose()
$record | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath ($provenance+'.generation.json') -Encoding utf8
[pscustomobject]@{file=$destination;sha256=$record.sha256;width=$record.width;height=$record.height} | ConvertTo-Json

