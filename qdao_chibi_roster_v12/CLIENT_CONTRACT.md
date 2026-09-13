# 游戏升级契约（实现准备，待样板验收后启用）

保留角色 ID、职业/性别映射、选角和现有角色存档。每位角色可独立从 V11 四帧升级到 V12 八帧，未完成角色继续使用 V11，避免制作期间出现缺帧或站立空图。

- V12 完整角色导入 `Assets/Resources/World/Characters/QdaoRosterV12/<ID>/`，PNG 路径与本包一致；portrait.png 默认沿用 V11，也支持本轮明确授权的新道家服饰肖像。
- 运行时每方向从 `walk/<DIR>/01` 到 `08` 读取独立动作纹理，`idle/<DIR>` 读取独立站立纹理；导出条带只供兼容/审阅。
- 全套资源验收后最后发布每角色 `appearance.json`：`version:12, frameCount:8, frameDurationMs:60, dedicatedIdle:true, status:passed, visualReview:passed`，并包含角色 ID、接触帧与三份验收 SHA-256。完整 metadata 及全部纹理存在时才选 V12，否则保持同角色 V11。游戏不能因单张 V12 缺失而直接换成另一人物。
- 现有 QdaoCharacterCatalog.Definition 已暴露每角色资源版本、FrameCount、FramesPerSecond、HasDedicatedIdle、FrameResourcePath 和 IdleResourcePath。肖像缓存按身份与版本隔离，完整 V12 可使用明确授权的新肖像；不完整时保留同角色 V11 肖像。
- QdaoBoySpriteAnimator 已补齐目录角色专用 idle，并按完整资源集处理动态帧数与速度。现有旧角色的 IdleFrames 接触相位表不能直接沿用到 V12；V12 以新作者指定的 0 或 4 号接触姿势作停走交接，发布脚本默认 0。
- 更新缓存键包含资源版本，避免同 ID 从 V11 升级后残留四帧缓存。保留脚底、像素/世界单位、运动距离驱动、阴影、渲染层级与方向迟滞行为。
- 验证：V11/V12 混用、八帧八方向、独立站立、完整/缺失/损坏资源回退、停走与换向、外观切换时不移动实体/重复阴影，以及在真实主城中播放新样板。

客户端目录、世界动画器和战斗外观加载已实现版本选择与完整性回退；测试已适配混用，尚待 Unity 执行。当前未发布 V12 图片，只有样板完整通过视觉验收后才能启用。

静态编译：配套 Unity 6000.6 Roslyn 已编译通过角色生产代码和 Tianyong/Battle/PlayMode 三个测试程序集（0错误），输出位于 E:/work/tmp/qdao-v12-csharp-check。完整工程另有并行 CityTravelUiRoot 的4个缺失地图API错误；此次隔离检查未编译该文件及其 CityTravelWindowTests，也未修改它们。尚未启动 Unity 或执行运行时测试，不能据静态编译声明游戏验收完成。
