# 赤砂魁 · 战斗动作

本包沿用 Image 原有陶塑小守卫身份，E/W 两向受击、普攻、施法共68张正式帧已落盘，六组静态全帧和技术检查完成。连续播放视觉待验，未接入客户端；详细状态见 [STATUS.md](STATUS.md)。

|动作|每向帧数|帧时长|单次时长|
|---|---:|---:|---:|
|hit 受击|6|40ms|240ms|
|attack 普攻|12|30ms|360ms|
|cast 施法|16|45ms|720ms|

合同共68张1024×1024 RGBA，正式路径为 `runtime/<action>/<E|W>/<01..N>.png`。E真实斜前朝右下，W独立后视朝左上；双臂双腿、无翼和可见尾，解剖右手握短玉锤，窑炉固定背中央。原 W 静态持锤侧与 E 不一致，本批新绘 W 统一到 E 的解剖右手。姿态阶段和原图依据见 [POSES.md](POSES.md)。

[交互预览](preview/index.html) 每组独立播放，左侧原时间，右侧0.25倍，支持暂停、上一帧/下一帧及滑块。APNG保留45ms等精确帧时长，不使用GIF的10ms量化。预览是导出帧容器，未使用插值。

|组|全帧|原时间 APNG|0.25倍 APNG|
|---|---|---|---|
|hit E|[全帧](preview/hit-E-contact.png)|[原速](preview/hit-E-normal.png)|[慢放](preview/hit-E-slow025.png)|
|hit W|[全帧](preview/hit-W-contact.png)|[原速](preview/hit-W-normal.png)|[慢放](preview/hit-W-slow025.png)|
|attack E|[全帧](preview/attack-E-contact.png)|[原速](preview/attack-E-normal.png)|[慢放](preview/attack-E-slow025.png)|
|attack W|[全帧](preview/attack-W-contact.png)|[原速](preview/attack-W-normal.png)|[慢放](preview/attack-W-slow025.png)|
|cast E|[全帧](preview/cast-E-contact.png)|[原速](preview/cast-E-normal.png)|[慢放](preview/cast-E-slow025.png)|
|cast W|[全帧](preview/cast-W-contact.png)|[原速](preview/cast-W-normal.png)|[慢放](preview/cast-W-slow025.png)|

每张独立内置 image_gen 调用，实际 prompt 在 `prompts/`，工具返回文字及源路径在 `records/`，PNG旁 `.generation.json` 记录目标、参数、SHA、原生尺寸、整画布导出和参考证据。[生成索引](generation-index.json) 对应逐图记录。目标 GPT Image2.5 Sunburst/max，工具未开放型号/质量参数，实际返回也未披露，故 submitted model/quality 与 actualModel/actualQuality 均为 null；目标不冒充实际选择器。

[manifest.json](manifest.json) 提供帧号、方向、时长、名义pivot `[0.5,0.08]` / 顶部锚点 `[512,942]`、事件、像素边界和SHA。[validation.json](validation.json) 区分尺寸/alpha/缺帧/重复/引用与预览时间检查，和实际视觉/动态验收。[SHA256SUMS.txt](SHA256SUMS.txt) 为正式PNG校验表。

导出只对完整原生方形画布统一等比缩放，不逐帧裁边、移动脚点、镜像或补帧。少量原生alpha=1边缘残点保留，主体边界另以alpha≥16记录供检查。所有动作保持同方向统一导出坐标；名义pivot不表示已经实测客户端挂接。

浏览器安全策略拒绝自动打开本地 `file:` 预览，没有绕过；实际连续播放美术验收未完成，不能用文件齐全或预览时长检查替代。可在本机直接打开预览自行复核。客户端接入、场景脚点及引擎内动作切换尚未验证。

已修订的错帧及残余脚位/尺度变化见 [静态复看记录](VISUAL_REVIEW.md)。本目录只保留正式图片及所需预览；加工参考裁图、重复检查图已按 [清理记录](cleanup.json) 删除，prompt、模型/质量和来源文字完整保留。历史生成输入的当前审计SHA不冒充原提交字节；旧runtime版本可追溯到 `records/superseded/` 的文字来源记录。

构建脚本 `tools/package.py` 只从正式帧重建清单/校验/预览，`tools/finalize.py` 检查引用和APNG时长；它们不生成动作。`tools/ingest.py` 依据receipt导出并保留真实源证据。任何再生成均须内置image_gen。
