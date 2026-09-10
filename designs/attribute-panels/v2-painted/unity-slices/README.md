# 人物、宝宝属性界面 · Unity 切图包

2026-09-09。以本目录上级的最终人物无相性稿、宝宝稿为准，通过 **Unity 官方 AI Assistant / relay MCP 的 `Unity_RunCommand`** 在 Unity 6000.6.0f1 内裁切、补出无字控件底板并配置 Sprite 导入。共 **31 张 PNG**。

- [全部切图总览](sprite-overview.png)
- [Unity 原生 UGUI 组合与九宫格拉伸预览](unity-sprite-preview.png)
- [裁切、尺寸、边距与资源路径清单](manifest.json)
- [Unity 导入与资源加载验收](unity-validation.json)
- [文件一致性及来源校验](file-validation.json)

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

## 原图与处理

人物采用 `01-character-ui-no-affinity.png`，原生 1932×814；宝宝采用 `02-pet-ui.png`，原生 1931×814。使用的原图快照在 `sources/`，SHA256 在 `file-validation.json`。

原稿为含文字的 RGB 图片：无字底板由原图清洁像素、边角与纹理重组；原图本身保持不变。主窗是原图边角、直边和无字纸面重组，不是把整张效果图作为背景。透明边缘使用颜色与形状遮罩处理。此次没有调用 AI 重绘。

四只宝宝在截图里的头像带烘焙等级，因此使用已确认的独立透明宠物素材裁出头像，避免把示例等级带进运行时。其实际来源、取景与 160×160 重采样均在 manifest 中记录；它们不是从截图无损去除等级后的头像。

`paper_tile`、`stat_field`、`slider_track`、`slider_fill` 保留不透明材质区域，其余图片具有实际 Alpha。纸面框与装饰应按层级组合，不能把不透明底板当作透明覆盖层。

## Unity 接入

已导入目录：`E:/work/mmorpg-client/Assets/Resources/UI/Ugui/AttributesPaintedV2/`。

资源键为 `UI/Ugui/AttributesPaintedV2/<name>`，例如：

```csharp
image.sprite = Resources.Load<Sprite>("UI/Ugui/AttributesPaintedV2/button_primary");
image.color = Color.white;
image.type = image.sprite.border.sqrMagnitude > 0 ? Image.Type.Sliced : Image.Type.Simple;
image.preserveAspect = image.type == Image.Type.Simple;
image.pixelsPerUnitMultiplier = Mathf.Max(1f, image.sprite.rect.height / image.rectTransform.rect.height);
```

可伸缩的底板已设置九宫格边距；标题整体、头像、圆形图标与分隔装饰按比例缩放，避免太极徽章变形。Sprite 为 Single、Full Rect、Clamp、Bilinear、无压缩、关闭 mipmap、启用 Alpha Is Transparency，最大纹理尺寸 4096。

文字、真实数值、等级、宝宝名称、状态和点击事件由现有原生控件提供。此包负责切图、导入和独立渲染验证；游戏页面的布局与功能接入由并行的“按效果图拼接游戏 UI”任务继续处理。这里的 Unity 预览是素材验收画面，不是正式游戏画面。

## 验证与复现

31 张 Sprite 已通过 Unity 资源加载、导入参数和九宫格合法性检查；主按钮、次按钮、方案按钮、宝宝卡与横页签已在 180/300/500 像素宽度下实际渲染检查。两目录 PNG 的尺寸、SHA256 一致，原生裁切矩形端点采用独立取整。

`tools/SliceAttributeArtwork.cs` 是实际执行的官方 MCP 裁图脚本；`tools/VerifyAttributeSlices.cs` 是隔离临时场景的验证脚本，执行后恢复原场景。现有客户端 MCP 入口可以直接执行它们：

```powershell
& 'E:/work/mmorpg-client/.codex/unity-mcp-client.ps1' -Action run -CodePath 'E:/work/image/designs/attribute-panels/v2-painted/unity-slices/tools/SliceAttributeArtwork.cs' -Title '重建人物宝宝切图'
```

脚本中的源图、输出与客户端路径面向当前工程；迁移工程时同步修改常量。执行前打开目标 Unity 工程并保持编辑模式。
