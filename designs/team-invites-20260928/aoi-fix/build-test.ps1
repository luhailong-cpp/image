param([ValidateSet('red','green')][string]$Phase='red', [string]$ServerRoot='E:/work/xuanming-server-mmo')
$ErrorActionPreference='Stop'
$sourceProject=Join-Path $ServerRoot 'cpp/tests/aoi_test/aoi_test.vcxproj'
$projectDirectory=Split-Path -Parent $sourceProject
[xml]$project=Get-Content -LiteralPath $sourceProject -Raw
$ns=[Xml.XmlNamespaceManager]::new($project.NameTable)
$ns.AddNamespace('m','http://schemas.microsoft.com/developer/msbuild/2003')
foreach($node in $project.SelectNodes('//m:PreprocessorDefinitions',$ns)) {
    # 与生产 Scene 相同，防止 Windows 的 max 宏污染导航头文件。
    $node.InnerText='NOMINMAX;'+$node.InnerText
}
foreach($name in @('AdditionalIncludeDirectories','AdditionalLibraryDirectories')) {
    foreach($node in $project.SelectNodes("//m:$name",$ns)) {
        $paths=@($node.InnerText.Split(';') | Where-Object { $_ } | ForEach-Object {
            if($_.Contains('$(') -or $_.Contains('%(') -or [IO.Path]::IsPathRooted($_)){ $_ } else { [IO.Path]::GetFullPath((Join-Path $projectDirectory $_)) }
        })
        if($name -eq 'AdditionalIncludeDirectories'){
            $paths+=Join-Path $ServerRoot 'third_party/grpc/third_party/utf8_range'
            $paths+=Join-Path $ServerRoot 'cpp/libs/services/scene/spatial/system'
        }
        $node.InnerText=$paths -join ';'
    }
}
# 固定到既有测试的 Debug 链接依赖，仅重编 AOI 及它的空间算法，不编译 Scene/战斗。
foreach($node in @($project.SelectNodes('//m:ItemGroup/m:ClCompile',$ns))){ [void]$node.ParentNode.RemoveChild($node) }
$items=$project.CreateElement('ItemGroup',$ns.LookupNamespace('m'))
$aoi=if($Phase -eq 'red'){Join-Path $ServerRoot 'cpp/libs/services/scene/spatial/system/aoi.cpp'}else{Join-Path $PSScriptRoot 'server/cpp/libs/services/scene/spatial/system/aoi.cpp'}
$sources=@(
    (Join-Path $PSScriptRoot 'aoi_delivery_test.cpp'),
    $aoi,
    (Join-Path $ServerRoot 'cpp/libs/services/scene/spatial/system/grid.cpp'),
    (Join-Path $ServerRoot 'cpp/libs/services/scene/spatial/system/interest.cpp'),
    (Join-Path $ServerRoot 'cpp/libs/services/scene/spatial/system/view.cpp'),
    (Join-Path $ServerRoot 'cpp/libs/engine/thread_context/ecs_context.cpp'),
    (Join-Path $ServerRoot 'cpp/libs/engine/core/utils/stat/stat.cpp')
)
foreach($source in $sources){
    $entry=$project.CreateElement('ClCompile',$ns.LookupNamespace('m'))
    $entry.SetAttribute('Include',$source)
    [void]$items.AppendChild($entry)
}
[void]$project.Project.AppendChild($items)
$projectPath=Join-Path $PSScriptRoot "aoi-delivery-$Phase.vcxproj"
$project.Save($projectPath)
$out=Join-Path $PSScriptRoot "build/$Phase/"
$int=Join-Path $PSScriptRoot "build/$Phase/obj/"
New-Item -ItemType Directory -Path $out,$int -Force | Out-Null
$msbuild='D:/Program Files/Microsoft Visual Studio/18/Enterprise/MSBuild/Current/Bin/MSBuild.exe'
# 宿主有时同时带 Path/PATH；.NET Framework MSBuild 的进程环境字典会拒绝它们。
# 为该子进程按不区分大小写去重，不改系统或父进程环境。
$start=[Diagnostics.ProcessStartInfo]::new($msbuild)
$start.UseShellExecute=$false
$start.CreateNoWindow=$true
$start.RedirectStandardOutput=$true
$start.RedirectStandardError=$true
$start.WorkingDirectory=$PSScriptRoot
$start.Environment.Clear()
foreach($pair in [Environment]::GetEnvironmentVariables('Process').GetEnumerator()) {
    $key=if($pair.Key -ieq 'PATH'){'Path'}else{$pair.Key.ToUpperInvariant()}
    $start.Environment[$key]=[string]$pair.Value
}
foreach($argument in @($projectPath,'/m:1','/nologo','/v:minimal','/p:Configuration=Debug','/p:Platform=x64',"/p:OutDir=$out","/p:IntDir=$int",'/p:TargetName=aoi_delivery_test')) { $start.ArgumentList.Add($argument) }
$process=[Diagnostics.Process]::new()
$process.StartInfo=$start
[void]$process.Start()
$stdout=$process.StandardOutput.ReadToEndAsync()
$stderr=$process.StandardError.ReadToEndAsync()
$process.WaitForExit()
$output=$stdout.Result+$stderr.Result
$output | Tee-Object -FilePath (Join-Path $PSScriptRoot "compile-$Phase.log")
if($process.ExitCode -ne 0){throw "AOI $Phase 构建失败"}
$env:PATH=(Join-Path $ServerRoot 'bin')+';'+(Join-Path $ServerRoot 'lib')+';'+(Join-Path $ServerRoot 'third_party/grpc/install_vs2026_dbg/bin')+';'+$env:PATH
& (Join-Path $out 'aoi_delivery_test.exe') --gtest_color=no 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot "test-$Phase.log")
exit $LASTEXITCODE
