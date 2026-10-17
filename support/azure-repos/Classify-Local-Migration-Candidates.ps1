#requires -Version 7.0
[CmdletBinding()]
param([string]$Repository='E:/work/image',[string]$OutputDirectory=$PSScriptRoot)
$ErrorActionPreference='Stop'
$env:GIT_NO_LAZY_FETCH='1'
$env:GIT_OPTIONAL_LOCKS='0'
function Read-Git([string[]]$Arguments) {
    $data=& git -C $Repository -c core.quotepath=false @Arguments
    if($LASTEXITCODE -ne 0){throw "Read-only Git command failed: $($Arguments[0])"}
    return ($data -join "`n")
}
$head=Read-Git @('rev-parse','HEAD')
$pending=@(Get-Content -LiteralPath (Join-Path $OutputDirectory 'local-pending-paths.json') -Raw | ConvertFrom-Json)
$untracked=(Read-Git @('ls-files','--others','--exclude-standard','-z')).Split([char]0,[StringSplitOptions]::RemoveEmptyEntries)
$cleanTeam=@{}
foreach($entry in (Read-Git @('ls-tree','-r','-z','949b1516','--','designs/team-invites-20260928')).Split([char]0,[StringSplitOptions]::RemoveEmptyEntries)) {
    if($entry -match '^[0-9]+ blob ([0-9a-f]+)\t(.*)$'){$cleanTeam[$Matches[2]]=$Matches[1]}
}
$all=[Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
foreach($entry in $pending){$all[$entry.Path]=$entry}
foreach($path in $untracked){$all[$path]=[pscustomobject]@{Path=$path;Change='Untracked';BaseGitBlob=$null;HeadGitBlob=$null}}
$result=[Collections.Generic.List[object]]::new()
foreach($candidate in $all.Values) {
    $path=$candidate.Path
    $item=[IO.FileInfo]::new((Join-Path $Repository $path))
    $category='KeepCandidate'; $reason='Current project content, integration source, design metadata, or provenance.'
    if($candidate.Change -eq 'D'){$category='DeletionReview';$reason='Explicit committed deletion; apply only after comparing the other computer content to the original base blob.'}
    elseif(-not $item.Exists){$category='MissingReview';$reason='No current file; never infer deletion from sparse checkout.'}
    elseif($path -match '^\.cache/azure-repos-probe-20261016/'){$category='Exclude';$reason='Synthetic Azure probe, tools, or authentication diagnostics.'}
    elseif($path -match '^designs/team-invites-20260928/(aoi-fix/(build|baseline-source)/|aoi-fix/baseline-source\.tar$|integration/friend-invites\.exe$|integration/verification-data/(bin|obj)/|.*(?:^|/)(go-cache|go-tmp|gocache|gotmp)/)'){$category='Exclude';$reason='Team verification cache or build output; explicitly excluded by its local .gitignore.'}
    elseif($path -match '^designs/team-invites-20260928/.*\.(exe|pdb|obj|ilk|tlog|lastbuildstate|recipe|log)(\.(stderr|stdout)\.txt)?$'){$category='Exclude';$reason='Team test binary, build output, or raw log.'}
    elseif($path -match '^designs/class-skills-20260928/integration/(\.contract-generation|python-deps)/'){$category='Exclude';$reason='Downloaded contract-generation tooling, module cache, or Python dependency cache.'}
    elseif($path -match '^designs/class-skills-20260928/integration/\.client-validation/(.*/)?(bin|obj)/' -or $path -match '^designs/class-skills-20260928/integration/\.client-validation/.*\.(dll|pdb|exe)$'){$category='Exclude';$reason='Class-skill verification build output.'}
    elseif($path -match '^designs/(class-skills-20260928|equipment-ui-20261008|equipment-ui-20261009)/.*\.log$'){$category='Exclude';$reason='Raw compiler, preview-server, or Unity log.'}
    elseif($path -match '^support/azure-repos/(local-(migration-audit|pending-paths|migration-candidates|migration-candidates-summary)\.(json|txt)|Collect-Local-Migration-Audit\.ps1|Classify-Local-Migration-Candidates\.ps1)$'){$category='AuditOnly';$reason='Local reconciliation audit, not production content.'}
    elseif($path -match '^designs/team-invites-20260928/'){
        if(-not $cleanTeam.ContainsKey($path)){$category='TeamContentReview';$reason='Not present in the previously sanitized 949b1516 delivery; preserve new source, but inspect before upload.'}
        elseif($candidate.HeadGitBlob -ne $cleanTeam[$path]){$category='TeamContentReview';$reason='Current source tree blob differs from the previously sanitized 949b1516 delivery; check for credentials and preserve later code changes.'}
        else{$reason='Path and tree blob match the previously sanitized 949b1516 team delivery; current working content still needs final hash verification.'}
    }
    $result.Add([pscustomobject][ordered]@{Path=$path;Category=$category;Reason=$reason;Change=$candidate.Change;Bytes=$(if($item.Exists){$item.Length}else{$null});BaseGitBlob=$candidate.BaseGitBlob;HeadGitBlob=$candidate.HeadGitBlob;CleanDeliveryGitBlob=$cleanTeam[$path]})
}
$flagged=@((Read-Git @('ls-files','-z')).Split([char]0,[StringSplitOptions]::RemoveEmptyEntries) | Where-Object {$_ -match '(?i)(^|/)(\.env(\..*)?|id_(rsa|ed25519)(\.pub)?|credentials(\..*)?|secrets?(\..*)?|.*\.pfx|.*\.p12|.*\.pem|.*\.key|.*credential.*|.*password.*)$'})
$summary=[ordered]@{
    GeneratedUtc=[DateTime]::UtcNow.ToString('o');Head=$head
    CandidateCount=$result.Count
    Categories=@($result|Group-Object Category|ForEach-Object {[ordered]@{Category=$_.Name;Count=$_.Count;Bytes=[long](($_.Group|Measure-Object Bytes -Sum).Sum)}})
    CredentialsPathNameMatches=$flagged
    Scope='Metadata-only proposal; no file copies, uploads, deletions, history rewrites, credential-value reads, or content-based conflict resolutions performed.'
    Limitations=@('KeepCandidate does not independently prove an image is the currently approved final asset.','Content scans and file hashes must be checked before uploading; matching a historical blob does not prove an uncommitted file is unchanged.','Other computer changes and LFS data have not been compared.','Source checkout can change concurrently. Re-run collection/classification immediately before packaging.')
}
$result | Sort-Object Path | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'local-migration-candidates.json') -Encoding utf8NoBOM
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'local-migration-candidates-summary.json') -Encoding utf8NoBOM
$summary | ConvertTo-Json -Depth 6
