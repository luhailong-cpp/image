# 五行奇谈 · 装备 UI 续作

2026-10-09。延续已确认的 Q 版道家画法：深玉绿标题、象牙米白纸面、暖金卷云、太极顶饰。沿用上一轮合格的弹窗、按钮、复选框与原创装备图标，本次用内置 GPT Image 重新制作装备详情底板，并完成完整信息显示及主客户端背包接线。

## 查看

- [四状态可交互预览](preview.html)：武器期望属性、防具期望属性、青云灵剑详情、踏云靴详情。
- 本地浏览器地址：`http://127.0.0.1:4312/preview.html`。该地址仅在本地预览服务运行时有效；HTML 已嵌入图片与 SimKai 字体，可离线打开。
- 预览使用正式切片与原生中文文字。原图数值、属性池和头部信息用于完整排版验收，不连接服务器，也不是 Unity 截图。

## 完整信息与美术资源

用户要求“原来有多少属性就要多少属性”。浏览器预览和两客户端的 Editor 夹具均保留原图完整信息，现状如下：

| 状态 | 保留内容 |
|---|---|
| 武器期望属性 | 18 项，含五行相性、所有相性、所有技能上升及忽视抗性/抗异常 |
| 防具期望属性 | 21 项，含五行抗性、所有抗性及各类抗异常 |
| 青云灵剑详情 | 10 行正文，含限制交易；另保留等级 120、火、改造、角色要求、进化星级、星条与已装备状态 |
| 踏云靴详情 | 14 行正文，含灰色“改5 气血 285”与限制交易；重复的速度、所有属性条目逐行保留，另有完整头部信息 |

- 两张详情预览保留“分享”“更多”“卸下”入口，沿用项目原创名称和图标。旧版六行样例、额外“准确 360”“等级 80”要求和诗句已移除。
- 新详情底板 [tooltip_panel.png](sprites/tooltip_panel.png) 为 448×930、真实 Alpha，九宫格 L/B/R/T 为 48/80/48/160。保留两客户端原 GUID 与资源键 `UI/Ugui/EquipmentV1/tooltip_panel`。
- 装备名称放在深绿标题内，头部信息与全部词条显示在浅色纸面上；蓝、紫、金、绿、红语义颜色采用适合纸面的深色，禁用条目仍明确保留。
- `EquipDetailCard` 宽 460，横向留白 38，参考样例分别高 684/804。`Lines` 没有六行、八行或十四行上限，不截断条目，也不合并重复名称。普通十四行在参考画布中直接完整显示；只有内容实测高度超过可用空间时才启用滚动，所有行仍保留。
- 期望属性弹窗保留三列布局、整行选择高亮、已选/可选计数、清除、取消、确认、键盘导航与长列表分页。样例 ID 不是服务器属性编号；运行时属性池由调用方提供。
- 复用的 8 张资源及其生成证据见 [上一轮素材](../equipment-ui-20261008/README.md)。旧导出脚本已阻止深绿旧卡覆盖本次卡片。

正式资源与新版共享显示组件已同步到 `E:/work/mmorpg-client` 和 `E:/work/mmorpg-client-equip`。图片位于各自的 `Assets/Resources/UI/Ugui/EquipmentV1/`，显示层包括 `EquipDetailCard.cs`、`EquipUiSkin.cs`、`EquipWishDialog.cs` 与 `EquipUiStyle.cs`。现有 Claude Code 业务实现和其他未提交改动保留。

## 客户端接线与服务端现状

主客户端已移植 `EquipTooltip`、`EquipBagModel` 等装备业务与背包接线，现有真实背包通过 `GameplayWindow → EquipTooltip → EquipDetailCard` 显示调用方的装备数据并传递穿脱回调；装备工作树也使用新版完整详情卡。正式 MessageIds 已按项目生成器同步，EquipErrorTip 已由 Tip 表及正式 protoc 生成，证据见 [服务端与协议状态](validation/server-contract-status.json)。

