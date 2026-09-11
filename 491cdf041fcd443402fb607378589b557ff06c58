# 五行奇谈 · 全文件夹美术对比

已对照 **1,471 个视觉文件**，包括正式素材、切片、来源母图、历史备份、隐藏暂存图和 SVG。已实际查看 **76 页联系表**，对主要问题放大复核；相同像素副本通过哈希关联，8 个复杂 SVG 另核对源码和同名导出。

主要偏差集中于旧 UI 控件及派生整屏；人物、宠物和物件大部分仍在同一美术家族。新属性切片方向更接近已确认稿，但局部去字纹理仍需精修。

**快照范围：**文件集合截至 2026-09-09T17:17:48.679702+00:00；期间变化的 32 个原路径复核于 2026-09-09T17:35:35.789057+00:00。其他任务仍在新增、覆盖素材，本文对每件记录被审阅的 SHA-256；快照之后的改动不自动继承结论。本次只生成审查文件，没有修改原素材。

[逐文件筛选查看](index.html) · [完整记录与哈希](results.json) · [初始来源清单](inventory.json) · [新增文件清单](supplement.json) · [变动复核](revisions.json)

## 判断基准

[用户最近提供的选角风格参考](../../designs/attribute-panels/v2-painted/reference-style.png) 为 UI 首要基准：深玉绿、米白纸面、细暖金边、局部云饰，表面安静、手绘层次柔和。人物与场景结合项目定调，保留 Q 比例、道家元素和清晰大色块。职业颜色、宠物物种体态、地图俯视用途不直接等同于风格错误。

部分带 v1/v5 名字的旧路径已被 v7 覆盖，文件名和旧文档的“保留不变”不能证明它还是当初确认的图。真正参考文件与当前交付必须分开。

## 优先修正

### 1. 旧横条 UI：母图材质和控件造型偏离

亮绿玉石流纹、凸起金色云纹端帽被反复用在按钮、页签、列表、搜索框和服务器卡片上，较参考更亮、更厚、更像同一种胶囊按钮。根源在 v7 母图及映射；重新裁切同一母图不能恢复原稿区别。

涉及 `exact_qdao_slices/`、v5 `components/` 与 `hud/`、v7 `ui/`、旧登录原子与分层、客户端 `prepared/UI/`，以及旧属性预览的复制资源。

代表：[client_ui_refresh_20260908/prepared/UI/qdao_v3/ui/tab_button_green_active_v3.png](../../client_ui_refresh_20260908/prepared/UI/qdao_v3/ui/tab_button_green_active_v3.png)、[client_ui_refresh_20260908/prepared/UI/qdao_v3/ui/search_box_with_icon_v3.png](../../client_ui_refresh_20260908/prepared/UI/qdao_v3/ui/search_box_with_icon_v3.png)、[client_ui_refresh_20260908/qa/02-server-native.png](../../client_ui_refresh_20260908/qa/02-server-native.png)。来源证据：[qdao_gpt_image2_refresh_v7/ui/prepare_assets.py](../../qdao_gpt_image2_refresh_v7/ui/prepare_assets.py)、[qdao_gpt_image2_refresh_v7/ui/source-map.json](../../qdao_gpt_image2_refresh_v7/ui/source-map.json)。

建议按主按钮、次按钮、页签、列表、输入框和卡片分别建立无字母件，再按原尺寸、透明度及九宫格约定统一派生。

### 2. 结算与 HUD：存在另一套皮肤和版本混用

[client_ui_refresh_20260908/qa/11-result-native.png](../../client_ui_refresh_20260908/qa/11-result-native.png) 当前仍为大面积深棕木纹面板；按钮已更新成绿云饰，但主面板尚未接近米白纸面与深玉标题。

[qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png](../../qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png) 与 [qdao_ui_redesign_v5/source/04_main_city_hud.png](../../qdao_ui_redesign_v5/source/04_main_city_hud.png) 是两套场景/按钮版本。需要先确定统一来源；当前 source 版仍继承亮玉流纹，确定版本后还应统一按钮材质，再重建导出。截图只证明记录中的画面，未在本轮运行实际客户端检查当前引用。

### 3. 新属性切片：方向已对，剩下局部去字质量

[designs/attribute-panels/v2-painted/unity-slices/png/button_primary.png](../../designs/attribute-panels/v2-painted/unity-slices/png/button_primary.png)、[designs/attribute-panels/v2-painted/unity-slices/png/step_plate.png](../../designs/attribute-panels/v2-painted/unity-slices/png/step_plate.png)、[designs/attribute-panels/v2-painted/unity-slices/png/tab_horizontal.png](../../designs/attribute-panels/v2-painted/unity-slices/png/tab_horizontal.png)、[designs/attribute-panels/v2-painted/unity-slices/png/tab_vertical_selected.png](../../designs/attribute-panels/v2-painted/unity-slices/png/tab_vertical_selected.png)、[designs/attribute-panels/v2-painted/unity-slices/png/title_plate.png](../../designs/attribute-panels/v2-painted/unity-slices/png/title_plate.png) 可见水平色带或矩形填补，手绘底纹连续性不足；头像框 [designs/attribute-panels/v2-painted/unity-slices/png/portrait_frame.png](../../designs/attribute-panels/v2-painted/unity-slices/png/portrait_frame.png) 仍有轻微角接残点。

