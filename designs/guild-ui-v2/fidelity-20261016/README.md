# 帮会 PNG 原稿还原包

本包以 `designs/gameplay-ui/04-guild.png` 为视觉基准，使用内置 imagegen 清理动态文字与样例数据，保留金云边框、太极题牌、福灯、兔灯、帮徽及四个功能插画。主总览恢复左侧帮会资料／公告、右侧五行成员表及四张插画入口的结构。真实六页业务全部保留，原稿四页签扩为六个同款页签。

只在本目录暂存，未修改实际客户端，未启动 Unity。安装清单为 [install-manifest.json](install-manifest.json)，54 个文件：24 张 PNG 及 .meta、两份邮件外独立的帮会 runtime 源码及 .meta、一份现有帮会测试源码及 .meta。安装前核对三项源 SHA guard，若已变化则合并而不覆盖。

资源路径只新增 `Assets/Resources/UI/Ugui/GuildFidelity20261016/`；源码替换 `GuildWindow.cs`／`GuildUiArt.cs`，保留原 GUID。`.meta` 明确 Single、FullRect、无压缩、无 mipmap、Clamp 与逐图九宫格，未添加 AssetPostprocessor。其他 Social、Gameplay、Team、邮件及共享字体设置不变。

当前 public API、GuildPage 六页、GuildClient 和全部真实事件均保留；68 个原 GuildWindow 方法逐字相同，包括五个业务页、权限、申请审批、捐献、商店、活动、升级、同道历练邀请与过期处理。仅主窗构造、身份资料、已入帮总览、呈现布局／资源路由调整；保留未入帮总览原逻辑。详情见 [staged-code-manifest.json](staged-code-manifest.json) 和 [包审计](qa/package-audit.json)。

原稿的成员等级、周贡献、建设目标、签到和驻地操作没有对应当前 GuildMember／GuildInfo 业务字段，因此没有烘焙或虚构样例数据：表格显示真实职位、累计帮贡和在线状态；进度条明确标为“升级资金”，显示资金／UpgradeCostFunds；页脚保留可用／累计帮贡与真实刷新。四插画入口分别打开捐献、排行、活动、商店；“查看同道”打开已有成员页。头像是原稿默认头像，数据协议未提供实际角色外观身份。

当前 451 份 runtime 源替换后 [离线编译通过](qa/compile-result.json)，0 error；暂存测试源码也 [编译通过](qa/test-compile-result.json)。原业务断言保留，仅将旧整窗 Sprite 断言改为新同源 Sprite，以及让行高核验覆盖正文与 SimKai 两种实际字体。这里没有执行 Unity 测试，不把编译通过视为游戏内视觉验收通过。

安装后可复用现有 `GuildUiVerification.CaptureAll`，它使用隔离附加场景与本地 fixture，不保存用户场景、不连接真实服务端。将 `GuildUiVerification.OutputDirectory` 指向本包 `qa/unity` 后运行，覆盖 2560×1080、1920×1080 的 26 张六页／弹窗／空态截图。入口记录见 [capture-request.json](qa/capture-request.json)。还需主任务逐页检查文字基线、长帮名、按钮、弹窗及真实游戏入口。

图片与记录：

- [guild-controls-clean.png](art/guild-controls-clean.png)／[逐图记录](art/guild-controls-clean.png.generation.json)：原稿无字控件与绿色填充来源。
- [guild-empty-shell.png](art/guild-empty-shell.png)／[逐图记录](art/guild-empty-shell.png.generation.json)：最终空外框、太极牌、灯与兔子。
- [guild-progress-empty.png](art/guild-progress-empty.png)／[逐图记录](art/guild-progress-empty.png.generation.json)：真实动态升级资金使用的空轨道来源。
- [24 张切片清单](sprite-manifest.json)：每张 PNG 旁都有来源、SHA 和裁切记录；默认头像与自身勾记追溯已确认 PNG 原稿，不伪称新生图。

本批官方核对仍支持 Images 2.5／Sunburst 与最高质量目标，见 [产品公告](https://openai.com/index/introducing-chatgpt-images-2-5/)、[模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)、[Images API](https://developers.openai.com/api/reference/resources/images/methods/generate)。实际使用内置工具，没有 model／quality 参数，所有新增 AI 图的实际具体版本、质量均为“未确认”；配置目标保留在每张记录快照，不将目标当作已返回参数。

重建顺序：`extract_guild_sprites.py`、`stage_guild_code.py`、`stage_guild_tests.py`、`compile-staged.ps1`、`compile-staged-tests.ps1`、`package_guild.py`。这些步骤只写当前包；提取脚本需要上述当前母图及已确认原稿。
