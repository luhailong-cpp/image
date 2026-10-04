$ErrorActionPreference = 'Stop'
$taskBase = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$expectedBase = 'D:\work\image\qdao_original_roster_v14_hd\action-remake-20261001\characters\17_ghost_script_calligrapher_boy'
if ($taskBase -ne $expectedBase) { throw 'Wrong cleanup workspace' }
$externalBase = 'C:\Users\luyua\.codex\generated_images\01a0f77a-fb47-7bd0-8402-cf6df9512a1c'
$planPath = Join-Path $taskBase 'cleanup-plan.json'
$plan = Get-Content -Raw -LiteralPath $planPath | ConvertFrom-Json
if ($plan.status -ne 'ready_for_cleanup_review' -or $plan.manifestStatus -ne 'passed' -or $plan.validatedRuntimeFrames -ne 196) { throw 'Final cleanup prerequisites missing' }
function Assert-Hash([string]$file, [string]$hash) {
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hash) { throw "Changed file: $file" }
}
Assert-Hash (Join-Path $taskBase 'manifest.json') $plan.manifestSha256
Assert-Hash (Join-Path $taskBase 'preview\delivery.html') $plan.deliveryChecks.htmlSha256
Assert-Hash (Join-Path $taskBase 'preview\delivery-data.json') $plan.deliveryChecks.dataSha256
$candidates = @()
foreach ($item in $plan.localCandidates) {
    $absolute = [IO.Path]::GetFullPath((Join-Path $taskBase $item.file))
    if (-not $absolute.StartsWith($taskBase + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Candidate escapes task' }
    if ($item.file -notmatch '^(staging|review|preview)/' -or [IO.Path]::GetExtension($absolute) -notin @('.png','.jpg','.jpeg','.webp','.gif','.avif','.bmp')) { throw 'Unexpected local candidate' }
    if ($absolute -eq (Join-Path $taskBase 'preview\run-current-1200ms.webp')) { throw 'Formal preview is protected' }
    $candidates += [pscustomobject]@{file=$absolute;sha256=$item.sha256;bytes=$item.bytes;scope='local'}
}
foreach ($item in $plan.externalCandidates) {
    $absolute = [IO.Path]::GetFullPath($item.file)
    if (-not $absolute.StartsWith($externalBase + '\', [StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetExtension($absolute) -ne '.png') { throw 'External candidate escapes exact recorded thread root' }
    $candidates += [pscustomobject]@{file=$absolute;sha256=$item.sha256;bytes=$item.bytes;scope='same_thread_original'}
}
# Resolve and validate every literal target before deleting any file.
foreach ($item in $candidates) {
    $actual = Get-Item -LiteralPath $item.file
    if ($actual.PSIsContainer -or $actual.LinkType) { throw 'Deletion target must be a regular image file' }
    Assert-Hash $item.file $item.sha256
}
$deleted = @()
$errors = @()
foreach ($item in $candidates) {
    try {
        Assert-Hash $item.file $item.sha256
        Remove-Item -LiteralPath $item.file
        $deleted += $item
    } catch { $errors += [pscustomobject]@{file=$item.file;error=$_.Exception.Message} }
}
$report = [ordered]@{
    character='17_ghost_script_calligrapher_boy'
    status=$(if ($errors.Count -eq 0) {'completed'} else {'partial_failure'})
    completedAt=[DateTimeOffset]::UtcNow.ToString('o')
    authorization='User AGENTS.md 2026-09-23 retention policy; final runtime and active references verified before removal'
    planSha256=(Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant()
    manifestSha256=$plan.manifestSha256
    deletedImages=$deleted.Count
    deletedBytes=($deleted | Measure-Object -Property bytes -Sum).Sum
    preserved='196 runtime PNGs, formal run WebP, all generation/model/quality/source text, old external formal libraries'
    deleted=$deleted
    errors=$errors
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskBase 'cleanup-report.json') -Encoding utf8
[pscustomobject]@{status=$report.status;deletedImages=$deleted.Count;errors=$errors.Count} | ConvertTo-Json -Compress
if ($errors.Count) { exit 2 }
