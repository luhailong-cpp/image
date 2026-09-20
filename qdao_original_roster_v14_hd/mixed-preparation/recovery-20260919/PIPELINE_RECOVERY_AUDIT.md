# 2026-09-19 原版角色断线接续独立审计

审计只读角色、客户端与工具，没有生成图片、重写角色、启动 Unity 或发布。统计是本次接手时文件快照，不是视觉审批；其他代理继续补图后应再盘点。机器审计另见本目录 readonly-recovery-audit.json（仅在脚本完成后有效）。

## 实际进度

- 正式和隔离工程都只有 V13 00–03，尚无 QdaoOriginalRosterV14；正式完成仍 4/23。
- 04 旧 104 walk + 8 idle 未重做；V14 已导入 SW02/03/04/06/07/08/10/11/12 共 9 个新增动作。E01 是已有槽的试图，不计增量。04 仍缺 SW14/15/16，以及 NW02/03/04/06/07/08/10/11/12/14/15/16。
- 05 旧 52 walk + 8 idle 未重做；已导入 NE02/03/04/06，共 4 个新增动作；仍缺 72 walk。
- 06 旧 16 walk + 8 idle；仍缺 112 walk。
- 07–22 尚无新动作，每名缺 128 walk + 8 idle。
- 接手快照共缺 2247 walk + 128 idle = 2375 动作。未导入 raw 和缺工具回执的疑似恢复图不计完成。
- mixed-candidates、mixed-approved、mixed-stage-audits 和 mixed-publication-audits 当时均不存在。没有已封存的真实混合角色。

## 比旧 handoff 更新的工具事实

旧 handoff 声称混合发布器尚未实现已过时。现有 assemble_mixed_roster.py、approve_mixed_roster.py、stage_mixed_roster.py、publish_mixed_roster.py 已串起独立重建、线下视觉封存、隔离导入和首次正式 04 发布。文档分别是 tools/ASSEMBLE_MIXED_ROSTER.md、APPROVE_STAGE_MIXED_ROSTER.md、PUBLISH_MIXED_ROSTER.md。

11 项历史文本 SHA 差异已由 mixed-preparation/legacy-text-reconciliation-20260918/reconciliation-report.json 做精确字节规则白名单核对，status=passed。必须使用 --reconcile-legacy-text，不改写旧文本或其历史 hash。旧 handoff 的“7 项仍未解释”不再是最新状态。

现有发布器明确仅支持 04 首次发布；05/06 后续需要扩展流程以识别已发布 V14 的 GUID/index 差异，不能直接把 character ID 替换为 05/06。

## 具体缺口与限制

1. 现有 tools/preview.html 与根 index.html 为全 1024 预览，固定 candidate/<id> 路径，canvas 1024 使用 drawImage(im,0,0)。混合时旧 512 会以一半大小画出，不能据此审批比例。经主代理授权已新增独立 tools/mixed-preview.html、serve_mixed_preview.py、MIXED_PREVIEW.md，读取明确 immutable assembly，同世界尺寸统一绘到 1024×1024，标真实尺寸和 PPU。旧预览未改。真实 Edge QA 通过，记录见 preview-browser-qa.json；不构成角色视觉审批。
2. 当前 Unity 观测截图在角色停止后拍摄，04 为保留的 512 idle。publisher 明确记录该限制。真实 1024 walk 的近距细节、混合边界和接缝由完整线下封存审核，截图不能被表述为 1024 walk 的真实游戏近景证明。若用户目标要求该证明，仍应补专门的真实运动截图/观察。
3. native assembler 不接受无原回执恢复图：validate_native_receipt 需要 actual_request 的精确 prompt、referenced_image_paths、started_at；真实 output_hint 完整路径；原 generated PNG 现存且 raw SHA 一致；一次内置、零付费调用。找不到工具回执只能保留孤立 raw 与明确未确认绑定，不能凭“图很像”伪造完整来源或算完成。
4. capture_unity_inputs.py 拒绝任何存在的 Temp/UnityLockfile。stage/publish 可验证未占用的 stale 文件而不删除。审计当时隔离工程没有锁，正式工程有旧锁；正式不需要跑此快照工具。
5. 审批对 assembler/approve 文件 SHA 绑定；真正封存以后更改工具会让旧审批失效。因此先定妥工具和测试，再审批。
6. **实际首次 04 发布阻点，现已修复：** 正式与隔离旧角色均 3451 文件，文件集合一致，但 637 个既有 V13 .meta 的 SHA 不同；全部作者资源一致，50 绑定源码/配置/meta 一致。正式 meta 有的仅 fileFormatVersion/guid 两行，隔离已导入 meta 带独立 GUID 和完整 TextureImporter。原 publisher 跨项目要求旧全集相同导致拒绝。后续已获主代理授权，改为正式历史固定基线与隔离stage基线分别完整保护，跨项目只比作者文件。16项小型测试通过；没有改旧meta或发布，详见本目录 PUBLISHER_META_FIX.md。

## 04 完成后的精确命令序列

以下是核对实现后的操作清单，不是已执行证据。当前素材不完整时不要执行后续步骤。RUN 名必须新建且不得复用既有输出。

