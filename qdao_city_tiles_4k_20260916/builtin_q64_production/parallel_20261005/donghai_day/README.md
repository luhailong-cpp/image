# 04 渔村日景地图 · 本任务制作记录

本页由 save_progress.py 按磁盘当前事实生成。内部资产 ID：donghai_day；正式项目采用《五行奇谈》原创命名，旧 ID 不代表已确认的新旧地名映射。

目标65536×65536，16×16共256块，每块4096×4096。当前完整像素候选 **15/256**，基线坐标 3 个、新增坐标 12 个。正式验收 **0**；整城未完成、未客户端验收。

当前状态见 [progress.json](progress.json)，逐坐标状态见 [tile-index.json](tile-index.json)。[当前预览](current-preview.png)仅缩小展示候选，不能用于原像素验收。

## 当前候选与在制区域

同一坐标仅统计一次，选择顺序为 tiles/ 当前版本 → 各图块 output/ → handoff基线。计入图均已完整解码、核实4096×4096和记录SHA；优先版本校验失败会排除并报告，不自动退回旧版。

| 坐标 | 当前候选 | 来源 | SHA-256 |
|---|---|---|---|
| r07_c15 | [PNG](r07_c15/output/r07_c15.png) | assembled_output | 4e9e6677f9f456422de5d1acceb359d63bd8908656784f44c30acc20118eff4b |
| r07_c16 | [PNG](r07_c16/output/r07_c16.png) | assembled_output | de2ffe83eff08483741521f59e81bbc1ea62927024a86229cb6890eb55477ad0 |
| r08_c08 | [PNG](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c08.png) | handoff_baseline | cc2369d3bfd61a71104cc53cc330e37034367761094d54de8d437da3eaed9ff2 |
| r08_c09 | [PNG](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c09.png) | handoff_baseline | 2595df0fb75328de5fc748da03a08d6ebf8c64ef10f331bdc408a1a6c2921caa |
| r08_c10 | [PNG](tiles/r08_c10.png) | current_tiles | b3c8ff658caf55ef4e7adccac38a0dd02de2fd4b874b371668b2493624f692cc |
| r08_c11 | [PNG](tiles/r08_c11.png) | current_tiles | 5c62427846f8cbde26d94390666257ddb6a5d35926f4bf301bd9badf11247b2f |
| r08_c12 | [PNG](tiles/r08_c12.png) | current_tiles | 69baa04bc59853455e76fd11d9a88e3b4b85c8470bac67245546cfa7139caf99 |
| r08_c13 | [PNG](tiles/r08_c13.png) | current_tiles | 4f97a018ca09c9c1b96f2c71e4fdd8ed601ab72d2374a5f094653ba8785d5b16 |
| r08_c14 | [PNG](tiles/r08_c14.png) | current_tiles | ed9ff4e38f96a1ad32a42fb185e4bc841626dea6add65f1d9bcfc899e79140e8 |
| r08_c15 | [PNG](r08_c15/output/r08_c15.png) | assembled_output | 70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585 |
| r08_c16 | [PNG](r08_c16/output/r08_c16.png) | assembled_output | 3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de |
| r09_c15 | [PNG](r09_c15/output/r09_c15.png) | assembled_output | 33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff |
| r09_c16 | [PNG](r09_c16/output/r09_c16.png) | assembled_output | 75e40578e8c29233bd6b73fbf60a3ea0d7eec917769b93de51404ad34e99a5f9 |
| r10_c15 | [PNG](r10_c15/output/r10_c15.png) | assembled_output | 0b32765cd251e3fb0adb873d202035d4f66aed0d60ebef663f442df2ca8c0fa3 |
| r10_c16 | [PNG](r10_c16/output/r10_c16.png) | assembled_output | 76171e89da5aa391e359c9c6095f3a09bf46912a8f876f0f4a059d6459b608e7 |

当前优先在制块：**r10_c16**；阶段：candidate_pending_scoped_review。

- r07_c14：已核验原生片 3/16；尚无完整像素候选。片段、结构参考和透明进度图不计整块。
- r07_c15：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r07_c16：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c11：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c12：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c13：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c14：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c15：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c16：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r09_c15：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r09_c16：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r10_c15：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r10_c16：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r11_c15：已核验原生片 9/16；尚无完整像素候选。片段、结构参考和透明进度图不计整块。
- r11_c16：已核验原生片 12/16；尚无完整像素候选。片段、结构参考和透明进度图不计整块。

