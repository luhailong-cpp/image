# 08 炼丹童子 · 当前动作交接

2026-10-04。本角色八方向跑步接地修正已导出并完成离线复核；本轮 85 张替换以 contact-pairs-selection.json 为准。当前权威入口为 manifest.json、run-timing.json 和 runtime；此前选表与审阅记录仅作为历史来源证据。

## 正式资源

| 动作 | 方向 | 帧数 | 正常配时 |
| --- | --- | --- | --- |
| run | N/NE/E/SE/S/SW/W/NW | 各 16，共 128 | 各 1200 ms，每帧 75 ms |
| hit | E/W | 各 6，共 12 | 各 240 ms，每帧 40 ms |
| attack | E/W | 各 12，共 24 | 各 360 ms，每帧 30 ms |
| cast | E/W | 各 16，共 32 | 各 720 ms，每帧 45 ms |

共 196 张 1024×1024 透明 RGBA，196 个不同图像 SHA 与独立来源 SHA。PNG 相邻 generation.json 与 manifest 对应，记录来源、导出操作、相位和时长。战斗动作仅交付 E/W；本轮保留原 68 张战斗图片及配时。

preview/index.html 提供正常 1×、0.25×、暂停逐帧、128/256 显示、背景切换及联系表。正式页面仅引用 runtime，不依赖已经清理的原图。普攻事件标记为 06（150 ms）；施法 E09（360 ms）、W10（405 ms），客户端尚未验证事件接入。

## 本轮修正

本轮替换 N 9、NE 8、E 11、SE 12、S 11、SW 12、W 10、NW 12，共 85 张；其他 43 张跑步帧保持。以用户认可的 09 竹弓少女核对方向和膝踝关系，修复脚掌外撇、反向鞋尖、提前抬起支撑足和错换支撑足。解剖右手持丹炉、左手持药瓶，随视角遮挡但不交换。

最新接地顺序是同一支撑脚每位置两个独立姿态：右足 16/01→02/03→04/05→06/07，左足 08/09→10/11→12/13→14/15。依次为身体前方初接触、身体下承重、稍后承重、更后前掌推蹬，每对 150 ms。旧的中间四帧解释和 05/13 腾空标签不再适用。详见 RUN_PHASES.md。

## 画布与根点

本轮以已注册 runtime 为编辑输入，原生 1254 画布只做完整画布统一缩至 1024、偏移 0。不要再次应用旧的 940+(42,50)。未修历史帧的原始导出可能保留该旧参数，以每帧 operation 为准。

逻辑根点仍为 (512,942)，用于摆放，并非所有透视脚底的接触线。无逐帧包围盒适配、整身贴脚平移或扭曲。少量发梢和上身轮廓仍有绘画差异，不宣称像素级一致。

## 验证

- tools/verify_delivery.py：196 文件、不同图像与来源 SHA、1024 RGBA、透明通道、来源记录 SHA、14 组预览引用和 8 组 1200 ms 配时通过。
- tools/verify_preview_timing.cjs：执行正式页面时钟逻辑，14 组×正常/慢放共 28 项通过，循环无额外停顿。
- 浏览器：14 组、196 张全部成功解码为 1024；正常/慢放采样、重点接触帧与 128/256 小图检查完成。
- 全部八方向联系表经逐帧及支撑半圈复核；独立文件审计确认选择、配时与引用闭合。

最终审阅记录为 provenance/contact-pairs-20261004/review-result.json。技术与时钟报告分别为 provenance/delivery-technical-verification.json、provenance/preview-timing-verification.json。

本机未运行客户端。连续游戏位移、滑步、跨方向与 idle 过渡、命中及特效同步尚未验收；dynamicAccepted/clientValidated 保持 false，不将离线截图采样当作完整游戏动态认证。

## 来源与清理

本批使用内置 image_gen。配置目标 gpt-image-2.5-sunburst / max；入口未提供型号或质量参数，返回也未披露，实际值记录 null/未确认。未使用计费 API/CLI。完整提示词、原调用与逐图记录保留在 generation/contact4-20261004 和 generation/contact-pairs-20261004；159 条生成记录的来源链见 provenance/contact-pairs-20261004/edit-lineage.json。

按用户规则，已删除本轮 188 张原图、拒稿及加工中间图，共 202,832,603 字节，无图片备份。目录仅余 196 张 runtime 和 14 张当前联系表；全部来源文字和配套设计/接入文件保留。清单与结果位于 provenance/contact-pairs-20261004/cleanup-plan.json 和 cleanup-result.json。来源记录中的历史图片路径用于追溯，不是运行依赖。

可运行 tools/rebuild_runtime_preview.py 从当前 runtime 重建预览，或运行 verify_delivery.py 和 verify_preview_timing.cjs。原生图已清理，制作历史中的 export_delivery.py、apply_grounding_revision.py、apply_contact_pairs.py、close_contact_pairs_delivery.py 及候选工作页生成脚本不要重跑。临时 contact-pairs-work.html/data.js 已删除。以后修图以当前 runtime 为输入建立新来源链。
