#requires -Version 7.0
[CmdletBinding()]
param([string]$Repository='E:/work/image',[string]$OutputDirectory=$PSScriptRoot)
$ErrorActionPreference='Stop'
$env:GIT_NO_LAZY_FETCH='1'
$env:GIT_OPTIONAL_LOCKS='0'
$capturedUtc=[DateTime]::UtcNow.ToString('o')
$headStart=(& git -C $Repository rev-parse HEAD).Trim()
if($LASTEXITCODE -ne 0){throw 'Unable to read current HEAD.'}
$candidates=@(Get-Content -LiteralPath (Join-Path $OutputDirectory 'local-migration-candidates.json') -Raw|ConvertFrom-Json)
$findings=[Collections.Generic.List[object]]::new()
$credentialLiteral=[regex]::new('(?im)(?:^|[\s{,])[''"'']?([\w-]*(?:password|passwd|client[_-]?secret|api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|private[_-]?key)[\w-]*)[''"'']?\s*(?::=|=|:)\s*([''"''])([^\r\n]*?)\2')
$knownToken=[regex]::new('(?m)(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{40,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
$textExtensions=@('.ps1','.py','.go','.cs','.cpp','.cc','.h','.yaml','.yml','.json','.md','.txt','.xml','.config','.env','.js','.mjs','.ts','.html','.sh','.cmd','.bat','.proto','.ini','.toml')
foreach($entry in $candidates){
    if($entry.Category -eq 'TeamContentReview'){
        if($entry.Path -like 'designs/team-invites-20260928/integration/original/*'){$entry.Category='Exclude';$entry.Reason='Original pre-change source backup; current integration source is retained separately.'}
        elseif($entry.Path -eq 'designs/team-invites-20260928/aoi-fix/deployed-pdb-sources.txt'){$entry.Category='Exclude';$entry.Reason='Raw debugger source-list diagnostic.'}
        elseif($entry.Path -eq 'designs/team-invites-20260928/integration/server/PROGRESS.md'){$entry.Category='DeferredReview';$entry.Reason='Large imported server progress/history record not present in sanitized delivery; preserve locally for later comparison.'}
        elseif($entry.Path -like 'designs/team-invites-20260928/live-acceptance/*.png.json'){$entry.Category='Exclude';$entry.Reason='Capture metadata for screenshots already removed from the project.'}
        elseif($entry.Path -eq 'designs/team-invites-20260928/live-acceptance/robot.yaml'){$entry.Category='BlockedSensitiveContent';$entry.Reason='Nonempty password field differs from sanitized 949b1516 template. Never upload current bytes.';$findings.Add([pscustomobject]@{Path=$entry.Path;Field='password';Finding='Nonempty credential field';ValuePrinted=$false})}
        else{$entry.Category='KeepCandidate';$entry.Reason='Additional integration/generated source or human-readable verification metadata; retained after targeted credential-pattern scan.'}
    }
    if($entry.Category -ne 'KeepCandidate'){continue}
    if($entry.Path -like 'qdao_city_tiles_4k_20260916/*'){$entry.Category='DeferredReview';$entry.Reason='City continuation contains repair/context/assembly versions. Preserve locally and compare current asset references on the other PC before choosing production files.';continue}
    if($entry.Path -match '^designs/team-invites-20260928/live-acceptance/unity-[^/]+/.*(?:-report|-signal|pair-result)\.json$'){$entry.Category='DeferredReview';$entry.Reason='Raw Unity test-session report/signal/result JSON. Keep local; retain summarized verification separately.';continue}
    $path=Join-Path $Repository $entry.Path
    if(-not [IO.File]::Exists($path)){$entry.Category='DeferredReview';$entry.Reason='File no longer exists at final review; no restoration or deletion inferred.';continue}
    $file=[IO.FileInfo]::new($path)
    $entry.Bytes=$file.Length
    if($entry.Path -match '^support/azure-repos/(local-.*\.(json|txt)|(?:Collect|Classify|Review)-Local-Migration.*\.ps1)$'){$entry.Category='AuditOnly';$entry.Reason='Local audit artifact; package separately from production delta.';continue}
    if([IO.Path]::GetExtension($path).ToLowerInvariant() -in $textExtensions -and $file.Length -le 16MB){
        $body=[IO.File]::ReadAllText($path)
        foreach($match in $credentialLiteral.Matches($body)){
            $field=$match.Groups[1].Value
            $value=$match.Groups[3].Value
            if($entry.Path -eq 'designs/class-skills-20260928/integration/client/tools/gen_messageids.ps1' -and $field -eq 'ClientPlayerLoginRefreshToken' -and $value -eq 'RefreshToken'){continue}
            if([string]::IsNullOrWhiteSpace($value) -or $value -match '^(?:<[^>]+>|\$\{[^}]+\}|\$env:.*|REDACTED|__REDACTED__|CHANGE_ME|CHANGEME|YOUR_[A-Z_]+)$'){continue}
            $entry.Category='BlockedSensitiveContent';$entry.Reason='Nonempty credential-like literal detected; requires manual review or a sanitized template before upload.'
            $findings.Add([pscustomobject]@{Path=$entry.Path;Field=$field;Finding='Nonempty credential-like string literal';ValuePrinted=$false})
        }
        if($knownToken.IsMatch($body)){$entry.Category='BlockedSensitiveContent';$entry.Reason='Credential-token or private-key pattern detected; manual review required.';$findings.Add([pscustomobject]@{Path=$entry.Path;Field='token-or-private-key-pattern';Finding='Recognized credential pattern';ValuePrinted=$false})}
    }
    if($entry.Category -eq 'KeepCandidate'){
        $hash=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        $entry|Add-Member -NotePropertyName Sha256 -NotePropertyValue $hash -Force
    }
}
$headEnd=(& git -C $Repository rev-parse HEAD).Trim()
$final=[ordered]@{
    CapturedUtc=$capturedUtc;CompletedUtc=[DateTime]::UtcNow.ToString('o');HeadStart=$headStart;HeadEnd=$headEnd
    ConcurrentHeadChange=($headStart -ne $headEnd)
    Categories=@($candidates|Group-Object Category|ForEach-Object {[ordered]@{Category=$_.Name;Count=$_.Count;Bytes=[long](($_.Group|Measure-Object Bytes -Sum).Sum)}})
    CredentialFindings=@($findings)
    ScanScope='Candidate text files no larger than 16MiB: credential-like quoted literals and common token/private-key signatures. Values are never printed or serialized. This is a targeted scan, not a guarantee against all possible secrets.'
    FinalKeepRequirements=@('Use only KeepCandidate files matching their recorded SHA256 and byte count.','No Git history, old .git directory, missing sparse paths, excluded/deferred/blocked files, or screenshot binaries are to be copied.','Preserve deferred/blocked records locally and compare them explicitly later.','NPC and other concurrent task output may change; recheck hashes and update the manifest when needed.','The new Azure main would be an incomplete migration starting point, not a complete project checkout.')
}
$candidates|Sort-Object Path|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $OutputDirectory 'local-migration-reviewed.json') -Encoding utf8NoBOM
$final|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $OutputDirectory 'local-migration-reviewed-summary.json') -Encoding utf8NoBOM
$candidates|Where-Object Category -eq KeepCandidate|Select-Object -ExpandProperty Path|Set-Content -LiteralPath (Join-Path $OutputDirectory 'local-reviewed-keep.txt') -Encoding utf8NoBOM
$candidates|Where-Object {$_.Category -in @('BlockedSensitiveContent','DeferredReview')}|Select-Object -ExpandProperty Path|Set-Content -LiteralPath (Join-Path $OutputDirectory 'local-reviewed-hold.txt') -Encoding utf8NoBOM
$final|ConvertTo-Json -Depth 6
