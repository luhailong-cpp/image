# 装备右栏与验收兼容补丁

本补丁只暂存，不写客户端、不启动 Unity、不改图片。最小安装使用 `equipment-compat-install-manifest.json`（6 份 C# 与对应原 GUID `.meta`），安装前核对 `equipment-compat-sourceguard.json` 的最新客户端 SHA。

01 期望属性截图中，原验收 `Find` 同时匹配了隐藏的窗口 wish 和独立 wish；03 独立装备卡片随后又会与当前游戏右栏的按钮同时激活。验收现只匹配 `activeInHierarchy` 后仍用 `Single`，截图前主动断言装备按钮名没有两个可见实例；独立卡片 fixture 打开前隐藏 GameplayWindow，避免用 `First` 掩盖双活。EquipmentIntegration 与 Forge 验收也保留唯一匹配；少数明确检查生命周期隐藏节点的地方单独查找或提前保存引用。

正式运行时只改 `RenderNativeItem`：右栏加明确 `GameplayEquipmentDetails` 容器，显示真实“已穿戴/未穿戴”，要求行保留 `TooltipLevel/TooltipClass` 语义字段名，实际属性/宝石行按原色和顺序单列。长词条与说明按 TMP 实际测量换行并纳入固定滚动区域，动作按钮位置保持原稿坐标。隐藏旧 EquipTooltip 保留，游戏右栏不调用它的 Show。穿上、卸下、更多/养成、分享的现有回调逐项保持；不新增假装备数据或新 public API。

当前 Scripts 没有 `ShowEquippedItem` / `ShowBagItem` 方法；真实入口是 `GameplayUiRoot.OpenEquipment` 调用 `ShowEquipment`、背包格与“已穿戴”分类选中以及 `OpenEquipmentForge`。它们继续使用同一 `_selectedItem` 和当前两份快照，穿脱后按实例 ID 跟随。没有为套装造独立接口；装备种类仍由服务器字段和既有 EquipDisplay 处理。

原 EquipWindowTests 全部方法保留，只有旧 tooltip 层级、常驻装备列、打勾图片和固定页码几何查询改为原稿右栏与真实分类/滚动控件。装备栏查询短暂切入“已穿戴”后回到物品页，不发读取请求、不改选择记忆；点击穿戴项也通过真实原生按钮。RPC、服务器拒绝原因、忙碌互斥、超时后双快照重同步、会话代次、分享副本和养成权限断言保留，并新增可见动作唯一性用例。Forge 测试仅改控件查询与详情根节点，业务体不改。`equipment-compat-test-audit.json` 记录原方法和协议断言保留情况。

离线复编记录在 `equipment-compat-compile.json`：当前全部运行时源（只替换暂存 partial）、Battle 测试源（只替换这两份测试）、三份 Editor 验收脚本。语法编译不代表 Unity 测试已运行。父任务安装后执行 EquipWindowTests、EquipForgeWindowTests，以及 EquipmentUiVerification / EquipmentIntegrationVerification / EquipmentForgeUiVerification 三套 CaptureAll，再核对实际游戏右栏与弹窗。
