# 15 人战斗动作新窗口共同契约

本交接由用户在 2026-09-30 要求整理，供用户分别开新窗口续作。原授权是补齐 V14 当前保留 15 人的受击、普攻、施法；本轮只整理交接并恢复已成功返回的 00 cast/W/15 候选，没有重新生成图片。每个新窗口只负责其单角色交接指定的角色，无需重复询问已确定的名单和帧数。

## 工作范围与写入边界

- 仓库：`D:/luyuan/wuxingqitan/image`。
- 战斗批次：`D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929`。
- 保留 ID：00–10、14、15、17、20，共 15 人；不要恢复撤下角色，也不要混入新增 Q 版名单。
- 唯一角色范围来源：`D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/CONTINUATION_STATE_20260920_SCOPE_UPDATED.json` 的 `active_character_ids`。该文件的历史暂停状态、移动缺帧计数不是本次授权或当前库存。
- 每个窗口只写 `combat-20260929/characters/<完整角色ID>/`。允许在自己的角色目录内放提示词、候选、来源、选表、导出工具副本和验收；不要同时修改共享 tools、README、config、其他角色目录或客户端。
- 原移动、站立、肖像、designs 与恢复目录只读。不得把战斗 PNG 覆盖到原 137 张资源契约中。
- 开始前重新枚举本角色 staging/runtime/selection/receipts，记录哈希和缺槽；其他窗口可能已新增。00、01、14曾由另一个聊天制作，尤其先复核写入者和已有返回。不能在相同角色上同时开两个生产窗口。
- 不自动提交、推送、启动客户端或改客户端加载器。本次是图片和配套接入清单交付。

## 已确定的规格

| 动作 | E 每方向 | W 每方向 | 合计 | 正常速度 |
|---|---:|---:|---:|---|
| hit 受击 | 6 | 6 | 12 | 40ms/帧，240ms/段 |
| attack 普攻 | 12 | 12 | 24 | 30ms/帧，360ms/段 |
| cast 施法 | 16 | 16 | 32 | 45ms/帧，720ms/段 |

每人 68 张，整批 1020 槽。每槽是真实独立绘制姿态；E 朝屏幕右、W 朝屏幕左，分别生成，保持人物解剖左右、持手和非对称装饰。禁止镜像、复制、变形或插值补足帧数。不能用移动帧充当新的战斗姿态，也不能只改变透明区噪声就算一帧。

成品为单帧 **1024×1024 RGBA 透明 PNG**。单张原生图与导出尺寸分别记录，不能把多格小图放大称为原生高清。保持同角色全局比例、镜头、画布与地根；允许后仰、弯膝、身体转动等真正动作，不逐帧按包围盒缩放或居中。优先让生成图保持统一画布与站姿参考的根位置，再使用明确且稳定的整体等比导出变换。

我方/敌方站位、击退距离和方向、闪白、屏幕震动由代码处理；同朝向所有站位复用同一套动作。图片负责身体、表情、衣摆、武器及手势。跑近/回位不包含在普攻 360ms 内。法术弹道、光圈、粒子另做；角色已有身份道具/伴生物仍保留，例如14的小白狐和雪晶、17的两只墨灵，不能一律当作特效删除。

## 作图前读与实际参考输入

1. `D:/luyuan/wuxingqitan/image/AGENTS.md`。
2. `D:/luyuan/wuxingqitan/image/designs/README.md`。
3. `D:/luyuan/wuxingqitan/image/config/image-generation.json` 和 `D:/luyuan/wuxingqitan/image/docs/IMAGE_MODEL_POLICY.md`。
4. `D:/luyuan/wuxingqitan/image/README.md` 的接手说明，以及 `docs/WUXING_QITAN_HANDOFF.md`、`docs/QDAO_ART_DIRECTION.md`。
5. `D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/README.md` 的规格。其“尚无成功返回”状态行已过时，当前库存以本目录快照和新窗口实扫为准。

使用 imagegen 技能和内置 `image_gen`。先通过 view_image 实际打开本角色肖像、对应 E/W 姿态，以及已确认风格图 `D:/luyuan/wuxingqitan/image/designs/jubaozhai-ui/02-characters.png`。生成时把图片实际附作输入，并分别说明身份、动作衔接和风格用途。保持明亮干净、圆润饱满的道家 Q 版手绘，不能仅依靠绿金配色。

