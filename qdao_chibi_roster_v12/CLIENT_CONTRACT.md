# 游戏升级契约（当前接入状态与后续门禁）

2026-09-17 03:28 UTC 完成状态：八位道家 Q 版角色的造型、自然步态和游戏素材接入已完成。每人 64 张真实行走、8 张独立站立、1 张肖像及 8 张行走条带，每人 81 张、八人共 648 张 PNG；全部按对齐 v3 发布，预览与游戏逐文件 SHA 一致。独立 Unity 副本的 127/127 EditMode、8/8 PlayMode 通过，八人主城外观已逐一视审。测试结论对应 03:18 UTC 保存的代码与资源快照；内部验收不代表用户已经认可美术。

八位角色为灯穗小使、年轻吕洞宾、狮鼓护卫、桂香药婆、墨鸢游侠、月兔机关师、何仙姑、韩湘子，均已启用 V12。吕洞宾、何仙姑、韩湘子保留各自八仙身份与器物，造型按道家 Q 版制作。

## 本轮八人交付与验证（2026-09-17 UTC）

- 最终美术源：`candidate-stable-body/<角色ID>`；何仙姑使用 `candidate-natural-body/29_he_xiangu`，为素色道袍与长裤版本。原始生成图、来源记录和此前版本保留。
- 运行证据：[summary.json](../../mmorpg-client/Docs/ArtEvidence/v12-stable-roster/eight-natural-current-code-20260916-retry/summary.json)。394 个 C#、648 张 PNG 与 8 个启用文件在启动前逐一匹配。运行期间其他任务修改了 6 个社交/地图相关 C#，因此结论针对该保存快照。原打开 Unity 场景未操作。
- 首轮同一检查因测试超时未完成；只为原有测试增加 `[Timeout(600000)]`，断言未改。重试的 127 项 EditMode 与 8 项 PlayMode 均通过，历史失败记录保留。
- [预览源校验](review/site/preview-source-verification.json)与[浏览器验收](review/browser-qc/review-pages-result.json)通过：8 人 × 8 方向共 64 组，没有禁用角色；逐帧、循环、独立站立、半速、390px 移动端均可用。一次图片请求失败后重新选择同方向的恢复检查也通过。
- [八人新版总览](review/site/roster-final.jpg)、[新旧肖像对照](review/site/portrait-comparison.jpg)、[本地交互预览](http://127.0.0.1:8871/)。恢复本地服务可运行 `python review/serve_final_preview.py`，只提供 `review/site` 目录。

保留角色 ID、职业/性别映射、选角和现有角色存档。每位角色可独立从 V11 四帧升级到 V12 八帧，未完成角色继续使用 V11，避免制作期间出现缺帧或站立空图。

- V12 完整角色导入 `Assets/Resources/World/Characters/QdaoRosterV12/<ID>/`，PNG 路径与本包一致；portrait.png 默认沿用 V11，也支持本轮明确授权的新道家服饰肖像。
- 运行时每方向从 `walk/<DIR>/01` 到 `08` 读取独立动作纹理，`idle/<DIR>` 读取独立站立纹理；导出条带只供兼容/审阅。
- 全套资源验收后最后发布每角色 `appearance.json`：`version:12, frameCount:8, frameDurationMs:60, dedicatedIdle:true, status:passed, visualReview:passed`，并包含角色 ID、接触帧与三份验收 SHA-256。完整 metadata 及全部纹理存在时才选 V12，否则保持同角色 V11。游戏不能因单张 V12 缺失而直接换成另一人物。
- 现有 QdaoCharacterCatalog.Definition 已暴露每角色资源版本、FrameCount、FramesPerSecond、HasDedicatedIdle、FrameResourcePath 和 IdleResourcePath。肖像缓存按身份与版本隔离，完整 V12 可使用明确授权的新肖像；不完整时保留同角色 V11 肖像。
- QdaoBoySpriteAnimator 已补齐目录角色专用 idle，并按完整资源集处理动态帧数与速度。现有旧角色的 IdleFrames 接触相位表不能直接沿用到 V12；V12 以新作者指定的 0 或 4 号接触姿势作停走交接，发布脚本默认 0。
- 更新缓存键包含资源版本，避免同 ID 从 V11 升级后残留四帧缓存。保留脚底、像素/世界单位、运动距离驱动、阴影、渲染层级与方向迟滞行为。
- 验证：V11/V12 混用、八帧八方向、独立站立、完整/缺失/损坏资源回退、停走与换向、外观切换时不移动实体/重复阴影，以及在真实主城中播放新样板。

客户端目录、世界动画器和战斗外观加载已实现版本选择与完整性回退。当前逐角色完成整套美术与资源验收后发布；本轮八位已全部接入。运行资源完整性门禁和内部 passed 标记不能替代用户对造型、步态及脸型比例的确认。

历史静态编译记录：早期使用Unity 6000.6 Roslyn隔离编译角色生产代码及Tianyong/Battle/PlayMode三个测试程序集，0错误，输出在E:/work/tmp/qdao-v12-csharp-check。当时因并行CityTravelUiRoot的4个缺失地图API错误，隔离检查未包含该文件及CityTravelWindowTests；这不是当前完整工程状态判断，也不代表游戏或美术验收完成。

历史运行记录：`E:/work/mmorpg-client/Docs/ArtEvidence/v12-three-immortals/`中的121/121 EditMode、7/7 PlayMode仅对应24/29/30三位V12；`v12-four-approved/`中的121/121和7/7对应2026-09-13 14:13–14:16 UTC的四位V12定向回归。不得把历史结果作为停步修复后的新全量测试。

历史停步修复定向运行记录：`E:/work/mmorpg-client/Docs/ArtEvidence/v12-stop-fix/playmode.xml`为8/8 PlayMode Passed、0失败（2026-09-13 15:04:04–15:04:12 UTC），包含`V12_StoppingAtDifferentPhases_ShowsDirectionIdleOnTheNextFrame`，验证停步下一帧显示该方向独立idle。这个8/8结果不代表本次重跑了历史121项EditMode，也不能替代用户的道家风格、走路自然度和脸型大小验收。

- 对齐版本2：512画布的根点(256,471)由上身水平轴和脚底高度定义，横向不再追随每帧支撑脚的脚掌中心。最终图像仅整帧平移，Sprite pivot仍用居中X/既定脚底Y；manifest alignment.version=2与独立验证必须通过后发布。详见README与alignment-validation/regression.json。


## 2026-09-14：吕洞宾稳定定位与完整接入

对齐v3以同方向独立idle确定固定头部ROI和头顶Y；所有72帧共用一个scale，每帧只整数平移。世界根点仍为(256,471)，但步行时不同远近脚可围绕根点变化，不再把最低鞋像素强行锁死。独立验收按源RGBA重构平移结果，拒绝错位、裁断、改像素及错误参考元数据。旧角色v2仍按原规则验证。

本次修正了SE06腿部遮挡和摆臂、NE头型，以及S/N/E/SE独立站立比例。追加边缘清理显式使用4px边缘及12px颜色参考；全部72帧alpha、G通道、位置和受保护红色不变。默认去色仍2px/6px，旧默认输出54次真实帧比较逐像素一致；细发梢中无可靠参考的像素未强行改色。

最终源：`E:/work/image/qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin`。81PNG已接入，alignmentVersion=3；导入前资源留存在 `Docs/ArtEvidence/v12-natural-lu/before-import/`。新运行结果是独立副本127/127 EditMode和8/8 PlayMode，副本81PNG、启用记录及357个C#文件在启动前与正式项目一致。真实城市图为 `Docs/ArtEvidence/v12-natural-lu/tianyong-24_lu_dongbin.png`。这些是离线游戏测试，不是整批8位角色的美术完成声明。
