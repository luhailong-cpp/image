# 00 金发带道童合并交接

交付对象：`00_reference_topright_boy`。工作区 `D:/work/image`；本批启动基线 `80562e0b64037c7bea600f0211b57bd2bf820590`，分支由统筹维护为 `codex/character-actions-20261001`。此处只交接本角色文件，没有执行 Git 暂存、提交、推送或客户端覆盖。

当前是**制作中的候选素材交接**。最终目标为八方向跑步各 16 帧，加 E/W 受击各 6、普攻各 12、施法各 16，共 196 槽。另一台电脑未提交图没有获取；本机已提交旧素材经实图审核后复用，复用不计作本批新生图。

<!-- CURRENT_SNAPSHOT_START -->
核对时间：2026-10-02T07:24:50.968381-04:00（America/New_York）。本段由 tools/audit_provenance.py 实扫更新。

当前候选导出 **57/196**，缺 **139** 槽；本批本角色 generation 实际原图 **4** 张。正式美术通过 **0**；客户端 **未接入、未运行**。

| 动作/方向 | 实际导出帧号 | 缺失帧号 | 帧时长 / 完整段时长 |
| --- | --- | --- | --- |
| run/N | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/NE | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/E | 01、04 | 02、03、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/SE | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/S | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/SW | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/W | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/NW | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| hit/E | 01、02、03、04、05、06 | 无 | 40 / 240 ms |
| hit/W | 01、02、03、04、05、06 | 无 | 40 / 240 ms |
| attack/E | 01、02、03、04、05、06、07、08、09、10、11、12 | 无 | 30 / 360 ms |
| attack/W | 无 | 01、02、03、04、05、06、07、08、09、10、11、12 | 30 / 360 ms |
| cast/E | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 45 / 720 ms |
| cast/W | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15 | 16 | 45 / 720 ms |

当前本批原图（逐图来源、完整路径及导出链见 [来源审计](review/provenance-completion.json)）：

| 文件 | SHA-256 | 已关联导出 |
| --- | --- | --- |
| [generation/combat/attack/W/06-v3.png](generation/combat/attack/W/06-v3.png) | `527ff10ab675ab3c0596ee1a3a8274ee095b8e3fc17a1f3919083a86d6cf21e8` | 未导出；待选帧/验收 |
| [generation/run/E/01-v5.png](generation/run/E/01-v5.png) | `0335d08d84cd367c85a43fb72dd69980a45befd970d9ab1de1a1758a315b4dc6` | 未导出；待选帧/验收 |
| [generation/run/E/04-v1.png](generation/run/E/04-v1.png) | `ecc55b1b0e7dea0d3f2077e106a229d679e7f2e71cacba773df263f0a6927a06` | frames/run/E/04.png |
| [generation/run/E/09-v3.png](generation/run/E/09-v3.png) | `703ab6983638bbcd29488af9806644205168a508c7bd85f6bb6ea56d208e5a83` | 未导出；待选帧/验收 |

已确认失败请求 6 项（原始网络错误证据保留）；无完成证据请求 3 项（unknown，不等同于已确认失败）。

- `generation/combat/attack/W/06-v1.request.json` — `confirmed_failure`；SHA `46b18acd30cdc2e76aab1eb552faa90e3a9cefb054396a9ba700a871a8f424ab`。
- `generation/combat/attack/W/06-v2.request.json` — `confirmed_failure`；SHA `15f79062b2d44e7fca1cdbd8b10929ed62b80bda705b618c82ab3c164fde5fb2`。
- `generation/combat/cast/W/16-v1.request.json` — `confirmed_failure`；SHA `5a4f35dbfa78cba8797b994877eb7d284b61a8330c1b5194e223d22232b5209e`。
- `generation/combat/cast/W/16-v2.request.json` — `confirmed_failure`；SHA `fd301a6b0279b4605f81bdf5d0d375e3d524243abf3cf044a7699b86ebec4d12`。
- `generation/run/N/01-v1.request.json` — `confirmed_failure`；SHA `4369161b44a6161fc9f1b1c1ffcd092d42851e587181ed1261f72a668bd045c5`。
- `generation/run/N/01-v2.request.json` — `confirmed_failure`；SHA `cb1890b901b4b6b3ec504771eeb236648b3c9a4100c0ceb8349269f5ce8fe0b5`。
- `generation/combat/cast/W/16-v3.request.json` — `unknown_no_completion_receipt`；SHA `5d13252494f0ca7d776eece32b29a35e01f57aa5ffbec9dab5efc6ca81df8fa0`。
- `generation/run/E/09-v2.request.json` — `unknown_no_completion_receipt`；SHA `65b205d98eb8e51761d040eb5f6a4a50020cee35ea04f4537da01db2866eda03`。
- `generation/run/N/01-v3.request.json` — `unknown_no_completion_receipt`；SHA `68659a615a528a35f695bc357bb30c97903a2771d499d906e005de1241a05eff`。

