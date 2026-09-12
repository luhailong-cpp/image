# 五行奇谈 · UI 统一风格重制与重新切图 v10

更新：2026-09-11。所有 UI 的画法、材质、边框与装饰统一遵循[用户指定选角图](../docs/references/ui-style-20260910.png)，保留道家 Q 版及少量春节、元宵、中秋元素。其他游戏截图仅提取功能、字段、布局与交互意图；单独贴图不改变项目美术风格。长期规则和可复用提示词统一维护在 [UI 制作规范第 2 节](../qdao_ui_redesign_v5/UI_SPEC.md#2-统一视觉与控件层级)。

## 本次交付

已完成六组内置生图原画、45 个透明美术裁片，以及 158 个正式 PNG 合同的重制输出。155 个输出更换皮肤或重新裁切；另 3 个独立纯文字层保留：属性标题 `title_character`、`title_pet` 与 `hud_labels`。保留项不含旧框体，不虚报为新生图。四只宝宝头像的最新边缘修复已纳入正式资源；[首次正式发布记录](../qdao_cutout_edge_repair_20260910/published-ui.json)确认 158 个 PNG 与 126 个伴随文件共 284 项均与暂存区一致。本次已完成 296 项正式资源、支持文件与标准预览的核验同步，最终清单以 [发布记录](publication.json) 和 [全量验证](validation.json) 为准，逐件基线保存在 [current_files.json](contracts/current_files.json)。

| 家族 | 正式 PNG 数量 | 合同 |
|---|---:|---|
| 通用控件与状态 | 39 | [components.json](contracts/components.json) |
| 旧 exact 与原子控件、徽标、图集 | 73（50 + 23） | [legacy.json](contracts/legacy.json) |
| 旧选服分层与兼容画面 | 12 | [layers.json](contracts/layers.json) |
| HUD 皮肤、标签、叠层 | 3 | 原布局和独立标签层 |
| 人物／宝宝属性切图 | 31 | [attributes.json](contracts/attributes.json) |

资源名、画布、Alpha、状态语义、九宫格边距和已有图集帧坐标保留；SVG 为内嵌新 PNG 的便携包装，不能作为无限细节矢量。关联清单、SVG、组合预览和 QA 图另交付，不增加上述正式 PNG 数量。四只宝宝头像使用已确认的独立透明宠物素材重新取景；人物“相性点”不恢复。

## 原画与真实调用记录

直接使用 ChatGPT/Codex 宿主内置 `image_gen`，无需另配 `OPENAI_API_KEY`。[官方说明](https://learn.chatgpt.com/docs/image-generation)确认该路径使用 GPT Image 2、计入 Codex 用量。本次以最高视觉质量为目标；工具未开放 model／quality 参数，因此不宣称已显式强制设置 `quality=high`。

| 原画 / 实际提示词 | 内容 | 实际原生尺寸 |
|---|---|---|
| [01-plates.png](source/01-plates.png) · [提示词](source/01-plates.prompt.txt) | 按钮、普通／选中卡片、标题及禁用底板 | 1254×1254 |
| [02-main-window.png](source/02-main-window.png) · [提示词](source/02-main-window.prompt.txt) | 主窗与纸面、固定边饰 | 1672×941 |
| [03-content-window.png](source/03-content-window.png) · [提示词](source/03-content-window.prompt.txt) | 细金边内容面板 | 1672×941 |
| [04-emblems.png](source/04-emblems.png) · [提示词](source/04-emblems.prompt.txt) | 十枚徽标、勾锁和状态图标 | 1254×1254 |
| [05-ornaments.png](source/05-ornaments.png) · [提示词](source/05-ornaments.prompt.txt) | 云纹、分隔、太极体系与节日小饰 | 1254×1254 |
| [06-attribute-fields.png](source/06-attribute-fields.png) · [提示词](source/06-attribute-fields.prompt.txt) | 数值框、滑杆、页签、头像框、小控件 | 1254×1254 |

指定参考原图为 2560×1080，SHA-256 `913e301b1955a4dd78888bebcec82d1dbf504c0517ed606cc8eaab667675b825`。本地路径输入曾遇到 Windows ACL 故障，改用内存中的对话参考图后六组均生成成功；这是输入通道问题，与 API 密钥无关。原画为洋红底，清理后裁片和正式透明件均检查实际 Alpha。提示词期望尺寸不冒称实际原生尺寸，重采样导出也不冒称新增原生细节。

[生成状态](generation-status.json)保存实际参数、来源与哈希；历史备用 API/CLI 尝试在请求发出前因未配置密钥退出，没有发送 API 请求或产生付费 API 图片。后续继续默认使用内置路径。

## 验收与来源

- [透明美术裁片索引](artwork/index.json)记录 45 个裁片的原画、源矩形、九宫格和固定饰件；[美术联系表](artwork/contact-sheet.png)用于对照。
- [通用与旧路径映射](source-map.common.json)、[属性映射](source-map.attributes.json)记录逐件来源及保持的合同。
- [公共与兼容切图视觉验收](staged/common-legacy-visual-qa.json)覆盖 112 组 PNG/SVG；[四头像修复补充验收](staged/visual-qa-supplement.json)绑定当前 46 张属性及复合图和最终展示图。
- [属性与组合历史视觉验收](staged/attribute-composite-visual-qa.json)覆盖 31 个属性件、12 个选服及 3 个 HUD；检查文字区、边框连续性、固定符号比例、透明边缘、整屏布局与 HUD 叠层误差。
- [最终交付审计](final-verification.json)核对 296 个正式文件、112 对 PNG/SVG、31 个属性控件复建像素、6 张标准界面及 10 张 Unity 验收截图。
- [全量验证](validation.json)与[发布记录](publication.json)区分待发布文件和正式路径。历史 v6／v7 或旧 Unity 报告不能代替此次 v10 核验。

## 确定性重建

在仓库根目录运行，需要现有 Python（Pillow、NumPy）及 Node.js / Sharp。脚本使用已保存原画进行裁切、透明清理和控件适配，不重新请求图片服务。不得重新运行库存盘点覆盖 `contracts/current_files.json` 的历史基线。

```powershell
python qdao_ui_style_recut_v10/tools/extract_art.py
python qdao_ui_style_recut_v10/tools/build_common_legacy.py
python qdao_ui_style_recut_v10/tools/build_attributes.py
node qdao_ui_style_recut_v10/tools/build_composites.mjs
python qdao_ui_style_recut_v10/tools/validate_staged.py
python qdao_ui_style_recut_v10/tools/publish_staged.py
# 核对待发布映射、来源变化和视觉报告后发布：
python qdao_ui_style_recut_v10/tools/publish_staged.py --apply
```

Sharp 无法自动解析时，在合成命令后添加 `--sharp '<已安装的 node_modules>/sharp'`。前四步只写本包的中间图和 `staged/<原资源相对路径>`；发布器核对通过后才覆盖明确列出的正式路径。旧布局和精确场景输入冻结在 contracts/composite-inputs，四个最终头像切片冻结在 contracts/reviewed-portraits，避免覆盖并行任务的后续原画或头像修复。重建改变输入或图像后，须重新实看联系表、九宫格与拼合效果，不能把旧视觉报告用于新哈希。旧 components、exact、选服和 HUD 的直接写入构建入口已阻止重新写入历史皮肤；按本节重建。

## 接入与后续边界

本次完成美术原画、重新切图、组合检查与仓库正式资源交付。并行客户端任务已通过官方 Unity relay MCP 同步 31 张 v10 属性 Sprite，保留 GUID，核对哈希、尺寸、资源加载与九宫格边距；[导入报告](../designs/attribute-panels/v2-painted/unity-slices/unity-import-v10.json)通过。人物／宝宝真实面板在 2560×1080、1920×1080 两种尺寸下完成 10 张编辑器截图检查，26 项测试通过、0 项失败，见 [v10 Unity 验收](../designs/attribute-panels/v2-painted/unity-slices/unity-validation-v10.json)与[检查记录](../designs/attribute-panels/v2-painted/unity-slices/unity-review-v10/qa-checks.txt)。验收使用临时编辑器场景和离线样例数据，没有执行在线服务器验证；该结论仅覆盖属性面板，不能扩展为全库 UI／FairyGUI 全部接入完成。

`designs/attribute-panels/index.html` 的可操作预览仍为第一版交互；`v2-painted/index.html` 仍为历史静态效果稿。它们未随本轮换皮，不作为 v10 当前视觉验收。标准 02 选服与 04 HUD 纳入本次新皮肤组合预览的同步范围，最终文件与哈希见发布记录；其余登录／选角等历史整屏原画继续保留，不等于全部页面已经实现。

2026-09-12 全库前置交付已完成，[全库节庆精修](../qdao_festival_refinement_20260910/README.md)正在接续；v10 当前控件母图和切片经本轮实看可保留，新的登录前整屏与人物／场景来源变化以本轮发布记录为准。此处保留首次 v10 发布与验收的历史哈希，不用旧报告冒充新图验收。
