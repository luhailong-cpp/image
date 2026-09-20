# 保留15名原版角色动画｜暂停交接（2026-09-20范围更新）

**当前状态：用户要求暂停，剩余任务以后继续。全部任务未完成，正式接入仍为4/15（00–03）。**

最新用户原话：“这样吧 剩下的东西你写个交接文档，我们以后再继续做”。本文件是下一窗口第一入口；第0节2026-09-20范围更新优先于所有旧23名目标，其他暂停和验证边界沿用。停止新增绘图；已发出的调用只归档，已启动处理收尾。未创建定时任务或后台续画。

## 0. 2026-09-20最新角色范围（优先于全部历史23名清单）

用户已在 `E:/work/image/q_daoist_character_pack_4096` 删除部分角色，并要求交接同步。当前只保留 **15名：00–10、14、15、17、20**，原ID不重排。当前范围和精确缺槽以 [2026-09-20范围库存](CONTINUATION_STATE_20260920_SCOPE_UPDATED.json) 的 `active_character_ids` 为准。

**移出后续制作/发布范围的8名：** 11玉拳少年、12铁刀少年、13风刃少女、16金铃舞者、18沙海日轮少女、19御兽少年、21厨道童子、22执刀小侍。不要给这些角色补帧，不要从baseline、旧提交或旧参考目录自动恢复已删除肖像；它们不再计入缺帧或完成率。旧00别名PNG的删除不另算一名角色。

V13/V14的历史 `inventory.json`、2026-09-19暂停JSON和旧验收证据仍保留原23名，作为历史身份/来源记录，不再单独决定当前工作范围。恢复时所有批量补帧、完整性统计和发布计划必须先与当前15名白名单取交集；仍硬编码23名的工具/运行时注册表需先检查适配，不能用旧“缺文件”检查恢复用户删除。本次没有修改运行时注册表或发布器，不代表相关代码已适配。

本次仅同步范围与文档，角色绘制继续保持暂停；没有额外删除历史候选/证据或改正式客户端。04–06的6张已生成未导入原图仍全部保留在当前范围内。

## 1. 用户目标和仍有效的授权

原始身份来源：提交 `9adcf9291e4a867601868889a5965f3cd48630ba` 中原版00–22共23名；当前只执行上方保留15名。每名8方向×16真实行走帧，另8独立idle；30ms/帧、480ms/周期，原移动速度9、原肖像身份不改，最后真实Unity验证并接入正式客户端。

最新绘图授权明确为：“允许用当前内置入口继续，不要求确认2.5”。将来用户恢复时可沿用，不必重新问型号确认；**仅当前内置工具获准，收费API/CLI未获授权**。如实记录host-managed/unverified，不能把配置、提示词或公告当本次型号证据。

旧图保留，00–03不重做/不重封存。04–06旧512帧不重画、不放大冒充高清；新缺帧原生完整cell两边≥1024，再输出1024。禁止复制、镜像、插值、扭曲或平移同姿势凑16帧。没有原图需要用户重传。

暂停后先等用户明确恢复，不能把本交接当继续执行的指令。

## 2. 路径与第一批必读文件

- 工作目录：`E:/work`。
- 素材：`E:/work/image`；本包：`E:/work/image/qdao_original_roster_v14_hd`。
- 正式客户端：`E:/work/mmorpg-client`。
- **唯一隔离验证工程**：`E:/work/tmp/qdao-original-live-candidate-20260917`；不要重建或用旧verify工程替换。
- 历史身份/来源清单（须按第0节当前白名单过滤）：`../qdao_original_roster_v13/inventory.json`，用character_id字段，不能误用带transparent_4096后缀的source_id；旧character_move_8dir是00的别名，不是第24名。
- 本次逐角色、逐方向缺槽：[当前15名库存JSON](CONTINUATION_STATE_20260920_SCOPE_UPDATED.json)。数字是文件库存，不是视觉合格数；不把孤立raw、strip、pilot或拒稿算完成。
- 先读适用`AGENTS.md`、`image/config/image-generation.json`、`image/docs/IMAGE_MODEL_POLICY.md`及generate2dsprite/imagegen技能。上次已授权host-managed，不要重新陷入2.5前置确认。
- [上一完整历史交接](HANDOFF_FOR_NEW_WINDOW_20260918.md)保存原合同和旧Unity证据；过时部分按本文件修正。

## 3. 当前15名库存（2026-09-20重新核对文件存在性）

| 角色 | 旧V13行走+idle | 已导入新增HD行走 | 合并已有行走+idle | 尚缺行走 |
|---|---:|---:|---:|---:|
| 00–03 | 各128+8 | 不重做 | 各128+8，已正式 | 0 |
| 04 山岳守卫 | 104+8 | 14 | 118+8 | 10 |
| 05 天音少女 | 52+8 | 12 | 64+8 | 64 |
| 06 雷法少年 | 16+8 | 5 | 21+8 | 107 |
| 07–10、14、15、17、20（8名） | 0 | 0 | 0 | 各128，另各缺8idle |