协议注册和客户端生成文件更新不等于服务端已经上线：服务端 C++ protobuf/RPC 元数据、运行二进制及部署尚未更新，也未执行 MessageLimiter 导出。本次不能据此声称在线穿脱请求已经验证成功。

两客户端的 `EquipWishDialog` 仍没有实际炼化页面/后端调用方；组件能返回选择结果，但炼化保存、持久化和命中提醒尚未接通。浏览器与 Editor 夹具中的改造、进化、星条、交易限制等原图头部/正文信息是明确的布局样例，未伪造为线上角色数据。运行时只显示调用方实际提供的字段。预览中的分享、更多只产生本地说明；真实入口由调用方提供回调，不代表已完成分享、改造、进化或套装后台功能。

## 验证

最新证据集中在 [validation](validation/)：

- [主客户端编译记录](validation/main-integration-compile-status.json)：381 个运行时源文件、25 个测试源文件、1 个 Editor 截图夹具，三组均为 0 错误；使用真实 Unity 程序集作离线编译引用。
- [纯逻辑测试记录](validation/main-integration-unit-tests.json)：119/119 通过、0 失败。包括 EquipClient 70、EquipBagModel 13、EquipWishSelection 5、PlayerFeaturesClient 31；执行的是当前主工程实际业务源码与 NUnit 断言，在 .NET 中运行，未运行 Unity 窗口，也未连接真实服务器。
- [完整字段浏览器复验](validation/browser-status.json)：825×871 视口下，武器 10 行、靴子 14 行逐图完整可见，无截断；18/21 项选择池全部可访问，防具末项勾选并确认后重新打开仍保留。总览图片全部加载，页面无视口溢出，控制台无 error/warn；记录中的 HTML SHA256 对应当前完整字段版本。
- 四状态、灵剑和靴子的三张浏览器布局截图已按用户要求于 2026-10-15 删除；浏览器验证与逐图来源文字记录保留，见 [清理清单](../../docs/screenshot-cleanup-20261015.json)。当前页面可通过上方可交互预览查看。

本机 Unity 6000.6.0f1 的许可证离线有效期已过期，原生运行与截图验收未完成。`Assets/Editor/EquipmentUiVerification.cs` 已包含完整 18/21 项和 10/14 行样例，输出目录为本目录 `qa/`；授权恢复后可运行菜单 `MMORPG/UI/Capture equipment artwork`，检查 6 状态×3 分辨率、完整字段、超长内容与原生回调。`qa/verification.txt` 不存在时不能视为原生验收通过。以上成功的离线编译与纯逻辑测试不替代这一检查。

## 图片来源与重建

| 图片 | 来源证据 |
|---|---|
| [原生详情底板](tooltip-paper-source.png)（1024×1536） | [逐图记录](tooltip-paper-source.png.generation.json) · [实际提示词](prompts/tooltip-paper.txt) |
| [客户端切片](sprites/tooltip_panel.png)（448×930） | [派生记录](sprites/tooltip_panel.png.generation.json) · [双客户端哈希与 GUID](sprite-manifest.json) |

此次目标为项目配置的 GPT Image 2.5 Sunburst / max，走内置 `image_gen.imagegen`。工具未开放 model/quality 参数，未返回可核实的具体后端型号与画质，所以记录为“未确认”，没有用提示词冒充参数锁定。产品开放情况本次查阅了 [官方 Images 2.5 公告](https://openai.com/index/introducing-chatgpt-images-2-5/) 和 [官方 Sunburst 模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)。

`export-tooltip.cjs` 从保留的原生母图裁剪、等比缩小，再仅延伸九宫格中心，以保留标题与角饰比例；输出尺寸不冒称原生尺寸。脚本同步两客户端切片并保留 GUID。`build-preview.cjs` 重建自含 HTML，不调用生图 API。当前母图是重建所需源文件，保留用途明确。

本次未提交、推送或合并分支。
