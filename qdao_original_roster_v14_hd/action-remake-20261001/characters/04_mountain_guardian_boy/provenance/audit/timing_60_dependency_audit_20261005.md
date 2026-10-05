# 04 山岳守卫：60ms 时序依赖只读审计

审计时间：2026-10-05 08:46:39 UTC。根窗口正在迁移，本文件是**迁移中的依赖快照**，不能当作迁移完成后的失败报告。授权目标：八向跑步16帧，每帧60ms，全圈960ms；每两个独立姿态的位置段120ms；0.25倍慢放240ms/帧、3840ms/圈。受击40ms、普攻30ms、施法45ms保持原规格。

本次只读脚本、当前JSON清单、HTML和APNG编码；唯一写入为本审计文件。没有执行会写审核/运行清单的校验脚本，没有修改图片、sidecar、工具、runtime、交接或历史证据。

## 当前时序入口与写入依赖

下列相对路径都以本角色目录为根：
`D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy/`。

| 活跃入口 | 实际读取/写入关系 | 60ms迁移易漏项 |
|---|---|---|
| `tools/timing_profile.py` | RUN_FRAME_MS=60、RUN_CYCLE_MS=960、16项RUN_NORMAL_DURATIONS；被预览/交付/验证工具导入 | 当前已60/960；作为当前时序源保留。 |
| `tools/register_frame.py:25`、`:179` | SPECS决定新正式帧sidecar的frameDurationMs；每次登记会写 `frames/run/<D>/frame_<NN>.generation.json` | 初读仍75，已即时报告；后续复读已由根改为60。建议以后直接引用RUN_FRAME_MS，避免下一次新登记重新产生旧时序。新登记目前不自动产生完整runTiming，仍要由收尾统一。 |
| `tools/finalize_video_axis_followup.py` | 读旧runtime、delivery、review、所有正式sidecar与新视觉核准；run覆盖为RUN_FRAME_MS；写196份正式sidecar、runtime、review、delivery、frames.sha256、新snapshot/ledger | 输入检查保留75/1200是本次有意的迁移前置条件；不能直接把全部75字符串替换成60。apply后是一次性完成，不应当成后续反复刷新工具。 |
| `runtime_timing.json` | 客户端合并交接读取的机器时序 | run.frameMs、offlineDefaultLoopMs、offlineFrameDurationsMs、previewFrameDurationsMs、status、timingRationale、groundContactSegments八向各8段durationMs必须一起迁移。当前新finalizer已包含段时长乘RUN_FRAME_MS。 |
| `frames/run/<D>/frame_<NN>.generation.json` | 128份当前正式记录 | frameDurationMs=60；runTiming.offlinePreviewFrameMs=60、offlinePreviewDefaultLoopMs=960、offlinePreviewFrameDurationsMs=[60]×16。历史timingHistory和priorReview保留旧75证据。 |
| `manifest.delivery.json` | files[].path/sha256指正式PNG，files[].record/recordSha256指其sidecar，另引用review和runtime | 仅修改时序也会改变sidecar的SHA。根审核更新196份记录后需刷新全部对应recordSha256；PNG SHA只因真正换图才变化。 |
| `tools/build_preview.py` | 从当前正式PNG和完整sidecar读取；生成 `manifest.technical.json` 与 `preview/index.html` | 必须在最终sidecar与核准全部落盘后**再运行一次**。其中source.record_sha256和declared_record是嵌入快照，早建会保存旧75或旧审核信息。 |
| `preview/template.html:53–54` | frameMs()读取内嵌sequence.frame_ms；cycleMs()读取duration_ms，按speed除算 | 播放器不在运行时fetch runtime_timing.json；只改runtime不能更新已生成的index。模板说明已960/60。 |
| `preview/index.html` | manifest-data脚本块内嵌整个技术清单；图片URL附当前PNG SHA前缀 | 迁移需重建页面；每帧JSON来源record_sha256也需和当前sidecar一致。不要因图片像素未变就跳过重建。 |
| `tools/build_review_media.py` | run读取RUN_FRAME_MS，写每方向contact PNG、normal/slow APNG及各自.generation.json | 八向都要构建；normal=[60]×16，slow=[240]×16，编码总长960/3840。工具已60，当前并非所有已有文件自动随代码变化。 |
| `preview/run_<D>_normal.apng.generation.json`、slow同名记录 | 绑定动画文件SHA、derivedFrom当前16PNG、operation.durationsMs/logicalFrameMs/sequenceDurationMs | 动画重编码会改变自身SHA；更换正式帧也要求刷新derivedFrom。contact没有时长，但当前换图方向仍须更新contact及其来源。 |
| `preview/gallery.html:18–24` | 直接加载run_<D>_normal/slow.apng与战斗GIF；revision查询串用于刷新资源 | 说明文字已960/60不代表磁盘APNG已重建。查询串当前已video_axis_hands_960_20261005；最终需确认浏览器不继续缓存旧动画。 |
| `tools/validate_timing_960_player.cjs` | 读取实际index及内嵌脚本，验证60/960、0.5/0.25、暂停、逐帧、战斗时长；写独立新审计 | 此新入口已存在。应在最终index构建后执行，否则报告中的html SHA会过期。旧1200报告继续作为历史。 |
| `tools/verify_delivery.py` | 读取delivery/review/current approval、runtime、technical、正式帧/sidecar、42份预览，并写final_delivery_verification.json | 已新增60/960及每段120、APNG60/240检查。它对technical校验PNG SHA和序列时长，但当前代码未单独复验technical中source.record_sha256，也未读取index内嵌副本；因此最终build_preview顺序仍必要。 |

