# 保留15名人物：本机实际资源盘点（2026-09-21）

> **同日绘图恢复后的补充（隔离素材，不改以下canonical盘点）：** 04现有[review-set-v3](../../recovery-20260921/04-delivery-preview/revisions/review-set-v3/index.html)共128walk+8idle，112张旧PNG原字节保留、24张HD补帧；离线预览复核见[最新交接](../../recovery-20260921/04-HANDOFF-20260921.md)。06的E04/06/13旧raw已在隔离目录处理，未写canonical。原始盘点JSON和下表仍保留原时点数字，不能据此重复生成04的10个已补槽或06的3张既有raw。正式接入/发布状态没有因此提升。按用户一窗口一角色要求，后续使用[独立接手文本](../../recovery-20260921/new-window-prompts/INDEX.md)。

来源：[逐文件状态与逐方向缺槽JSON](retained-roster-inventory-detailed.json)。本次只读取当前文件，未恢复删除人物，未生成或批准任何候选。

00–03正式V13资源齐套，现存appearance通过标记及manifest/validation SHA绑定一致；本轮真实Unity离线组件/沙盒测试通过，正式联网身份全流程未验收。运行资源仍为512×512的既有V13，不计为新增高清通过。
04–06均未齐套；其余8名有原始肖像但无动作包。当前V14正式包0名。总缺1205walk + 64idle = 1269动作槽。

M/V/A依次表示manifest.json、validation.json、appearance.json是否存在；存在不等于通过。包肖像/JSON列：00–03读取正式V13，其余读取V14候选。

| 原ID | 旧walk/idle | 新增HD walk（不含重叠） | 缺walk/idle | 原肖像 | 包portrait | M/V/A | 接入状态 |
|---|---:|---:|---:|---|---|---|---|
| 00_reference_topright_boy | 128/8 | 0 | 0/0 | 有 | 有 | 有/有/有 | 正式V13既有通过；本轮真实Unity离线组件/沙盒测试通过，正式联网身份全流程未验收 |
| 01_ice_sword_girl | 128/8 | 0 | 0/0 | 有 | 有 | 有/有/有 | 正式V13既有通过；本轮真实Unity离线组件/沙盒测试通过，正式联网身份全流程未验收 |
| 02_fire_talisman_boy | 128/8 | 0 | 0/0 | 有 | 有 | 有/有/有 | 正式V13既有通过；本轮真实Unity离线组件/沙盒测试通过，正式联网身份全流程未验收 |
| 03_lotus_healer_girl | 128/8 | 0 | 0/0 | 有 | 有 | 有/有/有 | 正式V13既有通过；本轮真实Unity离线组件/沙盒测试通过，正式联网身份全流程未验收 |
| 04_mountain_guardian_boy | 104/8 | 14 | 10/0 | 有 | 缺 | 有/缺/缺 | 候选未齐套/未批准，不能发布 |
| 05_celestial_musician_girl | 52/8 | 12 | 64/0 | 有 | 缺 | 有/缺/缺 | 候选未齐套/未批准，不能发布 |
| 06_thunder_caster_boy | 16/8 | 5 | 107/0 | 有 | 缺 | 有/缺/缺 | 候选未齐套/未批准，不能发布 |
| 07_moon_shadow_assassin_girl | 0/0 | 0 | 128/8 | 有 | 缺 | 缺/缺/缺 | 候选未齐套/未批准，不能发布 |
| 08_alchemy_prodigy_boy | 0/0 | 0 | 128/8 | 有 | 缺 | 缺/缺/缺 | 候选未齐套/未批准，不能发布 |
| 09_bamboo_archer_girl | 0/0 | 0 | 128/8 | 有 | 缺 | 缺/缺/缺 | 候选未齐套/未批准，不能发布 |
| 10_crimson_spear_girl | 0/0 | 0 | 128/8 | 有 | 缺 | 缺/缺/缺 | 候选未齐套/未批准，不能发布 |
| 14_short_hair_snow_summoner_girl | 0/0 | 0 | 128/8 | 有 | 缺 | 缺/缺/缺 | 候选未齐套/未批准，不能发布 |
| 15_water_dragon_scholar_boy | 0/0 | 0 | 128/8 | 有 | 缺 | 缺/缺/缺 | 候选未齐套/未批准，不能发布 |
| 17_ghost_script_calligrapher_boy | 0/0 | 0 | 128/8 | 有 | 缺 | 缺/缺/缺 | 候选未齐套/未批准，不能发布 |
| 20_star_formation_master_girl | 0/0 | 0 | 128/8 | 有 | 缺 | 缺/缺/缺 | 候选未齐套/未批准，不能发布 |

## 精确动作缺口

- **00_reference_topright_boy**：
  walk：无缺槽。idle：无缺槽。
- **01_ice_sword_girl**：
  walk：无缺槽。idle：无缺槽。
- **02_fire_talisman_boy**：
  walk：无缺槽。idle：无缺槽。
- **03_lotus_healer_girl**：
  walk：无缺槽。idle：无缺槽。
