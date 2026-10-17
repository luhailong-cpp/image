param([string]$ClientRoot = 'E:/work/mmorpg-client')
$ErrorActionPreference = 'Stop'
$stageRoot = Join-Path $PSScriptRoot 'client'
$checkRoot = Join-Path $PSScriptRoot '.client-validation'
New-Item -ItemType Directory -Force -Path $checkRoot | Out-Null
# Reuse the installed Unity project's own references and defines.
& pwsh -File (Join-Path $ClientRoot 'tools/client_compile_check.ps1') -ShowErrors 0 | Out-Null
$baseRsp = Join-Path ([IO.Path]::GetTempPath()) 'mmorpg_compile_check/poll.rsp'
$options = @(Get-Content -LiteralPath $baseRsp | Where-Object { $_ -notmatch '^"' -and $_ -notmatch '^-out:' })
$sources = @{}
foreach ($rootPath in @($ClientRoot, $stageRoot)) {
    Get-ChildItem -LiteralPath (Join-Path $rootPath 'Assets/Scripts') -Recurse -Filter '*.cs' | ForEach-Object {
        $relative = [IO.Path]::GetRelativePath($rootPath, $_.FullName).Replace('\','/')
        $sources[$relative] = $_.FullName
    }
}
$assemblyPath = Join-Path $checkRoot 'client-runtime.dll'
$responsePath = Join-Path $checkRoot 'runtime.rsp'
Set-Content -LiteralPath $responsePath -Encoding utf8 -Value ($options + ('-out:"' + $assemblyPath + '"') + @($sources.Values | Sort-Object | ForEach-Object { '"' + $_ + '"' }))
$sdk = Get-ChildItem 'C:/Program Files/dotnet/sdk' -Directory | Sort-Object Name -Descending | Select-Object -First 1
$compiler = Join-Path $sdk.FullName 'Roslyn/bincore/csc.dll'
$result = & dotnet exec $compiler "@$responsePath" 2>&1
$compileExit = $LASTEXITCODE
$result | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'client-compile.log') -Encoding utf8
$result | Where-Object { $_ -match ': error ' } | Select-Object -First 25 | Write-Output
Write-Output "Overlay runtime compile: exit=$compileExit sources=$($sources.Count)"
if ($compileExit -ne 0) { exit $compileExit }

$editorResponse = Join-Path $checkRoot 'editor.rsp'
$editorAssembly = Join-Path $checkRoot 'client-skill-editor.dll'
$editorSource = Join-Path $stageRoot 'Assets/Editor/ClassSkillUiVerification.cs'
Set-Content -LiteralPath $editorResponse -Encoding utf8 -Value ($options + ('-r:"' + $assemblyPath + '"') + ('-out:"' + $editorAssembly + '"') + ('"' + $editorSource + '"'))
$editorResult = & dotnet exec $compiler "@$editorResponse" 2>&1
$editorExit = $LASTEXITCODE
$editorResult | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'client-editor-compile.log') -Encoding utf8
$editorResult | Where-Object { $_ -match ': error ' } | Write-Output
Write-Output "Skill editor helper compile: exit=$editorExit"
if ($editorExit -ne 0) { exit $editorExit }

$nunit = Get-ChildItem (Join-Path $ClientRoot 'Library/PackageCache') -Recurse -Filter nunit.framework.dll | Select-Object -First 1
if (-not $nunit) { throw 'Unity NUnit framework missing' }
$testSources = @(
    (Join-Path $stageRoot 'Assets/Scripts/Game/Skills/SkillDefinition.cs'),
    (Join-Path $stageRoot 'Assets/Scripts/Game/Skills/SkillBookSnapshot.cs'),
    (Join-Path $stageRoot 'Assets/Scripts/Game/Skills/SkillClient.cs'),
    (Join-Path $ClientRoot 'Assets/Scripts/Game/Battle/IBattleTransport.cs'),
    (Join-Path $ClientRoot 'Assets/Tests/EditMode/Battle/FakeBattleTransport.cs'),
    (Join-Path $stageRoot 'Assets/Tests/EditMode/Battle/SkillClientTests.cs'),
    (Join-Path $stageRoot 'Assets/Tests/EditMode/Battle/SkillManaReplayTests.cs'),
    (Join-Path $stageRoot 'Assets/Scripts/Game/Battle/Presentation/TurnPlan.cs'),
    (Join-Path $PSScriptRoot 'SkillCoreTestRunner.cs')
)
$protocol = @{}
foreach ($rootPath in @($ClientRoot, $stageRoot)) {
    $folder = Join-Path $rootPath 'Assets/Scripts/Proto/Generated'
    if (Test-Path $folder) {
        Get-ChildItem $folder -Filter '*.cs' | ForEach-Object { $protocol[$_.Name] = $_.FullName }
    }
}
$messageIds = Join-Path $stageRoot 'Assets/Scripts/Net/MessageIds.cs'
if (-not (Test-Path $messageIds)) { $messageIds = Join-Path $ClientRoot 'Assets/Scripts/Net/MessageIds.cs' }
$testSources += $messageIds
$testSources += @($protocol.Values)
$compileItems = ($testSources | ForEach-Object { '<Compile Include="' + [Security.SecurityElement]::Escape($_) + '" />' }) -join "`n"
$projectXml = @"
<Project Sdk="Microsoft.NET.Sdk">
 <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><NoWarn>CS8981;CS0612;CS3021</NoWarn></PropertyGroup>
 <ItemGroup>
 $compileItems
 <Reference Include="Google.Protobuf"><HintPath>$ClientRoot/Assets/Plugins/Google.Protobuf.dll</HintPath></Reference>
 <Reference Include="nunit.framework"><HintPath>$($nunit.FullName)</HintPath></Reference>
 </ItemGroup>
</Project>
"@
$projectPath = Join-Path $checkRoot 'SkillCoreTests.csproj'
Set-Content -LiteralPath $projectPath -Value $projectXml -Encoding utf8
& dotnet run --project $projectPath --configuration Release -- (Join-Path $PSScriptRoot 'client-core-tests.xml') 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot 'client-core-tests.log')
exit $LASTEXITCODE
