> **2026-09-19 最新：用户要求暂停，之后再继续。请先读 [暂停总交接](HANDOFF_20260919_PAUSED.md) 和 [精确暂停库存](CONTINUATION_STATE_20260919_PAUSED.json)。下文为历史记录，不要沿用旧数量或2.5前置暂停要求；本任务没有后台续画。**

# 原版角色接续：混合分辨率与型号阻点

本轮从 `HANDOFF_FOR_NEW_WINDOW_20260918.md` 接手。全部23名尚未完成；原交接和既有证据保留。

## 用户现已授权当前内置入口续画（最新）

用户在明确说明当前型号未确认、上次创建记录为2.0后，选择：“允许用当前内置入口继续，不要求确认 2.5”。剩余绘图已获准恢复；仅取消2.5确认前置要求，仍须真实来源记录、单格原生至少1024、逐方向视觉审核及真实Unity验收。旧图和旧型号记录保留，00–03不重做，不调用收费API，不覆盖地图/UI工作。[授权记录](model-evidence/20260918-user-authorized-current-builtin.json)。当前从04的SW缺帧继续。

## 14:20 UTC 单次授权核验后的历史状态

用户随后明确回复“确认”，授权仅一次 04 山岳守卫 SW02 内置生图，允许先生成该核验图以检查实际型号；这不是授权未确认型号的批量续画。此次实际调用一次，原图 1254×1254，创建记录时间 2026-09-18T14:20:19.551901706Z，内嵌 software_agent 为 gpt-image / 2.0，工具回执没有实际型号字段。因此仍不能确认 GPT Image 2.5，已停止后续绘图。C2PA 仅提取元数据，未验证签名。

核验图、实际参数、回执及来源检查单独保留在 [SW02 单次核验目录](generation-model-probe/04_mountain_guardian_boy/SW02-single-v1/README.md)；[机器结果](model-evidence/20260918-sw02-single-probe-result.json)绑定原图 SHA。默认生成原图保留。没有切入候选、没有视觉批准、没有计入完成、没有导入 Unity、没有收费 API。SW02 仍为下一缺帧，缺失总数仍为2388，正式角色仍为4/23。此次例外已用完，不自动重试。

## 此次单次核验前的记录（保留历史）

用户在本记录之后再次要求继续未完成的绘图，并明确确认：“确认是剩下的用gpt iamge  2.5”。此确认保留剩余新图必须可确认为GPT Image2.5的限制，没有授权型号未确认的内置续画或收费API。再次核查本窗口入口参数未变化，model-evidence也没有新后端证据，因此没有新增生图调用。只读复核04的SW/NW仍各仅01/05/09/13，下一张待补为SW02。

本窗口实际工具仍仅有 `prompt`、`referenced_image_paths`、`num_last_images_to_include`，没有型号/质量选择器或新的后端版本证明。[官方API模型文档](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)证明2.5型号存在，不能证明本会话内置调用使用2.5。没有进行任何新生图或收费API/CLI调用。

证据：[本窗口入口核查](model-evidence/20260918-new-window-entry-check.json)。旧图型号和来源记录未改写。

## 已核对的实际库存

- 正式接入仍为00–03，共4/23名；没有正式V14资源目录。
- 04保留104walk+8idle，缺SW/NW各12walk。
- 05保留52walk+8idle，缺76walk。
- 06保留16walk+8idle，缺112walk。
- 07–22仍各缺128walk+8idle。
- 合计仍缺2260walk+128idle=2388张动作；没有用strip、试图或测试纹理抵数。

[精确缺帧表](mixed-preparation/preserve-20260918-run1/missing-actions.json)保存19名逐槽路径。

## 旧素材保护与来源问题

04–06的196动作及3肖像建立了保护快照；1553个相关证据文件纳入重验。12项准备工具测试通过，`--require-complete`实际拒收不完整准备记录。详见[准备工具验证](mixed-preparation/pipeline-validation-20260918.json)。

