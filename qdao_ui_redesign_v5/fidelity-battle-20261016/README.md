# 战斗 UI 呈现还原（2026-10-17）

`installation-manifest.json` 冻结 7 项：5 个原有战斗视图源码、局部 `BattleFidelityArt.cs` 和它的标准 MonoImporter meta。每个原文件都有当前客户端 SHA guard；不得覆盖 guard 不同的并行改动。没有修改 `BattleUiStyle`、`BattleUiWidgets` 或其他模块的公共颜色。

现有原生截图显示战斗场景已经使用最终 05 场景图；进入战斗使用最终 06 插画。两图文件和 RGBA 像素均与客户端完全相同，不重新生成。当前云气与最终云气轮廓、尺寸、alpha 完全相同，RGB 尚有差异（686734 像素、通道最大20）；本次不改过场资产，差异记入 `qa/source-and-asset-audit.json`，由主线程统一判定过场颜色。

本次把旧棕色回合卡、人物队列卡、圆轮按钮和暗色排队／观战／结算窗改为现有 `AttributesPaintedV2` 的米白、玉绿、鎏金控件材质。原始31张同源控件不变，无新图、无 AI 编辑、无全局 AssetPostprocessor。数字、冷却、状态、技能、人物肖像仍来自真实客户端数据；不烘焙预览角色。

`qa/source-and-asset-audit.json` 验证剥离呈现 hook 和3处文本颜色后5个原文件与原源码完全一致。回合、目标、自动、逃跑、队列容量、观战、结果回调、连接事务、点击区域与动画时序均保留。

`compile-staged.ps1` 使用已安装 Unity 引用进行离线 Roslyn 编译，不启动 Unity。`qa/compile-report.json` 为编译证据。安装后用现有 `ClientBattleUiQaCapture.CaptureAll` 断网捕获4张原生页面；不以编译代替渲染验收。该工具创建临时附加场景并恢复已有场景，仍由主线程统一运行。重点验收回合标题、命令文字、冷却文字、队友 HP/MP 与排队／观战状态的可读性，以及结算淡入后的奖励与按钮。
