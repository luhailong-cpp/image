# UI 素材清理交接（2026-09-20）

## 用户目标与当前边界

用户希望继续清理 E:/work/image 内无用图片、过程图和确认可重建的副本，包括 Git 已追踪文件及本地文件；保留原图、必要脚本与清单。用户此前已授权清理后 commit。最新要求是先提供详情，由新窗口接续。本轮除本交接文档外没有新增修改、删除图片、commit 或 push。

本轮重点目录：

1. E:/work/image/q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic
2. E:/work/image/q_daoist_login_ui_uncropped_highres_final_layers

另一个已讨论目录 E:/work/image/exact_qdao_slices 是现行原尺寸 UI 资源路径，本轮未删；104 个文件约 3.80 MiB，含 50 张 PNG。

所有数字均为本地文件逻辑体积、单位 MiB，不是游戏包体或 Git 历史体积。删除工作区文件并提交不会自动清除 Git 历史中的旧图片。本任务不包含历史重写、强推或 Git 内部清理。

## 1. 原子控件目录：134.07 MiB

共有 181 个文件、148 张 PNG。根目录文件约 9.95 MiB；svg_q5 目录 23 个文件约 13.21 MiB；qstyle_redrawn_600x600 目录 131 个文件约 110.92 MiB。

### 已核实用途

- 根目录控件、徽标与图集仍列在 qdao_ui_style_recut_v10/source-map.common.json 中。目录名老、带 redrawn 或 final，不表示内容已废弃。
- README_NATIVE_Q5.md 说明该目录控件已沿原路径更新，当前构建入口转到 v10；icon_leaf.png 是桃灵兼容别名。
- ai_qstyle_badges_sheet_chroma.png 虽保留 chroma 名字，说明文档将其列为真透明徽标图集。不能仅凭名称判为色键过程图。
- client_ui_refresh_20260908/sync_assets.py 的 build_plans 仍把部分原子件映射到 UI/Ugui/Native，以及 UI/qdao_v3/ui 的别名。
- wire_qdao_v3_assets.py 也引用该目录，但它包含旧仓库布局假设；存在脚本引用不等于当前客户端运行时直接读取此源目录。
- 当前客户端 QdaoRefreshArt.cs 的加载根路径为 UI/Ugui/RefreshV8/，QdaoServerSelectView 使用这套路径的 tab_selected、server_card_wide_* 等控件。不能把旧导入映射说成当前客户端逐张仍在使用。
- qstyle_redrawn_600x600 包含 100 + 24 枚 600×600 物件图标，以及 FairyGUI 图集，不是整目录过程截图。
- 图集 qstyle_redrawn_600x600/fairygui_atlas/qstyle_fairygui_atlas_600.png 为 57,302,979 字节，约 54.65 MiB。qdao_asset_refresh_v6/icons/build_atlas.py 根据 124 个图标与 JSON/XML 几何组装图集，因此它是可核验的派生候选；本轮尚未执行重建或确认客户端是否需要这份打包输出，不能直接称为可删。
- 注意 build_atlas.py 的 --check 也会写 validation.json。接续审计不能假定所有 --check 都纯只读。

### 风格抽查结论

实际查看了：

- docs/references/ui-style-20260910.png（指定风格参考）；
- designs/team-ui-v2/team-ui-v2.png（design 效果稿）；
- 原子目录 server_card_bg_wide_selected_green.png；
- 原子目录 icon_pagoda.png。

抽查控件与 design 采用相近的玉绿、米白、金色，但并非完全一致：选中卡片的多层金边更厚，绿底和侧边花饰更突出；宝塔徽标的金属高光与浮雕体积更强。design 整屏的纸面、细线条和内容层次更轻。用户所说的风格差异有实际依据；不能拿历史“验收通过”的文字否定用户观察，也不能仅凭抽查推断 148 张 PNG 全部不合格。

风格需要替换与图片可以删除是两件事。当前用户没有要求本轮重新生图或重绘；先去重，保留正式资源与布局合同，另行明确替换范围。

## 2. 高分辨率分层目录：100.00 MiB

13 个文件：6 张 PNG 共约 69.10 MiB；3 个 SVG 共约 30.81 MiB；2 个 JSON、1 个 MD、1 个 MJS。

名称写 login，但实际内容是选服 UI 的背景装饰层、默认按钮组合层和两层合成图，不是独立原生 10K 生图。

