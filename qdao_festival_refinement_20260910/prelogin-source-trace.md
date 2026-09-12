# 登录前图片来源与传播追踪

核验时间：2026-09-12。仅作读取和追踪；本报告没有修改图片、构建程序、正式清单或客户端。

最新用户约束：登录首页、选服、创角、选角不出现九尾狐；登录道童保持大小，靠圆台中央并避开标题与按钮。独立游戏内宠物、战斗入场等用途按各自合同保留。用户在客户端采用的位移不是所有图片通用的像素位移。

## 结论与最小处理范围

1. **登录 01、选角 03 是完整栅格效果稿**，文字和控件已烘焙。它们没有与选服同样的独立 labels.svg。最小做法是在最新曝光修正后的 source PNG 上，仅编辑角色／九尾狐所在的场景区域；保留原始文字、按钮、边框的像素，登录角色调整到圆台中央。处理后以既定画布导出对应 2560×1080 图片，同时更新来源／导出记录。不能只改标准预览而留下 source，否则重建会恢复旧图。
2. **选服 02 已是 v10 组合结果**。它与 12 个 legacy 文件同源，其中文字层独立。保留 39 个现行控件、既有九宫格、控件坐标及 labels.svg，只有确认场景或角色需要修改时替换本轮场景／角色输入，再生成相关背景层、组合层及 RGB 别名；无字按钮层可逐项记为保留。选服页的右上角小道童位置是独立装饰合同，不机械套用“登录圆台居中”。
3. **实际客户端采用净底、独立角色、原生控件组合**。本仓库没有核实到独立创角整屏母图；UI_SPEC 只定义选角空槽进入创建流程。创角应继承客户端已完成的无狐布局，不凭空制造全屏资源，也不把完整效果稿当净底。
4. v10 构建器固定读取历史冻结目录 `contracts/composite-inputs`。修改正式 hero/city 后直接重跑原构建器，会继续使用旧冻结输入。新一轮应建立本轮输入快照及明确的构建参数／独立入口，保留旧冻结合同作回退；不能伪造旧 v10 来源哈希或复用旧视觉验收。

## A. 当前 01 与 03 的权威像素及有效导出

| 页面 | 当前 source | 画布／模式 | 标准有效导出 |
|---|---|---|---|
| 登录 | `qdao_ui_redesign_v5/source/01_login.png` | 1928×815 RGB | `qdao_ui_redesign_v5/01_login_2560x1080.png`，2560×1080 RGB |
| 选角 | `qdao_ui_redesign_v5/source/03_character_select.png` | 1931×814 RGB | `qdao_ui_redesign_v5/03_character_select_2560x1080.png`，2560×1080 RGB |

`qdao_ui_redesign_v5/manifest.json` 是当前标准文件元数据入口。`export_ui.py` 从 source 进行等比居中 cover；此脚本默认还会处理其余四屏及过场，实际精修宜按本轮明确的文件清单做同等变换，避免无关回写。若只处理 01／03，保持它们当前 source 画布，再同步两个标准导出并更新 manifest 对应项。

`qdao_gpt_image2_refresh_v7/scenes/01_login.raw.png`、`03_character_select.raw.png` 及各自 `*.prompt.txt`、`*.exports.json` 是旧生图来源记录，当前正式 PNG 已有后续曝光修正，不能用旧 raw 回灌。v7 `02_server_select.raw.png` 已被 v10 选服组合取代。`docs/references/ui-style-20260910.png` 是固定风格参考，即使参考图有狐也应保留原档，不等于正式登录前成品。

## B. v10 选服及 legacy 同源文件族

当前组合权威入口：`qdao_ui_style_recut_v10/tools/build_composites.mjs`，发布入口 `tools/publish_staged.py`。历史 `q_daoist_login_ui_uncropped_highres_final_layers/native_q5/build_layers.mjs` 已禁止直接写入。

组合输入：

- 新控件：`qdao_ui_style_recut_v10/staged/qdao_ui_redesign_v5/components/png/`，回退查找 `qdao_ui_style_recut_v10/derived/components/`；实际正式 39 个控件为 `qdao_ui_redesign_v5/components/png/`，SVG 是内嵌 PNG 包装。
- 冻结几何／文字：`qdao_ui_style_recut_v10/contracts/composite-inputs/q_daoist_login_ui_uncropped_highres_final_layers/native_q5/{base,controls,labels}.svg`。
- 冻结角色：`qdao_ui_style_recut_v10/contracts/composite-inputs/qdao_chibi_game_pack_v4/hero-transparent_1024.png`。
- 冻结选服城市：同目录 `qdao_chibi_game_pack_v4/main-city_2560x1080.png`。
- 角色装饰合同 `contracts/layers.json`：2560 基准 `[2042,30,310,310]`。
- 正式层源码路径为 `q_daoist_login_ui_uncropped_highres_final_layers/native_q5/{base,controls,labels}.svg`；当前 builder 重新换入 v10 位图皮肤，并保留 SVG 的几何和文本。

12 个正式 PNG 合同（不是 12 张独立生图）：

