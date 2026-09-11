# 五行奇谈 UI 重新绘制 v7

历史归档：本目录记录 v7 母图与当时的重建步骤。2026-09-11 起正式 UI 重建使用 [v10](../../qdao_ui_style_recut_v10/README.md#确定性重建)；下文旧构建命令已禁止写回历史皮肤，不能作为当前交付流程。

2026-09-07。使用宿主内置 `image_gen` 生成新的道家 Q 版 UI 皮肤和徽标母图，再按原路径、原像素尺寸和九宫格契约导出。原生输出保存在 `source`；高分辨率兼容导出不等于原生高分辨率生成。

工具未开放模型或质量参数，因此记录用户要求 `gpt-image-2` 与最高质量目标，不宣称本次强制设置了 `quality=high`。未调用外部 API。

原画元素为新 AI 绘制，SVG 包装嵌入 PNG，便携且无需外部文件。尺寸适配、边缘清理、九宫格和文字排版为确定性后处理。动态文字仍在独立文字层，由项目中文 JSON 提供真值。


本轮两张母图的 PNG 内嵌 C2PA `softwareAgent` 字段均为 `gpt-image` / `2.0`；原始工具路径、提示词和检测说明见 [生成记录](source/generation.json)。每个输出保留实际原生尺寸与衍生链，不将 10240 或其他兼容画布称作原生生成分辨率。

成品入口：[39 组件与状态](../../qdao_ui_redesign_v5/components/overview.png)、[10 徽标](../../qdao_ui_redesign_v5/components/badges_overview.png)、[旧 UI 73 件清单](../../exact_qdao_slices/manifest_native_q5.json)、[主城 HUD](../../qdao_ui_redesign_v5/hud/README.md)、[旧选服 12 分层与画面](../../q_daoist_login_ui_uncropped_highres_final_layers/README_NATIVE_Q5.md)。

本地重建顺序（使用已安装 Python/Pillow/NumPy、Node/Sharp；不联网）：

```powershell
python qdao_gpt_image2_refresh_v7/ui/prepare_assets.py
node qdao_ui_redesign_v5/components/build.mjs
node exact_qdao_slices/build_native_q5.mjs
node q_daoist_login_ui_uncropped_highres_final_layers/native_q5/build_layers.mjs
node qdao_ui_redesign_v5/hud/build.mjs
python qdao_gpt_image2_refresh_v7/ui/verify_ui.py
```

末两种画面组合需要先生成本轮主城、道童与主城人物预览。已有迁移辅助脚本 `update_builders.py` / `update_docs.py` / `harden_writes.py` 用于记录本轮构建器变更；正常重建不运行这些一次性迁移。
