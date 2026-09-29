param([switch]$Execute, [switch]$ValidateOnly)
# Default is read-only validation. Root executes explicitly with -Execute after acceptance.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($Execute -and $ValidateOnly) { throw 'Use either -Execute or -ValidateOnly, not both.' }
$taskRecovery = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskRepo = [IO.Path]::GetFullPath((Join-Path $taskRecovery '..\..'))
$taskGen = Join-Path $taskRecovery '10-generation'
$taskWork = Join-Path $taskRecovery '10-work'
$taskReferences = Join-Path $taskWork 'references'
$taskRevisions = Join-Path $taskRecovery '10-delivery-preview\revisions'
$taskCurrent = Join-Path $taskRecovery '10-delivery-preview\current'
$taskHost = 'C:\Users\Administrator\.codex\generated_images'
$taskIdentity = Join-Path $taskRepo 'q_daoist_character_pack_4096\10_crimson_spear_girl_transparent_4096.png'
$taskPlanPath = Join-Path $taskWork 'cleanup-20260928\plan.json'
$taskResultPath = Join-Path $taskWork 'cleanup-20260928\result.json'
$taskPlan = Get-Content -LiteralPath $taskPlanPath -Raw -Encoding UTF8 | ConvertFrom-Json
$taskPlanSHA = (Get-FileHash -LiteralPath $taskPlanPath -Algorithm SHA256).Hash.ToLowerInvariant()
$taskDirections = @('N','NE','E','SE','S','SW','W','NW')
$taskImageExtensions = @('.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff')

