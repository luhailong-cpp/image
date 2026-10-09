# 06 仙岛日景地图制作中

内部资产 ID：`penglai_day`。仅在本目录继续制作，旧来源只读。

目标为65536×65536、16×16共256张4096×4096。目前有 **17张完整像素候选**，尚缺239张完整像素图块。正式验收0张；整城和客户端验收尚未完成。

## 当前图块

| 图块 | 当前图片 | 检查状态 |
|---|---|---|
| r08_c12 | [4096×4096 PNG](tiles/current/region-v7/r08_c12-step1.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r09_c10 | [4096×4096 PNG](tiles/current/region-v6/r09_c10-candidate.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r09_c11 | [4096×4096 PNG](tiles/current/region-v6/r09_c11-candidate.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r09_c12 | [4096×4096 PNG](tiles/current/region-v7/r09_c12-step2.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r09_c13 | [4096×4096 PNG](tiles/current/region-v3/r09_c13-candidate.png) | 完整像素，接缝验收处理中 |
| r09_c14 | [4096×4096 PNG](tiles/current/region-v5/r09_c14-candidate.png) | 完整像素，接缝验收处理中 |
| r09_c15 | [4096×4096 PNG](tiles/current/region-v7/r09_c15-step4.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r10_c10 | [4096×4096 PNG](tiles/current/region-v7/r10_c10-step6.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r10_c11 | [4096×4096 PNG](tiles/current/region-v6/r10_c11-candidate.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r10_c12 | [4096×4096 PNG](tiles/current/region-v4/r10_c12-candidate.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r10_c13 | [4096×4096 PNG](r11_c13/repairs/north/joint-v3/r10_c13-candidate.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r10_c14 | [4096×4096 PNG](tiles/current/region-v7/r10_c14-step5.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r10_c15 | [4096×4096 PNG](tiles/current/region-v7/r10_c15-step9.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r11_c10 | [4096×4096 PNG](tiles/current/region-v7/r11_c10-step7.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r11_c13 | [4096×4096 PNG](r11_c13/repairs/north/joint-v3/r11_c13-candidate.png) | 局部图像及接缝已复查；其余相邻块待完成 |
| r11_c14 | [4096×4096 PNG](r11_c14/tiles/r11_c14-candidate.png) | 完整像素，接缝验收处理中 |
| r11_c15 | [4096×4096 PNG](tiles/current/region-v7/r11_c15-step8.png) | 局部图像及接缝已复查；其余相邻块待完成 |

r09_c13 已合并内部修缝、两处AI木纹修补及c12共享边，轮廓微阶已修复。实际像素来源、早期配准和色彩场保留完整记录，不将拼合图标成单次原生4K。

## 正在补齐

- r08_c11：9/16张原生细节片；native_details。
- r08_c12：16/16张原生细节片；complete_pixel_candidate_pending_qa。
- r09_c14：16/16张原生细节片；complete_pixel_candidate_pending_qa。
- r09_c15：16/16张原生细节片；local_candidate_complete_global_integration_pending。
- r10_c10：16/16张原生细节片；local_native_qa_complete_shared_mask_proposal_ready。
- r10_c11：16/16张原生细节片；internal_qa_completed_shared_north_east_pending。
- r10_c12：16/16张原生细节片；complete_pixel_candidate_pending_qa。
- r10_c13：16/16张原生细节片；complete_native_pixel_candidate_pending_seam_qa。
- r10_c14：16/16张原生细节片；complete_pixel_candidate_pending_qa。
- r10_c15：16/16张原生细节片；ready_for_root_integration。
- r11_c10：16/16张原生细节片；local_native_qa_complete_handoff_ready。
- r11_c11：3/16张原生细节片；native_details。
- r11_c13：16/16张原生细节片；local_candidate_complete_north_shared_review_passed。
- r11_c14：16/16张原生细节片；complete_pixel_candidate_pending_qa。
- r11_c15：16/16张原生细节片；local_internal_and_north_complete_ready_for_root_integration。

## 文件与检查入口

- [当前区域预览](current-region-preview.png) / [全城覆盖位置](coverage-preview.png)
- [256块清单](tile-manifest.json) / [逐图来源索引](asset-index.json)
- [进度](progress.json) / [继续制作位置](current-work.json)
- [r09整合复查](qa/integrated-r09/root-review.json)
- [导航与日景/节庆约束](evidence/structure-navigation-review.json)

## 生图与保留规则

使用宿主内置image_gen。所有生图和AI编辑均有独立记录；配置目标与实际参数分开，工具未披露的型号和质量为未确认。实际提示词、参考图角色、工具来源、原生尺寸和SHA可从逐图索引查询。结构稿及低清布局仅用于参考，未作为高清成品放大。

当前用于邻块衔接、尚未导出最终成品的唯一在制稿及修补依赖暂留。成品与引用核验完成后，按用户规则清除拒稿、回退图和中间图，保留来源文字证据。

刷新本索引使用 `refresh_index.py`。
