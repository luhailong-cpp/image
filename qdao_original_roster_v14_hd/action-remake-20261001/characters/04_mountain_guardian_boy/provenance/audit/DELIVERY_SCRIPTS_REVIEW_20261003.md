# 04 交付脚本只读审阅

审阅时间：2026-10-03 19:24 UTC。范围为 `tools/finalize_delivery.py`、`tools/build_preview.py`、`tools/build_review_media.py`、`tools/timing_profile.py`，并只读核对 `preview/template.html` 的时长消费逻辑。没有运行 finalizer，没有修改脚本、正式图、sidecar 或全局状态。当前仍有方向在修图，本记录不是 196 张美术通过证明。

## 1. P1：旧审计未绑定当前成品，新 native 可能在没有对应实测证据时被删

`finalize_delivery.py:17–18` 只检查审计文件存在；`23–26` 只验证正式图 SHA、1024 RGBA 与 model/quality 为 null，没有读取审计里的 formal/native 对应关系，也没有实测当前 native 尺寸和 SHA。`78–87` 随后把清理记录指向该审计并声明已实测。`build_preview.py:163–165` 在原生删除后，仅凭 `fileRetained=false`、声明尺寸与 64 字符 SHA，即把原生规格记为已验证，不检查 retentionRecord 或审计中的匹配证据。

实际快照：旧审计完成于 `2026-10-03T15:52:09.404067+00:00`；19:24 UTC 当前有 20 张正式图 SHA 已不同于该审计，分别为 NE 02/03/10/11、NW 01/02/16、S 02、SE 01/02/03/11/12/13/14/15/16、SW 09/10/11。后续修图可能继续增加差异。

建议在全部方向稳定并视觉核准后重新实测选中 native 的 SHA、尺寸、色彩模式、整画布导出关系，并绑定正式 SHA + native SHA + native 路径。finalizer 应在任何写入或删除前核验这份新证据完全匹配；预览的已删除原生分支应查验同一证据与真实删除记录，不能仅信布尔值。此项应在清理前解决。

## 2. P1：finalizer 无当前 SHA 的视觉核准门槛，且边验证边写通过状态

`finalize_delivery.py:28–32` 对每个输入无条件写 `visual_passed`、`independentPoseObserved=true` 与完整静态/离线检查声明；`43–52` 固定宣布 196 张静态通过。当前只读快照仍为 114 张 visual_passed、82 张 candidate_pending_visual。脚本尚未运行，未发生本脚本导致的假通过；问题是它目前不能强制兑现“全向修完并根视觉核准后运行”的前置要求。

另外 `40` 已保存当前帧后才继续验证下一帧，`42` 才检查总数与唯一性。后面的输入失败时，前面的 sidecar 已被提升为通过。

建议先完成全部输入预检，再读取根视觉核准记录并核对其中所有当前正式 SHA，只有完整匹配才统一写入通过状态。独立姿态与动态观感依赖实际视觉复核，不能用数量、尺寸、不同 SHA 代替。

## 3. P2：清理后 nativeSource 与 derivedFrom 保留状态互相矛盾

`finalize_delivery.py:83–88` 只更新 `nativeSource.fileRetained=false`。当前 40 张正式 sidecar 的 `derivedFrom` 原生条目仍有 `fileRetained=true`，因此同一已删源图会同时声明保留与未保留。

建议按原生路径与 SHA 同步对应 derivedFrom 的保留状态，保持模型、质量、SHA、尺寸与原始调用证据不变。并以实际删除成功的结果填写删除时间和保留状态；当前 `85` 标记已删发生在 `89` 真正 unlink 之前，删除中途失败可能留下错误状态。

## 核对通过的脚本逻辑

- 清理候选只来自本 04 目录的 provenance 下 PNG/GIF，以及明确列出的三组过期 preview/run_E_normal、run_N_normal、run_S_normal GIF 与对应派生记录。逐项 resolve 后有角色根目录边界断言，没有枚举 frames，也没有枚举其他角色目录。
- 提示词、提交参数、回执等 provenance 文字记录不在图片 glob 删除范围内；actualModel、actualQuality、submittedParameters 与原生 SHA/尺寸未被改写。
- 交付 manifest 的 recordSha256 在 sidecar 更新之后计算，顺序正确。
- 加权跑步节奏 `[40,70,60,40,40,30,30,50] × 2` 为 16 帧共 720 ms；承重段每半周 130 ms、短腾空每半周 60 ms；慢放乘 4 为 2880 ms。浏览器逐帧消费该数组，GIF 同样消费该数组，未发现算术或默认选择错误。
- 均匀跑步 640/720/800 与历史 480 入口仍可对照。受击 240 ms、普攻 360 ms、施法 720 ms 的总时长正确；一基帧号的普攻第 6 帧接触起点 150 ms、施法第 10 帧释放起点 405 ms 正确。
- 512,928 仍标作历史布局声明而非实测地面；客户端接入和跑步正式时长仍标未确认。

本记录检查代码与当前证据的一致性，不代替根对最终 14 组动画和新增修图的视觉验收，也不授权提前清理。