本批目标仍为配置中的 `gpt-image-2.5-sunburst / max`。2026-09-30 已重新打开官方模型页确认支持 max：<https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst>。内置入口没有 model/quality 选择器时继续使用宿主管理路径，不能把提示词或官方公告当作实际参数证据。不得自行切换付费 API/CLI，不要求用户为内置生图补 API Key。

每次成功或失败都保留文字证据。逐图必须记录 file、SHA256、时间及时间证据、原生尺寸、tool/route、当次配置快照、实际提交参数、实际返回型号/质量、提示词和参考路径/用途。未披露的型号/质量为 null，并写明未确认。恢复旧结果时不能按今天的配置重标历史型号。派生 PNG 记录 derivedFrom、原图哈希和 operation。

## 推荐制作与验收次序

1. 核对已有候选，先用真实姿态与来源选择可用稿；已有失败回执或只有提示词的槽不能计作有图。版本号较大不自动代表通过。
2. 缺整段时，先固定相应方向的受击峰值/普攻接触/施法释放关键姿态，然后补前后过渡。每帧描述与前后帧的具体差别，锁定持手、道具数量、头发、服装和脚根。
3. hit：01初受力、02压缩、03后仰峰值、04回弹、05恢复、06警觉收势。attack：01–03准备蓄力、04加速、05–06接触/峰值、07随动、08–10回收、11–12收势。cast：01–04起手、05–08聚气、09–10释放、11–13回收、14–16收势。此为动作设计起点，结合每人武器；已有00必须沿用现有真实选序，不机械重排。
4. 在角色目录保存六组显式 selection：action、direction、frame、file、generationRecord及SHA。一份源图只选到一个动作槽。未齐全的选择表标明 partial，不提交给要求完整序列的导出器。
5. 导出 runtime/hit/E/01.png 等标准路径，保留逐帧来源链。先在角色私有 preview 中审阅，PNG存在不自动等于已通过。
6. 检查 PNG 完整性、1024 RGBA/真透明、源与记录哈希、68槽齐全、无重复像素或镜像凑数、四肢/法器没有裁切或额外数量，清除结果须保留明确操作记录。需要重新绘制修边时使用 image_gen；不要用程序扭曲姿态。
7. 以正常速度和有明确倍率标识的慢放，检查六段连续动作及起止衔接、头身比例、根位置、脚滑、持手、武器长度、服装闪变、黑/白背景边缘。SHA不同不能证明动作不同；静态联系表不能代替连播。
8. 在角色目录写 delivery/README 或等效交付说明，列出68成品、选表、来源、技术验证、视觉验收、建议命中/释放帧（1-based）和正常播放时长。命中/释放帧必须按最终实图确定，不能声称已与游戏代码对齐。
9. 仅在最终成品落盘、引用完整且候选不再是唯一在制稿后，按AGENTS素材保留规则清理本角色拒稿/中间图；保留逐图文字来源。不要清理其他角色、其他聊天生成缓存或移动素材。

## 可复用工具及已知限制

- `combat-20260929/tools/register_output.py` 可复制内置返回结果并写逐图记录，拒绝覆盖。但它预设已知提交引用与返回结构；恢复旧图时必须按真实证据修正记录，不能补造参数。
- `combat-20260929/tools/audit_combat.py` 使用标准库检查 runtime 和来源，并生成离线预览。使用 `--characters <完整ID> --out <本角色目录内的唯一audit目录>`；不要使用共享默认 report 目录让15个窗口互相覆盖。缺帧退出码2是制作中状态，不代表工具坏了。
- `combat-20260929/tools/export_selected.py` 当前是00样板，参考固定为 attack-E-01、cast-W-01且页面标题偏00。其他角色先在自己的目录制作/适配导出入口，不在多个窗口同时改共享脚本。它的既有预览固定90ms/帧，是慢放，不能当作契约速度；新预览须用上表40/30/45ms或明确显示倍率。
- 已存在的 NumPy/Pillow Python：`C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。换机器应重新用 load_workspace_dependencies 定位；普通 python 在本次环境曾缺依赖。

结项分别报告：候选齐全、1024导出、技术检查、视觉连播、客户端接入、运行验收。没有做过的后两项明确写未接入/未测试，不以图片制作完成推定游戏已经可用。
