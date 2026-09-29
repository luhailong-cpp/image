param([switch]$Execute)
$ErrorActionPreference = 'Stop'
$recoveryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$generationRoot = (Resolve-Path (Join-Path $recoveryRoot '09-generation')).Path
$deliveryRoot = (Resolve-Path (Join-Path $recoveryRoot '09-delivery-preview')).Path
$finalRoot = (Resolve-Path (Join-Path $deliveryRoot 'final')).Path
$plan = Get-Content -LiteralPath (Join-Path $finalRoot 'cleanup-plan.json') -Raw | ConvertFrom-Json
$acceptance = Get-Content -LiteralPath (Join-Path $finalRoot 'acceptance.json') -Raw | ConvertFrom-Json
if ($plan.character -ne '09_bamboo_archer_girl' -or $acceptance.status -ne 'passed') { throw 'Require accepted character 09 final package' }
$checksums = Get-Content -LiteralPath (Join-Path $finalRoot 'package-checksums.json') -Raw | ConvertFrom-Json
foreach ($item in $checksums.files.PSObject.Properties) {
    $p = [IO.Path]::GetFullPath((Join-Path $finalRoot $item.Name))
    if (-not $p.StartsWith($finalRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Package reference escapes final' }
    if ((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.Value) { throw "Final SHA differs: $p" }
}
$entries = $plan.files
if (-not $entries) { throw 'Cleanup plan has no files' }
$bytes = [long]0
foreach ($item in $entries) {
    $p = [IO.Path]::GetFullPath($item.path)
    $withinGeneration = $p.StartsWith($generationRoot + '\', [StringComparison]::OrdinalIgnoreCase)
    $withinDelivery = $p.StartsWith($deliveryRoot + '\', [StringComparison]::OrdinalIgnoreCase)
    if ((-not $withinGeneration -and -not $withinDelivery) -or $p.StartsWith($finalRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe target: $p" }
    $file = Get-Item -LiteralPath $p
    if ($file.PSIsContainer -or $file.Attributes.HasFlag([IO.FileAttributes]::ReparsePoint)) { throw "Linked/non-file target: $p" }
    $parent = $file.Directory
    while ($parent -and $parent.FullName -ne $recoveryRoot) {
        if ($parent.Attributes.HasFlag([IO.FileAttributes]::ReparsePoint)) { throw "Linked ancestor: $p" }
        $parent = $parent.Parent
    }
    if (-not $parent) { throw "Target outside recovery root: $p" }
    if ($file.Length -ne $item.bytes -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Cleanup source changed: $p" }
    $bytes += $file.Length
}
if (-not $Execute) { @{status='validated_only'; files=$entries.Count; bytes=$bytes; final=$finalRoot} | ConvertTo-Json; exit 0 }
$log = Join-Path $finalRoot 'cleanup-executed.jsonl'
if (Test-Path -LiteralPath $log) { throw 'Execution log already exists' }
foreach ($item in $entries) {
    Remove-Item -LiteralPath $item.path -Force
    if (Test-Path -LiteralPath $item.path) { throw "Delete did not complete: $($item.path)" }
    @{path=$item.path;sha256=$item.sha256;bytes=$item.bytes;deleted=$true;at=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath $log -Encoding utf8
}
@{character='09_bamboo_archer_girl';status='completed';files=$entries.Count;bytes=$bytes;completedAt=[DateTime]::UtcNow.ToString('o');scope='Only exact SHA-verified project-local 09 generation and processing files in accepted cleanup plan';externalPortraitPreserved=$true;approvedDesignsPreserved=$true;otherCharactersUntouched=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $finalRoot 'cleanup-result.json') -Encoding utf8
Get-Content -LiteralPath (Join-Path $finalRoot 'cleanup-result.json')
