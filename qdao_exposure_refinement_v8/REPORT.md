# 五行奇谈 · 曝光修复交付报告

**已完成并通过验收**。生成时间：2026-09-09 19:46:27 UTC。

[打开逐文件搜索与前后对照](index.html) · [处理清单](processing.json) · [验收记录](validation.json)

| 扫描登记 | 已修复 | 本轮保留 | 失败文件 | 待完成 |
|---:|---:|---:|---:|---:|
| 2,494 | 953 | 74 | 0 | 0 |

本轮处理 1,027 个文件：修正 953 个、原样保留 74 个。另有归档保留 1,467 个，不计入本轮处理量。只有已发布且通过对应哈希验收的文件计入“已修复”。

初次扫描 2,459 个视觉文件；latest 快照新增 35 个路径、更新 13 个已有路径。合并去重后登记 2,494 个路径，其中 1,027 个进入本轮处理清单。参考、诊断和归档文件单列保留。

## 处理结果

明亮场景重点控制天空、云雾和亮地面；人物与图标使用轻档，保留肤色、白毛、金饰与暗部层次。天墉城地图已有清晰的石路、瓦顶和树林层次，保留原亮度的原因是避免暗部继续变重。具体处理状态见逐文件表。

| 方案 | 清单文件数 | 用途 |
|---|---:|---|
| 明亮场景（scene） | 28 | 重点收住天空、云雾与亮地面的中高光，保留暗部和原有配色。 |
| 整屏界面（screen） | 18 | 降低登录、选服、选角等整屏视觉的亮度，照顾人物与背景的层次。 |
| 米白面板（ui） | 273 | 控制米白底、金边和浅色条目的亮度，保留边缘与原有纹理。 |
| 界面轻调（ui_soft） | 34 | 较轻地调整界面装饰与控件，保护可读性及按钮状态区别。 |
| 人物轻调（character） | 173 | 轻压皮肤、白衣与白毛高光；同一套动作使用一致规则。 |
| 图标轻调（item） | 422 | 轻压金属与浅色装饰反光，保留物件的小尺寸辨识度。 |
| 云层轻调（cloud） | 5 | 收住明亮云气，保持透明度与原有层次。 |
| 原样保留（preserve） | 74 | 已合适的地图、功能文字、遮罩、诊断和参考文件保持原样。 |

这些是同源分组的固定规则；同一图像的别名共用结果。透明度、透明区域隐藏 RGB、地图切片、图集和 GIF 结构由独立验收检查。

## 代表图前后对照

HTML 页并列显示原图与正式路径，图像可点击查看原尺寸。此报告不另生成对比彩图。

