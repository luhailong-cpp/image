$ErrorActionPreference = 'Stop'
$npcRepository = 'E:/work/mmorpg-client'
$npcBranch = 'codex/npc-showroom-20261016'
$npcIndex = Join-Path $PSScriptRoot 'verification/npc-delivery.index'
$npcPreviousIndex = $env:GIT_INDEX_FILE
$npcPaths = @(
    'Assets/Editor/Tianyong/TianyongNpcTextureImporter.cs',
    'Assets/Editor/Tianyong/NpcArtShowroomBuild.cs',
    'Assets/Editor/Tianyong/NpcArtShowroomBuild.cs.meta',
    'Assets/Scripts/World/Tianyong/TianyongCityNpcs.cs',
    'Assets/Scripts/World/Tianyong/NpcArtShowroom.cs',
    'Assets/Scripts/World/Tianyong/NpcArtShowroom.cs.meta',
    'Assets/Tests/EditMode/Tianyong/TianyongCityNpcTests.cs',
    'Assets/Resources/World/Tianyong.meta',
    'Assets/Resources/World/Tianyong/Npcs.meta',
    'Assets/Resources/World/Tianyong/Npcs',
    'Assets/Scenes/World/NpcArtShowroom.unity',
    'Assets/Scenes/World/NpcArtShowroom.unity.meta',
    'Docs/CityNpcs.md',
    'Docs/CityNpcs.sources.json',
    'Docs/NpcShowroom',
    'tools/sync_city_npcs.py',
    'tools/test_sync_city_npcs.py',
    'tools/preview_city_npcs.py'
)
function Invoke-NpcGit {
    $npcResult = & git -c safe.directory=E:/work/mmorpg-client -c core.safecrlf=false -C $npcRepository @args
    if ($LASTEXITCODE -ne 0) { $npcResult | Write-Host; throw "Git failed: $($args -join ' ')" }
    return $npcResult
}
try {
    if (Test-Path -LiteralPath $npcIndex) { throw 'Temporary NPC index already exists.' }
    & git -c safe.directory=E:/work/mmorpg-client -C $npcRepository show-ref --verify --quiet "refs/heads/$npcBranch"
    if ($LASTEXITCODE -eq 0) { throw 'NPC delivery branch already exists; inspect it before retrying.' }
    $npcBase = Invoke-NpcGit rev-parse HEAD
    $env:GIT_INDEX_FILE = $npcIndex
    Invoke-NpcGit read-tree $npcBase
    Invoke-NpcGit add -- @npcPaths
    Invoke-NpcGit diff --cached --check
    $npcTree = Invoke-NpcGit write-tree
    $npcCommit = Invoke-NpcGit commit-tree $npcTree -p $npcBase -m 'Add native-resolution city NPC art and standalone showroom'
    Invoke-NpcGit update-ref "refs/heads/$npcBranch" $npcCommit ('0' * 40)
    [ordered]@{ branch=$npcBranch; commit=$npcCommit; parent=$npcBase; paths=$npcPaths; note='Scoped snapshot using an isolated index; current branch and existing working changes retained.' } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'verification/client-commit.json') -Encoding utf8
    Write-Output "Saved $npcCommit on $npcBranch"
}
finally {
    $env:GIT_INDEX_FILE = $npcPreviousIndex
    if (Test-Path -LiteralPath $npcIndex) { Remove-Item -LiteralPath $npcIndex }
}
