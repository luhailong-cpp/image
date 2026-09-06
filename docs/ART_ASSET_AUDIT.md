# 全库美术资产审计

审计基线：`60134a6`，2026-09-06。此报告是制作前逐资源基线，后续完成状态以本轮替换清单和验证记录为准。审计未更改或删除图片。

共 **369** 个已跟踪视觉文件：**332** 个位图、**37** 个 SVG。包含逐文件原像素尺寸、透明信息、Git blob、SHA-256、引用和处理方法的机器清单见 [ART_ASSET_AUDIT.json](ART_ASSET_AUDIT.json)。

## 已实看与结论

已实看根目录全部20张、人物包全部24张、物件全部124枚、切片全部50张、八方向各首帧、旧6张登录分层和12张原子控件，以及新版登录、选角、灵玥、三只宠物。

- 124枚物件的蓝金写实质感与新版玉绿米白Q版不一致。部分法器带有邻格金色弧线污染，应全部重绘并保持600×600 RGBA和名称。
- 24张旧人物及8向动作偏细长比例。保留职业、武器、方向与帧序，按新版大头短身道童定调重绘；人物包4096×4096，动作1254×1254。
- 50张exact切片有徽标/状态点烘焙、残背景与裁边，需要全部重建。卡片、底层、徽标、状态点、笔划按原像素尺寸分别输出。
- 旧云气图带旧道童，不是可直接复用的纯云层。战斗入場与云气应替换；纯暗色遮罩属于代码效果，可明确复用或重建。
- 已完成v4/v5画面、透明新道童、灵玥与三只Q宠物定调保留；动画与透明宠物需要额外生产导出。

## 家族与执行顺序

|家族|原文件数|执行|
|---|---:|---|
|`movement_32`|32|`redraw_same_path`|
|`exact_slices_50`|50|`redraw_same_path`|
|`diagnostic_screenshots`|2|`delete_after_replacement`|
|`hero_variants_7`|7|`redraw_same_path`|
|`portraits_24`|24|`redraw_same_path`|
|`approved_v4_reference`|6|`preserve`|
|`legacy_screen_7`|6|`redraw_same_path`|
|`atomic_ui_12`|12|`redraw_same_path`|
|`objects_124`|124|`redraw_same_path`|
|`runtime_atlas`|1|`rebuild_same_layout`|
|`old_atlas_preview`|1|`delete_after_replacement`|
|`old_source_sheets_5`|5|`delete_after_replacement`|
|`login_layers_6`|6|`redraw_same_path`|
|`legacy_scene`|1|`redraw_same_path`|
|`battle_background`|1|`redraw_same_path`|
|`battle_overlay`|1|`reuse_or_rebuild_code`|
|`battle_clouds`|1|`redraw_same_path`|
|`battle_entry`|1|`redraw_same_path`|
|`approved_pet_concepts`|3|`preserve`|
|`approved_v5`|85|`preserve`|

旧运行时物件不能当过程图删除。按JSON中`assets[].path/size/replacement_recipe`逐一替换原路径；如果采用新路径，必须记录可用映射并保留兼容导出。尺寸是像素画布，不能把AI原生尺寸与放大导出混为一谈。

## 目录尺寸清单

