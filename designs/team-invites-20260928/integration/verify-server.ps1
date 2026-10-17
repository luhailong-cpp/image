param([string]$ServerRoot = 'E:/work/xuanming-server-mmo')
$ErrorActionPreference = 'Stop'
$stage = Join-Path $PSScriptRoot 'server'
$go = 'C:/Users/luyua/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.26.5.windows-amd64/bin/go.exe'
$env:GOCACHE = 'E:/work/image/.cache/go-build'
$env:GOTMPDIR = 'E:/work/image/.cache/go-tmp'
$env:GOTOOLCHAIN = 'local'
$env:GOWORK = 'off'
New-Item -ItemType Directory -Path $env:GOCACHE,$env:GOTMPDIR -Force | Out-Null
$replace = @{}
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $stage 'go') -Filter '*.go' -Recurse) {
    $relative = [IO.Path]::GetRelativePath($stage,$file.FullName)
    $replace[(Join-Path $ServerRoot $relative)] = $file.FullName
}
$overlay = Join-Path $stage 'overlay.json'
@{Replace=$replace} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $overlay -Encoding utf8
Push-Location (Join-Path $ServerRoot 'go/friend')
try {
    & $go test -mod=readonly "-overlay=$overlay" ./... -count=1
    if ($LASTEXITCODE -ne 0) { throw 'friend 测试失败。' }
    & $go vet -mod=readonly "-overlay=$overlay" ./...
    if ($LASTEXITCODE -ne 0) { throw 'friend 静态检查失败。' }
    # overlay 包含尚未落入原仓提交的代码，不能用原仓提交号给审核二进制盖戳。
    & $go build -buildvcs=false -mod=readonly "-overlay=$overlay" -o (Join-Path $PSScriptRoot 'friend-invites.exe') .
    if ($LASTEXITCODE -ne 0) { throw 'friend 编译失败。' }
} finally {
    Pop-Location
}
