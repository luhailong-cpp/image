# 吕洞宾 16 帧行走升级：给另一个窗口的完整任务

本任务先升级 **24_lu_dongbin（年轻版吕洞宾）**。目标是保留当前道家 Q 版形象，在现有 8 帧之间补绘真实过渡动作，完成八方向 16 帧并接入游戏。其余七位角色保持已完成的 V12 八帧。本轮不增加攻击、跑步、技能或 32 帧动作。

## 1. 先接手现有成果

工作目录：`E:\work`；Unity 项目：`E:\work\mmorpg-client`。

先阅读这些文件，并检查是否已有另一个窗口开始同一项工作：

- `E:\work\image\AGENTS.md`、其引用的当前图片模型策略和 README 接手说明。新生图开始前按该策略核对当前能力，不把旧交接中的模型名当成永远有效的配置。
- `C:\Users\luyua\.agents\skills\generate2dsprite\SKILL.md`
- `C:\Users\luyua\.codex\skills\.system\imagegen\SKILL.md`
- `E:\work\image\qdao_chibi_roster_v12\README.md`
- `E:\work\image\qdao_chibi_roster_v12\CLIENT_CONTRACT.md`
- `E:\work\image\qdao_chibi_roster_v12\completion-20260916.json`

**准确的吕洞宾基线**：

`E:\work\image\qdao_chibi_roster_v12\candidate-stable-body\24_lu_dongbin`

该目录有 `portrait.png`、`idle/<DIR>.png`、`walk/<DIR>/01.png` 至 `08.png`、`source`、`processing`、`review`、`manifest.json`、`qc.json`、`validation.json`。必须从这套已验收成果接手，不能误用原始角色目录、旧老人或早期候选。

基线 manifest SHA-256：

`3dbc699023fd7fe6f45304fd91ecea2f088e107d4c727d375dc1b23c31e68c68`

正式启用资源：

`E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12\24_lu_dongbin`

现有预览：`http://127.0.0.1:8871/`；文件位于 `E:\work\image\qdao_chibi_roster_v12\review\site`。端口不在时先检查既有服务，再使用 `review/serve_final_preview.py`，只服务该站点目录。

此前八人 127 项 EditMode、8 项 PlayMode 和 64 方向浏览器验收已通过。那是 V12 保存快照的历史结果，不能当成本次 V13 的测试结果。

## 2. 形象与动作要求

使用当前年轻吕洞宾：年轻面容、深色发髻、米白与深青布衣、背剑及既有红穗、腰间葫芦。以基线图的配饰归属为准，不能在某个方向翻到另一侧。

保持道家 Q 版、普通布料和现有画风。不要重新设计脸型、头身比例、服饰、肖像或站立图；不要增加发光、光翼、漂浮粒子或华丽幻想铠甲。

动作要表现自然走路：左右腿轮流承重，摆臂与腿协调，脚掌释放、经过、前伸、落地连贯。避免踢正步、高抬膝、腿打结、脚滑动、双脚同时离地、配饰跳边。人物大小、五官和身体比例不能随帧改变。

## 3. 精确帧数与时序

| 项目 | 目标 |
| --- | --- |
| 方向 | N、NE、E、SE、S、SW、W、NW，共 8 向 |
| 行走 | 每向 16 张独立真实动作；共 128 张 |
| 站立 | 每向 1 张独立 idle；沿用现有 8 张 |
| 单帧 | 512×512，RGBA 透明 PNG |
| 肖像 | 沿用现有 1024×1024 PNG |
| 单帧时长 | 30 ms |
| 完整步态周期 | 16×30=480 ms，与原 8×60=480 ms 相同 |
| 单向条带 | 8192×512，16 格，仅作审阅/兼容；运行优先使用独立单帧 |
| 总 PNG | 128 行走 + 8 idle + 1 肖像 + 8 条带 = 145 张 |

帧数翻倍后不能让一次迈步变慢或加快。保留角色实际移动速度及一个完整步态周期对应的世界移动距离；按原有距离驱动逻辑调整每帧对应距离/FramesPerUnit，并实测脚底是否滑动。

## 4. 如何补成 16 帧

保留已验收的 8 张作为新序列的奇数帧，**新增 64 张实绘过渡帧**：

| 现有 V12 帧 | 新序列位置 | 新增过渡帧 |
| --- | --- | --- |
| 01 | 01 | 02：旧 01→02 的中间动作 |
| 02 | 03 | 04：旧 02→03 的中间动作 |
| 03 | 05 | 06：旧 03→04 的中间动作 |
| 04 | 07 | 08：旧 04→05 的中间动作 |
| 05 | 09 | 10：旧 05→06 的中间动作 |
| 06 | 11 | 12：旧 06→07 的中间动作 |
| 07 | 13 | 14：旧 07→08 的中间动作 |
| 08 | 15 | 16：旧 08→01 的循环衔接动作 |

