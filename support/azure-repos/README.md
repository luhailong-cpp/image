# Windows 上使用 Azure Repos

复制本目录到其他 Windows 电脑，使用 PowerShell 7。先安装 [Git for Windows](https://gitforwindows.org/)，安装时勾选 Git Credential Manager。工具不会替你安装 Git、修改全局 Git 设置、自动合并两台成果或删除旧仓。

正式私有仓库 `image` 的首批本机增量已上传并独立下载验证：764 文件、约 255 MiB，新历史始于根提交 `a0108e328631477df3caeb0b9fb80ecad7a82799`，该批全部 SHA256 一致，后续通过正常提交继续补充。**这不是完整项目**；另一台电脑的当前成果仍需合入。先读 [两台迁移说明](MIGRATION.md) 和 [另一台电脑交接指令](OTHER-PC-HANDOFF.txt)，首批验证记录为 `verification-migration-first-batch.json`。

重启后本机对照清单已更新为 `this-pc-current-plan.json`（24,976个实体文件，19,469个稀疏缺失路径）。清单用于比较，不能据此认为这些文件已全部上传。新处理决定见 `reconciliation-20261016-resume.json`；它保留失败验收文字，并将仍需核对的城市图片与进度记录明确列出。

另一台电脑可以用以下命令将新 main 下载到全新目录，随后与它已有的项目对照。它不会覆盖旧项目；如果目标已存在，请换一个尚不存在的目录名。

```powershell
pwsh -NoProfile -File .\Azure-Repos.ps1 -Action Clone -RemoteUrl 'https://luyuacpp.visualstudio.com/image/_git/image' -TargetPath (Join-Path $env:USERPROFILE 'image-azure') -AuthFlow devicecode
```

每台电脑第一次连接、授权过期或组织要求验证时，都需要由你本人完成微软账号登录和 MFA。成功后由该电脑的 Git Credential Manager / Windows 凭据管理器保管凭据，通常后续可自动连接；不能保证永久免登录。复制工具包不会复制另一台电脑的登录状态。无需填写 PAT、密码，也不要把它们发到聊天或写入 URL。

若默认浏览器登录不方便，可加 `-AuthFlow devicecode`，按照终端显示的微软登录网址和一次性设备码，在已登录的浏览器内由本人确认。不要把设备码发给其他人。默认 `-AuthFlow system` 使用系统浏览器。

设备码模式请在普通交互式 PowerShell 7 或 Windows Terminal 窗口运行，工具会关闭 GUI 提示，将设备码显示在终端。由代理执行时必须分配 TTY（例如 `exec_command` 的 `tty:true`）；GCM 2.9 会直接向 Windows 控制台写设备码，普通后台管道可能看不到提示却持续等待，重定向 stdout/stderr 不能补救。

本轮专用测试仓：https://luyuacpp.visualstudio.com/azure-repos-probe/_git/azure-repos-probe 。实际上传、拉取和独立克隆已通过，100+ GB 正式素材项目尚未迁移。组织已有其他项目不在测试范围内。

其他 Windows 电脑解压工具包后，在包含本文件的目录打开交互式 PowerShell 7，直接执行以下 Clone 命令。目标为当前用户主目录下的全新 `azure-probe-copy` 文件夹；若它已存在，请换一个尚不存在的目录名。

```powershell
pwsh -File .\Azure-Repos.ps1 -Action Clone -RemoteUrl 'https://luyuacpp.visualstudio.com/azure-repos-probe/_git/azure-repos-probe' -TargetPath (Join-Path $env:USERPROFILE 'azure-probe-copy') -AuthFlow devicecode
```

## 命令

以下 `组织/项目/仓库` 是占位符，请换成 Azure Repos 显示的 HTTPS 仓库地址，去掉 URL 中的 `用户名@`。首次可加 `-CheckOnly`，只检查本地参数和保护条件，不联网、不修改文件。

```powershell
$remote = 'https://dev.azure.com/组织/项目/_git/仓库'

# 新建独立目录，克隆 Git 与当前版本的 LFS 素材
pwsh -File .\Azure-Repos.ps1 -Action Clone -RemoteUrl $remote -TargetPath 'D:\work\image-azure'

# 拉取：只允许快进，分叉时停止；不会丢弃或自动提交本地改动
pwsh -File .\Azure-Repos.ps1 -Action Pull -RemoteUrl $remote -TargetPath 'D:\work\image-azure'

# 先自行检查并明确 add/commit 要提交的文件，再上传已提交内容
pwsh -File .\Azure-Repos.ps1 -Action Push -RemoteUrl $remote -TargetPath 'D:\work\image-azure'
```

默认分支 `main`，其他分支加 `-Branch 分支名`。目标必须是独立普通仓库；现有目录、脏工作区、分支不一致、未结束合并、不同 origin、独立 LFS 地址、URL 重写或自定义 hooks 路径会停止。脚本不会删除目录、覆盖远端、强推、自动 stash 或批量提交你的文件。上传使用现有 LFS 预推送钩子；已有自定义钩子冲突时停下，不强行替换。

## 先做小型测试

在 Azure 页面新建**空的专用测试仓**，不要在已有项目仓中测试，不勾选初始化 README。传入该仓的 URL：

```powershell
pwsh -File .\Azure-Repos.ps1 -Action Probe -RemoteUrl 'https://dev.azure.com/组织/测试项目/_git/空测试仓' -TargetPath 'D:\work\azure-probe'
```

Probe 仅生成并提交普通文本与 16 MiB 随机文件，上传后从远端独立克隆、下载 LFS 并对比 SHA256。`probe-result.json` 保存结果，不含凭据。失败时保留现场，不删除或覆盖；重跑需要新的本地目录及空测试仓，不能对已经有提交的同一测试仓重复 Probe，可改用 Clone。小样本成功不证明百 GB 迁移一定完成，也不能替代计费页面核对；结果将 `BillingVerified` 保持为 `false`。

Probe 会为自己生成的 `README.txt` 和 `.gitattributes` 写入 `text eol=lf` 属性，保留二进制 LFS 规则。这样即使其他 Windows 电脑启用了 `core.autocrlf=true`，检出文本也保持 LF，SHA256 可以直接比较。普通 Clone/Pull 不改仓库或全局的换行偏好。

## Git LFS

已有 Git LFS 时直接使用。缺失时自动下载官方 Windows x64 便携包 **3.8.0** 至 `%LOCALAPPDATA%\AzureReposHelper\tools`，先核对官方 SHA256 再运行，不注册系统环境变量。ARM64 电脑请先安装对应官方 Git LFS。

也可通过 `-LfsExecutable 'D:\tools\git-lfs.exe'` 使用已有便携工具，或 `-ToolDirectory 'D:\tools\azure-repos'` 指定缓存。便携工具的 PATH 仅在脚本执行期间生效；若要在其他 Git 客户端直接执行 LFS 操作，需自行安装 Git LFS。本工具只对目标仓运行 `git lfs install --local`，不会对主仓或全局执行安装。

固定下载来源：https://github.com/git-lfs/git-lfs/releases/tag/v3.8.0

Windows amd64 ZIP SHA256：`b62e7b8ceddee635f691233d77de8eaa4b213e9209e0173811d8cfa77f7882c1`。

认证依据：[微软 GCM 文档](https://learn.microsoft.com/en-us/azure/devops/repos/git/set-up-credential-managers?view=azure-devops)、[GCM 配置说明](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/configuration.md)。脚本用进程范围的 OAuth、系统浏览器与 Windows 安全凭据存储设置；退出时恢复进程环境。

## 本轮验证结果

2026-10-16（UTC）实际连接上述私有测试仓，通过 Git 与 16 MiB LFS 文件上传、脚本 Push、快进 Pull、独立 Clone 和 `git lfs fsck`。最终 `main` 提交为 `b9e449848c11a8ed396f6f7e564e7e1104760375`；独立下载的 README 与 LFS 文件均与源文件 SHA256 相同。详细结果见 `verification-azure.json`。

首次 Probe 的文本哈希检查因 Windows 将 LF 转为 CRLF 而失败。已修复测试仓的明确 LF 属性，再通过全新克隆逐字节校验；工具中的 Probe 同步修复，并通过离线回归。本轮没有对同一个非空远端重新执行完整 Probe。

组织 Billing 页面确认当前未设置付费计费，使用免费层及 5 个 Basic 用户名额，本任务未启用付费。这记录的是本轮小样本实测与当时页面状态，不代表对 100+ GB 容量、性能或永久免费作保证；全量迁移尚未完成。3 张网页证据截图已按用户要求于 2026-10-16 删除，验证 JSON 中的图片路径仅作历史记录，便携 ZIP 不包含截图。逐文件清单见 [截图清理记录](../../docs/screenshot-cleanup-20261016.json)。

离线检查共 **19 项通过**，覆盖语法、17 项保护条件、真实子进程的跟踪环境隔离，以及 `core.autocrlf=true` 下的独立检出与文本 SHA256 回归，结果见 `verification-offline.json`。这些检查不访问远端。`Test-Azure-Repos.ps1` 可独立重复运行，只在临时目录创建合成仓并保存离线结果。
