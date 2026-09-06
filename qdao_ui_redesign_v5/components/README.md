# 五行奇谈 · 通用 UI 控件 v5.2

本套件重做仓库现有的通用 UI 形状，使用玉绿 `#176C5F` / `#438E78`、米白 `#FFF7DE`、暖金 `#C59645` 和桃木 `#795638`。双层金框、轻微厚度与阴影建立按钮层级，云纹只放在不遮文字的边缘。源文件是原创矢量图形，不含人物、场景或外部图片。

查看 [可视总览](overview.html)、[总览 PNG](overview.png)、[十枚徽标与小尺寸总览](badges_overview.png) 和 [资源清单](manifest.json)。总览中的中文只是检查用的独立文字，**39 个 SVG 和 39 个 PNG 控件均未烘焙动态文字**。

## 资源范围

| 类别 | 每张尺寸 | 状态 / 数量 |
|---|---|---|
| `primary_button` | 460 × 112 | normal / selected / disabled，共 3 张 |
| `tab` | 360 × 114 | 三态，共 3 张 |
| `list_row` | 360 × 96 | 三态，共 3 张 |
| `server_card_wide` | 640 × 141 | 三态，共 3 张 |
| `server_card_medium` | 520 × 126 | 三态，共 3 张 |
| `search` | 420 × 84 | 三态，共 3 张 |
| `summary_bar` | 1280 × 79 | 1 张 |
| `main_frame` | 1440 × 840 | 1 张 |
| `content_panel` | 1080 × 620 | 1 张 |
| `round_badge` | 120 × 120 | 太极、楼阁、莲花、山、炼丹炉、剑、水纹、罗盘、桃灵、火焰，共 10 张 |
| `status_dot` | 32 × 32 | 绿勾、橙感叹号、灰横线，共 3 张 |
| `recommend_badge` | 96 × 40 | 1 张，无文字；客户端叠加“推荐” |
| `check` / `lock` | 48 × 48 | 各 1 张 |
| `gold_flower` | 120 × 120 | 1 张 |
| `cloud_corner` | 160 × 160 | 1 张；可镜像至其余三角 |

`svg/` 是可缩放源文件，`png/` 是与清单尺寸一致的透明 RGBA 导出。边缘透明区域包含阴影留白，不是额外可点击区域。圆徽标中的楼阁、莲花、山等是功能图形，不代表生产职业或服务器类型。

## 九宫格与原生文字

`manifest.json` 为可伸缩板件记录 `nine_slice.left/top/right/bottom`，单位是**原始 PNG 像素**；这四个值是保持不变的边框厚度，`center` 同时给出可拉伸矩形。边框值已经包含阴影和透明留白。圆徽标、状态点与装饰不做九宫格，等比缩放。

`minimum_size` 防止两侧固定区域碰撞；`content_insets` 是推荐文字和内容边距；`text_color` 是对应底色的文本颜色。服务器卡片右侧预留独立圆徽标区域，不会把圆徽标一起拉伸。实际触控尺寸、排版、锚点和像素密度由客户端确定。

**带勾记、锁形或放大镜的六类三态控件及摘要栏只按原高度做横向九宫格**，清单中为 `resize_axes: horizontal` 与 `fixed_height`；否则标识处于左/右边条中段，纵向拉伸会改变其形状。主框架和内容面板标记为 `resize_axes: both`，允许双向九宫格。若确需改变按钮高度，可整体等比缩放，或将标识分离后用原生图标叠加；不要直接纵向拉伸成品 PNG。

保持正方形徽标比例。背景纹理与渐变也会随九宫格中间区域伸缩，适用于有限范围的宽高变化；跨度很大时优先按目标尺寸重建 SVG 或调整原生布局，不把细长摘要栏拉成整页面板。

动态游戏名、服名、角色名、状态、搜索输入和按钮字由客户端文字层绘制。建议原尺寸按钮 / 页签 28–32 px，列表 / 卡片 / 搜索 24–28 px；缩小整个总览不是运行时文字尺寸规范。深绿底使用米白字，浅底使用深色字；禁用态仍保留可读文字，不用透明度把标签一起淡化。

