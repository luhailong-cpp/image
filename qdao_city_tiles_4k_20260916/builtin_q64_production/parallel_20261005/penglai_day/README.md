# 06 仙岛日景地图制作中

内部资产 ID：`penglai_day`。新成果仅写入本目录，旧来源只读。

目标：65536×65536；16×16，共256张4096×4096。整城、正式验收及客户端验收均未完成。

## 当前像素与检查范围

- 已核对并复用旧 r09_c10、r09_c11、r09_c12 三张候选，SHA与handoff一致。
- 新 r09_c13 已有16张1254×1254原生细节片，按1024核心、115外围上下文拼成完整4K候选；无成品放大。
- 原始候选尚有内部色差和 c12 共边几何问题；独立修补与校正工作位于 `repairs/`，未经检查不升级正式计数。
- r10_c12 正在独立子目录连续向南扩展。
- 原生来源型号/质量由宿主管理，工具未披露；配置目标 gpt-image-2.5-sunburst/max 与实际提交/返回分别记录。

## 入口

- [逐图索引](asset-index.json)
- [进度](progress.json) / [当前工作](current-work.json)
- [当前r09_c13预览](current-preview.png) / [全城覆盖位置示意](coverage-preview.png)
- [完整像素候选](tiles/r09_c13-raw-candidate.png)（未验收，不是正式成品）
- [内部校正](repairs/internal/candidate-record.json) / [共边修补](repairs/left-edge/repair-status.json)
- [导航与日景/节庆约束](evidence/structure-navigation-review.json)

## 原生图与逐图记录

| 图 | 记录 |
|---|---|
| [p11.png](native/p11.png) | [生成记录](native/p11.png.generation.json) |
| [p12.png](native/p12.png) | [生成记录](native/p12.png.generation.json) |
| [p13.png](native/p13.png) | [生成记录](native/p13.png.generation.json) |
| [p14.png](native/p14.png) | [生成记录](native/p14.png.generation.json) |
| [p21.png](native/p21.png) | [生成记录](native/p21.png.generation.json) |
| [p22.png](native/p22.png) | [生成记录](native/p22.png.generation.json) |
| [p23.png](native/p23.png) | [生成记录](native/p23.png.generation.json) |
| [p24.png](native/p24.png) | [生成记录](native/p24.png.generation.json) |
| [p31.png](native/p31.png) | [生成记录](native/p31.png.generation.json) |
| [p32.png](native/p32.png) | [生成记录](native/p32.png.generation.json) |
| [p33.png](native/p33.png) | [生成记录](native/p33.png.generation.json) |
| [p34.png](native/p34.png) | [生成记录](native/p34.png.generation.json) |
| [p41.png](native/p41.png) | [生成记录](native/p41.png.generation.json) |
| [p42.png](native/p42.png) | [生成记录](native/p42.png.generation.json) |
| [p43.png](native/p43.png) | [生成记录](native/p43.png.generation.json) |
| [p44.png](native/p44.png) | [生成记录](native/p44.png.generation.json) |

所有提示词位于 `prompts/`；内置结果路径、哈希、参考图角色及提交参数见逐图记录。结构稿和guides仅为布局参考，不能计作高清成品。

当前在制图、修补依赖和唯一像素来源暂留；确认最终导出和当前引用完整后按用户规则清理原图、拒稿和中间图片，文字来源证据保留。
