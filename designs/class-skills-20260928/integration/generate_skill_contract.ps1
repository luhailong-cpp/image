$ErrorActionPreference = 'Stop'
$serverRoot = 'E:/work/xuanming-server-mmo'
$generationRoot = Join-Path $PSScriptRoot '.contract-generation'
$stagedServer = Join-Path $PSScriptRoot 'server'
$stagedClient = Join-Path $PSScriptRoot 'client'
New-Item -ItemType Directory -Force -Path $generationRoot | Out-Null
$templateDestination = Join-Path $generationRoot 'internal/template'
New-Item -ItemType Directory -Force -Path $templateDestination | Out-Null
Copy-Item -Path (Join-Path $serverRoot 'tools/proto_generator/protogen/internal/template/*') -Destination $templateDestination -Recurse -Force
Copy-Item -LiteralPath 'C:/Users/luyua/go/bin/protoc-gen-go.exe','C:/Users/luyua/go/bin/protoc-gen-go-grpc.exe' -Destination $generationRoot -Force
New-Item -ItemType Directory -Force -Path (Join-Path $generationRoot 'robot/logic/handler') | Out-Null
foreach ($relative in @('proto', 'generated/code/proto')) {
    $destination = Join-Path $generationRoot $relative
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    Copy-Item -Path (Join-Path $serverRoot ($relative + '/*')) -Destination $destination -Recurse -Force
}
Get-ChildItem -LiteralPath (Join-Path $stagedServer 'proto') -Recurse -File | ForEach-Object {
    $relative = [IO.Path]::GetRelativePath($stagedServer, $_.FullName)
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $generationRoot $relative) -Force
}
$unityOutput = Join-Path $generationRoot 'unity'
$handlerOutput = Join-Path $unityOutput 'Assets/Scripts/Net/Generated'
New-Item -ItemType Directory -Force -Path $handlerOutput | Out-Null
Copy-Item -Path 'E:/work/mmorpg-client/Assets/Scripts/Net/Generated/*' -Destination $handlerOutput -Recurse -Force
$config = Get-Content -Raw (Join-Path $serverRoot 'tools/proto_generator/protogen/etc/proto_gen.yaml')
$config = $config.Replace('output_root: "../../../"', 'output_root: "' + $generationRoot.Replace('\','/') + '/"')
$config = $config.Replace('unity_client_dir: "{{output_root}}../mmorpg-client/"', 'unity_client_dir: "{{output_root}}unity/"')
$config = $config.Replace('protobuf_dir: "{{grpc_dir}}third_party/protobuf/src/"', 'protobuf_dir: "' + $serverRoot + '/third_party/grpc/third_party/protobuf/src/"')
$configPath = Join-Path $generationRoot 'proto_gen.yaml'
Set-Content -LiteralPath $configPath -Value $config -Encoding utf8
$env:PROTO_GEN_CONFIG_PATH = $configPath
$env:PATH = $serverRoot.Replace('/','\') + '\third_party\grpc\install_vs2026\bin;C:\Users\luyua\go\bin;' + $env:PATH
Push-Location $generationRoot
try {
    & (Join-Path $serverRoot 'tools/proto_generator/protogen/proto-gen.exe') *> (Join-Path $PSScriptRoot 'client-contract-generation.log')
    if ($LASTEXITCODE -ne 0) { throw 'Standard proto-gen failed; see client-contract-generation.log' }
} finally { Pop-Location }
$idFile = Join-Path $generationRoot 'proto/message_id.txt'
$upgrade = Select-String -LiteralPath $idFile -Pattern '^\d+=SceneSkillClientPlayerUpgradeSkill$'
if (-not $upgrade) { throw 'Standard generator did not allocate UpgradeSkill' }
Copy-Item -LiteralPath $idFile -Destination (Join-Path $stagedServer 'proto/message_id.txt') -Force
New-Item -ItemType Directory -Force -Path (Join-Path $stagedClient 'Assets/Scripts/Net') | Out-Null
& pwsh -File (Join-Path $stagedClient 'tools/gen_messageids.ps1') -ProtoRoot $generationRoot
if ($LASTEXITCODE -ne 0) { throw 'C# message-id projection failed' }
$generatedClient = Join-Path $stagedClient 'Assets/Scripts/Net/Generated'
New-Item -ItemType Directory -Force -Path (Join-Path $generatedClient 'Handlers') | Out-Null
Copy-Item -LiteralPath (Join-Path $handlerOutput 'HandlerRegistry.cs') -Destination $generatedClient
$handler = Get-ChildItem -LiteralPath (Join-Path $handlerOutput 'Handlers') -Filter '*UpgradeSkill*.cs'
if ($handler.Count -ne 1) { throw 'Expected exactly one generated UpgradeSkill handler' }
Copy-Item -LiteralPath $handler.FullName -Destination (Join-Path $generatedClient 'Handlers')
Write-Output "Standard generator allocated $($upgrade.Line); C# IDs, handler and registry projected into staging."