当前索引/源SHA问题 0 项。逐项文件、源PNG、生成记录与回执SHA均在 `review/provenance-completion.json`。
旧 `current-validation.json` 的 57 张检查仅适用于其原始快照；新增原图、替换及当前动态美术结果须另行刷新。
<!-- CURRENT_SNAPSHOT_END -->

## 合并文件和来源入口

本角色唯一写入根目录：`D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy/`。合并时保留目录相对关系：

| 文件或目录 | 用途与合并限制 |
| --- | --- |
| `frames/<动作>/<方向>/<01起两位帧号>.png` 及 `.png.generation.json` | 实际 1024×1024 RGBA 候选导出及派生来源。不是已获正式美术通过的 runtime 包；缺槽保持空。 |
| `manifest.json`、`sources.json` | 当前选帧、导出 SHA、源路径/SHA、操作与模型证据索引。旧状态与实际库存冲突时先核对，不能用旧计数覆盖新增图。 |
| `generation/` 下当前原图及提示词、请求、回执、逐图记录 | 仍在修正、尚未导出或当前参考中的唯一在制稿和证据。多版本不增加动作槽数；高版本号不自动通过。 |
| `review/provenance-completion.json` | 本次实扫的全部导出/本批原图、源图、生成记录、请求回执路径和完整 SHA-256 清单；包含缺槽、unknown/确认失败及 E04/E09 配置来源补记。 |
| `review/current-validation.json`、`technical_report.json` | 有明确时间和范围的技术/预览记录；新增或换图后重跑，不能套用旧快照证明新图通过。 |
| `review/scale-audit.*`、`combat-reviewed.*`、`cast-selection.json`、`cast-review.md`、`visual-notes.json` | 绑定原图 SHA 的静态选帧、比例与问题证据；新稿必须重新审核。 |
| `review/index.html`、配套检查图及 `tools/` | 正常/慢速/逐帧预览和角色私有审计/导出工具。运行前核对选表和来源，不运行共享默认输出管线。 |
| `IDENTITY.md`、`STATUS.md`、`MERGE_HANDOFF.md`、`TASK.md` | 身份锁定、当前缺口、合并说明和任务范围。 |

旧来源在 `D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/00_reference_topright_boy/` 与 `run-correction-20260930/characters/00_reference_topright_boy/`，仅只读引用。每张使用了哪个旧源、原图 SHA、生成记录和当前导出 SHA 都在来源审计的 `frameInventory`。换电脑后先用仓库相对位置定位并核对 SHA；不要假定旧 `E:/work/image` 或 `D:/luyuan/wuxingqitan/image` 绝对路径存在，也不要改写历史证据中的原始路径来冒充当时记录。

## 根锚、画布和事件契约

成品目标是 1024×1024 RGBA；当前已选原生单帧为 1254×1254。现行导出对完整 1254 画布等比缩至 901，然后放入 1024 画布：E 偏移 `(61,106)`，W 偏移 `(41,118)`，记录中的根锚 `(512,942)`。这些都是**待复核候选映射**；统一画布不证明原图人物比例统一，E/W 既有偏移也没有完成跨方向验收。跑步比例不能靠逐帧不同缩放、最低像素贴地或独立包围盒居中修好。

暂以 `combat-20260929/characters/00_reference_topright_boy/staging/attack-E-01-v1.png`（SHA `ccb31d8b268579b952810310cda02695d12f701f94fd203bbbfea8607d41e1b6`）与 `cast-E-01-v1.png`（SHA `d4cb208d2478166aface9ce4066207e1b5687bd9a45d2d6fe058091fd0bca7f9`）作为 E 向原画布比例参考，idle 仅校对身份。原生虚拟地面约 `y=1164`、E 向虚拟根约 `x=628` 是复核建议，不是逐帧脚底吸附坐标。允许真实支撑压低、蹬地、腾空和重心起伏。

| 动作 | 正常帧时长 | 完整段时长 | 暂定事件，均为 1-based |
| --- | ---: | ---: | --- |
| run | 30 ms | 480 ms / 每方向16帧 | 无战斗事件 |
| hit | 40 ms | 240 ms / 每方向6帧 | 由战斗代码触发受击；未接入 |
| attack | 30 ms | 360 ms / 每方向12帧 | **06 命中候选，待验收**；该帧起点 150 ms |
| cast | 45 ms | 720 ms / 每方向16帧 | **10 释放候选，待验收**；该帧起点 405 ms |

