$ErrorActionPreference = 'Stop'
$c07Root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../next_tile_r08_c07'))
$cleanupDir = Join-Path $c07Root 'continuation-20260923/cleanup-selected-c07'
$planPath = Join-Path $cleanupDir 'plan.json'
$expectedPlan = '6e8688a9a165cfed35902f28620a96ed4e089d5d7d23b95c25c251acc1a04276'
if ((Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedPlan) { throw 'Cleanup plan changed' }
$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if ([IO.Path]::GetFullPath($plan.scopeRoot) -ne $c07Root) { throw 'Unexpected cleanup root' }
if ((Get-FileHash -LiteralPath $plan.selection.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.selection.sha256) { throw 'Selection changed' }
$items = @($plan.items)
foreach ($item in $items) {
    $target = [IO.Path]::GetFullPath($item.file)
    if (-not $target.StartsWith($c07Root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw "Outside scope: $target" }
    $info = Get-Item -LiteralPath $target
    for ($node = $info; $null -ne $node -and $node.FullName.Length -ge $c07Root.Length; $node = $node.Parent) {
        if ($node.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point: $($node.FullName)" }
    }
    if ($info.PSIsContainer -or $info.Length -ne $item.bytes) { throw "Not expected file: $target" }
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Changed: $target" }
}
$receiptPath = Join-Path $cleanupDir 'deleted-files.jsonl'
if (Test-Path -LiteralPath $receiptPath) { throw 'Receipt already exists, do not repeat cleanup blindly' }
$utf8 = New-Object Text.UTF8Encoding($false)
$deletedCount = 0
$deletedBytes = [long]0
foreach ($item in $items | Where-Object action -eq 'delete') {
    $target = [IO.Path]::GetFullPath($item.file)
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Concurrent modification: $target" }
    Remove-Item -LiteralPath $target
    $receipt = [ordered]@{deletedAtUtc=[DateTime]::UtcNow.ToString('o');file=$target;sha256=$item.sha256;bytes=$item.bytes;reason=$item.reason;status='deleted_by_user_not_current_bytes_verifiable'}
    [IO.File]::AppendAllText($receiptPath, (($receipt | ConvertTo-Json -Compress) + [Environment]::NewLine), $utf8)
    $deletedCount++
    $deletedBytes += $item.bytes
}
foreach ($item in $items | Where-Object action -eq 'keep') {
    if ((Get-FileHash -LiteralPath $item.file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Retained file changed: $($item.file)" }
}
$summary = [ordered]@{completedAtUtc=[DateTime]::UtcNow.ToString('o');scopeRoot=$c07Root;planSha256=$expectedPlan;deletedCount=$deletedCount;deletedBytes=$deletedBytes;retainedImageCount=@($items | Where-Object action -eq 'keep').Count;imageBackupCreated=$false;retainedFilesShaVerified=$true;historicalSources='Deleted under user retention policy; original bytes cannot be reverified. Requests, receipts, SHA, assembly and review text remain.';formalAccepted=$false;runtimeVerified=$false}
[IO.File]::WriteAllText((Join-Path $cleanupDir 'receipt.json'), ($summary | ConvertTo-Json -Depth 8), $utf8)
$summary | ConvertTo-Json -Compress
