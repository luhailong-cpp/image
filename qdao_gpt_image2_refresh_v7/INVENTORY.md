# GPT Image 2 全库重绘：基线盘点

本清单从 Git HEAD blob（不是并行修改中的工作区）冻结当前 Git 跟踪的全部视觉资产，包括历史设定图、源图、SVG、PNG、切片、原子控件和图集。所有项目均纳入 v7；没有沿用 v6 的已确认素材豁免。用户无关的 `unity-download-resume/` 未读取或修改。

- 跟踪视觉文件：**470**。
- 格式：.png 350, .svg 120。
- 字节完全相同的别名：13 组，可减少 51 个独立内容生成任务。

## 按素材家族

| 家族 | 文件数 |
|---|---:|
| movement_frames | 32 |
| legacy_exact_slices | 100 |
| hero_compat | 9 |
| profession_portraits | 22 |
| hero_master_and_export | 3 |
| legacy_screen_layers_and_compat | 15 |
| legacy_atomic_controls | 46 |
| item_icons | 124 |
| item_atlas | 1 |
| city_master_and_derivatives | 4 |
| screen_scene_master_and_derivatives | 17 |
| utility_dim_mask | 1 |
| pet_concepts_and_transparents | 8 |
| ui_components_and_overviews | 82 |
| hud_layers | 6 |

## 最少母图集合与重建关系

以下按来源去重，是可执行的母图规划，并非保证一次生成就通过的调用次数。

- 道童身份 1 组母图：重绘金发带 Q 道童，生成可透明提取的完整身体。派生根目录概念图、v4 chroma 来源、1024透明人物、9个4096兼容输出；原有 a/b/c 是同一身份的别名，不需要画不同人物。
- 22 个职业人物：每职业独立母图；保持主题、配色、武器和发型，分别输出4096×4096 RGBA。
- 八方向动作 8 张2×2母表：32帧逐一提取，1254×1254 RGBA，脚底 y=1179；需要视觉核验方向、左右手、步态和帧间身份。
- 四只宠物 4 组母图：灵玥、葫团团、符小虎、云啾啾。每只同时更新有底设定与透明输出，保持1254方图；场景中需要复用新身份参考。
- 124件物件/法器：8张母表（7×16件＋1×12件）可覆盖，继续原600×600 RGBA；建议生成更高原生尺寸母表以保证每格细节。随后按原 XML 坐标重建7912×6088图集。
- 场景/整屏 7组母图：主城、登录、选服、选角、森林石桥战斗、战斗入场、纯云气。包含所有 source/ 原图及根目录旧图；六张标准页面导出保持2560×1080，HUD页由主城＋新人物＋新UI重建。
- UI 39个语义组件：需新增 GPT Image 2 生成的框板/按钮/页签/卡片/10徽标视觉母图，可按4–6张分组母表开始。保持39套PNG＋SVG以及已有状态/九宫格合同；历史50切片、23原子输出及对应SVG、两张总览、HUD层和12张旧选服兼容层由这套新视觉重建。不能只运行旧脚本后声称它们已用新模型重绘。
- 黑色暗罩和文字层属于技术图层：重新构建，保持黑色 alpha=178、既有文案与动态文字分离。语义等同的技术像素允许不变，应在最终逐文件结果说明。

不含UI母表的视觉生成下限规划为50组：1道童＋22职业＋8动作＋4宠物＋8物件＋7场景。UI从4–6组母表开始，但最终数量以39组件覆盖、分辨率和视觉验收决定。

## 现有可用重建入口

| 脚本 | 覆盖 |
|---|---|
| `qdao_chibi_game_pack_v4/build_pack.py` | 新主城/道童来源→背景、透明道童、组合预览 |
| `qdao_asset_refresh_v6/build_hero_compat.py` | 新道童→9个4096兼容输出 |
| `q_daoist_character_pack_4096/process_portrait.py` | 职业人物抠底、对齐与4096导出 |
| `qdao_asset_refresh_v6/icons/process_batch.py` | 物件母表切格、透明清理、600导出 |
| `qdao_asset_refresh_v6/icons/build_atlas.py` | 124单件→保留坐标的图集 |
| `qdao_ui_redesign_v5/export_ui.py` | 场景source→标准画面和兼容别名 |
| `qdao_ui_redesign_v5/build_transition.py` | 入场/云气及兼容别名、技术遮罩 |
| `qdao_ui_redesign_v5/components/build.mjs` | 旧原生SVG系统，须接入新视觉后才算重绘 |
| `exact_qdao_slices/build_native_q5.mjs` | 50旧切片＋23原子PNG/SVG；需接入新UI视觉 |
| `qdao_ui_redesign_v5/hud/build.mjs` | HUD皮肤/文字/组合及主城HUD页面 |
| `q_daoist_login_ui_uncropped_highres_final_layers/native_q5/build_layers.mjs` | 旧5120/10240透明分层与根目录兼容画面 |

## 验收约束

每个文件的路径、尺寸、模式、alpha范围、基线SHA-256、类别、来源（可识别时）和构建入口见 `inventory.json`。清单同时携带控件的九宫格/内容边距元数据。

v6 `validation.json` 比对369个历史基线；当前是470个文件。v6 `verify_delivery_contracts.py` 中92个保留文件的哈希条件与本次全量重绘冲突，v7应以新清单验收，不把旧保留检查当作新任务要求。

保持原路径、像素画布和透明属性；真实AI原生分辨率另记录。背景原source有1927–1932×814–816等历史尺寸，仍须导出到原画布，不可将放大后的4096/10240称为原生模型生成。图集保持124帧名称/位置和7912×6088；动作保持1254×1254、脚底y=1179及帧序。

本盘点只创建清单和摘要，没有修改任何素材或构建脚本。
