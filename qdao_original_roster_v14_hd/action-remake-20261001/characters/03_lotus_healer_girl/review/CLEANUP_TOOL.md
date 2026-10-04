# 莲花医者原生图清理工具

2026-10-04 最终选帧稳定、196张导出及14组浏览器加载通过后，已完成实际清理：删除285张未选生成图，显式保留195张本角色当前原生设计母稿及196张1024导出图；另1张当前来源在旧目录，仅只读引用。所有逐图文字记录与SHA保留，没有新增图片备份。技术核验不代表用户或客户端验收。

实际记录：[清理计划](cleanup-plan-final-20261004T232411095411Z.json)、[完整执行日志](cleanup-applied-20261004T232535264075Z.json)、[文字冻结清单](final-export-freeze-20261004T232411095411Z.json)。计划使用all-sources模式并逐个keep-source保留当前母稿，285个非当前源逐个retire-source；没有删除当前选用的原生PNG。所有删除路径均在本角色generation内，196成品在删除后再次核验完整。

以下为工具使用说明和历史准备记录。当前冻结清单所列文件应保持不变；如有新的修订任务，应建立新版本记录与冻结清单，不能把旧冻结记录视为新版本核验。未选祖先图片已淘汰，来源文字记录中的历史路径允许不再存在。

工具仅适用于 `D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl`。没有可改BASE的命令行选项，未修改现有build/finalize脚本。

## 安全边界与计划内容

- 唯一允许删除的对象：本角色 `generation/**/*.png` 中的普通文件。逐文件unlink，不递归删除目录；不删除任何JSON、prompt、job、receipt、review、设计图、宿主generated_images、旧角色或其他路径。
- 拒绝越界、符号链接、Windows目录联接/reparse point、硬链接、NTFS备用数据流；每次unlink前重新检查路径、PNG及溯源SHA。
- 开始时读取14组input、14组导出selection和all-actions-selection；要求196槽齐全且196个源SHA及196个导出SHA独立。逐帧核对原生和generation记录、1024×1024 RGBA透明导出、导出来源及完整画布LANCZOS像素一致。跑步每帧必须75ms。
- 计划使用实际绝对路径与SHA，列出selected、keep、delete、references、requiredFiles和外部源。只写紧凑的文件证据，不把完整提示词塞进计划；冻结文件另保存逐图源记录快照。
- 应用时重新完成全套检查，并与原计划指纹、目标列表严格比较。选表/图片/文字记录/工具代码任一变化，旧计划不能应用，需重新dry run。每次删除前还重查当前选表；选中源逐帧再与导出像素比较。中途失败立即停止，已执行部分写入journal，**不会自动回滚或继续扩大范围**。
- 不得与生图、选表编辑、build或finalize并发运行。若中途失败，先读journal确认已删内容；不要把它当作完整清理，也不要手工放宽校验继续。
- 当前E01/E05来自旧run-correction目录。它们参与196唯一源及导出核验，但不在删除边界内，任何模式都只读；冻结文件保留其文字记录快照。

## 两种模式

`unselected` 是默认模式。保留当前选中母稿、可找到的本角色参考祖先及显式指定的当前母稿。只将状态明确为reject/not_selected/superseded/discard/replaced的未选图列为删除项；未审/在制/缺少记录的唯一稿会列为hold。参考图在此阶段保留，供后续AI局部编辑。没有新增授权性确认流程：根任务可在核对具体计划后按既有用户保留规则执行。

`all-sources` 允许把当前本角色已选原生PNG也列入删除，但必须先由根任务明确决定冻结。它仍保留 `--keep-source` 指定的当前设计母稿，以及状态不明确的未选在制稿。确已淘汰但状态缺失的图，可用明确逐文件的 `--retire-source` 放入新计划；这不会覆盖unselected模式对当前母稿/参考祖先的保护。不是把所有未知文件一律当拒稿。

## 原始操作说明（实际执行见页首记录）

