#requires -Version 7.0
[CmdletBinding()]
param([string]$Repository = 'E:/work/image', [string]$OutputDirectory = $PSScriptRoot)
$ErrorActionPreference = 'Stop'
$env:GIT_NO_LAZY_FETCH = '1'
$env:GIT_OPTIONAL_LOCKS = '0'
function Read-Git([string[]]$Arguments) {
    $result = & git -C $Repository -c core.quotepath=false @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Read-only Git command failed: $($Arguments[0])" }
    return ($result -join "`n")
}
$headStart = Read-Git @('rev-parse','HEAD')
$base = Read-Git @('rev-parse','origin/main')
$index = (Read-Git @('ls-files','--stage','-z')).Split([char]0, [StringSplitOptions]::RemoveEmptyEntries)
$indexFlags = (Read-Git @('ls-files','-v','-z')).Split([char]0, [StringSplitOptions]::RemoveEmptyEntries)
$skipWorktree = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($flag in $indexFlags) { if ($flag.StartsWith('S ')) { [void]$skipWorktree.Add($flag.Substring(2)) } }
$allCurrent = [System.Collections.Generic.List[object]]::new()
$missing = [System.Collections.Generic.List[string]]::new()
$lfsPointers = [System.Collections.Generic.List[object]]::new()
$gitlinks = [System.Collections.Generic.List[string]]::new()
$extensionTotals = @{}
$currentBytes = [long]0
foreach ($record in $index) {
    if ($record -notmatch '^([0-9]+) ([0-9a-f]+) ([0-3])\t(.*)$') { throw 'Unexpected index format.' }
    $mode, $blob, $stage, $relative = $Matches[1], $Matches[2], $Matches[3], $Matches[4]
    if ($stage -ne '0') { throw "Unmerged path: $relative" }
    if ($mode -eq '160000') { $gitlinks.Add($relative); continue }
    $absolute = Join-Path $Repository $relative
    $file = [System.IO.FileInfo]::new($absolute)
    if (-not $file.Exists) { $missing.Add($relative); continue }
    $size = $file.Length
    $currentBytes += $size
    $extension = [System.IO.Path]::GetExtension($relative).ToLowerInvariant()
    if (-not $extensionTotals.ContainsKey($extension)) { $extensionTotals[$extension] = @{Count=0;Bytes=[long]0} }
    $extensionTotals[$extension].Count++
    $extensionTotals[$extension].Bytes += $size
    $pointer = $null
    if ($size -gt 0 -and $size -le 1024) {
        $small = [System.IO.File]::ReadAllText($absolute)
        if ($small -match '\Aversion https://git-lfs.github.com/spec/v1\r?\n(?:[^\r\n]+\r?\n)*oid sha256:([0-9a-f]{64})\r?\nsize ([0-9]+)\s*\z') {
            $pointer = [ordered]@{Path=$relative;Oid=$Matches[1];ObjectBytes=[long]$Matches[2]}
            $lfsPointers.Add($pointer)
        }
    }
    $allCurrent.Add([pscustomobject]@{Path=$relative;Bytes=$size;IndexBlob=$blob;LfsPointer=($null -ne $pointer)})
}
$rawChanges = (Read-Git @('diff','--raw','--no-abbrev','--no-renames','-z','origin/main..HEAD')).Split([char]0,[StringSplitOptions]::RemoveEmptyEntries)
$pending = [System.Collections.Generic.List[object]]::new()
for ($i=0; $i -lt $rawChanges.Length; $i+=2) {
    if ($rawChanges[$i] -notmatch '^:([0-9]+) ([0-9]+) ([0-9a-f]+) ([0-9a-f]+) ([AMDTR])$') { throw 'Unexpected raw diff format.' }
    $oldMode,$newMode,$oldBlob,$newBlob,$status=$Matches[1],$Matches[2],$Matches[3],$Matches[4],$Matches[5]
    $relative=$rawChanges[$i+1]
    $file=[System.IO.FileInfo]::new((Join-Path $Repository $relative))
    $pending.Add([pscustomobject]@{Path=$relative;Change=$status;BaseGitBlob=$oldBlob;HeadGitBlob=$newBlob;ExistsNow=$file.Exists;CurrentBytes=$(if($file.Exists){$file.Length}else{$null});ExcludeTaskCache=$relative.StartsWith('.cache/azure-repos-probe-20261016/')})
}
$worktree = (Read-Git @('status','--porcelain=v1','-z','--untracked-files=all')).Split([char]0,[StringSplitOptions]::RemoveEmptyEntries)
$headEnd = Read-Git @('rev-parse','HEAD')
$summary=[ordered]@{
    GeneratedUtc=[DateTime]::UtcNow.ToString('o')
    Repository=$Repository
    HeadStart=$headStart
    HeadEnd=$headEnd
    ConcurrentHeadChange=($headStart -ne $headEnd)
    OriginMain=$base
    CommitsAhead=[int](Read-Git @('rev-list','--count','origin/main..HEAD'))
    NoLazyFetch=$true
    NoNetwork=$true
    IndexTrackedEntries=$index.Count
    CurrentTrackedFiles=$allCurrent.Count
    CurrentTrackedBytes=$currentBytes
    MissingTrackedPathCount=$missing.Count
    MissingTrackedPathSamples=@($missing | Select-Object -First 12)
    SkipWorktreeCount=$skipWorktree.Count
    MissingSkipWorktreeCount=@($missing | Where-Object {$skipWorktree.Contains($_)}).Count
    MissingNonSkipWorktreePaths=@($missing | Where-Object {-not $skipWorktree.Contains($_)})
    GitlinkPaths=@($gitlinks)
    WorkingTreeLfsPointers=@($lfsPointers)
    PendingHeadChanges=$pending.Count
    PendingHeadChangesByStatus=@($pending | Group-Object Change | ForEach-Object { @{Change=$_.Name;Count=$_.Count} })
    PendingHeadChangesByTopLevel=@($pending | Group-Object {$_.Path.Split('/')[0]} | Sort-Object Count -Descending | ForEach-Object { @{Directory=$_.Name;Count=$_.Count} })
    PendingExistingFileBytes=[long](($pending | Where-Object {$_.ExistsNow -and -not $_.ExcludeTaskCache} | Measure-Object CurrentBytes -Sum).Sum)
    PendingCacheExcludedCount=@($pending | Where-Object ExcludeTaskCache).Count
    CurrentBytesByExtension=@($extensionTotals.GetEnumerator() | Sort-Object {$_.Value.Bytes} -Descending | ForEach-Object { @{Extension=$_.Key;Count=$_.Value.Count;Bytes=$_.Value.Bytes} })
    WorkingTreeStatus=@($worktree | Where-Object {$_ -notlike '*azure-repos-probe-20261016*'})
    CacheTrackedCount=@($index | Where-Object {$_ -like '*.cache/azure-repos-probe-20261016/*'}).Count
    CacheIgnoreConfirmed=([bool](Read-Git @('check-ignore','--','.cache/azure-repos-probe-20261016/tools/git-lfs-3.8.0/git-lfs-3.8.0/git-lfs.exe')))
    Limitations=@('Index and files were read while other tasks can modify the checkout; this is not a frozen release snapshot.','File byte totals count current working-tree bytes and duplicate paths; they are not Git pack size or upload estimates.','No missing history was downloaded. Content of ignored untracked files and old Git objects was not inventoried.','Other Windows computer is unavailable; no cross-computer content comparison has been performed.','Pending file list is a candidate reconciliation set, not automatic permission to overwrite files on the other computer.')
}
$summaryPath=Join-Path $OutputDirectory 'local-migration-audit.json'
$pendingPath=Join-Path $OutputDirectory 'local-pending-paths.json'
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8NoBOM
$pending | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $pendingPath -Encoding utf8NoBOM
[ordered]@{Summary=$summaryPath;PendingManifest=$pendingPath;Head=$headEnd;IndexTrackedEntries=$index.Count;CurrentTrackedFiles=$allCurrent.Count;CurrentTrackedBytes=$currentBytes;MissingCount=$missing.Count;WorkingTreeLfsPointerCount=$lfsPointers.Count;GitlinkCount=$gitlinks.Count;PendingChanges=$pending.Count;PendingExistingFileBytes=$summary.PendingExistingFileBytes;CacheTrackedCount=$summary.CacheTrackedCount} | ConvertTo-Json
