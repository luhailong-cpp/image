# 游戏地图素材

## 给接手的 Codex

2026-10-10 根据当前用户要求与在制记录恢复本交接入口。先读 [已确认风格](designs/README.md)、[统一配置](config/image-generation.json)、[逐图策略](docs/IMAGE_MODEL_POLICY.md)、[UI 视觉](qdao_ui_redesign_v5/UI_SPEC.md)，再读 [当前恢复制作指令](qdao_city_tiles_4k_20260916/builtin_q64_production/resume-production-20261010/README.md)。

当前仅主城、渔村、八仙岛三张日景；各自 production-contract.json 定义固定绘图坐标与分区。主城 16×16 个 4096 图块；渔村和岛各 14×14。世界空间尺寸尚未最终批准，不能把图像分辨率当作容量证明。5000 人静态脚点排布已通过条件试验，入口和运行验收仍未完成。当前允许继续绘图，不再全局暂停。不得回填旧图片的模型字段。
