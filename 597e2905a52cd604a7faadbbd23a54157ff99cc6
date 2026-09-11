# 人物、宝宝属性界面 · 切图包 v10

更新：2026-09-11。当前 31 张 PNG 依据全项目指定选角风格重新制作：25 张新 UI 皮肤／控件、4 张宠物头像重裁，2 张干净的独立书法标题保留原像素。遵守深玉绿、象牙米白、细暖金、道家 Q 版及少量春节／元宵／中秋点缀；其他游戏截图只提供功能布局。完整原画和复现流程见 [v10](../../../../qdao_ui_style_recut_v10/README.md)。

本次没有重新导入 Unity 或执行引擎内 UGUI 验收。原有 `unity-validation.json`、`unity-sprite-preview.png` 记录的是 2026-09-09 旧版导入，不能用于证明当前 v10 图片已经在客户端加载。

- [当前切片总览](sprite-overview.png)
- [文件、边距与资源路径清单](manifest.json) · [文件核验](file-validation.json)
- [九宫格检查](nine-slice-review.png) · [固定符号与标题](fixed-glyph-title-review.png)
- [人物组合检查](character-layout-review.png) · [宝宝组合检查](pet-layout-review.png)
- [本次属性／组合视觉验收](../../../../qdao_ui_style_recut_v10/staged/attribute-composite-visual-qa.json)

## 内容

| 用途 | 资源 |
|---|---|
| 主窗 | `window_frame`、`paper_tile`、`divider` |
| 标题 | `title_plate`、`title_character`、`title_pet` |
| 按钮 | `button_primary`、`button_secondary`、`button_scheme`、`dropdown_arrow` |
| 页签与小标题 | `tab_horizontal`、`tab_vertical_normal`、`tab_vertical_selected`、`section_header` |
| 关闭 | `close_button`、`close_tassel` |
| 加点与数值 | `step_minus`、`step_plus`、`step_plate`、`stat_field`、`notice_icon` |
| 滑杆 | `slider_track`、`slider_fill`、`slider_thumb` |
| 宝宝列表 | `pet_card_normal`、`pet_card_selected`、`portrait_frame`、四张 `portrait_*` |

所有按钮底板、页签、数值框和列表卡均不带动态文字。两个固定书法标题单独提取为透明图片，可按需使用，也可以用 TMP 绘制标题。±、×、叹号和下拉箭头属于固定图标。

## 来源与透明度

当前 UI 使用 v10 六组内置 GPT Image 2 原画的透明裁片；源图、真实原生尺寸、固定边距和逐件映射见 [v10 记录](../../../../qdao_ui_style_recut_v10/README.md)与 [属性来源映射](../../../../qdao_ui_style_recut_v10/source-map.attributes.json)。生成工具未开放质量参数，不宣称显式强制 high，也不要求 API 密钥。

四只宠物沿用已确认的独立透明素材重新裁出 160×160 头像，避免把截图中的示例等级带入运行时。两个独立书法标题继续使用干净原图；它们不是本次重新生成。上级两张含字效果稿和 `sources/` 保留为历史快照，不作为当前皮肤重建源。

`paper_tile` 为有意保留的不透明纸面纹理；其余控件按清单保留所需 Alpha、原画布及边距。24 个新制非平铺 UI 件设置 1 像素透明外缘；头像与独立纯文字按各自合同处理。透明 PNG 中的纸面本体可以不透明，不应当作覆盖式透明框使用。

## 客户端接入合同

既有目标目录为 `E:/work/mmorpg-client/Assets/Resources/UI/Ugui/AttributesPaintedV2/`，资源键仍是 `UI/Ugui/AttributesPaintedV2/<name>`。本次只更新本美术仓库的资源，不声称该客户端目录已经同步。

接入时按当前 `manifest.json` 核对 31 个文件和哈希，沿用原名称、画布及 `borderLeftBottomRightTop`。可伸缩底板采用 Sliced；标题、头像与圆形图标保持比例。文字、真实属性值、等级、名称、状态和点击事件由原生控件实现；“相性点”继续移除。

已有导入合同为 Sprite Single、Full Rect、Clamp、Bilinear、无压缩、关闭 mipmap、Alpha Is Transparency、最大纹理尺寸 4096。同步后仍需重新执行资源加载、中文排版、实际尺寸九宫格和游戏页面检查，保存针对新哈希的引擎报告。

## 重建与历史脚本

在仓库根按 [v10 确定性重建步骤](../../../../qdao_ui_style_recut_v10/README.md#确定性重建)执行。属性构建入口为 `python qdao_ui_style_recut_v10/tools/build_attributes.py`，输出到 v10 暂存区；统一核验与发布器负责正式路径写入。

`tools/SliceAttributeArtwork.cs` 是旧版 Unity 原图裁切脚本，原逻辑会同时覆盖美术仓库和客户端为旧皮肤，现已阻止执行并提示使用 v10。代码保留供历史追溯。`tools/VerifyAttributeSlices.cs` 是旧版引擎验证脚本，重用前须核对其输入和检查项适用于当前清单；不能直接沿用旧报告。

本目录组合检查为离线静态美术检查，未运行 Unity。上级 HTML 和静态效果稿也没有随本次换皮。
