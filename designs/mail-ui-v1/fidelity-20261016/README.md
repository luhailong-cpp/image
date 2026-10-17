# 邮件原稿还原包

电脑重启后已继续核对现有交付。保留原来的 25 张正式 Sprite、两份邮件专用源码与 .meta，没有重新生图，没有改实际客户端，没有改共享 Social／Gameplay／Team 代码。

安装清单为 [install-manifest.json](install-manifest.json)：54 个文件，目标仅 `Assets/Resources/UI/Ugui/MailV1Fidelity/` 及 `Assets/Scripts/UI/Ugui/Mail/MailWindow.cs`、`MailFidelityArt.cs`。覆盖前必须核对清单中的 `sha256Before`；本次原客户端 `MailWindow.cs` 仍为 `5cb5aba5e5fd47a43bf529e7b6b837c868766bc6a388d60e1c3ebe3d91c97c73`。若不同，应合并变化，不覆盖新业务代码。

按清单复制 `client/` 下列出的文件即可安装；生成记录、提示词和 art 母图留在素材包，不复制进 Assets。资源自带 Single、FullRect、无压缩、无 mipmap、Clamp 的明确 .meta，不添加 AssetPostprocessor。`MailWindow.cs.meta` 保留原客户端 GUID。MailFidelityArt 只用于邮件，不改共享字体设置。

最新静态核验见 [resume-package-audit.json](qa/resume-package-audit.json)，结果通过：54 个载荷 SHA、25 张 PNG 解码／尺寸／来源记录、唯一 Sprite GUID、导入参数、固定素材引用和现有字体依赖完整。`Show`、`Hide`、`Back`、`ResetSession`、`Tick`、删除／清理确认、活动与弹窗方法、`Dispose` 的业务实现与原客户端逐字相同；MailUiState 不改。

最新 [compile-result.json](qa/compile-result.json) 使用当前客户端共 451 份 runtime 源，替换邮件源码后编译 exit 0，0 条 error。保留的 warning 来自既有 Protobuf/netstandard 引用和 App 开发脚本；本包未改这些文件。

视觉依据仍为上级 `01-mail-event.png`／`02-mail-system.png`。1932×814 无字纸面与原稿边饰、夜景按统一比例适配 2560×1080；分类、列表、附件和操作分别使用独立 Sprite；标题、正文、寄件人、时间、计数及按钮状态由原生控件呈现。已检查底板、空行、空附件槽与横幅，没有演示正文、日期、奖励数量残留。未读信封透明区域虽保留原 RGB，红点 alpha=0；运行时只由状态绘制一次红点。

尚需主任务在实际 Unity 编辑器中安装并截图验收。本包不把外部 C# 编译视为 Unity 导入、运行或逐像素还原通过。长信保留正文滚动，现有 reward IconKey 及其他活动 BannerKey 保留旧资源回退，不注入样例邮件或虚构奖励对应关系。活动横幅和动文字的字距、基线、真实数据长度，需在运行中继续对齐。

复核顺序：先执行 `compile-staged.ps1`，再用可用 Python 执行 `package_mail.py`、`verify_package.py`。后两步只更新本包清单与核验报告，不写客户端。
