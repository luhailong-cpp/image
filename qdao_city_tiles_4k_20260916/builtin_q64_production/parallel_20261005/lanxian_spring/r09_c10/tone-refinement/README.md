# r09_c10 桥面与水面局部色差精修候选

本目录仅对已完成春景的内部 1024 / 2048 / 3072 拼块线作局部 RGB 加法校正。`selected/` 原图、日景快照、进度记录均未修改。

- 4K 候选：[core4096.png](core4096.png)；含 115 像素外圈：[extended4326.png](extended4326.png)；观察预览：[preview1254.png](preview1254.png)。
- 完整参数与每材质沿缝估计：[processing.json](processing.json)。
- 完整浮点校正场：[additive-rgb-field4326.npz](additive-rgb-field4326.npz)；实际整数差值：[actual-rgb-delta4326.npz](actual-rgb-delta4326.npz)。
- 支持范围、实际变化、材质分区分别存于 `allowed-support4326.png`、`changed-mask4326.png`、`material-labels4326.png`。
- 原像素检查与未处理问题：[qa/final-review.json](qa/final-review.json)；裁切坐标、外圈变化范围、前后指标：[qa/scope-and-metrics.json](qa/scope-and-metrics.json)。
- 所有派生图片的来源索引：[derived-image-index.json](derived-image-index.json)。正式候选另附逐图 `.generation.json`，明确本次没有新的 AI 调用，来源模型记录沿旧图追溯。

日景 `selection-proof.json` 确认原始 16 小块直接像素拼合，未应用后置色场。本次处理的是原始小块色偏。按水、灰石／阴影、绿叶、暖色铺地独立估计接缝色差，在接缝两侧各不超过 320 像素内对称分担，以 smoothstep 回到零。只平滑校正参数，不模糊图片。实际累计最大 RGB 改动为 `[14,13,14]`，低于每通道 16 的限制。没有位移、几何变形、插值重采样或放大。

北侧 115 像素外圈及首 64 行核心像素完全不变，之后 256 像素逐渐进入校正；与 `r08_c10/selected-v2` 的 230 行重叠比较保持原值。东／西／南外圈的内部接缝修正连续延伸，具体半开坐标范围见 `outerStrips`，下块 guide 应从本候选刷新。

桥与水面的矩形色阶已明显减轻，六条完整接缝和十二条回落边缘均实际按 1:1 检视。水面 x3072 典型绝对色阶约 16.67→1.0，y3072 约 10.67→1.0。轮廓、反射和石缝均保留。

单独记录：红灯柱上段在核心 y1024 附近仍有原有细小色阶／疑似 1–3 像素轮廓折点，检查框 `[900,964,1120,1084]`。红色区域在本次被排除且保持原像素；未用色场掩盖此问题。需要彻底去除时应单独进行局部表面／轮廓修复。

本目录是供主任务选择的当前候选，不宣称整城完成或客户端验收。确认采用后，主任务可按项目素材保留规则移除当前 QA 裁图与被替换中间图片，继续保留完整文字来源、最终色场、遮罩与参数。
