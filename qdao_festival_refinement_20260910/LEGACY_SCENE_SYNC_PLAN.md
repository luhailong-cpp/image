# 旧场景画布与派生同步计划

2026-09-12T08:12:02.001262+00:00。仅完成只读追踪与计划；图片修改 0 张，未读取/写入客户端工程。

最新 6144 主城和四张独立新场景由根任务目视确认可保留。本计划仅解决旧正式路径与派生链的一致性；01/03 登录及选角整屏由根任务负责，v11 边缘和客户端导航接入不在本子任务范围。

| 用途 | 已接受的 2560×1080 复制源（新场景 runtime 目录） | 旧目标数 |
|---|---|---:|
| main_city | 01_main_city_wide_2560x1080.png | 5 |
| forest_battle | 04_battle_forest_bridge_2560x1080.png | 4 |
| battle_entry | 05_battle_entry_2560x1080.png | 4 |
| login_background_only | 02_login_landscape_2560x1080.png | 2 |

四组共 15 个旧 RGB 目标；确切路径、当前 SHA/字节/尺寸、新来源 SHA 和 crop/scale 参数见 legacy-scene-sync-plan.json。全部来源与 runtime-manifest 声明哈希一致，全部旧目标仍是 2560×1080 RGB。

## 可以同步的正式链

1. main_city_wide → v4/main-city_2560x1080 → 根 q_daoist_scene_bg；同一图还复制到 prepared 的 Native/scene_background、World/Tianyong/Backgrounds/tianyong_city_main 与 RefreshV8/sanctuary_background。新主城/庭院共享原图有正式清单依据。
2. forest_bridge → v5/05_battle_scene_2560x1080 → 根 qdao_battle_arena_forest_bridge → prepared 的两个 battle_background 别名。
3. battle_entry → v5/06_battle_entry_loading_2560x1080 → 根 qdao_battle_entry_loading_v2 → prepared 的两个 battle_loading 别名。
4. login_landscape → additional/login_background.png → prepared/RefreshV8/login_background.png。只更新干净背景，不碰 v5 01/03 整屏。

## 需要重合成，不能直接复制背景

- v4/preview-main-city 保留当前透明人物，依据 placements.json 重合成并复核脚点 (1240,680)。
- v5/source/04_main_city_hud 和 04 标准图由 v10 合成流程重建，保留 UI、文字和 HUD 排布；不能用空场景盖掉界面。

## 云层、遮罩与原图保护

- 五份云层（1 原生＋4 标准/别名）已记录 alpha SHA。四份 2560 云层 alpha 一致：True；文件字节一致：True。应保留各自 alpha，不用不透明新场景替换，不随便重新执行可能改变量化边缘的 cloud 导出。
- qdao_battle_dim_overlay 是功能素材：RGB 0、Alpha 178，要求逐像素不变。inventory 的通用 overlay 命名规则误把它标成证据，JSON 已给出纠正。
- v5 source/05、source/06 入场，v7 main-city.raw、qdao_main_city_chibi_v1 及 additional/login_background.raw/reference 为原始生成/参考记录，保留原字节与原尺寸。新当前来源可指向节庆包并另记 superseding export，不伪造旧原图。
- tianyong_city_6x6 是明确的历史客户端归档，共 41 张 PNG，全部保留，不把新 HD 地图写进去。新 HD 包与客户端路径/导航接入由主城任务维护。

## 元数据与执行边界

- 仅拟定逐文件复制清单；必须写新的仓库内发布/来源记录。旧客户端 assets_manifest 的失败、client_sha256 和 baseline 是历史，不改成新客户端验收。
- 不直接运行 sync_assets.py、export_ui.py 或 build_transition.py 总入口，它们可能触及客户端、旧原生图导出、云层重处理和根任务的 01/03。使用本任务限定目标的同步方案。
- 本轮读取并记录目标当前文件与云层 alpha 哈希；实施前重查，避免覆盖并行修改。

计划文件检查错误：[]。尚未执行复制、重合成、图片精修或客户端验收。