每个方向新 01 是解剖 RIGHT 接触、新 09 是解剖 LEFT 接触；`contactFrame` 使用零基下标 0。只看鞋子在屏幕左右或上下的位置不能判定左右腿，必须结合髋部、裤腿遮挡和支撑关系检查。

新增帧必须通过图像生成工具实绘。不得用复制、镜像、叠化、光流补帧、局部扭曲、AI 视频插帧或缩放已有动作凑数。Pillow/脚本仅用于透明处理、完整格切分、统一分辨率、整数平移、来源核验、排版联系图和预览。

优先用内置 image_gen，按其当前实际接口提供参考图。参考相邻两个已批准姿势，同时保留该方向 idle 的比例参考。每次只生成少量姿势便于检查。原始生成图、提示词、选择过程和 SHA 全部保存；失败稿保留但不能混入正式输出。若工具没给可证明的模型信息，应如实记录，不能把提示词里写模型名当成切换成功。

可用的单帧提示词骨架：

> 以提供的同方向吕洞宾 A/B 两张姿势及站立比例为严格参考，只绘制 A 到 B 之间的一张真实中间行走姿势。保持年轻脸型、发髻、米白与深青布衣、背剑红穗、葫芦和相同镜头。明确写出该帧支撑腿、摆动腿、脚掌离地高度与手臂阶段。低抬脚自然行走，身体及头部比例固定，全身完整。使用项目规定的背景与留白，不能拼贴参考姿势、改变方向或镜像器物。

## 5. 对齐与来源要求

复用 V12 的 alignment v3：世界根点 `(256,471)`，同方向独立 idle 的固定头部 ROI、水平轴和头顶参考；吕洞宾当前 common_scale 为 1.0。以其 manifest 和 frame-transforms 记录为准。

- 现有 64 张行走输出映射到新奇数帧后，PNG 文件 SHA 应与基线一一相同；8 张 idle、肖像也保持原文件 SHA。
- 新增偶数帧按同一比例基准与对应 idle 对齐。归一化只作用于完整源格；禁止按每个人物 bbox 单独缩放，更不能拉长身体或腿。
- 头部定位稳定，允许前后脚保留透视深度；不能把所有鞋底最低点强行拉到同一屏幕 Y。
- 透明边缘清理可复用当前实现，不能侵蚀发梢、红穗、鞋底或轮廓。保存清理前后证据；不要重复处理已经通过的旧帧。
- 每个最终格都记录原始生成文件、原始格位置、整格归一化、允许的边缘清理、整数平移及最终 SHA。奇数帧引用已冻结的 V12 manifest 与原文件来源链。

已有数值门槛继续保留：同方向 body CV≤0.08、跨方向平均高度比≤1.10、idle/walk 高度差≤0.08、头部横向轴误差≤0.5px、头顶与该向 idle 一致；每向 16 帧全都唯一，idle 不能复制某张 walk。新增帧进入后若不通过，要改具体问题，不能放宽门槛。

## 6. 工作目录和接入方式

建议新候选放到：

`E:\work\image\qdao_chibi_roster_v13\candidate\24_lu_dongbin`

建议新游戏资源：

`E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV13\24_lu_dongbin`

制作期间游戏继续使用已批准 V12。不要覆盖 V12 的 PNG、manifest、QC 或验收 SHA，也不要重跑旧处理器把原目录输出改掉。现有 `process_roster.py`、`verify_delivery.py`、`sync_to_client.py` 有 8 帧假设；可以复用经过核验的底层函数，但需为 V13 明确实现 16 帧的导出、来源证明及验证，保留旧默认行为。

需要检查并适配的实际客户端文件：

- `E:\work\mmorpg-client\Assets\Scripts\World\QdaoCharacterCatalog.cs`
- `E:\work\mmorpg-client\Assets\Scripts\World\QdaoBoySpriteAnimator.cs`
- `E:\work\mmorpg-client\Assets\Editor\QdaoCharacterSpriteImporter.cs`
- `E:\work\mmorpg-client\Assets\Editor\QdaoFrameAlphaProcessor.cs`，仅在其路径识别确有必要时适配。

当前目录加载器把 V12 绑定为 8 帧/60ms，其余版本走旧四帧；停止立即切 idle 的动画分支也有 `Version == 12`。不能只把资源 metadata 的 frameCount 改成 16。

接入要求：

