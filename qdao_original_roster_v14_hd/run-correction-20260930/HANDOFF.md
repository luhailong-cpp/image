# 角色跑步与摆臂修正交接（2026-09-30）

## 接手目标与当前状态

用户原话：“所有角色的走路不对，不像跑步，手也没动”。随后要求生成交接细节，到新窗口继续做。

工作区：D:/luyuan/wuxingqitan/image  
关联客户端：D:/luyuan/wuxingqitan/mmorpg-client

本窗口已完成：读取项目规则、只读核查客户端资源与播放代码、查看原动作、定位旧步行/持物手约束、生成并保存 00 号 E 向四关键姿势研究稿及逐图来源记录。

尚未完成：任何角色的完整新跑步循环、八方向新跑步、全角色重绘、跑步专用导出锚点实现、动态美术验收、客户端替换与运行验收。没有提交或推送。用户现在要求交接，本窗口不再继续批量生成。

## 先读这些文件

1. D:/luyuan/wuxingqitan/image/AGENTS.md
2. D:/luyuan/wuxingqitan/image/designs/README.md
3. D:/luyuan/wuxingqitan/image/config/image-generation.json
4. D:/luyuan/wuxingqitan/image/docs/IMAGE_MODEL_POLICY.md
5. D:/luyuan/wuxingqitan/image/docs/WUXING_QITAN_HANDOFF.md
6. D:/luyuan/wuxingqitan/image/docs/QDAO_ART_DIRECTION.md
7. 本目录 README.md、client-audit.json
8. D:/luyuan/wuxingqitan/mmorpg-client/Docs/QdaoAllRosterPlaytest20260929.md
9. D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/recovery-20260921/COMPLETION_20260929.md

第 9 项是另一窗口的旧移动素材收尾记录，不是本次跑步已完成证明；其中“保持已验收动作”反映旧任务边界，不能用来否定用户本次修正反馈。旧模型、旧验收结论也不能自动套给新图。

## 名单：已核实与未决定

当前客户端新建角色使用这 15 名原人物：

| ID | 角色 | 当前客户端资源族 |
| --- | --- | --- |
| 00_reference_topright_boy | 金发带Q道童 | QdaoOriginalRosterV13 |
| 01_ice_sword_girl | 冰剑少女 | QdaoOriginalRosterV13 |
| 02_fire_talisman_boy | 火符少年 | QdaoOriginalRosterV13 |
| 03_lotus_healer_girl | 莲花医者 | QdaoOriginalRosterV13 |
| 04_mountain_guardian_boy | 山岳守卫 | QdaoOriginalRosterV14 |
| 05_celestial_musician_girl | 天音少女 | QdaoOriginalRosterV14 |
| 06_thunder_caster_boy | 雷法少年 | QdaoOriginalRosterV14 |
| 07_moon_shadow_assassin_girl | 月影少女 | QdaoOriginalRosterV14 |
| 08_alchemy_prodigy_boy | 炼丹童子 | QdaoOriginalRosterV14 |
| 09_bamboo_archer_girl | 竹弓少女 | QdaoOriginalRosterV14 |
| 10_crimson_spear_girl | 赤枪少女 | QdaoOriginalRosterV14 |
| 14_short_hair_snow_summoner_girl | 唤雪少女 | QdaoOriginalRosterV14 |
| 15_water_dragon_scholar_boy | 水龙书生 | QdaoOriginalRosterV14 |
| 17_ghost_script_calligrapher_boy | 灵篆书生 | QdaoOriginalRosterV14 |
| 20_star_formation_master_girl | 星阵少女 | QdaoOriginalRosterV14 |

通用目录还含 23–30 八名 QdaoRosterV12。没有恢复 11–13、16、18、19、21、22 的指令。

本窗口已询问“所有角色”是否指当前15名，用户尚未回答，转而要求交接。因此不能声称额外8名已被明确纳入整批。建议继续共同范围中的15名修正准备和00样板；是否额外包含23–30只需一次简短澄清，不必因此停止共同范围工作。不要要求用户重新授权已明确提出的跑步/摆臂修正。

真实客户端 PNG：
D:/luyuan/wuxingqitan/mmorpg-client/Assets/Resources/World/Characters/<资源族>/<完整ID>/walk/<N|NE|E|SE|S|SW|W|NW>/01.png…
原人物16帧；V12八帧。不能仅凭 image 仓库某个旧 candidate/recovery 路径判断实际游戏用图，先对照当前客户端与来源清单。

