# 冰剑少女动作 · 当前状态

更新：2026-10-04T14:11:00.824160+00:00

实际导出 164/196 张1024透明候选；技术检查通过 164 张，完整序列 12/14。图像数量与美术验收分开记录。
八方向最新“两帧一个位置、同脚连续支撑8帧”检查通过方向：暂未全部完成验证。

[全动作当前预览](preview/all.html) · [逐序列与来源清单](manifest.json) · [最新接地要求](review/paired-position-contact-requirement.json)

跑步固定16帧×75ms＝1.2秒/圈。受击6×40ms，普攻12×30ms，施法16×45ms。
同一脚依次前落地、身体靠近、身体经过、后蹬，每个位置两张不同关节姿态，然后换脚；不以腾空帧或重复帧补接地。

| 动作/方向 | 已导出/目标 | 单帧ms | 当前美术状态 |
|---|---:|---:|---|
| run/S | 16/16 | 75 | needs_sequence_review |
| run/SE | 16/16 | 75 | needs_sequence_review |
| run/E | 16/16 | 75 | needs_sequence_correction |
| run/NE | 16/16 | 75 | new_contact_4_positions_x2_frames_revision_in_progress |
| run/N | 16/16 | 75 | new_contact_4_positions_x2_frames_revision_in_progress |
| run/NW | 0/16 | 75 | not_yet_reviewed |
| run/W | 16/16 | 75 | static_inspected_sequence_review_pending |
| run/SW | 0/16 | 75 | not_yet_reviewed |
| hit/E | 6/6 | 40 | candidate_segment_complete_needs_motion_grounding_review |
| hit/W | 6/6 | 40 | candidate_segment_complete_with_grounding_variation |
| attack/E | 12/12 | 30 | candidate_segment_complete_pending_motion_review |
| attack/W | 12/12 | 30 | candidate_segment_complete_pending_motion_review |
| cast/E | 16/16 | 45 | candidate_segment_complete_static_reviewed_pending_motion_review |
| cast/W | 16/16 | 45 | candidate_segment_complete_static_reviewed_pending_motion_review |

## 范围和来源

仅修改本角色目录。没有修改其他角色或客户端，没有Git提交、推送。
实际对照用户确认的09竹弓少女当前同方向动作，只参考姿态、脚轴、手臂链和接地，不复制其人物/服饰/武器。
冰剑少女始终右手冰剑、左手蓝符；近远侧按各自肩→袖→肘→手追踪。
斜向地面的投影随深度变化，不用最低透明像素把每帧鞋底强贴到同一水平线。
所有导出只做完整方形画布等比缩放，无镜像、重复图、姿态插值或整图平移。
逐图generation记录保存来源、SHA、原生尺寸、实际提示词和工具回执。
同批配置目标2.5 Sunburst/max；宿主内置image_gen未披露实际型号/质量，实际值均为null，未把提示词当作参数证据。

## 客户端与保留

客户端D:/work/mmorpg-client存在，但本任务未接入或运行客户端。预览的75ms不代表游戏内速度已经改变。
最终素材与当前引用闭合后清理淘汰图；尚在编辑和验收期间保留所需在制源。
旧E单向审阅文档和四帧最低接地记录是历史过程，不作为最新完成依据。
