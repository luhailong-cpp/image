# v9 04 / 14 连续色边修复（待正式发布）

两张 4096 × 4096 RGBA 已完成独立暂存及视觉验收，正式路径未覆盖。

- 04：沿已确认甲缝、袖口及邻接金杖从顶环至底端清边，共 61,593 个 RGB 像素。
- 14：沿白发外轮廓、飞发环与两侧发髻完整清边，共 37,336 个 RGB 像素。
- 全部 Alpha、区域外像素、未选像素不变；正常紫眼睛和流苏设保护区并逐字节核对。
- 使用邻近正常前景色相并保留原明暗；7 张原生 2× 浅深底前后页及整体区域验收未见连续粉紫线，细暗描线、玉石和金色保留。

最终入口：`stage_expanded_edges.py`。`stage_local_edges.py` 为首轮局部方法留档，最终结果以 `review.json` 与 `staged/` 为准。`review-04-*`、`review-14-*` 为首轮证据；`expanded-review-*` 是最终验收页。

发布前核对 `review.json` 的 source_sha256，先备份再复制 staged_path 到 path；随后同步两张人物的 manifest、来源记录与 1024 预备图。

![完整人物前后](full-portrait-before-after.jpg)