建议局部恢复无字底纹、修齐边线。审查期间已看到关闭按钮背景块、宠物卡残线、灵玥头像取景、标题透明底等问题得到修复；新属性运行截图也已替换旧亮绿厚框，**这些已修复项不再列为当前待办**。

### 4. 人物与宠物：边缘质量优先，避免把正常差异当错误

[character_move_8dir/east_frame_01.png](../../character_move_8dir/east_frame_01.png)、[character_move_8dir/south_frame_01.png](../../character_move_8dir/south_frame_01.png) 放大可见品红细边；同批 32 帧应按同一边缘处理规则复核。[qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png](../../qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png) 尾毛外缘有类似残色，处理时保留本身淡紫毛色。

多数职业和宠物的身份、配色与画法可保留。审查期间 11 张正式人物被 v9 差异化角色覆盖，已另按新版本复核；人物多样化属于该版本方向，不能把成熟脸、不同身形或非玉绿职业色直接归为失败。旧 `prepared` 副本和新正式人物需注意版本对应。

宝宝旧整屏 [designs/attribute-panels/v2-painted/02-pet-ui.png](../../designs/attribute-panels/v2-painted/02-pet-ui.png) 中云啾啾是成年鹤头像，与幼鹤设定不一致；新增头像切片已改为正确幼鹤，旧整屏仅需同步头像修订。

## 可以保留的部分

- **124 个物件图标**：深玉底、金边、米白材质、云纹和红穗整体连贯。雕刻与金属光泽符合物件用途，不建议整批重画。十枚功能徽标的符号和造型也可保留，只需轻微统一翠绿底与光泽。
- **多数人物和三只幼宠**：Q 比例与手绘家族一致；少量人物的硬边光影可定向精修。v7 腰挂葫芦四向候选不能直接混入手持葫芦八向正式动作。
- **场景与天墉地图**：场景大体保持同一家族。天墉 36 切片内部一致，较参考沉重、细碎是整组美术差异，不是每张切片失败；如调整应从母图统一处理后再切。
- **技术层与过程图**：透明云气、黑遮罩、纯文字 SVG、洋红背景母图、联系表有各自用途；不因缺背景或保留色键母底而判风格错误。

## 文件夹覆盖

以下数量包含复制路径与来源，并非需要独立重绘的工作量。逐件结论见筛选页面；历史/技术图不计作“全部待重做”。

| 文件夹 | 视觉文件 | 明显偏离 | 局部需统一 |
|---|---:|---:|---:|
| `.work` | 4 | 0 | 0 |
| `[root]` | 20 | 6 | 4 |
| `character_move_8dir` | 32 | 0 | 0 |
| `client_ui_refresh_20260908` | 257 | 55 | 26 |
| `designs` | 58 | 4 | 14 |
| `exact_qdao_slices` | 100 | 50 | 50 |
| `q_daoist_character_pack_4096` | 114 | 0 | 3 |
| `q_daoist_login_ui_10240_redraw_clear_final_layers` | 171 | 16 | 30 |
| `q_daoist_login_ui_uncropped_highres_final_layers` | 9 | 4 | 2 |
| `qdao_asset_refresh_v6` | 164 | 0 | 0 |
| `qdao_character_diversity_v9` | 55 | 0 | 0 |
| `qdao_chibi_game_pack_v4` | 4 | 0 | 2 |
| `qdao_chibi_pets_v1` | 6 | 0 | 0 |
| `qdao_exposure_refinement_v8` | 22 | 0 | 0 |
| `qdao_gpt_image2_refresh_v7` | 310 | 55 | 87 |
| `qdao_ui_redesign_v5` | 104 | 40 | 42 |
| `tianyong_city_6x6` | 41 | 0 | 0 |

另已遍历但未发现本次范围内图片的顶层目录：`.agents`, `docs`, `movement_diagnostics`, `unity-download-resume`。Git 内部对象、依赖库与本报告自己的输出不计作项目美术。

## 审查范围与使用方式

- 全覆盖指列入清单的文件都有人工视觉结论、同像素关联结论或技术源码结论；不是逐像素质检认证。
- 所有独立位图均经过联系表查看，关键项另放大；没有把尺寸/哈希检查成功当作风格验收。
- 动画按帧静态看风格与边缘，本轮不等同于动画连续性、引擎交互、导航或碰撞验收。
- 同步清单提到的若干旧客户端路径仅为本库外部引用，不能据此声称已经看到其图片或当前客户端正在使用。
- 每张联系表格子显示稳定编号；在筛选页搜索编号或文件名即可看到完整路径、结论和修正方向。
