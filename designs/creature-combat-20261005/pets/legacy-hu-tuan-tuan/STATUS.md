# 交付状态

2026-10-05：葫团团六组动作完成，共68张独立绘制的1024×1024透明RGBA正式帧。

| 动作 | E | W | 每帧 |
|---|---:|---:|---:|
| 受击 hit | 6 | 6 | 40ms |
| 普攻 attack | 12 | 12 | 30ms |
| 施法 cast | 16 | 16 | 45ms |

没有走路或跑步动作。原身份、坐姿支撑、太极葫芦及E斜正面／W真斜背面保持。

技术检查覆盖68帧数量、尺寸、透明通道、哈希、来源链和像素不重复。全部帧逐张查看，最终六组总览、正常与0.25倍浏览器播放抽样及逐帧控件已复核；12个APNG帧数与时长检查通过。浏览器有调度延迟，未宣称游戏引擎帧率或客户端验收。

[交互预览](preview/index.html) · [说明及APNG](README.md) · [技术清单](manifest.json) · [最终视觉检查](records/final-visual-review.json) · [交接说明](MERGE_HANDOFF.md)

已清理74张中间／来源图片，正式帧、当前方向设计、配套预览和逐图文字记录保留。最终检查以manifest和final-visual-review中绑定的正式帧SHA为准；其他带pre-registration或早期时间的报告仅记录制作历史。

配置目标gpt-image-2.5-sunburst/max。使用内置image_gen；宿主未披露实际型号与质量，实际字段为null。未使用收费API/CLI，未接入客户端，未操作Git或其他仓库。
