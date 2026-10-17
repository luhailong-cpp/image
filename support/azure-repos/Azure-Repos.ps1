#requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Probe', 'Clone', 'Pull', 'Push')][string]$Action,
    [Parameter(Mandatory)][string]$RemoteUrl,
    [Parameter(Mandatory)][string]$TargetPath,
    [string]$Branch = 'main',
    [ValidateSet('system', 'devicecode')][string]$AuthFlow = 'system',
    [string]$LfsExecutable,
    [string]$ToolDirectory = (Join-Path $env:LOCALAPPDATA 'AzureReposHelper/tools'),
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Resolve-AzureUrl([string]$Value) {
    $uri = $null
    if (-not [Uri]::TryCreate($Value, [UriKind]::Absolute, [ref]$uri) -or $uri.Scheme -ne 'https' -or
        -not $uri.IsDefaultPort -or $uri.UserInfo -or $uri.Query -or $uri.Fragment) {
        throw '只接受不含用户名、密码、查询参数的 HTTPS Azure Repos URL。'
    }
    if ($uri.Host -eq 'dev.azure.com') { $valid = $uri.AbsolutePath -match '^/[^/]+/[^/]+/_git/[^/]+/?$' }
    elseif ($uri.Host -match '^[a-zA-Z0-9-]+\.visualstudio\.com$') { $valid = $uri.AbsolutePath -match '^/(?:DefaultCollection/)?[^/]+/_git/[^/]+/?$' }
    else { $valid = $false }
    if (-not $valid) { throw 'URL 必须指向 Azure Repos 的具体 Git 仓库，不能填组织或项目首页。' }
    return $uri.AbsoluteUri.TrimEnd('/')
}