[只读库存审计](mixed-preparation/inventory-audit-20260918.json)确认旧动作输出、raw和23名原肖像SHA匹配。另发现11项旧来源文本SHA偏差，其中4项确认只是LF/CRLF；剩余7项均在04，尚不能解释。保留预期/实际双SHA，没有覆盖历史记录或宣告来源通过。这7项是S左靴pair-v4提示词，以及NE四个resume批次、SE两个resume批次回执。

00–03未重新加工或封存。正式3451个角色资源文件另有本轮保护基线。

## 分辨率兼容实现

[混合合同](MIXED_RESOLUTION_CONTRACT.md)明确仅04–06启用`mixed-preserved-v1`。旧动作保留512/52PPU，新动作1024/104PPU，逐帧加载，世界尺寸和归一化pivot一致；完整137PNG、来源尺寸/SHA、保留快照、方向缓存及生命周期均显式记录。

客户端代码仅在原有角色加载器、元数据索引、角色测试内改动；相机和地图配置不改。混合观测独立记录，不算全HD。新增测试在内存创建测试纹理，不进入任何候选或Unity Resources。

## 本轮真实Unity状态

唯一隔离工程：`E:/work/tmp/qdao-original-live-candidate-20260917`。

新运行：`E:/work/image/qdao_original_roster_v13/runtime-validation/mixed-resolution-client-run1`。

- EditMode：363/363，failed/skipped/inconclusive=0，Unity exit0。
- PlayMode：43/43，failed/skipped/inconclusive=0，Unity exit0。
- 新增混合测试为14 Edit+8 Play，共22项，使用内存夹具验证真实加载器和生命周期。
- Edit、Play、post三次完整输入共25977文件，逐SHA零增删改。
- 50个源码/meta/相机配置绑定全部核对；6个已有角色C#和4个新增C#/meta，共10文件已按白名单同步正式客户端。
- 正式3451个角色资源文件在同步前后逐SHA及文件集均未变。正式原有锁文件确认未占用后保留，没有删除；正式Unity未启动。
- [独立同步后审计](../qdao_original_roster_v13/runtime-validation/mixed-resolution-client-run1/independent-post-sync-audit.json)再次读取正式/隔离50项绑定并检查3451资源全集，结果零增删改；SHA：`f227556ffc57c6b0596652e02c62a255215636a7ca8b2c59c400556941b244b2`。
- [最终运行审计](../qdao_original_roster_v13/runtime-validation/mixed-resolution-client-run1/final-result-review.json) SHA：`d5e8860e30cdda7cd6d19596ed38967c835bc1780acb001e2f819b3e6e519e24`。
- [正式源码同步结果](../qdao_original_roster_v13/runtime-validation/mixed-resolution-client-run1/source-sync-result.json) SHA：`b1a3bf539d4c945053275afc314f282fbae363b117be7958f5c0233baf28330c`。
- 12张实际正常视角PNG均通过来源/尺寸/相机记录核对；03正常截图已实际目视作源码回归抽查，[观察记录](../qdao_original_roster_v13/runtime-validation/mixed-resolution-client-run1/normal-view-regression-observation.json)不改写旧审批。
- 尚无完整真实混合角色、完整真实全HD角色或新角色近景清晰度验收。

## 后续实际待完成

确认可验证的内置GPT Image2.5入口后，从04的SW/NW缺帧开始。不得通过更换收费入口或重复旧型号探针绕过暂停。新图真实原生cell两边至少1024，单人单帧优先，保留raw/prompt/真实工具回执/型号证据。

混合准备工具只写元数据。目前原V14发布器仍为全高清合同；真实混合资产还需完成来源独立重建、旧文本证据冲突处理、逐方向与近景视觉封存、混合发布门禁及其拒收测试，再用新run完成真实混合素材的Unity验证和正式资产发布。不能将本轮代码测试当作这些步骤已完成。