## 08:46:39 UTC 实际文件快照

- runtime仍75ms/1200ms；64个支撑位置段仍150ms。
- 128份run正式sidecar的frameDurationMs均75；N01的当前runTiming仍75/1200。
- technical及index内嵌的八向sequence已全部frame_ms=60、duration_ms=960。
- 16份run APNG全部自身SHA与各sidecar匹配。NW normal实际16×60=960，NW slow实际16×240=3840；其余7向仍normal16×75=1200、slow16×300=4800。
- W normal及slow的derivedFrom分别有9个PNG SHA过期，需要最终重建；其余当时所读run APNG的来源SHA匹配。
- delivery存在30条旧PNG SHA和30条旧sidecar SHA，首批样例为NE02、03、07、10、14。此为本轮改图尚未finalize的预期状态，根正在处理。
- technical与index的PNG/record SHA在该快照时刻均无过期；finalizer后将因sidecar变化需要重建。
- review.rootVisualApproval当时仍指向 `provenance/audit/stancepairs_final_visual_approval_20261004.json`，SHA为 `4dbe4a34779edf3bd5f727d14cab8bc4f369edde82d7e54e68ae275923053632`；timingUpdate仍指向旧run_timing_1200_update审计。新finalizer负责更新当前绑定，不改旧审计本身。

## 历史入口与当前文档引用

以下含75/1200并不等于应改写历史证据，但要避免以后被误当当前写入入口：

- `tools/apply_run_timing_1200.py` 开头已检查RUN_FRAME_MS!=75即退出；当前60下不会回写旧时序。
- `tools/finalize_delivery.py` 主入口末尾已有75数组守卫；内有旧75/1200写入逻辑，当前只作为新finalizer导入辅助函数。新finalizer已明确覆盖导入SPECS的run，故不是本次遗漏。
- `tools/finalize_bamboo_followup.py` 与 `tools/finalize_stancepairs_followup.py` 预检要求[75]×16；当前60源会阻止它们进入写入。
- `tools/build_bamboo_reference.py` 已有75保护；旧竹弓对照不应重新引入当前gallery。
- `tools/validate_timing_1200_player.cjs` 仍是75/1200测试，且会写旧命名验证报告。完成后文档应改指960工具和新报告，而不以旧测试失败作为素材失败。
- `provenance/audit/preview_timing_audit.py` 是旧GIF专用审计，不覆盖当前run APNG；不能用它代替当前verify_delivery。
- `provenance/run/E_build_preview.py`、`W_build_preview.py`、`NE_contact_review.py` 等旧制作脚本含720/800等GIF写入，产物在provenance；当前gallery实际引用preview/*.apng，正式重建只使用tools/build_review_media.py。
- 当前 `tools/README.md`、角色 `README.md`、`STATUS.md`、`MERGE_HANDOFF.md` 仍有75/1200、300/4800、每段150和旧1200验证入口。根完成迁移时需同步当前描述和报告链接；其中明确标注历史轮次的记录可原样保留。
- `provenance/run/video_axis_N_NE_combat_100_review_20261004.json` 的durationMs=75是此前真实审查快照；补充手审与其他逐图历史SHA也只代表各自审查时点。保留这些历史证据，通过当前rootVisualApproval和新时序迁移证据声明最新状态。

## 建议的收尾顺序

1. 当前新视觉核准绑定最终196张PNG；执行本轮finalizer迁移正式sidecar、runtime、review与delivery，确保64个支撑位置段各120ms。
2. 用build_review_media重建八向run的contact/normal/slow，实际解码16份APNG确认60/240，无额外首尾帧；战斗时序不动。
3. 最后运行build_preview刷新technical和index的完整sidecar快照，再跑960播放器逻辑验证与verify_delivery。注意后续任何sidecar变更都会要求再次刷新内嵌record SHA。
4. 同步当前README/STATUS/MERGE_HANDOFF/tools README的时长、旧验证链接和“完成”状态；浏览器查看当前gallery与index。客户端未接入维持事实说明。

本审计只给依赖与迁移中状态，不代表最终时序、美术或客户端验收。