按上述已导入候选，仍缺 **1205walk+64idle=1269个动作槽**。有待修或未完整审核的候选可能还需返工。这不是“再画1269张就一定验收”的承诺。

正式仍只有V13 00–03；本轮无新mixed assembly、审批、stage或正式资源发布，未启动Unity。

### 04 山岳守卫

- V14已有SW补帧02/03/04/06/07/08/10/11/12（9）；本轮新导入NW02-v2、03、04、06、07（5）。候选E01是旧HD pilot，对已有V13槽不能计新增或替换旧图。
- SW缺14/15/16；NW缺08/10/11/12/14/15/16，共10。
- 用户停止时在途NW08/10/11只归档raw/prompt/receipt，不计已导入。
- NW04/06/07处理后有亮紫红细残边疑点，未封存；需在深浅背景放大复查/修复，不能仅依数字过关。
- 旧NW02-single-v1因脚底露出过多拒收，用v2，不复活旧拒稿。
- 3张旧SW孤立raw缺可核对prompt/receipt/帧映射，不能凭外观认定SW14–16；保留不计数，后续如无法恢复证据再重画。
- 详细：[04完整交接](generation-current-builtin/04_mountain_guardian_boy/HANDOFF_20260919.md)，同目录HANDOFF_STATE_20260919.json；8次本轮内置调用全部收尾。

### 05 天音少女

- NE新增02/03/04/06/07/08/10/11/12/14/15/16全部导入。结合V13 NE01/05/09/13，**NE库存16帧齐全但未连播验收**。
- SE/SW/W/NW各16walk缺失；N/E/S旧完整，8旧idle保留。
- 旧NE02/03/04/06的精确请求/回执从归档日志恢复，新建recovered-bound批次重新导入同raw，旧source批次保留。NE07断线原图真实output_hint成功找回并导入，没有重复生成。
- 本轮真正新画NE08/10/11/12/14/15/16（7）；所有新raw1254原生，1024输出，.84固定scale，purple-preserve50/75。
- 暂停收尾12帧文件绑定全过；新的12帧独立像素重建、完整16帧混合连播、边缘和接缝检查待做。
- [05完整交接](candidate/05_celestial_musician_girl/HANDOFF_20260919_PAUSED.md)及其review/PAUSE_FILE_BINDINGS_20260919.json。

### 06 雷法少年

- 原S方向16帧及8idle不动。E01/02/03/05/09已导入5张；E09用第二稿。
- E04/06/13只有已归档真实原图，下一步切图/核对，不计已导入。
- E09第一稿没有交换领先腿，明确拒收；E03处理后疑有细紫边，未视觉批准。
- E其余缺04/06/07/08/10/11/12/13/14/15/16，共11；另N/NE/SE/SW/W/NW共96，总缺107。
- 详细：[06完整交接](generation/06_thunder_caster_boy/PAUSED_HANDOFF_20260919.md)，同目录inventory-at-pause-20260919.json；本轮原生1254，固定scale .88。5张独立重建已通过，全部调用和命令已收尾。

## 4. 本次工具与代码增量

### 混合预览

新增`tools/serve_mixed_preview.py`、`tools/mixed-preview.html`及[使用说明](tools/MIXED_PREVIEW.md)。按相同世界几何显示旧512/52PPU与新1024/104PPU，读取真实PNG并复核SHA；八方向、16×30ms、独立idle、正常/放大、关键帧和15/16/01接缝均可检查。输出审核草稿始终pending，不自动批准。

实际Edge检查通过，见`mixed-preparation/recovery-20260919/preview-browser-qa.json`。使用的是复制既有PNG的工具QA夹具，**不是新角色美术验收**。临时服务/夹具已清理。旧全HD预览未改，不能直接用其固定1024读取方式评审混合帧；共享preview-index可能尚未反映最新帧，恢复时统一刷新。

### 首次04发布门禁修复

真实正式/隔离各3451旧角色文件，其中637个.meta因独立GUID/Unity导入信息不同。旧publisher要求跨工程旧全集SHA相同，会错误拒绝首次04。

`publish_mixed_roster.py`现分别保护正式历史基线和隔离stage基线，跨工程只比较作者资源；各自.meta仍按各自基线完整防篡改，没有覆盖旧meta。16/16小型针对性测试通过。见[修复报告](mixed-preparation/recovery-20260919/PUBLISHER_META_FIX.md)。

未用真实新资产运行发布；大fixture全套未重跑，不能称真实发布通过。**仍只支持首次04**；05/06顺序发布需前序V14/index及多混合角色runtime证据链，不可仅放开ID。正式后续若自行导入改变旧meta，固定历史基线会拒收，不能临时生成新基线绕过。

### 隔离工程两份测试已改，正式未同步

详见[最终测试交接](mixed-preparation/recovery-20260919/WALK_CAPTURE_FINAL_HANDOFF.md)和同目录`WALK_CAPTURE_HANDOFF_STATE.json`（准确路径、SHA、备份、输出）。

