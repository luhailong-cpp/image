# 最新状态：第二次对齐探片拒选，原图与失败 QA 已清理

2026-09-23 主任务确认：正确贴入 y1139..1254 的底邻 halo 后，输出仍有花瓣错位，并新增原城没有的横向倒角砖缝，因此第二次探片拒选。仅删除 `alignment-20260923T132520Z/probe-aligned-halo-v2/` 本轮原生图及 4 张失败 QA；无图片备份。

当前 c10 选用 native=0，完整 4096 候选=0，正式验收=0。真实请求／配置／回执、来源 SHA、原字节文字备份与拒选结论保留；删除清单和执行回执见 `alignment-20260923T132520Z/probe-aligned-halo-v2/cleanup-rejected-20260923/`。已删来源状态为 deleted_by_user_not_reverified，不能按历史观察声称现在仍可复验像素。

当前布局、共享 halo 对照和 registered-reference-only 设计输入保留。下一步以 `alignment-20260923T132520Z/probe-aligned-halo-v2/calibration-proposal.json` 的浮雕轮廓／控制点校准方案为准，先解决局部几何接续，不重复同一提示词。未恢复旧图，未写共享五 JSON，未改导航和宿主缓存。

---

以下为此前交接记录，按历史保留：

# 当前状态：r04_c02 探片拒选并已清理

2026-09-23 主任务亲看原像素接边，确认浮雕花瓣位置／弧形边界存在明显横断层，正式拒选。仅删除本探片原图与 3 张失败 QA 图，无图片备份；16 格准备几何、当前设计、风格与材质参考保留。当前选用 native 为 0，4096 候选为 0，正式验收为 0。

删除清单及原 SHA：`probe-r04_c02-20260923T125732Z/cleanup-rejected-probe-20260923/manifest.json`；执行结果见同目录 `receipt.json`。真实请求、配置、回执和来源文字保留。历史 SHA 不代表原图仍可读取，删除后的来源状态为 deleted_by_user_not_reverified。

下一步须处理原城 master 与已选底邻的局部几何接续；不要重复相同提示词刷图。没有更改共享五份 JSON，也没有处理宿主缓存。

---

以下是生图前准备记录，作为历史保留：

# r08_c10 制作输入交接（尚未生图）

已准备 16 格原生分区计划，单格目标 1254×1254，核心 1024×1024、四边 halo 115；相邻分区重叠 230。所有现有 PNG 仅为设计／材质／布局／检查参考，成品候选 0，正式美术与客户端实机验收 0。没有调用 image_gen、API 或 CLI，也没有更新共享 JSON。

## 坐标与来源

- 全城核心 LTRB：`[36864,28672,40960,32768]`；含 halo：`[36749,28557,41075,32883]`。
- 原城 6144 图核心：`[3456,2688,3840,3072]`。它是几何基准；广场重绘的名义对应范围 `[2816,1280,3584,2048]` 只用于比对，尚未证明逐点几何同一。
- 底邻是当前选用 `r09_c10 external-v8`，SHA `f5a45f15f69104c6f3dfe9f7a855e71f5d142d896cc78ffadbf12b3a57f813e4`。
- 左邻 `r08_c09` 的 `dbaf9d7e...` 仍在返修，记录为 provisional，不作为最终固定边。
- 材质使用选用 r08_c07 的原像素 768 裁片，风格实际附 `designs/gameplay-ui/04-guild.png`。全部完整来源 SHA 见 `layout-record.json` 与各 `.derived.json`。

## 请主任务先看的输入

1. `references/master-core-native384.png` 与 `references/plaza-core-native768.png`：对照原城／局部重绘差异。
2. `guides/r04_c02.master-layout-only.png` 与 `guides/r04_c02.plaza-layout-review-only.png`：首片几何对照。
3. `references/r04_c02.bottom-neighbor-native-context.png`：已选底邻的原像素条带。
4. `references/clean-stone-native768.png`：干净材质参考。

首片选 r04_c02：避开未定左边，先研究底邻约束。其全城范围 `[37773,31629,39027,32883]`；底邻顶端 115 行对应目标 y=1139..1254。1254×512 条带中剩余部分仅供上下文参考，不是多出来的目标重叠。首片灰色嵌板、弧线倒角及花卉浮雕在两版布局之间有局部区别，不能把数值变换通过当作衔接通过。

## 防止机械直线污染

新引导由单一原城源采样，没有邻图矩形拼贴，没有画 4×4 网格。底邻独立附图。x/y=115、1024、1139 是制作坐标，不是砖缝；禁止模型为色块或采样不连续补画水平／垂直分割线。真实构造线只依据原城设计。材质图只取画法，不复制它的金线、台阶或砖块布局。

`requests/r04_c02.draft.request.json` 仅是待审请求，不可视为真实提交。`generationReady=false`；须主任务先核清原城与底邻的几何冲突，再决定是否生图。配置目标是 gpt-image-2.5-sunburst / max；actualModel、actualQuality 均为 null。所有参考放大图、导航覆盖图与预览均不得进入拼接成品。

`preparation-validation.json` 的算术及 24 组分区重叠检查只验证制作计划，不是图像接缝验收。下一步生成后仍需完整检查 6 条内部缝、9 个内部交点及实际相邻外边和四块交点，精确绑定对应 SHA。现阶段这些图像验收全部未检查。
