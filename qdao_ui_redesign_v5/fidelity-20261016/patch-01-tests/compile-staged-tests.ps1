[CmdletBinding()]
param([string]$ClientRoot="E:\work\mmorpg-client")
$ErrorActionPreference="Stop"
$packageRoot=$PSScriptRoot
$qaRoot=Join-Path $packageRoot "qa"
$runtime=Join-Path $qaRoot "..\..\patch-01\qa\core-patch-01-runtime-check.dll"
if(!(Test-Path -LiteralPath $runtime)){throw "Run compile-staged.ps1 first"}
[xml]$project=Get-Content -LiteralPath (Join-Path $ClientRoot "MmorpgClient.Tests.PlayMode.csproj") -Raw
$unityRoot=(Get-ChildItem "C:\Program Files\Unity\Hub\Editor" -Directory | Where-Object {Test-Path (Join-Path $_.FullName "Editor\Unity.exe")} | Sort-Object Name -Descending | Select-Object -First 1).FullName
$sdkRoot=(Get-ChildItem "C:\Program Files\dotnet\sdk" -Directory | Where-Object {Test-Path (Join-Path $_.FullName "Roslyn\bincore\csc.dll")} | Sort-Object Name -Descending | Select-Object -First 1).FullName
$csc=Join-Path $sdkRoot "Roslyn\bincore\csc.dll"
$defines=$project.Project.PropertyGroup | ForEach-Object {$_.DefineConstants} | Where-Object {$_} | Select-Object -First 1
$opts=@("-nologo","-target:library","-langversion:latest","-unsafe","-nowarn:0169,0649","-define:$defines")
$references=@($project.Project.ItemGroup | ForEach-Object {$_.Reference} | Where-Object {$_ -and $_.HintPath} | ForEach-Object {$_.HintPath})
$refArgs=foreach($ref in $references){
 $refPath=if([IO.Path]::IsPathRooted($ref)){$ref}else{Join-Path $ClientRoot $ref}
 if(!(Test-Path -LiteralPath $refPath) -and $refPath -match '^(.*\\Unity\\Hub\\Editor\\)[^\\]+\\(.*)$'){$refPath=Join-Path $unityRoot $Matches[2]}
 if(!(Test-Path -LiteralPath $refPath)){throw "Missing test reference $refPath"}
 '-r:"'+$refPath+'"'
}
$assembly=Join-Path $qaRoot "MmorpgClient.Tests.PlayMode.dll"
$source=Join-Path $packageRoot "client\Assets\Tests\PlayMode\QdaoRoleIdentityPlayModeTests.cs"
$rsp=Join-Path $qaRoot "test-compile.rsp"
$sources=@($project.Project.ItemGroup | ForEach-Object {$_.Compile} | Where-Object {$_ -and $_.Include} | ForEach-Object {if($_.Include -eq "Assets\Tests\PlayMode\QdaoRoleIdentityPlayModeTests.cs"){'"'+$source+'"'}else{'"'+(Join-Path $ClientRoot $_.Include)+'"'}})
Set-Content -LiteralPath $rsp -Value ($opts+$refArgs+('-r:"'+$runtime+'"')+('-out:"'+$assembly+'"')+$sources) -Encoding utf8
$output=& dotnet exec $csc "@$rsp" 2>&1
$exit=$LASTEXITCODE
$output | Set-Content -LiteralPath (Join-Path $qaRoot "test-compile.log") -Encoding utf8
$status=[ordered]@{checkedAtUtc=[DateTime]::UtcNow.ToString("o");exitCode=$exit;errors=@($output | Where-Object {$_ -match ': error '});source=$source;runtimeAssembly=$runtime;testsExecuted=$false;nativeUnityRun=$false}
$status | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $qaRoot "test-compile-result.json") -Encoding utf8
$status | ConvertTo-Json -Depth 4
exit $exit