| 角色 | 正式路径 | 画布／模式 |
|---|---|---|
| base | `q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_background_ui_uncropped_final_5120x2160.png` | 5120×2160 RGBA |
| controls | `q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_buttons_uncropped_final_5120x2160.png` | 5120×2160 RGBA |
| combined | `q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_ui_uncropped_final_recomposed_5120x2160.png` | 5120×2160 RGBA |
| combined 别名 | `q_daoist_login_ui_lidazui_headband_v2_5120x2160.png` | 5120×2160 RGBA |
| combined 别名 | `q_daoist_login_ui_redrawn_transparent_5120x2160.png` | 5120×2160 RGBA |
| base | `q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_background_ui_uncropped_final_10240x4320.png` | 10240×4320 RGBA |
| controls | `q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_buttons_uncropped_final_10240x4320.png` | 10240×4320 RGBA |
| combined | `q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_ui_uncropped_final_recomposed_10240x4320.png` | 10240×4320 RGBA |
| 完整选服参考 | `q_daoist_login_clear_2560x1080.png` | 2560×1080 RGB |
| 同上别名 | `q_daoist_login_clear_lidazui_headband_2560x1080.png` | 2560×1080 RGB |
| 同上别名 | `ugui_qdao_headband_2560x1080.png` | 2560×1080 RGB |
| 同上别名 | `ugui_qdao_headband_native_2560x1080.png` | 2560×1080 RGB |

base 是透明框板与小道童组合，名称里的 background 不表示它是纯场景。controls 无动态文字。combined 是 base 与 controls 的 Alpha-over。4 张 RGB = 城市场景 + 淡雾 + combined + labels.svg。

发布器 `prepare_exports()` 还将 `staged/ugui_qdao_headband_2560x1080.png` 复制为：

- `qdao_ui_redesign_v5/source/02_server_select.png`
- `qdao_ui_redesign_v5/02_server_select_2560x1080.png`

二者当前均 2560×1080 RGB、相同字节。随后还应同步本库有效准备副本 `client_ui_refresh_20260908/prepared/UI/Ugui/Native/screen_art_headband.png`。该副本是含文字效果参考，不能当运行时无字皮肤。

如果仅替换选服城市场景，RGBA 的 8 项及按钮／文字均可保留，只需重组 4 张 RGB 和 2 张标准图、1 张准备副本；如果替换小道童，则除 controls 两张可保留，其余对应 base、combined、RGB 及有效副本均须传播。所有改变都应更新本轮来源和验收记录。

## C. 客户端可用净底、标题与独立角色

| 素材 | 本库当前来源 | 本库有效准备副本 |
|---|---|---|
| 登录净底 | `client_ui_refresh_20260908/additional/login_background.png` | `client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/login_background.png` |
| 游戏标题 | `client_ui_refresh_20260908/additional/title_logo.png` | `client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/title_logo.png` |
| 独立道童 | `qdao_chibi_game_pack_v4/hero-transparent_1024.png` | `client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/hero.png` |
| 城市场景 | `qdao_chibi_game_pack_v4/main-city_2560x1080.png` | `client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/sanctuary_background.png` |
| 独立九尾狐（保留游戏内用途） | `qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png` | `client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/companion_fox.png` |

净底生成记录／重建入口：`additional/login_background.generation.json`、`additional/prepare_login_background.py`。原生 `login_background.raw.png` 是 1931×814；净底标准副本是 2560×1080，标题是 960×495 RGBA。只读核验净底与其准备副本当前字节相同，标题及其准备副本也相同。

标题由旧登录效果稿提取，但当前已有独立透明文件。修改登录角色时应保留独立标题，避免重新生成中文字；无需因旧提取来源带狐而删除标题。

最新节庆场景另有完整来源链：

`qdao_festival_scenes_20260910/login_landscape/scene-native.png` → `final/02_login_landscape.png`（1931×814 RGB 原生副本）→ `runtime/02_login_landscape_2560x1080.png`。

这一最新场景尚未在 `client_ui_refresh_20260908/sync_assets.py` 被映射为旧 login_background；不能因场景包完成就宣称客户端净底已更新。决定用它替换旧净底时，先核对圆台落脚与标题／按钮安静区，再保持旧目标画布并同步有效准备副本。

`client_ui_refresh_20260908/sync_assets.py` 无参数会准备许多素材并重建报告，`--sync` 会写客户端；本次图片修复不要顺手运行全量客户端同步。`assets_manifest.json` 顶层历史 failed 及客户端哈希应保留语义，本库准备副本更新不等于客户端导入／运行验收。

## D. 文案与证据边界

`qdao_ui_redesign_v5/copy.zh-CN.json` 仍有 `demoData.loginCompanionId = demo-nine-tailed-fox` 与 `pages.characterSelect.fields.companion = 同行灵宠`。UI_SPEC 第 3、5 节历史描述仍提九尾狐。对登录前新的实际组合，应省略过时同伴展示并以最新节庆文档为准；不删除全局独立宠物身份数据。若选角旧效果稿右侧烘焙了九尾狐文字，也需纳入小范围修订，保留其余字段位置与中文清晰度。

`client_ui_refresh_20260908/qa/*`、Unity 截图、浏览器 QA 截图、`docs/references/*`、v7 原图、v10 冻结输入及旧 staged 发布证据属于历史／验证／来源档案，不作为需要抹狐的成品逐图改写。新效果必须另行重新组合与验收，不能修改截图充当新客户端验收。
