param([string]$Stem,[string]$Source,[string]$Status,[string]$Notes)
$ErrorActionPreference='Stop'
$out=$PSScriptRoot
Copy-Item -LiteralPath $Source -Destination "$out/$Stem.png"
$b=[IO.File]::ReadAllBytes("$out/$Stem.png")
[Array]::Reverse($b,16,4)
[Array]::Reverse($b,20,4)
$width=[BitConverter]::ToUInt32($b,16)
$height=[BitConverter]::ToUInt32($b,20)
$req=Get-Content -Raw -LiteralPath "$out/$Stem.request.json" | ConvertFrom-Json
$refs=@()
foreach($p in $req.parameters.referenced_image_paths){$refs+=@{path=$p;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower()}}
$record=[ordered]@{file="$out/$Stem.png";sha256=(Get-FileHash -LiteralPath "$out/$Stem.png" -Algorithm SHA256).Hash.ToLower();generatedAt=(Get-Item -LiteralPath "$out/$Stem.png").LastWriteTimeUtc.ToString('o');width=$width;height=$height;format='PNG';mode=$(if($b[25] -eq 6){'RGBA'}else{'other'});tool='image_gen.imagegen';route='builtin_host_managed';configSnapshot=(Get-Content -Raw -LiteralPath 'D:/work/image/config/image-generation.json' | ConvertFrom-Json);submittedParameters=@{model=$null;quality=$null;transparent_background=$true};actualModel=$null;actualQuality=$null;unverifiedReason='Host managed; tool exposes no model/quality selectors and returns no verified model/quality metadata.';evidence=@{receipt="$Stem.receipt.json";request="$Stem.request.json";source=$Source};prompt="$Stem.request.json#/parameters/prompt";references=$refs;editTarget=$req.parameters.referenced_image_paths[0];editTargetRecord=($req.parameters.referenced_image_paths[0]+'.generation.json');visualReview=@{status=$Status;notes=$Notes};timing=@{frameDurationMs=75;cycleDurationMs=1200;frameCount=16}}
$record | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath "$out/$Stem.png.generation.json" -Encoding utf8
[pscustomobject]@{stem=$Stem;width=$width;height=$height;mode=$record.mode;sha256=$record.sha256;status=$Status} | ConvertTo-Json -Compress

