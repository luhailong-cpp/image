# 当前在制图与并行交接

本轮已完成局部修补、原像素接缝检查和来源交接，继续制作入口已切换到 [七套独立任务](../../parallel_20261005/README.md)。

[current-work.json](current-work.json) 锁定29张4096×4096在制候选：主城节庆11张，其余6套各3张；另有一张主城 r08_c10 的原生局部片段。完整4K图块数不因返修或片段增加。全部地图仍未完成，正式验收0。

最新修补来源：

- [主城6图联动检查点](c08/adjacent-qa/current-selection.json)：金环及两处交点已修；窗口外旧细断线与材质跳变已列出，尚未整边全部通过。
- [小镇日景](lanxian/lanxian_day/current-selection.json)与[春节](lanxian/lanxian_spring/current-selection.json)：伞骨、砖缝局部修补后已按当前SHA检查，外部缺邻块待补。
- [渔村检查](donghai/review.json)与[仙岛检查](penglai/input-and-qa-index.json)：既有6张各自内部拼缝/交点与本批共边按原像素实看，所查范围内保留原图。
- [主城新片段](c10-expansion/completion.json)：唯一有效1254×1139片段保留，未充作完整4K图。

逐图模型、质量、原生尺寸、来源与哈希见各候选旁生成记录和其源链。目标为GPT Image 2.5（配置Sunburst/max）；内置实际型号/质量未披露，未使用付费API。前一全局状态仅以[文字快照](previous-global-state-before-parallel.json)留存，不是当前选择。

本轮限定清理已删除62张已替代或拒绝的图片，当前图与仍被并行任务引用的来源保留；逐文件路径、哈希、替代与删除结果见[清理回执](c08/adjacent-qa/cleanup_20261005/receipt.json)。清理后当前29张4K候选与唯一局部片段已再次核验存在。
