# 五行奇谈 · 旧选服画面与高分辨透明分层

本批在原路径重建了 **12 张旧选服素材**：本目录 5120 × 2160 与 10240 × 4320 各三张分层、根目录两张 5120 × 2160 透明整 UI，以及四张 2560 × 1080 不透明选服视觉稿。原文件名保留兼容；画面语义为选择服务器。v5 已完成的五张标准画面没有重绘或覆盖。

[逐文件记录](manifest_native_q5.json) 保存原哈希、新哈希、尺寸、Alpha、来源与每个控件/文字的位置；[验证结果](validation_native_q5.json) 记录十二图与两组分层合成检查。原生构建入口为 [build_layers.mjs](native_q5/build_layers.mjs)。

## 真正独立的层

| 文件中的名称 | 内容 | 文字与背景 |
|---|---|---|
| `background_ui_uncropped_final` | 玉绿金框、米白板面、标题底板、太极/炉/花装饰与已接受的新版 Q 道童 | 真实透明外缘；没有城市场景、按钮或动态文字 |
| `buttons_uncropped_final` | 分类、搜索、八张卡片、选择摘要和两枚操作按钮；独立图标和默认状态的摆放 | 大部分画布透明；不含底板、人物或动态文字 |
| `ui_uncropped_final_recomposed` | 同尺寸背景装饰层与按钮层的 Alpha 合成 | 仍为真 RGBA，无动态文字 |

根目录两张 `*_5120x2160.png` 透明整 UI 与同尺寸无字合成层内容相同，作为旧路径兼容输出。四张 2560 × 1080 RGB 画面在已接受的 v4 主城上叠加 UI，再单独绘制文字，仅用于视觉参考。

文字唯一来源仍为 [copy.zh-CN.json](../qdao_ui_redesign_v5/copy.zh-CN.json)。[独立文字 SVG](native_q5/labels.svg) 与清单的 `text_placements_2560` 记录全部标签；正式名称“五行奇谈”已确认，八服、状态和默认选择仍是现有演示数据。透明素材中没有文字烘焙，也没有把带字整屏放入其中一层来冒充拆层。

按钮层是一个默认状态的组合示例。客户端应使用 [39 个独立控件](../qdao_ui_redesign_v5/components/README.md) 或 [原尺寸旧路径控件](../exact_qdao_slices/README.md)，根据真实数据切换 selected/disabled、状态点、推荐与文字；合成 PNG 不负责交互。

## 布局与来源

原生设计坐标为 2560 × 1080；清单保存 `control_placements_2560`、`text_placements_2560` 和 `hero_placement_2560`。5120 与 10240 输出按 2 倍与 4 倍绘制矢量，九宫格目的切边对齐整数设计像素，避免抗锯齿细缝。徽标与人物整体等比缩放。

背景装饰中的人物沿用 [1024 透明 Q 道童](../qdao_chibi_game_pack_v4/hero-transparent_1024.png)；RGB 视觉稿沿用 [2560 主城](../qdao_chibi_game_pack_v4/main-city_2560x1080.png)。人物为现有位图重采样，框板和控件是原生 SVG；不会把 10240 输出冒称为 10240 原生 AI 图片。

## 重建

需要 Node 22+ 和已安装的 Sharp。在仓库根目录执行：

```powershell
node q_daoist_login_ui_uncropped_highres_final_layers/native_q5/build_layers.mjs --sharp '<已安装 node_modules>/sharp'
```

构建使用本库审计清单定位恰好 12 个旧文件，只覆盖这些交付和本目录的原生源/清单。所有临时检查图仅在内存中查看，本批没有添加过程 PNG。分层的效果、尺寸和 Alpha 已验证；未修改或接入未知客户端。