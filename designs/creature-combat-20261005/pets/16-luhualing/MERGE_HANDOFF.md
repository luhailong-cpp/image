# 露华灵接手说明

当前仍在生成和验收，禁止把本目录当作68帧已完成包。

仅本角色目录可写；公共/旧图只读；禁止读取客户端与兄弟仓库，不提交、推送或切分支。

1. 先看 STATUS.md、POSES.md、manifest.json、validation.json。
2. 复用已审正确帧；缺帧继续内置image_gen，逐帧独立调用，附原生E/W身份和人物属性样板。实际模型/质量未知用null。
3. 原生图落 `.work/<action>/<direction>/NN.png`，文字证据落records，prompt落prompts。每个新候选先保留独立文字记录。
4. `tools/export_frames.py` 按统一坐标导出已记录原生；`tools/build_delivery.py` 更新清单、SHA和预览。脚本不创造动作，不补缺帧。
5. 修换手、额外肢体、方向跳变、原生裁边；完成后实际看全帧和六组正常/慢放连播，记录结论。客户端状态始终如实。
6. 正式图及引用核实后清理本目录中间图片，保留来源文字记录。跨窗口身份参考不可删除。
