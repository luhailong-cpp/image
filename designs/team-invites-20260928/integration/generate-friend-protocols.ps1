param(
    [string]$ServerRoot = 'E:/work/xuanming-server-mmo',
    [string]$Protoc = 'E:/work/xuanming-server-mmo/third_party/grpc/install_vs2026/bin/protoc.exe',
    [string]$GoPlugin = 'C:/Users/luyua/go/bin/protoc-gen-go.exe'
)
$ErrorActionPreference = 'Stop'
$serverStage = Join-Path $PSScriptRoot 'server'
$clientStage = Join-Path $PSScriptRoot 'client/Assets/Scripts/Proto/Generated'
$goStage = Join-Path $serverStage 'go/proto'
New-Item -ItemType Directory -Path $goStage,$clientStage -Force | Out-Null
& $Protoc "--proto_path=$serverStage" "--proto_path=$ServerRoot" "--proto_path=$ServerRoot/third_party/grpc/third_party/protobuf/src" "--plugin=protoc-gen-go=$GoPlugin" "--go_out=$goStage" '--go_opt=module=proto' '--go_opt=Mproto/friend/friend.proto=proto/friend' '--go_opt=Mproto/common/base/tip.proto=proto/common/base' '--go_opt=Mproto/common/base/empty.proto=proto/common/base' '--go_opt=Mproto/db/proto_option.proto=proto/db' "--csharp_out=$clientStage" 'proto/friend/friend.proto'
if ($LASTEXITCODE -ne 0) { throw 'Friend 协议生成失败。' }
Write-Output 'Friend 的 Go 与 C# 协议已由 protoc 生成；RPC 方法与消息号未变。'
