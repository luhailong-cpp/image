# 道家 Q 版宠物 · 第一组

2026-09-06，共三只原创宠物。沿用主城和发带小道童的青绿、米白、暖金手绘风格；每只采用不同动物轮廓与道家饰物，名字独立记录，未烘焙在图片中。

| 名字 | 类型 | 识别特征 | 图片与提示词 |
|---|---|---|---|
| **葫团团** | 葫芦灵狐 | 雪白软毛、金色发带、青绿尾尖，抱着太极葫芦 | [图片](01_hu_tuan_tuan.png) · [提示词](01_hu_tuan_tuan.prompt.txt) |
| **符小虎** | 符箓虎崽 | 杏金虎纹、额前小符箓、太极铃铛，举爪打招呼 | [图片](02_fu_xiao_hu.png) · [提示词](02_fu_xiao_hu.prompt.txt) |
| **云啾啾** | 云游小仙鹤 | 白羽红冠、青绿翼尖、祥云脚垫，展开小翅膀 | [图片](03_yun_jiu_jiu.png) · [提示词](03_yun_jiu_jiu.prompt.txt) |

## 本轮透明素材

三只均新增1254×1254真RGBA静态图，原概念图保留。

|宠物|透明PNG|透明版提示词|
|---|---|---|
|葫团团|[成品](01_hu_tuan_tuan-transparent_1254.png)|[prompt](01_hu_tuan_tuan-transparent_1254.prompt.txt)|
|符小虎|[成品](02_fu_xiao_hu-transparent_1254.png)|[prompt](02_fu_xiao_hu-transparent_1254.prompt.txt)|
|云啾啾|[成品](03_yun_jiu_jiu-transparent_1254.png)|[prompt](03_yun_jiu_jiu-transparent_1254.prompt.txt)|

[统一清单与验收](../qdao_asset_refresh_v6/pets/README.md)记录真实生成尺寸、处理参数、Alpha和哈希。透明版本按原参考使用内置生图重绘，再清底、对齐并检查毛羽边缘；未做宠物动画或客户端接入。

## 原概念图

### 葫团团

![葫团团 · 葫芦灵狐](01_hu_tuan_tuan.png)

### 符小虎

![符小虎 · 符箓虎崽](02_fu_xiao_hu.png)

### 云啾啾

![云啾啾 · 云游小仙鹤](03_yun_jiu_jiu.png)

## 制作与继续使用

本组使用 Codex 内置图像工具生成。三张均为工具原生输出的 1254 × 1254 RGB PNG，浅米色背景，完整单宠物立绘，文件未做放大。图片完整性、尺寸和视觉检查已完成，校验值见 [manifest.json](manifest.json)。

基础风格参考为 [主城](../qdao_main_city_chibi_v1.png) 和 [发带小道童](../q_daoist_hero_chibi_headband_v3.png)。后两只同时参考前面已经完成的宠物，以统一眼睛、毛羽、金饰和背景的表现。

继续迭代时先查看对应宠物图片，再读取同名 `.prompt.txt`，保持名字、动物种类和上述识别特征一致。原三张是带底色的静态概念图；本轮真透明精灵使用上表的新文件。后续动作需按实际引擎与播放需求另行制作，不把静态交付冒称动画。
