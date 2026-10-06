# 七套主城并行制作

用户于2026-10-05确认每套主城图各一个独立任务。以下7个任务均已实际创建；全部来源交接已就绪。每套目标256张4096×4096，整图65536×65536，继续内置生图、GPT Image 2.5目标配置，不使用付费API。

| 任务 | 内部资产ID | 交接 | 当前任务进度 |
| --- | --- | --- | --- |
| 01 主城节庆地图 | `tianyong_festival` | [来源](tianyong_festival/handoff.json) | [进度](tianyong_festival/progress.json) |
| 02 小镇日景地图 | `lanxian_day` | [来源](lanxian_day/handoff.json) | [进度](lanxian_day/progress.json) |
| 03 小镇春节地图 | `lanxian_spring` | [来源](lanxian_spring/handoff.json) | [进度](lanxian_spring/progress.json) |
| 04 渔村日景地图 | `donghai_day` | [来源](donghai_day/handoff.json) | [进度](donghai_day/progress.json) |
| 05 渔村元宵地图 | `donghai_lantern` | [来源](donghai_lantern/handoff.json) | [进度](donghai_lantern/progress.json) |
| 06 仙岛日景地图 | `penglai_day` | [来源](penglai_day/handoff.json) | [进度](penglai_day/progress.json) |
| 07 仙岛中秋地图 | `penglai_mid_autumn` | [来源](penglai_mid_autumn/handoff.json) | [进度](penglai_mid_autumn/progress.json) |

[实际任务ID清单](dispatch-index.json) · [父任务冻结的29块在制源集](../resume_single_city_20260921/completion_20261004/current-work.json)

各任务正在补新区域。父任务冻结源集为29/1792个完整4K候选坐标，正式验收0、整城完成0；新片段不算完整图块，任务数也不代表地图完成数。实际新增产出看各任务进度与绑定图像检查记录。

旧目录ID仅作历史追溯，正式原创地名映射仍以项目已确认设计为准。每张新生成图片记录配置目标、真实参数、实际披露值、时间、来源和哈希；内置未披露的实际型号/质量保持未确认。