PowerShell，工具输出实际计划路径；不要预先猜测计划文件名：

```powershell
$taskPython = 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskCleanup = 'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl/tools/cleanup_generation.py'

# 默认只核验并写JSON计划，绝不删除
& $taskPython -B $taskCleanup --mode unselected

# 当前母稿可额外保留；参数为本角色相对路径或其绝对路径
& $taskPython -B $taskCleanup --mode unselected --keep-source 'generation/N/01-v1.png'

# 实际删除只能显式给出刚核对过的计划；替换为上一步真实输出
& $taskPython -B $taskCleanup --apply 'review/cleanup-plan-unselected-实际时间戳.json'
```

本轮已冻结文字清单，但显式保留了全部当前原生母稿。下面是不保留当前母稿时的工具用法，并非本轮执行结果：

```powershell
# 只创建冻结文字清单及all-sources计划，仍不删除
& $taskPython -B $taskCleanup --mode all-sources --write-freeze

# 只有根任务核对all-sources计划并决定后才应用
& $taskPython -B $taskCleanup --apply 'review/cleanup-plan-all-sources-实际时间戳.json'

# 删除原生源后仍可验证成品、文字证据与像素哈希
& $taskPython -B $taskCleanup --verify-freeze
```

默认冻结文件为 `review/cleanup-export-freeze.json`，使用独占创建，绝不覆盖旧冻结。如冻结前后还改选表/图/证据，应在原生仍齐全时使用新的 `--freeze-file review/cleanup-export-freeze-新编号.json`；后续all-sources计划、apply和verify必须传同一freeze-file。计划也独占创建，默认带时间戳。不要手改计划或冻结JSON；指纹/文件检查会拒绝，记录也会失去审计价值。

## 最小冻结方案与删除后的限制

保留现有196张 `candidate/<action>/<direction>/<slot>.png` 1024透明成品及每张generation记录；保留14个input和selection、all-actions-selection、manifest、时序/根点/事件/来源索引、交接/验证记录，以及 `preview/actions.html`、`actions.js`、`timing.js`。全部本角色generation文字记录继续保留。冻结JSON记录这些真实文件的SHA、逐帧导出像素SHA、来源SHA及完整源generation记录快照；**不另存任何原生PNG备份**。当前预览只读取导出图和all-actions-selection，因此不需要已删除原生PNG。

删除已选原生源后，下列工作不再可执行：

- `build_action_review.py`及兼容入口`build_review.py`：重新导出、原生SHA检查、原生联系图均要打开已选PNG，会缺源失败。
- `build_nw_review.py`、`review_w_sequence.py`、`review_diagonal_sequences.py`、战斗选表/审阅脚本及其他直接打开generation源的检查：会缺源，不能用旧脚本覆盖冻结的选表。
- 以原生图作为target的AI局部编辑、重新导出更大尺寸或改变降采样方式：原生已删除，无法无损恢复。1024成品可作为后续明确新任务的输入，但不是原生副本。
- `finalize_actions_review.py`/`finalize_review.py`本身主要读导出和选表，不必然因删原生而报错，但会重写冻结的交接/事件/索引文件，导致冻结核验失效；`update_status.py`也会改写冻结库存。冻结后应停用这些写入脚本，只用`--verify-freeze`验证交付。

若仍需调整动作/根点/接入结构，不应选择all-sources。先做unselected拒稿清理，保留母稿直至根任务确认成品和当前引用完整。工具不会替根任务把待审候选声明成已验收成品。

## 已做的测试

`tools/test_cleanup_generation.py`的10项测试仅使用内存图与mock，无实际素材扫描或删除。覆盖14组196目标、指纹变化、重复/缺失槽、越界/非PNG、备用流、symlink/reparse、硬链接、过期/篡改计划、无冻结all-sources、即使声明SHA匹配仍拒绝错误导出像素。随后执行的真实清理及核验以页首计划、冻结清单和执行日志为准。
