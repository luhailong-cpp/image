# 08 炼丹童子 · 当前动作交接

2026-10-04。本目录是本角色当前交付入口。按用户认可的09竹弓少女核对八方向下肢姿态，并更新1200ms配时。本轮已完成34张修正帧的最终合并，替换清单以grounding-selection.json为准。早期选表及静态报告保留为历史证据，以本文件、manifest.json、grounding-selection.json和run-timing.json为准。

## 正式资源

| 动作 | 方向 | 帧数 | 时长 |
| --- | --- | --- | --- |
| run | N/NE/E/SE/S/SW/W/NW | 各16，共128 | 各1200ms，每帧均匀75ms |
| hit | E/W | 各6，共12 | 各240ms，40ms/帧 |
| attack | E/W | 各12，共24 | 各360ms，30ms/帧 |
| cast | E/W | 各16，共32 | 各720ms，45ms/帧 |

runtime为196张1024透明RGBA。E/W独立生成，没有镜像、复制帧或插值补槽。manifest记录SHA、逐图来源、导出操作、相位及previewDurationMs；PNG相邻的generation.json保存同条记录。run-timing.json给出八方向完整16项75ms时长数组，1200÷16=75；旧快速档已移除。

preview/index.html支持正常1×、0.25×、逐帧、128/256小视图与背景切换。默认1200ms、均匀75ms；640/720/480/800ms等旧快档已从正式预览移除。普攻命中标记仍为06（150ms）；施法E09（360ms）、W10（405ms）。战斗节奏未因本次跑步反馈整体减速。

## 本轮修图

- E02增加屈膝承重。E04–10把近侧后靴从整块棕色鞋底朝外，改为沿右向跑步平面的侧面；E10保留落地压重。
- NE08/16补平底初次接触，NE09反向鞋尖改向右上；NE10/11原本方向正确，保留。
- N04、NW04改善蹬离，N11最终v6把浮起的平掌支撑补回相邻帧接触带。
- NW按竹弓少女修正小腿、踝和靴形透视，让前后摆腿沿NW行进平面。全16帧的最终来源见选表。
- S04/12改善正向前掌蹬离，SW02从朝W侧靴转为朝SW的承重靴；SW06/07前摆鞋尖从右下改朝左下，保留屈膝到渐伸背屈的先后关系。
- 其余正确帧保留。左右受击、普攻、施法全部联系表重新核查，未发现同等级反脚；持物归属为解剖右手丹炉、左手药瓶。

替换列表与理由见grounding-selection.json。原始提示词、来源及模型证据在generation/grounding-20261003和generation/bamboo-reference-20261003的文字记录，连续编辑链在provenance/grounding-20261003/edit-lineage.json。竹弓参照修正的逐槽选择和独立审阅在provenance/bamboo-reference-20261003。

## 画布与根点

未修帧沿用原1254画布统一缩至940、放到1024画布(42,50)的初始导出。此次修图输入已经是注册好的runtime，故新1254编辑结果只做完整画布统一缩至1024、偏移0；不能再套一次940+(42,50)。每帧operation是权威参数。

逻辑根点仍为(512,942)，用于摆放，不是所有透视脚底的接触线。没有逐帧包围盒适配、整身贴脚平移或图像扭曲。远近脚、摆腿和支撑必须结合相邻相位判断。

## 验证与边界

196文件、独立来源、1024RGBA、透明通道、来源记录SHA、14组预览引用及8组1200ms数组已通过tools/verify_delivery.py。浏览器正常与慢速采样、128/256显示及战斗资源加载已复核；脚向与承重配时反馈已落实。截图采样和逐帧联系表不是连续游戏录像，因此dynamicAccepted不冒充完整游戏动态认证。

N11旧版约10px的浮脚差异已由v6替换，最终支撑底位于相邻帧接触带。S12为晚蹬离，前掌投影约高11px；E/NE部分发梢及躯干轮廓仍有小幅绘画差异。没有逐帧平移整身掩盖差异。最新结论见provenance/grounding-20261003/review-result.json。

本机无D:/work/mmorpg-client，未运行或覆盖客户端。实际位移速度、滑步、跨方向与idle过渡、命中和特效同步仍需游戏接入验证。受击/普攻/施法交付范围是E/W，不应误报为八方向。

## 来源与清理

配置目标GPT Image 2.5 Sunburst/max；内置imagegen无型号/质量选择器，也未披露实际返回值，记录null/未确认。没有使用收费API或CLI。保留逐图文本证据，不将配置目标或提示词当作已锁定实际模型。

按用户素材保留规则，正式导出及引用闭合后清理原图、拒稿和加工中间图，保留196张runtime、14张当前联系表及所有文字记录。早期清单为provenance/cleanup-images-20261003.json；一次被自动审批阻止的旧尝试保留在provenance/grounding-20261003/cleanup-result.json。最终本轮清理结果记录于provenance/bamboo-reference-20261003/cleanup-result.json。历史来源图路径不是运行依赖。

tools/rebuild_runtime_preview.py从当前runtime重建预览，可运行。tools/verify_delivery.py可核验当前交付。旧build_preview.py、export_delivery.py及本轮apply_grounding_revision.py依赖清理前原图，保留为制作记录，清理后不要重跑。以后修图以当前runtime作为输入建立新的来源链。


本轮最终合并、浏览器复核和素材清理已完成：删除75张源图/拒稿/中间图（84,511,609字节），保留196张runtime与14张当前联系表。全部文字证据保留；详见STATUS.md及最新cleanup-result.json。

最终NW14采用generation/bamboo-reference-20261003/NW/14-v5.png的导出：直接以编辑前runtime14锁定构图，只取v1的靴方向参考，去除串入绿坠。v2–v4为构图改变的拒稿。最终源选择与SHA见provenance/bamboo-reference-20261003/NW/selection-final14.json。原PNG已按规则清理，逐图记录仍在。

播放时钟验证：tools/verify_preview_timing.cjs实际执行当前预览的durations/tick函数，14组动作×2档共28例通过，完整16帧回到首帧，无额外循环停顿。浏览器检查记录：provenance/bamboo-reference-20261003/browser-final-review.json。
