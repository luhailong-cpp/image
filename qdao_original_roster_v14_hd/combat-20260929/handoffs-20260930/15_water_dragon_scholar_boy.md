# 15 水龙书生：战斗动作独立新窗口交接

库存核对：2026-09-30 06:57 EDT。下面是用户已授权的续作任务；只负责 `15_water_dragon_scholar_boy`，完成后不自动接下一角色。

## 可直接复制给新窗口

```text
请在 D:\luyuan\wuxingqitan\image 继续完成 15_water_dragon_scholar_boy（水龙书生）的战斗图片。
先完整读取 D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/15_water_dragon_scholar_boy.md 和 D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/COMMON_CONTRACT.md，按当前磁盘重新核对库存后直接续作。
本角色每方向受击6帧、普通攻击12帧、施法16帧；E/W分别独立绘制，共68张1024×1024透明PNG。
保留已有候选和来源，不从头重做；不镜像、复制、扭曲或插值凑帧，不覆盖移动、站立、肖像。
只写 D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/15_water_dragon_scholar_boy 内的图片、提示词、来源、选表和预览验收文件。
做到本角色68帧选定、透明PNG导出、逐图来源齐全、六段按正常速度连播验收，并写明未做的客户端接入/运行验证。
```

## 当前库存与准确缺槽

已有 **0 张 staging PNG尝试稿**，覆盖 **0/68 个候选槽**；还有 **68 个槽没有候选**。标准 runtime 路径实际有 **0/68 张**。候选齐全、导出、视觉验收与客户端接入分别计算。

| 动作/方向 | 所需 | 已有候选槽 | 没有候选的帧号 |
|---|---:|---|---|
| hit/E | 6 | 无 | 01–06 |
| hit/W | 6 | 无 | 01–06 |
| attack/E | 12 | 无 | 01–12 |
| attack/W | 12 | 无 | 01–12 |
| cast/E | 16 | 无 | 01–16 |
| cast/W | 16 | 无 | 01–16 |

已有选表：
- 尚无完整显式选表；请核对候选后建立，不按最高版本号自动选稿。

## 必须实际附入生图的参考

- [身份肖像](<D:/luyuan/wuxingqitan/image/q_daoist_character_pack_4096/15_water_dragon_scholar_boy_transparent_4096.png>)（当前4096×4096，RGBA）。
- [E朝右身份/朝向参考](<D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/recovery-20260921/15-delivery-preview/runtime/idle/E.png>)（当前1024×1024，RGBA）。
- [W朝左身份/朝向参考](<D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/recovery-20260921/15-delivery-preview/runtime/idle/W.png>)（当前1024×1024，RGBA）。
- [已确认主要风格样板](<D:/luyuan/wuxingqitan/image/designs/jubaozhai-ui/02-characters.png>)（当前1932×814，RGB）。

参考尺寸不等于新成品尺寸；旧512仅作身份/朝向参考，不能放大充当新高清动作。实际view_image后再附图。

## 身份与持手锁定

藏蓝直发小马尾、青金发饰蓝穗、蓝眼、蓝象牙金书生袍、波云纹；右手展开的象牙白水龙扇、左手空闲、玉佩固定解剖左胯。

## 动作安排建议

受击扇手护胸、左臂配合平衡；普攻右手短促挥扇或前点后收回；施法左手起诀、右扇引导水法、释放、收势，不烘焙水龙/浪花。

上述为续作建议，不是声称已画出的动作。通用阶段与正常速度见COMMON_CONTRACT；命中和释放帧按最终实际选图记录，不能假称已经接入游戏。

## 本角色特别注意

移动旧素材SHA被客户端绑定，且仍有复核边界，严禁在本战斗任务中原地改移动runtime/验收。不要给角色增加其他法器。

## 产物位置及完成检查

- 候选：`D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/15_water_dragon_scholar_boy/staging/<action>-<E|W>-<两位帧号>-vN.png`。新增版本不覆盖现有版本。
- 提示词/来源：`D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/15_water_dragon_scholar_boy/prompts/` 与 `provenance/receipts/`，旧图旁generation.json也继续保留来源关系。
- 成品：`D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/15_water_dragon_scholar_boy/runtime/<hit|attack|cast>/<E|W>/<01起两位帧号>.png`。
- 六组明确选表、68槽来源链、透明与重复像素检查、六段正常/慢放和深浅底视觉验收、交付清单。
- hit正常40ms/帧，attack30ms/帧，cast45ms/帧；慢放必须显示倍率。
- 站位/击退由代码设置，不为每个站位复制一套图；本窗口不改客户端。

技术检查命令（只在自己的角色目录输出，不使用共享默认report）：

```powershell
Set-Location -LiteralPath 'D:\luyuan\wuxingqitan\image'
python qdao_original_roster_v14_hd/combat-20260929/tools/audit_combat.py --characters 15_water_dragon_scholar_boy --out qdao_original_roster_v14_hd/combat-20260929/characters/15_water_dragon_scholar_boy/audit-handoff --allow-incomplete
```

制作中allow-incomplete只改变退出码，不把缺帧或视觉问题变成通过。最终验收移除该参数，并阅读实际结果；来源/姿态/镜像/连播仍需另核。共享export_selected.py有00固定参考和90ms限制，先阅读共同契约再决定在本角色目录适配。
