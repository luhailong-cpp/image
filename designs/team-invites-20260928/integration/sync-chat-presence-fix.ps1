[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$clientRoot = 'E:/work/mmorpg-client'
$stagingRoot = Join-Path $PSScriptRoot 'client'
$files = @(
    @{ path = 'Assets/Scripts/Game/Team/TeamInvitationDirectory.cs'; previous = '675104ED0F8C778CC948BABB376486450AE94330D45A477FBF6A0AAF2507A538' },
    @{ path = 'Assets/Tests/EditMode/Tianyong/TeamInvitationDirectoryTests.cs'; previous = 'D40F716AE01880DFA03BC52323277D3FB01C199F6F719500F059DAF468C489A2' }
)
$writes = @()
foreach ($file in $files) {
    $source = Join-Path $stagingRoot $file.path
    $destination = Join-Path $clientRoot $file.path
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    $currentHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if ($currentHash -ne $file.previous -and $currentHash -ne $sourceHash) {
        throw ('目标文件已被其他任务修改，停止同步: ' + $file.path)
    }
    $writes += [pscustomobject]@{ path=$file.path; source=$source; destination=$destination; sha256=$sourceHash }
}
foreach ($write in $writes) {
    Copy-Item -LiteralPath $write.source -Destination $write.destination -Force
    if ((Get-FileHash -LiteralPath $write.destination -Algorithm SHA256).Hash -ne $write.sha256) {
        throw ('同步后哈希不一致: ' + $write.path)
    }
}
$writes | Select-Object path,sha256 | ConvertTo-Json |
    Set-Content -LiteralPath (Join-Path $PSScriptRoot 'verification-data/chat-presence-synced-20260929.json') -Encoding utf8
Write-Output '仅同步邀请目录与对应测试，两文件哈希校验通过。'
