$ErrorActionPreference = 'Stop'
$projectRoot = 'E:/work/mmorpg-client'
$reviewRoot = 'E:/work/image/designs/equipment-ui-20261009/validation'
$scratchRoot = 'E:/work/tmp/equipment-ui-20261009-compile'
$csc = 'C:/Program Files/dotnet/sdk/10.0.400/Roslyn/bincore/csc.dll'
[IO.Directory]::CreateDirectory($scratchRoot) | Out-Null

function Get-CompilerOptions([string]$projectFile) {
    [xml]$project = Get-Content -LiteralPath (Join-Path $projectRoot $projectFile) -Raw
    $options = @('-nologo','-target:library','-langversion:9.0','-nowarn:0169,0649,USG0001')
    $defines = $project.Project.PropertyGroup | ForEach-Object { $_.DefineConstants } | Where-Object { $_ } | Select-Object -First 1
    foreach($define in ($defines -split ';')) { if($define.Trim()) { $options += '-define:' + $define.Trim() } }
    $references = $project.Project.ItemGroup | ForEach-Object { $_.Reference } | Where-Object { $_ -and $_.HintPath }
    foreach($reference in $references) {
        $hint = [string]$reference.HintPath
        $absolute = if([IO.Path]::IsPathRooted($hint)) { $hint } else { Join-Path $projectRoot $hint }
        if(-not (Test-Path -LiteralPath $absolute)) { throw ('Missing real assembly reference: ' + $absolute) }
        $options += '-r:"' + $absolute + '"'
    }
    return $options
}

$runtime = Join-Path $scratchRoot 'MmorpgClient.dll'
$runtimeOptions = @(Get-CompilerOptions 'MmorpgClient.csproj')
$runtimeOptions += '-out:"' + $runtime + '"'
$runtimeOptions += Get-ChildItem -LiteralPath (Join-Path $projectRoot 'Assets/Scripts') -Filter '*.cs' -Recurse | ForEach-Object { '"' + $_.FullName + '"' }
$runtimeRsp = Join-Path $scratchRoot 'runtime.rsp'
Set-Content -LiteralPath $runtimeRsp -Value $runtimeOptions -Encoding utf8
$runtimeOutput = & dotnet exec $csc ('@' + $runtimeRsp) 2>&1
$runtimeExit = $LASTEXITCODE
Set-Content -LiteralPath (Join-Path $reviewRoot 'runtime-compile.log') -Value $runtimeOutput -Encoding utf8
Write-Output ('Runtime exit=' + $runtimeExit)
if($runtimeExit -ne 0) { $runtimeOutput; exit $runtimeExit }

$editorOptions = @(Get-CompilerOptions 'Assembly-CSharp-Editor.csproj')
$editorOptions += '-r:"' + $runtime + '"'
$editorOptions += '-out:"' + (Join-Path $scratchRoot 'EquipmentUiVerification.Editor.dll') + '"'
$editorOptions += '"' + (Join-Path $projectRoot 'Assets/Editor/EquipmentUiVerification.cs') + '"'
$editorRsp = Join-Path $scratchRoot 'editor.rsp'
Set-Content -LiteralPath $editorRsp -Value $editorOptions -Encoding utf8
$editorOutput = & dotnet exec $csc ('@' + $editorRsp) 2>&1
$editorExit = $LASTEXITCODE
Set-Content -LiteralPath (Join-Path $reviewRoot 'editor-compile.log') -Value $editorOutput -Encoding utf8
Write-Output ('EquipmentUiVerification editor exit=' + $editorExit)
$editorOutput
exit $editorExit

