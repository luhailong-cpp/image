# 两台 Windows 电脑合并当前成果，迁移到没有旧历史的 Azure 仓库

正式目标是私有仓库：<https://luyuacpp.visualstudio.com/image/_git/image>，分支 `main`。首批本机增量已上传并完成独立下载、逐文件 SHA256 和 LFS 校验：764 文件，约 255 MiB，根提交 `a0108e328631477df3caeb0b9fb80ecad7a82799`。完整素材仍需另一台电脑补齐；详见 `verification-migration-first-batch.json`。本机旧历史尚未删除。

2026-10-16 重启后已完成本机当前实体清单：`this-pc-current-plan.json`，24,976 个文件、5,199,924,221 字节，另有 19,469 个稀疏检出缺失路径。`SourceComplete=false`，用于两端对照；清单中的文件并未全部上传或全部批准迁移。新增核对记录为 `reconciliation-20261016-resume.json`：63 份来源／制作／失败验收文字保留，8 份过期轮询信号留在原机，9 个明确删除的截图保持删除；剩余61张城市图和1份仍被接入引用的进度记录待核对。另一台电脑尚未开始迁移，完整项目仍未具备。

新仓库以本机已核对的当前增量建立新根提交，再用正常后续提交合入另一台电脑的当前成果。旧分支、旧标签、旧提交和旧 `.git` 不进入新仓。先保留源目录及其 `.git`，等两端成果合并、上传、独立下载校验后再清理旧本地历史；这个工具不负责删除旧仓或强推任何远端。

## 另一台电脑先生成清单

解压工具包，用 **PowerShell 7** 进入解压目录，Git for Windows 需 **2.46 或更新版**。将下面 `D:\work\image` 改成另一台电脑真正包含最新成果的仓库路径。不要选择旧备份；已提交和未提交的新文件都要保留。采集期间暂停改图、保存文件和定时提交。

```powershell
pwsh -NoProfile -File .\Prepare-Azure-Snapshot.ps1 -Action Plan -SourcePath 'D:\work\image' -OutputPath "$env:USERPROFILE\azure-other-pc-plan.json"
```

把生成的 `azure-other-pc-plan.json` 交回当前对话，或交给负责两台电脑合并迁移的助手。这份清单含本机路径、当前 HEAD、工作区变更、逐文件路径/大小/SHA256、LFS 属性和排除记录；没有文件正文、密码或 Git 历史。不要原样上传整个 `.git`。

`Plan` 会顺序读取当前文件计算 SHA256，100GB 内容可能需要较长时间，但不会复制 100GB 数据、下载缺失历史、联网或上传。只想先看文件数量和体积，可以把 `-Action Plan` 换成 `-Action Inventory`，输出另起一个文件名；Inventory 没有哈希，不能据此导出。

若提示输出已经存在，换一个新输出文件名即可；工具不会覆盖它。若提示未还原的 LFS 指针，先在这台电脑恢复对应文件的实际内容。若提示 sparse / skip-worktree，意味着当前目录不是完整检出，必须先确认完整素材来源，不能把未下载的文件当作删除。工具不会自动下载大体积内容。

可复制给另一台电脑的助手：

> 请检查最新 image 仓库，保留这台电脑做过的所有当前成果和未提交修改。使用 Prepare-Azure-Snapshot.ps1 生成 Plan 清单，输出到仓库外；暂停采集期间的自动提交。目标 Azure 地址是 https://luyuacpp.visualstudio.com/image/_git/image，main 从无旧历史的新根开始。先把清单回传，特别说明这台新增/修改/有意删除的资源和源码；再与 Azure 中本机首批增量比较，合并到新 main。当前阶段保留源仓和 .git，不推送旧历史；同名内容不同先处理冲突，不能覆盖另一台的新工作。

## 两端对照

两端都完成 Plan 扫描后，可比较清单：

本机已提供上述对照清单；可将下面 `-PlanPath` 替换为下载到的 `this-pc-current-plan.json`，另一端用其最新生成的清单。两端的 `Complete=true` 表示扫描完成，只有 `SourceComplete=true` 才表示完整检出。比较结果必须结合新核对记录和有意删除记录处理。

