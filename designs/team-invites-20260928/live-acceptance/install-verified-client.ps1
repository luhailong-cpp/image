[CmdletBinding()]
param(
    [switch]$PrepareOnly,
    [string]$PairResultPath
)

# Updating the existing one-click client is the last step of the team-invitation task.
# Preparation copies and hashes the entire build. Installation requires both real
# UI clients to have passed, and never overwrites a staging directory or a backup.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$tmpRoot = [IO.Path]::GetFullPath('E:/work/tmp').TrimEnd('\', '/')
$sourceDir = [IO.Path]::GetFullPath('E:/work/tmp/wuxing-team-invites-player-20260929').TrimEnd('\', '/')
$stagingDir = [IO.Path]::GetFullPath('E:/work/tmp/showcase_player.team-invites-20261001-new').TrimEnd('\', '/')
$targetDir = [IO.Path]::GetFullPath('E:/work/tmp/showcase_player').TrimEnd('\', '/')
$backupDir = [IO.Path]::GetFullPath('E:/work/tmp/showcase_player.before-team-invites-20261001').TrimEnd('\', '/')
$preparedPath = Join-Path $PSScriptRoot 'client-install-prepared-20261001.json'
$installedPath = Join-Path $PSScriptRoot 'client-install-result-20261001.json'

function Assert-LocalPackagePath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    if (-not $full.StartsWith($tmpRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Package path escaped E:/work/tmp: $full"
    }
    if ([IO.Path]::GetDirectoryName($full) -ne $tmpRoot) { throw "Package must be a direct child of E:/work/tmp: $full" }
    $ancestor = $full
    while ($ancestor) {
        if (Test-Path -LiteralPath $ancestor) {
            $item = Get-Item -LiteralPath $ancestor -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing linked package path: $ancestor" }
        }
        $ancestor = [IO.Path]::GetDirectoryName($ancestor)
    }
}

function Get-PackageManifest([string]$Directory) {
    Assert-LocalPackagePath $Directory
    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) { throw "Missing package: $Directory" }
    $items = @(Get-ChildItem -LiteralPath $Directory -Recurse -Force)
    foreach ($item in $items) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing linked package entry: $($item.FullName)" }
    }
    $entries = @($items | Where-Object { -not $_.PSIsContainer } | Sort-Object FullName | ForEach-Object {
        [pscustomobject][ordered]@{
            path = [IO.Path]::GetRelativePath($Directory, $_.FullName).Replace('\', '/')
            bytes = $_.Length
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        }
    })
    if ($entries.Count -eq 0) { throw "Empty package: $Directory" }
    foreach ($required in @('mmorpg.exe', 'UnityPlayer.dll', 'mmorpg_Data/globalgamemanagers')) {
        if (@($entries | Where-Object { $_.path -eq $required }).Count -ne 1) { throw "Missing Unity player file: $required" }
    }
    return ,$entries
}

function Assert-SameManifest($Expected, $Actual, [string]$Description) {
    $left = @($Expected | ForEach-Object { "$($_.path)|$($_.bytes)|$($_.sha256)" })
    $right = @($Actual | ForEach-Object { "$($_.path)|$($_.bytes)|$($_.sha256)" })
    if ($left.Count -ne $right.Count -or @(Compare-Object $left $right -CaseSensitive).Count) {
        throw "Package verification failed: $Description"
    }
}

function Get-ManifestHash($Manifest) {
    $canonical = (@($Manifest | ForEach-Object { "$($_.path)|$($_.bytes)|$($_.sha256)" }) -join "`n") + "`n"
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return [Convert]::ToHexString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($canonical))) }
    finally { $sha.Dispose() }
}

