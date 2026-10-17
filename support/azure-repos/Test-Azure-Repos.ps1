#requires -Version 7.0
$ErrorActionPreference = 'Stop'
$tool = Join-Path $PSScriptRoot 'Azure-Repos.ps1'
$tokens = $null
$parseErrors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile($tool, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
$fixtureRoot = Join-Path ([IO.Path]::GetTempPath()) ('azure-repos-guards-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $fixtureRoot | Out-Null
$repo = Join-Path $fixtureRoot 'source'
$emptyTemplate = Join-Path $fixtureRoot 'empty-template'
New-Item -ItemType Directory -Path $emptyTemplate | Out-Null
$url = 'https://luyuacpp.visualstudio.com/azure-repos-probe/_git/azure-repos-probe'
function Fixture-Git([string[]]$Arguments) {
    & git @Arguments | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Fixture Git command failed.' }
}
Fixture-Git @('init', '--initial-branch=main', "--template=$emptyTemplate", $repo)
Fixture-Git @('-C', $repo, 'config', '--local', 'user.name', 'Offline Guard Test')
Fixture-Git @('-C', $repo, 'config', '--local', 'user.email', 'offline-guard@example.invalid')
Fixture-Git @('-C', $repo, 'config', '--local', 'commit.gpgSign', 'false')
[IO.File]::WriteAllText((Join-Path $repo 'README.txt'), 'Offline-only test fixture.')
Fixture-Git @('-C', $repo, 'add', '--', 'README.txt')
Fixture-Git @('-C', $repo, 'commit', '-m', '离线保护条件测试')
Fixture-Git @('-C', $repo, 'remote', 'add', 'origin', $url)
$results = [Collections.Generic.List[object]]::new()
function Check([string]$Name, [hashtable]$Parameters, [string]$ExpectedError = '') {
    $errorText = ''
    try { & $tool @Parameters -CheckOnly | Out-Null } catch { $errorText = $_.Exception.Message }
    $passed = if ($ExpectedError) { $errorText -like "*$ExpectedError*" } else { -not $errorText }
    $results.Add([pscustomobject]@{ Name = $Name; Passed = $passed; Observed = $errorText })
    if (-not $passed) { throw "Failed: $Name; $errorText" }
}
$newPath = Join-Path $fixtureRoot 'new-clone'
Check 'Clone 参数检查不创建目录' @{Action='Clone'; RemoteUrl=$url; TargetPath=$newPath}
if (Test-Path -LiteralPath $newPath) { throw 'CheckOnly created a directory.' }
Check '空测试目标参数可通过' @{Action='Probe'; RemoteUrl=$url; TargetPath=(Join-Path $fixtureRoot 'new-probe')}
Check '干净独立仓可检查 Pull' @{Action='Pull'; RemoteUrl=$url; TargetPath=$repo}
Check '干净独立仓可检查 Push' @{Action='Push'; RemoteUrl=$url; TargetPath=$repo}
Check '拒绝含凭据 URL' @{Action='Clone'; RemoteUrl='https://user:secret@dev.azure.com/org/project/_git/repo'; TargetPath=$newPath} '不含用户名'
Check '拒绝非 HTTPS' @{Action='Clone'; RemoteUrl='http://dev.azure.com/org/project/_git/repo'; TargetPath=$newPath} 'HTTPS'
Check '拒绝其他托管域' @{Action='Clone'; RemoteUrl='https://github.com/org/repo'; TargetPath=$newPath} 'Azure Repos'
Check '拒绝组织首页 URL' @{Action='Clone'; RemoteUrl='https://luyuacpp.visualstudio.com/'; TargetPath=$newPath} '具体 Git 仓库'
Check '拒绝相对路径' @{Action='Clone'; RemoteUrl=$url; TargetPath='relative-folder'} '绝对路径'
Check '拒绝磁盘根目录' @{Action='Clone'; RemoteUrl=$url; TargetPath=[IO.Path]::GetPathRoot($fixtureRoot)} '根目录'
Check '拒绝 Clone 覆盖已有目录' @{Action='Clone'; RemoteUrl=$url; TargetPath=$repo} '尚不存在'
Check '拒绝分支不一致' @{Action='Pull'; RemoteUrl=$url; TargetPath=$repo; Branch='other'} '当前分支'
Check '拒绝 origin 不一致' @{Action='Push'; RemoteUrl='https://dev.azure.com/org/project/_git/other'; TargetPath=$repo} 'origin'
[IO.File]::WriteAllText((Join-Path $repo 'untracked.txt'), 'Generated dirty guard data.')
Check '拒绝未跟踪文件' @{Action='Push'; RemoteUrl=$url; TargetPath=$repo} '未提交或未跟踪'
# 只移动自身生成的单个测试文件，保留现场证据。
Move-Item -LiteralPath (Join-Path $repo 'untracked.txt') -Destination (Join-Path $fixtureRoot 'untracked-evidence.txt')
[IO.File]::AppendAllText((Join-Path $repo 'README.txt'), 'Changed fixture.')
Check '拒绝已跟踪脏文件' @{Action='Pull'; RemoteUrl=$url; TargetPath=$repo} '未提交或未跟踪'
[IO.File]::WriteAllText((Join-Path $repo 'README.txt'), 'Offline-only test fixture.')
Fixture-Git @('-C', $repo, 'config', '--local', 'lfs.url', 'https://example.invalid/lfs')
Check '拒绝其他 LFS 地址' @{Action='Push'; RemoteUrl=$url; TargetPath=$repo} '自定义 LFS'
Fixture-Git @('-C', $repo, 'config', '--local', '--unset', 'lfs.url')
[IO.File]::WriteAllText((Join-Path $repo '.git/MERGE_HEAD'), '0000000000000000000000000000000000000000')
Check '拒绝未完成合并' @{Action='Pull'; RemoteUrl=$url; TargetPath=$repo} '未完成'
# 调用正式脚本的环境设置函数，再启动真正的子进程检查继承环境；不发起 Git 认证。
$environmentFunction = $ast.Find({ param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Enter-SessionEnvironment' }, $true)
if (-not $environmentFunction) { throw '未找到正式环境设置函数。' }
. ([scriptblock]::Create($environmentFunction.Extent.Text))
$traceNames = @('GIT_TRACE', 'GIT_TRACE_CURL', 'GIT_CURL_VERBOSE')
$originalTraceEnvironment = @{}
$previousSessionEnvironment = $null
try {
    foreach ($name in $traceNames) {
        $originalTraceEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
        [Environment]::SetEnvironmentVariable($name, '', 'Process')
    }
    $previousSessionEnvironment = Enter-SessionEnvironment 'devicecode'
    $childCheck = @'
$variables = [Environment]::GetEnvironmentVariables('Process')
$remaining = @('GIT_TRACE', 'GIT_TRACE_CURL', 'GIT_CURL_VERBOSE') | Where-Object { $variables.Contains($_) }
if ($remaining.Count -gt 0) { Write-Output ('Unexpected trace variables: ' + ($remaining -join ',')); exit 1 }
if ($env:GCM_GUI_PROMPT -ne 'false' -or $env:GCM_TRACE -ne '0' -or $env:GCM_TRACE_SECRETS -ne '0') { exit 2 }
Write-Output 'CHILD_TRACE_VARIABLES_ABSENT'
'@
    $childOutput = & (Join-Path $PSHOME 'pwsh.exe') -NoProfile -Command $childCheck
    if ($LASTEXITCODE -ne 0 -or $childOutput -ne 'CHILD_TRACE_VARIABLES_ABSENT') { throw '子进程环境验证失败。' }
    $results.Add([pscustomobject]@{Name='真实子进程不含空值 Git trace 环境变量';Passed=$true;Observed=$childOutput})
} finally {
    if ($previousSessionEnvironment) {
        foreach ($name in $previousSessionEnvironment.Keys) {
            if ($null -eq $previousSessionEnvironment[$name]) { [Environment]::SetEnvironmentVariable($name, [NullString]::Value, 'Process') }
            else { [Environment]::SetEnvironmentVariable($name, $previousSessionEnvironment[$name], 'Process') }
        }
    }
    foreach ($name in $originalTraceEnvironment.Keys) {
        if ($null -eq $originalTraceEnvironment[$name]) { [Environment]::SetEnvironmentVariable($name, [NullString]::Value, 'Process') }
        else { [Environment]::SetEnvironmentVariable($name, $originalTraceEnvironment[$name], 'Process') }
    }
}
$attributesFunction = $ast.Find({ param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Set-ProbeTextAttributes' }, $true)
if (-not $attributesFunction) { throw '未找到正式 Probe 文本属性函数。' }
. ([scriptblock]::Create($attributesFunction.Extent.Text))
$eolSource = Join-Path $fixtureRoot 'eol-source'
$eolDownload = Join-Path $fixtureRoot 'eol-download'
Fixture-Git @('init', '--initial-branch=main', "--template=$emptyTemplate", $eolSource)
Fixture-Git @('-C', $eolSource, 'config', '--local', 'user.name', 'Offline EOL Test')
Fixture-Git @('-C', $eolSource, 'config', '--local', 'user.email', 'offline-eol@example.invalid')
Fixture-Git @('-C', $eolSource, 'config', '--local', 'commit.gpgSign', 'false')
Fixture-Git @('-C', $eolSource, 'config', '--local', 'core.autocrlf', 'false')
[IO.File]::WriteAllText((Join-Path $eolSource '.gitattributes'), "*.bin filter=lfs diff=lfs merge=lfs -text`n", [Text.UTF8Encoding]::new($false))
Set-ProbeTextAttributes $eolSource
foreach ($name in @('README.txt', 'unfixed.txt')) {
    [IO.File]::WriteAllText((Join-Path $eolSource $name), "Offline LF checkout regression.`nSecond line.`n", [Text.UTF8Encoding]::new($false))
}
Fixture-Git @('-C', $eolSource, 'add', '--', '.gitattributes', 'README.txt', 'unfixed.txt')
Fixture-Git @('-C', $eolSource, 'commit', '-m', '验证 Probe 的 LF 检出属性')
# 本地独立克隆不联网；只在测试下载仓启用 Windows 换行转换，不改正式脚本的 Clone/Pull 配置。
Fixture-Git @('clone', '--no-checkout', '--no-hardlinks', "--template=$emptyTemplate", '--', $eolSource, $eolDownload)
Fixture-Git @('-C', $eolDownload, 'config', '--local', 'core.autocrlf', 'true')
Fixture-Git @('-C', $eolDownload, 'checkout', 'main')
foreach ($name in @('README.txt', '.gitattributes')) {
    $expected = (Get-FileHash -LiteralPath (Join-Path $eolSource $name) -Algorithm SHA256).Hash
    $actual = (Get-FileHash -LiteralPath (Join-Path $eolDownload $name) -Algorithm SHA256).Hash
    if ($actual -ne $expected -or [IO.File]::ReadAllText((Join-Path $eolDownload $name)).Contains("`r")) { throw "$name 未保持 LF 与相同 SHA256。" }
}
if (-not [IO.File]::ReadAllText((Join-Path $eolDownload 'unfixed.txt')).Contains("`r`n")) { throw '未配置属性的对照文件没有转换为 CRLF，回归条件不成立。' }
$binaryAttribute = & git -C $eolDownload check-attr filter -- synthetic-16mib.bin
if ($LASTEXITCODE -ne 0 -or $binaryAttribute -ne 'synthetic-16mib.bin: filter: lfs') { throw '原有二进制 LFS 属性未保留。' }
$results.Add([pscustomobject]@{Name='core.autocrlf=true 检出仍保持 Probe 文本 LF 和相同 SHA256';Passed=$true;Observed='README.txt/.gitattributes SHA256 相同；无属性对照为 CRLF；*.bin 仍使用 LFS'})
$report = [ordered]@{ Status='OFFLINE_GUARDS_PASS'; CapturedUtc=[DateTime]::UtcNow.ToString('o'); ScriptSha256=(Get-FileHash -LiteralPath $tool -Algorithm SHA256).Hash; ParserErrors=0; Cases=@($results); FixtureRoot=$fixtureRoot; RemoteNetworkUsed=$false; RemoteUploadDownloadVerified=$false }
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'verification-offline.json') -Encoding utf8
[pscustomobject]@{Passed=$results.Count;Failed=0;NetworkUsed=$false;FixtureRoot=$fixtureRoot} | ConvertTo-Json
