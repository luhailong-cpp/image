<#
.SYNOPSIS
Build the independent 23-NPC showroom from the client's approved resources.
.DESCRIPTION
Copies only the showroom scripts, NPC PNGs/manifest, Chinese font/license and
their metadata into preview-project beside this script. Builds one Windows x64
Development player; does not launch or verify it, or modify the source client.
.EXAMPLE
pwsh -File .\Build-NpcShowroom.ps1
#>
[CmdletBinding()]
param(
    [string]$ClientRoot = 'E:/work/mmorpg-client',
    [string]$UnityPath = 'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe',
    [string]$Output = (Join-Path $PSScriptRoot 'player')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ClientRoot = (Resolve-Path -LiteralPath $ClientRoot).Path
$UnityPath = (Resolve-Path -LiteralPath $UnityPath).Path
$ProjectPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'preview-project'))
$Output = [IO.Path]::GetFullPath($Output)
$LogPath = Join-Path $PSScriptRoot 'build-showroom.log'
$clientPrefix = $ClientRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
foreach ($destination in @($ProjectPath, $Output)) {
    if ($destination.Equals($ClientRoot, [StringComparison]::OrdinalIgnoreCase) -or
        $destination.StartsWith($clientPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Project and output must be outside ClientRoot; the source client is read-only.'
    }
}
if (Test-Path -LiteralPath (Join-Path $ProjectPath 'Temp/UnityLockfile')) {
    throw "preview-project is in use. Close that project before rebuilding: $ProjectPath"
}

$copies = [Collections.Generic.List[object]]::new()
function Add-FileCopy([string]$Source, [string]$Destination) {
    $sourcePath = Join-Path $ClientRoot $Source
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "Required showroom dependency is missing: $sourcePath"
    }
    $copies.Add([pscustomobject]@{ Source = $sourcePath; Destination = (Join-Path $ProjectPath $Destination) })
}
function Add-AssetCopy([string]$Source, [string]$Destination) {
    Add-FileCopy $Source $Destination
    Add-FileCopy ($Source + '.meta') ($Destination + '.meta')
}

$npcRoot = 'Assets/Resources/World/Tianyong/Npcs'
$manifest = Get-Content -LiteralPath (Join-Path $ClientRoot "$npcRoot/placements.json") -Raw | ConvertFrom-Json
if (@($manifest.entries).Count -ne 23) { throw 'Expected exactly 23 NPC entries in placements.json.' }
$seenResources = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($entry in $manifest.entries) {
    $resource = [string]$entry.spriteResource
    if ($resource -notmatch '^World/Tianyong/Npcs/Sprites/[A-Za-z0-9_-]+$' -or
        -not $seenResources.Add($resource)) {
        throw "Invalid or repeated NPC resource: $resource"
    }
    $relative = "Assets/Resources/$resource.png"
    Add-AssetCopy $relative $relative
}
Add-AssetCopy "$npcRoot/placements.json" "$npcRoot/placements.json"
Add-AssetCopy 'Assets/Scripts/World/Tianyong/NpcArtShowroom.cs' 'Assets/Runtime/NpcArtShowroom.cs'
Add-AssetCopy 'Assets/Editor/Tianyong/NpcArtShowroomBuild.cs' 'Assets/Editor/NpcArtShowroomBuild.cs'
Add-AssetCopy 'Assets/Editor/Tianyong/TianyongNpcTextureImporter.cs' 'Assets/Editor/TianyongNpcTextureImporter.cs'
Add-AssetCopy 'Assets/Resources/Fonts/TeamNotoSansSC.otf' 'Assets/Resources/Fonts/TeamNotoSansSC.otf'
Add-AssetCopy 'Assets/Resources/Fonts/TeamNotoSansSC-LICENSE.txt' 'Assets/Resources/Fonts/TeamNotoSansSC-LICENSE.txt'
foreach ($folderMeta in @(
    'Assets/Editor.meta',
    'Assets/Resources.meta',
    'Assets/Resources/Fonts.meta',
    'Assets/Resources/World.meta',
    'Assets/Resources/World/Tianyong.meta',
    'Assets/Resources/World/Tianyong/Npcs.meta',
    'Assets/Resources/World/Tianyong/Npcs/Sprites.meta'
)) { Add-FileCopy $folderMeta $folderMeta }

foreach ($copy in $copies) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $copy.Destination) -Force | Out-Null
    Copy-Item -LiteralPath $copy.Source -Destination $copy.Destination -Force
}
New-Item -ItemType Directory -Path (Join-Path $ProjectPath 'Packages'), (Join-Path $ProjectPath 'ProjectSettings'), $Output -Force | Out-Null
$manifestText = @'
{
  "dependencies": {
    "com.unity.modules.imgui": "1.0.0",
    "com.unity.modules.jsonserialize": "1.0.0",
    "com.unity.modules.imageconversion": "1.0.0",
    "com.unity.modules.screencapture": "1.0.0"
  }
}
'@
[IO.File]::WriteAllText((Join-Path $ProjectPath 'Packages/manifest.json'), $manifestText)
[IO.File]::WriteAllText((Join-Path $ProjectPath 'ProjectSettings/ProjectVersion.txt'),
    "m_EditorVersion: 6000.6.0f1`nm_EditorVersionWithRevision: 6000.6.0f1 (f7f8ed4d1e24)`n")

Write-Host "[NPC showroom] Copied 23 PNGs, placements, 3 scripts, font/license and metadata."
Write-Host "[NPC showroom] Building independent project: $ProjectPath"
Write-Host "[NPC showroom] Build log: $LogPath"
# Quote path arguments because Start-Process joins ArgumentList into one Windows command line.
$unityArgs = @(
    '-batchmode', '-quit',
    '-projectPath', ('"' + $ProjectPath + '"'),
    '-executeMethod', 'MmorpgClient.Editor.Tianyong.NpcArtShowroomBuild.Build',
    '-npcShowroomOut', ('"' + $Output.TrimEnd('\', '/') + '"'),
    '-logFile', ('"' + $LogPath + '"')
)
$process = Start-Process -FilePath $UnityPath -ArgumentList $unityArgs -WindowStyle Hidden -PassThru -Wait
$player = Join-Path $Output 'NpcArtShowroom.exe'
if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $player -PathType Leaf)) {
    throw "NPC showroom build failed (exit $($process.ExitCode)). See $LogPath"
}
Write-Host "[NPC showroom] BUILD PASS: $player"
Copy-Item -LiteralPath (Join-Path $ClientRoot 'Assets/Resources/Fonts/TeamNotoSansSC-LICENSE.txt') -Destination (Join-Path $Output 'NotoSansSC-LICENSE.txt') -Force
Write-Host '[NPC showroom] Build only; this script does not run visual verification.'
Write-Host '[NPC showroom] To verify, run the player in a VISIBLE window with -npcShowroomVerify <directory>.'
Write-Host '[NPC showroom] Do not use Hidden, -batchmode or -nographics for player verification: real rendering is required.'
Write-Host '[NPC showroom] This is a static NPC showroom, not main-city gameplay or input-click automation.'
