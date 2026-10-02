# 既有受击、普攻、施法实图核查

核查日期：2026-10-01。仅核查本机 `D:/work/image` 中已存在的内容，没有读取另一台电脑的未提交修改，没有生成、修改或删除图片。

用户已明确：沿用以前的制作方式；已有可用成果继续使用，只补缺口、修正存在的问题，无需把全部角色从头重画。

## 结论与计数口径

- 15 人目标均为 E/W 两个独立方向：受击 6 帧/方向、普攻 12 帧/方向、施法 16 帧/方向，每人 68 槽，共 1020 槽。
- 当前实际存在 85 张 `staging` 尝试 PNG，覆盖 67 个动作槽，其中水龙书生唯一一槽已有明确拒稿记录。因此可继续审阅的非拒稿候选覆盖至多 66 槽；候选存在不等于已通过视觉验收。
- 标准 `runtime/<hit|attack|cast>/<E|W>/<帧号>.png` 当前合计 **0/1020**。没有角色已完成 68 帧正式导出及六段连播验收。
- 下表每个动作按“E/W”列出实图覆盖槽数，重试版本不重复计槽。00 的 W 受击按既有选表计算，不能只按文件名误报缺第 1 帧。
- 00 另有 24 张 1024 技术预览帧以及 3 张联系表，全部由已有候选派生，不能计为新增姿态或 runtime 成品。
- 实际解码了本目录全部 112 张 PNG，全部可读取。85 张尝试稿均为 1254×1254 RGBA；24 张单帧预览为 1024×1024 RGBA。解码通过仅证明文件可读，不代表画法、姿态或连续性合格。

## 逐角色当前库存

| 角色 | 受击 E/W | 普攻 E/W | 施法 E/W | 尝试 PNG | 实图覆盖槽 | 当前可复用程度 |
|---|---:|---:|---:|---:|---:|---|
| 00 金发带道童 | 6/6 | 12/0 | 16/15 | 67 | 55/68 | 受击 E/W、普攻 E 已有明确选表，共 24 槽；全部仍待最终连播验收。施法候选需选序。 |
| 01 冰剑少女 | 3/0 | 0/0 | 0/0 | 3 | 3/68 | E 受击 01、03、06 在制候选，记录为 pending。 |
| 02 火符少年 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 有计划、提示词及失败记录，尚无实图。 |
| 03 莲花医者 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 有交接文件，本批次没有角色产图目录。 |
| 04 山岳守卫 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 有交接文件，本批次没有角色产图目录。 |
| 05 天音少女 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 已准备 68 帧提示词；交付状态为内置生图网络失败，非已完成。 |
| 06 雷法少年 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 交付状态明确候选、选定帧、runtime 均为 0。 |
| 07 月影少女 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 有制作准备，尚无实图。 |
| 08 炼丹童子 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 有制作准备，尚无实图。 |
| 09 竹弓少女 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 两次生成失败，交付状态明确成功生成 0。 |
| 10 赤枪少女 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 有制作准备，尚无实图。 |
| 14 唤雪少女 | 2/0 | 0/0 | 0/0 | 2 | 2/68 | E 受击 01-v1、03-v4，均标记 visual_provisional。 |
| 15 水龙书生 | 1/0 | 0/0 | 0/0 | 1 | 1/68 | E 受击 03-v1 明确拒稿：实际朝左，不可算可复用 E 候选。 |
| 17 灵篆书生 | 1/1 | 1/1 | 1/1 | 12 | 6/68 | 受击 03、普攻 06、施法 10 的 E/W 六个关键槽，有重试版本，尚待选定及验收。 |
| 20 星阵少女 | 0/0 | 0/0 | 0/0 | 0 | 0/68 | 有交接文件，本批次没有角色产图目录。 |

本次“可靠可复用”指可作为续作依据的已有图、选表与来源链，不表示任何段落已经最终验收。最成熟的是 00 已选定的 24 槽；01、14、17 的实图可以先复核后延续。15 当前唯一尝试稿不能作为正确的 E 方向帧。

## 00 的准确缺口与选序

