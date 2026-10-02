# 既有跑步制作核对与接续依据

核对日期：2026-10-01。只读核对对象为 `../run-correction-20260930/`，不包含本轮 `action-remake-20261001` 新图，也不包含战斗动作。本文保存已经完成的核对结果，没有为此扩展扫描或改动旧稿。

用户已澄清：沿用之前的制作方式，之前已经做过的内容继续做。**已有稿先复核、选用、补齐和修正；完整方向尚未验收，不等于制作进度为零。** 本地现存旧跑步稿已在仓库中保存，不能把它们误称为另一台电脑尚未提交、当前拿不到的稿件；本次不依赖另一台电脑未提交的内容。

## 计数定义与范围

- 原生单帧尝试：实际存在的 `characters/<id>/generation/<方向>/<帧号>-v<版本>.png`。相同动作槽的多个版本分别计为尝试；本次57张均实际核对PNG头为1254×1254，并均有相邻逐图来源JSON。
- 相位槽：方向与帧号组合去重，不按版本重复计数。现有57次单帧尝试覆盖42个E向相位槽，其中包含未审稿与明确拒稿，不能推定42槽均可用。
- 候选槽：实际存在的 `candidate/walk/<方向>/01.png` 至 `16.png`。每角色目标八方向×16帧=128槽；现有21张1024候选只是技术导出，不能推定已经美术通过。
- 候选缺槽：128减去实际候选文件数。已有原生稿但尚未选图导出的槽仍计为候选缺槽；不能据此重画所有缺槽。
- 研究母表及切格：用于动作探索，不计入原生HD单帧槽。01的十六格研究图分格尺寸不足1024，不得把16张切格当成完整高清循环。
- 验收结论：读取现存review、manifest、独立审阅记录和逐图记录。本次没有新增动态验收，不把文件数、SHA、PNG尺寸或播放器可切帧当成美术通过。

旧跑步目录共有101张PNG：57张独立原生单帧尝试、21张候选导出、2张研究母表、16张研究切格、5张预览图。两张母表分别为根目录00四关键姿势研究稿与01十六格研究稿。15个角色子目录合计100张；根目录00研究母表另占1张。

未找到任何已通过完整新跑步循环动态验收并完成正式交付的方向。已有候选和制作资料应保留并继续复核，不能因此把制作量写成零。所有已找到的新单帧都在E方向，其余七方向尚无新单帧稿。

## 逐角色实际库存

本表只描述旧“跑步修正”批，不代表相应角色没有更早的移动成品或战斗图。原生尝试包含重试与拒稿；候选数量不代表通过数量。

| 完整ID／角色 | 原生单帧尝试 | 已有E向相位槽 | 候选槽／128 | 候选缺槽 |
|---|---:|---|---:|---:|
| 00_reference_topright_boy 金发带Q道童 | 4 | 01、09 | 1 | 127 |
| 01_ice_sword_girl 冰剑少女 | 7 | 01、03、05、09、11、13 | 6 | 122 |
| 02_fire_talisman_boy 火符少年 | 5 | 01、02、03、04、08 | 3 | 125 |
| 03_lotus_healer_girl 莲花医者 | 8 | 01、05、09 | 0 | 128 |
| 04_mountain_guardian_boy 山岳守卫 | 0 | 无 | 0 | 128 |
| 05_celestial_musician_girl 天音少女 | 6 | 01、02、03、05、09、13 | 0 | 128 |
| 06_thunder_caster_boy 雷法少年 | 0 | 无 | 0 | 128 |
| 07_moon_shadow_assassin_girl 月影少女 | 23 | 01–16全部已有生成稿 | 8 | 120 |
| 08_alchemy_prodigy_boy 炼丹童子 | 0 | 无 | 0 | 128 |
| 09_bamboo_archer_girl 竹弓少女 | 0 | 无 | 0 | 128 |
| 10_crimson_spear_girl 赤枪少女 | 0 | 无 | 0 | 128 |
| 14_short_hair_snow_summoner_girl 唤雪少女 | 0 | 无 | 0 | 128 |
| 15_water_dragon_scholar_boy 水龙书生 | 4 | 01、02、07、10 | 3 | 125 |
| 17_ghost_script_calligrapher_boy 灵篆书生 | 0 | 无 | 0 | 128 |
| 20_star_formation_master_girl 星阵少女 | 0 | 无 | 0 | 128 |
| 合计 | 57 | 42个不同相位槽 | 21／1920 | 1899 |

