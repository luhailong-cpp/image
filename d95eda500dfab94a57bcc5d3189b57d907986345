# GPT Image 2.5 规则迁移验收

> 2026-09-18 后续集中配置：现行设置只有 [config/image-generation.json](../config/image-generation.json)，各 MD、技能和已适配 CLI 引用它；使用方式见[执行策略](IMAGE_MODEL_POLICY.md)。下文迁移数值与验证结果仅描述首轮修改。

日期：2026-09-16。

首轮迁移将项目及本机绘图规则默认统一为 **GPT Image 2.5 Sunburst**（`gpt-image-2.5-sunburst`），最高质量参数为 `max`。优先使用宿主内置 `image_gen`；参数未开放时如实记录目标与实际工具能力，规则升级不代表能够强制切换宿主后端。单独计费 API/CLI 保留用户明确授权要求。

## 修改范围

首轮共修改 44 个已有文件，另新增本验收记录。当前生图选择以 [最新模型策略](IMAGE_MODEL_POLICY.md) 为准；下文记录首次迁移的验证基线。

| 范围 | 文件数 | 内容 |
|---|---:|---|
| 项目规则与交接 | 6 | AGENTS、README、移机说明、UI规范、节庆规范、人物设计简报 |
| 系统 imagegen 技能 | 8 | 规则、CLI默认、参数校验、帮助及提示词示例 |
| 用户 gpt-image 与实际CLI | 14 | 技能、launcher、已安装Python包、源代码/build副本和SDK示例 |
| 用户 baoyu-image-gen | 16 | OpenAI默认/质量映射、Codex提示与缓存、Azure部署校验、配置与测试 |

主规则见 [AGENTS.md](../AGENTS.md)。用户目录技能和实际 CLI 修改仅保存在当前电脑；移机或重新安装按 [工具说明](AI_DESIGN_TOOLS_SETUP.md#4-安装-skills-并迁移本机修正)复核本地修正。

## 验证

- 系统 imagegen：29 项离线 dry-run 检查通过。
- gpt-image：25 项离线检查通过，覆盖默认、显式覆盖、generate/edit及launcher。
- baoyu-image-gen：37 项CLI/提供商测试、3项缓存检查通过。
- 三个技能的格式验证通过；已修改文件的UTF-8编码与最终哈希已核对。
- 未进行真实生图或付费API调用。

已复查项目隐藏规则、父级规则、用户技能、插件技能、Codex模型/指令配置、自动任务、绘图模型环境覆盖及EXTEND配置位置。未发现剩余有效旧模型默认或推荐。

## 保留项

历史图片的真实模型来源、已完成批次的记录脚本、历史画廊提示词与引用、真实上游仓库名/URL、迁移前备份，以及用户显式选择旧模型时的兼容代码继续保留；它们不作为新的默认规则。Azure使用实际部署名，不把未确认的服务别名写成可调用型号。

## 本机审计材料

详细文件路径及哈希：[全部修改文件](../.work/image25-migration/all-changed-files.json)。

验证记录：[系统imagegen](../.work/image25-migration/system-imagegen-validation/validation.json)、[gpt-image](../.work/image25-migration/user-skills-validation.json)、[baoyu-image-gen](../.work/image25-migration/baoyu-image-gen-validation.json)。`.work`为本机忽略目录，不随Git同步。

## 官方依据

- [GPT Image 2.5 Sunburst 模型](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)
- [图像生成参数](https://developers.openai.com/api/docs/guides/image-generation)
- [图像编辑参数](https://developers.openai.com/api/reference/python/resources/images/methods/edit)

## 后续策略升级：每个任务跟随最新版

用户随后要求未来使用最新版。现按 [最新模型策略](IMAGE_MODEL_POLICY.md)执行每任务官方核对、真实参数选择与禁止静默降级；2.5/max 改为最近验证基线。六处项目规则与三个技能入口已同步，原迁移验证仍保留为当时基线的检查结果。本次新增规则修改只进行文本、链接与技能格式检查，不把它表述为内置后端已升级。项目 Git 提交包含项目规则和交接文档；用户目录的技能及CLI修正保存在本机，不属于本项目的 Git 跟踪范围。

## 2026-09-18：统一配置与官方开放状态更正

OpenAI 发布公告确认 Images 2.5 面向 ChatGPT、ChatGPT Work 和 Codex 开放。此前仅凭旧帮助页阻塞内置生图的判断已更正；内置仍优先，实际是否传入模型／质量参数按工具能力记录。

现行默认只保存在 [config/image-generation.json](../config/image-generation.json)。项目规则、当前交接、六个生图相关技能入口和本机 Python/TypeScript CLI 读取同一设置；用户目录的注册 JSON 只保存该文件路径。后续模型升级无需逐个改 MD 或技能中的型号常量。

本次验证使用临时配置和离线替身检查实际生成／编辑请求、默认优先级、显式覆盖及错误处理；没有真实生图或付费 API 调用。用户目录技能／CLI 不在项目 Git 内，迁移时须保留其配置读取适配。

历史图片、原提示词、C2PA、receipt 和已完成批次的原始模型／质量记录保持可追溯；可复用脚本生成的新规则改为配置引用，来源信息从对应 receipt 取得，未知时明确记录未知。
