[CmdletBinding()]
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$target = 'E:\work\image\.agents'
$restoreOwner = 'LUYUAN\luyua'
$item = Get-Item -LiteralPath $target -Force
if ($item.FullName.TrimEnd('\') -ine $target -or (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
    throw 'Refusing: target must be the exact existing .agents directory and must not be a link.'
}
$aclBefore = Get-Acl -LiteralPath $target
$accessBefore = $aclBefore.GetSecurityDescriptorSddlForm([System.Security.AccessControl.AccessControlSections]::Access)
$plan = [ordered]@{
    target = $target
    currentOwner = $aclBefore.Owner
    proposedOwner = $restoreOwner
    command = 'icacls E:\work\image\.agents /setowner LUYUAN\luyua'
    recursive = $false
    grantOrResetPermissions = $false
    applyRequested = [bool]$Apply
}
if (-not $Apply) { $plan | ConvertTo-Json; return }
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Administrator elevation is required; no changes made.'
}
if ($aclBefore.Owner -ine 'LUYUAN\CodexSandboxOffline') {
    throw 'Owner differs from the reviewed state; no changes made. Inspect current ownership first.'
}
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')
$beforePath = Join-Path $PSScriptRoot ("acl-before-" + $stamp + '.json')
[ordered]@{
    observedAtUtc = [DateTime]::UtcNow.ToString('o')
    target = $target
    owner = $aclBefore.Owner
    sddl = $aclBefore.Sddl
    accessSddl = $accessBefore
} | ConvertTo-Json | Set-Content -LiteralPath $beforePath -Encoding UTF8
& "$env:SystemRoot\System32\icacls.exe" $target /setowner $restoreOwner
$commandExitCode = $LASTEXITCODE
$aclAfter = Get-Acl -LiteralPath $target
$accessAfter = $aclAfter.GetSecurityDescriptorSddlForm([System.Security.AccessControl.AccessControlSections]::Access)
$result = [ordered]@{
    observedAtUtc = [DateTime]::UtcNow.ToString('o')
    target = $target
    commandExitCode = $commandExitCode
    beforeFile = $beforePath
    ownerAfter = $aclAfter.Owner
    sddlAfter = $aclAfter.Sddl
    accessSddlUnchanged = ($accessBefore -ceq $accessAfter)
    expectedOwnerRestored = ($aclAfter.Owner -ieq $restoreOwner)
    note = 'Only ownership was requested to change. No recursive operation, grant, ACL reset, sandbox setting change, or automatic rollback. If access SDDL differs, inspect for concurrent official helper changes before concluding.'
}
$result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot ("acl-result-" + $stamp + '.json')) -Encoding UTF8
$result | ConvertTo-Json
if ($commandExitCode -ne 0 -or $aclAfter.Owner -ine $restoreOwner) { exit 1 }

