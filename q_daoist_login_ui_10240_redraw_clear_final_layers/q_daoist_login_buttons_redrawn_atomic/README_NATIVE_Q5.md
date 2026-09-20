# 五行奇谈 · 原子 UI 新版原尺寸资产

本目录原有 11 个控件和徽标母图已按原像素尺寸原路径重做；旧清单中缺失的 10 枚 420 × 420 圆徽标已补齐。`icon_leaf.png` 是桃灵兼容别名。所有 PNG 均为真 RGBA。

详见 [逐件清单](manifest_native_q5.json)、[十徽标清单](manifest_ai_qstyle_badges.json) 与 [完整重建/拆层/九宫格说明](../../exact_qdao_slices/README.md)。原生 SVG 源在 `svg_q5/`，当前构建入口见 [v10 重建流程](../../qdao_ui_style_recut_v10/README.md#确定性重建)，旧 `build_native_q5.mjs` 已禁止写回历史皮肤；当前原画、哈希与验收以 v10 为准。

母图文件保留 `ai_qstyle_badges_sheet_chroma.png` 旧名和 1774 × 887 尺寸，背景已经改为真透明，10 个单元的原坐标未变。此文件由原生 SVG 构建，已不再是 AI 色键过程图。

子目录中的物件素材与相关图集由独立构建链管理，本批没有改动。

## 2026-09-20 暂存去重

正式控件、124 张图标及 FairyGUI 图集全部保留。对应 v10 暂存中的 46 个同字节 PNG/SVG 已移除；读取时按哈希引用正式来源，需要实体副本时使用恢复工具。图集已在隔离输出重建并核对为同字节，仍按正式交付合同保留。详见 [清理与恢复记录](../../docs/ui-cleanup-20260920/README.md)。
