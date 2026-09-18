Add-Type -AssemblyName System.Drawing
$root=$tileDir
$sourceImg=[System.Drawing.Image]::FromFile($source)
$actual=@($sourceImg.Width,$sourceImg.Height)
$sourceImg.Dispose()
if($actual[0] -ne 1254 -or $actual[1] -ne 1254){throw ('Unexpected native dimensions: '+($actual -join 'x'))}
$output=Join-Path $root ('native/'+$id+'.png')
Copy-Item -LiteralPath $source -Destination $output
$prompt=Join-Path $root ('prompts/'+$id+'.prompt.txt')
$guide=Join-Path $root ('guides/'+$id+'.layout-only.png')
$preview=Join-Path $root ('guides/'+$id+'.input-preview.jpg')
$record=[ordered]@{id=$id;route='builtin_image_gen';backendModelVerified=$false;backendModel='host-managed, unverified';modelSelectorAvailable=$false;actualNativePixels=$actual;sourceOutputPath=$source;outputPath=$output;promptPath=$prompt;guidePath=$guide;sourceOutputSha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant();outputSha256=(Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash.ToLowerInvariant();promptSha256=(Get-FileHash -LiteralPath $prompt -Algorithm SHA256).Hash.ToLowerInvariant();guideSha256=(Get-FileHash -LiteralPath $guide -Algorithm SHA256).Hash.ToLowerInvariant();actualSubmittedReferencePath=$preview;actualSubmittedReferenceSha256=(Get-FileHash -LiteralPath $preview -Algorithm SHA256).Hash.ToLowerInvariant();actualSubmittedReferencePixels=@(1254,1254);actualSubmittedReferenceFormat='JPEG';actualSubmittedReferenceJpegQuality=65;referenceTransport='visible conversation image; num_last_images_to_include=1';guideRole='PNG layout reference only; final art generated anew';finalArtUpscaled=$false;resizedAfterGeneration=$false;createdAtUtc=[DateTime]::UtcNow.ToString('o');visualQa=$qa;adjacentSeamQa='pending assembly'}
if($record.outputSha256 -ne $record.sourceOutputSha256){throw 'Native copy hash mismatch'}
[System.IO.File]::WriteAllText((Join-Path $root ('native/'+$id+'.record.json')),($record | ConvertTo-Json -Depth 6),[System.Text.UTF8Encoding]::new($false))
[ordered]@{id=$id;actualNativePixels=$actual;sourceOutputPath=$source;outputSha256=$record.outputSha256;referenceSha256=$record.actualSubmittedReferenceSha256} | ConvertTo-Json