## 状态与交互边界

- `selected` 同时使用勾记、边缘标识和底部小三角，不能仅靠颜色判断。选中不是推荐，也不等于 hover 或键盘焦点。
- `disabled` 包含锁形。客户端还应显示明确原因，并禁止相应动作；返回、清空或改选等恢复入口按业务保持可用。
- 状态点用颜色加形状区分；绿 / 橙 / 灰分别用于可用 / 繁忙 / 不可用的设计示意。服务端实际枚举由客户端映射，橙色不自动意味着禁入。
- 推荐徽标与勾选图标分别使用；“推荐”文字通过客户端叠加。
- 搜索框三态是视觉资源，不实现输入、焦点或验证。焦点与悬停需要原生控件在当前资源上额外提供可辨认的轮廓；此包不提供程序逻辑。

本套件只覆盖上述控件，未实现引擎导入、运行时九宫格、鼠标/键盘交互或页面事件绑定。

## 本地重建

需要 Node.js 22 或更高版本，PNG 导出需要已经安装的 `sharp`。本次使用 Sharp 0.35.4 / libvips 8.18.6；构建脚本不下载依赖、不读取凭证、不调用图片 API，并且只写入当前 `components/`。

```sh
node build.mjs --sharp "<已安装的 node_modules>/sharp"
```

Windows 本机的复现示例：

```powershell
& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' `
  './build.mjs' `
  --sharp 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp'
```

在其他电脑上替换上述运行时与包路径。若 Sharp 可以从本脚本解析，直接 `node build.mjs` 即可；脚本也会检查当前用户的 Codex bundled runtime。无 Sharp 时可执行 `node build.mjs --svg-only` 只重建 SVG / 清单 / 网页，清单会将 PNG 路径置空；已有 PNG 不会被删除或假称为本次重新导出。

构建后 [validation.json](validation.json) 记录 39 张 PNG 的尺寸、RGBA 与 Alpha 范围。再用浏览器打开 `overview.html` 检查形状、边缘、标识和客户端叠字空间。本次另经 XML 解析确认 39 个源文件有效且没有 `<text>`、外链图片或脚本；透明 PNG 完整性、尺寸、状态对应关系和九宫格边界检查通过，并已实看总览核对勾记、锁形、边缘和图标。引擎内九宫格和交互尚未验收。

## 十枚圆徽标补齐记录

六枚新增徽标沿用原四枚的底盘几何、双金边、玉绿渐变与阴影；尺寸统一为 120 × 120，符号使用米白和暖金。先实看旧母图确认炼丹炉、竖剑、旋涡水纹、八向罗盘、桃果叶片与卷芯火焰，再以原生 SVG 重绘。桃灵沿用桃果语义，不新增人物脸或职业定义。完整制作指令与逐项旧资源映射见 [设计说明](badge_design_brief.md)；同一映射已写入清单的 `badge_replacements`。

[徽标 SVG 总览](badges_overview.svg) 与 PNG 总览同时检查 120、48、32 px。已实看十枚同框及小尺寸行，六枚轮廓可区分；32 px 会减少炉身火纹、剑柄等内部细节，建议有操作含义的徽标采用 48 px 或更大并配原生标签。图标本身不提供运行时触控区域或交互。

[补齐验证记录](badge_validation.json) 包含 39 个 SVG 的 XML 与禁嵌元素检查、39 个 PNG 的尺寸与 Alpha 检查、10 枚徽标的透明角落、SHA-256，以及与交接提交 `60134a6` 中原 33 枚输出的比较。原 33 个 PNG 内容未改变；原 SVG 在换行规范化后内容未改变。新徽标文件名固定为 `round_badge_furnace`、`round_badge_sword`、`round_badge_water`、`round_badge_compass`、`round_badge_peach_spirit` 和 `round_badge_flame`，各有同名 SVG 与 PNG。
