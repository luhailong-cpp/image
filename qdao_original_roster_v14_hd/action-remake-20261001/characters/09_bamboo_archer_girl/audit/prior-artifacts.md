# 09 竹弓少女本机旧动作审计

核查日期：2026-10-01（用户时区 America/New_York）。精确核查时间、15份旧文件 SHA256 与196个缺槽见同目录 `prior-artifacts.json`。

## 磁盘实际库存

| 入口 | 文件总数 | PNG 数 | 可复用新动作帧 |
| --- | ---: | ---: | ---: |
| `qdao_original_roster_v14_hd/run-correction-20260930/characters/09_bamboo_archer_girl/` | 1 | 0 | 0/128 |
| `qdao_original_roster_v14_hd/combat-20260929/characters/09_bamboo_archer_girl/` | 14 | 0 | 0/68 |

以上以本机目录递归枚举为准。run-correction 仅有 `HANDOFF.md`，没有 STATUS、review、manifest 或候选 PNG。combat 的 `delivery/status.json`、网络阻塞审计 manifest、实际文件一致：0候选、0选定、0导出、68缺槽。

旧成品入口 `qdao_original_roster_v14_hd/recovery-20260921/09-delivery-preview/final/runtime/` 实有 idle 8 PNG、walk 128 PNG。这些用于身份与朝向参考，不计作这次跑步修正或战斗成果；本审计没有把它们改名复用为新动作。

## 前次已做工作与失败证据

combat 的 `production/animation-plan.json` 与 `.md` 有完整68槽逐帧战斗设计，明确标记 `production_design_only`，不是68张成图。`provenance/attempts/hit-E-03-v1.request.json` 和 `prompts/hit-E-03-v1.txt` 保存了先前真正提交的单帧提示词及三张参考路径。路径属于历史机器，当前制作必须改用 TASK.md 指定的 D:/work/image 路径。

首个槽 `hit/E/03` 曾提交内置 image_gen 两次，`attempt-1.json` 与 `attempt-2.json` 都记录：`image generation failed: network error: error sending request`。第二次调用的 UTC 时间为 2026-09-30 19:27:20 至19:32:08，未返回图片、实际型号或质量。目标配置为 gpt-image-2.5-sunburst / max；实际型号与质量为 null，不能将目标当成已测返回值。

当前没有旧新动作图片可进行逐帧视觉复用或修正。延续先前工作意味着使用既有身份锁定、动作分解、关键帧顺序、提示词与来源结构来补出缺图，不是重新推翻已有方案。

## 可直接续用的动作安排

- 受击6帧：初受力、压缩、后仰峰值、回弹、恢复、警觉收势。左手稳弓、右臂护身；候选峰值03。
- 普攻12帧：右手取箭、搭弦、拉弦、松弦、回弹、收势。候选06满弦、07释放。
- 施法16帧：强化拉弓/引导、聚势、释放、收势。候选09满弦、10释放；法术光效另层。
- E/W独立绘制；解剖左手完整竹弓、右手取箭/拉弦、右肩箭筒。旧计划根点约E(600,940)、W(450,940)，仅属参考假设，须结合实际新图确认，不进行逐帧最低脚贴地。
- 正常时长：hit40ms/帧、attack30ms/帧、cast45ms/帧；事件帧均需成图后重新确认，未接入游戏。

`tools/export_bamboo_combat.py` 和 `tools/preview_bamboo.html` 已有显式选表、SHA来源绑定、整画布固定导出与正常/0.25倍慢放、逐帧、深浅底预览逻辑。历史记录只证明空选表拒绝和JS语法检查；没有真实68图全量导出测试。若沿用，须先复制/适配到当前独占角色目录，禁止执行旧目录写入口。

旧跑步交接只有总体方案：八方向各16帧、腿交替、肩肘协调摆臂、支撑/蹬地/腾空/落地、统一根锚点。没有本角色逐帧跑步图或通过记录。

## 审计边界

只读旧角色目录与对应交接；未生图，未修改旧文件，未操作Git。报告写入当前角色 `audit/`。本报告不替代新图视觉验收；客户端仍未接入、未运行验收。
