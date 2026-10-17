[CmdletBinding()]
param([switch]$CheckOnly, [ValidateSet('all','client','server')][string]$Repository = 'all')
$ErrorActionPreference = 'Stop'
$integrationRoot = $PSScriptRoot
$repositories = @{ client = 'E:\work\mmorpg-client'; server = 'E:\work\xuanming-server-mmo' }
$entries = @()
foreach ($manifestFile in Get-ChildItem -LiteralPath $integrationRoot -Filter '*-manifest.json' -File) {
    $repositoryName = if ($manifestFile.Name -like 'server-*') { 'server' } else { 'client' }
    if ($Repository -ne 'all' -and $Repository -ne $repositoryName) { continue }
    $manifest = Get-Content -LiteralPath $manifestFile.FullName -Raw | ConvertFrom-Json
    if ($manifest -isnot [array] -and $null -ne $manifest.PSObject.Properties['files']) { $manifest = $manifest.files }
    foreach ($entry in $manifest) {
        $relativePath = [string]$entry.path
        if ([string]::IsNullOrWhiteSpace($relativePath)) { throw ('清单缺少 path: ' + $manifestFile.Name) }
        $repositoryRoot = [IO.Path]::GetFullPath($repositories[$repositoryName])
        $destination = [IO.Path]::GetFullPath((Join-Path $repositoryRoot $relativePath))
        $sourceRoot = [IO.Path]::GetFullPath((Join-Path $integrationRoot $repositoryName))
        $source = [IO.Path]::GetFullPath((Join-Path $sourceRoot $relativePath))
        if (-not $destination.StartsWith($repositoryRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or
            -not $source.StartsWith($sourceRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw ('路径越界: ' + $relativePath) }
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw ('缺少待同步文件: ' + $source) }
        $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
        $currentHash = if (Test-Path -LiteralPath $destination -PathType Leaf) { (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash } else { $null }
        if ($currentHash -ne $sourceHash -and $currentHash -ne $entry.originalSha256) {
            throw ('原文件已被其他任务修改，停止同步: ' + $destination)
        }
        $entries += [pscustomobject]@{ repository=$repositoryName; path=$relativePath; source=$source; destination=$destination; sha256=$sourceHash; changed=($currentHash -ne $sourceHash) }
    }
}
if ($entries.Count -eq 0) { throw '没有可同步的文件。' }
if (@($entries | Group-Object destination | Where-Object Count -gt 1).Count -gt 0) { throw '清单包含重复目标。' }
if (-not $CheckOnly) {
    foreach ($entry in $entries | Where-Object changed) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $entry.destination) -Force | Out-Null
        Copy-Item -LiteralPath $entry.source -Destination $entry.destination -Force
        if ((Get-FileHash -LiteralPath $entry.destination -Algorithm SHA256).Hash -ne $entry.sha256) { throw ('落盘校验失败: ' + $entry.destination) }
    }
    $entries | Select-Object repository,path,sha256,changed | ConvertTo-Json -Depth 4 |
        Set-Content -LiteralPath (Join-Path $integrationRoot 'applied.json') -Encoding utf8
}
$entries | Group-Object repository | Select-Object Name,Count
Write-Output $(if ($CheckOnly) { '同步前校验通过。' } else { '组队邀请代码已同步并校验。' })
