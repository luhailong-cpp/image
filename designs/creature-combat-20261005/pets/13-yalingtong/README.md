# 芽铃童 · 战斗动作

本包只沿用 Image 原有芽铃童：棕发橡果帽、苔绿短衣、双种铃悠悠球，每手一绳一铃。两臂两腿；右腰两种子袋，左腰红结短穗。无移动循环。

**正在制作与修正，尚未最终验收。** 当前准确数量及缺帧见 [technical-audit.json](technical-audit.json)，状态见 [STATUS.md](STATUS.md)。

## 规格

| 动作 | 每向帧数 | 帧时长 | 总时长 |
|---|---:|---:|---:|
| hit 受击 | 6 | 40ms | 240ms |
| attack 普攻 | 12 | 30ms | 360ms |
| cast 施法 | 16 | 45ms | 720ms |

E 为真斜前朝右下；W 为独立绘制的真斜后朝左上。两向合计68张1024×1024 RGBA透明PNG。编号各组从01开始；预定pivot为左下坐标[0.5,0.08]、顶部锚点[512,942]。动作允许原地蓄力、屈膝、反冲、抬跟与回位。

## 打开预览

[六组交互预览](preview/index.html)支持正常1×、0.25×慢放、暂停、单步与逐帧滑杆，另有深底/白底与透明棋盘。每组附全帧总览；完成组还提供正常/慢放无损WebP。预览读取正式PNG，不另造动画姿态。

## 文件与证据

- 正式资源候选：`runtime/<hit|attack|cast>/<E|W>/01.png`等。
- [manifest.json](manifest.json)：逐帧动作、方向、时间、锚点、事件、SHA与生成记录索引。
- [SHA256SUMS.txt](SHA256SUMS.txt)：PNG文件校验值。
- `prompts/`：逐次实际提示词；`evidence/`及部分图旁`*.generation.json`：请求、返回路径、原生SHA、模型证据与重试历史。
- [POSES.md](POSES.md)：身份、解剖归属和动作阶段。
- [MODEL_CHECK.md](MODEL_CHECK.md)：本批模型核对。

全部姿态使用宿主内置 `image_gen` 逐帧生成/编辑；未使用付费API/CLI。目标为用户指定GPT Image2.5/max；工具没有model/quality选择器、返回未披露实际型号和质量，逐图actualModel/actualQuality均为null。原生返回1254方图与1024导出分开记录，不冒称原生1024。后处理只做统一导出，不复制、镜像、平移或插值制造动作帧。

本包尚未接入或验证游戏客户端。