function Test-TaskWithin([string]$Path, [string]$Root) {
    return $Path.StartsWith($Root.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)
}
function Assert-TaskRegularPath([string]$Path) {
    if (-not [IO.Path]::IsPathRooted($Path) -or $Path -ne [IO.Path]::GetFullPath($Path)) { throw "Not canonical absolute path: $Path" }
    $taskResolved = (Resolve-Path -LiteralPath $Path).ProviderPath
    if ($taskResolved -ne $Path) { throw "Resolved path differs: $Path" }
    $taskInfo = Get-Item -LiteralPath $Path
    if ($taskInfo.PSIsContainer) { throw "Expected file: $Path" }
    # Reject links/junctions in every ancestor; lexical scope alone is insufficient.
    $taskNode = $taskInfo
    while ($null -ne $taskNode) {
        if ($taskNode.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point in path: $Path" }
        if ($taskNode -is [IO.DirectoryInfo]) { $taskNode = $taskNode.Parent } else { $taskNode = $taskNode.Directory }
    }
}
function Assert-TaskFile($Entry) {
    Assert-TaskRegularPath ([string]$Entry.path)
    if ($Entry.sha256 -notmatch '^[a-f0-9]{64}$') { throw "Invalid SHA: $($Entry.path)" }
    $taskInfo = Get-Item -LiteralPath $Entry.path
    if ($taskInfo.Length -ne $Entry.bytes) { throw "Size changed: $($Entry.path)" }
    if ((Get-FileHash -LiteralPath $Entry.path -Algorithm SHA256).Hash -ne $Entry.sha256) { throw "SHA changed: $($Entry.path)" }
}
function Assert-TaskEvidence($Entry) {
    $taskEvidence = $Entry.evidence
    $taskReceiptPath = [IO.Path]::GetFullPath($taskEvidence.receiptPath)
    $taskAttempt = [IO.Path]::GetDirectoryName($taskReceiptPath)
    if ([IO.Path]::GetDirectoryName($taskAttempt) -ne $taskGen -or [IO.Path]::GetFileName($taskReceiptPath) -ne 'generation-receipt.json') { throw 'Receipt outside character 10.' }
    $taskToolPath = Join-Path $taskAttempt 'tool-result.json'
    if ($taskEvidence.toolResultPath -ne $taskToolPath) { throw 'Unexpected tool-result location.' }
    Assert-TaskRegularPath $taskReceiptPath
    Assert-TaskRegularPath $taskToolPath
    if ((Get-FileHash -LiteralPath $taskReceiptPath -Algorithm SHA256).Hash -ne $taskEvidence.receiptSHA256) { throw "Receipt changed: $taskReceiptPath" }
    if ((Get-FileHash -LiteralPath $taskToolPath -Algorithm SHA256).Hash -ne $taskEvidence.toolResultSHA256) { throw "Tool result changed: $taskToolPath" }
    $taskReceipt = Get-Content -LiteralPath $taskReceiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $taskToolResult = Get-Content -LiteralPath $taskToolPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($taskReceipt.character -ne '10_crimson_spear_girl' -or $taskReceipt.rawSHA256 -ne $Entry.sha256 -or $taskEvidence.rawSHA256 -ne $Entry.sha256) { throw 'Character or raw SHA binding failed.' }
    if ($taskReceipt.toolResultSHA256 -ne $taskEvidence.toolResultSHA256 -or [IO.Path]::GetFullPath((Join-Path $taskRepo $taskReceipt.toolResultFile)) -ne $taskToolPath) { throw 'Receipt/tool binding failed.' }
    if ($taskReceipt.original_generated_file -ne $taskEvidence.originalGeneratedFile -or -not ([string]$taskToolResult.output_hint).Contains([string]$taskEvidence.originalGeneratedFile)) { throw 'Host path not present in exact recorded tool result.' }
    if ($Entry.kind -eq 'host-generated-original') {
        if ($Entry.path -ne $taskReceipt.original_generated_file) { throw 'Host target differs from receipt.' }
    } elseif ($Entry.path -ne (Join-Path $taskAttempt 'raw.png')) { throw 'Raw target differs from receipt directory.' }
}
function Assert-TaskTarget($Entry) {
    $taskFull = [IO.Path]::GetFullPath($Entry.path)
    if ($taskFull -ne $Entry.path -or (Test-TaskWithin $taskFull $taskCurrent) -or (Test-TaskWithin $taskFull $taskReferences) -or $taskFull -eq $taskIdentity) { throw "Protected or noncanonical target: $taskFull" }
    if ([IO.Path]::GetExtension($taskFull).ToLowerInvariant() -notin $taskImageExtensions) { throw "Non-image target: $taskFull" }
    $taskParent = [IO.Path]::GetDirectoryName($taskFull)
    switch ($Entry.kind) {
        'generation-raw' {
            if ([IO.Path]::GetDirectoryName($taskParent) -ne $taskGen -or [IO.Path]::GetFileName($taskFull) -ne 'raw.png') { throw "Outside raw scope: $taskFull" }
            Assert-TaskEvidence $Entry
        }
        'host-generated-original' {
            if ([IO.Path]::GetDirectoryName($taskParent) -ne $taskHost -or [IO.Path]::GetFileName($taskParent) -notmatch '^[0-9a-f-]{36}$' -or [IO.Path]::GetFileName($taskFull) -notmatch '^exec-[0-9a-f-]+\.png$') { throw "Outside exact host scope: $taskFull" }
            Assert-TaskEvidence $Entry
        }
        'work-intermediate-image' {
            if (-not (Test-TaskWithin $taskFull $taskWork) -or (Test-TaskWithin $taskFull $taskReferences) -or [IO.Path]::GetFullPath((Join-Path $taskWork $Entry.relativePath)) -ne $taskFull) { throw "Outside work image scope: $taskFull" }
        }
        'superseded-preview-image' {
            if (-not (Test-TaskWithin $taskFull $taskRevisions) -or [IO.Path]::GetFullPath((Join-Path $taskRevisions $Entry.relativePath)) -ne $taskFull) { throw "Outside revision image scope: $taskFull" }
        }
        default { throw "Unknown deletion kind: $($Entry.kind)" }
    }
    Assert-TaskFile $Entry
}
function Get-TaskU32([byte[]]$Data, [int]$Offset) {
    return ([long]$Data[$Offset] * 16777216 + [long]$Data[$Offset+1] * 65536 + [long]$Data[$Offset+2] * 256 + [long]$Data[$Offset+3])
}
function Assert-TaskAPNG([string]$Path) {
    $taskData = [IO.File]::ReadAllBytes($Path)
    if ($taskData.Length -lt 33 -or [Convert]::ToBase64String($taskData[0..7]) -ne 'iVBORw0KGgo=') { throw "Not PNG: $Path" }
    $taskOffset = 8; $taskFrameCount = 0; $taskCycleMs = 0; $taskAnimation = $false; $taskEnd = $false; $taskHeader = $false
    while ($taskOffset + 12 -le $taskData.Length) {
        $taskLength = Get-TaskU32 $taskData $taskOffset
        if ($taskLength -gt $taskData.Length - $taskOffset - 12) { throw "Invalid PNG chunk: $Path" }
        $taskType = [Text.Encoding]::ASCII.GetString($taskData, $taskOffset+4, 4)
        $taskBody = $taskOffset + 8
        switch ($taskType) {
            'IHDR' {
                if ($taskHeader -or $taskLength -ne 13 -or (Get-TaskU32 $taskData $taskBody) -ne 1024 -or (Get-TaskU32 $taskData ($taskBody+4)) -ne 1024) { throw "Invalid loop dimensions: $Path" }
                $taskHeader = $true
            }
            'acTL' {
                if ($taskAnimation -or $taskLength -ne 8 -or (Get-TaskU32 $taskData $taskBody) -ne 16 -or (Get-TaskU32 $taskData ($taskBody+4)) -ne 0) { throw "Expected endless 16-frame APNG: $Path" }
                $taskAnimation = $true
            }
            'fcTL' {
                if ($taskLength -ne 26) { throw "Invalid frame control: $Path" }
                $taskNumerator = [int]$taskData[$taskBody+20] * 256 + [int]$taskData[$taskBody+21]
                $taskDenominator = [int]$taskData[$taskBody+22] * 256 + [int]$taskData[$taskBody+23]
                if ($taskDenominator -eq 0) { $taskDenominator = 100 }
                $taskDuration = 1000.0 * $taskNumerator / $taskDenominator
                if ($taskDuration -ne 30) { throw "Frame duration is not 30 ms: $Path" }
                $taskFrameCount++; $taskCycleMs += $taskDuration
            }
            'IEND' { $taskEnd = $true }
        }
        $taskOffset += [int]$taskLength + 12
        if ($taskEnd) { break }
    }
    if (-not $taskHeader -or -not $taskAnimation -or -not $taskEnd -or $taskOffset -ne $taskData.Length -or $taskFrameCount -ne 16 -or $taskCycleMs -ne 480) { throw "APNG structure/timing mismatch: $Path" }
}
function Assert-TaskDelivery {
    foreach ($taskKeep in $taskPlan.protectedFiles) {
        if (-not (Test-TaskWithin $taskKeep.path $taskCurrent) -and -not (Test-TaskWithin $taskKeep.path $taskReferences) -and $taskKeep.path -ne $taskIdentity) { throw 'Invalid protected-file scope.' }
        Assert-TaskFile $taskKeep
    }
    $taskManifest = Get-Content -LiteralPath (Join-Path $taskCurrent 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $taskAcceptance = Get-Content -LiteralPath (Join-Path $taskCurrent 'visual-acceptance.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $taskValidation = Get-Content -LiteralPath (Join-Path $taskCurrent 'validation.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $taskLoopManifest = Get-Content -LiteralPath (Join-Path $taskCurrent 'loops\manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($taskAcceptance.status -ne 'accepted' -or $taskAcceptance.character -ne '10_crimson_spear_girl' -or $taskAcceptance.walkCount -ne 128 -or $taskAcceptance.idleCount -ne 8 -or @($taskAcceptance.files).Count -ne 136 -or @($taskAcceptance.blockingSlots).Count -ne 0 -or @($taskAcceptance.missingSlots).Count -ne 0) { throw 'Formal visual acceptance must be accepted for all 136 frames.' }
    if ($taskManifest.character -ne '10_crimson_spear_girl' -or $taskManifest.visualReview -ne 'accepted_offline' -or $taskManifest.walkCount -ne 128 -or $taskManifest.idleCount -ne 8 -or @($taskManifest.missing).Count -ne 0 -or $taskManifest.frameDurationMs -ne 30 -or $taskManifest.loopDurationMs -ne 480) { throw 'Final manifest is not complete and accepted.' }
    if ($taskValidation.character -ne '10_crimson_spear_girl' -or $taskValidation.walkCount -ne 128 -or $taskValidation.idleCount -ne 8 -or $taskValidation.uniqueRawSources -ne 136 -or $taskValidation.uniqueOutputPixels -ne 136) { throw 'Validation frame/source counts failed.' }
    foreach ($taskCheck in @('png1024Transparent','nativeAtLeast1024','eightLoops16Frames30ms480ms','loopPixelsExactlySource','sourceRequestReceiptPromptHashBound')) {
        if ($taskValidation.$taskCheck -ne $true) { throw "Validation failed: $taskCheck" }
    }
    if ((Get-FileHash -LiteralPath (Join-Path $taskCurrent 'manifest.json') -Algorithm SHA256).Hash -ne $taskValidation.manifestSHA256) { throw 'Validation belongs to a different manifest.' }
    if (@(Get-ChildItem -LiteralPath (Join-Path $taskCurrent 'walk') -Recurse -File -Filter '*.png').Count -ne 128 -or @(Get-ChildItem -LiteralPath (Join-Path $taskCurrent 'idle') -File -Filter '*.png').Count -ne 8 -or @(Get-ChildItem -LiteralPath (Join-Path $taskCurrent 'loops') -File -Filter '*.png').Count -ne 8) { throw 'Unexpected final PNG file counts.' }
    if (@($taskPlan.finalFrames).Count -ne 136 -or @($taskPlan.finalLoops).Count -ne 8 -or @($taskManifest.frames.PSObject.Properties).Count -ne 136) { throw 'Plan/manifest counts mismatch.' }
    $taskExpected = @{}; $taskAccepted = @{}
    foreach ($taskDirection in $taskDirections) {
        foreach ($taskNumber in 1..16) { $taskExpected[('{0}{1:00}' -f $taskDirection,$taskNumber)] = ('walk/{0}/{1:00}.png' -f $taskDirection,$taskNumber) }
        $taskExpected[$taskDirection + 'idle'] = 'idle/' + $taskDirection + '.png'
    }
    foreach ($taskItem in $taskAcceptance.files) {
        if ($taskAccepted.ContainsKey($taskItem.slot)) { throw 'Duplicate acceptance slot.' }
        $taskAccepted[$taskItem.slot] = $taskItem
    }
    $taskSeenFrames = @{}
    foreach ($taskFrame in $taskPlan.finalFrames) {
        $taskSlot = [string]$taskFrame.slot
        if (-not $taskExpected.ContainsKey($taskSlot) -or $taskSeenFrames.ContainsKey($taskSlot) -or $taskFrame.file.Replace('\','/') -ne $taskExpected[$taskSlot] -or $taskFrame.path -ne [IO.Path]::GetFullPath((Join-Path $taskCurrent $taskExpected[$taskSlot]))) { throw "Unexpected frame slot/path: $taskSlot" }
        $taskSeenFrames[$taskSlot] = $true
        Assert-TaskFile $taskFrame
        $taskM = $taskManifest.frames.$taskSlot; $taskA = $taskAccepted[$taskSlot]
        if ($null -eq $taskA -or $taskM.finalVisualReview -ne 'accepted' -or $taskM.sha256 -ne $taskFrame.sha256 -or $taskA.sha256 -ne $taskFrame.sha256 -or $taskM.file.Replace('\','/') -ne $taskFrame.file -or $taskA.file.Replace('\','/') -ne $taskFrame.file) { throw "Unaccepted or changed frame: $taskSlot" }
    }
    $taskSeenLoops = @{}
    foreach ($taskLoop in $taskPlan.finalLoops) {
        $taskDirection = [string]$taskLoop.direction
        if ($taskDirection -notin $taskDirections -or $taskSeenLoops.ContainsKey($taskDirection) -or $taskLoop.path -ne (Join-Path $taskCurrent ('loops\' + $taskDirection + '.png'))) { throw 'Unexpected loop path/direction.' }
        $taskSeenLoops[$taskDirection] = $true
        Assert-TaskFile $taskLoop
        Assert-TaskAPNG $taskLoop.path
        $taskL = $taskLoopManifest.$taskDirection
        if ($taskL.sha256 -ne $taskLoop.sha256 -or $taskL.file.Replace('\','/') -ne ('loops/' + $taskDirection + '.png') -or $taskL.frames -ne 16 -or $taskL.cycleMs -ne 480 -or $taskL.decodedFramesExactlyMatchSource -ne $true -or @($taskL.durationsMs).Count -ne 16 -or @($taskL.sourceFrames).Count -ne 16) { throw "Loop binding mismatch: $taskDirection" }
        foreach ($taskDuration in $taskL.durationsMs) { if ($taskDuration -ne 30) { throw 'Loop duration record changed.' } }
        foreach ($taskIndex in 0..15) {
            $taskSlot = '{0}{1:00}' -f $taskDirection,($taskIndex+1)
            if ($taskL.sourceFrames[$taskIndex].slot -ne $taskSlot -or $taskL.sourceFrames[$taskIndex].sha256 -ne $taskManifest.frames.$taskSlot.sha256) { throw 'Loop source sequence mismatch.' }
        }
    }
}

if ($taskPlan.schemaVersion -ne 1 -or $taskPlan.character -ne '10_crimson_spear_girl' -or $taskPlan.roots.recovery -ne $taskRecovery -or $taskPlan.roots.repository -ne $taskRepo -or $taskPlan.roots.hostGeneratedImages -ne $taskHost) { throw 'Unexpected cleanup plan/root.' }
if ($Execute -and (Test-Path -LiteralPath $taskResultPath)) { throw "Cleanup result already exists; review it before any further execution: $taskResultPath" }
Assert-TaskDelivery
$taskUnique = @{}
foreach ($taskEntry in $taskPlan.targets) {
    if ($taskUnique.ContainsKey($taskEntry.path)) { throw 'Duplicate target.' }
    $taskUnique[$taskEntry.path] = $true
    Assert-TaskTarget $taskEntry
}
$taskBytes = ($taskPlan.targets | Measure-Object -Property bytes -Sum).Sum
if (@($taskPlan.targets).Count -ne $taskPlan.summary.totalFiles -or $taskBytes -ne $taskPlan.summary.totalBytes) { throw 'Plan summary disagrees with exact targets.' }
if (-not $Execute) {
    [ordered]@{status='validated-no-deletion'; planSHA256=$taskPlanSHA; targets=@($taskPlan.targets).Count; bytes=$taskBytes; protectedFiles=@($taskPlan.protectedFiles).Count; walk=128; idle=8; loops=8; frameMs=30; visualAcceptance='accepted'; recursiveDeletion=$false} | ConvertTo-Json
    exit 0
}

$taskDeleted = [Collections.Generic.List[object]]::new()
$taskCompleted = $false
$taskFailure = $null
try {
    foreach ($taskEntry in $taskPlan.targets) {
        # Recheck immediately before each exact-file deletion; never enumerate shared host storage.
        Assert-TaskTarget $taskEntry
        Remove-Item -LiteralPath $taskEntry.path
        if (Test-Path -LiteralPath $taskEntry.path) { throw "Deletion not confirmed: $($taskEntry.path)" }
        $taskDeleted.Add($taskEntry)
    }
    Assert-TaskDelivery
    $taskCompleted = $true
} catch {
    $taskFailure = $_.Exception.Message
    throw
} finally {
    [ordered]@{character='10_crimson_spear_girl'; completedAtUtc=[DateTime]::UtcNow.ToString('o'); planSHA256=$taskPlanSHA; status=$(if($taskCompleted){'deleted-and-verified'}else{'partial-stop'}); error=$taskFailure; recursiveDeletion=$false; deletedFiles=$taskDeleted.Count; deletedBytes=($taskDeleted | Measure-Object -Property bytes -Sum).Sum; protectedFiles=@($taskPlan.protectedFiles).Count; targets=$taskDeleted} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $taskResultPath -Encoding UTF8
}
[ordered]@{status='deleted-and-verified'; deletedFiles=$taskDeleted.Count; deletedBytes=($taskDeleted | Measure-Object -Property bytes -Sum).Sum; result=$taskResultPath} | ConvertTo-Json