## 已做内容如何接续

### 00 金发带Q道童

`generation/E/01-v4.png` 已用于固定画布校准，候选槽为E01；它仍待完整方向复核。`01-v1.png`记录为多余手部端点，`01-v3.png`双臂链条不合理，`09-v1.png`葫芦穗颜色及头部比例不一致，均明确拒收，不得选作正式帧。01-v2只有网络失败记录，不算图。

先复核01-v4的双臂、葫芦持手和比例，再据此修E09异侧落地；不要重新把所有已做尝试当成从未生成。

证据：[review.json](../run-correction-20260930/characters/00_reference_topright_boy/review.json)、[candidate-inventory.json](../run-correction-20260930/characters/00_reference_topright_boy/candidate-inventory.json)。

### 01 冰剑少女

候选E01、03、05、09、11、13均已存在，另有09-v2原生修稿。后续review明确全套尚未通过：09-v1和11-v1存在道具换手，05与13未建立反向腿相位，09-v2虽改善近侧剑臂，仍有比例与相位问题。十六格研究稿也未通过，不能用于补齐HD槽。

先看review和现有图，保留已得到的身份、反向摆臂诊断与来源记录；优先修异侧相位和稳定比例。不要把旧candidate中已被后续review否定的帧直接接入。

证据：[review.json](../run-correction-20260930/characters/01_ice_sword_girl/review.json)、[manifest.json](../run-correction-20260930/characters/01_ice_sword_girl/manifest.json)。

### 02 火符少年

候选为E01、02、04。01、02仅有“持手正确”的局部静态检查，不能推定完整步态通过。E03-v1明确因道具换手而拒收；E08-v1已落盘，但尚未进入候选清单。

先复核已有01、02、04与新返回08，修03近侧右臂／远侧左臂链条，再续完整E圈。技术validation中的无问题只指几何、alpha和SHA检查。

证据：[review.json](../run-correction-20260930/characters/02_fire_talisman_boy/review.json)、[manifest.json](../run-correction-20260930/characters/02_fire_talisman_boy/manifest.json)、[validation.json](../run-correction-20260930/characters/02_fire_talisman_boy/validation.json)。

### 03 莲花医者

E01有三次稿，E05有两次稿，E09有三次稿。生产契约把`generation/E/01-v3.png`作为E向基准，但未授予动态验收。E05独立审阅优先推荐`05-v1.png`作为姿势候选，指出`05-v2.png`地面注册更差；01-v1明确拒收。E09-v4和E13-v1只有job／提示词，不能计成已生成。

优先沿01-v3与05-v1复核比例、左右手和脚相位，检查已有09三稿，再补连续相位。保持右手莲灯、左手玉瓶和解剖左侧花饰；契约已指出旧E基线的持手／饰品深度有误，不能盲目复刻。

证据：[PRODUCTION_CONTRACT.md](../run-correction-20260930/characters/03_lotus_healer_girl/PRODUCTION_CONTRACT.md)、[05-REVIEW.md](../run-correction-20260930/characters/03_lotus_healer_girl/generation/E/05-REVIEW.md)、[原生稿与逐图记录](../run-correction-20260930/characters/03_lotus_healer_girl/generation/E)。

### 05 天音少女

六张原生稿E01、02、03、05、09、13均已存在，逐图记录状态为`pending_visual_review`。旧STATUS仍说尚无完成新帧，已落后于实际PNG与逐图来源，不能继续照抄。

