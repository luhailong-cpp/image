# 墨鸢游侠：八方向自然行走候选

此目录记录第 27 号角色的实绘修订及统一 v3 导出。角色保持原有道家 Q 版身份、深灰青衣、长发和随身小物，不增加幻想光效。

- 64 个行走来源格：37 格用内置 image_gen 重新绘制，27 格原样保留。NE03 原格逐像素保留；S 仅替换 04、08。
- 原来的 8 个独立 idle 来源和人物头像来源保留。
- 八方向均按解剖 RIGHT contact 为 01、LEFT contact 为 05；本次不旋转、不镜像。SW 的判断记录在 `final-phase-plan.json`，依据腰袋一侧的近髋到裤腿、鞋子的连续关系。
- 所有格只做整格分辨率统一、标准背景清理、统一比例和整数位置对齐。未使用逐帧包围盒缩放、局部拉伸或补间造动作。
- 新 S 原图是生成器输出的 RGBA。选用下排两个完整格；原图不改动。归一化后仅清除 alpha 1–3 的透明背景噪点，全部 RGB 和 alpha > 3 逐字节保持不变。透明噪点曾触发 source_edge_touch，初次失败记录保留在 `first-final-attempt-before-alpha-cleanup`，没有放宽门槛。
- 固定 common scale 为 0.997624703087886，component padding 为 0；边缘去紫仅用既有 despill radius 4。

关键记录：

- `final-source-reconstruction.json`：独立重建 64/64 来源格通过，含透明噪点清理规则。
- `final-unified-provenance.json`：八方向源图及 SHA、原 idle/portrait 来源、处理参数。
- `final-phase-plan.json`：左右脚相位核验。
- `six-direction-gait/S/final-sheet.assembly.json`：本次补齐的两帧完整提示词、生成器原文件、整格切分、清理统计和保留帧证据。
- `candidate-stable-body/27_ink_kite_ranger`：输出候选（相对上两级的根目录）。

最终素材仍须 root 对八方向 512 画布联系图进行视觉验收；本子任务不发布、不将视觉审核标记为 approved。

已通过严格数值 QC 与独立 verify（64 walk / 8 idle / 89 media）。最终 manifest SHA：`ff24d843c121ea51ad76ffe24d48d2b3e44be082359aae62a4b81e4ac28aba2f`。八方向联系图和 `eight-directions.gif` 已生成。详细结果见 `candidate-handoff.json`。
