param([string]$ClientRoot = 'E:/work/mmorpg-client')
$ErrorActionPreference = 'Stop'
$stage = Join-Path $PSScriptRoot 'client'
$artRoot = Split-Path $PSScriptRoot
$iconOutput = Join-Path $stage 'Assets/Resources/UI/Skills'
New-Item -ItemType Directory -Force -Path $iconOutput | Out-Null
$catalog = Get-Content -Raw (Join-Path $artRoot 'catalog.json') | ConvertFrom-Json
Copy-Item -LiteralPath (Join-Path $artRoot 'catalog.json') -Destination (Join-Path $stage 'Assets/Resources/Skills/catalog.json')
foreach ($skill in $catalog.skills) {
    $source = Join-Path $artRoot $skill.iconPath
    if (-not (Test-Path -LiteralPath $source)) { throw "Missing final skill icon: $source" }
    $target = Join-Path $iconOutput "$($skill.id).png"
    Copy-Item -LiteralPath $source -Destination $target
    if (-not (Test-Path "$target.meta")) {
        $id = [Guid]::NewGuid().ToString('N')
        $spriteId = [Guid]::NewGuid().ToString('N')
        $meta = @"
fileFormatVersion: 2
guid: $id
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {}
  serializedVersion: 13
  mipmaps:
    enableMipMap: 0
    sRGBTexture: 1
  isReadable: 0
  textureFormat: 1
  maxTextureSize: 512
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  compressionQuality: 100
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 0
  alignment: 0
  spritePivot: {x: 0.5, y: 0.5}
  spritePixelsToUnits: 100
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
  alphaUsage: 1
  alphaIsTransparency: 1
  textureType: 8
  textureShape: 1
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 512
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 100
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: $spriteId
    internalID: 0
    secondaryTextures: []
    nameFileIdTable: {}
  userData: Original four-class skill icon; source designs/class-skills-20260928
  assetBundleName:
  assetBundleVariant:
"@
        Set-Content -LiteralPath "$target.meta" -Value $meta -Encoding utf8
    }
}
Get-ChildItem -LiteralPath (Join-Path $stage 'Assets') -Recurse | ForEach-Object {
    if ($_.Name.EndsWith('.meta')) { return }
    $relative = [IO.Path]::GetRelativePath($stage, $_.FullName)
    $existing = Join-Path $ClientRoot ($relative + '.meta')
    $metaPath = $_.FullName + '.meta'
    if ((Test-Path -LiteralPath $metaPath) -or (Test-Path -LiteralPath $existing)) { return }
    $id = [Guid]::NewGuid().ToString('N')
    if ($_.PSIsContainer) {
        $body = "folderAsset: yes`nDefaultImporter:`n  externalObjects: {}`n"
    } elseif ($_.Extension -eq '.cs') {
        $body = "MonoImporter:`n  externalObjects: {}`n  serializedVersion: 2`n  defaultReferences: []`n  executionOrder: 0`n  icon: {instanceID: 0}`n"
    } else {
        $body = "TextScriptImporter:`n  externalObjects: {}`n"
    }
    Set-Content -LiteralPath $metaPath -Encoding utf8 -Value ("fileFormatVersion: 2`nguid: $id`n" + $body)
}
Write-Output "Prepared $($catalog.skills.Count) production skill icons and Unity import metadata."