## 已确认的原因与证据边界

### 1. 旧出图要求是步行，并锁住持物手

00 号原提示词：
D:/luyuan/wuxingqitan/image/qdao_original_roster_v13/candidate/00_reference_topright_boy/source/walk-W-quarter50-v1/prompt.txt

第2行要求：
- Only the free RIGHT arm counter-swings.
- Do not move gourd.
- One planted supporting foot in every pose, no both-feet flight.

它会产生每帧着地的步行与固定持物手，和当前用户期望冲突。新提示词必须改变姿态要求；不能只复制旧模板再把 walk 改名 run。

本窗口直接打开：
- qdao_original_roster_v13/candidate/00_reference_topright_boy/review/E-contact.png
- qdao_original_roster_v13/candidate/00_reference_topright_boy/walk/E/01.png

可见空手在部分帧有摆动，所以不要声称双手逐像素永远相同；持物手和上身接近固定展示姿势，动作观感不够像跑步。子代理还初步观察到06法杖、14雪花、20星盘等持物姿势近似固定，但其最终审阅文件因连接中断未落盘，新窗口如需逐角色定论应重新查看原图。没有 art-audit.md，不要引用不存在的报告。

### 2. 旧逐帧贴地导出会抵消腾空

D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/tools/pipeline.py:71
记录 vertical=lowest_alpha_gt_8。

同目录 verify.py:68、:85，使用当前帧最低alpha像素计算偏移，并要求最低点 y=942。
V13 tools/pipeline.py:65 同类规则使用 y=471。

跑步应保留固定虚拟地面/角色根锚点与真实腾空高度；不能每帧把最低脚重新拖回地面，也不能按各帧包围盒缩放。先做独立的新跑步导出/验证路径，不直接改坏既有冻结walk验收。具体相位根点方案尚未实现。

### 3. 客户端不是独立骨骼摆臂

D:/luyuan/wuxingqitan/mmorpg-client/Assets/Scripts/World/QdaoBoySpriteAnimator.cs:
- 约119、654行：动画按 distance * Fps / 9 推进。
- 约635行：移动状态判定。
- 约687–693行：整张Sprite保持刚性，步态来自画好的PNG。

QdaoCharacterCatalog.cs、RoleFlowUi.cs 的准确行号与内容已保存 client-audit.json。原人物16帧×30ms，默认9 u/s下一圈480ms；V12八帧×60ms同样480ms。调快帧率不会补出缺失的手臂姿态。

已读取2,432张walk、184个方向组：无缺帧，组内无SHA完全重复。这里只排除了字节完全重复，未做解码像素判重，也不能证明姿势合理。没有启动Unity、没有观察用户实际运行现场，因此不能宣称运行播放绝对无其他问题。

## 已有新稿：仅姿势研究，不可直接接入

目录：
D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/run-correction-20260930/00-reference-run-E/

- run-keys-v1.png
- run-keys-v1.prompt.txt
- run-keys-v1.png.generation.json

目标是 E 向01/05/09/13四个关键姿势，近侧空手与远侧左手葫芦前后运动。它已显示比旧稿更明显的手臂位置交换，但不是完整循环；腿的交替、远近遮挡与循环接缝尚未通过动态检查。

原生1254×1254，2×2网格每格627×627；没有达到每帧原生1024的HD条件。禁止放大后宣称正式高清；完整生产应重新取得符合原生尺寸的每帧输入。不要拿四张关键姿势复制、镜像、插值凑16帧。

已验证PNG SHA：
1448fab8dfe60e6bfd49ac920982ee6aec36ec0513320876ad5eabfef65398d2

已检查RGBA头、角落/格间alpha=0，提示词和参考路径存在，JSON可解析，复制后SHA一致。未做全图边缘清洁或完整动画美术验收。

内置生成时实际附图：
- 原人物：qdao_original_roster_v13/candidate/00_reference_topright_boy/walk/E/01.png
- 主要画法参考：designs/jubaozhai-ui/02-characters.png

当前配置目标为gpt-image-2.5-sunburst / max。2026-09-30已再次查官方模型页，配置目标未变；内置工具不开放model/quality参数，实际返回也未披露，记录均为null。不要把官方公告、配置或提示词当作本次实际模型证明。继续每张候选和重试都记录来源。

