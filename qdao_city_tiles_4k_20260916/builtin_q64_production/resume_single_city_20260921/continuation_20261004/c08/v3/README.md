# r08_c08 第三版局部候选

[当前 4096×4096 候选](r08_c08.png)已合入三处原生修补：下方金环 `(1024,3072)`、上方石刻／金环 `(2048,1024)`，以及右上蓝灰太极嵌面 `y1024` 色带。第三版 SHA256：`d55428d435ad5147bb46b2c004d05286d3aed450c9d7a399f97b67db2b7f06a2`。

第二、第三次修补均实际使用内置 `image_gen`，分别返回 1254×1254 原生 PNG，并附上 `designs/gameplay-ui/04-guild.png` 作为已确认风格参考。按原像素窗口拼回，外周 24 像素保持原图、到 184 像素处平滑过渡为完整新图；没有放大、变形、模糊或重新锐化。逐像素核对确认窗口外和四条外边不变。

- [当前来源链](r08_c08.png.generation.json)与[精简实际视觉检查](visual-review.json)
- [第二次提示词](../repair-02/prompt.txt)、[第二次生成记录](../repair-02/native.png.generation.json)、[带外周原像素检查图](../repair-02/composite-perimeter-context.png)
- [第三次提示词](../repair-03/prompt.txt)、[第三次生成记录](../repair-03/native.png.generation.json)、[带外周原像素检查图](../repair-03/composite-perimeter-context.png)
- [可复现机械拼合脚本](../rebuild_v2_v3.py)

两处中心色阶已明显改善，外围曲线没有新增双线或明显错位。但旧缝仍在修补窗口之外延伸：上方石刻窗外的竖缝、蓝灰面右边与下方残余色带，以及东西南邻接中已记录的问题仍需后续处理。正式美术、全块连续性及游戏运行验收均未通过。

两张新图配置目标为 `gpt-image-2.5-sunburst / max`；实际模型与质量未披露，记录为 `null`。没有覆盖 v1/v2，也没有改变全局选择指针。
