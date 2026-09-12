# 韩湘子 · 30

已完成并通过数值、文件契约与视觉验收。沿用确认的年轻无须 Q 版笛仙：黑直发半束、天青月白短袍、深蓝灯笼裤、腰笛与金玉桂花小饰。

|正式文件|规格|
|---|---|
|`portrait.png`|1024×1024 RGBA 透明立绘|
|`walk/{S,SW,W,NW,N,NE,E,SE}/{01,02,03,04}.png`|32 张独立绘制的动作帧；512×512 RGBA|
|`walk/<方向>/strip.png`|8 张 2048×512 RGBA 横条|
|`walk/<方向>/walk.gif`|8 个透明循环预览，每向 4 帧，每帧 120 ms|
|`walk-cardinal.png`|2048×2048 RGBA；行序 S、W、E、N|
|`walk-diagonal.png`|2048×2048 RGBA；行序 SW、NW、NE、SE|

全部共 51 个正式图像文件，以 [manifest.json](manifest.json) 的文件与哈希为准。每方向帧序均为来源 2×2 的左上、右上、左下、右下；正式帧脚点为左上坐标系中的 (256,471)，自动判定阈值 alpha>8。PNG 是完整 RGBA 素材；GIF 经过调色板量化与二值透明，用作动画预览。

[数值与视觉 QC](qc.json) 为 `passed`，[文件验收](processing/artifact-validation.json) 确认 32 个互不重复的 RGBA 帧、全部 GIF 四帧及 120 ms 时长、8 张横条和两张总表逐格与单帧相同、51 个文件哈希正确。跨方向平均身高比为 1.01023，脚底 y 标准差为 0。最终已查看立绘、全部 PNG 帧与全部 GIF 解码帧： [前四向](processing/visual-review-1.jpg)、[后四向](processing/visual-review-2.jpg)、[GIF 解码总览](processing/gif-decoded-review.jpg)、[视觉记录](processing/visual-review.json)。

原画全部使用宿主内置 `image_gen`。立绘与每个方向的原生来源均为 1254×1254；512 单帧和 2048 总表是后处理导出尺寸，不冒称原生生成尺寸。工具未暴露 model/quality 参数，不声称显式强制了 high。完整提示词位于 [prompts](prompts)，缓存来源映射见 [sources/cache-index.json](sources/cache-index.json)。西南旧版脸向右而脚向左，被排除；正式西南方向使用既有向西图作为身份参考重新生成，提示词为 `prompts/walk_SW_2x2.txt`。`sources/rejected_SW_face_right.png` 仅留作来源审计，不进入交付。

处理只做洋红去底、完整连通主体切分、同方向四帧共用等比缩放、统一脚点、组装与 GIF 导出。最终对洋红/紫色背景溢色取附近现有角色颜色清理，未改变 alpha、像素位置或轮廓，详见 [边缘处理](processing/edge-cleanup.json)。没有镜像、旋转、变形或复制静态人物凑动作。四帧保留手绘步态与衣饰差异；Q 版短腿使部分相反步态的轮廓接近，没有添加插值帧。

可运行本目录 `rebuild.ps1` 从保留原画重建；依赖系统 Python 的 Pillow、numpy 及已安装的 `generate2dsprite` 后处理脚本。重建会使共享处理器重写 QC 为数值通过待视觉复核，重新生成或重建后应再次查看成品再标记视觉通过。

本包是图片素材交付；尚未接入客户端。现有客户端若固定使用每向八帧，需按本包 manifest 的每向四帧契约适配。
