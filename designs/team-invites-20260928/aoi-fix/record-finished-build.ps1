$ErrorActionPreference = 'Stop'
$result = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'baseline-build-result.json') -Raw | ConvertFrom-Json
if ($result.exitCode -ne 0) { throw '隔离 Scene 尚未编译成功，不可记录完成' }
if ((Get-FileHash -LiteralPath $result.exe).Hash.ToLowerInvariant() -ne $result.sha256) { throw 'Scene 产物 SHA 不一致' }
$serverRoot = 'E:/work/xuanming-server-mmo'
$actual = Join-Path $serverRoot 'cpp/libs/services/scene/spatial/system/aoi.cpp'
$stage = Join-Path $PSScriptRoot 'server/cpp/libs/services/scene/spatial/system/aoi.cpp'
Copy-Item -LiteralPath $actual -Destination $stage
$verificationPath = Join-Path $PSScriptRoot 'verification.json'
$verification = Get-Content -LiteralPath $verificationPath -Raw | ConvertFrom-Json -AsHashtable
if (-not $verification.ContainsKey('sceneBuildHead')) { $verification['sceneBuildHead'] = $verification['sceneBuild'] }
$verification['sceneBuild'] = @{
    revision = $result.revision; exitCode = $result.exitCode; log = $result.log; exe = $result.exe
    sha256 = $result.sha256; deployedBinaryUnchanged = $result.deployedBinaryUnchanged
    originalDeployedSha256 = 'f39344f361dd975497aa0340d1c6e6dcf78204b293a950fe54e61092046073f1'
    pdbSourceChecksumMatchCount = 993; pdbSourceChecksumMismatchCount = 0
    buildTargets = @('cpp\libs\services\gate', 'cpp\libs\services\battle', 'cpp\nodes\scene')
    linkedInputEvidence = 'baseline-linked-inputs.json'
    verifiedLocalLibraryCount = 16
    sourceDifference = '仅加入当前任务 AOI 双向通知修复，自有库使用同一提交构建，禁 PostBuildEvent'
}
$verification['fixedSha256'] = (Get-FileHash -LiteralPath $actual).Hash.ToLowerInvariant()
$verification | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $verificationPath -Encoding utf8
$progress = Join-Path $serverRoot 'PROGRESS.md'
$title = '## 2026-10-01 组队邀请联机验收：修复 AOI 反向创建/销毁通知（Codex，已编译与回归）'
if (-not ([IO.File]::ReadAllText($progress).Contains($title))) {
    $entry = @"


$title

- 缺陷：后来入场玩家能看到静止玩家，但静止玩家仅有服务器兴趣关系，收不到 ActorListCreate；移出视野时反向 ActorListDestroy 同样遗漏。aoi.cpp 现在对实际新增的反向兴趣关系立即发创建通知，对反向移除立即发销毁通知；原有隐身、容量拒收、pinned 例外保持独立方向判定。
- 正式回归：新增 cpp/tests/aoi_delivery_test，直接编译生产 AOI/Grid/Interest/View，仅截获网络发送边界；登记 tools/scripts/run_cpp_tests.ps1。原实现 2 项失败、3 项通过；修复后和正式入口 -Build -Filter aoi_delivery_test 均 5/5 通过，覆盖静止观察者、新入场、双向移出、隐身/容量及 pinned 行为。
- 当前主工作区完整 Scene 构建暴露其他任务的 GuildInternal/GuildActivity 生成链缺失。只补齐了正式 protoc 35.1 生成的 guild_internal.pb/grpc.pb 四文件，没有手改生成代码、没有给新 Guild RPC 分号，也没有改变路由。当前主工作区的整套构建仍不可据本条宣称通过。
- 为交付本次最小修复，只读提取已部署 scene.exe 的 PDB 源码校验和；正式提交 $($result.revision) 与全部 993 个仓库源码记录匹配，零差异。部署前旧 exe SHA256=f39344f361dd975497aa0340d1c6e6dcf78204b293a950fe54e61092046073f1。
- 从上述唯一提交导出隔离源码，仅加入已回归的 aoi.cpp 最小补丁；所有自有库使用同一源码从空目录构建，第三方 SDK 复用；MSBuild /m:1 /nr:false，关闭 PostBuildEvent。中途工具会话被打断后，仅增量续编同一输出目录；未清缓存，未混入当前主工作区新库。解决方案遗漏 gate/battle 前置依赖，因此显式先构建这两个同基线正式目标，再完成 Scene 链接。最终构建 exit 0，0 警告/0 错误；真实 link.read 输入逐项证明 16 个本地库全部来自隔离目录，详见 baseline-linked-inputs.json。
- 新 exe：$($result.exe)，SHA256=$($result.sha256)。本子任务未替换/重启运行服务器；根任务负责随后部署和双客户端四入口验证，联网结果以组队邀请总验收记录为准。
- 证据：E:/work/image/designs/team-invites-20260928/aoi-fix/verification.json、deployed-pdb-sources.txt、deployed-baseline-comparison.json、repository-regression.log、baseline-build-result.json 及其构建日志。
"@
    [IO.File]::AppendAllText($progress, $entry, [Text.UTF8Encoding]::new($false))
}
Write-Output '已更新 AOI 交付证据与 PROGRESS，仅记录实际通过项。'
