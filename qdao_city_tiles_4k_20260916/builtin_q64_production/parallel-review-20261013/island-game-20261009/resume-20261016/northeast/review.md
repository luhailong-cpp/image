# 八仙岛东北既有素材增量检查（2026-10-16）

本批已检查完冻结输入，仍有美术待修和缺块。原东北49坐标已按归属去重：本表统计原制作区39坐标与海岸加速4坐标，东民居6坐标交由 parallel 批合并，未算空块或重复计数。

冻结于 UTC 2026-10-16T13:37:33.140035+00:00。43坐标共340个唯一选中1024核心；20张核心完整并已采用的4096候选，2张部分覆盖，21张尚无选中核心，正式全图验收0。制作区39坐标占276核心、16完整、2部分、21空；海岸4张占64核心。

## 可先查看的现有 4K 图

新增完整候选 r06_c12、r06_c14 已有绑定当前候选哈希的49项内部QA。独立核对32张1254源图、32个1024原像素核心摆放，以及98份现有检查裁片与当前4096成图像素完全一致，故复用已通过证据。两张各自北邻4096接边已有当前哈希绑定的通过记录，缺少左／下邻的外接仍待后续。

- [r06_c12，4096×4096](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r06_c12-continued-v1-20261016.png)；内部QA可复用，上邻通过，左／右／下邻未完成。
- [r06_c14，4096×4096](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r06_c14-native-v1-20261013.png)；内部QA可复用，上邻通过，左／下邻未完成，东侧为地图边界。

两组现有局部拼接的8张4K输入哈希均未改变，原共享边和四交点通过证据继续有效，外围状态按原记录保留。本批未新建8192图或整图。

- g03-main-r03-r04-c11-c12：[r03_c11](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r03_c11.png)、[r03_c12](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r03_c12.png)、[r04_c11](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c11.png)、[r04_c12](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c12.png)。
- g04-main-r04-r05-c13-c14：[r04_c13](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c13.png)、[r04_c14](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c14.png)、[r05_c13](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c13.png)、[r05_c14](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c14-v2-20261012.png)。

## 本批补查与待修

只针对 r03_c09、r04_c09 新选核心补查27条原像素接边与11个四交点，9张100%拼板全部实际查看。22条边及7个十字的局部轮廓／材质检查通过；1条边保留灰缝几何问题，4条边及4个十字保留材质问题。局部通过不等于部分图块整体布局验收。

- r03_c09：冻结11/16，p01_02_v3→p01_03 中部灰缝错位仍待修。p01_01_v2→p01_02_v3 本条接边有当前源哈希绑定通过记录；旧 pendingIssues 中提到的 p01_02_v2 为已替换版本，不能把该文字直接当作新版本已失败或已通过。
- r04_c09：冻结9/16。p01_04_v3 上／左侧、p04_03_v2 上／右侧仍有矿物斑驳石面到细密菱格石面的可见过渡；p04_04 灯笼整体宽度保留生产原布局待核，接边连续不能替代整物布局验收。
- r05_c11：候选哈希未变，灯笼下 p01_04 矩形虚化左／下边及北接金色细棱问题继续开放。
- 海岸 r02_c13／r02_c14：候选哈希未变，世界 x53248、y约7900—8050 的蓝色材质带继续待修。原南北接边通过证据与这处竖边缺陷分别保留。

## 逐图冻结候选

下表全部绑定冻结版本和实核哈希。冻结后新增／替换的实时选源另列于后，不继承旧问题或旧通过状态。

| 坐标 | 原始4096文件 | SHA256前12位 | 冻结版本QA |
|---|---|---|---|
| r01_c13 | [r01_c13.4096-candidate.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast/candidates/r01_c13.4096-candidate.png) | c31ac74ea0f3 | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r01_c14 | [r01_c14.4096-candidate.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast/candidates/r01_c14.4096-candidate.png) | 505a87057930 | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r02_c13 | [r02_c13.4096-candidate.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast/candidates/r02_c13.4096-candidate.png) | 4cf9dee26962 | 内部原记录复用；海岸竖边材质待修 |
| r02_c14 | [r02_c14.4096-candidate.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast/candidates/r02_c14.4096-candidate.png) | 1ee2c2bb2bbb | 内部原记录复用；海岸竖边材质待修 |
| r03_c10 | [r03_c10-native-v2-20261013.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r03_c10-native-v2-20261013.png) | 2b3a0942c40c | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r03_c11 | [r03_c11.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r03_c11.png) | 38a2deea4cef | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r03_c12 | [r03_c12.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r03_c12.png) | 0e6d7aa562ad | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r03_c13 | [r03_c13.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r03_c13.png) | 607e8fac0c1f | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r03_c14 | [r03_c14.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r03_c14.png) | b85fc423d05d | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r04_c10 | [r04_c10-native-v1-20261013.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c10-native-v1-20261013.png) | 1c2426a455f7 | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r04_c11 | [r04_c11.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c11.png) | c7740d60c062 | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r04_c12 | [r04_c12.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c12.png) | 1eed7489617d | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r04_c13 | [r04_c13.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c13.png) | 9568fd0f47a4 | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r04_c14 | [r04_c14.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r04_c14.png) | 38cfd83306ac | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r05_c11 | [r05_c11-continued-v2-20261013.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c11-continued-v2-20261013.png) | 63184c2550d2 | 内部材质待修；北接细棱待核 |
| r05_c12 | [r05_c12-sol-v1.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c12-sol-v1.png) | d6b9d2d1f087 | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r05_c13 | [r05_c13.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c13.png) | 2a34551e872c | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r05_c14 | [r05_c14-v2-20261012.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c14-v2-20261012.png) | d3c5f8ae10db | 当前图哈希未变，复用原内部记录；仅原已查外接有效 |
| r06_c12 | [r06_c12-continued-v1-20261016.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r06_c12-continued-v1-20261016.png) | 0106c3f95720 | 98裁片之一组验证完成；完整49项内部QA复用，北接通过 |
| r06_c14 | [r06_c14-native-v1-20261013.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r06_c14-native-v1-20261013.png) | b5bf81a2aaeb | 98裁片之一组验证完成；完整49项内部QA复用，北接通过 |

## 冻结后变化

收尾复核 99 项本批输入，96 项哈希未变，3 项变化。冻结源图像素未变化。后续生产矩阵只记录为 delta，不移用旧通过结论，也不无限追赶在制版本。

- [冻结后变化和输入哈希复核](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/resume-20261016/northeast/source-recheck.json)
- [逐图完整路径、哈希、尺寸、QA清单](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/resume-20261016/northeast/current-candidates.json)
- [两张新完整图的32原图／98裁片像素核验](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/resume-20261016/northeast/reused-full-pixel-verification.json)
- [完整坐标、27边与11十字检查记录](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/resume-20261016/northeast/summary.json)
- [待修队列](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/resume-20261016/northeast/repair-queue.json)

本批零生图、零AI修图，原生产图与选源账本只读，未操作Git。现存图实际生成型号未返回，不追溯标为2.5。
- 冻结后 r03_c09 选中数现为 12/16。新增核心未纳入本批接边检查。
- 冻结后 r05_c11 选中数现为 16/16。实时候选已换为 [r05_c11-localfinish-v3-20261016.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c11-localfinish-v3-20261016.png)；生产记录声明内部状态 passed16core24seam9cross。该新图未纳入本批像素／美术检查，旧图问题不能直接套用到新图。
