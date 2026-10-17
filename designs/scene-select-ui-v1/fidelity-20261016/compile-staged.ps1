param([string]$Client='E:/work/mmorpg-client')
$ErrorActionPreference='Stop'
$package=$PSScriptRoot
$qa=Join-Path $package 'qa'
New-Item -ItemType Directory -Force -Path $qa | Out-Null
[xml]$xml=Get-Content -Raw (Join-Path $Client 'MmorpgClient.csproj')
$opts=@('-nologo','-target:library','-langversion:9.0','-nowarn:0169,0649')
$defines=$xml.Project.PropertyGroup | ForEach-Object {$_.DefineConstants} | Where-Object {$_} | Select-Object -First 1
foreach($d in ($defines -split ';')){if($d.Trim()){$opts+='-define:'+$d.Trim()}}
$editor=Get-ChildItem 'C:/Program Files/Unity/Hub/Editor' -Directory | Sort-Object Name -Descending | Select-Object -First 1
$refs=@();$missing=@()
foreach($ref in ($xml.Project.ItemGroup | ForEach-Object {$_.Reference} | Where-Object {$_ -and $_.HintPath} | ForEach-Object {$_.HintPath})){
  $full=if([IO.Path]::IsPathRooted($ref)){$ref}else{Join-Path $Client $ref}
  if(!(Test-Path -LiteralPath $full) -and $full -match '^(.*\\Unity\\Hub\\Editor\\)[^\\]+\\(.*)$'){
    $candidate=Join-Path $editor.FullName $Matches[2]
    if(Test-Path -LiteralPath $candidate){$full=$candidate}
  }
  if(Test-Path -LiteralPath $full){$refs+='-r:"'+$full+'"'}else{$missing+=$full}
}
$sources=@(Get-ChildItem (Join-Path $Client 'Assets/Scripts') -Recurse -Filter *.cs | ForEach-Object {
  if($_.Name -eq 'SceneChannelWindow.cs'){'"'+(Join-Path $package 'integration/SceneChannelWindow.cs')+'"'}elseif($_.Name -eq 'CityTravelWindow.cs'){'"E:/work/image/designs/world-map-original-20260925/fidelity-20261016/integration/CityTravelWindow.cs"'}else{'"'+$_.FullName+'"'}
})
$runtime=Join-Path $qa 'SceneTravelFidelity.Runtime.dll'
$runtimeRsp=Join-Path $qa 'runtime.rsp'
Set-Content -Encoding utf8 -LiteralPath $runtimeRsp -Value ($opts+$refs+('-out:"'+$runtime+'"')+$sources)
$csc='C:/Program Files/dotnet/sdk/10.0.400/Roslyn/bincore/csc.dll'
$runtimeOutput=& dotnet exec $csc ('@'+$runtimeRsp) 2>&1
$runtimeExit=$LASTEXITCODE
Set-Content -Encoding utf8 -LiteralPath (Join-Path $qa 'runtime-compile.log') -Value $runtimeOutput
$editorRefs=@('-r:"'+$runtime+'"')
foreach($dll in Get-ChildItem (Join-Path $editor.FullName 'Editor/Data/Managed') -Filter UnityEditor*.dll -Recurse){$editorRefs+='-r:"'+$dll.FullName+'"'}
$editorDll=Join-Path $qa 'SceneTravelFidelity.Editor.dll'
$editorRsp=Join-Path $qa 'editor.rsp'
Set-Content -Encoding utf8 -LiteralPath $editorRsp -Value ($opts+$refs+$editorRefs+('-out:"'+$editorDll+'"')+('"'+(Join-Path $package 'integration/SceneChannelFidelityVerification.cs')+'"')+('"E:/work/image/designs/world-map-original-20260925/fidelity-20261016/integration/WorldMapFidelityVerification.cs"'))
$editorOutput=& dotnet exec $csc ('@'+$editorRsp) 2>&1
$editorExit=$LASTEXITCODE
Set-Content -Encoding utf8 -LiteralPath (Join-Path $qa 'editor-compile.log') -Value $editorOutput
$result=[ordered]@{checkedAtUtc=[DateTime]::UtcNow.ToString('O');runtimeExit=$runtimeExit;editorExit=$editorExit;runtimeSources=$sources.Count;missingReferences=$missing;unityEditor=$editor.FullName;csc=$csc;unityLaunched=$false;nativeCaptureRun=$false}
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $qa 'compile-report.json')
$result | ConvertTo-Json -Depth 8
if($runtimeExit -ne 0){$runtimeOutput | Select-Object -First 12}
if($editorExit -ne 0){$editorOutput | Select-Object -First 12}
if($runtimeExit -ne 0 -or $editorExit -ne 0){exit 1}
