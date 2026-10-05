# r08_c10 / r03_c02 原生上扩分片

内置 image_gen 实际生成 1 次，返回 1254×1254；原字节保存在 `native.png`，SHA256 `b4d1e8ec87ae0bbbae09f1b2a4a393efe0101da8f21fecc8b07cabf864892c1a`。没有 API 调用、放大、配准或合入当前地图。

目标全局范围 `[37773,30605,39027,31859]`，本块范围 `[909,1933,2163,3187]`。输入只在下方 230 行有原生上下文，上方 1024 行透明待绘。来源为任务 source-checkpoint 的 v001 片段；来源快照与 SHA 见 `preparation.json`。

实际提示词见 [prompt.txt](prompt.txt)，完整提交 payload 见 [request.json](request.json)。真实工具输出提示、宿主路径及观察时间见 [tool-response.json](tool-response.json)；逐图来源见 [native.png.generation.json](native.png.generation.json)。配置目标 `gpt-image-2.5-sunburst / max`，实际提交 model/quality 与实际返回 model/quality 均为 null；generatedAt 未知，观察完成时间另记。

原像素检查未通过直接接入：已知下边多处轮廓出现约 8–26 px 偏移，原布局的宽横向象牙石带被简化成细缝。详见 [visual-review.json](visual-review.json)、[comparison.json](comparison.json) 和 [overlap-edge-diagnostic.json](overlap-edge-diagnostic.json)。这张留作当前待修输入，未计完整 4K、未自动通过、未修改 current/progress/source-checkpoint。