## 建议接续顺序

1. 快速检查当前git状态及来源，保护并行工作；阅读本交接与已有图，不重复大范围扫目录。
2. 先将00号E向做成真正完整、可循环的16帧跑步样板，按30ms正常速度和慢速查看。研究稿可辅助姿态设计，但不能冒充已批准身份/尺寸/动画模板。
3. 以固定虚拟地面和根锚点导出，保留落地压低、蹬地、腾空和自然重心起伏。先证明它不会被旧最低脚贴地规则消掉。
4. 对00号完成剩余七方向，确认左右手、法器握法、远近腿和转向身份不翻转；再按名单扩展其他角色。可以并行分角色，确保一名角色同一写入者，公共清单由主窗口维护。
5. 每角色保留职业特色：徒手或单手持物可明显交替摆臂；双手持大物件应采用合理随躯干/肩肘运动的跑姿，不能为了大摆臂丢物、换手、漂浮或穿身。法器始终跟随真实握持点。
6. 在正常游戏大小与放大/慢速下检查：手臂反向协调、左右脚交替、支撑/腾空可辨、无滑步、无头身体积跳变、末帧接首帧自然、透明边缘干净。运动幅度不能只在放大静态对照时才看得出。
7. 保存新候选、来源、逐帧清单和验收证据，再整理给客户端主写者的准确文件/SHA/锚点交接。不要自动覆盖对方并行资源或把离线样板当引擎验收。
8. 分别报告：制作完成多少、视觉通过多少、正式导出多少、客户端接入多少、提交/推送是否完成。不同SHA、文件齐全、测试通过都不是动作观感通过。

现有原人物接口是八方向×16动作帧，8张独立idle。目标只修跑步相关内容；无必要不重绘idle/portrait，更不能误动正在制作的普攻、受击、施法。

## 风格、工具和并行边界

- 沿用designs已确认画法：清雅、圆润、明亮干净、道家Q版、玉绿/米白/暖金与克制点缀；保留每个人物原身份。生成时实际附上角色原图与接近用途的designs成图。
- 内置image_gen优先。用户没有选择单独计费API/CLI，不要因缺model选择器、路径或画质问题切换API或要求Key。
- 当前新跑步工作只在本目录新增；未修改旧候选、旧审核、原runtime或客户端。
- image仓库已有邮件UI改动、combat-20260929及recovery-20260921若干未提交工作；客户端有Catalog/RoleFlow等并行修改、07资源暂存。不要reset、clean、全量add、覆盖或混入本任务提交。
- 用户授权清理已废弃中间图，但必须先核实成品与当前引用。本次研究稿还是唯一新跑步在制稿，不应提前删；不做无关全库清理。
- 本轮没有新建聊天、发送其他聊天消息、启动Unity、提交或推送。新窗口请依据用户后续明确要求处理这些动作，不把交接文档当作额外授权。

## 工具小坑

默认python是C:/Users/Administrator/AppData/Local/Python/pythoncore-3.14-64/python.exe；本机默认环境未证实装有Pillow，py -0p也没有列出已注册版本。别重复假定py启动器能找到依赖。读取中文JSON/文本显式用encoding='utf-8'；本轮一次默认cp1252读取失败后已按UTF-8重验通过。图像编辑仍用内置生成工具，不用脚本伪造新的关节姿态。

## 新窗口第一条可直接粘贴

在 D:/luyuan/wuxingqitan/image 继续角色跑步与摆臂修正。先完整阅读 qdao_original_roster_v14_hd/run-correction-20260930/HANDOFF.md，并查看同目录的README、client-audit.json和00-reference-run-E样板。
我的要求是所有角色跑起来像真正跑步，手臂和持物手也要合理运动。当前已定位旧稿按步行制作、持物手固定，以及导出逐帧贴地的问题；仅生成了00号E向四关键姿势研究稿，尚未完成任何新16帧循环或客户端替换。
先推进当前15名保留原人物中的00完整跑步样板与导出验证，再扩展其余角色和八方向。资源库额外23–30八名是否纳入尚待澄清，不要恢复已移出的角色。沿用已确认designs风格，内置生图，逐图保留实际来源；保护并行战斗动作、邮件UI和客户端WIP。不要只提高帧率、复制帧或把现有研究稿放大后冒充正式HD，不要把离线素材完成说成游戏已接入。

