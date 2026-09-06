# 道家 Q 版游戏美术

本仓库保存道家 Q 版游戏的界面、场景和人物素材。新增美术沿用青绿山水、玉色屋瓦、暖金装饰、太极与葫芦元素。

## 给接手的 Codex

需要在另一台电脑安装或补齐工具时，先阅读 [AI 设计工具安装与交接](docs/AI_DESIGN_TOOLS_SETUP.md)。文档列出 9 个 Skills、4 个 MCP、固定版本、安装命令、必要路径适配和验证步骤；安装程序仍需在当前用户环境执行。

制作新素材前，阅读 [主城与人物美术定调](docs/QDAO_ART_DIRECTION.md)，查看指定参考图、版本记录与图旁提示词。需要使用标准宽屏背景、透明人物或重建导出时，阅读 [v4 素材包说明](qdao_chibi_game_pack_v4/README.md)。保留已经被客户端使用的旧图；新增版本后再按实际接入任务替换。

## 最新素材包：v4

2026-09-06：基于主城 v1 与人物 v3 的定调，补充可单独使用的背景和透明人物，并提供排布预览与本地重建记录。

| 素材 | 查看 | 说明 |
|---|---|---|
| 标准宽屏主城背景 | [2560 × 1080 PNG](qdao_chibi_game_pack_v4/main-city_2560x1080.png) | 由 1930 × 815 主城原图等比 cover 适配并重采样 |
| 独立透明小道童 | [1024 × 1024 RGBA PNG](qdao_chibi_game_pack_v4/hero-transparent_1024.png) | 以 v3 为参考生成洋红底来源图，经本地处理得到透明人物 |
| 主城广场人物排布 | [2560 × 1080 预览](qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png) | 用于查看人物比例和场景关系 |

完整文件、来源提示词、处理记录与重建命令见 [v4 素材包说明](qdao_chibi_game_pack_v4/README.md)。主城仍是平面背景，人物仍是单张静态素材；本次未接入 FairyGUI、Unity 或可操作地图。

## 历史定调图

| 版本 | 查看 | 制作提示词 |
|---|---|---|
| 主城 v1 | [主城 PNG](qdao_main_city_chibi_v1.png) | [提示词](qdao_main_city_chibi_v1.prompt.txt) |
| 人物 v3：更圆润的发带小道童 | [人物 PNG](q_daoist_hero_chibi_headband_v3.png) | [提示词与修订](q_daoist_hero_chibi_headband_v3.prompt.txt) |

以上原图保留不变。主城 v1 为场景定调插画；人物 v3 为浅米色背景的单人物定调稿。原生尺寸和后续素材拆分要求见 [美术定调文档](docs/QDAO_ART_DIRECTION.md)。

原登录素材说明见 [q_daoist_login_notes.md](q_daoist_login_notes.md)。

## 道家 Q 版宠物

新增 [三只宠物与命名说明](qdao_chibi_pets_v1/README.md)：葫芦灵狐 **葫团团**、符箓虎崽 **符小虎**、云游小仙鹤 **云啾啾**。每只包含独立图片、完整提示词和制作记录。
