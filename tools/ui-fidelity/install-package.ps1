param([Parameter(Mandatory=$true)][string]$ManifestPath)
$ErrorActionPreference='Stop'
$clientRoot=[IO.Path]::GetFullPath('E:\work\mmorpg-client')
$packageRoot=Split-Path -Parent ([IO.Path]::GetFullPath($ManifestPath))
$manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
function Sha([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Under([string]$base,[string]$relative){
    $resolved=[IO.Path]::GetFullPath((Join-Path $base $relative))
    if(-not $resolved.StartsWith($base+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw "Path escapes package or client: $relative"}
    $resolved
}
$guards=@{}
foreach($guard in @($manifest.guards)){
    if($null -eq $guard){continue}
    $guards[(Under $clientRoot $guard.target)]=$guard.sha256Before
}
foreach($guard in (@($manifest.sourceChecks)+@($manifest.sources))){
    if($null -eq $guard){continue}
    $absolute=[IO.Path]::GetFullPath($guard.source)
    if(-not $absolute.StartsWith($clientRoot+'\Assets\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected source guard root'}
    $guards[$absolute]=$guard.sha256
}
if($manifest.sourceGuard){
    $absolute=[IO.Path]::GetFullPath($manifest.sourceGuard.source)
    if(-not $absolute.StartsWith($clientRoot+'\Assets\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected source guard root'}
    $guards[$absolute]=$manifest.sourceGuard.sha256
}
$payload=@()
foreach($file in $manifest.files){
    $relative=if($file.target){$file.target}elseif($file.destination){$file.destination}else{$file.path}
    if(-not $relative.StartsWith('Assets/')){throw "Unexpected payload target: $relative"}
    $source=if($file.source){Under $packageRoot $file.source}else{
        $stagingRoot=[IO.Path]::GetFullPath($manifest.staging_root)
        if(-not $stagingRoot.StartsWith($packageRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Staging root escapes package'}
        Under $stagingRoot $relative
    }
    $target=Under $clientRoot $relative
    if((Sha $source) -ne $file.sha256){throw "Payload hash changed: $source"}
    $exists=Test-Path -LiteralPath $target
    $current=if($exists){Sha $target}else{''}
    if($exists -and $current -ne $file.sha256){
        if($file.expected_target_sha256){
            if($current -ne $file.expected_target_sha256){throw "Client changed since staging: $target"}
        }elseif($guards.ContainsKey($target)){
            if($current -ne $guards[$target]){throw "Client changed since staging: $target"}
        }elseif($file.overwriteExisting -eq $true -and $target.EndsWith('.meta')){
            $oldGuid=(Select-String -LiteralPath $target -Pattern '^guid:').Line
            $newGuid=(Select-String -LiteralPath $source -Pattern '^guid:').Line
            if($oldGuid -ne $newGuid){throw "Existing GUID would change: $target"}
        }else{throw "Unapproved existing payload collision: $target"}
    }
    $payload+=[pscustomobject]@{source=$source;target=$target;sha256=$file.sha256;changed=($current -ne $file.sha256)}
}
# Validate the whole package before making the first write.
foreach($file in $payload){
    if(-not $file.changed){continue}
    [IO.Directory]::CreateDirectory((Split-Path -Parent $file.target)) | Out-Null
    Copy-Item -LiteralPath $file.source -Destination $file.target
    if((Sha $file.target) -ne $file.sha256){throw "Installed payload did not match: $($file.target)"}
}
$qa=Join-Path $packageRoot 'qa';[IO.Directory]::CreateDirectory($qa)|Out-Null
[pscustomobject]@{status='installed';completedAtUtc=[DateTime]::UtcNow.ToString('O');clientRoot=$clientRoot;files=$payload} |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $qa 'install-result.json') -Encoding utf8
Write-Output "UI_FIDELITY_INSTALLED files=$($payload.Count) changed=$(@($payload|Where-Object changed).Count)"
