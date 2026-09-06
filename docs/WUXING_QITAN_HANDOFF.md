# 五行奇谈：新窗口交接与剩余工作

记录日期：2026-09-06。本机素材仓库为 `E:/work/image`。其他电脑使用自己的仓库绝对路径；文内链接相对于本文件。

## 先读与当前目标

用户希望道家 Q 版游戏美术更精致，重做现有 UI、主城、人物和战斗场景，生成并命名宠物；游戏正式名称是 **五行奇谈**。最新宠物要求是类似《问道》气质的灵秀 Q 版九尾狐。用户现在转到新窗口继续，要求列清剩余任务。此前已经授权完成后提交 Git；当前交接按本地提交处理，未要求推送远端。

1. 先看本文件的“必须补齐”，再打开 [v5 说明](../qdao_ui_redesign_v5/README.md) 与 [UI 规范](../qdao_ui_redesign_v5/UI_SPEC.md)。
2. 实看 [新版登录](../qdao_ui_redesign_v5/01_login_2560x1080.png)、[选角](../qdao_ui_redesign_v5/03_character_select_2560x1080.png)、[灵玥设定](../qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox.png)，以这些文件统一形象。
3. 检查 `git status --short` 与最近提交。接手时核对本清单和实物；已经补齐的项目不重复制作。
4. 缺少工具时按 [安装说明](AI_DESIGN_TOOLS_SETUP.md) 补装，已有工具优先复用。

## 已完成，直接接着用

| 交付 | 实际位置 | 实际状态 |
|---|---|---|
| 登录页 | [01_login_2560x1080.png](../qdao_ui_redesign_v5/01_login_2560x1080.png) | 五行奇谈标题、Q 道童、灵秀九尾狐、当前服、进入游戏等；整张视觉稿 |
| 选择服务器 | [02_server_select_2560x1080.png](../qdao_ui_redesign_v5/02_server_select_2560x1080.png) | 四分类、搜索、2列4行区服、选中/推荐/维护展示；整张视觉稿 |
| 选择角色 | [03_character_select_2560x1080.png](../qdao_ui_redesign_v5/03_character_select_2560x1080.png) | 两个演示人物槽+创建空槽、道童与九尾狐、右侧信息；整张视觉稿 |
| 主城 HUD | [04_main_city_hud_2560x1080.png](../qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png) | 原有战斗/观战/角色三个按钮已重做，有独立透明皮肤、文字层和位置记录，事件未绑定 |
| 森林石桥战斗背景 | [05_battle_scene_2560x1080.png](../qdao_ui_redesign_v5/05_battle_scene_2560x1080.png) | 新绘米白石桥、左右站位区、翠玉溪流、远处道观；无人无字静态背景 |
| 通用控件 | [components/README.md](../qdao_ui_redesign_v5/components/README.md) | 33 SVG + 33透明PNG，三态按钮/页签/列表/两种卡片/搜索、框板、状态点、4圆徽标及装饰 |
| 新版静态人物 | [hero-transparent_1024.png](../qdao_chibi_game_pack_v4/hero-transparent_1024.png) | 真RGBA，单张Q道童；不是动作集 |
| 主城背景 | [main-city_2560x1080.png](../qdao_chibi_game_pack_v4/main-city_2560x1080.png) | 独立静态背景；人物排布另有预览 |
| 九尾狐灵玥 | [pet/README.md](../qdao_ui_redesign_v5/pet/README.md) | 1254×1254 RGB独立设定图，九个可辨尾尖，全身完整；暖米白底，无动画 |
| 三只早期宠物 | [宠物v1说明](../qdao_chibi_pets_v1/README.md) | 葫团团、符小虎、云啾啾，独立有底设定图与提示词；登录已换灵玥方向 |
| 工具安装交接 | [AI_DESIGN_TOOLS_SETUP.md](AI_DESIGN_TOOLS_SETUP.md) | 本机9 Skills与4 MCP已安装，固定来源和迁移命令已记录 |

本轮五张标准画面均为2560×1080。AI原生尺寸分别为登录1928×815、选服1932×814、选角1931×814、战斗1930×815；HUD为2560×1080原生代码合成。标准导出对近似宽高比进行等比重采样和微量居中裁边，未把导出尺寸冒称原生生成尺寸。实际哈希、裁边与制作入口见 [manifest.json](../qdao_ui_redesign_v5/manifest.json)。

历史提交：`f66a370` 工具文档与初版Q主城/人物；`e98972f` 标准素材包与透明道童；`b76ad1f` 三只命名宠物。本文件与v5素材随其后的交接提交保存，实际提交号用 `git log -1 --oneline` 查。

