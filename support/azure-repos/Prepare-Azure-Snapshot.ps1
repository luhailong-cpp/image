#requires -Version 7.0
[CmdletBinding()]
param(
    [ValidateSet('Inventory', 'Plan', 'Export', 'Compare')][string]$Action = 'Inventory',
    [string]$SourcePath,
    [Parameter(Mandatory)][string]$OutputPath,
    [string]$PlanPath,
    [string]$OtherPlanPath,
    [string[]]$AdditionalExclude = @(),
    [switch]$AllowIncompleteSparse
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$utf8 = [Text.UTF8Encoding]::new($false)
$script:CheckedDirectories = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$script:CheckedRepositoryDirectories = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$script:SparsePaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$script:FilterOverrides = @()

function Full-Path([string]$Value) {
    if (-not $Value -or -not [IO.Path]::IsPathFullyQualified($Value) -or $Value.StartsWith('\\')) { throw 'Use an absolute local disk path.' }
    $full = [IO.Path]::GetFullPath($Value).TrimEnd('\', '/')
    if ($full -eq [IO.Path]::GetPathRoot($full).TrimEnd('\', '/')) { throw 'A drive root is not a valid source or output.' }
    return $full
}
function Assert-NoLinks([string]$Path) {
    $cursor = $Path
    while ($cursor) {
        if ($script:CheckedDirectories.Contains($cursor)) { break }
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point or symlink is not allowed: $cursor" }
            if (Test-Path -LiteralPath $cursor -PathType Container) { [void]$script:CheckedDirectories.Add($cursor) }
        }
        $parent = Split-Path -Parent $cursor
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
}
function Is-Within([string]$Child, [string]$Parent) {
    return $Child.Equals($Parent, [StringComparison]::OrdinalIgnoreCase) -or $Child.StartsWith($Parent + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)
}
function Relative-Path([string]$Value) {
    if (-not $Value -or $Value.Contains('\') -or $Value.StartsWith('/') -or $Value.Contains(':') -or $Value -match '[\x00-\x1f]') { throw "Invalid relative path in manifest: $Value" }
    $parts = $Value.Split('/')
    foreach ($part in $parts) {
        if (-not $part -or $part -in @('.', '..') -or $part.EndsWith('.') -or $part.EndsWith(' ') -or $part -match '^(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)') { throw "Unsafe Windows path: $Value" }
    }
    return $Value
}
function Exclusion-Reason([string]$Relative) {
    $parts = $Relative.Split('/')
    foreach ($part in $parts) {
        if ($part -in @('.git', '.cache', '.codex', '.aws', '.ssh', '.azure', 'node_modules', '__pycache__')) { return "Local-only directory: $part" }
    }
    $leaf = $parts[-1]
    if ($Relative.Equals('designs/team-invites-20260928/live-acceptance/robot.yaml', [StringComparison]::OrdinalIgnoreCase)) { return 'Known local acceptance-test account configuration; may contain credentials. Recreate a sanitized template separately if needed.' }
    if ($Relative.StartsWith('designs/team-invites-20260928/', [StringComparison]::OrdinalIgnoreCase)) {
        if ($Relative.StartsWith('designs/team-invites-20260928/aoi-fix/build/', [StringComparison]::OrdinalIgnoreCase) -or $leaf -match '(?i)\.(exe|pdb|obj|ilk|tlog)$' -or $leaf -match '(?i)\.log(?:\.(stderr|stdout)\.txt)?$') { return 'Known team-invites build output or raw acceptance log; no formal game executable excluded elsewhere.' }
    }
    if ($Relative.StartsWith('designs/class-skills-20260928/integration/', [StringComparison]::OrdinalIgnoreCase)) {
        if ($Relative -match '(?i)^designs/class-skills-20260928/integration/(\.contract-generation|python-deps)/') { return 'Known generated contract tool/dependency cache.' }
        if ($Relative -match '(?i)^designs/class-skills-20260928/integration/\.client-validation/(?:.*?/)?(?:bin|obj)/' -or $Relative -match '(?i)^designs/class-skills-20260928/integration/\.client-validation/.*\.dll$') { return 'Known client-validation compiled output; source/config/results retained.' }
    }
    if ($leaf -eq '.lfsconfig') { return 'Old LFS endpoint configuration; must not accompany Azure snapshot.' }
    if ($leaf -eq '.env' -or ($leaf.StartsWith('.env.') -and $leaf -notmatch '\.(example|sample|template)$')) { return 'Local environment / possible credentials.' }
    if ($leaf -match '(?i)^(id_(rsa|ed25519|ecdsa|dsa)(\.pub)?|credentials|credentials\.json|gcm[-.].*\.log)$' -or $leaf -match '(?i)\.(pfx|p12|key|pem)$') { return 'Credential or authentication diagnostic filename.' }
    foreach ($prefix in $AdditionalExclude) {
        $prefix = (Relative-Path $prefix.TrimEnd('/'))
        if ($Relative.Equals($prefix, [StringComparison]::OrdinalIgnoreCase) -or $Relative.StartsWith($prefix + '/', [StringComparison]::OrdinalIgnoreCase)) { return "Explicit exclusion: $prefix" }
    }
    return $null
}
function Git-Read([string[]]$Arguments, [string]$InputText = '', [switch]$AllowNoMatch) {
    $start = [Diagnostics.ProcessStartInfo]::new($script:Git)
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.RedirectStandardInput = $true
    $start.StandardOutputEncoding = $utf8
    $start.StandardErrorEncoding = $utf8
    $start.StandardInputEncoding = $utf8
    foreach ($argument in @('--no-optional-locks', '-c', 'core.fsmonitor=false', '-c', 'core.quotePath=false', '-c', 'protocol.allow=never') + $script:FilterOverrides + $Arguments) { [void]$start.ArgumentList.Add($argument) }
    foreach ($name in @('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_CONFIG_COUNT')) {
        if ($start.Environment[$name]) { throw "A Git override is set: $name. Start a clean PowerShell session." }
    }
    $start.Environment['GIT_NO_LAZY_FETCH'] = '1'
    $start.Environment['GIT_ALLOW_PROTOCOL'] = ''
    $start.Environment['GIT_TERMINAL_PROMPT'] = '0'
    $start.Environment['GCM_INTERACTIVE'] = 'never'
    $start.Environment['GIT_OPTIONAL_LOCKS'] = '0'
    foreach ($name in @('GIT_TRACE', 'GIT_TRACE_CURL', 'GIT_CURL_VERBOSE', 'GIT_TRACE_PACKET')) { [void]$start.Environment.Remove($name) }
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    [void]$process.Start()
    $outTask = $process.StandardOutput.ReadToEndAsync()
    $errTask = $process.StandardError.ReadToEndAsync()
    $process.StandardInput.Write($InputText)
    $process.StandardInput.Close()
    $process.WaitForExit()
    $stdout = $outTask.GetAwaiter().GetResult()
    $stderr = $errTask.GetAwaiter().GetResult()
    $exitCode = $process.ExitCode
    $process.Dispose()
    if ($exitCode -ne 0 -and -not ($AllowNoMatch -and $exitCode -eq 1)) { throw "Read-only Git command failed ($exitCode): $stderr" }
    return $stdout
}
function Assert-Source([string]$Path) {
    Assert-NoLinks $Path
    if (-not (Test-Path -LiteralPath (Join-Path $Path '.git') -PathType Container)) { throw 'Source must be an ordinary checkout with its own .git directory.' }
    $actual = (Git-Read @('-C', $Path, 'rev-parse', '--show-toplevel')).Trim()
    if ((Full-Path $actual) -ne $Path) { throw 'Source must be the exact repository root.' }
    foreach ($state in @('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-apply', 'rebase-merge')) {
        if (Test-Path -LiteralPath (Join-Path $Path ".git/$state")) { throw "Unfinished Git operation: $state" }
    }
    $sparse = Git-Read @('-C', $Path, 'ls-files', '-t', '-z')
    foreach ($entry in $sparse.Split([char]0)) { if ($entry.StartsWith('S ')) { [void]$script:SparsePaths.Add($entry.Substring(2)) } }
    if ($script:SparsePaths.Count -and ($Action -eq 'Export' -or -not $AllowIncompleteSparse)) { throw 'Sparse / skip-worktree entries would create an incomplete snapshot. For a comparison-only manifest use -AllowIncompleteSparse; Export always requires a full checkout.' }
}
function Get-Provenance([string]$Path) {
    return [ordered]@{
        Head = (Git-Read @('-C', $Path, 'rev-parse', '--verify', 'HEAD')).Trim()
        Branch = (Git-Read @('-C', $Path, 'branch', '--show-current')).Trim()
        StatusNul = (Git-Read @('-C', $Path, 'status', '--porcelain=v1', '-z', '--untracked-files=all', '--ignore-submodules=all'))
        StatusPurpose = 'Stability/deletion evidence only. All clean/process filters disabled: LFS worktree files can appear modified even if their pointer content is unchanged.'
    }
}
function Assert-ContentFile([string]$Root, [string]$Relative) {
    $relative = Relative-Path $Relative
    $full = [IO.Path]::GetFullPath((Join-Path $Root $relative))
    if (-not (Is-Within $full $Root)) { throw "Path escaped the source: $relative" }
    Assert-NoLinks $full
    $cursor = Split-Path -Parent $full
    while ($cursor -ne $Root) {
        if ($script:CheckedRepositoryDirectories.Contains($cursor)) { break }
        if (Test-Path -LiteralPath (Join-Path $cursor '.git')) { throw "Nested Git repository must be handled separately: $relative" }
        [void]$script:CheckedRepositoryDirectories.Add($cursor)
        $cursor = Split-Path -Parent $cursor
    }
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw "Not an ordinary file: $relative" }
    $info = Get-Item -LiteralPath $full -Force
    if ($info.Length -le 4096) {
        $prefix = [IO.File]::ReadAllText($full)
        if ($prefix.StartsWith('version https://git-lfs.github.com/spec/v1')) { throw "Unmaterialized LFS pointer: $relative. Restore its actual content locally before planning; this tool never downloads it." }
    }
    return $info
}
function Write-NewJson([string]$Path, [object]$Value) {
    $json = ConvertTo-Json -InputObject $Value -Depth 12
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $writer = [IO.StreamWriter]::new($stream, $utf8); $writer.Write($json); $writer.Flush() }
    finally { $stream.Dispose() }
}
function Read-Plan([string]$Path) {
    $full = Full-Path $Path
    Assert-NoLinks $full
    $plan = Get-Content -LiteralPath $full -Raw -Encoding utf8 | ConvertFrom-Json
    if ($plan.Schema -ne 'azure-current-snapshot-v1' -or $plan.Action -ne 'Plan' -or -not $plan.Complete) { throw 'A completed Plan manifest is required, not Inventory.' }
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in $plan.Files) {
        [void](Relative-Path $entry.Path)
        if (-not $seen.Add($entry.Path)) { throw "Duplicate/case-colliding path: $($entry.Path)" }
        if ($entry.SHA256 -notmatch '^[0-9a-fA-F]{64}$' -or $entry.Bytes -lt 0) { throw "Invalid hash or size: $($entry.Path)" }
        if (Exclusion-Reason $entry.Path) { throw "Plan contains a prohibited path: $($entry.Path)" }
    }
    return $plan
}

$output = Full-Path $OutputPath
Assert-NoLinks $output
if (Test-Path -LiteralPath $output) { throw 'Output already exists; this tool never overwrites or deletes it.' }
if (-not (Test-Path -LiteralPath (Split-Path -Parent $output) -PathType Container)) { throw 'Output parent directory must already exist.' }

if ($Action -eq 'Compare') {
    $left = Read-Plan $PlanPath
    $right = Read-Plan $OtherPlanPath
    $leftIndex = @{}; $rightIndex = @{}
    foreach ($entry in $left.Files) { $leftIndex[$entry.Path] = $entry }
    foreach ($entry in $right.Files) { $rightIndex[$entry.Path] = $entry }
    $differences = [Collections.Generic.List[object]]::new()
    $same = 0
    foreach ($path in @(@($leftIndex.Keys) + @($rightIndex.Keys) | Sort-Object -Unique)) {
        $l = $leftIndex[$path]; $r = $rightIndex[$path]
        if ($l -and $r -and $l.SHA256 -eq $r.SHA256) { $same++; continue }
        $kind = if (-not $l) { 'OnlyRight_ReviewAdditionOrDeletion' } elseif (-not $r) { 'OnlyLeft_ReviewAdditionOrDeletion' } else { 'DifferentContent_ManualMergeRequired' }
        $differences.Add([ordered]@{ Path = $path; Kind = $kind; Left = $l; Right = $r })
    }
    $result = [ordered]@{ Schema = 'azure-snapshot-comparison-v1'; CapturedUtc = [DateTime]::UtcNow.ToString('o'); LeftHead = $left.Provenance.Head; RightHead = $right.Provenance.Head; SameFiles = $same; DifferenceCount = $differences.Count; AutoApplied = $false; Differences = $differences.ToArray(); Note = 'One-sided files may represent additions OR intentional deletions. No automatic union/overwrite is safe without review.' }
    Write-NewJson $output $result
    Write-Host "Comparison complete: $same identical; $($differences.Count) require review. No source files changed. $output"
    return
}

$script:Git = (Get-Command git -ErrorAction Stop | Select-Object -First 1).Source
$gitVersion = Git-Read @('--version')
if ($gitVersion -notmatch 'git version (\d+)\.(\d+)\.' -or [int]$Matches[1] -lt 2 -or ([int]$Matches[1] -eq 2 -and [int]$Matches[2] -lt 46)) { throw 'Git 2.46 or newer is required to reliably disable partial-clone lazy fetching. Update Git for Windows first.' }
$source = Full-Path $SourcePath
if (Is-Within $output $source) { throw 'Output must be outside the source repository, so it cannot be re-exported or auto-committed.' }
if (Is-Within $source $output) { throw 'Output cannot be an ancestor of the source.' }
# Status can invoke clean/process filters. Discover names without executing a filter,
# then disable them for every subsequent read, including LFS (which can write its cache).
Assert-NoLinks $source
$filterNames = Git-Read @('-C', $source, 'config', '--null', '--name-only', '--get-regexp', '^filter\..*\.(clean|process|required)$') '' -AllowNoMatch
$filterSections = @($filterNames.Split([char]0, [StringSplitOptions]::RemoveEmptyEntries) | ForEach-Object { $_ -replace '\.(clean|process|required)$', '' } | Sort-Object -Unique -CaseSensitive)
foreach ($section in @($filterSections) + @('filter.lfs') | Sort-Object -Unique -CaseSensitive) { $script:FilterOverrides += @('-c', "$section.clean=", '-c', "$section.process=", '-c', "$section.required=false") }
Assert-Source $source
$before = Get-Provenance $source
$deletions = [Collections.Generic.List[object]]::new()
$stagedDeletionPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$statusRecords = $before.StatusNul.Split([char]0, [StringSplitOptions]::RemoveEmptyEntries)
for ($i = 0; $i -lt $statusRecords.Count; $i++) {
    $record = $statusRecords[$i]
    $code = $record.Substring(0, 2)
    $relative = $record.Substring(3)
    if ($code.Contains('D')) {
        $deletions.Add([ordered]@{ Path = $relative; IndexStatus = $code.Substring(0, 1); WorktreeStatus = $code.Substring(1, 1) })
        if ($code[0] -eq 'D') { [void]$stagedDeletionPaths.Add($relative) }
    }
    if ($code.Contains('R') -or $code.Contains('C')) { $i++ }
}

if ($Action -eq 'Export') {
    if (Test-Path -LiteralPath ($output + '.receipt.json')) { throw 'The export receipt path already exists; choose a fresh output name.' }
    $plan = Read-Plan $PlanPath
    if (-not $plan.SourceComplete) { throw 'An incomplete/sparse Plan cannot be exported as a full snapshot.' }
    if ((Full-Path $plan.SourcePath) -ne $source -or $plan.Provenance.Head -ne $before.Head -or $plan.Provenance.StatusNul -cne $before.StatusNul) { throw 'Source path, HEAD or working status changed since Plan; generate a fresh Plan.' }
    [void][IO.Directory]::CreateDirectory($output)
    $count = 0
    try {
        foreach ($entry in $plan.Files) {
            $info = Assert-ContentFile $source $entry.Path
            $target = Join-Path $output $entry.Path
            [void][IO.Directory]::CreateDirectory((Split-Path -Parent $target))
            Assert-NoLinks $target
            $input = [IO.File]::Open($info.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
            $out = [IO.File]::Open($target, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
            $hash = [Security.Cryptography.IncrementalHash]::CreateHash([Security.Cryptography.HashAlgorithmName]::SHA256)
            try {
                $buffer = [byte[]]::new(1024 * 1024)
                [long]$bytes = 0
                while (($read = $input.Read($buffer, 0, $buffer.Length)) -gt 0) { $out.Write($buffer, 0, $read); $hash.AppendData($buffer, 0, $read); $bytes += $read }
                $actual = [Convert]::ToHexString($hash.GetHashAndReset()).ToLowerInvariant()
            } finally { $input.Dispose(); $out.Dispose(); $hash.Dispose() }
            if ($bytes -ne $entry.Bytes -or $actual -ne $entry.SHA256) { throw "Content changed after Plan: $($entry.Path). Partial destination retained; do not upload it." }
            $count++
            if ($count % 500 -eq 0) { Write-Progress -Activity 'Export current files, without Git history' -Status "$count / $($plan.Files.Count)" -PercentComplete ($count * 100 / $plan.Files.Count) }
        }
        $after = Get-Provenance $source
        if ($after.Head -ne $before.Head -or $after.StatusNul -cne $before.StatusNul) { throw 'Source changed during Export. Partial destination retained; do not upload it.' }
        # Kept alongside the snapshot, not in it, to avoid re-importing machine-specific paths.
        Write-NewJson ($output + '.receipt.json') ([ordered]@{ Schema = 'azure-snapshot-export-v1'; Complete = $true; SourceHead = $before.Head; FileCount = $count; Bytes = $plan.TotalBytes; PlanSHA256 = (Get-FileHash -LiteralPath $PlanPath -Algorithm SHA256).Hash; ExportPath = $output; CapturedUtc = [DateTime]::UtcNow.ToString('o'); GitHistoryCopied = $false; NetworkUsed = $false })
        Write-Host "Export verified: $count files; no .git, no commits, no upload. $output"
    } finally { Write-Progress -Activity 'Export current files, without Git history' -Completed }
    return
}

$tracked = @{}
$casePaths = @{}
$entries = (Git-Read @('-C', $source, 'ls-files', '--stage', '-z')).Split([char]0, [StringSplitOptions]::RemoveEmptyEntries)
foreach ($entry in $entries) {
    if ($entry -notmatch '^([0-9]+) ([0-9a-f]+) ([0-3])\t([\s\S]+)$') { throw 'Unexpected Git index entry.' }
    $relative = Relative-Path $Matches[4]
    if ($Matches[3] -ne '0') { throw "Unresolved conflict: $relative" }
    if ($casePaths.ContainsKey($relative) -and $casePaths[$relative] -cne $relative) { throw "Case-colliding Git index paths cannot be represented safely on Windows: $relative" }
    $casePaths[$relative] = $relative
    if (Exclusion-Reason $relative) { $tracked[$relative] = 'excluded'; continue }
    if ($Matches[1] -eq '160000') { throw "Submodule / nested repository must be handled separately: $relative" }
    if ($Matches[1] -eq '120000') { throw "Tracked symlink is not supported: $relative" }
    $tracked[$relative] = 'tracked'
}
$untracked = (Git-Read @('-C', $source, 'ls-files', '--others', '--exclude-standard', '-z')).Split([char]0, [StringSplitOptions]::RemoveEmptyEntries)
foreach ($relative in $untracked) {
    if ($casePaths.ContainsKey($relative) -and $casePaths[$relative] -cne $relative) { throw "Case-colliding tracked/untracked paths cannot be represented safely on Windows: $relative" }
    $casePaths[$relative] = $relative
}
$paths = @(@($tracked.Keys) + @($untracked) | Sort-Object -Unique)
$files = [Collections.Generic.List[object]]::new()
$excluded = [Collections.Generic.List[object]]::new()
$deleted = [Collections.Generic.List[string]]::new()
$missingSparse = [Collections.Generic.List[string]]::new()
$toRead = [Collections.Generic.List[string]]::new()
foreach ($path in $paths) {
    [void](Relative-Path $path)
    $reason = Exclusion-Reason $path
    if ($stagedDeletionPaths.Contains($path)) { $reason = 'Staged deletion; do not reintroduce a surviving untracked copy.' }
    if ($reason) { $excluded.Add([ordered]@{ Path = $path; Reason = $reason }); continue }
    if (-not (Test-Path -LiteralPath (Join-Path $source $path))) {
        if ($script:SparsePaths.Contains($path)) { $missingSparse.Add($path) } else { $deleted.Add($path) }
        continue
    }
    $toRead.Add($path)
}
$filters = @{}
if ($toRead.Count) {
    $attrOutput = Git-Read @('-C', $source, 'check-attr', '-z', '--stdin', 'filter') (($toRead.ToArray() -join [char]0) + [char]0)
    $attrs = $attrOutput.Split([char]0, [StringSplitOptions]::RemoveEmptyEntries)
    for ($i = 0; $i -lt $attrs.Count; $i += 3) {
        if ($attrs[$i + 2] -notin @('lfs', 'unspecified', 'unset')) { throw "Custom content filter requires manual review: $($attrs[$i])" }
        $filters[$attrs[$i]] = $attrs[$i + 2]
    }
}
[long]$total = 0; $count = 0
try {
    foreach ($path in $toRead) {
        $info = Assert-ContentFile $source $path
        $size = $info.Length; $stamp = $info.LastWriteTimeUtc.Ticks
        $hash = if ($Action -eq 'Plan') { (Get-FileHash -LiteralPath $info.FullName -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
        $info.Refresh()
        if ($info.Length -ne $size -or $info.LastWriteTimeUtc.Ticks -ne $stamp) { throw "File changed while reading: $path" }
        $files.Add([ordered]@{ Path = $path; Bytes = $size; SHA256 = $hash; Tracking = $(if ($tracked.ContainsKey($path)) { 'tracked' } else { 'untracked' }); LfsFilter = ($filters[$path] -eq 'lfs'); RequiresLfsBySize = ($size -ge 50MB) })
        $total += $size; $count++
        if ($count % 500 -eq 0) { Write-Progress -Activity "$Action current checkout without history" -Status "$count / $($toRead.Count)" -PercentComplete ($count * 100 / $toRead.Count) }
    }
} finally { Write-Progress -Activity "$Action current checkout without history" -Completed }
$after = Get-Provenance $source
if ($after.Head -ne $before.Head -or $after.StatusNul -cne $before.StatusNul) { throw 'Source HEAD/status changed during scan. Pause edits and auto-save, then retry.' }
$result = [ordered]@{ Schema = 'azure-current-snapshot-v1'; Action = $Action; Complete = $true; SourceComplete = ($script:SparsePaths.Count -eq 0); SparseEntryCount = $script:SparsePaths.Count; MissingSparseCount = $missingSparse.Count; CapturedUtc = [DateTime]::UtcNow.ToString('o'); SourcePath = $source; Provenance = $before; FileCount = $files.Count; TotalBytes = $total; ExcludedCount = $excluded.Count; MissingTrackedCount = $deleted.Count; NetworkUsed = $false; SourceChanged = $false; GitHistoryIncluded = $false; AdditionalExclude = $AdditionalExclude; Files = $files.ToArray(); Excluded = $excluded.ToArray(); MissingTrackedFiles = $deleted.ToArray(); MissingSparseFiles = $missingSparse.ToArray(); WorktreeDeletions = $deletions.ToArray(); Note = 'Complete means the scan finished; SourceComplete=false means a comparison-only partial snapshot, never an export source. MissingSparseFiles are NOT deletions. Includes current tracked files and nonignored untracked files; staged deletions are absent from the index. Ignored untracked files are excluded. Review exclusions before export. Two-PC differences require deliberate reconciliation; committed deletions require separate baseline evidence.' }
Write-NewJson $output $result
Write-Host "$Action complete: $($files.Count) files, $total bytes, $($excluded.Count) excluded. Network/history fetch: none. $output"
