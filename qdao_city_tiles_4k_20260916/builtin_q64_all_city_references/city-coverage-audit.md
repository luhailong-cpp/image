# 主城与外观覆盖盘点

核查日期：2026-09-17。范围为当前客户端实际注册、可通过地图入口进入的主城及外观，以及相应本地资源。本次只读核查代码、清单和图片；没有运行游戏验收，没有修改代码、PNG、生成记录或生产目录清单。

**当前运行时范围是四个城市、七套外观。现有生产清单覆盖这七套；没有发现漏列的已接入第五城，天墉也没有独立配置的日景外观。此结论说明制作范围完整，不代表七套新的4K分块或64K整城已经完成。**

## 1. 当前运行时清单与制作名称映射

| 场景ID | 城市 | 已接入外观 | 制作清单variant | runtimeVariant | 现有完整源图 |
|---|---|---|---|---|---|
| 1 | 天墉城 | 综合节庆 | festival | festival | [节庆母图6144²](E:/work/image/tianyong_festival_hd_20260910/tianyong_city_master_6144.png) |
| 2 | 蓬莱岛 | 日景 | day | day | [原生1254²](E:/work/image/qdao_large_city_maps_20260912/penglai_island/penglai-island-native.png) |
| 2 | 蓬莱岛 | 中秋月夜 | mid_autumn | festival | [原生1254²](E:/work/image/qdao_large_city_maps_20260912/festival_variants/penglai_mid_autumn/map-native.png) |
| 3 | 东海渔村 | 日景 | day | day | [原生1254²](E:/work/image/qdao_large_city_maps_20260912/donghai_fishing_village/donghai-fishing-village-native.png) |
| 3 | 东海渔村 | 元宵灯会 | lantern | festival | [原生1254²](E:/work/image/qdao_large_city_maps_20260912/festival_variants/donghai_lantern_festival/map-native.png) |
| 4 | 揽仙镇 | 日景 | day | day | [原生1254²](E:/work/image/qdao_large_city_maps_20260912/lanxian_town/lanxian-town-native.png) |
| 4 | 揽仙镇 | 春节迎新 | spring | festival | [原生1254²](E:/work/image/qdao_large_city_maps_20260912/festival_variants/lanxian_spring_festival/map-native.png) |

制作中的中秋、元宵、春节名称必须映射为客户端的 festival，不能直接当作客户端外观目录名。当前[生产清单](E:/work/image/qdao_city_tiles_4k_20260916/production_catalog.json)已保存该映射。

运行时依据：

- [CityTravelUiRoot.cs:211](E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Gameplay/CityTravelUiRoot.cs:211) 的 CreateDestinations 明确列出天墉、蓬莱、东海、揽仙四个入口，场景ID为1、2、3、4。
- [FestivalRegionMap.cs:48](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/FestivalRegionMap.cs:48) 注册后三城及节庆名称；[同文件:21](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/FestivalRegionMap.cs:21) 只按 day / festival 选择贴图，[同文件:97](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/FestivalRegionMap.cs:97) 使用相同名称配置4K图块。
- [TianyongMapRuntime.cs:129](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongMapRuntime.cs:129) 在场景既非配置的默认天墉、又非注册地区时卸载并返回。本盘点没有将旧草稿、预览、战斗背景或未注册场景计为额外运行时主城。

## 2. 天墉没有独立日景外观的证据

[CityTravelUiRoot.cs:215](E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Gameplay/CityTravelUiRoot.cs:215) 的天墉项仅设置 DayResourcePath 为 World/FestivalRegions/tianyong/preview，没有 FestivalResourcePath。这里的字段名称不代表存在一套独立日景地图。

[CityTravelWindow.cs:20](E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Gameplay/CityTravelWindow.cs:20) 以是否存在 FestivalResourcePath 判断 HasFestival；[同文件:158](E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Gameplay/CityTravelWindow.cs:158) 据此隐藏节庆切换、禁用日景切换。天墉不是两套贴图之间的日/节切换。

实际天墉底图通过 [TianyongPaintedCity.cs:187](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs:187) 明确配置为 tianyong/festival。其菜单预览实测为1254×1254，正式底图则为下述6144整图对应的36片。因此预览不另计一套日景外观。此结论仅限当前运行时配置，不宣称仓库历史中从未存在过其他天墉草稿。

## 3. 已实测的源图与客户端匹配

六张区域图逐一执行了PNG解码、尺寸读取和SHA-256对照：

- 蓬莱、东海、揽仙的日景和节庆源图均为1254×1254。
- 对应客户端目录为 E:/work/mmorpg-client/Assets/Resources/World/FestivalRegions/，其下各地区 penglai、donghai、lanxian 各有 day.png 与 festival.png，六张尺寸均为1254×1254。
- 六组源文件与客户端文件逐字节SHA-256相同，并与[已导入清单](E:/work/image/qdao_large_city_maps_20260912/runtime/import-manifest.json)记录的 source_sha256 一致；没有将预览或放大副本算作新源图。

天墉实测：

- 节庆完整源图为6144×6144，SHA-256为 aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428。
- 客户端目录为 E:/work/mmorpg-client/Assets/Resources/World/Tianyong/SceneTiles6x6/Tiles/，36张 tianyong_r01_c01.png 至 tianyong_r06_c06.png 全部为1024×1024。
- 将源图按6×6、每格1024裁开后，36张客户端PNG的解码RGB像素全部与对应源裁块一致（36/36）。这里核验的是解码像素，不声称每个PNG压缩字节与另一份切片文件相同。
- [TianyongPaintedCity.cs:26](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs:26) 的资源目录、6×6数量和1024块尺寸与实测一致，[同文件:193](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs:193) 按行列加载这些贴图。6144整图是拼合资源，不是本轮65536整城交付。

## 4. 布局合同与验收限制

四城共用绘制世界范围 X=50..350、Z=0..300，即300×300世界单位；图像左上对应世界北侧、图像行向下对应Z减小。依据是 [TianyongMapDefinition.cs:73](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongMapDefinition.cs:73) 的400×300场地、[TianyongPaintedCity.cs:38](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs:38) 的正方形绘图范围及[像素转世界坐标:76](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs:76)；后三城直接使用同一绘图范围。

日景与节庆使用同城同一份150×150行走遮罩、每格2世界单位。依据为 [FestivalRegionMap.cs:22](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/FestivalRegionMap.cs:22) 的不含外观名的 MaskPath 与[同文件:104](E:/work/mmorpg-client/Assets/Scripts/World/Tianyong/FestivalRegionMap.cs:104) 的换景逻辑。这只能说明代码/资源合同一致，不能将两版不同画面说成逐像素相同，也不能替代新画稿的导航验收。

本轮七套完整Q版母参考另见[元数据审计](E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/model-audit.json)。它们用于统一后续分区的布局与画法，不计作七张64K成图，也不替代每套256张4096×4096正式图块。

本次盘点末次只读检查时，客户端 Assets/Resources/World/CityTiles4K 目录尚不存在。因此不能把制作范围覆盖、完整母参考齐全或局部4K候选，表述为全部主城高清图已完成并接入。

后续优先验收七套全部区域的真实原生细节、跨块接缝、日/节共同导航和实际最近镜头。天墉还须逐一检查旧前景剪影与新画稿的形状、位置、光照和近景清晰度，依据[客户端4K说明](E:/work/mmorpg-client/Docs/CityTiles4K.md:38)。本盘点没有执行这些新的美术、导航或实机验收。
