# 场景别名同步与主城／选服预览派生

已完成：32 张现行图片更新，2 张纯控件层保持原字节。共核验 34 个现行路径，全部保留修改前备份、输入来源哈希、逐文件合同与绑定输出哈希的视觉批准。此记录仅覆盖本子工作，不宣称全库精修已完成。

另已补齐 prepared/hero.png：与最终 1024 RGBA 主角源逐字节一致，原 alpha 完全保持，旧准备图备份及当前来源见 hero-prepared/publication.json。

15 张背景别名采用已验收的道家 Q 版节庆场景 runtime；3 张主城预览沿用原 HUD、文字和人物脚点，以去边后的当前主角源重合成。选服另核验 15 项：13 张随同一主角源更新、2 张纯控件层原样；选服保留原背景及现行 SVG 几何。

## 逐文件决定

|现行路径|决定|发布证据|
|---|---|---|
|qdao_chibi_game_pack_v4/main-city_2560x1080.png|adopt_accepted_scene|publication.json|
|q_daoist_scene_bg_2560x1080.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/Native/scene_background.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/prepared/World/Tianyong/Backgrounds/tianyong_city_main_64x27_v1.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/sanctuary_background.png|adopt_accepted_scene|publication.json|
|qdao_ui_redesign_v5/05_battle_scene_2560x1080.png|adopt_accepted_scene|publication.json|
|qdao_battle_arena_forest_bridge_2560x1080_v1.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/Battle/Backgrounds/qdao_battle_arena_cloud_terrace_2560x1080_v1.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/battle_background.png|adopt_accepted_scene|publication.json|
|qdao_ui_redesign_v5/06_battle_entry_loading_2560x1080.png|adopt_accepted_scene|publication.json|
|qdao_battle_entry_loading_2560x1080_v2.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/Battle/Backgrounds/qdao_battle_entry_loading_2560x1080_v1.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/battle_loading.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/additional/login_background.png|adopt_accepted_scene|publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/login_background.png|adopt_accepted_scene|publication.json|
|qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png|recompose_existing_layers|publication.json|
|qdao_ui_redesign_v5/source/04_main_city_hud.png|recompose_existing_layers|publication.json|
|qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png|recompose_existing_layers|publication.json|
|q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_background_ui_uncropped_final_5120x2160.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_buttons_uncropped_final_5120x2160.png|retain_unchanged_control_layer|server/publication.json|
|q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_ui_uncropped_final_recomposed_5120x2160.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|q_daoist_login_ui_lidazui_headband_v2_5120x2160.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|q_daoist_login_ui_redrawn_transparent_5120x2160.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_background_ui_uncropped_final_10240x4320.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_buttons_uncropped_final_10240x4320.png|retain_unchanged_control_layer|server/publication.json|
|q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_ui_uncropped_final_recomposed_10240x4320.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|q_daoist_login_clear_2560x1080.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|q_daoist_login_clear_lidazui_headband_2560x1080.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|ugui_qdao_headband_2560x1080.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|ugui_qdao_headband_native_2560x1080.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|qdao_ui_redesign_v5/source/02_server_select.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|qdao_ui_redesign_v5/02_server_select_2560x1080.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/Native/screen_art_headband.png|recompose_from_same_scene_and_current_hero|server/publication.json|
|client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/hero.png|sync_final_hero_source|hero-prepared/publication.json|

## 来源和合同

- 场景 18 张均保持 2560 × 1080 RGB；15 张别名与对应 runtime 原字节一致。新原画没有被宣称为原生 2560 输出。
- v5 05/06 manifest 的 source 已转向 qdao_festival_scenes_20260910/battle_forest_bridge/scene-native.png 与 battle_entry/scene-native.png，保留 source_history 和旧 PNG；记录 sourceCropBox 与 LANCZOS 派生。
- 主角源最终 SHA256：de0c3e6d71d7c3dbbfed313e7971b2b8220e27d3e79aafa617b225d3e322706d。主城脚点仍为 (1240, 680)，160 × 160 显示、top-left (1160, 529)；选服矩形仍为 (2042, 30, 310, 310)，各大图按原比例缩放。
- 选服保留背景快照 server/current-inputs/retained_server_city.png，SHA256 24ef86977dddd12ca7c509bc783f83c8c97c61efb878424bae73bef9ce30d8b4；因此不会把本轮的新 v4 主城背景意外带入选服。
- 选服 8 个 RGBA 图层/别名 alpha 逐像素相等，原主角矩形外像素不变。旧 prepared/screen_art_headband.png 曾落后于当前 v10，本次同步为现行 UI 加新主角，不能把该旧别名的全画面变化误报为仅主角变化。
- 123 个保护文件保持：冻结 v10 contracts、五云层、统一黑色 alpha 178 dim、41 张旧主城归档、旧 raw/native/reference、HUD 图层和脚点合同。新主角 RGB 由并行任务先发布，本子工作只更新当前输入快照。
- HUD 中文、图层、按钮位置与无字控件保持；未改客户端、01/03、inventory、monitor-state 或全局交接文档。

## 验证

- 场景暂存 162 项通过，正式 18 图/18 备份/123 保护文件最终通过；快照重建 18 张与正式输出 SHA256 全部一致。
- 选服 43 项暂存检查通过，旧配方先复现已有输出再替换主角；最终 15 项路径/字节/尺寸检查通过，8 RGBA alpha 保持。
- 已实看四类场景、主城/HUD 前后、脚点细节、选服前后和主角原生细节。visual-approval.json 与 server/visual-approval.json 均绑定本轮输出哈希。
- python qdao_ui_redesign_v5/export_ui.py --check 在全部发布后六页通过，同时验证现有云层与兼容映射。
- 三个旧全量入口已加写入前 guard：export_ui.py、build_transition.py、v4/build_pack.py。自动审批拒绝实际运行旧全量入口来测试拦截，因为其可能覆盖生产图；已改为只读 AST 检查，未执行旧导出函数。详见 legacy-entrypoint-guards.json。

## 复现与验证命令

```powershell
python qdao_festival_refinement_20260910/scenes-sync/build_scene_sync.py verify
python qdao_festival_refinement_20260910/scenes-sync/build_scene_sync.py reproduce
python qdao_festival_refinement_20260910/scenes-sync/server/publish_server.py verify
python qdao_ui_redesign_v5/export_ui.py --check
```

reproduce 仅在 scenes-sync/reproduced 写文件；读取本任务 current-inputs 快照并比较正式哈希。选服复现使用当前电脑 Node 和 Sharp：

```powershell
node qdao_festival_refinement_20260910/scenes-sync/server/compose_server.mjs <installed-sharp-package-path>
```

该命令仅重建 server/staged 与验收图，使用 server/plan.json 的新旧主角、保留背景与 SVG 快照，不改正式文件或冻结 contracts。发布为单次操作，后续先 review 新输入和哈希，不用旧全量导出恢复历史原画。

当前元数据：v4 manifest、v5 02/04/05/06 条目、HUD placement、server manifest_native_q5、prepared 的仓库刷新子记录、additional/login_background.current.json。旧客户端状态、失败记录、client hash 和旧 generation provenance 保留；没有新的引擎或在线功能验收声明。

最终合并逐文件检查：34 个正式路径和 34 份修改前备份全部匹配清单哈希／画布／模式，0 错误；32 更新、2 原样。
