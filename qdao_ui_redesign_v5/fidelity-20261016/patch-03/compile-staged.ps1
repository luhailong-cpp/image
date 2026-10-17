[CmdletBinding()]
param([string]$ClientRoot="E:\work\mmorpg-client",[string]$Phase="patch-03")
$ErrorActionPreference="Stop"
$packageRoot=$PSScriptRoot
$qaRoot=Join-Path $packageRoot "qa"
New-Item -ItemType Directory -Force -Path $qaRoot | Out-Null
$csproj=Join-Path $ClientRoot "MmorpgClient.csproj"
[xml]$project=Get-Content -LiteralPath $csproj -Raw
$unityRoot=(Get-ChildItem "C:\Program Files\Unity\Hub\Editor" -Directory | Where-Object {Test-Path (Join-Path $_.FullName "Editor\Unity.exe")} | Sort-Object Name -Descending | Select-Object -First 1).FullName
$csc=(Get-ChildItem "C:\Program Files\dotnet\sdk" -Directory | Where-Object {Test-Path (Join-Path $_.FullName "Roslyn\bincore\csc.dll")} | Sort-Object Name -Descending | Select-Object -First 1).FullName
$csc=Join-Path $csc "Roslyn\bincore\csc.dll"
$opts=@("-nologo","-target:library","-langversion:latest","-unsafe","-nowarn:0169,0649")
$defines=$project.Project.PropertyGroup | ForEach-Object {$_.DefineConstants} | Where-Object {$_} | Select-Object -First 1
if($defines){$opts+="-define:$defines"}
$missing=@()
$references=@($project.Project.ItemGroup | ForEach-Object {$_.Reference} | Where-Object {$_ -and $_.HintPath} | ForEach-Object {$_.HintPath})
$refArgs=foreach($ref in $references){
 $refPath=if([IO.Path]::IsPathRooted($ref)){$ref}else{Join-Path $ClientRoot $ref}
 if(!(Test-Path -LiteralPath $refPath) -and $refPath -match '^(.*\\Unity\\Hub\\Editor\\)[^\\]+\\(.*)$'){$refPath=Join-Path $unityRoot $Matches[2]}
 if(Test-Path -LiteralPath $refPath){'-r:"'+$refPath+'"'}else{$missing+=$ref}
}
if($missing.Count){throw "Missing compile references: $($missing -join ', ')"} 
$stagedFiles=@(Get-ChildItem (Join-Path $packageRoot "client\Assets\Scripts") -Recurse -Filter *.cs | Where-Object {$Phase -ne "login-server" -or $_.Name -ne "RoleFlowUi.cs"})
$excluded=@($stagedFiles | ForEach-Object {Join-Path $ClientRoot ($_.FullName.Substring((Join-Path $packageRoot "client").Length + 1))})
$sources=@(Get-ChildItem (Join-Path $ClientRoot "Assets\Scripts") -Recurse -Filter *.cs | Where-Object {$_.FullName -notin $excluded} | ForEach-Object {'"'+$_.FullName+'"'})
$stage=@($stagedFiles | ForEach-Object {'"'+$_.FullName+'"'})
$rsp=Join-Path $qaRoot "core-$Phase-compile.rsp"
$assembly=Join-Path $qaRoot "core-$Phase-runtime-check.dll"
Set-Content -LiteralPath $rsp -Value ($opts+$refArgs+('-out:"'+$assembly+'"')+$sources+$stage) -Encoding utf8
$output=& dotnet exec $csc "@$rsp" 2>&1
$exit=$LASTEXITCODE
$output | Set-Content -LiteralPath (Join-Path $qaRoot "core-$Phase-compile.log") -Encoding utf8
$status=[ordered]@{checkedAtUtc=[DateTime]::UtcNow.ToString("o"); exitCode=$exit; sourceCount=$sources.Count+$stage.Count; stagedSources=$stage; errors=@($output | Where-Object {$_ -match ': error '}); nativeUnityRun=$false; imageParityVerified=$false; scope="Current runtime sources with staged core login/server/role presentation replacing production source; current client not modified."}
$status | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $qaRoot "core-$Phase-compile-result.json") -Encoding utf8
$status | ConvertTo-Json -Depth 4
exit $exit

