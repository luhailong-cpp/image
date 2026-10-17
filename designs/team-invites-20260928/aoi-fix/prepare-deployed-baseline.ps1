$ErrorActionPreference = 'Stop'
$serverRoot = 'E:/work/xuanming-server-mmo'
$revision = '1ad634443d4d5028075d6b7e839b434018bfb0e8'
$snapshot = Join-Path $PSScriptRoot 'baseline-source'
$archive = Join-Path $PSScriptRoot 'baseline-source.tar'
if (-not (Test-Path -LiteralPath $snapshot)) {
    & git -c "safe.directory=$serverRoot" -C $serverRoot archive --format=tar "--output=$archive" $revision cpp game.sln Directory.Build.targets tools/scripts/check_no_raw_pointer_member.ps1 tools/scripts/lib/no_raw_pointer_project.ps1
    if ($LASTEXITCODE -ne 0) { throw 'Git 快照导出失败' }
    New-Item -ItemType Directory -Path $snapshot | Out-Null
    & tar -xf $archive -C $snapshot
    if ($LASTEXITCODE -ne 0) { throw 'Git 快照展开失败' }
}
$aoi = Join-Path $snapshot 'cpp/libs/services/scene/spatial/system/aoi.cpp'
$text = [IO.File]::ReadAllText($aoi)
$actualSource = Join-Path $serverRoot 'cpp/libs/services/scene/spatial/system/aoi.cpp'
if ((Get-FileHash -LiteralPath $actualSource).Hash -ne 'E9C098013C8746D856706F428DFCA3572DE49953EFB928DB4436DFA9FB1BDB41') { throw '正式修复与已验证 SHA 不一致' }
$fixed = [IO.File]::ReadAllText($actualSource)
$lfOriginal = $text.Replace("`r`n", "`n")
$sha = [Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($lfOriginal))
$hash = [Convert]::ToHexString($sha)
if ($hash -ne 'FC147FF827C7D2BB236788B92B5B0C672DEA83493BAB8C5405EEA8A5A065B172') { throw '基线 AOI 与部署 PDB 不一致' }
[IO.File]::WriteAllText($aoi, $fixed, [Text.UTF8Encoding]::new($false))
# 仅共享第三方源码与已安装 SDK；所有自有库和中间目录均从空目录编译。
# 禁止构建后部署；第三方项目本身的相对输出也落在隔离源码的 lib/bin。
New-Item -ItemType Junction -Path (Join-Path $snapshot 'third_party') -Target (Join-Path $serverRoot 'third_party') | Out-Null
New-Item -ItemType Directory -Path (Join-Path $snapshot 'lib'),(Join-Path $snapshot 'bin') | Out-Null
[ordered]@{ revision=$revision; source=$snapshot; projectSourceChecksumsMatched=993; projectSourceChecksumsMismatched=0; aoiSha256=(Get-FileHash -LiteralPath $aoi).Hash; ownLibraries='全部从空目录编译，不复用当前主工作区自有库'; sharedThirdParty=(Join-Path $serverRoot 'third_party') } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'baseline-build-input.json') -Encoding utf8
Write-Output $snapshot