```powershell
pwsh -NoProfile -File .\Prepare-Azure-Snapshot.ps1 -Action Compare -PlanPath "$env:USERPROFILE\this-pc-plan.json" -OtherPlanPath "$env:USERPROFILE\azure-other-pc-plan.json" -OutputPath "$env:USERPROFILE\azure-compare.json"
```

相同路径、相同 SHA256 可视为同一内容；同名内容不同必须合并或选定正式版本。只有一端出现的文件可能是新增，也可能是另一端主动删除，工具一律列入待核对，绝不自动求并集或删除。工作区删除有结构化证据；已经提交的历史删除需要另附基准到当前的变更清单。

当前这台电脑是部分克隆且使用稀疏检出，不能用它缺少的文件判断另一台应删除什么。它的待迁移增量由单独的只读审计清单提供，不把本机旧主分支合并进新的 Azure 历史。

如需采集当前实体用于对照，可显式加 `-AllowIncompleteSparse`。清单的 `SourceComplete=false` 表示它不是完整源；`MissingSparseFiles` 仅表示尚未取到的文件，绝不是删除。这样的清单可比较，但 `Export` 永远拒绝将它作为完整快照。`Complete=true` 仅表示本次扫描已经完成。

## 核对完成后再导出

导出会复制清单中的全部内容，需要足够的新目录空间。100GB 仓库不要在未确定空间和两端冲突前运行。导出目录必须尚不存在、位于源仓库之外，父目录已经存在：

```powershell
pwsh -NoProfile -File .\Prepare-Azure-Snapshot.ps1 -Action Export -SourcePath 'D:\work\image' -PlanPath "$env:USERPROFILE\azure-other-pc-plan.json" -OutputPath 'D:\azure-image-snapshot'
```

它一边复制一边核对哈希。源 HEAD、工作区状态或已记录文件内容变化会停止。失败的部分目录保留供检查，不会被自动上传；应重新生成清单并使用新输出目录。成功会在快照旁生成 `.receipt.json`，快照本身没有 `.git`、提交或远端。

导出不是上传，也不自动创建 Git 仓库。先从 Azure 新 main 克隆到独立目录，按两端清单合入确认的文件，检查 LFS 规则，再正常提交推送；最后到另一目录重新下载并验证。若远端仍为空，才创建新的根提交。已有 `.gitattributes` 会随文件保留；原仓 `.git/info/attributes` 和全局属性不会复制，因此需要核对清单记录的实际 LFS 属性以及 `RequiresLfsBySize`，不能仅凭扩展名认为所有大图已进入 LFS。

## 自动排除和停止条件

- 复制当前索引中的文件及非忽略的未跟踪文件；已删除文件不会被补回，staged deletion 的残留未跟踪副本也不会重新加入。
- 排除 `.git`、`.cache`、`.codex`、`.aws`、`.ssh`、`.azure`、`node_modules`、`__pycache__`、环境凭证文件、私钥文件、旧 `.lfsconfig` 和认证诊断文件名。每条排除写入清单，应核对是否包含需要单独处理的内容。
- 精确排除 `designs/team-invites-20260928/aoi-fix/build/` 和该组队交付目录内的测试 exe、pdb、obj、ilk、tlog、原始日志；不全局排除正式游戏 exe。
- 精确排除 `designs/team-invites-20260928/live-acceptance/robot.yaml`，这是可能含密码的本地验收账号配置。需要模板时应单独生成去掉凭证的版本，不能迁移当前配置。
- 排除技能接入目录 `designs/class-skills-20260928/integration/` 下的 `.contract-generation/`、`python-deps/` 缓存，以及 `.client-validation/` 下的 bin、obj、dll；保留 client/server 正式接入代码、测试源码、配置和结构化结果。
- 如还要排除已核实的本地输出，可传 `-AdditionalExclude '相对目录一','相对目录二'`，使用相对路径前缀，不使用通配符。
- 冲突、未结束的 merge/rebase、子模块、嵌套仓库、链接/目录联接、未恢复的 LFS 指针、稀疏检出会停止，避免漏文件或读取源仓以外内容。
- 清单和文件名排除不等同于完整的秘密扫描。正式上传前仍需审阅本轮实际迁移文件；工具默认不联网、不上传、不删除、不改源仓的 Git 配置。
- 采集时在子进程中禁用源仓所有 clean/process 过滤器，防止 `git status` 执行自定义脚本或写 LFS 缓存。因此清单状态只用来检测采集期间的变化和删除，LFS 实体文件可能显示为修改；内容判断应使用 SHA256。

