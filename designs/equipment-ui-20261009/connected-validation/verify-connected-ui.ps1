$ErrorActionPreference = 'Stop'
$projectRoot = 'E:/work/mmorpg-client'
$reviewRoot = $PSScriptRoot
$scratchRoot = 'E:/work/tmp/equipment-ui-connected-20261009'
$csc = 'C:/Program Files/dotnet/sdk/10.0.400/Roslyn/bincore/csc.dll'
[IO.Directory]::CreateDirectory($scratchRoot) | Out-Null

function Get-CompilerOptions([string]$projectFile) {
    [xml]$project = Get-Content -LiteralPath (Join-Path $projectRoot $projectFile) -Raw
    $options = @('-nologo','-target:library','-langversion:9.0','-nowarn:0169,0649,USG0001')
    $defines = $project.Project.PropertyGroup | ForEach-Object { $_.DefineConstants } | Where-Object { $_ } | Select-Object -First 1
    foreach($define in ($defines -split ';')) { if($define.Trim()) { $options += '-define:' + $define.Trim() } }
    foreach($reference in ($project.Project.ItemGroup | ForEach-Object { $_.Reference } | Where-Object { $_ -and $_.HintPath })) {
        $hint = [string]$reference.HintPath
        $absolute = if([IO.Path]::IsPathRooted($hint)) { $hint } else { Join-Path $projectRoot $hint }
        if(-not (Test-Path -LiteralPath $absolute)) { throw ('Missing real assembly reference: ' + $absolute) }
        $options += '-r:"' + $absolute + '"'
    }
    return $options
}

function Compile([string]$name, [string]$projectFile, [string[]]$sources, [string[]]$extraReferences = @()) {
    $dll = Join-Path $scratchRoot ($name + '.dll')
    $options = @(Get-CompilerOptions $projectFile)
    foreach($reference in $extraReferences) { $options += '-r:"' + $reference + '"' }
    $options += '-out:"' + $dll + '"'
    $options += $sources | ForEach-Object { '"' + $_ + '"' }
    $rsp = Join-Path $scratchRoot ($name + '.rsp')
    Set-Content -LiteralPath $rsp -Value $options -Encoding utf8
    $result = & dotnet exec $csc ('@' + $rsp) 2>&1
    $code = $LASTEXITCODE
    Set-Content -LiteralPath (Join-Path $reviewRoot ($name + '-integration-compile.log')) -Value $result -Encoding utf8
    Write-Output ($name + ': exit=' + $code + ', files=' + $sources.Count)
    if($code -ne 0) { $result; throw ($name + ' compilation failed') }
    $script:compilations += [pscustomobject]@{name=$name;files=$sources.Count;exitCode=$code;errors=0;warnings=@($result | Where-Object { $_ -match '(^|: )warning CS' }).Count;dll=$dll}
}

$script:compilations = @()
$runtimeSources = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'Assets/Scripts') -Filter '*.cs' -Recurse | ForEach-Object FullName)
$testSources = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'Assets/Tests/EditMode/Battle') -Filter '*.cs' -Recurse | ForEach-Object FullName)
$socialSources = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'Assets/Tests/EditMode/Social') -Filter '*.cs' -Recurse | ForEach-Object FullName)
$editorSources = @('EquipmentUiVerification.cs','EquipmentIntegrationVerification.cs','AttributePanelV10Verification.cs','GameplayUiVerification.cs') | ForEach-Object { Join-Path $projectRoot ('Assets/Editor/' + $_) }
$sourceHashes = @($runtimeSources + $testSources + $socialSources + $editorSources | ForEach-Object {
    [pscustomobject]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash}
})
Compile 'MmorpgClient' 'MmorpgClient.csproj' $runtimeSources
$runtime = Join-Path $scratchRoot 'MmorpgClient.dll'
Compile 'MmorpgClient.Tests.EditMode.Battle' 'MmorpgClient.Tests.EditMode.Battle.csproj' $testSources @($runtime)
Compile 'MmorpgClient.Tests.EditMode.Social' 'MmorpgClient.Tests.EditMode.Social.csproj' $socialSources @($runtime)
Compile 'EquipmentUiVerification.Editor' 'Assembly-CSharp-Editor.csproj' $editorSources @($runtime)
$changedSources = @($sourceHashes | Where-Object { (Get-FileHash -LiteralPath $_.path -Algorithm SHA256).Hash -ne $_.sha256 })
$status = [pscustomobject]@{
    verifiedAt=(Get-Date).ToUniversalTime().ToString('o')
    project=$projectRoot
    compilations=$script:compilations
    sourcesUnchangedDuringCompilation=($changedSources.Count -eq 0)
    changedSources=$changedSources
    sourceHashes=$sourceHashes
    note='Compilation against real Unity assemblies only. This does not execute the Unity editor, UI tests, or a live server.'
}
$status | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $reviewRoot 'main-integration-compile-status.json') -Encoding utf8
if ($changedSources.Count -ne 0) { throw 'Sources changed during compilation; repeat only the affected verification once edits settle.' }

