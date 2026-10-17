#requires -Version 5.1
$ErrorActionPreference = 'Stop'
Write-Host 'GitHub ticket 4853343 - complete local Git history report'
Write-Host 'No download, upload, cleanup or repository rewrite is performed.'
$repoInput = Read-Host 'Repository directory on this PC (press Enter to search)'
$repoInput = $repoInput.Trim().Trim('"')
$outputRoot = Join-Path ([Environment]::GetFolderPath('Desktop')) 'GitHub-4853343-reports'
$collector = Join-Path $PSScriptRoot 'Collect-GitSizer.ps1'
if ($repoInput) {
    & $collector -Repository $repoInput -IncludeJson -OutputDirectory $outputRoot
} else {
    & $collector -IncludeJson -OutputDirectory $outputRoot
}
Write-Host ('Reports are saved in: ' + $outputRoot)
