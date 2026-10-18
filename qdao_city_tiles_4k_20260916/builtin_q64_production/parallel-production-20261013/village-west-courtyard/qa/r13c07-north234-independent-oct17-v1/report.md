# r13_c07 北 N02–N04 独立原像素 QA

结论：局部通过，N03 左岩面保留未过。`formalAccepted=false`，未进行整图验收。

- N02 主体局部通过：band2 的 x[1024,2048) 已查看范围衔接自然；右侧 N03 重叠截痕不包含在通过范围。
- N04 与 cross3 局部通过：水纹、白浪及相邻回接未见硬直切边或新三角残片。
- 旧内部问题 context `[3185,470,3250,535]` 局部解决：old-triangle 图中水面与浪花连续，旧三角残片不可见。
- N03 未过：context `[2048,210,2448,270]`，candidate `[1933,95,2333,155]`；combined/band3 y 约345，cross2 y 约345。近水平纹理截断跨过阴影和受光岩面，上下色面与笔触密度在同一窄行突变。它并非随岩体走向延伸的自然裂缝。对应 N03 与 N03-v2 原生源 native `[0,722,400,782]`（截痕 y 约742）均已原尺度查看，v2 左部仍保留该截痕。
- N03 其余所见区域未见新增硬边，但不能因此把 N03 整体标为通过。已两次 AI 修复的当前残留按 pending 保留，后续集中处理。

六张指定 PNG 均以 `view_image(detail="original")` 查看，没有缩放或重绘；额外查看了 N03/N03-v2 原生源以核对截痕。报告不修改任何图片。

冻结版本：

- assembly：`5d383dc88e859311e6a0d77d9e0fb552b8f5ac1e1c08723a708c964bc7d6c5b0`
- context：`ce01ac0e6dcbf52a1a9b1275c8723db3f04100892aa0b71dc46c5fd8b51cb353`
- candidate：`38dfaa88dafe0136ee8c803ebaf26d70e766adc7c8c2ea58cb81dad322581f8b`
- 北 anchor：`99f50735f137c049b46ad315c5ea11873f9a30f25014561dcee25aaaec3e6f72`

生成与来源核验：67个 manifest 可达文件 pin 全部符合预期；4份 N02/N03/N04/N03-v2 generation 回执的原始工具文件、归档图和请求哈希均已核实。4图实际均为 RGB 1254×1254，原始工具文件与 native 归档逐字节一致。回执记录 route=builtin、actualModel=null、resampled=false；不能把未知型号标为 2.5。

4次按 source-layer-id 的独立源回放均为零差异；合并回放及 candidate 核心裁切也为零差异。这些只证明来源与操作一致，不作为视觉通过依据。

检查图的冻结北邻绑定：combined 由北 anchor `[0,3981,4326,4211]` 与当前 context `[0,115,4326,1115]` 上下原像素连接，再按各 combinedBox 取图。六张检查图重建均为零差异。五张 band/cross 的北邻前230行及修复重叠 anchor 范围均在 report.json 记录坐标与 decoded-RGB SHA256，不依赖最新 r12c07 west 版本的全文件 hash。核心边界为 combined y230；残留截痕位于 combined y345 / context y230。

N01 尚未修复验收；西 W1 context `[150,450,240,560]` 仍为范围外 pending。南、西冻结版只作为来源，不在本报告重复验收。较新 root 条目若有，只列入 report.json 的 newerRootEntriesObservedNotIngested，不切换本次输入。

完整来源、每张 crop 的 PNG/像素哈希、坐标、冻结 anchor 绑定、局部状态见 `report.json` 和 `sourcepins.json`。全部报告文件校验值见 `SHA256SUMS.txt`。
