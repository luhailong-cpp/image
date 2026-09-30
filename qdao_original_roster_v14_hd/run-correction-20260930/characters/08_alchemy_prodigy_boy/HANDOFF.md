# 08 炼丹童子：独立窗口跑步与摆臂修正交接

你只负责角色 **08_alchemy_prodigy_boy（炼丹童子）**。用户要求每个角色一个窗口，本文件就是本窗口的任务边界。其他角色由其他窗口并行负责；你可以直接开始，不需要等待00样板或其他角色。

## 用户目标与未完成状态

用户反馈：“所有角色的走路不对，不像跑步，手也没动”。

把本角色的八方向移动重绘成可读的跑步：左右腿交替、支撑/蹬地/腾空/落地、自然重心起伏、手臂反向协调。持物手随肩肘运动，法器跟随真实握持点；双手持大物件时采用合理的整体跑姿，不能强行松手或左右换手。保留本角色的脸、发型、服装、体态、职业法器和已确认画法，不套用00道童的脸、葫芦或握法。

目前没有本角色已完成并验收的新16帧跑步循环。已有旧walk和历史“通过”不能代替本次用户反馈后的跑步验收。任务仅含跑步相关动作与配套导出、预览、来源、接入清单；无必要不重做idle/portrait，不碰普攻、施法、受击。

## 精确输入路径（只读）

- 工作区：D:/luyuan/wuxingqitan/image
- 当前游戏基线：D:/luyuan/wuxingqitan/mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV14/08_alchemy_prodigy_boy
- 现存image素材入口：D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/recovery-20260921/08-delivery-preview/revisions/final-v1/runtime
- 游戏动画：上述基线下walk/<方向>/01.png至16.png；八方向N、NE、E、SE、S、SW、W、NW。原人物当前30ms/帧、480ms/圈。
- 全局诊断：D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/run-correction-20260930/README.md、D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/run-correction-20260930/client-audit.json
- 总交接背景：D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/run-correction-20260930/HANDOFF.md；其中旧“先00再扩展所有人”顺序已由用户每角色一窗口的最新要求覆盖。
- 风格/生成规则：D:/luyuan/wuxingqitan/image/AGENTS.md、designs/README.md、config/image-generation.json、docs/IMAGE_MODEL_POLICY.md、docs/WUXING_QITAN_HANDOFF.md、docs/QDAO_ART_DIRECTION.md。

上述image素材入口已核实存在walk与idle，但未重新证明它们和当前客户端逐图一致。开工先核对本角色来源与当前游戏基线，不要把废弃候选当正在使用的资源。

## 唯一项目写入目录

D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/run-correction-20260930/characters/08_alchemy_prodigy_boy/

新图片、每次候选/重试提示词、逐图记录、临时缓存、私有脚本、切图、预览、验收和交接都放在这个目录内。推荐布局：
- generation/：新图、实际提示词、逐图来源；每次返回结果单独对应记录。
- tools/：本角色私有导出与核验逻辑，所有输出/缓存路径显式限定到本目录。
- candidate/walk/<方向>/01.png…16.png：待验收的本角色128帧。
- preview/：正常速度、慢速和逐帧检查入口。
- manifest.json、review.json、CLIENT_HANDOFF.md、STATUS.md：只描述本角色。
以上是输出规划，不是已经存在或已经完成的文件。宿主生成图可能先存到用户目录；选用稿必须复制进本角色目录并保存来源。

不得改其他角色、旧candidate/recovery、客户端、共享pipeline、全局索引/总清单、共享配置或Git暂存区。若公共配置需升级，记录官方证据交给统筹窗口统一处理，不在15个窗口同时改同一JSON。不要启动Unity、提交、推送或清理其他在制稿；这些不属于本角色制作交接。

## 已知关键问题

1. 旧00提示词明确要求持葫芦手固定、每帧至少一脚着地。它说明原流程按步行设计，但不证明本角色每帧双手绝对相同。本窗口必须实际查看本角色E/SE等方向，确认自己的肢体问题。
2. 旧V14导出pipeline.py:71的vertical=lowest_alpha_gt_8和verify.py:68/85把每帧最低alpha对齐y=942；V13同类为y=471。跑步要保留同一地面/根锚点及腾空偏移，不能每帧把最低脚拽回地面或按包围盒缩放。
3. 客户端播放整张PNG，没有独立手臂骨骼。只提高帧率不能补出缺失的摆臂。现有客户端库存齐全、方向内SHA不同只证明文件不同，不证明动作正确。
4. **不要直接运行旧pipeline/verify的写入入口。** V14 pipeline的review会调用preview并改共享preview-index.json/index.html，旧verify也会写回旧candidate/validation；V13同样。“不修改脚本文件”不等于执行无写入。若复用逻辑，做本角色私有副本并逐项限定输出，不让旧验证器强迫新跑步逐帧贴地。

## 执行顺序

1. 检查当前Git状态，读取上述规则；只抽查本角色实际基线，记录来源/时间/SHA。不要重复全库扫描。
2. 自主选择本角色易看清手脚的侧向，先画完整16帧跑步循环，完成正常480ms循环、慢速与逐帧查看，再完成其余方向。本角色独立推进，不等其他窗口。
3. 新原人物候选目标为1024×1024 RGBA、每帧真实原生输入至少1024、同角色统一比例与相机。当前512/混合尺寸旧版仅作基线。生成返回尺寸不达标就明确标研究稿并继续解决，不能放大冒充原生HD，也不能悄悄修改客户端规模/PPU。
4. 以固定虚拟地面/角色根点导出，保留真实腾空与重心运动；保持一致root/pivot定义并写入接入清单，不能直接复用旧最低脚贴地规则。
5. 八方向各16张真实独立姿态，完整两步跑循环。禁止复制/镜像/图像插值凑数；不要把关键帧研究稿当完整动画。单方向过关后仍须检查跨方向体型、持物手和非对称饰物。
6. 使用内置image_gen，实际附上本角色原图与designs内已确认的相近用途成图；不要只写路径当已传入参考。每个候选/重试分别保存目标配置、实际提交参数、实际返回、时间、SHA、尺寸、提示词、参考用途。宿主未披露模型或画质时写未确认/null；API/CLI不是本次默认授权。
7. 产出本角色独立动态预览、验收记录与准确的128帧清单。完成候选后写CLIENT_HANDOFF.md，供统筹/客户端主写者统一接入；本窗口不写客户端或公共总览。

## 动态验收与结束条件

逐方向在正常游戏显示大小、放大慢速和逐帧情况下检查：
- 手脚反相、左右腿明确交替；持物手和法器随合理关节运动，非固定展示姿势。
- 支撑压低、蹬地、短暂腾空、异侧落地可辨；没有一直蹬同一条腿、滑步、双脚漂浮或高抬腿踏步。
- 肩肘腕连贯，握持点稳定；没有手指/法器分离、换手、穿身或因遮挡反复跳变。
- 头身比例、服饰和光照一致；不逐帧忽大忽小，不把正常重心起伏当作必须抹掉的漂移。
- 第16帧接第1帧自然；每张真透明、轮廓完整、无杂色污染/残肢/截断。
- 来源、原生尺寸、导出根点和候选SHA可核验；文件数量和工具成功不自动等于美术通过。

完成后只报告本角色：128帧制作/视觉/导出分别完成多少，输出与预览绝对路径，未解决问题，接入文件与SHA。没有实际接入和运行证据就写“未接入客户端/未运行验收”，不要声明整个角色库已经完成。

