# 八仙岛西区：10 月 16 日增量检查

本轮已按一次冻结快照完成西北／西南既有素材检查。98 坐标中，28 坐标有 16 个有效选中核心、4 坐标为部分覆盖、66 坐标无本区选中核心；有效核心 478/1568，缺 1090。正式验收仍为 0。独占划拨的 8 个西北坐标由专工另计，本表保留其本区选中数 0，不声称那些坐标没有平行产出。

现有可查看完整 4096 图 28 张，其中明确采用 27 张、独立诊断硬拼 1 张（r08_c02）。[逐张文件、hash、尺寸与 QA](current-candidates.json)；[98 坐标与证据](summary.json)。

r05_c02=v5、r07_c04=v4 来自冻结的分工 owner 明确选用清单。汇总 current-adopted 索引仍分别指 v4 和漏列，已记录[选用依据及索引差异](selection-authority-resolution.json)。不按文件新旧推断采用。

可以先查看的稳定四图小组：内部及组内相邻边沿用输入 hash 未变的既有证据，外围仍待齐片验收：

- [r10_c03 · 4096×4096](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/output/contiguous-r09-r10-c03-c04-v01/r10_c03-native-4096.png)
- [r10_c04 · 4096×4096](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/qa/central-north-roof-reselect-v01-r10_c04-candidate-4096.png)
- [r11_c03 · 4096×4096](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/qa/central-fasciaedge-v01-r11_c03-candidate-4096.png)
- [r11_c04 · 4096×4096](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/qa/central-pond-right-crisp-v02-r11_c04-candidate-4096.png)

新增采用图与 QA：

- [r05_c02 v5](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest/tiles/r05_c02_candidate-v5_4096.png)：比既有 v4 仅左下 819,133 像素改变；变边、九交点和下部整段原尺寸查看，未见明显的新几何错断。北部旧问题保留，完整生产收口按冻结 owner 状态待定。
- [r07_c04 v4](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest/tiles/r07_c04_candidate-v4_4096.png)：采用 owner 实际版本；已查看变化边及九交点，墙脚／勾缝旧收口项目仍按生产记录待修。南接 r08_c04 存在显著地面清晰度差，保留材质待修。
- [r12_c04 当前候选](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest/qa/central-r12c04-deckrim-v01-r12_c04-candidate-4096.png)：17 个源的 16,777,216 像素回放 0 不匹配。已查看全部 24 内边与九交点，木梁修补左缘小台阶、台阶转折及花蕊整物确认仍未通过。

与 v03 相比新增 45 个有效选中核心；另外 11 个基线后落盘而未被本次冻结选择采用的源文件单列，不计作新增核心。r03_c01 为 5/16、r06_c02 为 13/16；后者局部叶片留边需核查，未以暂缓当通过。

初查实际查看 92 段，owner 版本订正后补看 40 个变段、32 段逐像素相同直接复用；所有查看板均保存原像素，没有放大或重建 8192 总览。[待修清单](repair-queue.json)、[新核心合同核对](new-core-contract-check.json)、[新采用图像素回放](owner-candidates-pixel-replay.json)。

冻结时刻 UTC：2026-10-16T04:26:17.605232+00:00。结束仅复核当前输入，图像 hash 全部未变；元数据后续变化 4 项另记[结束核对](end-input-check.json)，不无限追随生产更新。

本轮生成调用 0，生产目录写入 0，共享 Git 操作 0。

本批结束后的一次独立观察发现：r03_c01 已有 v1、r06_c02 已有 v2、r07_c04 已换 v6。其实际文件、hash、尺寸已核实，尚未独立看图通过；[后续候选入口](post-freeze-next-candidates.json) 与 [元数据差异](post-freeze-metadata-delta.json) 分列。本批 r07_c04 v4 结论仅属于该旧版，不能套到 v6。另记录 r05_c02 v5 的后续生产内部收口已改为 true，像素未变。