## 必须补齐：先做这两项

### A. 战斗入场／加载过场

这是旧仓库里独立存在的资产；本轮05战斗背景不能替代它。

输入：

- [旧入场图](../qdao_battle_entry_loading_2560x1080_v2.png)
- [旧云气前景](../qdao_battle_entry_clouds_fg_2560x1080_v2.png)
- [旧暗色遮罩](../qdao_battle_dim_overlay_2560x1080_v1.png)
- 上表的新人物、灵玥、主城与05战斗场景。

执行：先实看三张旧图，确认它们的构图、透明通道及用途。用内置生图重绘新版入场画面，保持64:27宽屏和当前Q道童形象，过渡到新森林石桥场景；若画面加入陪伴宠物，使用灵玥。保存新文件，保留旧资产。现有旧过场没有确认的加载条/提示文案；新增文字或百分比应先检查实际客户端需求，动态进度由代码绘制。

建议交付文件位于 `qdao_ui_redesign_v5/`：

- `source/06_battle_entry_loading.png`、完整 `.prompt.txt`、生成记录。
- `06_battle_entry_loading_2560x1080.png`。
- 对云气前景和暗色遮罩明确写“复用旧文件”或“新版替换路径”。若重做前景，导出真实RGBA；暗色遮罩可由原生代码实现。
- 补充 `export_ui.py`、`manifest.json`、README和替换映射，记录实际原生尺寸与导出处理。

验收：风格与01/03/05相符，脸型服装一致，全身或构图所需主体完整，文字清楚；场景作为过场而非战斗底图命名；前景透明区域确有Alpha；每个旧资源都有可定位的新映射或复用理由。

### B. 六枚圆形徽标

旧徽标母图共10枚，本轮只重做了太极、楼阁、莲花、山4枚。尚缺 **炼丹炉、剑、水纹、罗盘、桃灵、火焰**。

输入：[旧徽标母图](../q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/ai_qstyle_badges_sheet_chroma.png)、[旧清单](../q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/manifest_ai_qstyle_badges.json)、[新徽标与构建脚本](../qdao_ui_redesign_v5/components/build.mjs)。

执行：实看旧符号辨认含义；沿现有原生SVG图标系统补6个120×120圆徽标，玉绿底、双金框、米白/暖金图形，符号在小尺寸仍可辨。建议ID为 `round_badge_furnace`、`round_badge_sword`、`round_badge_water`、`round_badge_compass`、`round_badge_peach_spirit`、`round_badge_flame`。

验收：每枚SVG+真实透明PNG齐全、无动态文字、尺寸正确；10枚圆徽标总览风格一致；在无其他增删情况下组件总数从33更新为39，构建脚本、清单、验证记录和README数量同步。圆徽标整体等比缩放，不做九宫格拉伸。

## 若下一步要实际进游戏，还需要这些制作与接入

这部分是当前未完成的生产工作。此仓库是素材库，尚未定位并操作真正的客户端工程。先确定本轮是继续交付素材，还是连同客户端一起接入；缺少客户端位置时才向用户索取路径，不猜测或自动写入其他项目。

| 项目 | 下一步具体工作 | 完成标准 |
|---|---|---|
| 三个整屏UI拆层 | 将01/02/03拆为无字装饰底图、独立人物/宠物、标题装饰及原生控件；动态服名/等级/搜索/按钮取 [copy JSON](../qdao_ui_redesign_v5/copy.zh-CN.json) | 运行时文字可改、不可用状态可切、整图烘焙文字不与原生文字重叠；分层清单可重建视觉效果 |
| 新Q人物动作 | [character_move_8dir](../character_move_8dir/)仍为旧版8方向×4帧，本轮没有替换；以新道童为基准按实际帧序/锚点重做并检查循环 | 八向轮廓一致，脚底锚点稳定、头部比例一致、无背景残边；输出真正RGBA与帧序/时长清单 |
| 宠物可用素材 | 灵玥及三只早期宠物目前是有底设定图；需要入场景时另做透明站立素材，需要动作时再按实际需求制作 | 九尾保持九个可辨尾尖，毛边无白底/杂色，大小锚点稳定；静态不冒称动画 |
| 登录→选服→选角 | 按UI规范实现当前服传递、维护禁入、搜索与无结果、角色选择、空槽创建入口、返回保留选择 | 使用真实服务接口或明确的演示适配器验证完整流程；演示服务器/角色不能冒称生产数据 |
| 主城与战斗接入 | 导入独立背景与透明人物，按 [HUD位置](../qdao_ui_redesign_v5/hud/placement.json) 还原三个入口，连接实际战斗/观战/角色页面 | 引擎内截图、可操作链路与返回路径通过；场景未提供碰撞/导航，确有需要时单独建数据 |

