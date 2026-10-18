# 八仙岛并行三区增量检查（2026-10-16）

本批冻结 154 个有效选中核心、162 个已存唯一坐标、196 个版本。14 块中4块选中满16、8块部分、2块无选中核心；正式验收与整块采纳均为0。相较 resume-v03 增加110个有效选中核心、91个唯一坐标、103个版本。

冻结时间（UTC）：2026-10-16T06:04:48.384291+00:00。只读生产源，零生图、零AI修图、未操作共享Git。

[规范14块清单](summary.json) · [实际4096候选路径及QA](current-candidates.json) · [原比例检查证据](visual-review.json) · [待修清单](repair-queue.json)

|坐标|有效选中核心|已存唯一坐标|版本数|当前QA|
|---|---:|---:|---:|---|
|r01_c02|15/16|15|15|核心不全，未作完整块验收|
|r01_c03|4/16|4|4|核心不全，未作完整块验收|
|r01_c04|16/16|16|17|internal_checked_locally_continuous_external_incomplete|
|r01_c10|0/16|0|0|核心不全，未作完整块验收|
|r01_c11|0/16|0|0|核心不全，未作完整块验收|
|r01_c12|5/16|5|5|核心不全，未作完整块验收|
|r02_c02|13/16|15|22|核心不全，未作完整块验收|
|r02_c03|15/16|16|21|failed_internal_trim_steps_and_south_retained_strip_hold_p44|
|r02_c04|16/16|16|20|internal_geometry_material_repairs_pending|
|r02_c10|8/16|11|19|核心不全，未作完整块验收|
|r02_c11|15/16|16|18|核心不全，未作完整块验收|
|r02_c12|15/16|16|21|provisional_complete_coverage_with_known_external_geometry_failure|
|r03_c05|16/16|16|16|known_surface_repairs_pending|
|r04_c05|16/16|16|18|known_surface_repairs_pending_stale_current_source|

本批可优先查看 r01_c04：24条内部缝、9个交汇、南边4段及西边最下1段未见明显断接。西边另3段、东边缺完整邻源，因此保持外边未完成状态。

- [r01_c04 · 4096候选](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-west-residences/tiles/r01_c04_candidate-v1_4096.png)：`internal_checked_locally_continuous_external_incomplete`。SHA-256 `8b50007e8982e0b1055e7fb5f6699bc3071334fbe121112bf823bcced296316f`。
- [r02_c03 · 4096候选](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-west-residences/tiles/r02_c03_candidate-v1_4096.png)：`failed_internal_trim_steps_and_south_retained_strip_hold_p44`。SHA-256 `304319e569a5cc31fcdfb9aa9adef5a37c9ccf892f400e24446fa0a7040918da`。
- [r02_c04 · 4096候选](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-west-residences/tiles/r02_c04_candidate-v1_4096.png)：`internal_geometry_material_repairs_pending`。SHA-256 `7a56c3ed7c32bd8393f3e0a5294d7d0c3c050853408699dbf6076cb092c3afe7`。
- [r03_c05 · 4096候选](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-northwest-east-extension/tiles/r03_c05_candidate-v1_4096.png)：`known_surface_repairs_pending`。SHA-256 `a1d00fdc789a3d6ac1f23ac0f51db51d3b291c3a6c4b6ac511dafff345de671f`。
- [r04_c05 · 4096候选](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-northwest-east-extension/tiles/r04_c05_candidate-v1_4096.png)：`known_surface_repairs_pending_stale_current_source`。SHA-256 `9bf0857418973fd25905a54e25c6aced687fa1b1b99e3c2eab16ad2ab37f0c5d`。
- [r02_c12 · 4096候选](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-east-residences/candidates/r02_c12-provisional-v001.png)：`provisional_complete_coverage_with_known_external_geometry_failure`。SHA-256 `8414f9846fb16d067cc13a428b40d0219ee1bdaf5ba555bf23ff9dfcafdbf645`。

6张现有4096均已验证每个像素来自记录的原生源，合计100,663,296像素无差异；西区使用重叠区择缝，扩展及东区为整数核心直拼，无缩放、羽化或绘制。原像素一致只证明来源，视觉质量另记。

r02_c03保留金边/蓝瓦截断、南边保留带失败及未选s04_04；r02_c04局部金边切角和树叶清晰度过渡待修。扩展r03_c05复用哈希未变证据，材质仍待修；r04_c05已存4096使用旧s04_02_a01，当前已选a02只补看受影响三条边，未重建生产候选。东区r02_c12的provisional含1个未选失败核心，不计16个有效选中核心。

初次索引快照遗漏r02_c02的新增明确续作QA，已在snapshot-v02补入9个有效选中核心，仍排除两处HOLD；summary.json采用校正后的154。

检查期间生产继续。末次源哈希核对与冻结后新增文件见[source-recheck.json](source-recheck.json)；新版本不自动套用旧候选或旧检查。
