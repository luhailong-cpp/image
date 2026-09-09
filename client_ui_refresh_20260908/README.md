# 五行奇谈客户端素材接入 · 2026-09-08

本目录把 `E:/work/image` 已有 GPT Image 成果接入 `E:/work/mmorpg-client/Assets/Resources`。主体批次复用已有 GPT Image 成果；后续为登录/选角补生成一张净背景，记录见 `additional/login_background.generation.json`。所有裁切、适配、重采样均在本 image 目录中完成，再按确定的客户端资源路径复制。

## 重复执行

```powershell
python E:/work/image/client_ui_refresh_20260908/sync_assets.py --sync
python E:/work/image/client_ui_refresh_20260908/sync_assets.py --check
```

依赖 Python 3.11+ 与 Pillow。支持 `--client <客户端根目录>`，但首次冻结的 `baseline.json` 绑定一个客户端，不能把同一基线误用于另一工程。无参数仅准备素材并生成盘点报告，不写客户端；`--check` 不写客户端。脚本不调用图片 API、不改 C#、不删除资源、不扫描备份目录、不重写任何已经存在的 `.meta`。

## 游戏可直接读取的新增资源

统一根路径 `UI/Ugui/RefreshV8/`，Resources.Load 时不加 `.png`：

- 39 个组件保留 `qdao_ui_redesign_v5/components/manifest.json` 中原始 `id` 名字，包括三态按钮、页签、卡片、搜索框、框架、面板、十个徽标。全部无动态文字。`refresh_components.json` 保留九宫格、内容边距、最小大小、文本色与缩放轴。
- `hero`：独立透明发带 Q 道童。
- `companion_fox`：独立透明九尾狐灵玥。
- `sanctuary_background`：已有宽屏主城纯场景。
- `login_background`：2026-09-08 官方内置 `image_gen` 以已有登录效果图为参考补齐的无人、无字、无 UI 仙境净底；左侧荷塘、右下宽阔空石台，供独立道童和狐狸叠放。实际原生 1931×814，等比 cover 导出 2560×1080，不冒称原生 2560。原图、完整提示词、参考图和重建脚本在 `additional/`。
- `battle_background`、`battle_loading`、`battle_clouds`：战斗净底、入场插画和真透明云层。
- `companion_hu_tuan_tuan`、`companion_fu_xiao_hu`、`companion_yun_jiu_jiu`：三只已有宠物透明静态资源。可用资源不代表已做动作或每个页面都显示它们。

新 PNG 的 `.meta` 使用由资源路径确定的稳定 GUID：Sprite Single、双线性、sRGB、真 Alpha、无 mipmaps、Full Rect；`spriteBorder` 按组件 `left,bottom,right,top` 合同配置。既有 PNG 大小和 `.meta` 字节保持，仍由原 GUID 引用。横向伸缩控件需要换高度时先整体等比适配高度，再横向九宫格，避免把内嵌标识纵向拉形。

`additional/login_background.png` 已通过官方内置工具补齐并发布；没有调用外部 API。干净 `title_logo.png` 与提取记录已保存在同目录，`prepared/UI/Ugui/RefreshV8/title_logo.png` 提供对应的客户端资源副本。已有登录/选服/选角整屏图仍只作视觉参考，不当作动态页面净底；旧名 `background_ui_uncropped_final` 是透明框板/装饰/人物组合，也不等于纯场景背景。

净背景生成先尝试本地 `referenced_image_paths`，因 Windows 沙箱 `apply deny-read ACLs` 在读取阶段失败、未产图。通过获准的只读 shell 显示内存参考图后，官方内置工具用对话图引用成功生成唯一一张新图。实际生成工具输出已视觉检查无人物/宠物/文字/UI，目标脚点落于连续石台；引擎页面合成验收由客户端主任务继续。

## 原路径更新和保留

- 124 物件图标以已有资源 ID 和原尺寸从美术库最终 PNG 适配，完整入库；当前静态代码未找到 `UI/qdao_v3/icons_weapon` 的直接加载入口，因此只声明资源库已同步，不声称每个图标已显示。
- 22 职业立绘更新原资源路径；`BattleArtCatalog.PortraitsRoot` 动态消费这些 ID。
- 旧 UI 中可精确对应的切片、原子控件、常用兼容控件，以及主城/战斗/过场别名同步到最新正式图。
- 天墉城 36 张 1024 方形地图块与本日 image 归档逐文件 SHA-256 相同，复用已接入素材。脚本仅核验，不覆盖潜在更新的客户端地图。6144 母图为拼接/派生画布，不声称是原生 AI 分辨率。
- 客户端现有八方向行走每方向 8 帧，image 原 v7 每方向 4 帧；不以不同合同替换正常动作。职业动作、怪物动作、特效、数字图集、Buff、场景材质等逐 PNG 留存，并记录原因。
- 新页面通过新控件构建；遗留资源保留用于已有场景和预制体兼容。现有动作/特效不因缺少匹配的新来源被覆盖为静态占位图。

## 验证记录

归档状态（2026-09-09）：当前 `assets_manifest.json` 保存的是 2026-09-08 的同步报告，状态为 `failed`，包含 240 条 `Baseline metadata changed` 和 32 条 `Existing meta changed`。这份记录保留当时的 `.meta` 差异，不能作为客户端同步验收通过的证据；本次归档未重新同步或修改客户端，差异原因与当前状态需在客户端工程中继续核对。

`baseline.json` 是首次接入之前 399 个 Resources PNG 的像素合同、SHA-256 与 `.meta` 哈希。

`assets_manifest.json` 覆盖运行时 Resources 中每一张 PNG：来源路径/哈希、客户端路径/哈希、原始与最终尺寸、处理方法、控件合同，或保留原因。包括其他并行客户端任务增加/修改的素材；脚本记录它们但不回滚。报告只有资源一致性结论，引擎运行与页面事件由客户端 UI 构建任务验收。

美术库 v5/v6 旧清单中的哈希/日期有历史字段；本次同步对实际当前文件算哈希，记录 v7 重新生成/派生关系，不把旧 README 的“未接入”当作当前客户端状态。正式来源的效果图可看 `qdao_ui_redesign_v5/01_login_2560x1080.png`、`02_server_select_2560x1080.png`、`03_character_select_2560x1080.png`、`04_main_city_hud_2560x1080.png`；当前真实游戏主城看 `tianyong_city_6x6/Previews/tianyong_city_master_preview_2048.png`。