$ErrorActionPreference = 'Stop'
$serverRoot = 'E:/work/xuanming-server-mmo'
$targetDirectory = Join-Path $serverRoot 'cpp/tests/aoi_delivery_test'
if (Test-Path -LiteralPath $targetDirectory) { throw '目标测试目录已存在，拒绝覆盖' }
[xml]$project = Get-Content -LiteralPath (Join-Path $serverRoot 'cpp/tests/aoi_test/aoi_test.vcxproj') -Raw
$ns = [Xml.XmlNamespaceManager]::new($project.NameTable)
$ns.AddNamespace('m', 'http://schemas.microsoft.com/developer/msbuild/2003')
foreach ($node in @($project.SelectNodes('//m:ProjectConfiguration', $ns))) {
    if ($node.Include -ne 'Debug|x64') { [void]$node.ParentNode.RemoveChild($node) }
}
foreach ($node in @($project.SelectNodes('//*[@Condition]', $ns))) {
    if ($node.Condition -match 'Configuration.*Platform' -and $node.Condition -notmatch 'Debug\|x64') {
        [void]$node.ParentNode.RemoveChild($node)
    }
}
$project.SelectSingleNode('//m:ProjectGuid', $ns).InnerText = '{C50C8603-A06B-450C-9D5D-697DDF52C635}'
$project.SelectSingleNode('//m:RootNamespace', $ns).InnerText = 'AoiDeliveryTest'
foreach ($node in $project.SelectNodes('//m:PreprocessorDefinitions', $ns)) { $node.InnerText = 'NOMINMAX;' + $node.InnerText }
foreach ($node in $project.SelectNodes('//m:AdditionalIncludeDirectories', $ns)) {
    $node.InnerText += ';../../../third_party/grpc/third_party/utf8_range;../../libs/services/scene/spatial/system'
}
foreach ($node in @($project.SelectNodes('//m:ItemGroup/m:ClCompile', $ns))) { [void]$node.ParentNode.RemoveChild($node) }
$items = $project.CreateElement('ItemGroup', $ns.LookupNamespace('m'))
foreach ($source in @(
    'aoi_delivery_test.cpp',
    '../../libs/services/scene/spatial/system/aoi.cpp',
    '../../libs/services/scene/spatial/system/grid.cpp',
    '../../libs/services/scene/spatial/system/interest.cpp',
    '../../libs/services/scene/spatial/system/view.cpp',
    '../../libs/engine/thread_context/ecs_context.cpp',
    '../../libs/engine/core/utils/stat/stat.cpp'
)) {
    $entry = $project.CreateElement('ClCompile', $ns.LookupNamespace('m'))
    $entry.SetAttribute('Include', $source)
    [void]$items.AppendChild($entry)
}
[void]$project.Project.AppendChild($items)
$runner = Join-Path $serverRoot 'tools/scripts/run_cpp_tests.ps1'
if ((Get-FileHash -LiteralPath $runner).Hash -ne 'AD462F76C2B9A1EC398F3A5BA3BEAF8CFC23F6EE7C6AA955554158CC84659FD9') { throw '测试入口已变化，拒绝覆盖' }
$runnerText = [IO.File]::ReadAllText($runner)
$anchor = "    'aoi_test'                 = 'cpp\tests\aoi_test\aoi_test.vcxproj'"
if (-not $runnerText.Contains($anchor)) { throw '测试入口锚点不存在' }
$runnerText = $runnerText.Replace($anchor, "    'aoi_delivery_test'        = 'cpp\tests\aoi_delivery_test\aoi_delivery_test.vcxproj'" + "`r`n" + $anchor)
New-Item -ItemType Directory -Path $targetDirectory | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'aoi_delivery_test.cpp') -Destination (Join-Path $targetDirectory 'aoi_delivery_test.cpp')
$project.Save((Join-Path $targetDirectory 'aoi_delivery_test.vcxproj'))
[IO.File]::WriteAllText($runner, $runnerText, [Text.UTF8Encoding]::new($false))
Write-Output '已登记 AOI 双向通知回归：pwsh tools/scripts/run_cpp_tests.ps1 -Build -Filter aoi_delivery_test'
