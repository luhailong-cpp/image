# 绛铃 · 战斗动作

沿用 Image 目录原有绛铃：墨黑短发折绢仙灵、象牙绛红折瓣衣、青玉丝带，右手三铃折扇、左手空手。没有新增角色或移动循环。

## 查看

- [交互预览](preview.html)：六组独立播放、正常 1×、0.25×慢放、逐帧按钮、滑块、深浅/棋盘背景、锚点。
- [当前交付状态](STATUS.md) · [清单](manifest.json) · [SHA256](SHA256SUMS.txt)
- [接入交接](MERGE_HANDOFF.md) · [锁定姿态](POSES.md)

| 动作 | E / W 每向帧数 | 每帧时间 | 每向总时长 | 事件帧 |
|---|---:|---:|---:|---:|
| hit 受击 | 6 | 40 ms | 240 ms | 03 impact |
| attack 普攻 | 12 | 30 ms | 360 ms | 07 attack |
| cast 施法 | 16 | 45 ms | 720 ms | 10 cast |

正式文件在 `runtime/<action>/<E|W>/01.png…`，共68张1024×1024 RGBA透明PNG。E斜前朝右下，W独立绘制为真正斜后朝左上。原生1254×1254，经同一整画布比例1024/1254导出；没有逐帧脚底对齐、镜像、复制平移或插值补帧。悬浮底锚点顶部坐标[512,942]，左下pivot[0.5,0.08]，实际重心反冲保留在图内。

## 动画文件

| 组 | 正常 | 0.25×慢放 | 全帧对照 |
|---|---|---|---|
| hit E | [WebP](previews/hit-E-normal.webp) | [WebP](previews/hit-E-slow025.webp) | [图](qa/technical-contact-hit-E.jpg) |
| hit W | [WebP](previews/hit-W-normal.webp) | [WebP](previews/hit-W-slow025.webp) | [图](qa/technical-contact-hit-W.jpg) |
| attack E | [WebP](previews/attack-E-normal.webp) | [WebP](previews/attack-E-slow025.webp) | [图](qa/technical-contact-attack-E.jpg) |
| attack W | [WebP](previews/attack-W-normal.webp) | [WebP](previews/attack-W-slow025.webp) | [图](qa/technical-contact-attack-W.jpg) |
| cast E | [WebP](previews/cast-E-normal.webp) | [WebP](previews/cast-E-slow025.webp) | [图](qa/technical-contact-cast-E.jpg) |
| cast W | [WebP](previews/cast-W-normal.webp) | [WebP](previews/cast-W-slow025.webp) | [图](qa/technical-contact-cast-W.jpg) |

动画WebP为512像素预览，带棋盘和帧编号；正式PNG仍为1024透明图。预览只缩放合成已生成帧，不创造姿态。预览来源在 `previews/generation.json`。

## 逐图来源

每张正式PNG旁的 `.png.generation.json` 保存模型目标、实际提交字段、实际返回证据、原生尺寸和SHA、导出操作、提示词和参考图。`prompts/`保存实际提示词，`receipts/`保存工具回执及失败记录，`records/`保留历史/拒稿文字来源。图到记录的索引在manifest每帧的sourceRecord中。

本批使用内置 `image_gen.imagegen`，目标 GPT Image 2.5 Sunburst / max。工具无model/quality选择器，实际型号和质量未披露，均如实记为null；没有API/CLI调用。见[当次官方核对](MODEL_VERIFICATION.md)。

## 验收边界

尺寸、alpha、文件/像素重复、缺帧和来源记录由[技术检查](qa/technical-check.json)记录。单帧及编号序列的实际目视检查记录与连续播放状态分开保存于 `qa/visual-review.json`。动画文件帧数、准确时长和解码帧唯一性见[流检查](qa/preview-frame-stream.json)。

浏览器工具的安全策略拒绝本地file协议，并明确禁止通过替代浏览器路径绕过。已提供本地预览页和正常/慢放WebP，但连续播放未实际目视验收；不能把编码/尺寸检查称为动态验收通过。没有读取或接入客户端，实际游戏内大小、锚点适配、事件和战斗衔接均未验证。

本目录保留正式PNG、当前预览和配套文字/工具，不保留工作区原图、拒稿图片或回退图片；历史生成文字记录继续保留。跨窗口原身份/风格参考不删除。宿主生成缓存处于本目录唯一写入范围之外，未清理宿主缓存。