离线测试命令：`pwsh -NoProfile -File .\Test-Prepare-Azure-Snapshot.ps1`。测试仅创建并清理自己的临时合成仓库，不访问 Azure。

本轮也补充本机后续提交里的194个新正式文件及37个直接依赖，约44.7MB，包括邮件、社交、组队UI与NPC接入成果。清单见 resume-new-work-review.json 和 resume-new-work-dependencies.json；其中63个首批已有文件按哈希去重。当时暂缓的3张gameplay底板及3份提示词已在2026-10-17后续增量重新核对，见文末。接入代码的暂存状态保留，上传不代表客户端已接入或新增视觉验收通过。

2026-10-17 后续增量：已按冻结哈希选择 68 个新建或修改文件，另有 133 个依赖与现有 Azure 内容相同。详见 current-file-delta-20261017.json、azure-gameplay-delta-20261017.json 和 azure-ui-delta-20261017.json。原6个 gameplay 底板/提示词已有采用与来源证据，按当前设计及唯一在制皮肤保留；实际未披露的模型、质量和生成时间继续标为未知。本轮冻结时另有 77 个 gameplay 接入/切片/验证文件及 80 个 guild 在制文件暂缓，待后续稳定后按新输入继续审阅，源文件均保留。原61张城市图及1份服务端进度记录仍待核对。此增量未重扫全库，须与旧 Plan 和历次增量一起对照。包内安装与静态编译声明保留其原始范围；客户端安装 guard 已发生变化，不能沿用旧 guard 覆盖当前客户端，也不能据此宣称 Unity 或游戏验收完成。另一台来源仍未提供，上传和独立下载结果以真实 main 及最新 verification 报告为准。

2026-10-17T04:56Z 后续审阅批次：本次选择 546 项新建或修改的当前文件，132 项依赖内容与 Azure 相同。最新清单为 current-batch-20261017T045606.json，四份对应 review-20261017T045606.json 及 parent-overrides 记录包内来源、逐文件SHA和旧Hold去向；以这些逐项结论更新前一批的待核对状态。本轮仍有 45 项Hold，具体路径和原因见 migration-status.json 的 LatestBatch.HeldPaths；原61张城市图、1份服务端进度记录及另一台完整来源仍待核对。保留来源未知信息和原验证范围，离线截图/安装报告不代表联机或全部视觉验收。此批次不重新扫描全部源文件、不导入旧历史、不修改原素材。当前上传与独立下载结果以实际main及最新verification报告为准。

2026-10-17T06:01Z bounded batch: 233 current changed/generated files; 227 unchanged dependencies. See current-batch-20261017T060107.json and its reviewed reports. The latest root AGENTS.md and both designated UI references are included and byte-checked. A current attribute/pet/skill code manifest distinguishes final payloads from superseded historical install manifests; no installer is run. 2 paths remain Hold, listed in migration-status.json LatestBatch. The original 61 city images and one server progress file, full local source coverage, and the other PC remain unresolved. FullProjectAvailable remains false. Runtime/test failures and unknown provenance are preserved; see the eventual independent verification report for actual upload/download status.


2026-10-17T06:59Z bounded batch: 63 current changed/generated files; 36 unchanged dependencies. See current-batch-20261017T065945.json and its reviewed reports. Existing user instructions and designated references remain in the verified baseline. A current patch map distinguishes final payloads from superseded intermediate manifests; no installer is run. 2 paths remain Hold, listed in migration-status.json LatestBatch. The original 61 city images and one server progress file, full local source coverage, and the other PC remain unresolved. FullProjectAvailable remains false. Runtime/test failures and unknown provenance are preserved; see the eventual independent verification report for actual upload/download status.

