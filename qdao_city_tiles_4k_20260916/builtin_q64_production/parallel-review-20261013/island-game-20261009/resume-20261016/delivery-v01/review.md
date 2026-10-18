# 八仙岛可查看素材与独立检查结果

本批已有素材独立检查已完成，可直接打开下列4096成图及分区报告。每张图保留当前检查版本、输入hash、内部和外边结论；正式全图验收仍为0。

优先查看：

| 图块 | 实际4096文件 | QA状态 |
| --- | --- | --- |
| r06_c12 | [打开成图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r06_c12-continued-v1-20261016.png) | 内部证据原像素核验通过；已查北边通过，其余缺邻待验。 |
| r06_c14 | [打开成图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r06_c14-native-v1-20261013.png) | 内部证据原像素核验通过；已查北边通过，其余缺邻待验。 |
| r05_c11 | [打开成图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c11-localfinish-v3-20261016.png) | v3内部通过，旧矩形虚化解决；北边金棱小台阶仍待修，东边通过，西南缺邻。 |
| r08_c10 | [打开成图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southeast/tiles/r08_c10.candidate-wall-recover-20261013-v02.png) | 24段内部缝、9交汇独立通过；外围未闭合，生产可用选源仍有1核状态分歧。 |
| r14_c14 | [打开成图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southeast/tiles/r14_c14.candidate-resume-20261013-v01.png) | 24段内部缝、9交汇独立通过；北西邻图未齐。 |
| r01_c04 | [打开成图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-west-residences/tiles/r01_c04_candidate-v1_4096.png) | 内部及已查南边、西边底段局部连续；其余外边缺邻，未采用。 |

西南 r10—r11、c03—c04 稳定四图小组的当前像素与既有检查一致，可先查看：

- [r10_c03](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/output/contiguous-r09-r10-c03-c04-v01/r10_c03-native-4096.png)
- [r10_c04](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/qa/central-north-roof-reselect-v01-r10_c04-candidate-4096.png)
- [r11_c03](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/qa/central-fasciaedge-v01-r11_c03-candidate-4096.png)
- [r11_c04](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/qa/central-pond-right-crisp-v02-r11_c04-candidate-4096.png)

该四图小组的内部和共享边证据可复用；r11_c03南邻r12_c03的材质问题及其余外围仍待修或待验。未重建8192拼接。

冻结检查清单按196坐标去重，共1322个有效选中核心，71处选中16核心、19处部分覆盖、106处无选中核心。索引另列75份4096文件，其中含未采用、诊断和已知失效候选；不能把文件数当作通过数。各区截点不同，后续生产仍在推进，这些数字仅用于本批检查范围，不能替代当前生产统计。

r12_c13 v04木纹修补已通过变化区检查，旧帆杆问题仍保留；r14_c11、r13_c13水面材质带、住宅金边和屋瓦断口、海岸水纹材质带等按分区问题清单保持未通过。r04_c05已拼候选落后于选中a02，r02_c12 provisional含未选失败源，均不得标为当前完整通过。

- [全部4096路径与逐块QA](current-4k-index.json)
- [196坐标冻结选源覆盖](coverage.json)
- [输入hash复核](input-hash-check.json)
- [待修入口](repair-index.json)
- [西北和西南报告](../west/review.md)
- [东北和海岸报告](../northeast/review.md)
- [东南报告](../southeast/review.md)
- [民居和扩展区报告](../parallel/review.md)

[r05_c11 v3完整收尾证据](../northeast/r05_c11-v3-closeout/review.md)单独绑定v3，原虚化问题已经解决，北边待修没有升级为通过。

冻结后新版本入口分别保留在西区、东北、东南与并行区的增量记录。旧通过证据仅适用于像素hash未变的对应版本。当前分工已包括island_more_20261016的r04_c01/r05_c01；本包没有将旧owner空位当作这些新分工已完成或已检查。

所有输出仅写入授权独立检查目录。未生成或AI修图、未修改生产选源和账本、未操作共享Git、未打断在途制作。