function Resolve-SafePath([string]$Value) {
    if (-not [IO.Path]::IsPathFullyQualified($Value) -or $Value.StartsWith('\\')) { throw '目标路径必须是本机磁盘的绝对路径。' }
    $full = [IO.Path]::GetFullPath($Value).TrimEnd('\', '/')
    if ($full -eq [IO.Path]::GetPathRoot($full).TrimEnd('\', '/') -or $full -eq $env:USERPROFILE) { throw '不能将磁盘根目录或用户主目录作为仓库。' }
    foreach ($protected in @($env:WINDIR, $env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if ($protected -and ($full -eq $protected -or $full.StartsWith($protected.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase))) { throw '不能使用系统或程序安装目录。' }
    }
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw '目标路径及其父目录不能是符号链接或目录联接。' }
        }
        $parent = Split-Path -Parent $cursor
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
    # 若工具放在正式仓库里，不允许把该正式仓库当作操作目标。
    $cursor = $PSScriptRoot
    while ($cursor) {
        if ((Test-Path -LiteralPath (Join-Path $cursor '.git')) -and $full -eq $cursor.TrimEnd('\', '/')) { throw '此路径是承载工具的主仓库；请指定独立目标仓库。' }
        $cursor = Split-Path -Parent $cursor
    }
    return $full
}

$gitCommand = Get-Command git -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $gitCommand) { throw '未找到 Git。请先安装官方 Git for Windows，并勾选 Git Credential Manager：https://gitforwindows.org/' }
$script:Git = $gitCommand.Source
foreach ($variable in @('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES')) {
    if ([Environment]::GetEnvironmentVariable($variable, 'Process')) { throw "当前进程设置了 $variable，可能把操作指向其他仓库；请在干净 PowerShell 窗口运行。" }
}
$script:GitOptions = @('-c', 'credential.helper=', '-c', 'credential.helper=manager', '-c', 'credential.useHttpPath=true')
function Invoke-Git([string[]]$Arguments) {
    $result = & $script:Git @script:GitOptions @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Git 命令失败（退出码 $LASTEXITCODE）；保留现场，未执行覆盖或强推。" }
    return $result
}
function Assert-IndependentCleanRepo([string]$Repo) {
    if (-not (Test-Path -LiteralPath (Join-Path $Repo '.git') -PathType Container)) { throw '需要独立的普通 Git 仓库，不接受父仓目录、裸仓或 worktree。' }
    $actual = (Invoke-Git @('-C', $Repo, 'rev-parse', '--show-toplevel')) -join ''
    if ([IO.Path]::GetFullPath($actual) -ne $Repo) { throw '目标与实际 Git 仓根目录不一致。' }
    if ((Invoke-Git @('-C', $Repo, 'status', '--porcelain=v1', '--untracked-files=normal')) -join '') { throw '目标仓有未提交或未跟踪文件。请先自行提交或处理，脚本不会自动 add/commit/stash。' }
    foreach ($state in @('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-apply', 'rebase-merge')) {
        if (Test-Path -LiteralPath (Join-Path $Repo ".git/$state")) { throw '目标仓存在未完成的合并、变基或拣选，请先处理。' }
    }
    $current = (Invoke-Git @('-C', $Repo, 'branch', '--show-current')) -join ''
    if ($current -ne $Branch) { throw '当前分支与 -Branch 不一致，脚本不会自动切换分支。' }
    $origin = @(Invoke-Git @('-C', $Repo, 'remote', 'get-url', '--all', 'origin'))
    if ($origin.Count -ne 1 -or (Resolve-AzureUrl $origin[0]) -cne $script:NormalizedUrl) { throw 'origin 与传入的 RemoteUrl 不一致；不会改写现有远端。' }
    $pushOrigins = @(Invoke-Git @('-C', $Repo, 'remote', 'get-url', '--push', '--all', 'origin'))
    if ($pushOrigins.Count -ne 1 -or (Resolve-AzureUrl $pushOrigins[0]) -cne $script:NormalizedUrl) { throw 'origin 的推送 URL 与 RemoteUrl 不一致。' }
}
function Assert-RepoEndpoint([string]$Repo) {
    if (Test-Path -LiteralPath (Join-Path $Repo '.lfsconfig')) { throw '仓库有独立 .lfsconfig；请先人工核对 LFS 服务地址，工具不会向旧端点传输。' }
    $overrides = & $script:Git -C $Repo config --get-regexp '^(lfs\.(url|pushurl|storage)|remote\..*\.lfs(url|pushurl)|url\..*\.(insteadof|pushinsteadof)|core\.hookspath)$' 2>$null
    $code = $LASTEXITCODE
    if ($code -notin @(0, 1)) { throw '读取目标仓配置失败。' }
    if ($overrides) { throw '目标仓继承了自定义 LFS 地址/存储、URL 重写或 hooks 路径；请先核对，脚本不覆盖这些配置。' }
}
function Ensure-Lfs {
    if ($LfsExecutable) {
        if (-not (Test-Path -LiteralPath $LfsExecutable -PathType Leaf)) { throw '指定的 git-lfs.exe 不存在。' }
        $env:PATH = (Split-Path -Parent ([IO.Path]::GetFullPath($LfsExecutable))) + ';' + $env:PATH
    }
    & $script:Git lfs version 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { return }
    if ($LfsExecutable) { throw '指定 Git LFS 无法运行。' }
    if ([Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne [Runtime.InteropServices.Architecture]::X64) { throw '便携下载仅支持 Windows x64；请安装对应架构的官方 Git LFS。' }
    $cache = Resolve-SafePath $ToolDirectory
    $archive = Join-Path $cache 'git-lfs-windows-amd64-v3.8.0.zip'
    $hash = 'b62e7b8ceddee635f691233d77de8eaa4b213e9209e0173811d8cfa77f7882c1'
    New-Item -ItemType Directory -Path $cache -Force | Out-Null
    if (-not (Test-Path -LiteralPath $archive)) {
        Write-Host '下载官方 Git LFS 3.8.0 便携工具（不安装到系统）。'
        Invoke-WebRequest -Uri 'https://github.com/git-lfs/git-lfs/releases/download/v3.8.0/git-lfs-windows-amd64-v3.8.0.zip' -OutFile $archive -TimeoutSec 300
    }
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hash) { throw 'Git LFS 下载包校验失败；停止，不执行该工具。请移走损坏下载包后重试。' }
    $extract = Join-Path $cache 'git-lfs-3.8.0-portable'
    Expand-Archive -LiteralPath $archive -DestinationPath $extract -Force
    $exe = @(Get-ChildItem -LiteralPath $extract -Filter git-lfs.exe -File -Recurse)
    if ($exe.Count -ne 1) { throw 'Git LFS 下载包的目录结构不符合预期。' }
    $env:PATH = $exe[0].DirectoryName + ';' + $env:PATH
    Invoke-Git @('lfs', 'version') | Out-Host
}
function Configure-Repo([string]$Repo) {
    Assert-RepoEndpoint $Repo
    Invoke-Git @('-C', $Repo, 'lfs', 'install', '--local') | Out-Host
    Invoke-Git @('-C', $Repo, 'config', '--local', '--replace-all', 'credential.helper', '') | Out-Null
    Invoke-Git @('-C', $Repo, 'config', '--local', '--add', 'credential.helper', 'manager') | Out-Null
    Invoke-Git @('-C', $Repo, 'config', '--local', 'credential.useHttpPath', 'true') | Out-Null
    Invoke-Git @('-C', $Repo, 'config', '--local', 'credential.azreposCredentialType', 'oauth') | Out-Null
    Invoke-Git @('-C', $Repo, 'config', '--local', 'credential.credentialStore', 'wincredman') | Out-Null
}
function Clone-Repo([string]$Destination) {
    Invoke-Git @('clone', '--no-checkout', '--no-tags', '--branch', $Branch, "--template=$script:EmptyTemplate", '--', $script:NormalizedUrl, $Destination) | Out-Host
    Configure-Repo $Destination
    Invoke-Git @('-C', $Destination, 'checkout', $Branch) | Out-Host
    Assert-RepoEndpoint $Destination
    Invoke-Git @('-C', $Destination, 'lfs', 'pull', 'origin') | Out-Host
    Invoke-Git @('-C', $Destination, 'lfs', 'fsck') | Out-Host
}
function Set-ProbeTextAttributes([string]$Repo) {
    # 仅约束 Probe 自己生成的文本，保证其他电脑检出时也可逐字节核验。
    $attributes = Join-Path $Repo '.gitattributes'
    $existing = [IO.File]::ReadAllText($attributes)
    $separator = if ($existing -and -not $existing.EndsWith("`n")) { "`n" } else { '' }
    [IO.File]::AppendAllText($attributes, $separator + "README.txt text eol=lf`n.gitattributes text eol=lf`n", [Text.UTF8Encoding]::new($false))
}
function Enter-SessionEnvironment([string]$Flow) {
    $previous = @{}
    $settings = @{
        PATH = $env:PATH; GCM_INTERACTIVE = 'true'; GCM_GUI_PROMPT = $(if ($Flow -eq 'devicecode') { 'false' } else { 'true' }); GCM_MSAUTH_FLOW = $Flow; GCM_MSAUTH_USEBROKER = 'false'
        GCM_AZREPOS_CREDENTIALTYPE = 'oauth'; GCM_CREDENTIAL_STORE = 'wincredman'; GCM_TRACE = '0'; GCM_TRACE_SECRETS = '0'
        # PowerShell 7.5/.NET 会保留空字符串环境变量；Git 的部分跟踪开关按存在性启用，必须真正删除。
        GIT_TRACE = $null; GIT_TRACE_CURL = $null; GIT_CURL_VERBOSE = $null; GIT_LFS_SKIP_SMUDGE = '1'
    }
    foreach ($name in $settings.Keys) {
        $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
        # 普通 $null 传给 .NET string 参数会被 PowerShell 绑定为空串；NullString 才是真正的 null。
        if ($null -eq $settings[$name]) { [Environment]::SetEnvironmentVariable($name, [NullString]::Value, 'Process') }
        else { [Environment]::SetEnvironmentVariable($name, $settings[$name], 'Process') }
    }
    return $previous
}

$script:NormalizedUrl = Resolve-AzureUrl $RemoteUrl
$destination = Resolve-SafePath $TargetPath
if ($Branch.StartsWith('-')) { throw '无效分支名。' }
Invoke-Git @('check-ref-format', '--branch', $Branch) | Out-Null
if ($Action -in @('Probe', 'Clone')) {
    if (Test-Path -LiteralPath $destination) { throw 'Probe/Clone 需要尚不存在的新目录；不会覆盖、删除或复用已有目录。' }
    if (-not (Test-Path -LiteralPath (Split-Path -Parent $destination) -PathType Container)) { throw '目标的父目录必须已存在。' }
} else {
    Assert-IndependentCleanRepo $destination
    Assert-RepoEndpoint $destination
}
if ($CheckOnly) {
    [pscustomobject]@{ Status = 'PARAMETERS_AND_LOCAL_GUARDS_PASS'; Action = $Action; RemoteUrl = $script:NormalizedUrl; TargetPath = $destination; Branch = $Branch; NetworkUsed = $false }
    return
}
if (-not $IsWindows) { throw '本工具仅面向 Windows。' }
Invoke-Git @('credential-manager', '--version') | Out-Host
$savedEnvironment = Enter-SessionEnvironment $AuthFlow
try {
    Ensure-Lfs
    # 新仓使用空模板；不复制机器上其他项目的 hook。
    $script:EmptyTemplate = Join-Path ([IO.Path]::GetTempPath()) ('azure-repos-empty-template-' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $script:EmptyTemplate | Out-Null
    if ($Action -eq 'Clone') { Clone-Repo $destination }
    elseif ($Action -eq 'Pull') {
        Configure-Repo $destination
        Invoke-Git @('-C', $destination, 'pull', '--ff-only', '--no-rebase', 'origin', $Branch) | Out-Host
        Assert-RepoEndpoint $destination
        Invoke-Git @('-C', $destination, 'lfs', 'pull', 'origin') | Out-Host
        Invoke-Git @('-C', $destination, 'lfs', 'fsck') | Out-Host
    }
    elseif ($Action -eq 'Push') {
        Configure-Repo $destination
        Invoke-Git @('-C', $destination, 'lfs', 'fsck') | Out-Host
        Invoke-Git @('-C', $destination, 'push', '--no-follow-tags', 'origin', "HEAD:refs/heads/$Branch") | Out-Host
    }
    else {
        # Probe 只面向用户新建的空远端；不会向既有项目历史追加测试文件。
        $remoteRefs = @(Invoke-Git @('ls-remote', '--heads', '--tags', $script:NormalizedUrl))
        if ($remoteRefs.Count -gt 0) { throw 'Probe 只接受空远端仓库；请新建专用测试仓。' }
        New-Item -ItemType Directory -Path $destination | Out-Null
        $source = Join-Path $destination 'source'
        $download = Join-Path $destination 'download'
        Invoke-Git @('init', '--initial-branch', $Branch, "--template=$script:EmptyTemplate", $source) | Out-Host
        Configure-Repo $source
        Invoke-Git @('-C', $source, 'config', '--local', 'user.name', 'Azure Repos Synthetic Probe') | Out-Null
        Invoke-Git @('-C', $source, 'config', '--local', 'user.email', 'azure-repos-probe@example.invalid') | Out-Null
        Invoke-Git @('-C', $source, 'config', '--local', 'commit.gpgSign', 'false') | Out-Null
        Invoke-Git @('-C', $source, 'config', '--local', 'core.autocrlf', 'false') | Out-Null
        Invoke-Git @('-C', $source, 'lfs', 'track', '*.bin') | Out-Host
        Set-ProbeTextAttributes $source
        [IO.File]::WriteAllText((Join-Path $source 'README.txt'), "Azure Repos synthetic Git and LFS probe. No real project data.`n", [Text.UTF8Encoding]::new($false))
        $data = [byte[]]::new(16 * 1024 * 1024)
        [Security.Cryptography.RandomNumberGenerator]::Fill($data)
        [IO.File]::WriteAllBytes((Join-Path $source 'synthetic-16mib.bin'), $data)
        Invoke-Git @('-C', $source, 'add', '--', '.gitattributes', 'README.txt', 'synthetic-16mib.bin') | Out-Null
        Invoke-Git @('-C', $source, 'commit', '-m', '验证 Azure Repos 合成数据上传下载') | Out-Host
        Invoke-Git @('-C', $source, 'remote', 'add', 'origin', $script:NormalizedUrl) | Out-Null
        Invoke-Git @('-C', $source, 'lfs', 'fsck') | Out-Host
        $pointerSize = [int](Invoke-Git @('-C', $source, 'cat-file', '-s', 'HEAD:synthetic-16mib.bin'))
        if ($pointerSize -gt 1024) { throw '合成二进制未成为 LFS 指针，停止上传。' }
        Invoke-Git @('-C', $source, 'push', '--no-follow-tags', '--set-upstream', 'origin', "HEAD:refs/heads/$Branch") | Out-Host
        Clone-Repo $download
        $matches = foreach ($name in @('README.txt', 'synthetic-16mib.bin')) {
            $expected = (Get-FileHash -LiteralPath (Join-Path $source $name) -Algorithm SHA256).Hash
            $actual = (Get-FileHash -LiteralPath (Join-Path $download $name) -Algorithm SHA256).Hash
            if ($actual -ne $expected) { throw "独立下载的 $name 校验不一致。" }
            [pscustomobject]@{ File = $name; Bytes = (Get-Item -LiteralPath (Join-Path $download $name)).Length; SHA256 = $actual }
        }
        $result = [ordered]@{ Status = 'UPLOAD_AND_INDEPENDENT_DOWNLOAD_PASS'; RemoteUrl = $script:NormalizedUrl; CapturedUtc = [DateTime]::UtcNow.ToString('o'); Branch = $Branch; Commit = ((Invoke-Git @('-C', $source, 'rev-parse', 'HEAD')) -join ''); Files = @($matches); BillingVerified = $false }
        $result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $destination 'probe-result.json') -Encoding utf8
        Write-Host "上传、独立下载及 SHA256 校验通过：$(Join-Path $destination 'probe-result.json')"
        Write-Host '这证明本次传输成功；是否免费须同时核对 Azure 计费页面。'
    }
} finally {
    foreach ($name in $savedEnvironment.Keys) {
        if ($null -eq $savedEnvironment[$name]) { [Environment]::SetEnvironmentVariable($name, [NullString]::Value, 'Process') }
        else { [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process') }
    }
    if (Get-Variable EmptyTemplate -Scope Script -ErrorAction SilentlyContinue) {
        if (Test-Path -LiteralPath $script:EmptyTemplate) { Remove-Item -LiteralPath $script:EmptyTemplate }
    }
}
