# 天墉城主城地图 · 6×6

2026-09-08 从本机 `E:/work/mmorpg-client` 同步客户端现有主城资源，保留原始 PNG 字节。这里是当前客户端资源的归档，不代表正在进行的 Q 版重绘已经交付。

## 图片入口

| 内容 | 文件 |
|---|---|
| 完整无网格母图，6144×6144 | [打开完整图](Previews/tianyong_city_master_6144.png) |
| 完整预览，2048×2048 | [打开预览](Previews/tianyong_city_master_preview_2048.png) |
| 原始来源图 | [打开来源图](Previews/tianyong_city_master_source_wide_1254.png) |
| 带行列标记的切图总览 | [打开总览](Previews/tianyong_city_tiles_contact_sheet.png) |
| 可行走区域叠加预览 | [打开叠加预览](Previews/tianyong_walkmask_overlay_2048.png) |
| 36 张正式切图，每张 1024×1024 | [Tiles 目录](Tiles/) |

切图按 6 行×6 列排列，左上为原点；文件名为 `tianyong_r01_c01.png` 至 `tianyong_r06_c06.png`，相邻图块直接贴边拼接。

## 来源与清单

- 完整图、预览、提示词和原始清单来自客户端 `Assets/Art/World/Tianyong/SceneTiles6x6/`。
- 正式切图来自客户端 `Assets/Resources/World/Tianyong/SceneTiles6x6/Tiles/`。
- [原始切图清单](tile_manifest.json) 中的 `file` 可相对此目录查找；`assetRoot` 和 `resourcesPath` 保留客户端的 Unity 路径含义。
- [提示词摘要](PROMPTS.md) 与[原客户端说明](CLIENT_README.md) 原样归档。
- [同步记录](sync_manifest.json) 保存每个来源路径、源文件修改时间、字节数和 SHA-256；复制前后已逐文件核对源文件与副本一致。

本目录共 41 张 PNG（36 张切图、5 张母图/来源图/预览）。Unity `.meta` 文件不属于本美术归档。原图尺寸不等于 AI 原生生成尺寸，来源和放大/拼接方式沿用原始清单说明。
