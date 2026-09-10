# 五行奇谈 · UI 统一风格重制与重新切图 v10

日期：2026-09-10。用户要求全部 UI 和 UI 切图采用指定选角图的风格，继续保留道家 Q 版与春节、元宵、中秋元素。其他游戏截图默认仅提供功能参考。规则与通用提示词唯一维护入口为 [UI 制作规范第 2 节](../qdao_ui_redesign_v5/UI_SPEC.md#2-统一视觉与控件层级)。

## 当前进度

- 已将[用户参考原图](../docs/references/ui-style-20260910.png)原样归档：2560×1080，SHA-256 `913e301b1955a4dd78888bebcec82d1dbf504c0517ed606cc8eaab667675b825`。
- 已更新 UI 规范、项目入口、美术定调、节庆方案、交接和属性制作 brief；已保存六组具体原画提示词及现有切片合同。
- 首次内置生图通过本地路径读取参考图时遇到 Windows 沙箱 ACL 故障；此错误属于文件输入通道，不是 GPT Image 2 不可用，也不需要靠配置 API 密钥解决。
- **内置生图已实际成功**：指定图转为内存中的 1280×540 对话参考图片后，使用 `image_gen` 的 `num_last_images_to_include=1` 完成[第一组无字控件原画](source/01-plates.png)，实际原生尺寸 1254×1254；提示词期望的 2048×2048 不作为原生尺寸。当前只完成第一组原画，其余组和正式重新切图继续制作；尚未替换正式资源。详情见 [生成状态](generation-status.json)。
- **当前执行方式为内置 GPT Image 2**：用户在授权继续制作后再次明确要求直接使用 ChatGPT 内置生图。此路径无需 `OPENAI_API_KEY`，以最高质量为目标；当前工具未开放 model／quality 参数，不宣称显式强制 high。[官方说明](https://learn.chatgpt.com/docs/image-generation)确认内置模型为 `gpt-image-2`，计入 Codex 用量。
- 历史 API 备用尝试在发出请求前返回 `OPENAI_API_KEY not set`，没有产生图片或发送 API 请求。这只描述备用路径的状态，不再作为本轮继续内置生图的阻塞条件；既有授权保留在记录中。

## 待重制与重切范围

| 家族 | 正式 PNG 数量 | 合同／来源 |
|---|---:|---|
| 通用控件与状态 | 39 | [components.json](contracts/components.json) |
| exact 切图与旧原子控件、徽标及图集 | 73 | [legacy.json](contracts/legacy.json)，含 50 exact + 23 atomic |
| 旧选服分层与兼容画面 | 12 | [layers.json](contracts/layers.json) |
| HUD 透明皮肤／标签／叠层 | 3 | 现有 HUD 布局与资源；纯标签层按功能需求保留文字 |
| 人物／宝宝属性切图 | 31 | [attributes.json](contracts/attributes.json) |

上述 158 PNG 为已盘点正式输出合同，另含关联 SVG 包装与清单。不把 QA 总览算进正式切片数。参考图、历史记录和当前人物／场景来源保持可追溯；重建 UI 组合时使用各相关任务最新已完成资源。

## 已备好的原画提示词

| 文件 | 负责内容 |
|---|---|
| [01-plates.prompt.txt](source/01-plates.prompt.txt) | 主／次按钮、普通／选中卡片、标题和禁用底板 |
| [02-main-window.prompt.txt](source/02-main-window.prompt.txt) | 主窗框与纸面，固定边饰区 |
| [03-content-window.prompt.txt](source/03-content-window.prompt.txt) | 清雅细金边内容面板 |
| [04-emblems.prompt.txt](source/04-emblems.prompt.txt) | 十枚徽标、勾锁与状态图标 |
| [05-ornaments.prompt.txt](source/05-ornaments.prompt.txt) | 云纹、分隔、太极体系配饰与三个节日的小装饰 |
| [06-attribute-fields.prompt.txt](source/06-attribute-fields.prompt.txt) | 数值框、滑杆、页签、头像框和小操作控件 |

六组均实际附上指定图作为风格参考，再视工具返回尺寸记录原生输出。透明度以实际 Alpha 核验；若输出非透明，先通过生图工具取得适合抠图的纯色底，不把棋盘格当透明。已保存提示词要求透明，但模型/API 是否支持相应输出应按当次真实结果处理。

## 继续执行与验收

1. 先读本 README 与 UI 规范；读取 `contracts/current_files.json`，确认现有资源自盘点后是否改变。若其他窗口已产出更新，重新核对最新来源，不覆盖其未完成结果。
2. 按用户最新要求直接用内置 GPT Image 2 继续，以最高质量为目标。实际附上指定风格图；本地路径输入失败时，排查输入通道，在工具支持的范围内使用对话图片参考，不要求用户另配 API 密钥。记录真实调用参数、原生尺寸和来源；先验收第一组画法，再推进其他组。
3. 逐控件记录源裁切矩形与固定边距，导出到 `staged/<原资源相对路径>`。旧 v7 统一比例的九宫格切分不能代替新图实际边饰分析；不得只留最大连通域而误删玉珠、流苏等分离装饰。
4. 统一导出 39 通用与 31 属性件，再同步 73 旧路径兼容件，最后重建 12 选服与 3 HUD 输出及关联 SVG。保留原资源名、画布、Alpha、九宫格、图集帧坐标和状态语义；纯文字层允许保持不变并记录原因。
5. 使用 [核验脚本](tools/validate_staged.py) 对照快照检查尺寸、透明边缘、真像素变化与缺失，并查看逐组联系表；另做九宫格拉伸与整屏重新拼合实看。只有完整资源验收后才替换正式路径，并保存可回退来源、实际提示词和来源映射。
6. 本目录的准备状态不等于 Unity 接入；如同步客户端，使用该项目的已确认资源键、导入边距和原生渲染验证。原全库节庆精修监测与等待顺序仍由[节庆方案](../docs/QDAO_FESTIVAL_REFINEMENT.md)维护。
