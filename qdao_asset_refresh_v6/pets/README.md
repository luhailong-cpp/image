# 五行奇谈 · 四只透明宠物

灵玥、葫团团、符小虎、云啾啾均提供1254×1254真RGBA静态图。已确认的有底设定图逐字节保留，透明版使用内置image_gen参考重绘，再按generate2dsprite处理；清理品红边缘时保留淡紫毛色和各宠物饰物。

|宠物|透明成品|完整提示词|记录|
|---|---|---|---|
|灵玥|[PNG](../../qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png)|[prompt](../../qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.prompt.txt)|[JSON](records/ling_yue.json)|
|葫团团|[PNG](../../qdao_chibi_pets_v1/01_hu_tuan_tuan-transparent_1254.png)|[prompt](../../qdao_chibi_pets_v1/01_hu_tuan_tuan-transparent_1254.prompt.txt)|[JSON](records/hu_tuan_tuan.json)|
|符小虎|[PNG](../../qdao_chibi_pets_v1/02_fu_xiao_hu-transparent_1254.png)|[prompt](../../qdao_chibi_pets_v1/02_fu_xiao_hu-transparent_1254.prompt.txt)|[JSON](records/fu_xiao_hu.json)|
|云啾啾|[PNG](../../qdao_chibi_pets_v1/03_yun_jiu_jiu-transparent_1254.png)|[prompt](../../qdao_chibi_pets_v1/03_yun_jiu_jiu-transparent_1254.prompt.txt)|[JSON](records/yun_jiu_jiu.json)|

[逐件清单](manifest.json)保存尺寸、Alpha、边界与SHA；[验收](validation.json)确认四张透明图、原概念保留和零强品红残色。灵玥实看九个独立尾尖；虎纹、葫芦和仙鹤形象按各自参考保留。

原生生成尺寸按每张record记录。1254为最终画布，部分经过同画布内的等比居中／脚底对齐处理；没有从128小图放大作为正式交付。透明精灵无烘焙名字，临时母图、GIF和切图副本已清理。

```powershell
python -B qdao_asset_refresh_v6/pets/build_manifest.py
```

脚本仅验证和更新清单，不生成图片。重新生成须先实看原概念图，使用完整提示词调用内置生图，再按各record的技能参数处理并实看。当前仅静态美术，未制作宠物动画或接入客户端。
