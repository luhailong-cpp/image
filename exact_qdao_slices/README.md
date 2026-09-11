# 五行奇谈 · 旧路径 UI 原尺寸重建

本批已在原文件路径重做全部 **50 张 exact 切片** 与 **11 个原子控件**，补齐旧清单缺失的 **10 枚 420 × 420 圆徽标**，并增加 `icon_leaf.png` 作为桃灵兼容别名；原徽标母图保持 **1774 × 887**，现为真 RGBA。合计 **73 个 PNG + 73 个 SVG 源文件**。当前画法统一为 v10 指定参考；六组内置原画及确定性重建流程见 [v10 UI](../qdao_ui_style_recut_v10/README.md)。

[完整逐件映射](manifest_native_q5.json) 记录每件原尺寸、原哈希、用途、源 SVG、新哈希和九宫格合同；[验证记录](validation_native_q5.json) 记录 73 件 XML、尺寸、透明边角与 11 项旧导入合同。SVG 在各交付目录的 `svg_q5/`，均为无动态文字的便携 SVG 包装，内嵌本轮 image_gen 新绘制并适配的 PNG。

## 拆层与使用

- `fx_server_card_N.png` 与 `fx_server_card_N_base.png` 均为同内容的无字纯底板，原路径兼容保留；不再混入徽标、状态点或抹字残迹。
- `fx_server_card_N_badge.png` 仅含完整圆徽标，编号 0–7 依次对应楼阁、太极、炼丹炉、山、剑、桃灵、水纹、罗盘。原尺寸 116 × 100 不变，内圆等比居中。
- `fx_server_card_N_dot.png` 独立重做为暖金边红色感叹号，保留旧红色标记；实际服务状态含义和可读状态文字由客户端提供。
- `fx_server_card_N_stroke.png` 从灰色抹字笔画改为无字描金短划装饰，不把它当作动态文字。
- 页签、列表行、底栏、原子卡片都是无字皮肤；搜索保留合同指定的放大镜，原生输入文字另叠。
- 原子 `icon_leaf.png` 与 `icon_peach_spirit.png` 同内容，只有 10 个独立圆徽标符号。母图的 `chroma` 旧名保留兼容，但透明通道已取代绿色底；无需色键抠除。

## 九宫格

原子控件在根 [wire_qdao_v3_assets.py](../wire_qdao_v3_assets.py) 中的 11 组目标尺寸和 `scale9grid=(left, top, center_width, center_height)` 已原值保留到清单，未运行该客户端接入脚本。原子源图仍保留原来的高分辨率尺寸，清单另给按原图坐标换算的 `source_grid_center_xywh`。

本库未找到 exact 切片的既有数值九宫格；清单中给出的安全九宫格明确标为新建议，未冒称旧客户端合同。圆角放在四角固定区域内；无字底板可按记录九宫格缩放。带放大镜搜索框固定高度，仅横向伸缩。徽标、状态点、花饰和短划只允许等比缩放。

选中状态通过独立绿色皮肤表达，底板中不嵌选择勾记。客户端应在文字/状态层叠加“已选择”或独立勾记，不仅凭颜色判断。新皮肤不改变服务状态数据、路由或真实交互。

## 重建与检查

按 [v10 确定性重建](../qdao_ui_style_recut_v10/README.md#确定性重建)执行，通用件和 73 个兼容件由 `python qdao_ui_style_recut_v10/tools/build_common_legacy.py` 生成到暂存区，通过验证和视觉检查后统一发布。

旧 `build_native_q5.mjs` 已禁止写回 v7 皮肤；只读 `--check` 入口保留。当前来源见 [v10 映射](../qdao_ui_style_recut_v10/source-map.common.json)，完整验收见 [v10 validation.json](../qdao_ui_style_recut_v10/validation.json)。旧 `validation_native_q5.json` 为历史验收，不能替代当前报告。

SVG 的内嵌图像是重新绘制并按合同适配的位图，不是无限细节矢量。生产路径保持兼容，不代表已经在 Unity／FairyGUI 中导入或实现交互。
