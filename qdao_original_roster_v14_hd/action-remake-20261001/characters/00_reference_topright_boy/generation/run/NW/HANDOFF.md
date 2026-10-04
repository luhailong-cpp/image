# NW 跑步定向修复推荐

16槽已给出推荐，全部独立原生1254×1254 RGBA、30ms/帧，16个不同SHA。**当前仍待独立根点、接地与动态审核，不是完成通过。**

- [推荐版本与SHA](selection.json)：逐槽source/status/phase/issues，exportApproved=false。
- [16槽完整画布联系表](selected-contact.jpg) · [静态复核报告](static-review.json)。
- [45张原生库存](inventory.json) · [全库存联系表](inventory-contact.jpg) · [逐槽画布指标](recommended-metrics.json)。

本轮已修正02换腿、03右臂回收、04右臂前摆与尺度、05过大、11/12重复右腿相位、15双脚后翻。07–09和13–15按实际姿态重新归位，来源文件名和最终相位不同已逐槽说明；没有复制插值、bbox拟合或脚底贴地。

本代理当前静态未见上述明确手脚硬伤。仍有跨半周期水平位置/头部轮廓漂移，09→10和16→01的脚底边界差，需在统一根点预览中审核。具体实测与范围见静态报告；不把最低像素当接地点。

每图prompt/request/receipt/generation记录完整，45张SHA均匹配，实际model/quality均未披露为null。目标配置仍为本批GPT Image2.5/max。3张1133×1388竖幅没有选入。未修改正式frames、selected-new、全局manifest或Git。

仅保留成品原则继续适用：本目录尚待独立动态验收，当前候选源图不提前删除；正式成品与引用完整后由root清理淘汰图片，保留文字来源。refresh_recommendations.py是当前清单/联系表重建脚本。

