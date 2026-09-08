# 五行奇谈 · Q 版游戏美术

本仓库保存“五行奇谈”的道家 Q 版界面、场景和人物素材。新增美术沿用青绿山水、玉色屋瓦、暖金装饰、太极与葫芦元素。

## 给接手的 Codex

绘图模型与质量偏好见根目录 [AGENTS.md](AGENTS.md)。换电脑时将该文件随项目一并同步，并在新环境确认生图工具与账号权限可用。

**开新窗口继续制作时，先阅读 [五行奇谈后续交接](docs/WUXING_QITAN_HANDOFF.md)**，其中列出最终交付、验收记录与客户端后续步骤。

需要在另一台电脑安装或补齐工具时，先阅读 [AI 设计工具安装与交接](docs/AI_DESIGN_TOOLS_SETUP.md)。文档列出 9 个 Skills、4 个 MCP、固定版本、安装命令、必要路径适配和验证步骤；安装程序仍需在当前用户环境执行。

制作新素材前，阅读 [主城与人物美术定调](docs/QDAO_ART_DIRECTION.md)，查看指定参考图、版本记录与图旁提示词。需要使用标准宽屏背景、透明人物或重建导出时，阅读 [v4 素材包说明](qdao_chibi_game_pack_v4/README.md)。本轮按用户授权更新旧资源路径并保持像素尺寸，最终映射和验收记录见全库交接；不对未知客户端工程执行接线。

## 客户端主城地图归档

2026-09-08：[天墉城 6×6 主城地图](tianyong_city_6x6/README.md)已从客户端同步，包含 [6144×6144 完整母图](tianyong_city_6x6/Previews/tianyong_city_master_6144.png)、[2048 预览](tianyong_city_6x6/Previews/tianyong_city_master_preview_2048.png)、36 张正式切图、来源图与切图清单。此处归档的是现有客户端素材；同步来源和文件校验见包内记录。

## 全库美术更新：v6

按 `60134a6` 的369个视觉文件逐项遍历：124枚物件图标、50张旧切片、旧原子控件和12张选服画面／分层全部更新；22个职业人物与32帧八向动作重绘，旧道童路径统一为新版形象；六个缺失徽标、战斗入场与纯云层补齐，四只宠物另交付透明静态图。原路径和像素尺寸保持不变。

[全部交付入口](qdao_asset_refresh_v6/README.md) · [全库验证](qdao_asset_refresh_v6/validation.json) · [清理记录](qdao_asset_refresh_v6/cleanup.json)。过程母图、切格副本和旧预览按记录删除，正式素材、已确认参考、提示词与构建来源保留。本轮未接入实际客户端。

## 最新界面重设计：v5

2026-09-06：正式游戏名确定为“五行奇谈”；重做登录、选服、选角、主城 HUD、森林石桥战斗背景和通用控件，登录与选角统一使用灵秀 Q 版九尾狐。入口见 [v5 UI 交付说明](qdao_ui_redesign_v5/README.md)。

| 页面 | 视觉稿 |
|---|---|
| 登录 | [01_login_2560x1080.png](qdao_ui_redesign_v5/01_login_2560x1080.png) |
| 选择服务器 | [02_server_select_2560x1080.png](qdao_ui_redesign_v5/02_server_select_2560x1080.png) |
| 选择角色 | [03_character_select_2560x1080.png](qdao_ui_redesign_v5/03_character_select_2560x1080.png) |
| 主城 HUD | [04_main_city_hud_2560x1080.png](qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png) |
| 森林石桥战斗背景 | [05_battle_scene_2560x1080.png](qdao_ui_redesign_v5/05_battle_scene_2560x1080.png) |
| 战斗入场与纯云气 | [过场与替换关系](qdao_ui_redesign_v5/transition_manifest.json) |
| 九尾狐灵玥 | [独立设定图与命名](qdao_ui_redesign_v5/pet/README.md) |
| 通用 UI 控件 | [组件资源与状态说明](qdao_ui_redesign_v5/components/README.md) |
| 主城透明 HUD 图层 | [无字皮肤、完整 HUD 与排布记录](qdao_ui_redesign_v5/hud/README.md) |

接手实现先读 [UI 规范](qdao_ui_redesign_v5/UI_SPEC.md)，文案以 [中文 JSON](qdao_ui_redesign_v5/copy.zh-CN.json) 为准，动态文字由客户端原生绘制。游戏名已经确认；区服、角色和槽位仍为演示数据。本轮共有六张标准视觉稿与39个SVG、39个PNG通用控件。主城 HUD 用原生 SVG 在 v4 场景预览上重做“战斗”“观战”“角色”三个入口，提供独立透明图层；战斗场景为静态背景。未接入 Unity、FairyGUI、登录/区服或战斗系统。原生尺寸与标准导出情况见包内清单。

## 游戏素材包：v4

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

## 历史宠物探索

保留 [三只宠物与命名说明](qdao_chibi_pets_v1/README.md)：葫芦灵狐 **葫团团**、符箓虎崽 **符小虎**、云游小仙鹤 **云啾啾**。每只包含已确认概念图、独立透明静态素材、完整提示词和制作记录。v5 登录与选角使用九尾狐，早期宠物的原设定图保留。
