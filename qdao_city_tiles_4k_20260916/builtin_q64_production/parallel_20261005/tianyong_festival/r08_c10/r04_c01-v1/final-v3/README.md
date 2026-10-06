# r04_c01 局部交付

终检通过本1254×1254局部补片及配套回接条，未接入根current。`r04_c01-joined.png` SHA256为 `8b8519ad0e04df77272a33da2917aef665c37e2599a63d906519465c9ab3a2f5`。接入使用本目录，不使用final-v1/v2。

窗口在r08_c10中的LTRB为 `[-115,2957,1139,4211]`，全局 `[36749,31629,38003,32883]`。`r04_c01-core1024.png` 核心对应r08_c10 `[0,3072,1024,4096]`。所有成品像素来自原生生成或原邻片，没有放大6144参考布局。

五个补丁须一起应用，所需原来源路径与SHA完整列在manifest.json。

| 文件 | 目标图块 | 块内LTRB |
|---|---|---|
| new-r08_c10.png | r08_c10 | [0,2957,909,4096] |
| return-r08_c10.png | r08_c10 | [909,2957,973,4096] |
| return-r08_c09.png | r08_c09 | [4032,2957,4096,4096] |
| return-r09_c10.png | r09_c10 | [0,0,973,96] |
| return-r09_c09.png | r09_c09 | [4032,0,4096,96] |

暖中板选自repaired-v1；下部选自下移512作画、下627为真实上下文的shifted-curve-v2；左石面和最后白边微区选自第7张内置AI修复left-repair-v1。下部完整双轮廓作最大24px水平有界回接、垂直0；未知区位移连续延伸。最后白边微区使用同一真实AI高光形状，按可见上端和真实native下端作单调C1配准，最大水平21.892px，输出只选微区。没有程序绘线或接入40px错稿。

终检实看整片、左右回接、底角、上下拼合和白边微修前后。底部18个轮廓点及左侧5个端点相对原来源误差≤1px，白边5–7px宽且连续，无7px骤断或双影。左右最外圈及底部最后19行逐像素回到原来源。机械色彩修正总场每通道≤12；AI重绘高光属于实际选取的新图像内容，不是色差校正。

逐图原字节、prompt、实际request、工具output_hint、宿主路径、SHA及时间证据沿generation-chain.json可追溯，累计7次内置生成。配置目标为gpt-image-2.5-sunburst/max；实际型号/质量仍为null，generatedAt未知，observedCompletionAt单独保存。

visual-review.json含独立实看终检结论；measurements.json含原像素测量；result.json为交付入口。formalAccepted和全图几何/导航验收保持false。本次没有修改根current、progress、source-checkpoint或completion目录。

来源继承问题：左c09条在本窗口y115和y1139已有横向色阶，原context中可直接核对，已单列而未改外部来源。c09上游仍是WIP。本局部接受不代表整个4096图块或整城正式验收；北侧后续邻片仍需按真实重叠像素接合。
