# 游戏图片与 AI 设计工具：安装及 Codex 交接

本文件记录 2026-09-05 已完成的个人安装，并提供在其他用户电脑上复现的步骤。范围为 **9 个 Skills、4 个 MCP，以及图片处理和 Figma 桥接所需运行时**。工具安装在用户目录；克隆本仓库只会取得本说明和项目文件，仍需执行安装。

## 项目绘图偏好与换电脑

本项目的模型、质量与调用方式以根目录 [AGENTS.md](../AGENTS.md) 为准。复制项目时保留该文件；通过 Git 迁移时需将新增规则提交并同步到新电脑，再从该项目开启 Codex 任务。

2026-09-07 核对的 [OpenAI 官方内置生图说明](https://learn.chatgpt.com/docs/image-generation) 指明内置生图使用 `gpt-image-2`，计入 Codex 用量。新电脑若已提供内置生图，无需为这条路径安装本文件列出的整套工具或配置 OpenAI API 密钥。内置接口未开放质量参数时，不能承诺已强制设置某个质量档位。

2026-09-10 用户重申：直接使用内置 GPT Image 2，以最高质量为目标，不将单独 API 配置作为出图前置条件。内置接口当前未提供 model／quality 参数，因此“最高质量目标”与“已显式设置 quality=high”分别记录。若本地参考路径遇到 Windows ACL 读取故障，排查参考图输入方式，优先使用工具支持的对话图片输入；文件读取故障与账号／密钥配置分开诊断。

API/CLI 仅作为用户明确选择的备用路径，需要在新电脑准备相应工具与账号凭证，并单独按 API 计费。项目文件不会自动安装用户目录工具或转移凭证；换电脑后先确认实际可用能力。仅修改规则不代表已完成真实生图验证。

给接手 Codex 的任务可以直接写成：

> 阅读 `docs/AI_DESIGN_TOOLS_SETUP.md`，检查当前电脑已有的 Skills、运行时和 MCP 配置，按固定版本补齐缺项。使用当前用户目录，保留已有配置和项目文件，完成离线验证。把需要用户提供凭证或在 Figma 中操作的项目单独列出；安装验证不调用付费生成 API。

## 1. 已安装内容与实际状态

| Skill | 能力 | 生图前提 |
|---|---|---|
| `frontend-design` | 页面、组件与界面的视觉设计实现 | 主要生成界面代码，无独立生图 API |
| `canvas-design` | 静态画面、海报与 PNG/PDF 设计，含字体 | 本地绘图与文档运行库 |
| `ui-ux-pro-max` | 风格、配色、字体、交互及技术栈数据搜索 | 本地 Python；搜索本身不生成图片 |
| `baoyu-image-gen` | 多提供商文生图、参考图、批量生图 | 选定提供商及其凭证；部分路径依赖宿主能力 |
| `baoyu-design` | HTML 视觉设计、原型、设计系统与资产整理 | Node；PPTX/视频导出另有可选依赖 |
| `gpt-image` | GPT Image 生成和编辑流程、提示词参考库 | `gpt-image-cli` 和 OpenAI API 凭证 |
| `get-prompt-from-image` | 从参考图提取高保真生成提示词 | 宿主能够读取图片；本身不调用生图 API |
| `generate2dsprite` | 游戏精灵、动画帧、抠底、对齐与透明导出 | 创作阶段使用宿主图像工具；本地处理用 Pillow/NumPy |
| `generate2dmap` | 地图、地形、道具切片及组合预览 | 创作阶段使用宿主图像工具；本地处理用 Pillow |

**原安装的 4 个 MCP 均为 `enabled = false`。** 尚未配置真实 API 凭证，尚未在 Figma 中导入并连接对应插件，也未测试实际生图或修改 Figma 文件。MCP 初始化成功仅代表程序和协议可启动。

## 2. 固定来源

### Skills：按源码提交安装

每一行的 `--path` 都是仓库内的完整 Skill 目录。复制整个目录，保留其中的 `scripts`、`references`、`agents`、字体和数据文件。

| GitHub 仓库 | 固定 commit | `--path`，同一行可传多个 |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f` | `skills/frontend-design skills/canvas-design` |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | `f3ac195224eac1eb0dfe1a3059c2a6add78ffbe3` | `.claude/skills/ui-ux-pro-max` |
| [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) | `6b7a2e417500561a5ecdd0b168332f4142584617` | `skills/baoyu-image-gen` |
| [JimLiu/baoyu-design](https://github.com/JimLiu/baoyu-design) | `026d4ea012bdd5cada72ac8cc13f21ba4edf2245` | `skills/baoyu-design` |
| [wuyoscar/GPT-Image2-Skill](https://github.com/wuyoscar/GPT-Image2-Skill) | `135d873e1a843db5f122a15ddda02bd2845d4d25` | `skills/gpt-image skills/get-prompt-from-image` |
| [0x0funky/agent-sprite-forge](https://github.com/0x0funky/agent-sprite-forge) | `64fd0b57d3f2ae117ef0a95e4c2decc25b4c9dd2` | `skills/generate2dsprite skills/generate2dmap` |

### MCP：按 npm 发布版本安装

`gitHead` 来自对应版本的 npm 发布元数据；它用于追溯源码，实际安装仍固定 npm 版本。未发布该字段的包如实标注。

| 配置名 | npm 包及精确版本 | 源码 / npm `gitHead` |
|---|---|---|
| `figma-context` | `figma-developer-mcp@0.13.2` | [GLips/Figma-Context-MCP](https://github.com/GLips/Figma-Context-MCP)；该版本未发布 `gitHead` |
| `figma-talk` | `cursor-talk-to-figma-mcp@0.3.5` | [grab/cursor-talk-to-figma-mcp](https://github.com/grab/cursor-talk-to-figma-mcp)；`df7673e2ef80b398d368f1d06141c632e23a2df9` |
| `figma-console` | `figma-console-mcp@1.40.0` | [southleft/figma-console-mcp](https://github.com/southleft/figma-console-mcp)；`e4d5605e6108cd0b21a950f6f57fc189749bd2eb` |
| `image-generation` | `mcp-image@0.13.2` | [shinpr/mcp-image](https://github.com/shinpr/mcp-image)；`3c4c54676c5aff99e81d58b26a9e4f35c0dff08e` |

Talk to Figma 的**配套插件及 WebSocket 桥接源码**另固定为 `grab/cursor-talk-to-figma-mcp@ddd90f3a6d454ea0b2fc29f1b084f50fd062b880`。这是实际部署的两部分来源；不要把桥接源码提交误写成 npm 服务器的构建提交。

## 3. 目录和运行时

下文 `<USER_HOME>` 为当前用户主目录，`<CODEX_HOME>` 为现有 `CODEX_HOME` 环境变量的值，未设置时取 `<USER_HOME>/.codex`。`<TOOLS>` 默认取 `<CODEX_HOME>/tools/ai-design-20260905`，`<SKILLS>` 默认取 `<USER_HOME>/.agents/skills`。TOML 中的占位符必须替换为实际绝对路径，不能原样粘贴。

Codex 支持用户级 `~/.agents/skills`；安装后会发现新增技能，未刷新时重启。详见 [OpenAI Skills 文档](https://learn.chatgpt.com/docs/build-skills)。

Windows PowerShell 初始化变量；不改写系统的 `HOME` 或 `CODEX_HOME`：

```powershell
$userRoot = [Environment]::GetFolderPath('UserProfile')
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $userRoot '.codex' }
$skillRoot = Join-Path $userRoot '.agents/skills'
$toolRoot = Join-Path $codexRoot 'tools/ai-design-20260905'
$skillInstaller = Join-Path $codexRoot 'skills/.system/skill-installer/scripts/install-skill-from-github.py'
```

macOS/Linux 使用同样的目录布局；用 `python3` 代替下面的 `python`，以 `command -v node` 获取 Node 路径。对应变量可设为：

```sh
userRoot="$HOME"
codexRoot="${CODEX_HOME:-$HOME/.codex}"
skillRoot="$userRoot/.agents/skills"
toolRoot="$codexRoot/tools/ai-design-20260905"
skillInstaller="$codexRoot/skills/.system/skill-installer/scripts/install-skill-from-github.py"
```

运行时要求与原安装快照：

| 组件 | 要求及用途 | 原安装验证版本 |
|---|---|---|
| Python | `>=3.11`，覆盖 GPT CLI 要求；执行帮助命令和图片后处理 | `3.12.10` |
| Node.js | `>=22`，覆盖四个 MCP 的要求 | `24.19.0` |
| npm 或 pnpm | 安装固定版本的 MCP；任选一个 | 使用了 `pnpm 11.19.0`，原环境没有 npm |
| Bun | baoyu-image-gen 的 TypeScript 入口、Figma Talk 桥接 | `1.4.2` |
| GPT Image CLI | `gpt-image` Skill 的外部运行后端 | `0.2.0`，来自上表 GPT 仓库 commit |
| Python 图像/设计库 | Pillow、NumPy、ReportLab、fontTools | `12.3.0`、`2.5.2`、`5.0.1`、`4.64.0` |
| Python 检查库 | PyYAML；用于解析 Skill 元数据 | `6.0.3` |

使用所选 Python 环境执行安装与后续 Skill 命令；若使用虚拟环境，后续也应指定该环境的解释器。以下命令安装原验证版本：

```powershell
python -m pip install Pillow==12.3.0 numpy==2.5.2 reportlab==5.0.1 fonttools==4.64.0 PyYAML==6.0.3
python -m pip install "gpt-image-cli @ https://github.com/wuyoscar/GPT-Image2-Skill/archive/135d873e1a843db5f122a15ddda02bd2845d4d25.zip"
```

GPT CLI 会安装 `openai`、`python-dotenv` 等依赖；原验证的 `openai` 为 `3.8.0`。Skill 包装器先查本地/已安装 CLI，再尝试外部后备启动方式；安装 CLI 可避免运行时临时下载。

已有 Bun 可直接用绝对路径。缺少时可按 [Bun 官方安装说明](https://bun.sh/docs/installation)安装对应平台的 `1.4.2`，或使用 `npm install --global bun@1.4.2`。核验 `bun --version`。本机原安装使用独立 `bin/bun.exe`；其他用户无需复制该 Windows 可执行文件。

## 4. 安装 Skills 并迁移本机修正

先读取当前环境提供的 `$skill-installer` 说明，定位其官方 `scripts/install-skill-from-github.py`。上面的默认路径不存在时，以当前技能目录为准；不要依赖另一台电脑的缓存路径。通过帮助命令确认支持 `--repo --path --ref --dest`。

对第 2 节的六行分别执行一次以下形式的命令。示例一次安装两个 Anthropic Skills：

```powershell
python "$skillInstaller" --repo anthropics/skills --path skills/frontend-design skills/canvas-design --ref 41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f --dest "$skillRoot"
```

其他五行仅替换 `--repo`、`--path` 和 `--ref`。显式传 `--dest` 才会安装到本说明使用的 `~/.agents/skills`；安装器自身默认目标可能是 `~/.codex/skills`。目标 Skill 已存在时，先核实来源和本地修改；官方安装器会中止该目录的重复安装，保留可用安装并单独处理版本更新。命令成功后，每个 `<SKILLS>/<name>/SKILL.md` 应存在且含有效 `name`、`description`。

目录依赖检查：`canvas-design/canvas-fonts`、`ui-ux-pro-max/data` 和 `scripts`、`baoyu-design/agents`（包含 `lib`、`vendor`）、`built-in-skills`、`references`、`starter-components` 均需保留。精灵/地图 Skill 的脚本是可独立复制的，所需 Python 库已在前一节列明。`baoyu-image-gen/scripts/codex-imagegen` 已随 Skill 提供，无需另装仓库顶层的同名开发包。

### UI UX 的 Claude 路径修正

固定上游 Skill 中有 `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max`。Codex 安装需把它替换为**当前电脑**的 `<SKILLS>/ui-ux-pro-max`，保留上游副本。以下 Python 代码可保存到 `<TOOLS>/setup/adapt-ui-ux.py` 后执行；默认使用用户级 Skills，定制安装者应调整 `base`：

```python
from pathlib import Path
import os
base = Path.home() / '.agents' / 'skills'
codex = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
backup = codex / 'tools' / 'ai-design-20260905' / 'setup' / 'ui-ux-pro-max.upstream.md'
skill = base / 'ui-ux-pro-max' / 'SKILL.md'
text = skill.read_text(encoding='utf-8')
token = '${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max'
if token in text:
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        backup.write_text(text, encoding='utf-8')
    skill.write_text(text.replace(token, (base / 'ui-ux-pro-max').as_posix()), encoding='utf-8')