`wire_qdao_v3_assets.py` 对 `<repo>/client/image` 目录关系有假设，当前工作目录下不能直接照跑；先检查并配置真实工程路径。现有艺术截图不证明 Unity 或 FairyGUI 已接入。

## 风格与数据约束

- 正式名只用 **五行奇谈**。服务器、角色、等级和三槽位是演示数据，文字真值在 `copy.zh-CN.json`；游戏名已确认与演示数据未确认是两个状态。
- 道童保持金色发带、短棕发、圆眼笑脸、米白短袍裤、玉绿金边背心、太极葫芦；沿用当前短身大头Q比例。
- 灵玥保持明确狐吻、长尖耳、杏仁金眼、白色轻盈身体、朱砂额纹、细金玉项圈与白色淡紫蓝长尾。用户用《问道》作方向参考，未给特定版本原图；以当前灵玥作为项目内部参考，保留九尾与仙气。
- 场景保持青绿山水、圆润建筑、米白石地、清澈水面、暖金饰件。战斗左右站位区保持清晰。
- 玉绿 `#176C5F/#438E78`、米白 `#FFF7DE`、暖金 `#C59645`、桃木 `#795638`。控件有独立normal/selected/disabled与文字/图标辅助状态。
- 真实存在的界面和符号逐项覆盖；素材库没有展示商城、背包、任务或战斗结算页面，这些不列为本轮已确认缺项。

## 重建、工具与验证

在仓库根目录运行：

```powershell
python qdao_ui_redesign_v5/export_ui.py --check
python qdao_ui_redesign_v5/export_ui.py
node qdao_ui_redesign_v5/components/build.mjs --sharp '<已安装node_modules>/sharp'
node qdao_ui_redesign_v5/hud/build.mjs --sharp '<已安装node_modules>/sharp'
```

`--check`只验证现有五张图及来源的尺寸和哈希；第二条重新导出，不调用AI。Python需要Pillow，SVG导出需要Node≥22和Sharp，本次Sharp为0.35.4；参考各自README查依赖和可选参数。先重建组件和HUD时，最后再导出标准画面和更新总清单。

普通图片生成使用内置 `image_gen`；现有9 Skills可复用，按任务读取imagegen、generate2dmap、generate2dsprite或原生UI相关Skill。4个MCP均已安装但disabled，未配真实凭证/未建立Figma桥接；不妨碍内置生图和本地导出。其他机器照安装MD检查并补缺，不把当前用户绝对路径原样复制过去。

当前会话的默认Windows沙箱、view_image和本地图片路径引用曾出现 `helper_unknown_error: apply deny-read ACLs`；这是环境记录，并非要求下一窗口绕过限制。下一窗口先用正常工具，若再次出现则按自己的审批机制请求正确权限，不复用不存在的会话变量/旧cell。内置生图完成后把最终文件复制进仓库，保留完整提示词；图片只留用户目录缓存不算项目交付。

最终验收：实看所有新增图；核对中文、九尾、Q人物和站位空间；PNG尺寸/Alpha/哈希及SVG解析通过；所有文档链接存在；更新剩余清单；`git diff --check`通过后只提交本任务相关文件。已有未跟踪的 `movement_diagnostics/move_20260905_082427.log` 是无关文件，应原样保留。

## 可直接贴到新窗口

> 在 E:/work/image 继续五行奇谈美术任务。先阅读 docs/WUXING_QITAN_HANDOFF.md，并实看其中列出的最新登录、选角、灵玥和战斗图。按“必须补齐”先完成新版战斗入场/加载过场及云气/遮罩映射，再补炼丹炉、剑、水纹、罗盘、桃灵、火焰六枚圆徽标。正式游戏名五行奇谈；九尾狐按灵玥及用户要求的《问道》灵秀Q方向，保持九尾，人物沿用金发带Q道童。现有五张新版视觉稿、33套控件、主城HUD、透明人物和宠物图不要重复从零制作。使用内置生图与已有原生SVG系统，保存原图、提示词、透明导出、清单和Markdown，完成视觉/文件验证后本地Git提交。先做好素材缺项；三整屏UI拆层、人物8向动作、宠物透明化和客户端接入按文档列为下一阶段，先核对实际工程需求，不宣称已完成，不修改未知客户端目录。保留无关修改，不推送远端。
