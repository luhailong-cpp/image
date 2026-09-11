# 27 墨鸢：本轮交付已完成

立绘、八向各四帧、八条 strip、八个 GIF 与两张 4×4 表共 51 个媒体已完成当前 SHA 的视觉和机械验收。客户端未导入。

当前处理输入在 sources/portrait_raw.png 与 sources/walk_DIRECTION_2x2.png，共9个输入；其中部分2×2是分别生成的姿态原画排版，不能计作一张原生生图。实际原生图及逐帧native尺寸、source_box、缩放和提示词见generation_lineage与sources/frame-originals/。1024/512/2048为处理后的导出尺寸。sources/cardinal_assembled.png 与 diagonal_assembled.png 是新帧拼接的兼容表，不是原生生图。

当前重建入口为本轮 qdao_cutout_edge_repair_20260911/27/tools/process_new_batch.py：先输出修复目录暂存，复核当前 SHA，再由同目录 publish_approved_batch.py 受保护发布。旧 assemble_directions.py、supplement_manifest.py 与旧流水线属于历史流程，不能不经复核覆盖当前成品。旧 source/ 内 raw 和 sources/ 内 rejected 候选保留为历史资料，不是当前原画。

验收：processing/final-visual-approval.json、processing/artifact-validation.json、qc.json。来源：processing/sources.json 和逐方向处理记录。
