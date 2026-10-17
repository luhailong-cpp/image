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
 if($_.Name -eq 'AttributePanel.cs' -or $_.Name -eq 'PetPanel.cs'){'"'+(Join-Path $package ('integration/'+$_.Name))+'"'}elseif($_.Name -eq 'SkillPanel.cs'){'"E:/work/image/designs/class-skills-20260928/fidelity-20261016/integration/SkillPanel.cs"'}else{'"'+$_.FullName+'"'}
})
$sources+=@('AttributeFidelityLayout.cs','AttributePanel.Fidelity.cs','PetPanel.Fidelity.cs') | ForEach-Object {'"'+(Join-Path $package ('integration/'+$_))+'"'}
$sources+='"E:/work/image/designs/class-skills-20260928/fidelity-20261016/integration/SkillPanel.Fidelity.cs"'
$runtime=Join-Path $qa 'AttributeSkillFidelity.Runtime.dll'
$runtimeRsp=Join-Path $qa 'runtime.rsp'
Set-Content -Encoding utf8 -LiteralPath $runtimeRsp -Value ($opts+$refs+('-out:"'+$runtime+'"')+$sources)
$csc='C:/Program Files/dotnet/sdk/10.0.400/Roslyn/bincore/csc.dll'
$runtimeOutput=& dotnet exec $csc ('@'+$runtimeRsp) 2>&1
$runtimeExit=$LASTEXITCODE
Set-Content -Encoding utf8 -LiteralPath (Join-Path $qa 'runtime-compile.log') -Value $runtimeOutput
$result=[ordered]@{checkedAtUtc=[DateTime]::UtcNow.ToString('O');runtimeExit=$runtimeExit;runtimeSources=$sources.Count;missingReferences=$missing;unityEditor=$editor.FullName;csc=$csc;unityLaunched=$false;nativeCaptureRun=$false}
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $qa 'compile-report.json')
$result | ConvertTo-Json -Depth 8
if($runtimeExit -ne 0){$runtimeOutput | Select-Object -First 18;exit 1}
