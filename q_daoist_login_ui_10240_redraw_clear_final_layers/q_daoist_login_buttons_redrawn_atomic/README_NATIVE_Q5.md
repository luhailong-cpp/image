# Unity UGUI 对应图标保留目录

2026-09-21 按用户要求，仅保留当前 Unity UGUI 客户端有对应画面的素材。

- `qstyle_redrawn_600x600/character_artifacts_redrawn_24_600x600/`：24 张独立物品图标。
- `qstyle_redrawn_600x600/west_eight_immortals_redrawn_100_600x600/`：100 张独立物品图标。
- 对应客户端路径：`mmorpg-client/Assets/Resources/UI/qdao_v3/icons_weapon/<同名文件>.png`。

保留图为 600×600；客户端对应图为 256×256，存在缩放和细微像素差异，不声明逐字节相同。124 张均有同名、画面对应的客户端版本；这不表示每个图标都在某个当前页面实际显示。

本次删除与当前客户端画面不一致的 23 张旧控件/徽标 PNG、对应 23 份嵌入 PNG 的 SVG，以及 3 份旧控件清单。4 个 FairyGUI 图集文件在本次操作前已由用户删除；当前项目采用 Unity UGUI，不再保留 FairyGUI 图集交付。

历史构建/同步脚本中可能仍有已删除控件或图集路径；这些引用不构成本次保留依据，不应直接运行旧脚本重建已经弃用的资源。本次未修改客户端文件。

[本次清理记录](../../docs/ugui-source-cleanup-20260921.md) · [逐文件哈希与客户端比对](../../docs/ugui-source-cleanup-20260921.json)
