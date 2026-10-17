#requires -Version 7.0
[CmdletBinding()]
param([string]$ResultPath)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$helper = Join-Path $PSScriptRoot 'Prepare-Azure-Snapshot.ps1'
$root = Join-Path ([IO.Path]::GetTempPath()) ('azure-snapshot-test-' + [Guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($root)
$source = Join-Path $root 'source'
$checks = [Collections.Generic.List[object]]::new()
function G([string[]]$A) { & git @A 2>&1 | Out-Null; if ($LASTEXITCODE -ne 0) { throw "Fixture Git failed: $A" } }
function Check([string]$Name, [bool]$Condition) { if (-not $Condition) { throw "FAIL: $Name" }; $checks.Add([ordered]@{ Name = $Name; Passed = $true }) }
function Reject([string]$Name, [scriptblock]$Operation, [string]$Expected) {
    $caught = $false
    try { & $Operation | Out-Null } catch { if ($_.Exception.Message -notmatch $Expected) { throw }; $caught = $true }
    Check $Name $caught
}
function Save([string]$Path, [string]$Text) { [IO.File]::WriteAllText($Path, $Text, [Text.UTF8Encoding]::new($false)) }
try {
    $template = Join-Path $root 'template'; [void][IO.Directory]::CreateDirectory($template)
    G @('init', '--initial-branch=main', "--template=$template", $source)
    G @('-C', $source, 'config', 'user.name', 'Snapshot Test')
    G @('-C', $source, 'config', 'user.email', 'snapshot-test@example.invalid')
    G @('-C', $source, 'config', 'commit.gpgSign', 'false')
    G @('-C', $source, 'config', 'core.autocrlf', 'false')
    Save (Join-Path $source 'tracked.txt') 'initial'
    Save (Join-Path $source 'deleted.txt') 'deleted later'
    Save (Join-Path $source 'staged-deleted.txt') 'deleted in index'
    Save (Join-Path $source '.gitignore') "ignored.txt`n"
    G @('-C', $source, 'add', '--all'); G @('-C', $source, 'commit', '-m', 'first history')
    Save (Join-Path $source 'tracked.txt') 'second commit'
    G @('-C', $source, 'add', 'tracked.txt'); G @('-C', $source, 'commit', '-m', 'second history')
    Save (Join-Path $source 'tracked.txt') 'latest dirty work'
    Save (Join-Path $source '新增内容.txt') 'untracked work'
    Save (Join-Path $source 'asset.bin') 'materialized binary content'
    Save (Join-Path $source '.gitattributes') "*.bin filter=lfs diff=lfs merge=lfs -text`n"
    Save (Join-Path $source 'ignored.txt') 'do not copy'
    Save (Join-Path $source '.env') 'SYNTHETIC=not-a-real-secret'
    [void][IO.Directory]::CreateDirectory((Join-Path $source '.cache'))
    Save (Join-Path $source '.cache/generated.log') 'do not copy'
    [void][IO.Directory]::CreateDirectory((Join-Path $source 'designs/team-invites-20260928/live-acceptance'))
    Save (Join-Path $source 'designs/team-invites-20260928/live-acceptance/test.exe') 'synthetic test binary'
    Save (Join-Path $source 'designs/team-invites-20260928/live-acceptance/runtime.log.stdout.txt') 'synthetic raw log'
    Save (Join-Path $source 'designs/team-invites-20260928/live-acceptance/robot.yaml') 'password: SYNTHETIC-NOT-REAL'
    Save (Join-Path $source 'game-release.exe') 'synthetic formal executable; retain'
    G @('-C', $source, 'rm', '--cached', 'staged-deleted.txt')
    [IO.File]::Delete((Join-Path $source 'deleted.txt'))
    $headBefore = (& git -C $source rev-parse HEAD) -join ''
    $statusBefore = (& git -C $source status --porcelain=v1 --untracked-files=all) -join "`n"
    $plan = Join-Path $root 'plan.json'
    & $helper -Action Plan -SourcePath $source -OutputPath $plan
    $data = Get-Content -LiteralPath $plan -Raw | ConvertFrom-Json
    Check 'Plan completes with no network or Git history' ($data.Complete -and -not $data.NetworkUsed -and -not $data.GitHistoryIncluded)
    Check 'Dirty tracked content hash is current' (($data.Files | Where-Object Path -eq 'tracked.txt').SHA256 -eq (Get-FileHash -LiteralPath (Join-Path $source 'tracked.txt')).Hash)
    Check 'Chinese untracked file included' ('新增内容.txt' -in $data.Files.Path)
    Check 'Ignored untracked file omitted' ('ignored.txt' -notin $data.Files.Path)
    Check 'Cache and environment file excluded' ('.env' -in $data.Excluded.Path -and '.cache/generated.log' -in $data.Excluded.Path)
    Check 'Only known team build artifacts excluded, formal executable retained' ('designs/team-invites-20260928/live-acceptance/test.exe' -in $data.Excluded.Path -and 'designs/team-invites-20260928/live-acceptance/runtime.log.stdout.txt' -in $data.Excluded.Path -and 'game-release.exe' -in $data.Files.Path)
    Check 'Known local test-account configuration excluded' ('designs/team-invites-20260928/live-acceptance/robot.yaml' -in $data.Excluded.Path -and 'designs/team-invites-20260928/live-acceptance/robot.yaml' -notin $data.Files.Path)
    Check 'Effective LFS attribute recorded without running LFS' (($data.Files | Where-Object Path -eq 'asset.bin').LfsFilter)
    Check 'Unstaged deletion retained as evidence' ('deleted.txt' -in $data.MissingTrackedFiles -and 'deleted.txt' -in $data.WorktreeDeletions.Path)
    Check 'Staged deletion is not reintroduced from disk' ('staged-deleted.txt' -notin $data.Files.Path -and 'staged-deleted.txt' -in $data.WorktreeDeletions.Path)
    Check 'Source HEAD and worktree state unchanged' (($headBefore -eq ((& git -C $source rev-parse HEAD) -join '')) -and ($statusBefore -ceq ((& git -C $source status --porcelain=v1 --untracked-files=all) -join "`n")))
    $inventory = Join-Path $root 'inventory.json'
    & $helper -Action Inventory -SourcePath $source -OutputPath $inventory
    Reject 'Inventory is not accepted as an export plan' { & $helper -Action Export -SourcePath $source -PlanPath $inventory -OutputPath (Join-Path $root 'wrong-export') } 'completed Plan'
    Reject 'Output inside source is rejected' { & $helper -Action Plan -SourcePath $source -OutputPath (Join-Path $source 'forbidden.json') } 'outside the source'
    Reject 'Existing output is never overwritten' { & $helper -Action Plan -SourcePath $source -OutputPath $plan } 'already exists'
    $snapshot = Join-Path $root 'snapshot'
    & $helper -Action Export -SourcePath $source -PlanPath $plan -OutputPath $snapshot
    Check 'Export contains no Git metadata' (-not (Test-Path -LiteralPath (Join-Path $snapshot '.git')))
    Check 'Export receipt confirms content verification' ((Get-Content -LiteralPath ($snapshot + '.receipt.json') -Raw | ConvertFrom-Json).Complete)
    Check 'Export preserves exact file bytes' ((Get-FileHash -LiteralPath (Join-Path $snapshot 'tracked.txt')).Hash -eq (Get-FileHash -LiteralPath (Join-Path $source 'tracked.txt')).Hash)
    $other = Join-Path $root 'other-plan.json'
    $otherData = Get-Content -LiteralPath $plan -Raw | ConvertFrom-Json
    ($otherData.Files | Where-Object Path -eq 'tracked.txt').SHA256 = ('a' * 64)
    $otherData.Files = @($otherData.Files | Where-Object Path -ne '新增内容.txt')
    Save $other ($otherData | ConvertTo-Json -Depth 12)
    $comparison = Join-Path $root 'comparison.json'
    & $helper -Action Compare -PlanPath $plan -OtherPlanPath $other -OutputPath $comparison
    $compare = Get-Content -LiteralPath $comparison -Raw | ConvertFrom-Json
    Check 'Different contents demand manual merge' (($compare.Differences | Where-Object Path -eq 'tracked.txt').Kind -eq 'DifferentContent_ManualMergeRequired')
    Check 'Single-sided file is reviewed, not automatically added' (($compare.Differences | Where-Object Path -eq '新增内容.txt').Kind -eq 'OnlyLeft_ReviewAdditionOrDeletion' -and -not $compare.AutoApplied)
    Save (Join-Path $source 'tracked.txt') 'changed after plan'
    Reject 'Changed file hash stops export' { & $helper -Action Export -SourcePath $source -PlanPath $plan -OutputPath (Join-Path $root 'stale-export') } 'Content changed after Plan'
    Save (Join-Path $source 'pointer.bin') "version https://git-lfs.github.com/spec/v1`noid sha256:$('0' * 64)`nsize 123`n"
    Reject 'Unmaterialized LFS pointer stops planning without fetching' { & $helper -Action Plan -SourcePath $source -OutputPath (Join-Path $root 'pointer-plan.json') } 'Unmaterialized LFS pointer'
    [IO.File]::Delete((Join-Path $source 'pointer.bin'))
    $malicious = Get-Content -LiteralPath $plan -Raw | ConvertFrom-Json
    $malicious.Files[0].Path = '../escape.txt'
    $bad = Join-Path $root 'bad-plan.json'; Save $bad ($malicious | ConvertTo-Json -Depth 12)
    Reject 'Manifest path traversal rejected' { & $helper -Action Compare -PlanPath $bad -OtherPlanPath $plan -OutputPath (Join-Path $root 'bad-compare.json') } 'Unsafe Windows path'
    G @('-C', $source, 'update-index', '--skip-worktree', 'tracked.txt')
    [IO.File]::Delete((Join-Path $source 'tracked.txt'))
    Reject 'Sparse entries block a full plan instead of becoming deletions' { & $helper -Action Plan -SourcePath $source -OutputPath (Join-Path $root 'sparse-plan.json') } 'Sparse / skip-worktree'
    $sparsePlan = Join-Path $root 'partial-plan.json'
    & $helper -Action Plan -AllowIncompleteSparse -SourcePath $source -OutputPath $sparsePlan
    $sparseData = Get-Content -LiteralPath $sparsePlan -Raw | ConvertFrom-Json
    Check 'Explicit partial Plan separates missing sparse files from deletions' (-not $sparseData.SourceComplete -and 'tracked.txt' -in $sparseData.MissingSparseFiles -and 'tracked.txt' -notin $sparseData.MissingTrackedFiles)
    Reject 'Partial Plan cannot export even with override' { & $helper -Action Export -AllowIncompleteSparse -SourcePath $source -PlanPath $sparsePlan -OutputPath (Join-Path $root 'partial-export') } 'Sparse / skip-worktree'
    G @('-C', $source, 'update-index', '--no-skip-worktree', 'tracked.txt')
    Save (Join-Path $source 'tracked.txt') 'dirty filtered file'
    Save (Join-Path $source '.gitattributes') "*.txt filter=audit`n"
    G @('-C', $source, 'config', 'filter.audit.clean', 'echo filter-executed > filter-marker.txt; cat')
    G @('-C', $source, 'config', 'filter.audit.required', 'true')
    Reject 'Custom filter rejected without executing its clean command' { & $helper -Action Plan -SourcePath $source -OutputPath (Join-Path $root 'filter-plan.json') } 'Custom content filter'
    Check 'Git status never executes source clean filters or their side effects' (-not (Test-Path -LiteralPath (Join-Path $source 'filter-marker.txt')))
    G @('-C', $source, 'config', 'filter.Audit.clean', 'echo case-filter-executed > filter-case-marker.txt; cat')
    Save (Join-Path $source '.gitattributes') "*.txt filter=Audit`n"
    Reject 'Differently cased filter names are all disabled' { & $helper -Action Plan -SourcePath $source -OutputPath (Join-Path $root 'filter-case-plan.json') } 'Custom content filter'
    Check 'Case-sensitive filter driver cannot bypass disable list' (-not (Test-Path -LiteralPath (Join-Path $source 'filter-case-marker.txt')))
    $fixtureBlob = ((& git -C $source rev-parse HEAD:tracked.txt) -join '').Trim()
    G @('-C', $source, '-c', 'core.ignorecase=false', 'update-index', '--add', '--cacheinfo', "100644,$fixtureBlob,Case.txt")
    G @('-C', $source, '-c', 'core.ignorecase=false', 'update-index', '--add', '--cacheinfo', "100644,$fixtureBlob,case.txt")
    Reject 'Case-colliding Git paths are not silently collapsed on Windows' { & $helper -Action Plan -SourcePath $source -OutputPath (Join-Path $root 'case-plan.json') } 'Case-colliding Git index'
    $result = [ordered]@{ Status = 'PASS'; CapturedUtc = [DateTime]::UtcNow.ToString('o'); Tests = $checks.Count; Checks = $checks.ToArray(); NetworkUsed = $false; HelperSHA256 = (Get-FileHash -LiteralPath $helper -Algorithm SHA256).Hash }
    if ($ResultPath) { $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ResultPath -Encoding utf8 }
    $result | ConvertTo-Json -Depth 8
} finally {
    $resolved = [IO.Path]::GetFullPath($root)
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if ($resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path -Leaf $resolved) -match '^azure-snapshot-test-[0-9a-f]{32}$') { Remove-Item -LiteralPath $resolved -Recurse -Force }
}
