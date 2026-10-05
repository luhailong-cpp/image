# 竹风狸素材接手

本目录是唯一可写工作范围，不涉及 Git 合并操作。未提交、推送、切分支或改Git索引。

最终接手应先核对 `STATUS.md`、`qa/technical.json` 与 `qa/visual-review.json`，确认68帧齐全及所有视觉问题状态。当前仍在制作，不能用本说明代替完成验收。

使用 `manifest.json` 的 `runtime/<action>/<direction>/<frame>.png`、durationMs、pivot、anchorTopLeft与event。保持1024完整透明画布，禁止按每帧bbox重居中；E敌方斜前右下、W我方斜后左上。hit/attack/cast均为原地动作，接入代码不得把本包当走路或跑步序列。

原有跨窗口身份/画法参考位于 Image 项目内部，只读保留。逐图模型目标与未知实际参数见各图generation记录；图片成品无需宿主缓存路径也能播放，宿主原生源SHA只是历史来源证据。

本次没有访问或接入客户端。后续客户端任务应独立验证pivot显示位置、动作结束衔接、事件触发、纹理导入alpha与排序；不得声称本包已通过引擎验收。