## 检查范围与来源限制

- 完整像素候选只证明当前文件及尺寸齐全，不代表艺术、导航、最近镜头或客户端验收。
- 内部缝、共边接回和修补检查分范围记录。修补后的版本不能自动继承旧SHA的全部审核；下列记录仅作索引，具体通过范围以报告绑定SHA、实际原像素证据及未变像素证明为准。
- 未补齐邻接边、跨排四块交点、全城布局、日景/节庆共用结构、导航、前景遮挡和客户端最近镜头仍待核验。
- [布局与导航审计](layout-audit.json)保留原导航多边形来源；独立风格母图不视为已几何对齐。道路、桥栏、台阶、建筑占地、入口及投影须保持连续。

- [r07_c15/qa/root-initial-review.json](r07_c15/qa/root-initial-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c15/repairs/unified/independent-internal-review.json](r07_c15/repairs/unified/independent-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c15/repairs/unified/producer-internal-insertion-review.json](r07_c15/repairs/unified/producer-internal-insertion-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c15/repairs/unified/producer-unchanged-internal-review.json](r07_c15/repairs/unified/producer-unchanged-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c15/repairs/unified/refined/producer-review-draft.json](r07_c15/repairs/unified/refined/producer-review-draft.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c15/repairs/unified/straight-integrated/close14-preliminary-internal-review.json](r07_c15/repairs/unified/straight-integrated/close14-preliminary-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c15/repairs/unified/straight-integrated/independent-panel-review.json](r07_c15/repairs/unified/straight-integrated/independent-panel-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c15/repairs/unified/straight-integrated-v5/producer-review.json](r07_c15/repairs/unified/straight-integrated-v5/producer-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c15/repairs/unified/straight-integrated-v6/independent-review.json](r07_c15/repairs/unified/straight-integrated-v6/independent-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r07_c15/repairs/unified/straight-integrated-v6/producer-review.json](r07_c15/repairs/unified/straight-integrated-v6/producer-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r07_c16/qa/row04-generation-review.json](r07_c16/qa/row04-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/qa/rows02-03-generation-review.json](r07_c16/qa/rows02-03-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/qa/structure-review.json](r07_c16/qa/structure-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/qa/top-row-generation-review.json](r07_c16/qa/top-row-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/repairs/final-rail-v2/independent-review.json](r07_c16/repairs/final-rail-v2/independent-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r07_c16/repairs/final-rail-v2/review.json](r07_c16/repairs/final-rail-v2/review.json)：匹配当前图块SHA；仅报告范围有效。
- [r07_c16/repairs/final-west-joint/independent-fill15-initial-review.json](r07_c16/repairs/final-west-joint/independent-fill15-initial-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/repairs/integrated-south-v2/local-review.json](r07_c16/repairs/integrated-south-v2/local-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/repairs/internal-color-match/visual-review.json](r07_c16/repairs/internal-color-match/visual-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/repairs/south-joint-color-v4/independent-south-review.json](r07_c16/repairs/south-joint-color-v4/independent-south-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/repairs/south-joint-color-v4/visual-review.json](r07_c16/repairs/south-joint-color-v4/visual-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/repairs/south-native-selection-review.json](r07_c16/repairs/south-native-selection-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r07_c16/repairs/west-upper-three/local-review.json](r07_c16/repairs/west-upper-three/local-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/qa/internal-review.json](r08_c11/qa/internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/qa/r04-native-review.json](r08_c11/qa/r04-native-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/qa/root-initial-edge-review.json](r08_c11/qa/root-initial-edge-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/repairs/west-common-edge/integration-qa/integration-review.json](r08_c11/repairs/west-common-edge/integration-qa/integration-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/repairs/west-leaf-01/qa/review.json](r08_c11/repairs/west-leaf-01/qa/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/repairs/west-leaf-02/qa/review.json](r08_c11/repairs/west-leaf-02/qa/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/qa/internal-review.json](r08_c12/qa/internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/qa/root-initial-edge-review.json](r08_c12/qa/root-initial-edge-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/qa/row03-generation-review.json](r08_c12/qa/row03-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/qa/row04-generation-review.json](r08_c12/qa/row04-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/qa/rows01-02-generation-review.json](r08_c12/qa/rows01-02-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/repairs/west-common-edge/integration-qa/integration-review.json](r08_c12/repairs/west-common-edge/integration-qa/integration-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c13/qa/internal-review.json](r08_c13/qa/internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c13/qa/r03-native-review.json](r08_c13/qa/r03-native-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c13/qa/row04-generation-review.json](r08_c13/qa/row04-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c13/qa/rows01-02-generation-review.json](r08_c13/qa/rows01-02-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c13/qa/structure-review.json](r08_c13/qa/structure-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c13/qa/west-joint-review.json](r08_c13/qa/west-joint-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c14/qa/rows01-02-left3-generation-review.json](r08_c14/qa/rows01-02-left3-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c14/qa/rows03-04-generation-review.json](r08_c14/qa/rows03-04-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c14/qa/structure-review.json](r08_c14/qa/structure-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c14/qa/water-repair-final-review.json](r08_c14/qa/water-repair-final-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c14/repairs/west-common-edge/integration-qa/review.json](r08_c14/repairs/west-common-edge/integration-qa/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c15/qa/column04-generation-review.json](r08_c15/qa/column04-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c15/qa/columns01-02-generation-review.json](r08_c15/qa/columns01-02-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c15/qa/pre-integration-internal-review.json](r08_c15/qa/pre-integration-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c15/qa/structure-review.json](r08_c15/qa/structure-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c15/qa/west-corners-initial-review.json](r08_c15/qa/west-corners-initial-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c15/repairs/approved-integration/independent-internal-review.json](r08_c15/repairs/approved-integration/independent-internal-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r08_c15/repairs/approved-integration/insertion-review.json](r08_c15/repairs/approved-integration/insertion-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r08_c15/repairs/approved-integration/review.json](r08_c15/repairs/approved-integration/review.json)：匹配当前图块SHA；仅报告范围有效。
- [r08_c15/repairs/approved-integration/root-external-review.json](r08_c15/repairs/approved-integration/root-external-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r08_c16/qa/column01-generation-review.json](r08_c16/qa/column01-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/qa/column02-generation-review.json](r08_c16/qa/column02-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/qa/column03-generation-review.json](r08_c16/qa/column03-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/qa/column04-generation-review.json](r08_c16/qa/column04-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/qa/internal-review-initial.json](r08_c16/qa/internal-review-initial.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/qa/root-external-initial-review.json](r08_c16/qa/root-external-initial-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/repairs/integrated-v1/independent-internal-review.json](r08_c16/repairs/integrated-v1/independent-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/repairs/integrated-v5/independent-internal-review.json](r08_c16/repairs/integrated-v5/independent-internal-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r08_c16/repairs/integrated-v5/insertion-review.json](r08_c16/repairs/integrated-v5/insertion-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r08_c16/repairs/integrated-v5/review.json](r08_c16/repairs/integrated-v5/review.json)：匹配当前图块SHA；仅报告范围有效。
- [r08_c16/repairs/integrated-v5/root-external-review.json](r08_c16/repairs/integrated-v5/root-external-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r08_c16/repairs/r01_c03-quiet-water/review.json](r08_c16/repairs/r01_c03-quiet-water/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/repairs/r01_c04-quiet-water/review.json](r08_c16/repairs/r01_c04-quiet-water/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/repairs/r02_c03-quiet-water/review.json](r08_c16/repairs/r02_c03-quiet-water/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/repairs/r02_c04-quiet-water/review.json](r08_c16/repairs/r02_c04-quiet-water/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c16/repairs/r04_c04-quiet-water/review.json](r08_c16/repairs/r04_c04-quiet-water/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c15/qa/root-external-initial-review.json](r09_c15/qa/root-external-initial-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c15/qa/rows02-04-generation-review.json](r09_c15/qa/rows02-04-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c15/qa/top-row-generation-review.json](r09_c15/qa/top-row-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c15/repairs/color-match/producer-review.json](r09_c15/repairs/color-match/producer-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r09_c15/repairs/color-match/root-independent-review.json](r09_c15/repairs/color-match/root-independent-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r09_c16/qa/root-initial-review.json](r09_c16/qa/root-initial-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c16/qa/rows02-04-cols02-04-generation-review.json](r09_c16/qa/rows02-04-cols02-04-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c16/qa/top-row-generation-review.json](r09_c16/qa/top-row-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c16/repairs/color-match-v2/independent-internal-review.json](r09_c16/repairs/color-match-v2/independent-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c16/repairs/color-match-v2/root-external-review.json](r09_c16/repairs/color-match-v2/root-external-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r09_c16/repairs/post-integrated-masked/independent-internal-review.json](r09_c16/repairs/post-integrated-masked/independent-internal-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r09_c16/repairs/post-integrated-masked/root-external-review.json](r09_c16/repairs/post-integrated-masked/root-external-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r10_c15/qa/assembly-initial-review.json](r10_c15/qa/assembly-initial-review.json)：匹配当前图块SHA；仅报告范围有效。
- [r10_c15/qa/native-source-review.json](r10_c15/qa/native-source-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/qa/structure-review.json](r10_c15/qa/structure-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/color-match/visual-review.json](r10_c15/repairs/color-match/visual-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/east-integrated/root-independent-east-geometry-review.json](r10_c15/repairs/east-integrated/root-independent-east-geometry-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/east-integrated/visual-review.json](r10_c15/repairs/east-integrated/visual-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/internal-integrated-v2/root-independent-internal-review.json](r10_c15/repairs/internal-integrated-v2/root-independent-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/internal-integrated-v2/visual-review.json](r10_c15/repairs/internal-integrated-v2/visual-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/north-integrated-v2/visual-review.json](r10_c15/repairs/north-integrated-v2/visual-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/north-joint/n3/rejected-review.json](r10_c15/repairs/north-joint/n3/rejected-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/north-joint/n3-retry/rejected-review.json](r10_c15/repairs/north-joint/n3-retry/rejected-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c15/repairs/north-joint/qa/outside-scope-review.json](r10_c15/repairs/north-joint/qa/outside-scope-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c16/qa/structure-review.json](r10_c16/qa/structure-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c16/repairs/internal-final-v2/visual-review.json](r10_c16/repairs/internal-final-v2/visual-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c16/repairs/north-integrated-color-v3/independent-internal-review.json](r10_c16/repairs/north-integrated-color-v3/independent-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c16/repairs/north-integrated-color-v3/root-north-review.json](r10_c16/repairs/north-integrated-color-v3/root-north-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c16/repairs/north-integrated-color-v3/visual-review.json](r10_c16/repairs/north-integrated-color-v3/visual-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c16/repairs/west-color-v1/independent-west-internal-review.json](r10_c16/repairs/west-color-v1/independent-west-internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r10_c16/repairs/west-color-v1/root-west-scope-review.json](r10_c16/repairs/west-color-v1/root-west-scope-review.json)：历史版本或无直接当前SHA绑定；须查范围。

