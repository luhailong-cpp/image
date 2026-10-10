# 五套主城制作

用户于2026-10-08明确取消02小镇日景、03小镇春节。后续只制作与交付原编号01/04/05/06/07；[production-scope.json](production-scope.json)是当前权威范围，覆盖旧七套要求。每套256张4096×4096，整图65536×65536，继续内置生图、GPT Image2.5目标配置，不使用付费API。

| 任务 | 内部资产ID | 交接 | 当前任务进度 |
|---|---|---|---|
| 01 主城节庆地图 | `tianyong_festival` | [来源](tianyong_festival/handoff.json) | [进度](tianyong_festival/progress.json) |
| 04 渔村日景地图 | `donghai_day` | [来源](donghai_day/handoff.json) | [进度](donghai_day/progress.json) |
| 05 渔村元宵地图 | `donghai_lantern` | [来源](donghai_lantern/handoff.json) | [进度](donghai_lantern/progress.json) |
| 06 仙岛日景地图 | `penglai_day` | [来源](penglai_day/handoff.json) | [进度](penglai_day/progress.json) |
| 07 仙岛中秋地图 | `penglai_mid_autumn` | [来源](penglai_mid_autumn/handoff.json) | [进度](penglai_mid_autumn/progress.json) |

[当前39块候选汇总与预览](parent_audit_20261008/README.md) · [统一索引](parent_audit_20261008/verified-current-index.json) · [五处同坐标父修补](parent_audit_20261008/parent-repair-current-overlay-v3.json)

**39/1280个完整4K候选，尚缺1241；正式验收0、完整城市0/5。** 本次仅按取消要求从已核验53块快照排除两套各7块，不加入未审计新图；父修补不增加坐标。

两套取消图的全部已有图片、来源与检查记录保留，未删除素材。[历史53块索引](parent_audit_20261008/historical-seven-appearances-53-before-cancellation.json)及[旧七任务创建记录](dispatch-index.json)仅供追溯，不能恢复已取消的制作范围。[线程状态回执](town-cancellation-thread-receipt-20261008.json)由父任务记录。

每张新图继续记录目标配置、真实提交参数、实际披露值与来源；内置未披露的实际型号/质量保持未确认。