|目录|位图 / SVG|原像素尺寸分布|
|---|---:|---|
|`character_move_8dir`|32 / 0|1254x1254 ×32|
|`exact_qdao_slices`|50 / 0|1250x180 ×1，240x65 ×5，250x61 ×1，473x100 ×16，116x100 ×8，47x46 ×8，142x35 ×8，260x76 ×1，300x66 ×1，344x66 ×1|
|`movement_diagnostics`|2 / 0|868x517 ×1，1302x776 ×1|
|`.`|20 / 0|4096x4096 ×7，1254x1254 ×1，2560x1080 ×9，5120x2160 ×2，1930x815 ×1|
|`q_daoist_character_pack_4096`|24 / 0|4096x4096 ×24|
|`q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic`|12 / 0|1774x887 ×1，6679x413 ×1，1419x380 ×2，360x360 ×1，1428x285 ×1，2364x574 ×2，2606x574 ×2，128x128 ×1，1391x441 ×1|
|`q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/character_artifacts_redrawn_24_600x600`|24 / 0|600x600 ×24|
|`q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/fairygui_atlas`|2 / 0|7912x6088 ×1，1300x1000 ×1|
|`q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/source_sheets`|5 / 0|1536x1024 ×1，1254x1254 ×3，1402x1122 ×1|
|`q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/west_eight_immortals_redrawn_100_600x600`|100 / 0|600x600 ×100|
|`q_daoist_login_ui_uncropped_highres_final_layers`|6 / 0|10240x4320 ×3，5120x2160 ×3|
|`qdao_chibi_game_pack_v4`|3 / 0|1024x1024 ×1，2560x1080 ×2|
|`qdao_chibi_game_pack_v4/source`|1 / 0|1254x1254 ×1|
|`qdao_chibi_pets_v1`|3 / 0|1254x1254 ×3|
|`qdao_ui_redesign_v5`|5 / 0|2560x1080 ×5|
|`qdao_ui_redesign_v5/components`|1 / 1|1800x2360 ×2|
|`qdao_ui_redesign_v5/components/png`|33 / 0|48x48 ×2，160x160 ×1，1080x620 ×1，120x120 ×5，360x96 ×3，1440x840 ×1，460x112 ×3，96x40 ×1，420x84 ×3，520x126 ×3，640x141 ×3，32x32 ×3，1280x79 ×1，360x114 ×3|
|`qdao_ui_redesign_v5/components/svg`|0 / 33|48x48 ×2，160x160 ×1，1080x620 ×1，120x120 ×5，360x96 ×3，1440x840 ×1，460x112 ×3，96x40 ×1，420x84 ×3，520x126 ×3，640x141 ×3，32x32 ×3，1280x79 ×1，360x114 ×3|
|`qdao_ui_redesign_v5/hud`|3 / 3|2560x1080 ×6|
|`qdao_ui_redesign_v5/pet`|1 / 0|1254x1254 ×1|
|`qdao_ui_redesign_v5/source`|5 / 0|1928x815 ×1，1932x814 ×1，1931x814 ×1，2560x1080 ×1，1930x815 ×1|

## 特别的映射约束

- FairyGUI图集为7912×6088 RGBA，124帧、每帧600×600、间距8px。用现有JSON中x/y重建，保持XML/JSON名字和坐标；清单内F:/旧绝对源路径应改为相对路径。
- 原子控件映射到v5SVG后按原大尺寸重新光栅化，不能把120px/360px PNG硬放大以冒充清晰重绘。
- 旧登录命名大图实际是选服界面。保留背景装饰层、按钮层与合成层角色，以新版选服资产重组；保留5120×2160与10240×4320两档。
- 徽标母图实际1774×887 RGB、5×2排列。两个旧清单声明的10个独立输出全部缺失，要求补420×420真透明图。`icon_leaf.png`与`icon_peach_spirit.png`语义需统一。
- `wire_qdao_v3_assets.py`实际选择22张01–22编号人物；注释的23不准确。此仓库没有真实客户端工程，不执行其目录推断写入。

## 可删过程图候选

下面仅列候选。先完成最终替换、校验引用再删除；本次审计没有删除。

- `movement_diagnostics/move_recovered.png` — Diagnostic screenshot, no runtime/build consumer. Delete image after replacement validation; preserve unrelated move_20260905_082427.log.
- `movement_diagnostics/movement_full_window.png` — Diagnostic screenshot, no runtime/build consumer. Delete image after replacement validation; preserve unrelated move_20260905_082427.log.
- `q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/fairygui_atlas/qstyle_fairygui_atlas_600_preview.jpg` — No runtime reference. Remove after final atlas rebuild; update docs if a link exists.
- `q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/source_sheets/supplement_source_001_024.png` — Delete only after all 124 replacement icons and atlas validate and old source_sheets references/manifests are retired.
- `q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/source_sheets/west_source_001_025.png` — Delete only after all 124 replacement icons and atlas validate and old source_sheets references/manifests are retired.
- `q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/source_sheets/west_source_026_050.png` — Delete only after all 124 replacement icons and atlas validate and old source_sheets references/manifests are retired.
- `q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/source_sheets/west_source_051_075.png` — Delete only after all 124 replacement icons and atlas validate and old source_sheets references/manifests are retired.
- `q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/source_sheets/west_source_076_100.png` — Delete only after all 124 replacement icons and atlas validate and old source_sheets references/manifests are retired.

不得按名字批量删除所有source/preview：`qdao_chibi_game_pack_v4/source/hero-matte.png`是透明人物构建输入；主城原图是背景构建输入；`preview-main-city_2560x1080.png`被v5HUD构建器读取；v5/source下图像由export_ui.py读取。若最终决定移除可复建预览，先改构建依赖。无关`movement_diagnostics/move_20260905_082427.log`保留。

## 保留与完成的判定

原生SVG是可复建源文件；整屏标准导出、透明切片、最终图集和最终人物均为交付资源。旧发型variant与高分辨率分层是历史交付，必须重绘或有等尺寸兼容替换，不能只因版本旧就当过程图删除。新生成中的母图、诊断表、临时裁格与验收预览在最终提取验证后可删，保留完整提示词、生成ID/尺寸/hash、处理配置和正式清单。