1. 新增明确的 V13 契约：version=13、frameCount=16、frameDurationMs=30、dedicatedIdle=true、alignmentVersion=3、contactFrame=0，保留角色 ID 与人物/职业/性别映射。
2. 完整性选择按 **已批准且完整的 V13 → 已批准且完整的同 ID V12 → 同 ID V11** 回退。缺任意新帧、idle、肖像或元数据损坏时，不能混用版本或换成别人，也不能因为 V13 不完整就跳过有效 V12。目录选择器和动画器的 `MissingAppearanceFrame` 都要覆盖这一回退顺序，包含目录校验后实际加载缺帧的情况。
3. 缓存与资源解析要包含版本、批准内容修订、帧数/时序，并观察 V13 和 V12 的启用记录变化。未完成导入不能被永久缓存为已完成结果。
4. 保留方向变化时的步态相位、独立站立、停步下一帧切 idle、脚底定位、阴影、碰撞体、移动速度、保存的角色身份及战斗外观。不要把所有旧角色的 8/4 常量一刀切成 16。
5. 导入器当前 maxTextureSize=4096。仅为确需的 V13 8192×512 条带支持8192上限，并检查运行设备限制；普通512单帧和其他角色/战斗素材的导入设置保持原行为。不能让条带静默缩成4096。
6. 最终验收通过后再复制完整资源，最后发布 `appearance.json` 与对应真实 SHA；从游戏实际加载结果确认启用了16帧。正式接入前保留可还原记录。

## 7. 建议执行顺序与验收

先做 S 正面、E 侧面两方向：每向补8张、形成16帧，和当前8帧在相同显示尺寸、同为480ms循环的条件下并排播放。检查中间帧是否使步态更顺、有没有新变形；不合格先修具体帧。通过自检后继续其余六方向，不要每一步停下来反复征求确认。

八方向完成后：

- 导出每向「1张idle + 16张walk」联系图、16帧循环预览，以及所有方向的8/16帧同步对比页；浏览器播放以PNG实际单帧为准。
- 检查01→16完整周期，重点检查15→16→01接缝、01/09左右接触、换向相位和站走转换；至少在正常游戏尺寸与放大尺寸各查看一次。
- 证明64张旧walk、8张idle、肖像保持原SHA；证明64张新walk有真实生图来源、每向16姿势唯一；证明条带每格与独立PNG逐像素相同，无切边或错序。
- 扩展相关 EditMode/PlayMode 测试：16帧完整加载、8/16混用、残缺V13回退V12、V12也残缺再回退V11、错误ID/批准状态/尺寸/时序、缓存刷新、独立idle、不同相位停步、换向连续性、相同路程的步态周期、切外观不改变位置/碰撞体/阴影。
- 在真实主城用真实移动控制器查看和移动吕洞宾，并确认其他七位仍加载各自完整V12。

已有测试入口：

`Assets/Tests/EditMode/Tianyong/QdaoCharacterCatalogTests.cs`
`Assets/Tests/EditMode/Tianyong/QdaoAppearanceVersionTests.cs`
`Assets/Tests/EditMode/Tianyong/QdaoRoleAppearanceBindingTests.cs`
`Assets/Tests/EditMode/Tianyong/QdaoBoySpriteAnimatorLogicTests.cs`
`Assets/Tests/PlayMode/QdaoBoySpriteAnimatorPlayModeTests.cs`
`Assets/Tests/PlayMode/QdaoRosterAnimatorPlayModeTests.cs`
`Assets/Tests/PlayMode/QdaoRosterSandboxPlayModeTests.cs`
`Assets/Tests/EditMode/Battle/BattleRosterAppearanceTests.cs`（版本选择受影响时覆盖）

保留现有 `QdaoAppearanceVersionTests` 中“V12 元数据声明16帧必须拒绝”的用例；合法16帧属于新增V13用例，不能为支持V13放宽V12契约。

这些路径相对于 Unity 项目。按实际改动选择必要测试，不冒用历史通过次数。逐像素全套检查已有单项600秒时限；如执行慢，先区分导入/测试与实际停滞，不因超时放宽图片断言。

使用独立 Unity 验证副本或确认空闲的隔离环境。先记录实际输入的代码与素材SHA，测试后记录同一快照和差异。不要保存、关闭、杀掉用户已打开且可能有未保存内容的Unity，也不要回退其他任务的社交、邮件、地图、队伍、公会、聚宝斋等改动。

## 8. 最终交付

交付吕洞宾完整八向16帧、8张独立idle、原肖像、来源清单、manifest/QC/独立验证、8对16同步预览、实际游戏截图、测试结果，以及V13正式启用/回退证据。现有V12继续可用。

最终说明要准确区分：制作完成、内部视觉验收、已接入、运行验证通过。如果某项受外部工程问题阻塞，写明实际完成部分和具体阻塞，不能用旧日志说全部通过。工作正常时持续做到整套完成。
