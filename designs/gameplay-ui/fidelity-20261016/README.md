# 背包、任务、活动原稿还原暂存包\n\n2026-10-17 装备验收适配已补齐，使用 [装备最小补丁](EQUIPMENT_COMPAT.md) 和 equipment-compat-install-manifest.json；该记录覆盖下文初次暂存时的装备测试待适配说明。

只在本目录暂存，尚未写入客户端、启动 Unity 或运行 Unity 测试。原稿为 `../01-quests.png`、`../02-inventory.png`、`../03-activities.png`，1931×814；重启前每张一次内置清理所得唯一在制皮肤为 `assets/*-clean-skin.png`，实际返回 1932×814。逐图记录明确区分当前配置目标、未知提交/返回型号与质量、文件时间证据，未再次生图。

`install-manifest.json` 列出完整安装文件与目标当前 SHA；安装前按 `sourceguard.json` 核对原 `GameplayWindow.cs`、`GameplayWindowTests.cs` 和 `GameplayUiArt.cs`。`staged/` 路径相对于客户端根目录。原 C# 和测试文件 `.meta` 保留原 GUID。新图片使用 Single/FullRect/Uncompressed/100 PPU、无 mipmap、4096 上限；没有新 AssetPostprocessor。客户端现存 `QdaoUiTextureQuality` 可能把新 UI 贴图的上限调整至 16384，这是既有全局策略，不会降采样这些小于 4096 的图片。

运行时三页分别用专用画面和从同源皮肤提取的控件，原生 1932×814 坐标整页单比例缩放。烘焙卡片/网格已清除，由实际快照重建：背包五列滚动，已穿戴独立分类包括服务器空槽；任务列表、所有目标、长文可滚动；活动卡横向滚动。任务原四种筛选均保留在同款小下拉中。所有 public API 及原装备穿脱、分享、更多/养成、任务追踪/接取/领奖、活动接任务/打开任务事件仍由原状态与业务回调驱动。正式代码没有构造视觉样例数据，活动只使用真实 `IconKey`；协议没有奖励物品明细时不填原图示例奖励。

离线验证使用 `compile-check.rsp`，只替换原 GameplayWindow 源路径并加入新 partial/fit 源，不修改客户端。编译器为 .NET SDK 10.0.400 Roslyn。`compile-validation.json` 与 `package-validation.json` 记录结果；这不代表 Unity 运行或视觉验收。

测试暂存保留原 `GameplayWindowTests` 业务语义用例和其既有测试 fixture，三项旧分页用例改成真实 ScrollRect 长列表/目标/活动可达断言，空页检查改成空滚动内容，并新增未接/进行中/已完成的过滤、追踪、权限断言。测试 fixture 只存在测试程序集，不进入正式 State。旧 `EquipWindowTests`/`EquipForgeWindowTests` 中依赖旧 tooltip 层级、常驻装备列和固定装备分页的断言需要后续适配：本次详情已按原稿改为右栏，装备列改为“已穿戴”分类；其穿脱/分享/养成权限语义仍须运行回归。

安装后标准截图入口是客户端现有 `GameplayUiVerification.OutputDirectory = <验收目录>; GameplayUiVerification.CaptureAll();`，或菜单 `MMORPG/UI/Capture gameplay screens`。现有方法在独立 additive Edit Mode 场景调用正式窗口，输出 2560×1080 与 1920×1080 的 13 种状态各一张，共 26 张。截图使用该方法原有的明确标注 fixture，不建立账号或网络，不替换在线 State。再补实际编辑器游戏视图的三页操作检查，确认过滤无残影、长列表滚动和各按钮权限。截图成品核验后按项目规则清理验收过程图。

可复现本目录资产/暂存代码/测试：依次执行 `build_assets.py`、`prepare_code.py`、`prepare_tests.py`、`verify_package.py`。这些脚本均不写客户端，不调用生图。
