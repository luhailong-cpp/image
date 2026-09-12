# 场景别名同步与预览重合成

当前：15 张背景别名已暂存并完成视觉验收；3 张预览已按旧人物源重合成且布局通过，等待并行主角 RGB 去边的最终源哈希后重建。正式图片尚未发布。

## 逐文件决定

|正式路径|操作|状态|
|---|---|---|
|qdao_chibi_game_pack_v4/main-city_2560x1080.png|adopt_accepted_scene|staged_visual_passed_not_published|
|q_daoist_scene_bg_2560x1080.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/prepared/UI/Ugui/Native/scene_background.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/prepared/World/Tianyong/Backgrounds/tianyong_city_main_64x27_v1.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/sanctuary_background.png|adopt_accepted_scene|staged_visual_passed_not_published|
|qdao_ui_redesign_v5/05_battle_scene_2560x1080.png|adopt_accepted_scene|staged_visual_passed_not_published|
|qdao_battle_arena_forest_bridge_2560x1080_v1.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/prepared/UI/Ugui/Battle/Backgrounds/qdao_battle_arena_cloud_terrace_2560x1080_v1.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/battle_background.png|adopt_accepted_scene|staged_visual_passed_not_published|
|qdao_ui_redesign_v5/06_battle_entry_loading_2560x1080.png|adopt_accepted_scene|staged_visual_passed_not_published|
|qdao_battle_entry_loading_2560x1080_v2.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/prepared/UI/Ugui/Battle/Backgrounds/qdao_battle_entry_loading_2560x1080_v1.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/battle_loading.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/additional/login_background.png|adopt_accepted_scene|staged_visual_passed_not_published|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/login_background.png|adopt_accepted_scene|staged_visual_passed_not_published|
|qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png|recompose_existing_layers|waiting_final_hero_hash|
|qdao_ui_redesign_v5/source/04_main_city_hud.png|recompose_existing_layers|waiting_final_hero_hash|
|qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png|recompose_existing_layers|waiting_final_hero_hash|

## 合同与证据

- 18 张均保持 2560 × 1080 RGB；15 张背景与已验收 runtime 来源逐字节一致。
- 人物原锚点 (1240, 680)、160 × 160 缩放、top-left (1160, 529) 保持；HUD 三按钮图层、标签、位置和遮罩保持。
- 162 项暂存检查通过。123 个受保护文件未变，含全部冻结 v10 contracts、五份云层、功能 dim 遮罩、旧主城归档和原生参考图。
- 本任务独立 current-inputs 快照；不改 v10 冻结 contracts，不运行全量构建，不接客户端。
- 本次只发布现行来源到旧正式路径；旧 source/05、source/06、raw/reference 和历史客户端错误记录保留。
- 仅追加/更新五份当前元数据：v4 manifest、v5 04/05/06 manifest、HUD placement、prepared 清单的 repository-only 子记录、新 additional/login_background.current.json。01/03 和其 prelogin_refinement 字段由主任务负责。

证据：before-index.json、current-inputs.json、staged-validation.json、visual-review-pre-hero-refresh.json、per-file-decisions.json。最终发布后将补齐 publication.json、visual-approval.json、final-verification.json。

此记录不是全库视觉精修完成声明；没有执行客户端或引擎验收。
