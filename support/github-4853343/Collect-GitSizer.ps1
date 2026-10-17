#requires -Version 5.1
<#
Read-only, offline Git repository measurements for GitHub Support ticket 4853343.
No fetch, checkout, rewrite, cleanup, upload, installation, or policy change is made.
An explicitly selected revision is measured as-is; no history migration is inferred.
#>
[CmdletBinding()]
param(
    [string]$Repository,
    [ValidatePattern('^[0-9a-fA-F]{40}$')]
    [string]$Revision = '083896b017503d69148557a3a8cece7ee17443e3',
    [string]$OutputDirectory,
    [string]$GitSizerPath = (Join-Path $PSScriptRoot 'tools\git-sizer.exe'),
    [switch]$IncludeJson,
    [ValidateRange(1, 8)][int]$SearchDepth = 5,
    [ValidateRange(100, 50000)][int]$DirectoryLimit = 8000,
    [ValidateRange(30, 7200)][int]$CommandTimeoutSeconds = 1800
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$script:GitExecutable = $null
$script:ScratchDirectory = $null
$script:CandidateChecks = New-Object System.Collections.Generic.List[object]
$script:SkippedDirectories = 0
$script:VisitedDirectories = 0
$script:ReportPlans = @(
    @{ Name='git-sizer-revision.txt'; Scope='revision'; Json=$false; Arguments=@('--verbose','--no-progress','--names=full') },
    @{ Name='git-sizer-all-refs.txt'; Scope='all-refs'; Json=$false; Arguments=@('--verbose','--no-progress','--names=full') },
    @{ Name='git-sizer-revision.json'; Scope='revision'; Json=$true; Arguments=@('--json','--json-version=2','--verbose','--no-progress') },
    @{ Name='git-sizer-all-refs.json'; Scope='all-refs'; Json=$true; Arguments=@('--json','--json-version=2','--verbose','--no-progress') }
)
$script:Utf8 = New-Object System.Text.UTF8Encoding($false)

function Quote-NativeArgument([string]$Value) {
    if ($Value -notmatch '[\s"]' -and $Value.Length -gt 0) { return $Value }
    $escaped = [regex]::Replace($Value, '(\\*)"', '$1$1\"')
    $escaped = [regex]::Replace($escaped, '(\\+)$', '$1$1')
    return '"' + $escaped + '"'
}

function Invoke-ReadOnlyProcess {
    param([string]$Executable, [string[]]$Arguments, [string]$WorkingDirectory,
          [int]$TimeoutSeconds = 30, [string]$OutputFile, [string]$InputText)
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $Executable
    $startInfo.Arguments = (($Arguments | ForEach-Object { Quote-NativeArgument $_ }) -join ' ')
    if ($WorkingDirectory) { $startInfo.WorkingDirectory = $WorkingDirectory }
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.RedirectStandardInput = ($null -ne $InputText -and $InputText.Length -gt 0)
    # Child-only environment; also covers git processes started by git-sizer.
    $startInfo.EnvironmentVariables['GIT_NO_LAZY_FETCH'] = '1'
    $startInfo.EnvironmentVariables['GIT_ALLOW_PROTOCOL'] = 'file'
    $startInfo.EnvironmentVariables['GIT_TERMINAL_PROMPT'] = '0'
    $startInfo.EnvironmentVariables['GCM_INTERACTIVE'] = 'Never'
    $startInfo.EnvironmentVariables['GIT_OPTIONAL_LOCKS'] = '0'
    $startInfo.EnvironmentVariables['GIT_NO_REPLACE_OBJECTS'] = '1'
    $startInfo.EnvironmentVariables['GIT_CONFIG_NOSYSTEM'] = '1'
    $startInfo.EnvironmentVariables['GIT_CONFIG_GLOBAL'] = 'NUL'
    # No inherited Git repository/index overrides. Command-scoped ownership exception.
    foreach ($key in @('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY',
                       'GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_CONFIG_PARAMETERS')) {
        $startInfo.EnvironmentVariables.Remove($key)
    }
    $startInfo.EnvironmentVariables['GIT_CONFIG_COUNT'] = '2'
    $startInfo.EnvironmentVariables['GIT_CONFIG_KEY_0'] = 'safe.directory'
    $trustedDirectory = if ($WorkingDirectory) { [IO.Path]::GetFullPath($WorkingDirectory) } else { [IO.Directory]::GetCurrentDirectory() }
    $startInfo.EnvironmentVariables['GIT_CONFIG_VALUE_0'] = $trustedDirectory.Replace('\','/')
    $startInfo.EnvironmentVariables['GIT_CONFIG_KEY_1'] = 'protocol.allow'
    $startInfo.EnvironmentVariables['GIT_CONFIG_VALUE_1'] = 'never'
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    $stream = $null
    try {
        if (-not $process.Start()) { throw 'Could not start the local command.' }
        if ($OutputFile) {
            $stream = [System.IO.File]::Open($OutputFile, 'CreateNew', 'Write', 'None')
            $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stream)
        } else {
            $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        }
        $stderrTask = $process.StandardError.ReadToEndAsync()
        if ($startInfo.RedirectStandardInput) {
            $process.StandardInput.Write($InputText)
            $process.StandardInput.Close()
        }
        $timer = [System.Diagnostics.Stopwatch]::StartNew()
        while (-not $process.WaitForExit(1000)) {
            if ($timer.Elapsed.TotalSeconds -gt $TimeoutSeconds) {
                $process.Kill()
                $process.WaitForExit()
                throw 'The local read-only command exceeded its time limit.'
            }
            if ($TimeoutSeconds -gt 30 -and ([int]$timer.Elapsed.TotalSeconds % 15) -eq 0) {
                Write-Host ('  Still reading local Git objects ({0}s).' -f [int]$timer.Elapsed.TotalSeconds)
            }
        }
        $stdoutTask.GetAwaiter().GetResult() | Out-Null
        $stderr = $stderrTask.GetAwaiter().GetResult()
        $stdout = if ($OutputFile) { $null } else { $stdoutTask.Result }
        return [pscustomobject]@{ ExitCode = $process.ExitCode; Output = $stdout; Error = $stderr }
    } finally {
        if ($stream) { $stream.Dispose() }
        $process.Dispose()
    }
}

function Invoke-Git([string]$Repo, [string[]]$GitArguments, [string]$OutputFile,
                    [int]$TimeoutSeconds = 30, [string]$InputText) {
    return Invoke-ReadOnlyProcess -Executable $script:GitExecutable -WorkingDirectory $Repo `
        -Arguments $GitArguments -OutputFile $OutputFile -TimeoutSeconds $TimeoutSeconds -InputText $InputText
}

function Test-RepositoryMarker([string]$Path) {
    return (Test-Path -LiteralPath (Join-Path $Path '.git')) -or
        ((Test-Path -LiteralPath (Join-Path $Path 'HEAD') -PathType Leaf) -and
         (Test-Path -LiteralPath (Join-Path $Path 'objects') -PathType Container) -and
         (Test-Path -LiteralPath (Join-Path $Path 'refs') -PathType Container))
}

function Get-SearchRoots {
    $roots = New-Object System.Collections.Generic.List[string]
    $profilePath = [Environment]::GetFolderPath('UserProfile')
    foreach ($relative in @('', 'Desktop', 'Documents', 'Downloads', 'source', 'repos', 'Projects', 'work', 'code')) {
        $candidate = if ($relative) { Join-Path $profilePath $relative } else { $profilePath }
        if (Test-Path -LiteralPath $candidate -PathType Container) { $roots.Add($candidate) }
    }
    $drives = @(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' -ErrorAction SilentlyContinue)
    foreach ($drive in $drives) {
        $driveRoot = $drive.DeviceID + '\'
        if (Test-RepositoryMarker $driveRoot) { $roots.Add($driveRoot) }
        foreach ($dir in @(Get-ChildItem -LiteralPath $driveRoot -Directory -Force -ErrorAction SilentlyContinue)) {
            if ($dir.Name -match '(?i)work|project|code|dev|repo|git|source|src|data|backup|archive|image|lfs|rewrit|migrat|\u5de5\u4f5c|\u9879\u76ee|\u5f00\u53d1|\u4ee3\u7801|\u4ed3\u5e93|\u5907\u4efd') {
                $roots.Add($dir.FullName)
            }
        }
    }
    return @($roots | Sort-Object -Unique)
}

function Find-RepositoryCandidates {
    $found = New-Object System.Collections.Generic.List[string]
    $visited = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    $queue = New-Object 'System.Collections.Generic.Queue[object]'
    foreach ($root in @(Get-SearchRoots)) { $queue.Enqueue([pscustomobject]@{Path=$root; Depth=0}) }
    $skip = '^(?i:Windows|Program Files(?: \(x86\))?|ProgramData|AppData|\$Recycle\.Bin|System Volume Information|Recovery|PerfLogs|node_modules|Library|objects|lfs|\.git|\.cache|cache|caches|Temp|\.nuget|\.gradle|\.m2|\.venv|venv|obj|bin|Packages|PackageCache|SteamLibrary|WindowsApps)$'
    while ($queue.Count -gt 0 -and $script:VisitedDirectories -lt $DirectoryLimit) {
        $item = $queue.Dequeue()
        if (-not $visited.Add($item.Path)) { continue }
        $script:VisitedDirectories++
        if (Test-RepositoryMarker $item.Path) {
            $found.Add($item.Path)
            continue # Never enumerate files or descend into a repository's asset tree.
        }
        if ($item.Depth -ge $SearchDepth) { continue }
        foreach ($dir in @(Get-ChildItem -LiteralPath $item.Path -Directory -Force -ErrorAction SilentlyContinue)) {
            if ($dir.Name -match $skip -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
                $script:SkippedDirectories++
                continue
            }
            $queue.Enqueue([pscustomobject]@{Path=$dir.FullName; Depth=$item.Depth+1})
        }
    }
    Write-Host ('Scanned {0} directory names; found {1} candidate repositories.' -f $script:VisitedDirectories,$found.Count)
    if ($queue.Count -gt 0) { Write-Warning 'Search limit reached. Specify -Repository if the desired repository was not found.' }
    return @($found)
}

function Check-Candidate([string]$Repo) {
    $type = Invoke-Git $Repo @('cat-file', '-t', $Revision)
    $head = Invoke-Git $Repo @('rev-parse', '--verify', 'HEAD')
    $headValue = if ($head.ExitCode -eq 0 -and $head.Output.Trim() -match '^[0-9a-f]{40}$') { $head.Output.Trim() } else { $null }
    $record = [pscustomobject]@{
        Path = $Repo
        CurrentHead = $headValue
        RequestedRevisionPresent = ($type.ExitCode -eq 0 -and $type.Output.Trim() -eq 'commit')
        HeadMatchesRequestedRevision = ($headValue -eq $Revision)
        ObjectTypeCheckExitCode = $type.ExitCode
    }
    $script:CandidateChecks.Add($record)
    return $record
}

function Assert-OutputOutsideRepositories([string]$Path) {
    $outputFull = [IO.Path]::GetFullPath($Path).TrimEnd('\','/')
    foreach ($candidate in $script:CandidateChecks) {
        $repoFull = [IO.Path]::GetFullPath($candidate.Path).TrimEnd('\','/')
        if ($outputFull.Equals($repoFull,[StringComparison]::OrdinalIgnoreCase) -or
            $outputFull.StartsWith($repoFull+'\',[StringComparison]::OrdinalIgnoreCase)) {
            throw 'The output directory must be outside every detected repository. Choose another -OutputDirectory.'
        }
    }
}

function Check-ObjectCompleteness([string]$Repo, [string]$Scope, [string[]]$Roots) {
    $objectList = Join-Path $script:ScratchDirectory ($Scope+'-objects.txt')
    $arguments = @('rev-list','--objects','--no-object-names','--missing=print') + $Roots
    $result = Invoke-Git -Repo $Repo -GitArguments $arguments -OutputFile $objectList -TimeoutSeconds $CommandTimeoutSeconds
    $missing = 0L
    $objects = 0L
    if (Test-Path -LiteralPath $objectList) {
        foreach ($line in [IO.File]::ReadLines($objectList)) {
            if ($line.StartsWith('?')) { $missing++ } elseif ($line -match '^[0-9a-f]{40}$') { $objects++ }
        }
    }
    $record = [pscustomobject]@{ Scope=$Scope; Command=('git '+($arguments -join ' ')); ExitCode=$result.ExitCode; PresentObjectCount=$objects; MissingObjectCount=$missing }
    if ($result.ExitCode -ne 0 -or $missing -gt 0 -or $objects -eq 0) {
        throw ('Incomplete local objects in scope {0}: exit={1}, present={2}, missing={3}. No complete report will be published; this script never fetches.' -f $Scope,$result.ExitCode,$objects,$missing)
    }
    return $record
}

function Write-JsonFile([string]$Path, $Value) {
    [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 12), $script:Utf8)
}

function New-MeasurementSnapshot([string]$Kind, [string]$ObjectsPath, [object[]]$References) {
    $snapshot = Join-Path $script:ScratchDirectory ($Kind+'.git')
    $template = Join-Path $script:ScratchDirectory 'empty-template'
    [IO.Directory]::CreateDirectory($template) | Out-Null
    $init = Invoke-Git $script:ScratchDirectory @('init','--bare','--quiet',('--template='+$template),$snapshot)
    if ($init.ExitCode -ne 0) { throw 'Could not initialize an isolated measurement snapshot.' }
    $infoDirectory = Join-Path $snapshot 'objects\info'
    [IO.Directory]::CreateDirectory($infoDirectory) | Out-Null
    [IO.File]::WriteAllText((Join-Path $infoDirectory 'alternates'),($ObjectsPath.Replace('\','/')+"`n"),$script:Utf8)
    $updates = New-Object System.Text.StringBuilder
    foreach ($reference in $References) {
        if ($reference.Object -notmatch '^[0-9a-f]{40}$' -or $reference.Name -notmatch '^refs/[^\s]+$') {
            throw 'Unexpected reference format; refusing to create a measurement snapshot.'
        }
        [void]$updates.Append(('update '+$reference.Name+' '+$reference.Object+"`n"))
    }
    if ($References.Count -gt 0) {
        $updateResult = Invoke-Git -Repo $snapshot -GitArguments @('update-ref','--stdin') -InputText $updates.ToString() -TimeoutSeconds $CommandTimeoutSeconds
        if ($updateResult.ExitCode -ne 0) { throw ('Could not copy local references to the isolated {0} snapshot; objects may be missing.' -f $Kind) }
    }
    return $snapshot
}

$runDirectory = $null
$metadata = $null
try {
    $gitCommand = Get-Command git.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1
    $script:GitExecutable = $gitCommand.Source
    if (-not (Test-Path -LiteralPath $GitSizerPath -PathType Leaf)) {
        throw 'Missing bundled tools\git-sizer.exe. Place the verified official v1.5.0 executable beside this script; no download or installation is performed.'
    }
    $GitSizerPath = (Resolve-Path -LiteralPath $GitSizerPath).Path
    if ($Repository) {
        $candidates = @((Resolve-Path -LiteralPath $Repository -ErrorAction Stop).Path)
    } else {
        Write-Host 'Locating repositories by directory names only (bounded search).'
        $candidates = @(Find-RepositoryCandidates)
    }
    foreach ($candidate in $candidates) { Check-Candidate $candidate | Out-Null }
    $matches = @($script:CandidateChecks | Where-Object { $_.RequestedRevisionPresent })
    if ($matches.Count -eq 0) { throw 'The requested commit is not available locally in the checked repositories. Specify -Repository on the computer containing it. Nothing was fetched.' }
    $preferred = @($matches | Where-Object { $_.HeadMatchesRequestedRevision })
    if ($preferred.Count -eq 1) { $selected = $preferred[0] }
    elseif ($matches.Count -eq 1) { $selected = $matches[0] }
    else { throw 'Several repositories contain the requested commit. Run again with an explicit -Repository to select one.' }
    $Repository = $selected.Path
    if (-not $OutputDirectory) { $OutputDirectory = Join-Path ([IO.Path]::GetTempPath()) 'GitHub-4853343-reports' }
    Assert-OutputOutsideRepositories $OutputDirectory
    $runDirectory = Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) ((Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')+'-'+[Guid]::NewGuid().ToString('N').Substring(0,8))
    $script:ScratchDirectory = Join-Path $runDirectory '_incomplete'
    [IO.Directory]::CreateDirectory($script:ScratchDirectory) | Out-Null
    Write-Host ('Measuring explicit commit {0}; no rewrite or migration is inferred.' -f $Revision)
    $gitVersion = Invoke-Git $Repository @('--version')
    $sizerVersion = Invoke-ReadOnlyProcess -Executable $GitSizerPath -Arguments @('--version') -WorkingDirectory $Repository
    if ($gitVersion.ExitCode -ne 0 -or $sizerVersion.ExitCode -ne 0) { throw 'Unable to verify the local tool versions.' }
    if ($sizerVersion.Output -notmatch '(?<![0-9])1\.5\.0(?![0-9])') { throw 'This collector requires the verified official git-sizer v1.5.0 executable.' }
    $shallow = Invoke-Git $Repository @('rev-parse','--is-shallow-repository')
    if ($shallow.ExitCode -ne 0 -or $shallow.Output.Trim() -ne 'false') { throw 'A shallow or unreadable repository cannot produce a complete history report.' }
    $metadata = [ordered]@{
        Ticket='4853343'; Status='validating'; GeneratedUtc=(Get-Date).ToUniversalTime().ToString('o')
        RequestedRevision=$Revision; CurrentHead=$selected.CurrentHead
        HeadMatchesRequestedRevision=$selected.HeadMatchesRequestedRevision
        HistoryClassification='Existing local history measured as-is; a rewrite or LFS migration is not inferred.'
        GitVersion=$gitVersion.Output.Trim(); GitSizerVersion=$sizerVersion.Output.Trim()
        Shallow=$false; NetworkFetchAllowed=$false; RepositoryModified=$false
        ScopeWarning='The all-refs report can include old backup refs and must not be confused with the explicit-revision report.'
        CandidateChecks=@($script:CandidateChecks.ToArray()); ObjectChecks=@(); Reports=@()
    }
    $objectsResult = Invoke-Git $Repository @('rev-parse','--git-path','objects')
    if ($objectsResult.ExitCode -ne 0) { throw 'Could not locate the original local Git object directory.' }
    $objectsPath = $objectsResult.Output.Trim()
    if (-not [IO.Path]::IsPathRooted($objectsPath)) { $objectsPath = Join-Path $Repository $objectsPath }
    $objectsPath = (Resolve-Path -LiteralPath $objectsPath).Path
    $refsResult = Invoke-Git $Repository @('for-each-ref','--format=%(objectname) %(refname)')
    if ($refsResult.ExitCode -ne 0) { throw 'Could not capture the original local reference list.' }
    $references = New-Object System.Collections.Generic.List[object]
    foreach ($line in ($refsResult.Output -split '\r?\n')) {
        if (-not $line) { continue }
        if ($line -notmatch '^([0-9a-f]{40}) (refs/[^\s]+)$') { throw 'Unexpected reference list output.' }
        $references.Add([pscustomobject]@{Object=$Matches[1];Name=$Matches[2]})
    }
    if ($references.Count -eq 0) { throw 'The repository has no refs; an all-refs comparison cannot be generated.' }
    $referenceDigest = [Security.Cryptography.SHA256]::Create()
    try { $metadata.ReferenceSnapshotSha256 = ([BitConverter]::ToString($referenceDigest.ComputeHash($script:Utf8.GetBytes($refsResult.Output)))).Replace('-','') }
    finally { $referenceDigest.Dispose() }
    $metadata.ReferenceCount = $references.Count
    $metadata.MeasurementMethod = 'Two temporary bare repositories read original objects through alternates. The revision snapshot contains only refs/heads/report-main at RequestedRevision. The all-refs snapshot contains the captured original refs. Original refs and objects are not written.'
    $snapshots = @{}
    $snapshots['revision'] = New-MeasurementSnapshot 'revision' $objectsPath @([pscustomobject]@{Name='refs/heads/report-main';Object=$Revision})
    $snapshots['all-refs'] = New-MeasurementSnapshot 'all-refs' $objectsPath $references.ToArray()
    Write-Host 'Checking that both isolated histories are locally complete.'
    $metadata.ObjectChecks += Check-ObjectCompleteness $snapshots['revision'] 'revision' @('--all')
    $metadata.ObjectChecks += Check-ObjectCompleteness $snapshots['all-refs'] 'all-refs' @('--all')
    # v1.5.0 rejects positional revision arguments: scope comes from snapshot refs.
    foreach ($plan in $script:ReportPlans) {
        if ($plan.Json -and -not $IncludeJson) { continue }
        $draft = Join-Path $script:ScratchDirectory $plan.Name
        Write-Host ('Collecting complete {0} output.' -f $plan.Scope)
        $result = Invoke-ReadOnlyProcess -Executable $GitSizerPath -Arguments $plan.Arguments -WorkingDirectory $snapshots[$plan.Scope] -OutputFile $draft -TimeoutSeconds $CommandTimeoutSeconds
        if ($result.ExitCode -ne 0 -or (Get-Item -LiteralPath $draft).Length -eq 0) { throw ('git-sizer failed for {0}; no complete report was published.' -f $plan.Scope) }
        if ($plan.Json) { Get-Content -Raw -LiteralPath $draft | ConvertFrom-Json | Out-Null }
        $metadata.Reports += [pscustomobject]@{ Scope=$plan.Scope; File=$plan.Name; Command=('git-sizer '+($plan.Arguments -join ' ')); ExitCode=$result.ExitCode; Bytes=(Get-Item -LiteralPath $draft).Length; Sha256=(Get-FileHash -LiteralPath $draft -Algorithm SHA256).Hash }
    }
    # Publish only when both required scopes and every requested format succeeded.
    foreach ($report in $metadata.Reports) {
        [IO.File]::Move((Join-Path $script:ScratchDirectory $report.File),(Join-Path $runDirectory $report.File))
    }
    $metadata.Status = 'complete'
    Write-JsonFile (Join-Path $runDirectory 'metadata.json') $metadata
    Write-Host ('Complete reports saved locally: {0}' -f $runDirectory)
    Write-Host 'Nothing was uploaded, fetched, installed, or changed in the repository.'
} catch {
    if ($runDirectory) {
        $failure = [ordered]@{Ticket='4853343';Status='failed';GeneratedUtc=(Get-Date).ToUniversalTime().ToString('o');RequestedRevision=$Revision;Error=$_.Exception.Message;CompleteReportPublished=$false;CandidateChecks=@($script:CandidateChecks.ToArray())}
        Write-JsonFile (Join-Path $runDirectory 'FAILED.json') $failure
    }
    Write-Error $_.Exception.Message
    exit 1
} finally {
    # Delete only this run's own isolated snapshots; alternates is a text file, not a link.
    if ($script:ScratchDirectory -and (Test-Path -LiteralPath $script:ScratchDirectory)) {
        $resolvedScratch = [IO.Path]::GetFullPath($script:ScratchDirectory).TrimEnd('\','/')
        $expectedScratch = [IO.Path]::GetFullPath((Join-Path $runDirectory '_incomplete')).TrimEnd('\','/')
        if (-not $resolvedScratch.Equals($expectedScratch,[StringComparison]::OrdinalIgnoreCase) -or
            -not $resolvedScratch.StartsWith([IO.Path]::GetFullPath($runDirectory).TrimEnd('\','/')+'\',[StringComparison]::OrdinalIgnoreCase)) {
            throw 'Refusing cleanup outside this run output directory.'
        }
        Remove-Item -LiteralPath $resolvedScratch -Recurse -Force
    }
}
