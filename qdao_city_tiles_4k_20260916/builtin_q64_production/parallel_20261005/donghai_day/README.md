# 04 渔村日景地图 · 本任务制作记录

内部资产 ID：`donghai_day`。目标 65536×65536，16×16 共256块，每块4096×4096。原有3块来源已按交接SHA复核；本任务新增r08_c11完整像素候选，尚未正式验收，整城未完成、未客户端验收。

当前状态见 [progress.json](progress.json)，当前连续区域见 [预览](current-preview.png)，256块坐标与可用性见 [tile-index.json](tile-index.json)。下一相邻块为r08_c12。

## 当前像素与检查

- r08_c11 位于全图 `[40960,28672,4096,4096]`，由16张1254×1254原生片（1024核心、115四边上下文）拼合，无成品放大。
- [完整候选](r08_c11/output/r08_c11.png)及[拼接来源清单](r08_c11/output/assembly-manifest.json)已落盘。
- [内部检查](r08_c11/qa/internal-review.json)实际查看6条完整内部缝和9个交点，未发现需要重绘的内部结构问题。
- 四角已查看。与西侧r08_c10的共边存在树叶、阴影与地砖错位，正在以原像素联合上下文重绘，见`r08_c11/repairs/west-common-edge/`。共边修正后还须检查接入外边及新横缝。
- 修正只写本目录的副本；旧来源文件保持只读。缺失区域不计为图块。
- [布局与导航审计](layout-audit.json)记录旧导航多边形来源；当前外观参考未通过同城日景/节庆几何与导航校准，不把独立参考图自动视为对齐。

## 逐图模型与来源

每张当前原生片在`r08_c11/native/<名称>.png.generation.json`保存实际工具路径、SHA、尺寸、配置快照、提示词及参考角色；结构参考与共边补片也有独立记录。配置目标为本批读取的`gpt-image-2.5-sunburst/max`，实际提交`model/quality`及实际返回`actualModel/actualQuality`均为`null`，原因是内置工具未开放选择器、未返回可确认型号质量。不能从提示词或官方公告推断本次实际版本。

本批复核了[官方产品公告](https://openai.com/index/introducing-chatgpt-images-2-5/)与[模型质量说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，记录见 [batch-model-check.json](batch-model-check.json)。未使用付费API。

`production.py`负责带相邻原像素的输入和逐图记录；`assembly.py`负责原像素拼合；`seam_repair.py`负责共边输入与记录；`integrate_west.py`负责联合补片接回与QA。缩放只用于布局参考和总览，不作为高清成品像素。

原生片、结构稿和修补片目前仍是当前接缝修复与可复现拼合依赖，暂保留；已拒绝的误增屋檐图片按用户规则删除，仅保留文字来源证据。最终当前引用核实后再清理可删除中间图，不保留图片备份。
