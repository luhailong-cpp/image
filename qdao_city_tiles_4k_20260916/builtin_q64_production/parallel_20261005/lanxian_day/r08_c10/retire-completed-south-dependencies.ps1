$ErrorActionPreference='Stop'
$allowedRoot='D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel_20261005\lanxian_day\r08_c10'
$tileResolved=(Resolve-Path -LiteralPath $allowedRoot).Path
if ($tileResolved -ne $allowedRoot) { throw 'Unexpected target resolution' }
$taskRoot=Split-Path -Parent $tileResolved
$records=@(
 @{file=(Join-Path $tileResolved 'west-repair\v3\core4096.png');sha256='02714e30830c5112d1a5d76e8666e57be626d6237b095f47c49aba3af50aa1e7'},
 @{file=(Join-Path $tileResolved 'west-repair\v3\extended4326.png');sha256='3d76bd7f4f990ad24f943982202c0a8a9ff284372900057c73da1fc3a34fc686'}
)
$dest=Join-Path $tileResolved 'retired-south-dependency-cleanup.json'
if (Test-Path -LiteralPath $dest) { throw 'Refuse to overwrite cleanup record' }
$finals=@()
foreach ($id in @('r08_c10','r09_c10','r09_c09')) {
 $manifest=Get-Content -Raw -LiteralPath (Join-Path $taskRoot "$id\selected\delivery.manifest.json")|ConvertFrom-Json
 if (-not $manifest.qualifiedComplete4KCandidate) { throw 'Dependent tile not selected' }
 foreach ($key in @('core','extended','preview')) {
  $o=$manifest.outputs.$key
  if ((Get-FileHash -LiteralPath $o.file -Algorithm SHA256).Hash.ToLower() -ne $o.sha256) { throw 'Final output mismatch' }
  $finals+=@{file=$o.file;sha256=$o.sha256}
 }
}
function HasTargetReference($value) {
 if ($value -is [string]) { foreach($r in $records) { if ($value.Replace('/','\').Equals($r.file,[StringComparison]::OrdinalIgnoreCase)) {return $true} }; return $false }
 if ($value -is [Collections.IDictionary]) { foreach($v in $value.Values) {if(HasTargetReference $v){return $true}} }
 elseif ($value -is [Collections.IEnumerable]) {foreach($v in $value){if(HasTargetReference $v){return $true}}}
 elseif ($null -ne $value -and $value -is [pscustomobject]) {foreach($v in $value.PSObject.Properties.Value){if(HasTargetReference $v){return $true}}}
 return $false
}
$checked=@()
foreach($dir in Get-ChildItem -LiteralPath $taskRoot -Directory) {
 if ($dir.Name -notmatch '^r\d\d_c\d\d$') {continue}
 $selected=Join-Path $dir.FullName 'selected\delivery.manifest.json'
 if ((Test-Path -LiteralPath $selected) -and (Get-Content -LiteralPath $selected -Raw|ConvertFrom-Json).qualifiedComplete4KCandidate) {continue}
 $inputs=@(Get-ChildItem -Path (Join-Path $dir.FullName 'regional\context.json'),(Join-Path $dir.FullName 'jobs\*.json') -ErrorAction SilentlyContinue|Where-Object {$_.Name -notmatch 'receipt|attempt|generation'})
 foreach($f in $inputs) {if(HasTargetReference (Get-Content -LiteralPath $f.FullName -Raw|ConvertFrom-Json)){throw 'Active consumer still references retired source'};$checked+=@{file=$f.FullName;sha256=(Get-FileHash -LiteralPath $f.FullName).Hash.ToLower()}}
}
foreach($r in $records) {
 $p=(Resolve-Path -LiteralPath $r.file).Path
 if (-not $p.StartsWith($tileResolved+'\',[StringComparison]::OrdinalIgnoreCase)) {throw 'Out of scope'}
 $entry=Get-Item -LiteralPath $p
 while($null -ne $entry) {if(($entry.Attributes -band [IO.FileAttributes]::ReparsePoint)-ne0){throw 'Reparse path'};$entry=if($entry.PSIsContainer){$entry.Parent}else{$entry.Directory}}
 if((Get-FileHash -LiteralPath $p).Hash.ToLower()-ne$r.sha256){throw 'Historical source hash mismatch'}
 $r.bytes=(Get-Item -LiteralPath $p).Length
}
$kept=@(Get-ChildItem -LiteralPath $tileResolved -Recurse -File|Where-Object {$records.file -notcontains $_.FullName}|ForEach-Object {@{file=$_.FullName;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLower()}})
$audit=[ordered]@{schemaVersion=1;createdAtUtc=[DateTime]::UtcNow.ToString('o');state='planned';reason='South consumer r09_c10 is selected and cleared. Subsequent r09_c09 and active r09_c08 use selected references only. User retention authorizes retiring superseded source PNG while keeping technical data and text provenance.';resolvedAllowedRoot=$tileResolved;deletedFiles=$records;verifiedSelectedOutputs=$finals;checkedCurrentInputs=$checked;preservedFiles=$kept;recursiveDelete=$false;outsideTileDelete=$false}
$audit|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $dest -Encoding utf8
foreach($r in $records){$p=(Resolve-Path -LiteralPath $r.file).Path;if(-not$p.StartsWith($tileResolved+'\',[StringComparison]::OrdinalIgnoreCase) -or (Get-FileHash -LiteralPath $p).Hash.ToLower()-ne$r.sha256){throw 'Target changed'};Remove-Item -LiteralPath $p -Force}
foreach($r in $kept+$finals){if((Get-FileHash -LiteralPath $r.file).Hash.ToLower()-ne$r.sha256){throw 'Preserved file changed'}}
$audit.state='completed';$audit['completedAtUtc']=[DateTime]::UtcNow.ToString('o');$audit['allPreservedHashesVerified']=$true
$audit|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $dest -Encoding utf8
@{state=$audit.state;deletedCount=2;deletedBytes=($records.bytes|Measure-Object -Sum).Sum;manifest=$dest}|ConvertTo-Json