先审六张现有稿的双手抱琴、琴体刚性、肩肘随动与左右腿交替，再选择可用稿并补其余相位；不能因为没有candidate导出就全量重画。

证据：[原生稿与逐图记录](../run-correction-20260930/characters/05_celestial_musician_girl/generation/E)、[run-plan.json](../run-correction-20260930/characters/05_celestial_musician_girl/run-plan.json)。

### 07 月影少女

E01–16全部有原生生成稿，合计23次尝试；当前预览选择E01、02、06、10、13、14、15、16共8帧。`01-v3.png`和`06-v3.png`被记录为可用于预览，不等于正式通过。review明确拒收01-v2、06-v2、11-v1，并指出04-v2需要修正；后续其他版本须结合实际图继续核对。

这是最接近完整E向圈的角色。**先复核16个已有相位并选图、补修，避免把已有整圈生成工作全部重做。** 8张预览候选与剩余已有原生稿之间仍有选择和修正工作；完整动态观察未完成。

证据：[generation/selection.json](../run-correction-20260930/characters/07_moon_shadow_assassin_girl/generation/selection.json)、[review.json](../run-correction-20260930/characters/07_moon_shadow_assassin_girl/review.json)、[manifest.json](../run-correction-20260930/characters/07_moon_shadow_assassin_girl/manifest.json)、[CLIENT_HANDOFF.md](../run-correction-20260930/characters/07_moon_shadow_assassin_girl/CLIENT_HANDOFF.md)。

### 15 水龙书生

E01、02、07已经导出候选；E10-v1已生成但未选入候选。四张逐图记录均注明待静态与动态复核，manifest为视觉通过0、方向通过0。

先审这四张与固定画布变换，保留合格候选并补其余E相位。旧STATUS只写E01，不能用它覆盖后续实际库存。

证据：[manifest.json](../run-correction-20260930/characters/15_water_dragon_scholar_boy/manifest.json)、[原生稿与逐图记录](../run-correction-20260930/characters/15_water_dragon_scholar_boy/generation/E)。

### 其余八名

04、06、08、09、10、14、17、20的旧跑步角色目录未发现新PNG，已有的是交接／规划资料。可沿旧角色身份成品和已有制作规范开展自己的E向样板；不能据此推断其旧移动资产或战斗资产也为空。

## 本轮接续方法

1. 各角色保持独立写入目录，先读取本角色既有review、选择清单、实际PNG和逐图来源。旧文档里“尚无图”的文字与实际库存冲突时，以实际文件及后续记录为准，并明确区别生成、候选、验收与正式交付。
2. 已有稿先复核续做。通过当前复核后才作为本轮参考或选用帧；明确拒稿仅保留诊断／来源价值，不选作正式成品。未审稿也不自动废弃。
3. 沿用已有单帧内置生成、真实解剖左右手、固定画布／根点、统一导出变换、来源记录与正常／慢速循环审阅的方法。禁止复制、镜像、插值凑帧，禁止逐帧最低脚贴地消掉腾空。
4. 先完成各自E向16帧并验证异侧相位与16接01，再制作其余七方向。15个窗口各自独立推进，无需串行等待00；07可优先利用已有整圈原生稿进行选图和复核。
5. 本轮新图与选用结果写到`action-remake-20261001/characters/<id>/`，记录旧稿来源及选择依据；旧目录保持只读，避免覆盖既有来源链和另一机器后续合并内容。成品确认落盘、引用完整后，素材清理仍遵循项目AGENTS规则，不能提前删除唯一在制稿。
6. 本机未找到`D:/work/mmorpg-client`。这不阻塞素材续做，但不能声称已接入或已运行游戏验收。

本次审计仅保存事实与接续建议，没有生成新图片、选定新的美术通过状态、修改旧稿或执行客户端操作。