隔离`Assets/Tests/PlayMode/`：
- `QdaoRosterAnimatorPlayModeTests.cs`：逐帧使用GeometryForResource断言混合尺寸/PPU，原固定1024断言对旧512会失败。
- `QdaoRosterSandboxPlayModeTests.cs`：增加真实控制器Run状态下SW02/NW02的新1024走帧捕获，每帧正常ortho27/最近ortho5两视图，同simulationFrame，真实移动和来源绑定；保留原idle截图。

仅离线C#编译exit0，**尚未跑Unity验证路线/时序/相机裁切或得到四张真实走帧截图**。正式两份仍旧字节，导致50源码绑定目前不一致；后续须审核、真实验证并有记录地同步，旧XML/快照不能当新通过。生产逻辑和相机配置未改。备份位于`mixed-preparation/recovery-20260919/walk-capture-before/`；编译产物不得拷入Unity。

新增`tools/verify_mixed_walk_captures.py`和测试：10/10小型绑定测试+4/4复用PNG/投影测试通过。校验器未对真实新run执行，且尚未接入publisher硬门禁；输出只是bound_evidence_requires_visual_review，不能替代实际目视。旧publisher仍检查idle截图，不能据此声称新HD行走近景通过。

## 5. 后续恢复执行顺序

1. 用户明确恢复后，先读本交接、实际库存JSON、三个角色停止记录和测试最终交接。核对当前文件，避免其他窗口工作/后续提交造成变化；不要自动回滚任何文件。
2. 04优先：处理NW残边问题，检视在途归档NW08/10/11，再补其余缺帧及SW14–16。05先独立重建并连播已齐NE；06先处理已有3张未导入原图。按角色隔离写，公共管线/Unity独占。
3. 完整角色原始source独立重建→新的不可覆盖mixed assembly→实际8方向/正常/放大/接缝/1080p视觉审核→新鲜SHA绑定审批。不能把incomplete候选强行发包。
4. 用唯一隔离工程stage完整已批角色；先完成Unity导入/meta/index生成并关闭，再建新run的Edit输入快照，真实Edit，Play输入快照，真实Play和截图，post全输入比较。每次源码或素材变化必须新run。
5. 实际SW02/NW02四张PNG经独立来源/尺寸/移动/投影校验后逐张目视，诚实记录最近镜头顶部裁切。原相机ortho27/5、速度9不偷改。离线预览和旧idle图不能替代。
6. 审查并完成正式/隔离两份测试源同步与50绑定，完成publisher dry-run/execute及旧资源独立保护审计。现成工具具体命令见下方清单，参数先读--help，不猜。
7. 再完善05/06顺序发布支持，并继续07–10、14、15、17、20。当前保留的全部15名正式接入且真实验收完成才可说“全部做完”。

## 6. 关键证据和工具入口

- [独立盘点与命令清单](mixed-preparation/recovery-20260919/PIPELINE_RECOVERY_AUDIT.md)
- [走帧截图入口/新run命令](mixed-preparation/recovery-20260919/WALK_CAPTURE_ENTRY_AUDIT.md)
- [混合装配说明](tools/ASSEMBLE_MIXED_ROSTER.md)
- [混合审核/stage说明](tools/APPROVE_STAGE_MIXED_ROSTER.md)
- [混合发布说明](tools/PUBLISH_MIXED_ROSTER.md)
- [混合分辨率合同](MIXED_RESOLUTION_CONTRACT.md)
- `tools/pipeline.py`、`verify.py`、`assemble_mixed_roster.py`、`approve_mixed_roster.py`、`stage_mixed_roster.py`。
- 旧11项文本SHA差异已有精确换行reconciliation报告通过，不再是未知原因；不改历史字节，装配按文档使用--reconcile-legacy-text。

Python可用：`C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`（本轮实际使用，带-X utf8 -B）；另旧安装Python312可用但恢复时先确认。

图像工具新单帧receipt必须保存实际请求（精确prompt字节、refs、UTC开始时间）、真实output_hint/default原图路径、1次成功内置/0收费API、SHA。不要只写空壳receipt；不要在prompt末尾多加换行造成实际request字节不一致。所有原始默认生成文件保留。

## 7. 暂停、进程与其他工作

本任务不自动恢复、不设提醒/定时器；所有在途结果已完整归档；04、05、06和工具分支均已确认无自有运行cell/session，主代理所有已启动命令也已结束。具体文件以本次STATE JSON和角色最终交接为准。没有启动Unity或发布进程。其他窗口主城/地图及既有提交推送任务不属于本角色任务，不要终止或回滚。运行期间曾观察git -C E:/work/image diff报告Not a git repository，未尝试修复仓库；以后需要Git操作时先重新只读确认，不据此做初始化/reset/clean。


## 8. 提交时的源码保存

隔离工程无Git仓库，两份已改PlayMode测试已原样复制到 [隔离测试源码快照](mixed-preparation/recovery-20260919/walk-capture-isolated-source/README.md)，SHA与最终测试交接一致。这是交接保存，不是正式工程同步或Unity验收。
