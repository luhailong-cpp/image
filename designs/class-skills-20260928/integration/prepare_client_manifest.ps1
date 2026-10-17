param([string]$ClientRoot = 'E:/work/mmorpg-client')
$ErrorActionPreference = 'Stop'
$stageRoot = Join-Path $PSScriptRoot 'client'
$baseline = Get-Content -Raw (Join-Path $PSScriptRoot 'client-baseline.json') | ConvertFrom-Json -AsHashtable
$dirty = @(& git -c "safe.directory=$ClientRoot" -C $ClientRoot diff --name-only)
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect concurrent client edits' }
$files = @()
Get-ChildItem -LiteralPath $stageRoot -Recurse -File | Sort-Object FullName | ForEach-Object {
    $relative = [IO.Path]::GetRelativePath($stageRoot, $_.FullName).Replace('\', '/')
    $target = Join-Path $ClientRoot $relative
    $stagedHash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    $originalHash = $null
    if (Test-Path -LiteralPath $target) {
        $originalHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
        if ($originalHash -eq $stagedHash) { return }
        if ($baseline.ContainsKey($relative)) {
            if ($originalHash -ne $baseline[$relative]) { throw "Concurrent edit since inspection: $relative" }
        } elseif ($dirty -contains $relative) {
            throw "Unreviewed concurrent client edit: $relative"
        }
    }
    $files += [ordered]@{path=$relative; sha256=$stagedHash; originalSha256=$originalHash}
}
$manifest = [ordered]@{target=$ClientRoot; generatedUtc=[DateTime]::UtcNow.ToString('O'); files=$files}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'client-publish-manifest.json') -Encoding utf8
Write-Output "Prepared $($files.Count) client files; identical files and unrelated edits excluded."