- 缺 **W 普攻 01–12**、**W 施法 16**，共 13 槽。其余 55 槽已有候选，无需重新全部生成。
- E 受击既有选序：01-v1 → 03-v3 → 02-v1 → 04-v1 → 05-v1 → 06-v1。
- W 受击第 1 帧使用 `hit-W-03-v1.png`，之后为 02-v1、03-v2、04-v1、05-v1、06-v1；这是既有明确选序，并非复制凑帧。
- E 普攻选 04-v2、07-v2，其余为 v1。对应 04-v1、07-v1 有 needs_correction 记录，不应自动选用。
- E 受击 03-v2 方向错误，有 needs_correction 记录；已有 03-v3 替代候选。
- 施法两方向尚无最终完整选表，不应只按最大版本号自动选择。W15 已从旧工具完成结果恢复，不应重复当作缺图重画。
- 已有复核提示：E 受击末帧身体可能变高；W 受击 02/03 峰值顺序与 03→04 回弹偏急；E 普攻 09→10→11 头高可能跳动。需在正常速度下观察后决定是否定向修正。
- `export-preview-20260930-v1` 只有受击 E/W 和普攻 E 的 24 张派生技术预览；既有固定 90ms 播放为慢放，不是契约正常速度。

## 按以前方式接续

1. 每角色独立制作，先查看身份、朝向、已确认风格图及已有候选，保留可用姿态与来源关系。
2. 对已经有图的动作槽先审阅，再补缺图与有明确问题的帧；不得将提示词、失败回执或重试版本计为完成帧。
3. E/W 独立绘制，保持解剖左右、持手和非对称装饰，不镜像、复制、变形或插值凑帧。角色画法继续沿用已确认道家 Q 版风格。
4. 每帧记录配置目标、实际提交参数、实际返回信息和来源。旧图记录保持原样；不能因本次指定 GPT Image 2.5 而回写旧图的实际模型或质量。工具未披露的实际型号、质量继续标记未确认。
5. 选图后采用角色统一画布、比例与脚根规则导出 1024×1024 透明 PNG，避免逐帧包围盒居中或缩放导致身体大小跳动。
6. 六段正常播放分别为受击 40ms/帧、普攻 30ms/帧、施法 45ms/帧。完成正常速度与标注倍率的慢放审阅后，才记录通过；图片存在、技术检查或预览页面存在均不等于完成。
7. 当前审计没有验证客户端接入或游戏运行；不得把候选、预览或正式导出与客户端验收混为一项。

本文件只统计战斗动作，跑步手脚问题需使用对应移动动作库存与审查结果另行接续。

## 来源与证据

本机批次根目录：[combat-20260929](D:/work/image/qdao_original_roster_v14_hd/combat-20260929)。旧文档中的 `D:/luyuan/wuxingqitan/image` 是旧机器位置，本次实际核查位置均为 `D:/work/image`。

- [共同制作契约](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/COMMON_CONTRACT.md)：动作数量、方向、尺寸、播放速度、来源与验收约定。
- [9 月 30 日交接索引](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/INDEX.md)及[当时库存快照](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/inventory-snapshot.json)：旧快照为 59 槽，后续 14、15、17 新实图使其已过时。本表以当前磁盘为准。
- [00 角色交接](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/handoffs-20260930/00_reference_topright_boy.md)、[E 受击选表](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/hit-E-selection.json)、[W 受击选表](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/hit-W-selection.json)、[E 普攻选表](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/staging/attack-E-selection.json)。
- [00 技术预览报告](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/export-preview-20260930-v1/technical-report.json)：24 张派生预览，不是 runtime 成品。
- [05 交付状态](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/05_celestial_musician_girl/delivery/state.json)、[06 交付状态](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/06_thunder_caster_boy/delivery/STATUS.json)、[09 交付状态](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/09_bamboo_archer_girl/delivery/status.json)：失败与准备状态不计成图。
- [14 第二张候选回执](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/14_short_hair_snow_summoner_girl/provenance/receipts/hit-E-03-v4.json)：visual_provisional。
- [15 唯一实图回执](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/15_water_dragon_scholar_boy/provenance/receipts/hit-E-03-v1.json)：rejected_wrong_facing_left_not_E。
- [17 实图目录](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/17_ghost_script_calligrapher_boy/staging)及[对应回执](D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/17_ghost_script_calligrapher_boy/provenance/receipts)：12 张尝试稿仅覆盖 6 个关键槽。

85 张尝试稿中，73 张有对应完整逐图 JSON，73 张记录中的 SHA-256 均与当前 PNG 实算一致。余下 12 张为 00 的 W 施法 01–09、11–13：有成功工具回执，缺对应完整逐图记录，最终交付前应据既有证据补齐记录；这不是缺图，不能据此重画或伪填未披露的模型信息。
