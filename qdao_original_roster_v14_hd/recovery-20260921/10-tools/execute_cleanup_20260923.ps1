param([ValidateSet('Workspace', 'Host')][string]$Scope, [switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$taskRecovery = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskPlanPath = Join-Path $taskRecovery '10-work\cleanup-20260923\plan.json'
$taskPlan = Get-Content -LiteralPath $taskPlanPath -Raw | ConvertFrom-Json
$taskNativeRoot = Join-Path $taskRecovery '10-generation'
$taskContactRoot = Join-Path $taskRecovery '10-delivery-preview\revisions\s-first-check\contact'
$taskCacheRoot = 'C:\Users\Administrator\.codex\generated_images'
$taskThreads = @('01a0c4ab-1960-75b0-bc37-6104e343b5e3', '01a0c4ab-bcf0-7c62-9a2a-62536ab300c4', '01a0c4b1-3bc5-71d0-92ad-0a3d9a0f0968', '01a0c4b7-ef5b-76c3-b8fd-213c5b2f605b')
$taskTargets = @($taskPlan.targets | Where-Object { ($_.kind -eq 'host-generated-duplicate') -eq ($Scope -eq 'Host') })
$taskLogPath = Join-Path $taskRecovery ('10-work\cleanup-20260923\result-' + $Scope.ToLowerInvariant() + '.json')
if ((Test-Path -LiteralPath $taskLogPath) -and !$ValidateOnly) { throw "Cleanup result already exists: $taskLogPath" }
function Assert-TaskFile($entry) {
    $taskResolved = (Resolve-Path -LiteralPath $entry.path).ProviderPath
    if ($taskResolved -ne [IO.Path]::GetFullPath($entry.path)) { throw "Unexpected resolved path: $taskResolved" }
    $taskInfo = Get-Item -LiteralPath $taskResolved
    if ($taskInfo.PSIsContainer -or ($taskInfo.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "Not a regular file: $taskResolved" }
    if ((Get-FileHash -LiteralPath $taskResolved -Algorithm SHA256).Hash -ne $entry.sha256) { throw "SHA changed: $taskResolved" }
    if ($taskInfo.Length -ne $entry.bytes) { throw "Size changed: $taskResolved" }
}
foreach ($taskKeep in $taskPlan.retainedNativeWIP) { Assert-TaskFile $taskKeep }
$taskIdentitySHA = (Get-FileHash -LiteralPath $taskPlan.protectedOriginalIdentityDesign -Algorithm SHA256).Hash
if ($taskIdentitySHA -ne 'ea068eb40dbd372b108d2e7d041c8e270e898f8ae979ce039873a08e49a0260f') { throw 'Identity design changed' }
foreach ($taskEntry in $taskTargets) {
    $taskFull = [IO.Path]::GetFullPath($taskEntry.path)
    $taskParent = [IO.Path]::GetDirectoryName($taskFull)
    switch ($taskEntry.kind) {
        'rejected-or-superseded-raw' {
            if ([IO.Path]::GetDirectoryName($taskParent) -ne $taskNativeRoot -or [IO.Path]::GetFileName($taskFull) -ne 'raw.png') { throw "Outside native scope: $taskFull" }
        }
        'obsolete-partial-contact-sheet' {
            if ($taskParent -ne $taskContactRoot -or [IO.Path]::GetExtension($taskFull) -ne '.jpg') { throw "Outside contact scope: $taskFull" }
        }
        'host-generated-duplicate' {
            if ([IO.Path]::GetDirectoryName($taskParent) -ne $taskCacheRoot -or [IO.Path]::GetFileName($taskParent) -notin $taskThreads -or [IO.Path]::GetFileName($taskFull) -notmatch '^exec-[0-9a-f-]+\.png$') { throw "Outside exact host scope: $taskFull" }
        }
        default { throw "Unknown kind: $($taskEntry.kind)" }
    }
    Assert-TaskFile $taskEntry
}
if ($ValidateOnly) {
    [ordered]@{ scope=$Scope; validatedFiles=$taskTargets.Count; retainedNativeWIP=$taskPlan.retainedNativeWIP.Count; deleteBytes=($taskTargets | Measure-Object -Property bytes -Sum).Sum; recursiveDeletion=$false } | ConvertTo-Json
    exit 0
}
$taskDeleted = [Collections.Generic.List[object]]::new()
try {
    foreach ($taskEntry in $taskTargets) {
        Assert-TaskFile $taskEntry
        Remove-Item -LiteralPath $taskEntry.path
        if (Test-Path -LiteralPath $taskEntry.path) { throw "Deletion not confirmed: $($taskEntry.path)" }
        $taskDeleted.Add($taskEntry)
    }
    foreach ($taskKeep in $taskPlan.retainedNativeWIP) { Assert-TaskFile $taskKeep }
    if ((Get-FileHash -LiteralPath $taskPlan.protectedOriginalIdentityDesign -Algorithm SHA256).Hash -ne $taskIdentitySHA) { throw 'Identity changed during cleanup' }
} finally {
    [ordered]@{ scope=$Scope; completedAt=[DateTime]::UtcNow.ToString('o'); planSHA256=(Get-FileHash -LiteralPath $taskPlanPath -Algorithm SHA256).Hash.ToLowerInvariant(); status=$(if ($taskDeleted.Count -eq $taskTargets.Count) { 'deleted-and-verified' } else { 'partial-stop' }); recursiveDeletion=$false; deletedFiles=$taskDeleted.Count; deletedBytes=($taskDeleted | Measure-Object -Property bytes -Sum).Sum; retainedNativeWIP=$taskPlan.retainedNativeWIP.Count; targets=$taskDeleted } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskLogPath -Encoding UTF8
}
Get-Content -LiteralPath $taskLogPath -Raw | ConvertFrom-Json | Select-Object scope,status,deletedFiles,deletedBytes,retainedNativeWIP | ConvertTo-Json