```

若从旧电脑复制的是已经修正过的 Skill，优先从固定 commit 重新取得上游版本后应用此修正，以免保留旧用户名。核验 Skill 文本中的搜索命令均指向本机，且 `scripts/search.py` 确实存在。

## 5. 安装 MCP 程序并配置 Codex

在 `<TOOLS>/node` 创建独立 npm 项目。下面两种包管理器方案任选一种；在该目录执行，保存生成的 lockfile 供后续复现。原安装使用 `--ignore-scripts`，已安装包的启动检查通过。此文档固定顶层版本；新机器的间接依赖仍以它生成的 lockfile 为准。

```sh
npm init -y
npm install --save-exact --ignore-scripts figma-developer-mcp@0.13.2 cursor-talk-to-figma-mcp@0.3.5 figma-console-mcp@1.40.0 mcp-image@0.13.2
```

仅有 pnpm 时：

```sh
pnpm init
pnpm add --save-exact --ignore-scripts figma-developer-mcp@0.13.2 cursor-talk-to-figma-mcp@0.3.5 figma-console-mcp@1.40.0 mcp-image@0.13.2
```

已有 `package.json` 时跳过 init。完成后核实四个包的 `package.json` 版本和下列 `dist` 入口。获取当前机器的 Node 绝对路径：PowerShell 使用 `(Get-Command node).Source`。原电脑使用 Codex 自带 Node，**不要把其个人缓存路径移植到别的电脑**。

备份 `<CODEX_HOME>/config.toml`，仅合并缺失的条目；同名条目已存在时比较后更新，保留其他 MCP。创建 `<TOOLS>/mcp-workdir` 和 `<CODEX_HOME>/generated_images/mcp-image`。以下模板中的 `<NODE>`、`<TOOLS>`、`<CODEX_HOME>` 全部替换为实际绝对路径；Windows TOML 建议使用 `/`。

```toml
[mcp_servers.figma-context]
command = "<NODE>"
args = ["<TOOLS>/node/node_modules/figma-developer-mcp/dist/bin.js", "--stdio"]
cwd = "<TOOLS>/mcp-workdir"
enabled = false
startup_timeout_sec = 60
tool_timeout_sec = 120
env_vars = ["FIGMA_API_KEY", "FIGMA_OAUTH_TOKEN"]

