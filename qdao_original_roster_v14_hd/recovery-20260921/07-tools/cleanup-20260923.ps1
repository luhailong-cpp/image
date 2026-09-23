param([ValidateSet('plan','workspace','external')][string]$Mode = 'plan')
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$genRoot = Join-Path $taskRoot '07-generation'
$toolsRoot = $PSScriptRoot
$previewsRoot = Join-Path $taskRoot '07-delivery-preview'
$ledgerPath = Join-Path $toolsRoot 'cleanup-20260923.json'
$utf8 = [Text.UTF8Encoding]::new($false)
$keepAttempts = @('idle-N-v2','idle-SW-v1','idle-W-v1','walk-N-01-v1','walk-N-02-v1','walk-N-03-v1','walk-N-04-v1','walk-N-05-v1','walk-N-06-v1','walk-N-13-v1','walk-N-09-v2','walk-SW-01-v1','walk-SW-05-v1','walk-SW-09-v1','walk-SW-13-v1','walk-W-01-v1')
function Save-Ledger($data) { [IO.File]::WriteAllText($ledgerPath, ($data | ConvertTo-Json -Depth 30), $utf8) }
function File-Row($file, $category) { [pscustomobject][ordered]@{path=$file.FullName;sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant();bytes=$file.Length;category=$category;deletedAt=$null} }
if ($Mode -eq 'plan') {
    if (Test-Path -LiteralPath $ledgerPath) { $prior = Get-Content -LiteralPath $ledgerPath -Raw | ConvertFrom-Json; if (@($prior.files | Where-Object deletedAt).Count) { throw 'Existing applied cleanup ledger; do not overwrite.' } }
    $rows = [Collections.Generic.List[object]]::new()
    $protected = [Collections.Generic.List[object]]::new()
    foreach ($f in Get-ChildItem -LiteralPath (Join-Path $toolsRoot 'candidate/07_moon_shadow_assassin_girl') -Recurse -File -Filter '*.png') { $protected.Add((File-Row $f 'current_candidate')) }
    foreach ($f in Get-ChildItem -LiteralPath $genRoot -Recurse -File -Filter 'raw.png') {
        $id = $f.Directory.Name
        if ($id -in $keepAttempts) { $protected.Add((File-Row $f 'unique_work_in_progress')); continue }
        $row = File-Row $f 'generation_source_or_rejected'
        $rows.Add($row)
        $resultPath = Join-Path $f.Directory.FullName 'result.json'
        if (Test-Path -LiteralPath $resultPath) {
            $result = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
            $sourcePath = $result.original_generated_file
            if (-not $sourcePath -and $result.output_hint -match ' as (.+?\.png) by default') { $sourcePath = $Matches[1] }
            if ($sourcePath -and (Test-Path -LiteralPath $sourcePath)) {
                $sourceFile = Get-Item -LiteralPath $sourcePath
                $allowedDefault = [IO.Path]::GetFullPath('C:/Users/Administrator/.codex/generated_images') + [IO.Path]::DirectorySeparatorChar
                if (-not $sourceFile.FullName.StartsWith($allowedDefault, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected generated source root' }
                $externalRow = File-Row $sourceFile 'host_generated_source'
                if ($externalRow.sha256 -ne $row.sha256) { throw ('Host source SHA differs: ' + $id) }
                $rows.Add($externalRow)
            }
        }
    }
    foreach ($sub in @('archives','exports','selection-history')) {
        $dir = Join-Path $toolsRoot $sub
        if (Test-Path -LiteralPath $dir) {
            foreach ($f in Get-ChildItem -LiteralPath $dir -Recurse -File | Where-Object Extension -In '.png','.gif','.jpg','.jpeg','.webp') { $rows.Add((File-Row $f $sub)) }
        }
    }
    foreach ($dir in Get-ChildItem -LiteralPath $previewsRoot -Directory | Where-Object Name -NE 'current-review-20260923') {
        foreach ($f in Get-ChildItem -LiteralPath $dir.FullName -Recurse -File | Where-Object Extension -In '.png','.gif','.jpg','.jpeg','.webp','.html') { $rows.Add((File-Row $f 'obsolete_preview')) }
    }
    $data = [ordered]@{schemaVersion=1;scope='07_moon_shadow_assassin_girl only';authorization='User 2026-09-23: delete originals and rollback versions; retain current game assets/designs and necessary textual provenance';plannedAt=[DateTimeOffset]::UtcNow.ToString('o');status='planned';preCleanupVerification=(Join-Path $toolsRoot 'pre-cleanup-verification-20260923.json');protected=$protected;files=@($rows | Sort-Object path -Unique);note='Current 69 candidate PNG are not art-approved. Sixteen unique unfinished sources remain temporarily. No image backup is created.'}
    Save-Ledger $data
} else {
    $data = Get-Content -LiteralPath $ledgerPath -Raw | ConvertFrom-Json
    foreach ($f in $data.protected) { if (-not (Test-Path -LiteralPath $f.path) -or (Get-FileHash -LiteralPath $f.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256) { throw ('Protected image changed: '+$f.path) } }
    foreach ($f in $data.files) {
        if ($f.deletedAt) { continue }
        $isExternal = $f.category -eq 'host_generated_source'
        if (($Mode -eq 'external') -ne $isExternal) { continue }
        $resolved = [IO.Path]::GetFullPath($f.path)
        $allowedRoots = if ($isExternal) { @('C:/Users/Administrator/.codex/generated_images') } else { @($genRoot,$toolsRoot,$previewsRoot) }
        $allowed = $false
        foreach ($dir in $allowedRoots) { $prefix = [IO.Path]::GetFullPath($dir) + [IO.Path]::DirectorySeparatorChar; if ($resolved.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { $allowed=$true } }
        if (-not $allowed) { throw ('Refusing out-of-scope path: '+$resolved) }
        if (Test-Path -LiteralPath $resolved) {
            if ((Get-Item -LiteralPath $resolved).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Refusing reparse point' }
            if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256) { throw ('Changed since plan: '+$resolved) }
            Remove-Item -LiteralPath $resolved -Force
        }
        $f.deletedAt = [DateTimeOffset]::UtcNow.ToString('o')
        Save-Ledger $data
    }
    $remaining = @($data.files | Where-Object { -not $_.deletedAt }).Count
    $data.status = if ($remaining) { 'partial' } else { 'completed' }
    Save-Ledger $data
}
$current = Get-Content -LiteralPath $ledgerPath -Raw | ConvertFrom-Json
$deleted = @($current.files | Where-Object deletedAt)
[ordered]@{status=$current.status;planned=$current.files.Count;deleted=$deleted.Count;deletedBytes=($deleted | Measure-Object bytes -Sum).Sum;protected=$current.protected.Count;byCategory=($current.files | Group-Object category | Select-Object Name,Count)} | ConvertTo-Json -Depth 5
