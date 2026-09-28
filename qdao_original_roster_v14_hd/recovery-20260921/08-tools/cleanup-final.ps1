param(
    [ValidateSet('Plan','Execute')][string]$Mode = 'Plan',
    [switch]$Workspace,
    [switch]$HostImages,
    [string]$PlanSha256
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$recovery = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$roots = @('08-generation','08-delivery-preview','08-tools') | ForEach-Object { Join-Path $recovery $_ }
$generation = $roots[0]
$final = [IO.Path]::GetFullPath((Join-Path $roots[1] 'revisions/final-v1'))
$planPath = Join-Path $PSScriptRoot 'cleanup-final-plan.json'
$logPath = Join-Path $PSScriptRoot 'cleanup-final-execution.jsonl'
$hostBase = 'C:\Users\Administrator\.codex\generated_images'
# Exact receipt-derived task directories; never enumerate these directories.
$hostRoots = @(
    '01a0c4a0-fe34-7fb1-8ff9-ec04d26df849','01a0c4a1-a452-7b81-a94b-bc93d11d6dde',
    '01a0c4a5-7a5a-7d22-8f28-1cef8eabd770','01a0c4a6-00bf-7d00-bff5-5b1917254c68',
    '01a0cda6-5d2e-7e71-a207-ed82930265d3','01a0cda9-3a5c-7f70-9840-5c1ac836b6ff',
    '01a0cdaa-f372-7d41-af83-6284b8e29519','01a0ce0a-c541-71b1-aa07-eea080a0cacd',
    '01a0ce0b-3d46-72c1-a68a-ff704986576e','01a0ce0b-ff0f-7133-ae2a-c29c6445da15'
) | ForEach-Object { Join-Path $hostBase $_ }
$imagePattern = '\.(png|jpe?g|gif|webp|bmp|tiff?|avif)$'
function Read-Json($path) { Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json }
function Hash($path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
function In-Root($path, $root) {
    $path.StartsWith($root.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)
}
function Assert-Safe($path, $allowedRoots) {
    $absolute = [IO.Path]::GetFullPath($path)
    if (-not @($allowedRoots | Where-Object { (In-Root $absolute $_) -or $absolute -eq $_ }).Count) { throw "Out of scope: $absolute" }
    $cursor = $absolute
    while ($cursor) {
        $item = Get-Item -LiteralPath $cursor -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point: $cursor" }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
    $absolute
}
function Safe-Files($root) {
    $null = Assert-Safe $root @($root)
    foreach ($item in Get-ChildItem -LiteralPath $root -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point: $($item.FullName)" }
        if ($item.PSIsContainer) { Safe-Files $item.FullName } else { $item }
    }
}
function Record($path) {
    $item = Get-Item -LiteralPath $path
    [ordered]@{path=$item.FullName; bytes=$item.Length; sha256=(Hash $item.FullName)}
}
function Assert-Hash($path, $sha) {
    if ((Hash $path) -ne $sha) { throw "SHA changed: $path" }
}
function Final-Locks {
    $mp = Join-Path $final 'manifest.json'
    $ap = Join-Path $final 'file-audit-before-cleanup.json'
    $null = Assert-Safe $mp @($final)
    $null = Assert-Safe $ap @($final)
    $m = Read-Json $mp
    $a = Read-Json $ap
    if ($a.status -ne 'passed_file_checks_only' -or $a.verified_frames -ne 136 -or @($a.errors).Count -ne 0) { throw 'Final file audit has not passed.' }
    Assert-Hash $mp $a.manifest_sha256
    if ($m.actual_walk -ne 128 -or $m.actual_idle -ne 8 -or @($m.files).Count -ne 136 -or @($m.missing).Count -ne 0 -or -not $m.visual_approval -or -not $m.browser_review_performed) { throw 'Final inventory or visual acceptance incomplete.' }
    $slots = foreach ($d in @('N','NE','E','SE','S','SW','W','NW')) { "idle/$d"; 1..16 | ForEach-Object { 'walk/{0}/{1:00}' -f $d,$_ } }
    if (@(Compare-Object ($slots | Sort-Object) ($m.files.slot | Sort-Object)).Count) { throw 'Final 136 slots differ.' }
    $rows = @($m.files) + @($m.gifs) + @($m.contact_sheets)
    if (@($m.gifs).Count -ne 16) { throw 'Expected 16 light/dark GIFs.' }
    foreach ($row in $rows) {
        $p = Assert-Safe (Join-Path $final $row.path) @($final)
        Assert-Hash $p $row.sha256
        Record $p
    }
    $actual = @(Safe-Files $final | Where-Object { $_.Name -match $imagePattern } | ForEach-Object { $_.FullName } | Sort-Object)
    $declared = @($rows | ForEach-Object { [IO.Path]::GetFullPath((Join-Path $final $_.path)) } | Sort-Object)
    if (@(Compare-Object $actual $declared).Count) { throw 'Final image list differs from manifest.' }
    foreach ($row in $m.files) {
        $source = Assert-Safe (Join-Path $final $row.source_record) @($final)
        Assert-Hash $source $row.source_record_sha256
    }
    $index = Join-Path $final 'index.html'
    $html = Get-Content -LiteralPath $index -Raw -Encoding UTF8
    $embeddedMatch = [regex]::Match($html, '(?s)const M=(\{.*?\}), \$=id=>')
    if (-not $embeddedMatch.Success) { throw 'Cannot verify embedded preview manifest.' }
    $embedded = $embeddedMatch.Groups[1].Value | ConvertFrom-Json
    if (@($embedded.files).Count -ne 136) { throw 'Preview does not reference all 136 final images.' }
    foreach ($row in $embedded.files) {
        $p = Assert-Safe (Join-Path $final $row.path) @($final)
        Assert-Hash $p $row.sha256
        if (-not @($m.files | Where-Object { $_.slot -eq $row.slot -and $_.path -eq $row.path -and $_.sha256 -eq $row.sha256 }).Count) { throw 'Embedded preview differs from manifest.' }
    }
    foreach ($name in @('index.html','previews.html')) {
        $p = Join-Path $final $name
        $html = Get-Content -LiteralPath $p -Raw -Encoding UTF8
        foreach ($match in [regex]::Matches($html, '(?:href|src)="([^"]+)"')) {
            $ref = $match.Groups[1].Value
            if ($ref -match '^(https?:|data:|#)') { continue }
            $null = Assert-Safe (Join-Path $final $ref) @($final)
        }
        Record $p
    }
    Record $mp
    Record $ap
}
if ($Mode -eq 'Plan') {
    if ($Workspace -or $HostImages) { throw 'Scope switches are for Execute only.' }
    if (Test-Path -LiteralPath $planPath) { throw 'Plan already exists; review it, never silently overwrite its lock.' }
    $locks = @(Final-Locks)
    $workspaceRows = @(foreach ($root in $roots) {
        foreach ($item in Safe-Files $root) {
            if ($item.Name -match $imagePattern -and -not (In-Root $item.FullName $final)) {
                $p = Assert-Safe $item.FullName $roots
                Record $p
            }
        }
    })
    $hostRows = @(foreach ($receiptFile in Safe-Files $generation | Where-Object { $_.Name -eq 'receipt.json' }) {
        $receipt = Read-Json $receiptFile.FullName
        $receiptMatches = [regex]::Matches($receipt.output_hint, 'C:\\Users\\Administrator\\\.codex\\generated_images\\[0-9a-f-]{36}\\exec-[0-9a-f-]{36}\.png')
        if ($receiptMatches.Count -ne 1) { throw "Ambiguous receipt: $($receiptFile.FullName)" }
        $hp = Assert-Safe $receiptMatches[0].Value $hostRoots
        if ([IO.Path]::GetDirectoryName($hp) -notin $hostRoots) { throw "Unexpected host nesting: $hp" }
        $raw = Assert-Safe (Join-Path $receiptFile.DirectoryName 'raw.png') @($generation)
        $rawSha = Hash $raw
        Assert-Hash $hp $rawSha
        $row = Record $hp
        $row.receipt = $receiptFile.FullName
        $row.receipt_sha256 = Hash $receiptFile.FullName
        $row.raw = $raw
        $row.raw_sha256 = $rawSha
        $row
    })
    if ($hostRows.Count -ne 186 -or @($hostRows.path | Sort-Object -Unique).Count -ne 186) { throw 'Expected exactly 186 unique receipt-mapped host files.' }
    $textLocks = @(foreach ($root in @($generation, (Join-Path $roots[1] 'processed'))) {
        foreach ($item in Safe-Files $root | Where-Object { $_.Extension -in @('.json','.txt') }) { Record $item.FullName }
    })
    if (@($workspaceRows | Where-Object { In-Root $_.path $final }).Count) { throw 'A final asset entered the deletion plan.' }
    $plan = [ordered]@{schema='qdao08-final-cleanup-lock-v1'; createdAt=[DateTime]::UtcNow.ToString('o'); script_sha256=(Hash $PSCommandPath); final=$final; finalLocks=$locks; textLocks=$textLocks; workspace=$workspaceRows; host=$hostRows; scope='Individual image files only; all text and entire final-v1 preserved.'}
    $plan | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $planPath -Encoding UTF8
    [pscustomobject]@{plan=$planPath; sha256=(Hash $planPath); workspace_images=$workspaceRows.Count; host_images=$hostRows.Count; protected_files=$locks.Count; protected_text_files=$textLocks.Count} | ConvertTo-Json
    exit
}
if (($Workspace -and $HostImages) -or (-not $Workspace -and -not $HostImages)) { throw 'Choose exactly one of -Workspace or -HostImages.' }
if ($PlanSha256 -notmatch '^[0-9a-fA-F]{64}$') { throw 'Execute requires the reviewed plan SHA256.' }
$null = Assert-Safe $planPath @($PSScriptRoot)
Assert-Hash $planPath $PlanSha256
$plan = Read-Json $planPath
Assert-Hash $PSCommandPath $plan.script_sha256
if ($plan.final -ne $final) { throw 'Plan final path changed.' }
$freshLocks = @(Final-Locks)
foreach ($row in $plan.finalLocks) { $null = Assert-Safe $row.path @($final); Assert-Hash $row.path $row.sha256 }
foreach ($row in $plan.textLocks) { $null = Assert-Safe $row.path $roots; Assert-Hash $row.path $row.sha256 }
if ($freshLocks.Count -ne @($plan.finalLocks).Count) { throw 'Final protected file count changed.' }
$scope = if ($Workspace) { 'workspace' } else { 'host' }
$candidates = @($plan.$scope)
$previous = @{}
if (Test-Path -LiteralPath $logPath) {
    foreach ($line in Get-Content -LiteralPath $logPath -Encoding UTF8) { if ($line) { $entry=$line|ConvertFrom-Json; if ($entry.status -eq 'deleted' -and $entry.plan_sha256 -eq $PlanSha256) { $previous[$entry.path]=$entry.sha256 } } }
}
# Preflight the entire chosen scope before any deletion. Missing files require this plan's completed deletion log.
foreach ($row in $candidates) {
    if (-not (Test-Path -LiteralPath $row.path)) {
        if ($previous.ContainsKey($row.path) -and $previous[$row.path] -eq $row.sha256) { continue }
        throw "Unaccounted missing candidate: $($row.path)"
    }
    $allowed = if ($Workspace) { $roots } else { $hostRoots }
    $p = Assert-Safe $row.path $allowed
    if ((In-Root $p $final) -or $p -notmatch $imagePattern) { throw "Protected or non-image: $p" }
    Assert-Hash $p $row.sha256
    if (-not $Workspace) {
        $null = Assert-Safe $row.receipt @($generation)
        Assert-Hash $row.receipt $row.receipt_sha256
        $receipt = Read-Json $row.receipt
        if (-not $receipt.output_hint.Contains($p) -or $row.raw_sha256 -ne $row.sha256) { throw "Receipt mapping changed: $p" }
        if (Test-Path -LiteralPath $row.raw) { Assert-Hash (Assert-Safe $row.raw @($generation)) $row.raw_sha256 }
    }
}
$deleted = 0
foreach ($row in $candidates) {
    if (-not (Test-Path -LiteralPath $row.path)) { continue }
    $allowed = if ($Workspace) { $roots } else { $hostRoots }
    $p = Assert-Safe $row.path $allowed
    Assert-Hash $p $row.sha256
    $entry = [ordered]@{at=[DateTime]::UtcNow.ToString('o'); scope=$scope; path=$p; sha256=$row.sha256; bytes=$row.bytes; plan_sha256=$PlanSha256; status='deleting'}
    $entry | ConvertTo-Json -Compress | Add-Content -LiteralPath $logPath -Encoding UTF8
    Remove-Item -LiteralPath $p
    $entry.status='deleted'; $entry.at=[DateTime]::UtcNow.ToString('o')
    $entry | ConvertTo-Json -Compress | Add-Content -LiteralPath $logPath -Encoding UTF8
    $deleted++
}
foreach ($row in $plan.textLocks) { $null = Assert-Safe $row.path $roots; Assert-Hash $row.path $row.sha256 }
[pscustomobject]@{scope=$scope; deleted=$deleted; log=$logPath; plan_sha256=$PlanSha256} | ConvertTo-Json
