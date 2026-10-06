# 04 渔村日景地图 · 本任务制作记录

本页由 save_progress.py 按磁盘当前事实生成。内部资产 ID：donghai_day；正式项目采用《五行奇谈》原创命名，旧 ID 不代表已确认的新旧地名映射。

目标65536×65536，16×16共256块，每块4096×4096。当前完整像素候选 **5/256**，基线坐标 3 个、新增坐标 2 个。正式验收 **0**；整城未完成、未客户端验收。

当前状态见 [progress.json](progress.json)，逐坐标状态见 [tile-index.json](tile-index.json)。[当前预览](current-preview.png)仅缩小展示候选，不能用于原像素验收。

## 当前候选与在制区域

同一坐标仅统计一次，选择顺序为 tiles/ 当前版本 → 各图块 output/ → handoff基线。计入图均已完整解码、核实4096×4096和记录SHA；优先版本校验失败会排除并报告，不自动退回旧版。

| 坐标 | 当前候选 | 来源 | SHA-256 |
|---|---|---|---|
| r08_c08 | [PNG](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c08.png) | handoff_baseline | cc2369d3bfd61a71104cc53cc330e37034367761094d54de8d437da3eaed9ff2 |
| r08_c09 | [PNG](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c09.png) | handoff_baseline | 2595df0fb75328de5fc748da03a08d6ebf8c64ef10f331bdc408a1a6c2921caa |
| r08_c10 | [PNG](tiles/r08_c10.png) | current_tiles | b3c8ff658caf55ef4e7adccac38a0dd02de2fd4b874b371668b2493624f692cc |
| r08_c11 | [PNG](tiles/r08_c11.png) | current_tiles | 5c62427846f8cbde26d94390666257ddb6a5d35926f4bf301bd9badf11247b2f |
| r08_c12 | [PNG](tiles/r08_c12.png) | current_tiles | bb0618d75e9fc58f822f952dd52b7dedac2dc0e65f4786bfcdf9a3c2b5ade1ce |

当前优先在制块：**r08_c13**；阶段：native_expansion_in_progress。

- r08_c11：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c12：已核验原生片 16/16；已有完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c13：已核验原生片 5/16；尚无完整像素候选。片段、结构参考和透明进度图不计整块。
- r08_c14：已核验原生片 0/16；尚无完整像素候选。片段、结构参考和透明进度图不计整块。

## 检查范围与来源限制

- 完整像素候选只证明当前文件及尺寸齐全，不代表艺术、导航、最近镜头或客户端验收。
- 内部缝、共边接回和修补检查分范围记录。修补后的版本不能自动继承旧SHA的全部审核；下列记录仅作索引，具体通过范围以报告绑定SHA、实际原像素证据及未变像素证明为准。
- 未补齐邻接边、跨排四块交点、全城布局、日景/节庆共用结构、导航、前景遮挡和客户端最近镜头仍待核验。
- [布局与导航审计](layout-audit.json)保留原导航多边形来源；独立风格母图不视为已几何对齐。道路、桥栏、台阶、建筑占地、入口及投影须保持连续。

- [r08_c11/qa/internal-review.json](r08_c11/qa/internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/qa/r04-native-review.json](r08_c11/qa/r04-native-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/qa/root-initial-edge-review.json](r08_c11/qa/root-initial-edge-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/repairs/west-common-edge/integration-qa/integration-review.json](r08_c11/repairs/west-common-edge/integration-qa/integration-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/repairs/west-leaf-01/qa/review.json](r08_c11/repairs/west-leaf-01/qa/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c11/repairs/west-leaf-02/qa/review.json](r08_c11/repairs/west-leaf-02/qa/review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/qa/internal-review.json](r08_c12/qa/internal-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/qa/row03-generation-review.json](r08_c12/qa/row03-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/qa/rows01-02-generation-review.json](r08_c12/qa/rows01-02-generation-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c12/repairs/west-common-edge/integration-qa/integration-review.json](r08_c12/repairs/west-common-edge/integration-qa/integration-review.json)：历史版本或无直接当前SHA绑定；须查范围。
- [r08_c13/qa/structure-review.json](r08_c13/qa/structure-review.json)：历史版本或无直接当前SHA绑定；须查范围。

## 逐图模型、拼接与保留

每张AI原生片、结构参考与修补片的 .generation.json 保存真实工具结果路径、SHA、原生尺寸、时间、配置快照、提示词路径及参考图角色。原生片位于各 rXX_cXX/native/；当前tiles旁的派生记录和integration manifest关联修补来源与参数。
本批目标来自 [batch-model-check.json](batch-model-check.json)：gpt-image-2.5-sunburst/max。实际提交 model/quality 与返回 actualModel/actualQuality 未披露、记为 null；提示词、配置和官方公告不等于后端版本证据。仅使用宿主内置生图，未使用付费API。
完整新块由16张1254×1254原生片组成，1024核心、115四边上下文。裁切、拼接、有限配准与色差匹配须看对应manifest；不把小图放大或布局裁图当高清成品，不宣称拼接图为单次原生4K。缩放仅用于布局参考及预览。
production.py / expand.py负责输入与来源记录；assembly*.py及integrate*.py负责拼接或修补接入。本脚本只刷新进度、索引、README及缩小预览，不改图源、审核结论或客户端。可安全重跑：python save_progress.py。
原生片、结构稿和修补片仍可能是当前依赖，不由本脚本删除。确认最终像素及引用完整后，按项目规则删除可删除原图、拒稿、回退和中间图片，不留图片备份；逐图文字、哈希及来源限制继续保留。