事件依据已查阅旧 `combat-20260929/handoffs-20260930/COMMON_CONTRACT.md` 第 3/8 项：普攻 05–06 为接触/峰值，施法 09–10 为释放阶段，最终事件按实际选图确定。旧 00 交接没有锁死单一帧号。当前静态复核认为 attack E05 可读作出掌接触开始、E06 为最远随动；cast E10 为释放起始、E11 最大伸展。因此保留 06/10 为**暂定标记**，不宣称它们已经得到动态确认或与客户端代码对齐。最终正常速/慢速检视后由明确事件表确认，E/W 都须各自验收。普攻 360 ms 不包含跑近和回位；特效/弹道与站位击退由独立层或代码处理。

## 尚未解决的美术与运行项

三张跑步问题源严格绑定如下，不能由新 PNG 出现自动解除：

| 问题源 | SHA-256 | 未通过原因 |
| --- | --- | --- |
| 旧 `run-correction-20260930/characters/00_reference_topright_boy/generation/E/01-v4.png` | `a5bf45554f0e74fcffdc7c9ce38bcc60c2d5a5376dd6dc3687b6e2dbdf348bea` | 头脸比战斗大且比另外两跑姿大；前鞋支撑偏低，需 AI 重约束比例与落脚。 |
| 本角色 `generation/run/E/04-v1.png` | `ecc55b1b0e7dea0d3f2077e106a229d679e7f2e71cacba773df263f0a6927a06` | 头脸偏大；保留后脚蹬地/前脚离地相位，不能两脚贴地。 |
| 本角色 `generation/run/E/09-v3.png` | `703ab6983638bbcd29488af9806644205168a508c7bd85f6bb6ea56d208e5a83` | 头脸仍大于战斗；落脚接近地面不等于比例或动作通过。 |

战斗四个静态问题继续保留：`hit/W/03` 双鞋横向站位突跳；`attack/E/10` 平底双鞋基线偏高；`cast/W/02` 提手过早后回落；`cast/W/05` 过早前伸后回收。对应源 SHA、观察与对比图见上述审核文件和来源审计；前两项须先校核支撑与根点，后两项严重度仍待正常速/慢速确认。

当前正式美术通过为 0。完整正常速、¼ 慢速、逐帧及首尾衔接、跨方向身份/手持侧、全帧透明边缘仍待验收。HTML 控件逻辑检查仅为简化 DOM，`file:` 浏览器打开曾受 URL 策略阻止；未实际浏览器播放的部分不能写成动态通过。当前机器未发现 `D:/work/mmorpg-client`，**未接入、未运行客户端**，素材制作继续独立推进。

## 模型与错误记录

本批配置目标是 GPT Image 2.5 Sunburst / max，按 2026-10-01 已核对的批次设置保持一致。内置工具没有 `model`/`quality` 选择器；实际提交和返回这两个字段均未确认，以各图原始记录的 null/说明为准。配置值、提示词、官方网址都不等于实际返回型号/质量。本批未使用收费 API/CLI。

本批 run E04-v1、E09-v3 的配置快照遗漏 `sources`；仅在 `review/provenance-completion.json/configSourcesSupplement` 关联同批已读配置、批次核对说明与 SHA 补充来源网址，不重写旧记录，也不回填 actualModel/actualQuality。历史 cast W01–09、W11–13 没有完整配置/原始参数记录，只保留已找到回执、提示词与当前 SHA，明确历史未记录，不用今天的配置补造。

网络失败只认带原始错误的 `.failure.json`。只有 request、没有完成回执/PNG 的条目记 `unknown_no_completion_receipt`；可能曾中断或仍在进行，不能称为已确认失败。每次重跑库存会重新关联后来到盘的回执和 PNG，历史请求中的 pending 字段不优先于已找到的完成证据。

## 合并后的刷新与清理

新图到盘后按顺序核对 SHA/逐图来源、重新选帧及导出、刷新 `manifest.json`/`sources.json`，重跑技术/预览与本角色 `tools/audit_provenance.py`，再对新源 SHA 做美术记录。来源审计只更新路径/库存/证据快照，不会把新图自动标成美术通过。新增图也可能只是替换同槽，不能按原图数量直接增加已完成槽。

当成品已落盘且引用完整后，按项目素材保留规则删除本角色被淘汰原图、回退稿与加工中间图，保留逐图文字来源与清理记录；仍是当前比例/姿态参考或未导出成品的唯一在制稿先按用途核实。旧定稿、共享身份/风格图及其他角色资源只读。当前没有执行图片清理。
