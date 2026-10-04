# 冰剑少女本机旧成果复核

2026-10-03，旧目录只读。本轮并未把新批目录没有PNG当作以前没做。

| 位置 | 实存与使用结论 |
|---|---|
| `qdao_original_roster_v13/candidate/01_ice_sword_girl/walk/` | 八方向各16帧，512×512。E01–16 SHA与旧manifest及frame-sources逐一相符；用于480/640/720/800ms旧基线比较。旧lowest_alpha_gt_8逐帧贴地规则不沿用。原母图已清理，不能恢复为原生1024帧。 |
| `qdao_original_roster_v14_hd/run-correction-20260930/characters/01_ice_sword_girl/` | 7次原生1254尝试，六个E槽01/03/05/09/11/13。最新review通过0；09-v1/11-v1换手，05/13未交替，03比例/支撑漂移，09-v2上身改善但尺度漂移。E01用于本轮编辑身份与近剑后摆参考，不直接冒充已验收跑步帧。 |
| `qdao_original_roster_v14_hd/combat-20260929/characters/01_ice_sword_girl/` | 受击E01/03/06三个在制候选及receipt仍在，pending；没有已通过完整战斗段。没有覆盖/改速。 |
| `qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/01_ice_sword_girl.md` | 实际复核交接，受击缺E02/04/05、W01–06；普攻E/W各12、施法E/W各16缺失，总计65战斗槽。历史另一电脑路径仅作记录。 |
| `qdao_original_roster_v14_hd/battle_actions_20260930/work/01_ice_sword_girl/attack_E.raw.png` | 1536×1024六格拒稿，剑跨格；不计普攻完成。 |

旧原生尝试均有可追溯来源，但没有一张能不经改动直接保证完整新循环成立。本轮沿用其身份、动作经验和E01输入，针对性补绘与重试；旧图/战斗候选保持只读。

官方模型/质量目标已在本轮打开核对：[GPT Image 2.5 Sunburst](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)、[Images 2.5发布](https://openai.com/index/introducing-chatgpt-images-2-5/)。沿用本批配置目标2.5/max。内置工具没有model/quality选择器，实际返回未披露；所有新图实际型号/质量均null。没有收费API/CLI调用，没有更改共享配置。
