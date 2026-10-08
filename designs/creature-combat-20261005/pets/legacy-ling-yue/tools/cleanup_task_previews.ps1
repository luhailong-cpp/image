param([switch]$Execute)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$expected='D:\work\image\designs\creature-combat-20261005\pets\legacy-ling-yue'
if (-not $taskRoot.Equals($expected,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected task root' }
$plan=Get-Content -LiteralPath (Join-Path $taskRoot 'cleanup-plan.json') -Raw | ConvertFrom-Json
$report=Get-Content -LiteralPath (Join-Path $taskRoot 'technical-validation.json') -Raw | ConvertFrom-Json
if (-not $report.technicalPassed -or $report.presentCount -ne 68) { throw 'Current technical report is not complete' }
$count=@($plan.runtimeSha256.PSObject.Properties).Count
if ($count -ne 68) { throw 'Cleanup plan does not snapshot 68 runtime files' }
foreach ($property in $plan.runtimeSha256.PSObject.Properties) {
    $path=(Resolve-Path -LiteralPath (Join-Path $taskRoot $property.Name)).Path
    if (-not $path.StartsWith($taskRoot+'\runtime\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Runtime snapshot path escaped runtime' }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw "Runtime changed: $($property.Name)" }
}
$prepared=@()
foreach ($item in $plan.candidates) {
    $path=(Resolve-Path -LiteralPath (Join-Path $taskRoot $item.file)).Path
    if (-not $path.StartsWith($taskRoot+'\receipts\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Candidate escaped task receipts directory' }
    if ([IO.Path]::GetExtension($path).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.webp','.gif')) { throw 'Candidate is not an intermediate image' }
    if ($item.referencedByCurrentGeneration) { throw 'Candidate is a current generation input' }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Candidate changed: $($item.file)" }
    $prepared += [pscustomobject]@{file=$item.file;absolutePath=$path;sha256=$item.sha256;bytes=$item.bytes;historicalMarkdownReferences=$item.historicalMarkdownReferences;removed=$false}
}
if (-not $Execute) { [pscustomobject]@{validated=$prepared.Count;deleted=0;executeRequired=$true} | ConvertTo-Json -Compress; exit 0 }
$record=[pscustomobject]@{startedAt=[DateTimeOffset]::UtcNow.ToString('o');completedAt=$null;status='running';taskRoot=$taskRoot;reason='User AGENTS retention policy; root authorized final task-only historical QA/preview cleanup after source and SHA checks';retained='68 runtime PNGs; current E/W design; necessary qa; all source/prompt/receipt/generation text; shared references and host cache untouched';planSha256=(Get-FileHash -LiteralPath (Join-Path $taskRoot 'cleanup-plan.json') -Algorithm SHA256).Hash.ToLowerInvariant();files=$prepared}
$recordPath=Join-Path $taskRoot 'cleanup-record.json'
$record | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $recordPath -Encoding utf8
foreach ($item in $prepared) {
    Remove-Item -LiteralPath $item.absolutePath -Force
    $item.removed=$true
    $record | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $recordPath -Encoding utf8
}
$record.completedAt=[DateTimeOffset]::UtcNow.ToString('o');$record.status='completed'
$record | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $recordPath -Encoding utf8
[pscustomobject]@{deleted=$prepared.Count;bytes=($prepared | Measure-Object -Property bytes -Sum).Sum;record='cleanup-record.json'} | ConvertTo-Json -Compress
