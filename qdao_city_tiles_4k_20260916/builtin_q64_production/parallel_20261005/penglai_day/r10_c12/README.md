# r10_c12 原生细节候选

已补齐16张原生1254×1254细节图，按每张1024×1024核心区域拼成4096×4096候选。没有放大最终像素。

- [当前完整像素候选](tiles/r10_c12-candidate.png)：SHA256 `b876e1fa659a138ce8a290b0cda475351ab40ec36b340e2fd79b9be1cdaf48cc`。
- [覆盖预览](current-preview.png)为缩小的检查图，不用于正式切块。
- [原生来源和逐像素验证](evidence/native-provenance-audit.json)全部通过。
- 内部、相邻图块拼缝修补与视觉验收见 `repairs/`，该原始候选不代表正式验收。整城与客户端仍未验收。
- p14采用新版北邻c12jointv3的原生锚点，记录见 [参考派生记录](guides/p14-north-v3.png.generation.json)及 [锚点制作脚本](prepare_north_v3.py)。

本批均使用内置image_gen；配置目标为 ChatGPT Images 2.5 / gpt-image-2.5-sunburst / max。工具未提供型号和质量选择器，也未披露实际型号与质量，因此各图记录中的实际值均为null，不能把配置目标当作已确认返回值。

| 原生图 | 来源记录 | 实际提示词 |
|---|---|---|
| [p11](native/p11.png) | [生成记录](native/p11.png.generation.json) | [提示词](prompts/p11.prompt.txt) |
| [p12](native/p12.png) | [生成记录](native/p12.png.generation.json) | [提示词](prompts/p12.prompt.txt) |
| [p13](native/p13.png) | [生成记录](native/p13.png.generation.json) | [提示词](prompts/p13.prompt.txt) |
| [p14](native/p14.png) | [生成记录](native/p14.png.generation.json) | [提示词](prompts/p14.prompt.txt) |
| [p21](native/p21.png) | [生成记录](native/p21.png.generation.json) | [提示词](prompts/p21.prompt.txt) |
| [p22](native/p22.png) | [生成记录](native/p22.png.generation.json) | [提示词](prompts/p22.prompt.txt) |
| [p23](native/p23.png) | [生成记录](native/p23.png.generation.json) | [提示词](prompts/p23.prompt.txt) |
| [p24](native/p24.png) | [生成记录](native/p24.png.generation.json) | [提示词](prompts/p24.prompt.txt) |
| [p31](native/p31.png) | [生成记录](native/p31.png.generation.json) | [提示词](prompts/p31.prompt.txt) |
| [p32](native/p32.png) | [生成记录](native/p32.png.generation.json) | [提示词](prompts/p32.prompt.txt) |
| [p33](native/p33.png) | [生成记录](native/p33.png.generation.json) | [提示词](prompts/p33.prompt.txt) |
| [p34](native/p34.png) | [生成记录](native/p34.png.generation.json) | [提示词](prompts/p34.prompt.txt) |
| [p41](native/p41.png) | [生成记录](native/p41.png.generation.json) | [提示词](prompts/p41.prompt.txt) |
| [p42](native/p42.png) | [生成记录](native/p42.png.generation.json) | [提示词](prompts/p42.prompt.txt) |
| [p43](native/p43.png) | [生成记录](native/p43.png.generation.json) | [提示词](prompts/p43.prompt.txt) |
| [p44](native/p44.png) | [生成记录](native/p44.png.generation.json) | [提示词](prompts/p44.prompt.txt) |