function Assert-NoPackageProcess {
    foreach ($process in @(Get-CimInstance Win32_Process -Filter "Name = 'mmorpg.exe'")) {
        if (-not $process.ExecutablePath) { throw "Cannot verify executable path for running mmorpg.exe PID $($process.ProcessId)." }
        $path = [IO.Path]::GetFullPath($process.ExecutablePath)
        foreach ($directory in @($targetDir, $stagingDir, $backupDir)) {
            if ($path.StartsWith($directory + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
                throw "Close the existing player before installation: PID $($process.ProcessId), $path"
            }
        }
    }
}

foreach ($directory in @($sourceDir, $stagingDir, $targetDir, $backupDir)) { Assert-LocalPackagePath $directory }
if (Test-Path -LiteralPath $backupDir) { throw "A previous backup already exists; refusing to overwrite it: $backupDir" }
if (Test-Path -LiteralPath $installedPath) { throw "Installation evidence already exists; refusing a repeated replacement: $installedPath" }
if (-not (Test-Path -LiteralPath $targetDir -PathType Container)) { throw "Existing default client not found: $targetDir" }

Write-Output 'Hashing the complete source player package.'
$sourceManifest = Get-PackageManifest $sourceDir
$prepared = $null
if (Test-Path -LiteralPath $stagingDir) {
    if (Test-Path -LiteralPath $preparedPath -PathType Leaf) {
        $prepared = Get-Content -LiteralPath $preparedPath -Raw | ConvertFrom-Json
        if ($prepared.source -ne $sourceDir -or $prepared.staging -ne $stagingDir -or $prepared.target -ne $targetDir -or $prepared.backup -ne $backupDir) {
            throw 'Existing preparation evidence refers to different paths.'
        }
        Assert-SameManifest $prepared.files $sourceManifest 'source changed after preparation'
    }
    # A fully copied package from an interrupted preparation can be adopted only
    # after hashing every file and proving exact equality; nothing is overwritten.
    Assert-SameManifest $sourceManifest (Get-PackageManifest $stagingDir) 'existing staging differs from the source'
    Assert-SameManifest $sourceManifest (Get-PackageManifest $sourceDir) 'source changed while checking existing staging'
    Write-Output 'Existing prepared package matches every source file; reusing it without changes.'
} else {
    if (Test-Path -LiteralPath $preparedPath) { throw 'Preparation evidence exists without its staging directory; refusing to replace evidence.' }
    New-Item -ItemType Directory -Path $stagingDir | Out-Null
    foreach ($item in @(Get-ChildItem -LiteralPath $sourceDir -Force)) {
        Copy-Item -LiteralPath $item.FullName -Destination $stagingDir -Recurse
    }
    $stagingManifest = Get-PackageManifest $stagingDir
    Assert-SameManifest $sourceManifest $stagingManifest 'copied staging package'
    Assert-SameManifest $sourceManifest (Get-PackageManifest $sourceDir) 'source changed while copying'
}
if (-not $prepared) {
    $prepared = [ordered]@{
        status = 'PREPARED_ONLY'
        preparedAtUtc = [DateTime]::UtcNow.ToString('o')
        source = $sourceDir
        staging = $stagingDir
        target = $targetDir
        backup = $backupDir
        fileCount = $sourceManifest.Count
        bytes = ($sourceManifest | Measure-Object -Property bytes -Sum).Sum
        manifestSha256 = Get-ManifestHash $sourceManifest
        files = $sourceManifest
    }
    $prepared | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $preparedPath -Encoding utf8
}

if ($PrepareOnly) {
    [ordered]@{ status='PREPARED_ONLY'; fileCount=$prepared.fileCount; bytes=$prepared.bytes; manifestSha256=$prepared.manifestSha256; evidence=$preparedPath; staging=$stagingDir; defaultClientUnchanged=$true } | ConvertTo-Json
    exit 0
}

if (-not $PairResultPath) { throw 'Installation requires -PairResultPath from the successful real two-client UI run.' }
$pairFullPath = [IO.Path]::GetFullPath($PairResultPath)
$evidenceRoot = [IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
if (-not $pairFullPath.StartsWith($evidenceRoot, [StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($pairFullPath) -ne 'pair-result.json') {
    throw 'Pair evidence must be a pair-result.json under this live-acceptance directory.'
}
$pair = Get-Content -LiteralPath $pairFullPath -Raw | ConvertFrom-Json
$pairDirectory = [IO.Path]::GetDirectoryName($pairFullPath)
if ([IO.Path]::GetFullPath($pair.player) -ne (Join-Path $sourceDir 'mmorpg.exe')) { throw 'Successful pair did not execute the prepared source package.' }
if ([IO.Path]::GetFullPath($pair.directory).TrimEnd('\', '/') -ne $pairDirectory) { throw 'Pair report directory does not match its evidence location.' }
if ($pair.runId -notmatch '^[0-9a-f]{16}$' -or @($pair.clients).Count -ne 2) { throw 'Invalid real-pair run or client count.' }
foreach ($role in @('leader', 'member')) {
    $clients = @($pair.clients | Where-Object { $_.role -eq $role })
    if ($clients.Count -ne 1 -or $clients[0].passed -isnot [bool] -or -not $clients[0].passed -or $clients[0].exitCode -ne 0) {
        throw "Real UI client did not pass: $role"
    }
    $clientReport = Get-Content -LiteralPath (Join-Path $pairDirectory ($pair.runId + '-' + $role + '-report.json')) -Raw | ConvertFrom-Json
    $clientLog = Get-Content -LiteralPath (Join-Path $pairDirectory ($role + '.log')) -Raw
    if ($clientReport.result -ne 'PASS' -or $clientLog -notmatch '\[TeamVerify\].*RESULT=PASS') { throw "Missing successful client evidence: $role" }
}
if ([DateTimeOffset]::Parse($pair.completedAt).UtcDateTime -lt (Get-Item -LiteralPath (Join-Path $sourceDir 'mmorpg.exe')).LastWriteTimeUtc) {
    throw 'Pair evidence predates the source player build.'
}
Assert-NoPackageProcess
# Final absolute paths are checked immediately before both directory renames.
foreach ($directory in @($stagingDir, $targetDir, $backupDir)) { Assert-LocalPackagePath $directory }
if (Test-Path -LiteralPath $backupDir) { throw 'Backup appeared during verification; refusing to overwrite it.' }
Rename-Item -LiteralPath $targetDir -NewName ([IO.Path]::GetFileName($backupDir))
try { Rename-Item -LiteralPath $stagingDir -NewName ([IO.Path]::GetFileName($targetDir)) }
catch {
    if (-not (Test-Path -LiteralPath $targetDir) -and (Test-Path -LiteralPath $backupDir)) {
        Assert-LocalPackagePath $backupDir
        Assert-LocalPackagePath $targetDir
        Rename-Item -LiteralPath $backupDir -NewName ([IO.Path]::GetFileName($targetDir))
    }
    throw
}
$installedManifest = Get-PackageManifest $targetDir
Assert-SameManifest $prepared.files $installedManifest 'installed default client'
$result = [ordered]@{
    status = 'INSTALLED'
    installedAtUtc = [DateTime]::UtcNow.ToString('o')
    source = $sourceDir
    target = $targetDir
    backup = $backupDir
    acceptedPairResult = $pairFullPath
    acceptedRunId = $pair.runId
    preparationEvidence = $preparedPath
    fileCount = $installedManifest.Count
    bytes = ($installedManifest | Measure-Object -Property bytes -Sum).Sum
    manifestSha256 = Get-ManifestHash $installedManifest
    executableSha256 = (Get-FileHash -LiteralPath (Join-Path $targetDir 'mmorpg.exe') -Algorithm SHA256).Hash
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $installedPath -Encoding utf8
$result | ConvertTo-Json -Depth 5
