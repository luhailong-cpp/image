# 五行奇谈 · 装备界面

2026-10-09 续作：详情卡已更新为玉绿标题、象牙纸面，当前切片、显示层与四状态可交互预览见 [最新交付](../equipment-ui-20261009/README.md)。本目录保留共用控件、图标及历史生成证据；旧深绿详情卡不再发布到客户端。

2026-10-08。以用户四张功能截图为参照，沿用现有背包与人物属性的玉绿、象牙纸面、暖金卷云风格。动态文字、数值与选择状态由 Unity uGUI / TMP 显示。

## 本轮交付

- 7 张透明皮肤：期望属性窗口、装备卡、主次按钮、复选框两态、关闭按钮。
- 2 张原创装备图标：青云灵剑、踏云靴，600×600 透明导出。
- 装备工作树 `E:/work/mmorpg-client-equip` 的 `EquipTooltip` 已接入新卡片，保留真实装备数据投影和既有穿脱回调。
- 主工程 `E:/work/mmorpg-client` 与装备工作树均加入通用 `EquipDetailCard`、`EquipWishDialog` 及皮肤资源。主工程没有引入未完成的装备协议，不假造消息号。
- 期望属性组件接收调用方提供的属性池与选中值，三列布局、21项分页、清除、取消、确认、Esc、Tab循环与焦点恢复；不自行发炼化请求，不根据当前词条猜可选全集。空池禁用确认。

**尚未完成线上装备／炼化功能。** 主工程现有背包尚无装备协议；装备工作树已有代码但缺正式消息号生成、完整资源与基线编译修复。炼化、属性池查询、进化、改造、套装与交易限制的数据/业务缺口详见 [backend-gaps.md](backend-gaps.md)。期望选择仅是可接线组件，尚未挂载为可用炼化入口，也未接持久化或命中提示。

## 图片与来源

| 图片 | 用途 | 记录 |
|---|---|---|
| [skin-atlas.png](skin-atlas.png) | 7件皮肤的重建母图 | [生成记录](skin-atlas.png.generation.json) |
| [equipment-icons.png](equipment-icons.png) | 武器/鞋图标重建母图 | [生成记录](equipment-icons.png.generation.json) |
| [sprites](sprites/) | 客户端正式透明 PNG | 每张同名 `.generation.json` 记录裁切来源 |

创作目标为共享配置的 `gpt-image-2.5-sunburst` / `max`，实际入口为内置 `image_gen.imagegen`。入口未开放型号/画质参数，工具也未披露可核实实际版本，因此实际型号与质量标记为未确认。不是以提示词冒称已锁定API参数。

原生母图均为1536×1024。图标600×600是裁切、等比缩放与透明留白的导出尺寸，不声称原生600方图。`alpha-retry.generation.json` 记录一次未使用的AI编辑；原始母图已有正确Alpha，工具预览显示了透明像素下的RGB背景。本轮使用原始母图无损裁切。

## 资源与接线

两个客户端的正式资源目录：`Assets/Resources/UI/Ugui/EquipmentV1`，共9张PNG及Unity导入meta。纹理为Sprite、无mipmap、无压缩；面板/按钮设置九宫格，复选框和关闭钮等比。

服务端图标配置如要使用新图，资源键为 `UI/Ugui/EquipmentV1/icon_sword`、`UI/Ugui/EquipmentV1/icon_boots`；本轮未改服务器表或将某类装备强行映射成这两个图标。

```csharp
var dialog = new EquipWishDialog(parent);
dialog.Show(authoritativeOptions, selectedIds, ids => SavePreferences(ids));

var card = new EquipDetailCard(parent, x, y);
card.Show(displayData, onEquipmentAction);
```

示例中的 `authoritativeOptions` 与 `SavePreferences` 由功能层提供；它们不代表已经存在的服务端接口或本轮完成的保存逻辑。

## 验证

- 主工程全运行时离线编译：371个源文件，0个错误。
- 期望属性选择模型真实源码的独立.NET检查：5/5通过；同时提供5个NUnit用例。
- 装备工作树离线编译仍有7个基线错误：2个缺失装备消息号、5个宠物Vector3歧义；本轮通用组件没有新增编译诊断。
- 原生截图夹具：主工程 `Assets/Editor/EquipmentUiVerification.cs`，菜单 `MMORPG/UI/Capture equipment artwork`。包含武器/防具期望选择、灵剑/靴子详情，以及空池与长属性两个边界状态，目标分辨率2560×1080、1920×1080、1280×720。样例数值全部标注为编辑器布局数据，不是在线角色数据。
- Unity官方MCP与截图的实际运行结果将以 `qa/verification.txt` 及独立MCP证据为准；文件不存在时不视为验证通过。

## 官方 MCP

主工程包清单恢复引用本机已有的官方 `com.unity.ai.assistant-2.17.0-pre.1.tgz`，存于 `E:/work/tools/unity-packages`，使用相对路径 `file:../../tools/unity-packages/...`，避免用户目录硬编码。此路径随工作区布局迁移；本轮没有将包上传或发布。

现有官方relay及调用脚本：`E:/work/mmorpg-client/.codex/unity-mcp-client.ps1`。初始只读探测为initialize成功、tools/list为空（编辑器未运行、包缺失），恢复后必须有实际工具调用成功证据才能称为完成MCP导入。

## 重建

`export-sprites.cjs`、`export-icons.cjs` 只做本地切图与资源复制，不调用付费API。它们保留逐图来源链，目标目录列在脚本中。客户端修改与资源均未提交或推送。
