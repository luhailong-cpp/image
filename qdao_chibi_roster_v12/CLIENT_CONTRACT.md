# 游戏升级契约（当前接入状态与后续门禁）

2026-09-13 当前状态：用户已明确指出道家造型、走路方向与姿势、脸型与大小三项均不符合预期。后续批量制作与发布暂停，目前仅制作吕洞宾自然走路样板，待用户复核后再决定是否扩展。内部数值/视觉记录或运行测试通过，不等于用户美术验收通过；25狮鼓护卫虽内部标记passed，仍未接入，也未获得本轮风格认可。

游戏当前实际接入V12的仅有24吕洞宾、26桂香药婆、29何仙姑、30韩湘子；23灯穗小使、25狮鼓护卫、27墨鸢游侠、28月兔机关师仍使用同ID的V11。已接入的四位也在本次造型、步态和比例复核范围内，不能把已接入状态表述为用户已认可。

保留角色 ID、职业/性别映射、选角和现有角色存档。每位角色可独立从 V11 四帧升级到 V12 八帧，未完成角色继续使用 V11，避免制作期间出现缺帧或站立空图。

- V12 完整角色导入 `Assets/Resources/World/Characters/QdaoRosterV12/<ID>/`，PNG 路径与本包一致；portrait.png 默认沿用 V11，也支持本轮明确授权的新道家服饰肖像。
- 运行时每方向从 `walk/<DIR>/01` 到 `08` 读取独立动作纹理，`idle/<DIR>` 读取独立站立纹理；导出条带只供兼容/审阅。
- 全套资源验收后最后发布每角色 `appearance.json`：`version:12, frameCount:8, frameDurationMs:60, dedicatedIdle:true, status:passed, visualReview:passed`，并包含角色 ID、接触帧与三份验收 SHA-256。完整 metadata 及全部纹理存在时才选 V12，否则保持同角色 V11。游戏不能因单张 V12 缺失而直接换成另一人物。
- 现有 QdaoCharacterCatalog.Definition 已暴露每角色资源版本、FrameCount、FramesPerSecond、HasDedicatedIdle、FrameResourcePath 和 IdleResourcePath。肖像缓存按身份与版本隔离，完整 V12 可使用明确授权的新肖像；不完整时保留同角色 V11 肖像。
- QdaoBoySpriteAnimator 已补齐目录角色专用 idle，并按完整资源集处理动态帧数与速度。现有旧角色的 IdleFrames 接触相位表不能直接沿用到 V12；V12 以新作者指定的 0 或 4 号接触姿势作停走交接，发布脚本默认 0。
- 更新缓存键包含资源版本，避免同 ID 从 V11 升级后残留四帧缓存。保留脚底、像素/世界单位、运动距离驱动、阴影、渲染层级与方向迟滞行为。
- 验证：V11/V12 混用、八帧八方向、独立站立、完整/缺失/损坏资源回退、停走与换向、外观切换时不移动实体/重复阴影，以及在真实主城中播放新样板。

客户端目录、世界动画器和战斗外观加载已实现版本选择与完整性回退，并已有上述四位V12接入。当前只做吕洞宾自然走路样板；其余角色保持现有版本，暂停后续批量发布。运行资源完整性门禁和内部passed标记不能替代用户对造型、步态及脸型比例的确认。

历史静态编译记录：早期使用Unity 6000.6 Roslyn隔离编译角色生产代码及Tianyong/Battle/PlayMode三个测试程序集，0错误，输出在E:/work/tmp/qdao-v12-csharp-check。当时因并行CityTravelUiRoot的4个缺失地图API错误，隔离检查未包含该文件及CityTravelWindowTests；这不是当前完整工程状态判断，也不代表游戏或美术验收完成。

历史运行记录：`E:/work/mmorpg-client/Docs/ArtEvidence/v12-three-immortals/`中的121/121 EditMode、7/7 PlayMode仅对应24/29/30三位V12；`v12-four-approved/`中的121/121和7/7对应2026-09-13 14:13–14:16 UTC的四位V12定向回归。不得把历史结果作为停步修复后的新全量测试。

当前停步修复定向运行记录：`E:/work/mmorpg-client/Docs/ArtEvidence/v12-stop-fix/playmode.xml`为8/8 PlayMode Passed、0失败（2026-09-13 15:04:04–15:04:12 UTC），包含`V12_StoppingAtDifferentPhases_ShowsDirectionIdleOnTheNextFrame`，验证停步下一帧显示该方向独立idle。这个8/8结果不代表本次重跑了历史121项EditMode，也不能替代用户的道家风格、走路自然度和脸型大小验收。

- 对齐版本2：512画布的根点(256,471)由上身水平轴和脚底高度定义，横向不再追随每帧支撑脚的脚掌中心。最终图像仅整帧平移，Sprite pivot仍用居中X/既定脚底Y；manifest alignment.version=2与独立验证必须通过后发布。详见README与alignment-validation/regression.json。