## 逐图模型、拼接与保留

每张AI原生片、结构参考与修补片的 .generation.json 保存真实工具结果路径、SHA、原生尺寸、时间、配置快照、提示词路径及参考图角色。原生片位于各 rXX_cXX/native/；当前tiles旁的派生记录和integration manifest关联修补来源与参数。
本批目标来自 [batch-model-check.json](batch-model-check.json)：gpt-image-2.5-sunburst/max。实际提交 model/quality 与返回 actualModel/actualQuality 未披露、记为 null；提示词、配置和官方公告不等于后端版本证据。仅使用宿主内置生图，未使用付费API。
完整新块由16张1254×1254原生片组成，1024核心、115四边上下文。裁切、拼接、有限配准与色差匹配须看对应manifest；不把小图放大或布局裁图当高清成品，不宣称拼接图为单次原生4K。缩放仅用于布局参考及预览。
production.py / expand.py负责输入与来源记录；assembly*.py及integrate*.py负责拼接或修补接入。本脚本只刷新进度、索引、README及缩小预览，不改图源、审核结论或客户端。可安全重跑：python save_progress.py。
原生片、结构稿和修补片仍可能是当前依赖，不由本脚本删除。确认最终像素及引用完整后，按项目规则删除可删除原图、拒稿、回退和中间图片，不留图片备份；逐图文字、哈希及来源限制继续保留。
