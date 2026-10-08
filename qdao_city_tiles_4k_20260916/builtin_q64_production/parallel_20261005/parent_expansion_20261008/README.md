# 主城当前候选与原生来源核验

当前选用 [child-selected/current-selection.json](child-selected/current-selection.json)：`r08_c10` 使用子任务已经完成的原生拼合图，`r08_c09` 使用兼容版本，保留子任务的右侧共边并叠入父任务已检查的不重叠修补。

- [r08_c10 当前图](../tianyong_festival/r07_c10/current/v004/r08_c10.png)：4096×4096，16,777,216 个有效不透明像素，SHA256 `d8b35c312bcb85c42bd3f2478c6f56a9c8c1aed67e6c7b11e3e79ab5c05e766c`。
- [r08_c09 兼容图](child-selected/r08_c09.png)：4096×4096，SHA256 `6cdd48488ea9b6e7c29a4cac2b205c78810ea999deb2358d233fe985cda7440c`。此为同坐标更新，不增加图块数。
- [来源审查](child-selected/audit.json)：104 份文件哈希、11 次增量拼合逐像素重建；6 张当前原像素裁图实际检查。[原生来源补充](child-selected/native-source-supplement.json)继续验证15张后续原生AI输入与逐图记录。
- [父任务复看记录](child-selected/root-visual-review.json)记录第二次实际检查。范围仍为本次新增区域和共边局部，不表示整图、整城或客户端验收。

原生 AI 素材经局部结构重绘和有记录的有限配准/色彩匹配后拼合，没有把布局参考放大充当细节。目标配置为 GPT Image 2.5 / max；内置工具未披露实际模型与质量，因此相关生成记录的实际值为未确认。每张图的记录与来源链继续保留。

父目录原先并行制作的同坐标竞争图未选用：西侧曾残留轻微斜向色差，子任务当前版本更完整。按用户素材保留规则，已删除120份未采用图片和二进制处理中间文件，保留全部提示词、工具回执、逐图模型记录、校验值、脚本和审查文字，详见 [退休清单](retirement.json)。`current/`、`integration-v1/`、`integration-v2/` 与旧 `r02_*` 下的图像路径为历史记录，图片已退休，不是当前交付入口。

只对 `r08_c10` 这个新增坐标计一次完整像素候选。正式验收仍为否，七套主城尚未完成。
