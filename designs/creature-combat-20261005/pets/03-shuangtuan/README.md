# 霜团貂 · 受击 / 普攻 / 施法

2026-10-05。**68张独立AI姿态透明PNG已落盘，六组静态全帧已实际查看。连续播放实看尚未完成，客户端未读取或接入。**

## 查看成品

[六组交互预览](preview/index.html)：正常速度、0.25慢放、暂停、逐帧前后与滑块；完整本地文件，无外部资源。用本机浏览器打开即可。当前自动化浏览器禁止file://，未改用其它入口绕过，故本次没有把预览文件生成当成连播实看通过。

|动作|E斜前朝右下|W真斜后朝左上|每向规格|
|---|---|---|---|
|受击|[正常](preview/media/hit-E-normal.webp) · [0.25慢放](preview/media/hit-E-slow.webp)|[正常](preview/media/hit-W-normal.webp) · [0.25慢放](preview/media/hit-W-slow.webp)|6帧 ×40ms =240ms|
|普攻|[正常](preview/media/attack-E-normal.webp) · [0.25慢放](preview/media/attack-E-slow.webp)|[正常](preview/media/attack-W-normal.webp) · [0.25慢放](preview/media/attack-W-slow.webp)|12帧 ×30ms =360ms|
|施法|[正常](preview/media/cast-E-normal.webp) · [0.25慢放](preview/media/cast-E-slow.webp)|[正常](preview/media/cast-W-normal.webp) · [0.25慢放](preview/media/cast-W-slow.webp)|16帧 ×45ms =720ms|

WebP为512方形、浅灰底的无损查看文件。正式游戏素材只用runtime中的1024透明PNG；预览没有生成插帧，也没有替换正式帧。

## 身份与输出

角色沿用Image原有霜团貂：珠灰圆耳灵貂、琥珀眼、四足、浅玉宽卷单尾、象牙青瓷丝巾与月玉露坠。原有E/W身份图与人物属性手绘风格样板实际附入每次生成/编辑。没有导入新宠物、尖耳狐改造、移动循环或客户端资源。

文件为runtime/{hit|attack|cast}/{E|W}/{01..N}.png。统一1024×1024 RGBA；本批AI原生1254×1254，使用同一整画布等比缩放1024/1254导出，未逐帧对齐脚点、平移、镜像、复制或插值补帧。锚点合同为顶部原点[512,942]，左下归一pivot[0.5,0.08]；画内自然反冲与重心变化保留。

[POSES](POSES.md)记录动作阶段、四肢解剖归属与事件；普攻第08帧attack-contact，施法第11帧cast-release。建议动作单次播放；预览循环用于检查，不能把重复首尾当作移动。

## 验收与剩余范围

[manifest](manifest.json) · [技术校验](validation.json) · [逐像素/Alpha校验](qa/pixel-alpha-audit.json) · [SHA256](SHA256SUMS.txt)

68帧均有独立来源记录、实际提示词、回执与SHA；文件和解码像素无重复。透明尺寸、缺帧和来源路径按清理后的状态复核。少量极弱Alpha散点触及画布边界：attack/E03为2像素max9、E05为4像素max22；主体alpha≥128轮廓均在画内，未将这类低透明度散点等同于主体裁切。

[受击逐帧检查](qa/hit-visual-review.md) · [独立受击复核](qa/hit-independent-review.md) · [普攻检查](qa/attack/DELIVERY.md) · [施法E检查](qa/cast/E-visual-review.md) · [施法W检查](qa/cast/W/static-review.json)

静态已核对方向、四肢/单尾、饰品归属和主要动作阶段，明显多爪、越界光效等已定点AI修正。**动态支撑与衔接仍待实播复核**：普攻W09→10后足收势变化，施法E03→05、11→16和W04→05、11→12的重心/抬爪过渡，以及各组末帧→首帧循环接缝。静态接触表不能证明正常速度无抖动或滑步。[播放验证状态](qa/playback-status.json)

## 模型与来源

[逐图记录索引](generation-index.md) · [官方目标核对与工具证据](qa/model-evidence.md)

本批使用内置image_gen；配置目标gpt-image-2.5-sunburst/max。工具无model/quality选择器，且未披露真实型号/质量，submitted与actual对应值均为null。每张图保留当次配置快照，不能把目标或提示词当作已确认型号。没有切换付费API/CLI。

## 素材清理与继续接手

本目录成品、提示词与引用核实后，source/attack及source/cast中的原生与拒稿图片已清理，仅保留来源文字/SHA及最终PNG、预览、QA与接入文件。根生成缓存位于本次唯一写入范围之外，未作越界删除；公共原有身份/风格参考未动。

[普攻清理](qa/attack/cleanup.json) · [施法E清理](qa/cast/E-cleanup.json) · [施法W清理](qa/cast/W/cleanup.json) · [交接](MERGE_HANDOFF.md) · [状态](STATUS.md)

tools/build_delivery.py重建清单与离线预览数据；tools/build_media.py重建接触表与无损动画预览；tools/audit_pixels.py检查像素重复并重建逐图索引。它们只处理已有独立AI帧，不会创造缺失姿态。

