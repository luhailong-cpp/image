# 葫团团 · 受击 / 普攻 / 施法

仅延续 Image 原有葫团团：白毛、单条青绿毛区尾巴、金发带、玉绿披肩、双前爪抱太极葫芦。E为右下斜正面；W为独立绘制的左上真斜背面。没有走路或跑步动作。

制作尚在进行，最新数量和实际验收结论见 `STATUS.md`。预览入口为 `preview/index.html`，缺帧会明确显示，不填充静态替代帧。

| 动作 | 每向帧数 | 每帧 | 单向总时长 |
|---|---:|---:|---:|
| hit | 6 | 40ms | 240ms |
| attack | 12 | 30ms | 360ms |
| cast | 16 | 45ms | 720ms |

合同共68张，正式路径 `runtime/<action>/<E|W>/<01..N>.png`，1024×1024 RGBA。脚点合同采用顶部坐标[512,942]、左下归一化pivot[0.5,0.08]，导出记录区分原生和最终画布；同方向跨动作共用变换。

每张均由内置 image_gen 单独生成或定点AI编辑。配置目标为用户指定GPT Image 2.5 / max；工具没有model/quality选择器，仅返回image_url与output_hint，因此实际型号与质量全部未确认（null）。没有收费API/CLI。官方核对记录在 `records/model-verification.json`；它只证明产品开放与目标档位，不证明具体调用返回型号。

每张正式PNG旁的 `.png.generation.json` 给出来源、SHA、时间、实际提示词路径与原生尺寸。原生文字记录在 `source/`，实际提示词在 `prompts/`；拒稿保留文字记录但最终不留拒稿图。当前使用的方向设计位于 `design/E.png` 与 `design/W.png`，原有跨窗口身份/风格参考保留在原路径。

最终提供 manifest.json、checksums与技术检查，以及正常速度、0.25倍慢放和逐帧预览。技术文件完整不等于动态验收；客户端接入未执行。