| 代表图 | 调色前原图 | 正式文件 | 亮度（0–100） |
|---|---|---|---|
| 登录整屏 | [原图](backups/6dbd46f6162c690d9657f81e81f3eba8ba5172f192f72f81a6fd052961f503d9.png) | [正式文件](../qdao_ui_redesign_v5/01_login_2560x1080.png) | 63.9 → 57.7 |
| 选择服务器 | [原图](backups/93c1c31239919d3d0c90bbdfd548a6ea104722e0b6a9f3b6ae92fc98a2dae407.png) | [正式文件](../qdao_ui_redesign_v5/02_server_select_2560x1080.png) | 74.7 → 65.5 |
| 选择角色 | [原图](backups/cdce850b6057524c2f3e23f7181b37c6bafcf02a8eccf10f76c69a7cbcd79bfe.png) | [正式文件](../qdao_ui_redesign_v5/03_character_select_2560x1080.png) | 70.1 → 62.2 |
| 明亮主城 | [原图](backups/c4eaa4e5edd758b9bebab50da88e887aac4df53b211298134b607508ec7e5069.png) | [正式文件](../qdao_main_city_chibi_v1.png) | 64.9 → 57.3 |
| 战斗场景 | [原图](backups/bb7b9cd21ea4ebabb65a0ce8c5038f4da7372d53c83bef01135ec190d5550db0.png) | [正式文件](../qdao_ui_redesign_v5/05_battle_scene_2560x1080.png) | 65.6 → 57.5 |
| 同期更新人物 · latest 原图 | [原图](backups/b45c42d320d615f16c1f65ffc3b13f0a5c3bee63d2692cb2e7846a0a79185723.png) | [正式文件](../q_daoist_character_pack_4096/01_ice_sword_girl_transparent_4096.png) | 61.6 → 58.1 |
| 人物动作 | [原图](backups/dac56ca8b152e7ce32416c5e86aad1dd545a31b82bdc8e39f38c0726ccb710b0.png) | [正式文件](../character_move_8dir/east_frame_01.png) | 50.7 → 48.8 |
| 白色宠物 | [原图](backups/db42c60f28754b4d4093ceee874b585926cc10bf118a00462af8e4188168c329.png) | [正式文件](../qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox.png) | 90.7 → 83.8 |
| 米白界面面板 | [原图](backups/d5e54ecd25e741f527c0f397ebc557f4997cea85ddb1bafd1bdb053bfe140b26.png) | [正式文件](../qdao_gpt_image2_refresh_v7/ui/derived/components/main_frame.png) | 87.7 → 78.6 |
| 玉绿选中态 | [原图](backups/1dfb2ff3a2f737a33c9e73aa7e90c1ae3864707200c7682c1a1fb566b67e4399.png) | [正式文件](../qdao_gpt_image2_refresh_v7/ui/derived/components/list_row_selected.png) | 64.6 → 61.4 |
| 物件图标 | [原图](backups/94c667cabb2f6d2271ae772fa7f1b9db8f8c37b8a318b338a2ce0eb82a37efe6.png) | [正式文件](../q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/west_eight_immortals_redrawn_100_600x600/001_daoist_saber.png) | 53.9 → 53.0 |
| 天墉城地图 · 保留原亮度 | [原图](backups/46d967e6d6d93bf91ec463287a9e19e9f251c270d4af86768ebd6b23aa8f4730.png) | [正式文件](../tianyong_city_6x6/Previews/tianyong_city_master_preview_2048.png) | 52.3 → 52.3 |

亮度来自匹配当前处理哈希的验收结果，使用可见区域 alpha 加权的 sRGB 亮度均值。SVG 显示第一张内嵌 PNG、GIF 显示第一帧，完整数据见验收记录；未统计的文件不填造数值。

## 验收与同期更新

验收状态：`passed`；与当前处理清单的哈希对应：是。

验收错误 0 条，提示 124 条。图集原有差异与新增失败分开记录。

124帧图集与独立图标在本轮之前已有像素版本差异；本轮分别修正曝光且未增加不匹配像素，不宣称二者逐像素一致。

同期素材以 2026-09-09 18:05:06 UTC 的 latest 原始快照为准，其中包含 13 个更新人物路径。表内标注“latest”的文件使用该快照作为调色前基线；这是当时捕获的原字节，不代表持续跟踪其他任务之后的修改。

[latest 原始快照清单](supplementary_inventory.json)

## 原图备份与恢复

原图保存在 `backups/<原图SHA-256>.<原扩展名>`，处理清单保存每个正式路径的备份对应关系。重复运行调色从原图开始，避免在已调暗的结果上继续叠加。

在仓库根目录运行以下命令可恢复本轮记录的原图：

```powershell
python qdao_exposure_refinement_v8/tools/refine_library.py restore
```

恢复会替换本轮正式路径；若文件已经被其他任务再次修改，恢复脚本会拒绝覆盖。

## 范围与限制

- 调色可降低已有高光，无法恢复原图中已经剪切成纯白的细节。
- 数值验收补充视觉检查，不能单凭亮度占比判定白毛、纸底或发光效果是否过曝。
- 本轮处理仅限此素材仓库，不推送远端，不写入客户端工程。
