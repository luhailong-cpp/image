param([string]$ClientRoot = 'E:/work/mmorpg-client')
$ErrorActionPreference = 'Stop'
$allowedRoot = [IO.Path]::GetFullPath('E:/work/mmorpg-client').TrimEnd('\','/')
$resolvedRoot = [IO.Path]::GetFullPath($ClientRoot).TrimEnd('\','/')
if ($resolvedRoot -ne $allowedRoot) { throw 'This publisher only targets E:/work/mmorpg-client.' }
$stage = Join-Path $PSScriptRoot 'client'
$manifest = Get-Content -Raw (Join-Path $PSScriptRoot 'client-publish-manifest.json') | ConvertFrom-Json
foreach ($entry in $manifest.files) {
    $destination = [IO.Path]::GetFullPath((Join-Path $resolvedRoot $entry.path))
    if (-not $destination.StartsWith($resolvedRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw "Path escapes client root: $destination" }
    if (Test-Path -LiteralPath $destination) {
        $current = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
        if ($current -ne $entry.originalSha256 -and $current -ne $entry.sha256) { throw "Concurrent edit detected: $destination" }
    } elseif ($entry.originalSha256) { throw "Original file removed concurrently: $destination" }
    $source = Join-Path $stage $entry.path
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $entry.sha256) { throw "Staged file changed after review: $source" }
}
foreach ($entry in $manifest.files) {
    $destination = Join-Path $resolvedRoot $entry.path
    New-Item -ItemType Directory -Force -Path (Split-Path $destination) | Out-Null
    Copy-Item -LiteralPath (Join-Path $stage $entry.path) -Destination $destination
}
Write-Output "Published $($manifest.files.Count) reviewed files to $resolvedRoot; other files left intact."