```powershell
$rosterPython = 'C:/Users/luyua/AppData/Local/Programs/Python/Python312/python.exe'
$rosterV14 = 'E:/work/image/qdao_original_roster_v14_hd'
$rosterV13 = 'E:/work/image/qdao_original_roster_v13'
$rosterIsolated = 'E:/work/tmp/qdao-original-live-candidate-20260917'
$rosterId = '04_mountain_guardian_boy'
$rosterRun = 'mixed04-real-assets-NEW_UNIQUE_RUN'
$rosterAssembly = "$rosterV14/mixed-candidates/$rosterRun/$rosterId"
$rosterApproved = "$rosterV14/mixed-approved/$rosterRun/$rosterId"
$rosterOfflineReview = "$rosterV14/mixed-reviews/$rosterRun/visual-review-input.json"
$rosterStageAudit = "$rosterV14/mixed-stage-audits/$rosterRun.json"
$rosterTestRun = "$rosterV13/runtime-validation/$rosterRun"

& $rosterPython -X utf8 -B "$rosterV14/tools/assemble_mixed_roster.py" assemble --character $rosterId --preparation "$rosterV14/mixed-preparation/preserve-20260918-run1" --hd-candidate "$rosterV14/candidate/$rosterId" --output $rosterAssembly --reconcile-legacy-text --require-complete
# Only after the dry run passes, repeat with --execute.
& $rosterPython -X utf8 -B "$rosterV14/tools/assemble_mixed_roster.py" check --directory $rosterAssembly --require-complete

# Actually review this exact assembly and create the evidence-bound review.
& $rosterPython -X utf8 -B "$rosterV14/tools/approve_mixed_roster.py" approve --assembly $rosterAssembly --review-input $rosterOfflineReview --output $rosterApproved
# Only after the dry run passes, repeat with --execute.
& $rosterPython -X utf8 -B "$rosterV14/tools/approve_mixed_roster.py" check --directory $rosterApproved
& $rosterPython -X utf8 -B "$rosterV14/tools/stage_mixed_roster.py" --approved $rosterApproved --project $rosterIsolated --audit $rosterStageAudit
# Only after the dry run passes, repeat with --execute.

# Run an import pass separately, close it, and confirm the actual metas/index exist.
# This isolates import changes from the three subsequent identical test snapshots.
$rosterUnity = 'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe'
$rosterImportArgs = @('-batchmode','-quit','-force-d3d11','-projectPath',('"'+$rosterIsolated+'"'),'-executeMethod','MmorpgClient.Editor.Tianyong.QdaoOriginalHdResourceIndexBuilder.RebuildAll','-logFile',('"'+$rosterTestRun+'/import.log"'))
# First create the new run directory and preserve launch/completion/exit evidence.
# Start-Process must use -WindowStyle Hidden and wait for completion.

& $rosterPython -X utf8 -B "$rosterV13/tools/capture_unity_inputs.py" --project $rosterIsolated --output "$rosterTestRun/input-editmode.json"
& "$rosterV13/tools/run_unity_tests.ps1" -Platform EditMode -Project $rosterIsolated -Run $rosterRun -InputSnapshot "$rosterTestRun/input-editmode.json"
& $rosterPython -X utf8 -B "$rosterV13/tools/capture_unity_inputs.py" --project $rosterIsolated --output "$rosterTestRun/input-playmode.json" --compare "$rosterTestRun/input-editmode.json"
& "$rosterV13/tools/run_unity_tests.ps1" -Platform PlayMode -Project $rosterIsolated -Run $rosterRun -InputSnapshot "$rosterTestRun/input-playmode.json"
& $rosterPython -X utf8 -B "$rosterV13/tools/capture_unity_inputs.py" --project $rosterIsolated --output "$rosterTestRun/post-playmode.json" --compare "$rosterTestRun/input-playmode.json"

# Inspect actual normal + nearest captures and save the runtime review schema
# documented in PUBLISH_MIXED_ROSTER.md, acknowledging preserved 512 idle.
& $rosterPython -X utf8 -B "$rosterV14/tools/publish_mixed_roster.py" --approved $rosterApproved --project 'E:/work/mmorpg-client' --run $rosterTestRun --stage-audit $rosterStageAudit --runtime-visual-review "$rosterTestRun/runtime-visual-review.json" --audit "$rosterV14/mixed-publication-audits/$rosterRun.json"
# Only after dry-run is ready and the current review is valid, repeat with --execute.
```

The publisher requires real Original5, Mixed1, FullHD0; 136 actual per-frame geometry entries; identical Edit/Play/post full inventories; all 50 bound source/config/meta files equal formal; the old real motor baseline; all required HD/mixed Unity tests passed; current screenshot hashes and visual observations. The older review_mixed_client_run.py is not suitable for this new art run because it requires mixed=0.

Formal execution only adds 140 authored files. It deliberately does not copy isolated GUID metadata or derived index. Its successful status is published_pending_formal_editor_import; it is not evidence that formal Unity has already imported or run the new assets.

## 并发与测试

只读进程查询未见运行中的 Unity。发现 PID 29536 为 E:/work/image/.git/push-until-success.py；另外有主城地图生成记录进程。没有干预这些进程，不做广泛 git/reset/clean 操作。其他角色读取进程属于当前并行代理。

本次发起既有 test_publish_mixed_roster、test_approve_stage_mixed_roster、test_assemble_mixed_roster 三组独立临时夹具测试。第一条完整 dry-run→140 文件发布的合成用例通过；单例耗时约 20 分钟，本次自有 worker 在第二例期间停止，**全套未完成**。结果见 tests-recovery-result.json，不能称三组全通过。它们不验证真实角色视觉或实际 Unity。

04 已有九张 SW 的另外一组低开销核对全部通过：prompt 与实际 request 字符完全一致；raw SHA 符合 source 记录；原 generated 文件 SHA 等于 raw；receipt SHA 符合 source 记录；全部 reference 文件存在。其 source 字段没有 05 旧四张发现的 request 缺失与末尾换行差异。