[mcp_servers.figma-talk]
command = "<NODE>"
args = ["<TOOLS>/node/node_modules/cursor-talk-to-figma-mcp/dist/server.js"]
cwd = "<TOOLS>/mcp-workdir"
enabled = false
startup_timeout_sec = 60
tool_timeout_sec = 120

[mcp_servers.figma-console]
command = "<NODE>"
args = ["<TOOLS>/node/node_modules/figma-console-mcp/dist/local.js"]
cwd = "<TOOLS>/mcp-workdir"
enabled = false
startup_timeout_sec = 60
tool_timeout_sec = 120
env_vars = ["FIGMA_ACCESS_TOKEN"]

[mcp_servers.image-generation]
command = "<NODE>"
args = ["<TOOLS>/node/node_modules/mcp-image/dist/index.js"]
cwd = "<TOOLS>/mcp-workdir"
enabled = false
startup_timeout_sec = 60
tool_timeout_sec = 120
env_vars = ["OPENAI_API_KEY", "GEMINI_API_KEY", "ARK_API_KEY", "IMAGE_PROVIDER"]

[mcp_servers.image-generation.env]
IMAGE_OUTPUT_DIR = "<CODEX_HOME>/generated_images/mcp-image"
```

`env_vars` 转发启动 Codex 时的环境变量；凭证由用户在本机环境中设置，文档、Git、验证日志只记录变量名。`enabled = false` 保留配置而不启动服务。字段解释见 [OpenAI MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)。

需要实际调用时，补齐下列条件，再仅启用所需条目并重启 Codex：

| MCP | 启用条件 |
|---|---|
| `figma-context` | `FIGMA_API_KEY` 或 `FIGMA_OAUTH_TOKEN`，并能访问目标 Figma 文件 |
| `figma-talk` | 第 6 节的桥接进程、Figma 插件和相同频道 |
| `figma-console` | 第 6 节的 Figma Desktop Bridge；部分 REST 功能另需 `FIGMA_ACCESS_TOKEN` |
| `image-generation` | OpenAI：`IMAGE_PROVIDER=openai` + `OPENAI_API_KEY`；Gemini：`IMAGE_PROVIDER=gemini` + `GEMINI_API_KEY`；Seedream：`IMAGE_PROVIDER=seedream` + `ARK_API_KEY` |

`mcp-image` 的 Seedream 路径使用 BytePlus/ModelArk AP 区域的凭证，详见其固定版本 README。`baoyu-image-gen` 的提供商配置与 MCP 配置分别生效；首次真实使用时读取其 `SKILL.md` 并设置提供商配置。宿主已有图像工具是否可用，需要在新环境现场确认。

## 6. Figma 插件与本地桥接

### Talk to Figma

在 `<TOOLS>/sources/talk-to-figma` 获取配套源码；已有目录先检查，命令用于首次安装：

```sh
git clone https://github.com/grab/cursor-talk-to-figma-mcp.git "<TOOLS>/sources/talk-to-figma"
git -C "<TOOLS>/sources/talk-to-figma" checkout --detach ddd90f3a6d454ea0b2fc29f1b084f50fd062b880
```

备份 `src/socket.ts` 后，在 `Bun.serve({ ... })` 的 `port: 3055` 旁添加有效的 `hostname: "127.0.0.1"`。若已有 hostname 属性则修改现有值，避免重复属性；保持监听本机。原安装也做了这一处修正。

以本机 Bun 启动并在使用期间保持运行：

```sh
bun "<TOOLS>/sources/talk-to-figma/src/socket.ts"
```

在 Figma 桌面版选择 **Plugins → Development → Import plugin from manifest**，导入 `<TOOLS>/sources/talk-to-figma/src/cursor_mcp_plugin/manifest.json`。在目标文件运行插件，连接本地 `3055` 服务，把显示的频道号交给 Codex，使 MCP 加入同一频道。单纯启动 MCP 不等于已经连接 Figma 文件。

### Figma Console

从同一菜单导入 `<TOOLS>/node/node_modules/figma-console-mcp/figma-desktop-bridge/manifest.json`。启用 `figma-console` 并重启 Codex，在目标文件运行 **Figma Desktop Bridge**，等待插件显示 READY。此 MCP 的本地模式会启动自己的桥接，无需 Talk to Figma 的 `socket.ts` 进程。

## 7. 验证、完成标准与交接记录

安装验收先做离线检查；图片生成和 Figma 文件编辑留给已明确要求的实际任务。

PowerShell 示例（使用第 3 节的变量）：

```powershell
python --version
node --version
bun --version
python -c "import PIL,numpy,reportlab,fontTools,yaml,openai,dotenv,gpt_image_cli; print('Python dependencies OK')"
python -B "$skillRoot/gpt-image/scripts/generate.py" --help
bun "$skillRoot/baoyu-image-gen/scripts/main.ts" --help
bun "$skillRoot/baoyu-image-gen/scripts/build-batch.ts" --help
python -B "$skillRoot/ui-ux-pro-max/scripts/search.py" gaming --domain product --json
python -B "$skillRoot/ui-ux-pro-max/scripts/search.py" cyberpunk --domain style --json
python -B "$skillRoot/generate2dsprite/scripts/generate2dsprite.py" --help
python -B "$skillRoot/generate2dmap/scripts/extract_prop_pack.py" --help
node "$skillRoot/baoyu-design/agents/build-preview.mjs" --help
```

接手 Codex 应逐项确认：

- 9 个 `SKILL.md` 的 YAML 是映射，`name` 与目录名一致，`description` 非空；字体、数据和脚本目录完整。
- 上述命令可运行，UI 查询有结果；精灵/地图的其他脚本也可运行 `--help`。静态设计 `.mjs` 通过 `node --check`。
- 四个 MCP 的包版本、启动文件、Node 路径和工作目录有效；合并后的 TOML 可解析，原有条目保留。
- 可选协议检查仅发送 MCP `initialize`、`notifications/initialized`、`tools/list`，随后正常关闭进程；只列工具，不调用工具。
- 分别报告“已安装”“通过离线检查”“已启用”“已连接真实服务”，列明缺少的凭证或插件步骤。

原安装验证结果：9 个 YAML 通过；Python 必需库导入通过；54 个字体存在且抽样解析成功；图片/精灵/地图/布局帮助命令通过；`gaming` 搜索命中 1 项，`cyberpunk` 命中 2 项。`baoyu-design` 的 6 个静态入口可加载，其中 `build-preview --help` 返回 0，其他无参入口按设计显示 usage 并返回 64。

`figma-talk`、`figma-console`、`image-generation` 的 MCP 初始化及工具列表分别返回 40、121、1 个工具；桥接在 `127.0.0.1:3055` 通过本地 HTTP 响应检查，测试后停止。`figma-context` 因缺少凭证仅核对入口和配置，真实连接未测。

`baoyu-design/agents/gen-pptx` 和 `gen-video` 的 `dist`、`node_modules` 未构建。导出 PPTX/视频属于可选后续工作，届时按各自 `package.json` 准备 Playwright、构建工具及视频编码依赖；不影响本次静态设计和游戏图片安装完成。

若命令需要 PATH 中的 Bun 或 Python Scripts 目录，按实际安装位置追加用户 PATH，保留原值。Windows 修改用户环境变量后完全退出并重开 Codex。原安装的 `bin` 中还提供了 `gpt-image` 启动器；新环境可直接用上述 Skill 包装器，无需复制旧启动器。

原电脑的审计记录位于 `<TOOLS>/setup/install-manifest.json`、`skill-verification.json`、`mcp-verification.json`、`bridge-verification.json`，本地说明位于 `<TOOLS>/安装说明.md`。这些个人文件不会随本仓库克隆；本文件已收录复现所需版本和步骤。新安装应在自己的 `<TOOLS>/setup` 保存来源提交、包版本、修改备份路径和验证结果，保留密钥值在用户环境中。