- **04_mountain_guardian_boy**：
  walk：SW=14,15,16；NW=08,10,11,12,14,15,16。idle：无缺槽。
  未计新增的旧槽重叠候选：walk/E/01.png。
- **05_celestial_musician_girl**：
  walk：SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：无缺槽。
- **06_thunder_caster_boy**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=04,06,07,08,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：无缺槽。
- **07_moon_shadow_assassin_girl**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；S=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：N,NE,E,SE,S,SW,W,NW。
- **08_alchemy_prodigy_boy**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；S=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：N,NE,E,SE,S,SW,W,NW。
- **09_bamboo_archer_girl**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；S=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：N,NE,E,SE,S,SW,W,NW。
- **10_crimson_spear_girl**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；S=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：N,NE,E,SE,S,SW,W,NW。
- **14_short_hair_snow_summoner_girl**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；S=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：N,NE,E,SE,S,SW,W,NW。
- **15_water_dragon_scholar_boy**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；S=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：N,NE,E,SE,S,SW,W,NW。
- **17_ghost_script_calligrapher_boy**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；S=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：N,NE,E,SE,S,SW,W,NW。
- **20_star_formation_master_girl**：
  walk：N=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；E=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SE=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；S=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；SW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；W=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16；NW=01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16。idle：N,NE,E,SE,S,SW,W,NW。

## 本轮真实Unity离线运行证据

正式工程run2的 [EditMode原始XML](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/editmode.xml) 为405/405通过，[PlayMode原始XML](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/playmode.xml) 为49/49通过。结果、启动记录和16张截图绑定的只读复核见 [run2门禁核对](run2-real-camera-runtime-gates.json)；实际资源身份见 [离线沙盒观测记录](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/runtime-observed-appearances.json)。这些结果证明本轮离线组件/沙盒运行，不构成正式联网登录、选角、主城、战斗、重登全流程验收。

00–03共8张正常/最近镜头截图。最近镜头的完整帧、脚点、名牌投影断言均通过，主任务已目视确认头、身、脚和名牌完整；截图仍使用512×512旧V13资源，不能证明1024高清走帧。

| 原ID | 正常镜头 | 最近镜头 |
|---|---|---|
| 00_reference_topright_boy | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-00_reference_topright_boy.png) | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-00_reference_topright_boy-nearest-zoom.png) |
| 01_ice_sword_girl | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-01_ice_sword_girl.png) | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-01_ice_sword_girl-nearest-zoom.png) |
| 02_fire_talisman_boy | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-02_fire_talisman_boy.png) | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-02_fire_talisman_boy-nearest-zoom.png) |
| 03_lotus_healer_girl | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-03_lotus_healer_girl.png) | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-03_lotus_healer_girl-nearest-zoom.png) |

另8张为既有23–30的正常镜头回归截图，仅用于保护旧角色，不扩展本批保留人物范围：

| 既有ID | 正常镜头 |
|---|---|
| 23_lantern_courier | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-23_lantern_courier.png) |
| 24_lu_dongbin | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-24_lu_dongbin.png) |
| 25_lion_drum_guard | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-25_lion_drum_guard.png) |
| 26_osmanthus_healer | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-26_osmanthus_healer.png) |
| 27_ink_kite_ranger | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-27_ink_kite_ranger.png) |
| 28_moon_rabbit_artificer | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-28_moon_rabbit_artificer.png) |
| 29_he_xiangu | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-29_he_xiangu.png) |
| 30_han_xiangzi | [截图](../../../qdao_original_roster_v13/runtime-validation/formal-character-20260921-run2/city-captures/tianyong-30_han_xiangzi.png) |

## 验收缺口与发布边界

04：NW04/06/07残边疑点尚待实际检查；NW08/10/11仅归档raw。05：NE16库存齐但独立重建、混合连播/接缝和视觉批准未完成。06：E04/06/13仅归档raw，E03紫边疑点；拒收E09第一稿不计数。这些交接状态没有被本次文件盘点提升为通过。

00–03本轮真实Unity离线组件/沙盒测试已通过，正式联网登录/选角/主城/战斗/重登的身份全流程仍未验收；04–06缺实际1024移动帧截图、正常/最近镜头检查和完整Unity运行；其余8名需先完成真实动作包。不存在可合法stage的本批新齐套包。

正式Unity本轮导入触发旧meta序列化变化；这与旧PNG/JSON是否改变分开审计。固定历史baseline仍受SHA保护，publisher拒绝未经单独认可的旧meta变化。没有替换baseline或以新git HEAD作为保护原点。

run2全量输入快照仍存在漂移：Unity导入中的Sentis AnalyticsDefineManager移除了SENTIS_ANALYTICS_ENABLED，PlayMode另有动态字体变化；原始before/after证据保留。离线测试和截图通过不抵消输入一致性失败，本轮不构成发布证明，未批准任何新增HD、未执行publish。

本次发布工具与测试结果另见 [发布工具接续报告](PIPELINE_REPORT.md)。
