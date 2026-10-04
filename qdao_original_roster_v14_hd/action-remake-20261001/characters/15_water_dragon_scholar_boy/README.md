> 当前状态：用户指出其他方向仍不正确，上一轮离线通过结论已撤回，正按09竹弓少女当前版定向重修。跑步最新正式预览参数为1200ms/圈、16帧各75ms；旧快速档已移除。下文上一轮交接细节尚待本轮完成后更新，不能据此宣称本轮已完成。

# 15 水龙书生 · 动作交付

本角色共 196 帧，已齐并完成逐帧静态复核：跑步八方向各 16 帧，受击 E/W 各 6 帧，普攻 E/W 各 12 帧，施法 E/W 各 16 帧。沿用已有可用帧与单帧制作方法，针对手脚、握扇、脚掌朝向和接地问题修正；没有使用另一台电脑未提交的素材，没有镜像或插值补帧。

最终正常／慢速播放结论以 [主审离线复核记录](audit/final-review.json) 为权威，应用状态见 [manifest](manifest.json)。`offline_reviewed` 仅表示本聊天／主审完成离线复核；用户尚未验收，客户端未接入、未运行验收。

## 查看与核对

- [单动作、正常／慢速和逐帧预览](preview/index.html)。
- [八方向跑步与六组战斗同播](preview/all-directions.html)：240px 显示，支持节奏比较。
- [八方向跑步总览 GIF](preview/run-all-directions.gif)与[当前关键姿态](preview/key-poses-current.png)。
- [成品清单与 SHA](manifest.json)、[逐图派生记录](provenance/derived/)、[当前进度](STATUS.md)。
- [逐图来源核验](audit/final-provenance-check.md)、[最终交付技术检查](audit/final-delivery-check.json)、[合并交接](MERGE_HANDOFF.md)。

跑步本地节奏为 `weighted720`，每半圈时长 `[50,70,60,40,30,25,35,50]ms`，重复两次共 720ms。HTML 按原始逐帧毫秒计时；GIF 的 10ms 精度量化为 `[50,70,60,40,30,30,30,50]ms × 2`，周期仍为 720ms。480ms 仅作旧基线，640/720/800ms 均匀节奏保留在 HTML 中比较。受击 240ms、普攻 360ms、施法 720ms，战斗原时序保留。

正式图片为 `runtime/<action>/<direction>/<frame>.png`，1024×1024 RGBA。固定将完整 1254 画布缩至 940，放入 1024 画布的 `(42,49)`，虚拟根 `(512,942)`，接入约定 pivot `(0.5,0.08)`；没有按逐帧脚底或包围盒对齐。

## 来源与留存

本轮选择为 195 张本批生成图及 1 张旧图复用。精确文件、SHA、选帧与原始生成证据见 `manifest.json`、`sources-index.json`、`provenance/derived/*.json` 内嵌的 `originalGenerationRecord`，以及保留的生成记录、请求、回执和提示词。以记录中的实际路径为准，不能假定所有回执都使用同一种文件后缀。旧来源与历史机器路径保留原义，不改写为本批生成。

模型目标为 GPT Image 2.5 Sunburst / max；本批使用宿主管理的内置生图入口。工具没有型号／质量选择器，未披露的实际 `model/quality`、`actualModel/actualQuality` 记录为 null／未确认，配置目标不代表逐图实测。

最终验证后已按 [清理执行记录](audit/retention-executed.json) 删除本角色目录内 514 张原图、退稿与中间图片，保留 196 张正式 PNG 和 44 张必要预览，共 240 张图片；完整来源文字继续保留。清理后的技术检查为 0 错误、0 警告。`source`、`inventory` 和历史记录中的原图路径记录生成历史，源像素已清理；可用 `tools/final_delivery_check.py` 核验成品与来源文字链，不再运行依赖原图的导出脚本。

当前收尾环境只读核查到 Git 分支为 `main`，与批次启动记录的 `codex/character-actions-20261001` 不同。本聊天未切分支、暂存、提交或推送；由用户在另一台电脑按交接记录合并。
