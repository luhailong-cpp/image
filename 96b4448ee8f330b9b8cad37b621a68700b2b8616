# 五行奇谈 · 人物与宝宝属性面板

2026-09-11 当前无字控件与头像以 [v10 重切说明](../../qdao_ui_style_recut_v10/README.md)和 [31 张属性切片](v2-painted/unity-slices/README.md)为准。遵循指定选角图的深玉绿、象牙米白、暖金与道家 Q 版节庆点缀；其他游戏图仅参考功能。本目录 HTML 交互和整屏主稿保持历史版本，尚未同步 v10 皮肤。

新版 UI 重绘：[人物/宝宝 UI 效果图](v2-painted/README.md)，按用户新参考采用深玉绿控件、米白底和细金边；本目录原 HTML 交互预览仍为第一版。

2026-09-09。本目录提供沿用项目玉绿、米白、暖金美术的两张整屏主稿和可操作 HTML 预览。

| 内容 | 文件 / 入口 |
|---|---|
| 人物主稿，2560×1080 | [01-character_2560x1080.png](01-character_2560x1080.png) |
| 宝宝主稿，2560×1080 | [02-pet_2560x1080.png](02-pet_2560x1080.png) |
| 人物交互预览 | [index.html?panel=hero](index.html?panel=hero) |
| 宝宝交互预览 | [index.html?panel=pet](index.html?panel=pet) |

PNG 整屏用于视觉确认。预览中的角色名、属性值、收益、页签和按钮文字由 HTML 原生文字层绘制；PNG 主稿不作为含动态数据的客户端整屏贴图。

预览支持人物与四只宝宝切换、属性加减和滑杆、方案选择、自动加点、撤销本次分配、确认加点、宝宝参战状态演示，以及返还本次预览已确认的宝宝点数。切换对象或关闭后重开面板，会保留当前页面各对象的独立分配记录。

首次默认展示待确认分配：人物体质 +2、力量 +8，剩余 10 点；灵玥灵力 +6，剩余 6 点。这样可直接核对绿色收益与确认状态。查看未分配初始状态，可使用 [人物 clean 入口](index.html?panel=hero&state=clean) 或 [宝宝 clean 入口](index.html?panel=pet&state=clean)。

所有操作仅保存在当前页面内存。刷新会恢复入口对应的初始状态，包括已经确认的分配和参战状态。基础属性不允许洗回；“返还加点”仅返还本次预览中提交的额外点数，同时撤销未确认分配。

数据与加点收益均用于演示。人物、灵玥的基础显示值参考用户提供截图，其余宝宝数值为虚构示例；`model.js` 的收益系数是交互预览公式，不代表真实游戏规则。当前交付没有接入客户端、账号、服务端或正式存档。

## 复用素材

素材复制到 `assets/`，未调用新生图。人物与宠物使用已有透明 PNG，主城使用已有宽屏纯场景。

| 本目录文件 | 仓库来源 |
|---|---|
| `assets/city.png` | `qdao_chibi_game_pack_v4/main-city_2560x1080.png` |
| `assets/hero.png` | `qdao_chibi_game_pack_v4/hero-transparent_1024.png` |
| `assets/lingyue.png` | `qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png` |
| `assets/hutuantuan.png` | `qdao_chibi_pets_v1/01_hu_tuan_tuan-transparent_1254.png` |
| `assets/fuxiaohu.png` | `qdao_chibi_pets_v1/02_fu_xiao_hu-transparent_1254.png` |
| `assets/yunjiujiu.png` | `qdao_chibi_pets_v1/03_yun_jiu_jiu-transparent_1254.png` |
| 框板、按钮、页签、太极徽标 | `qdao_ui_redesign_v5/components/png/` 下的同名 PNG |

`index.html` 定义页面结构，`panel.css` 定义排版，`app.js` 处理页面交互，`model.js` 管理独立点数状态及演示收益。无需构建即可通过静态文件预览；分享目录时保留这些文件和 `assets/` 的相对位置。
