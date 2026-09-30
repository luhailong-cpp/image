# 00 金发带道童：战斗动作独立新窗口交接

库存核对：2026-09-30 06:57 EDT。下面是用户已授权的续作任务；只负责 `00_reference_topright_boy`，完成后不自动接下一角色。

## 可直接复制给新窗口

```text
请在 D:\luyuan\wuxingqitan\image 继续完成 00_reference_topright_boy（金发带道童）的战斗图片。
先完整读取 D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/00_reference_topright_boy.md 和 D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/COMMON_CONTRACT.md，按当前磁盘重新核对库存后直接续作。
本角色每方向受击6帧、普通攻击12帧、施法16帧；E/W分别独立绘制，共68张1024×1024透明PNG。
保留已有候选和来源，不从头重做；不镜像、复制、扭曲或插值凑帧，不覆盖移动、站立、肖像。
只写 D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy 内的图片、提示词、来源、选表和预览验收文件。
做到本角色68帧选定、透明PNG导出、逐图来源齐全、六段按正常速度连播验收，并写明未做的客户端接入/运行验证。
```

## 当前库存与准确缺槽

已有 **67 张 staging PNG尝试稿**，覆盖 **55/68 个候选槽**；还有 **13 个槽没有候选**。标准 runtime 路径实际有 **0/68 张**。候选齐全、导出、视觉验收与客户端接入分别计算。

| 动作/方向 | 所需 | 已有候选槽 | 没有候选的帧号 |
|---|---:|---|---|
| hit/E | 6 | 01–06 | 无 |
| hit/W | 6 | 01–06 | 无 |
| attack/E | 12 | 01–12 | 无 |
| attack/W | 12 | 无 | 01–12 |
| cast/E | 16 | 01–16 | 无 |
| cast/W | 16 | 01–15 | 16 |

已有选表：
- [hit-E-selection.json](<D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/hit-E-selection.json>)
- [hit-W-selection.json](<D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/hit-W-selection.json>)
- [attack-E-selection.json](<D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/staging/attack-E-selection.json>)

候选原图和SHA清单见本目录 `inventory-snapshot.json` 对应角色条目。`staging` 中重试稿不能重复计数；提示词及失败回执不计成图。

### 00续接要点

- hit/E 的真实顺序为01-v1、03-v3、02-v1、04-v1、05-v1、06-v1，保留既有选表。
- hit/W 的01实际使用hit-W-03-v1，之后02-v1、03-v2、04-v1、05-v1、06-v1；不要因没有hit-W-01文件误报缺槽。
- attack/E选04-v2和07-v2，其余v1。已选24槽的源图/记录SHA已核对一致。
- cast/E全部16槽已有候选但有多份重试；cast/W目前01–15有候选，10含重试，不能自动取最高版本；两方向最终选表仍需确认。
- cast/W/15已从前窗口completed工具结果原字节恢复；来源证据见本交接目录recovered-cast-W-15-tool-result.json及角色receipts/cast-W-15-v1.json。未新生图，实际模型/质量和未暴露提交参数仍记null。
- export-preview-20260930-v1只包含hit E/W及attack E的24张1024技术预览，不属于runtime成品；其固定90ms慢放不是契约速度。
- 静态序列复核点：hit/E最后一帧可能显得身体变高；hit/W 02/03后仰峰值顺序与03→04回弹偏急；attack/E09→10→11有头高上跳后回落风险。需按40/30ms连播再判定，必要时定向重画。
- 当前缺W普攻01–12与W施法16。先补缺，再统一选序、固定画布变换导出、六段验收。

## 必须实际附入生图的参考

- [身份肖像](<D:/luyuan/wuxingqitan/image/q_daoist_character_pack_4096/00_reference_topright_boy_transparent_4096.png>)（当前4096×4096，RGBA）。
- [E朝右身份/朝向参考](<D:/luyuan/wuxingqitan/image/qdao_original_roster_v13/candidate/00_reference_topright_boy/idle/E.png>)（当前512×512，RGBA）。
- [W朝左身份/朝向参考](<D:/luyuan/wuxingqitan/image/qdao_original_roster_v13/candidate/00_reference_topright_boy/idle/W.png>)（当前512×512，RGBA）。
- [已确认主要风格样板](<D:/luyuan/wuxingqitan/image/designs/jubaozhai-ui/02-characters.png>)（当前1932×814，RGB）。

参考尺寸不等于新成品尺寸；旧512仅作身份/朝向参考，不能放大充当新高清动作。实际view_image后再附图。

## 身份与持手锁定

短棕发、纯金发带、玉绿金边背心、米白衣裤、圆眼短身；解剖左手抱金色太极葫芦，右手出掌/施法。葫芦和发带结不能镜像换侧。

## 动作安排建议

普攻沿用既有 E 向右掌出手样板，在 W 重新绘制同一解剖持手的12帧；施法沿用既有聚气、释放、回收节奏，先补 W16。

上述为续作建议，不是声称已画出的动作。通用阶段与正常速度见COMMON_CONTRACT；命中和释放帧按最终实际选图记录，不能假称已经接入游戏。

## 本角色特别注意

00原聊天 01a0eba1-485d-7f81-aaca-4b4c48fdc021 在2026-09-30 06:23 EDT 查询为 interrupted/notLoaded；新窗口仍需复查是否已恢复。已有生成结果 W15 已恢复到 staging，不能再次按缺帧重画。

## 产物位置及完成检查

- 候选：`D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/staging/<action>-<E|W>-<两位帧号>-vN.png`。新增版本不覆盖现有版本。
- 提示词/来源：`D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/prompts/` 与 `provenance/receipts/`，旧图旁generation.json也继续保留来源关系。
- 成品：`D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/runtime/<hit|attack|cast>/<E|W>/<01起两位帧号>.png`。
- 六组明确选表、68槽来源链、透明与重复像素检查、六段正常/慢放和深浅底视觉验收、交付清单。
- hit正常40ms/帧，attack30ms/帧，cast45ms/帧；慢放必须显示倍率。
- 站位/击退由代码设置，不为每个站位复制一套图；本窗口不改客户端。

技术检查命令（只在自己的角色目录输出，不使用共享默认report）：

```powershell
Set-Location -LiteralPath 'D:\luyuan\wuxingqitan\image'
python qdao_original_roster_v14_hd/combat-20260929/tools/audit_combat.py --characters 00_reference_topright_boy --out qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/audit-handoff --allow-incomplete
```

制作中allow-incomplete只改变退出码，不把缺帧或视觉问题变成通过。最终验收移除该参数，并阅读实际结果；来源/姿态/镜像/连播仍需另核。共享export_selected.py有00固定参考和90ms限制，先阅读共同契约再决定在本角色目录适配。
