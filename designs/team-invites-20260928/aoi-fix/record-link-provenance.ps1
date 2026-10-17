$ErrorActionPreference = 'Stop'
$snapshot = Join-Path $PSScriptRoot 'baseline-source'
$result = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'baseline-build-result.json') -Raw | ConvertFrom-Json
if ($result.exitCode -ne 0) { throw '需要先完成隔离构建' }
$tlogs = @(Get-ChildItem -LiteralPath (Join-Path $snapshot 'build/cpp/intermediate/nodes/scene') -Filter 'link.read.1.tlog' -Recurse)
if ($tlogs.Count -ne 1) { throw "应有一个 Scene 链接输入记录，实际 $($tlogs.Count)" }
$inputs = @(Get-Content -LiteralPath $tlogs[0].FullName | Where-Object { $_ -match '\.lib$' })
$records = @(Get-ChildItem -LiteralPath (Join-Path $snapshot 'lib') -Filter '*.lib' | ForEach-Object {
    $library = $_
    $matches = @($inputs | Where-Object { [IO.Path]::GetFileName($_) -ieq $library.Name })
    if ($matches.Count -ne 1 -or [IO.Path]::GetFullPath($matches[0]) -ine $library.FullName) {
        throw "链接器没有唯一使用隔离库 $($library.Name): $($matches -join ', ')"
    }
    [ordered]@{name=$library.Name;path=$library.FullName;sha256=(Get-FileHash -LiteralPath $library.FullName).Hash.ToLowerInvariant();lastWriteTime=$library.LastWriteTime.ToString('o')}
})
[ordered]@{
    revision=$result.revision
    sceneSha256=$result.sha256
    linkInputLog=$tlogs[0].FullName
    ownLibraryRoot=Join-Path $snapshot 'lib'
    localLibraries=$records
    policy='自有库由同一隔离源码提交构建；实际链接输入逐库核对路径，不使用当前主工作区的自有库。'
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'baseline-linked-inputs.json') -Encoding utf8
Write-Output "已核实 $($records.Count) 个本地库的实际链接路径。"
