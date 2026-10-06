$ErrorActionPreference = 'Stop'
$logPath = Join-Path $PSScriptRoot 'retention-log.json'
$plan = Get-Content -LiteralPath $logPath -Raw | ConvertFrom-Json
if ($plan.status -ne 'planned_not_deleted') { throw 'Plan must be reviewed and in planned state.' }
$rootPath = [IO.Path]::GetFullPath($plan.root).TrimEnd('\')
$allowed = @($plan.allowedDirectories | ForEach-Object { [IO.Path]::GetFullPath($_).TrimEnd('\') + '\' })
if ((Get-FileHash -LiteralPath $plan.final.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.final.sha256) { throw 'Final hash changed.' }
if ((Get-FileHash -LiteralPath $plan.oldWestSource.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.oldWestSource.sha256) { throw 'Old west hash changed.' }
$checked = @()
foreach ($entry in $plan.deleted) {
    $path = [IO.Path]::GetFullPath($entry.path)
    if (-not $path.StartsWith($rootPath + '\',[StringComparison]::OrdinalIgnoreCase)) { throw "Outside ROOT: $path" }
    if ($path -match '\\r10_c1[23]\\') { throw "Protected r10 path: $path" }
    $inAllowed = $false
    foreach ($dir in $allowed) { if ($path.StartsWith($dir,[StringComparison]::OrdinalIgnoreCase)) { $inAllowed = $true } }
    if (-not $inAllowed) { throw "Outside allowed directories: $path" }
    $item = Get-Item -LiteralPath $path
    if ($item.PSIsContainer) { throw "Not an individual file: $path" }
    $ancestor = $item
    while ($null -ne $ancestor -and $ancestor.FullName.StartsWith($rootPath,[StringComparison]::OrdinalIgnoreCase)) {
        if (($ancestor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse path forbidden: $path" }
        $ancestor = if ($ancestor.PSIsContainer) { $ancestor.Parent } else { $ancestor.Directory }
    }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "Input changed: $path" }
    $checked += $path
}
# All absolute targets validated before the first deletion. Native PowerShell only, no recursive delete.
$removed = 0
foreach ($path in $checked) { Remove-Item -LiteralPath $path -Force; $removed += 1 }
$plan.status = 'deleted_pending_text_retirement'
$plan.deletedCount = $removed
$plan | Add-Member -NotePropertyName deletedAt -NotePropertyValue ([DateTime]::UtcNow.ToString('o')) -Force
$plan | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $logPath -Encoding UTF8
Write-Output "Deleted $removed verified c13 historical files. Final runtime PNG untouched."
