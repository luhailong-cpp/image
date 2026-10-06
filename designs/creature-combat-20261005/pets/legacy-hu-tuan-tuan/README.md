# 葫团团 · 受击 / 普攻 / 施法

仅延续 Image 原有葫团团：白毛、单条青绿毛区尾巴、金发带、玉绿披肩、双前爪抱太极葫芦。E为右下斜正面；W为独立绘制的左上真斜背面。没有走路或跑步动作。

68张正式帧已完成。打开[六组交互预览](preview/index.html)，可正常播放、0.25倍慢放、暂停与逐帧查看。[交付状态](STATUS.md)、[帧清单与SHA](manifest.json)、[最终视觉检查](records/final-visual-review.json)分别记录制作、技术和视觉检查范围。

| 动作 | 每向帧数 | 每帧 | 单向总时长 |
|---|---:|---:|---:|
| hit | 6 | 40ms | 240ms |
| attack | 12 | 30ms | 360ms |
| cast | 16 | 45ms | 720ms |

合同共68张，正式路径 `runtime/<action>/<E|W>/<01..N>.png`，1024×1024 RGBA。脚点合同采用顶部坐标[512,942]、左下归一化pivot[0.5,0.08]，导出记录区分原生和最终画布；同方向跨动作共用变换。

每张均由内置 image_gen 单独生成或定点AI编辑。配置目标为用户指定GPT Image 2.5 / max；工具没有model/quality选择器，仅返回image_url与output_hint，因此实际型号与质量全部未确认（null）。没有收费API/CLI。官方核对记录在 `records/model-verification.json`；它只证明产品开放与目标档位，不证明具体调用返回型号。

每张正式PNG旁的 `.png.generation.json` 给出来源、SHA、时间、实际提示词路径与原生尺寸。原生文字记录在 `source/`，实际提示词在 `prompts/`；拒稿保留文字记录但最终不留拒稿图。当前使用的方向设计位于 `design/E.png` 与 `design/W.png`，原有跨窗口身份/风格参考保留在原路径。

| 组 | 正常 APNG | 0.25倍 APNG | 逐帧总览 |
|---|---|---|---|
| 受击 E · 6帧 | [播放](preview/hit-E-normal.png) | [慢放](preview/hit-E-slow.png) | [查看](preview/contact-hit-E.png) |
| 受击 W · 6帧 | [播放](preview/hit-W-normal.png) | [慢放](preview/hit-W-slow.png) | [查看](preview/contact-hit-W.png) |
| 普攻 E · 12帧 | [播放](preview/attack-E-normal.png) | [慢放](preview/attack-E-slow.png) | [查看](preview/contact-attack-E.png) |
| 普攻 W · 12帧 | [播放](preview/attack-W-normal.png) | [慢放](preview/attack-W-slow.png) | [查看](preview/contact-attack-W.png) |
| 施法 E · 16帧 | [播放](preview/cast-E-normal.png) | [慢放](preview/cast-E-slow.png) | [查看](preview/contact-cast-E.png) |
| 施法 W · 16帧 | [播放](preview/cast-W-normal.png) | [慢放](preview/cast-W-slow.png) | [查看](preview/contact-cast-W.png) |

正式帧通过68/68数量、1024×1024 RGBA、真实透明、SHA、来源记录和解码像素不重复检查。最终画布采用同方向固定变换：原1024画布整体缩至768，E贴入偏移[43,230]，W偏移[210,253]；同方向跨动作一致，没有逐帧包围盒对齐或插帧。[注册记录](records/final-registration.json)保存变换前后哈希。

全部帧已逐张查看，最终六组总览与浏览器正常／0.25倍播放已复核，六组逐帧按钮均已操作。播放复核采用现场截图抽样，没有保存连续录像；浏览器曾报告调度延迟，因此不作为游戏引擎帧率验收。12个APNG的帧数与时长元数据均通过[检查](records/apng-validation.json)。保留轻微手绘轮廓变化，未发现明显多肢、尾巴数量或身份偏移问题。

已按素材保留规则清理74张来源／中间图片，保留正式帧、当前E/W方向设计、必要预览及全部文字证据，详见[清理记录](records/cleanup.json)。检查中的提示项说明宿主未披露实际模型／质量，以及按规则删除的历史来源；不代表缺少正式帧。原共享身份与风格参考未改动。

客户端接入未执行，未读取客户端或其他仓库。接入字段与复核方法见[交接说明](MERGE_HANDOFF.md)。