| PNG 文件（该目录下） | MiB |
|---|---:|
| q_daoist_login_background_ui_uncropped_final_10240x4320.png | 18.34 |
| q_daoist_login_background_ui_uncropped_final_5120x2160.png | 5.59 |
| q_daoist_login_buttons_uncropped_final_10240x4320.png | 11.37 |
| q_daoist_login_buttons_uncropped_final_5120x2160.png | 3.52 |
| q_daoist_login_ui_uncropped_final_recomposed_10240x4320.png | 23.28 |
| q_daoist_login_ui_uncropped_final_recomposed_5120x2160.png | 6.99 |

### 本轮实际哈希核对

读取 qdao_festival_refinement_20260910/scenes-sync/server/staged-validation.json，通过各项 path 和 staged 字段定位输出：

- 上述 6 张正式 PNG 的对应节庆暂存文件全部仍存在。
- 6 对文件的 SHA-256 全部一致。暂存副本与正式图之间可以优先考虑去重，但删除前仍须确认保留位置、发布/校验依赖和恢复方式。
- 对照 qdao_ui_style_recut_v10/staged 下相同路径，只有两张 buttons 层与现行图一致；另四张 background/recomposed 均不同。旧 v10 暂存不能作为这些现行图的恢复副本。
- 在客户端 Assets 与 Docs 的 cs/json/md/prefab/unity 文本中，没有搜到这组 uncropped 文件名/目录的直接引用。这不等于完成所有间接、动态或二进制引用审计。

### 最新来源与风险

该目录 manifest_native_q5.json 已指向：

- source_builder: qdao_festival_refinement_20260910/scenes-sync/server/compose_server.mjs
- current_input_snapshot: qdao_festival_refinement_20260910/scenes-sync/server/plan.json
- current publication: qdao_festival_refinement_20260910/scenes-sync/server/publication.json

当前来源包括已修正的 hero-transparent_1024.png 和 server/current-inputs/retained_server_city.png。旧 v10 构建器读取冻结的 contracts/composite-inputs，直接重跑并发布可能恢复旧人物/场景状态。不要照旧 README 无条件执行 v10 publish --apply。

native_q5/{base,controls,labels}.svg 保存布局与文字，其中 base.svg、controls.svg 含大量嵌入位图，不能因体积大就判成截图。native_q5/build_layers.mjs 是已主动禁止直接写入的历史入口；保留来源记录，当前重建先核实节庆入口与完整输入。不要先删正式路径，再寄希望于未验证的旧脚本能恢复。

## 新窗口建议执行顺序

1. 先读取本文件、两个目录的 README_NATIVE_Q5.md、最新 Git 状态和相关 manifest；本交接是快照，删除前重算哈希。
2. 先处理已确认 6 对相同文件的去重，优先检查关联 staged/备份是否可以移除，保留当前正式源路径；若要移除正式派生输出，先补齐明确的按需恢复入口与当前使用策略。
3. 核验 54.65 MiB 物件图集能否从保留的 124 张图与 JSON/XML 完整重建，以及客户端/发布链是否需要它。验证时使用隔离输出，不覆盖正式素材或历史清单。
4. 对必要恢复操作实际做临时目录恢复并比对 SHA-256 或像素；删除文件保留逐项清单、大小、哈希、保留副本/重建依据。缺少证明的独立原图继续保留。
5. 清理确认无用的图片与副本，保留原图、必要脚本、清单、SVG 布局/文字和正式兼容路径；确认删除不会破坏生成/验证流程，避免以后旧脚本又生成已删过程图。
6. 只提交本任务更改。不要把其他窗口的主城或角色工作一起提交。是否 push 依据用户当前明确要求，不干扰已有后台上传。

## 前一轮已完成清理

commit 0391cb82：删除 client_ui_refresh_20260908 下 222 张已证实可恢复的 prepared 副本和 14 张旧 QA 图片，共约 129.33 MiB；原图、脚本、清单和 17 张没有独立同字节恢复来源的 prepared 角色图保留。详细依据：

- client_ui_refresh_20260908/cleanup-20260920.md
- client_ui_refresh_20260908/cleanup-20260920.json
- client_ui_refresh_20260908/restore_prepared.py（默认核验，--restore 才恢复）

客户端 E:/work/mmorpg-client 未修改。本轮开始后的 Git 日志已有其他工作提交 f09d353c（角色接续范围保留 15 名）；不要将旧角色清理范围当作当前人物需求。交接前看到的无关未追踪路径为 qdao_city_tiles_4k_20260916/builtin_q64_production/tianyong_festival/prepare_r09_c09_20260920.py 与同目录 r09_c09/，请保留并重新核实当前状态。
