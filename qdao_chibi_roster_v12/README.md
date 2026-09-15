# V12 八方向八帧人物动作

2026-09-14 当前状态：用户要求继续修正。年轻吕洞宾的新道家Q版已完成64张步行、8张独立站立及同身份肖像，按对齐v3接入游戏；候选源包为 `candidate-stable-body/24_lu_dongbin`。实际81张PNG及启用记录逐文件核对一致。独立Unity副本的127/127 EditMode、8/8 PlayMode通过，证据见客户端 `Docs/ArtEvidence/v12-natural-lu/summary.json`；原编辑器中的未保存场景保持原状。何仙姑、韩湘子正按具体原画问题修正，其余角色尚未全部完成。内部检查通过不等于用户已认可整批美术。

游戏当前实际接入V12的有23灯穗小使、24吕洞宾、25狮鼓护卫、26桂香药婆、29何仙姑、30韩湘子；27墨鸢游侠、28月兔机关师仍使用同ID的V11。已接入的角色也在本次造型、步态和比例复核范围内，不能把已接入状态表述为用户已认可。

本目录保留V11与上一版V12素材。后续角色按已核实的问题逐项修正并完成整套检查，不按旧内部passed记录直接批量发布。

风格为道家 Q 版：Q 只说明人物比例和画法，服饰、发髻与法器要有道家依据；不能把泛泛国风当作道家。本轮延续已验收的角色身份，不使用“幻想风格”替代用户指定风格。

每位角色交付 64 张真实走路动作、8 张独立自然站立图和延续同一人物身份的肖像（默认沿用 V11，可按本轮道家服饰修正使用新肖像）。八个方向为 N、NE、E、SE、S、SW、W、NW。每方向按 01→08 循环，参考帧时长 60ms，一轮 480ms。v2脚底像素锚点为左上坐标 (256,471)；v3以该点作为世界根点，并保持同方向idle与走路头部定位。单帧 512×512 RGBA，拼接条 4096×512。

原画使用内置 image_gen。脚本仅做去洋红底、提取原画单格、透明清理、共同缩放、显式v2/v3整帧平移对齐和导出，不绘制、镜像、重复或插值生成姿势。独立站立图不能来自走路帧复制。

| 输入 | 网格 | 行序 |
|---|---|---|
| s_e | 4列×4行 | 前两行 S 的 01–08，后两行 E 的 01–08 |
| n_w | 4列×4行 | 前两行 N，后两行 W |
| ne_sw | 4列×4行 | 前两行 NE，后两行 SW |
| nw_se | 4列×4行 | 前两行 NW，后两行 SE |
| idle | 4列×2行 | 逐格 N、NE、E、SE、S、SW、W、NW |

所有单格接近正方形，原图边长不能整除时只允许丢弃透明背景余边。走路和站立保持相同镜头距离、相同角色占格比例和中央安全留白。原生分辨率逐张记录，512 输出为确定性重采样结果，不宣称原生高清单帧。

单张原画先检查：

```powershell
python -X utf8 -B E:/work/image/qdao_chibi_roster_v12/inspect_sheet.py --kind s_e --input RAW.png --output-dir E:/work/tmp/v12-inspect
```

完整人物处理：

```powershell
python -X utf8 -B E:/work/image/qdao_chibi_roster_v12/process_roster.py --character-dir E:/work/image/qdao_chibi_roster_v12/24_lu_dongbin --s-e S_E.png --n-w N_W.png --ne-sw NE_SW.png --nw-se NW_SE.png --idle IDLE.png
```

完整 72 姿势共用一个最终缩放系数，每帧只可平移。每方向体态面积平方根 CV≤0.08、源脚底位置标准差≤0.05、跨方向平均高度比例≤1.10，同方向站立与走路平均高度差≤8%，无源裁切、输出触边、贴图钳位、空帧或精确重复帧。数值通过仍需检查脸部身份、八方向朝向、八个不同实际步态、脚/手/法器完整性、环接和透明边缘，才可将 qc.json 改为 passed / visual_review: passed。

运行时契约与证据范围见 CLIENT_CONTRACT.md。处理工具和运行时代码已有实现，当前资源版本及暂停状态以上述说明为准。

优先逐方向生成和验收真实八步。单方向默认 2列×4行，也可显式使用 4列×2行；每张均为逐行 01→08：

```powershell
python -X utf8 -B E:/work/image/qdao_chibi_roster_v12/inspect_sheet.py --kind E --rows 4 --cols 2 --input E_RAW.png --output-dir E:/work/tmp/v12-e-inspect
python -X utf8 -B E:/work/image/qdao_chibi_roster_v12/assemble_raw.py --kind s_e --first S_RAW.png --second E_RAW.png --output S_E.png
```

重排仅在原画已经通过朝向、八个真实步态和安全留白的视觉检查后进行。脚本记录全部来源、单格坐标和共同单格缩放，不把两张原画重排产生的分辨率称为新生图原生分辨率。

肖像默认原样沿用 V11。明确制作了同一人物的新道家服饰肖像时，可传 `--portrait 已处理1024RGBA.png` 或 `--portrait-raw 内置生成洋红底原图.png`；两者互斥，处理器保存来源 SHA、原生规格和清理记录，新肖像须连同全角色视觉验收。客户端在 V12 整套完成前仍使用同角色 V11 肖像。

## 相位 × 方向转置制作

若单方向八步原画难以保持八个真实相位，可先接受01–08的真实步态，再为每一个相位单独生成八方向转面。每张原画只冻结一个相位，固定为4列×2行：上排N、NE、E、SE，下排S、SW、W、NW。服饰、发髻、法器和短身比例保持道家 Q 版；转面不能擅自改步态。

```powershell
python -X utf8 -B E:/work/image/qdao_chibi_roster_v12/assemble_phases.py --phase phase-01.png --phase phase-02.png --phase phase-03.png --phase phase-04.png --phase phase-05.png --phase phase-06.png --phase phase-07.png --phase phase-08.png --output-dir phase-transposed
```

输出八张 `walk-<DIR>.png`，每张4列×2行是同方向01–08相位。`--directions E W`可只导出八个标准方向中的指定子集；默认全部八向，不改变输入原格顺序。脚本在每张原图的所有视角上统一使用同一个原格等比缩放，单格宽高略有差异时居中补洋红，不拉伸身体，不按人物边界逐帧适配。每张输出旁的`.assembly.json`保存八个原始SHA、原生尺寸、逐相位原格坐标及缩放/放置记录；此分辨率是重排导出尺寸。

先逐方向运行`inspect_sheet.py --kind E --rows 2 --cols 4`并做步态视觉验收。随后可用`assemble_raw.py`配对：输入转置结果时显式指定`--first-rows 2 --first-cols 4 --second-rows 2 --second-cols 4`。配对脚本保留完整上游相位转置记录，主处理器再将其收入最终来源链。转置只搬运已生成的动作；数值检查和格数正确都不能代替八个真实相位与自然环接的视觉验收。

## 2026-09-13：修正水平对齐，保留真实步态

初版处理器取最低10%脚部像素的水平中位数作为X锚点。换支撑脚时这个值随左右脚跳变，造成整个人左右平移；韩湘子64帧的相邻上身横跳最大41px，单方向范围最大46px。此问题与动作原画是否换腿分别验收。

对齐版本2将游戏根点定义为「上身水平轴 + 脚底高度」(256,471)。X是alpha>8主体上部42%像素的水平中位数；这批大头Q版角色的头部提供稳定参考轴。Y仍为最低alpha>8像素471。两者都具有平移不变的测量规则。脚掌可随走路在根点左右移动，不再强制当前支撑脚中心占据x256。每帧仍只平移，全72姿势仍共用一个缩放系数，未绘画、变形或插值。

新增独立门禁：每张走路和站立的水平轴距256不得超过0.5px，原有尺度CV、原图触边、裁切、透明边缘、独立站立与八个真实姿势要求保留。manifest必须声明alignment.version=2，verify_delivery.py独立重算轴与地面高度；旧支撑脚X对齐的导出不能直接发布。根点和Unity居中X/脚底Y的Sprite pivot格式不变，无需修改角色方向或移动控制器。

回归证据alignment-validation/regression.json使用64张真实旧导出，只做整数平移后，裁出人物的RGBA字节逐帧完全相同；水平轴相邻跳动从最高41px降到0px，脚底Y仍471。此回归仅验证对齐，不代表角色的原画视觉验收已通过。


## 已接入与边缘清理

游戏当前实际接入V12的有23灯穗小使、24吕洞宾、25狮鼓护卫、26桂香药婆、29何仙姑、30韩湘子；27墨鸢游侠、28月兔机关师仍使用同ID的V11。已接入的角色也在本次造型、步态和比例复核范围内，不能把已接入状态表述为用户已认可。

历史运行范围：`E:/work/mmorpg-client/Docs/ArtEvidence/v12-three-immortals`中的121/121 EditMode、7/7 PlayMode属于24/29/30三位V12时期，当时26仍为V11。`v12-four-approved`中的121/121 EditMode、7/7 PlayMode属于随后24/26/29/30四位V12的定向回归（2026-09-13 14:13–14:16 UTC）。两组均为历史离线运行证据，不是停步修复后的新一轮全量测试，也不能代替美术验收。

当前停步修复证据：`E:/work/mmorpg-client/Docs/ArtEvidence/v12-stop-fix/playmode.xml`记录2026-09-13 15:04:04–15:04:12 UTC，8/8 PlayMode Passed、0失败，包含`V12_StoppingAtDifferentPhases_ShowsDirectionIdleOnTheNextFrame`。该项验证不同步态相位停下后，下一帧切到对应方向独立站姿；运行行为通过不能证明道家风格、自然步态、脸型或大小符合用户要求。新吕洞宾已完成本轮修正与接入；其余角色按最新用户继续指令逐项推进。

`--despill-magenta-edge`为可选的确定性边缘去底色：仅alpha>8主体距离alpha<=8区域2px内的明显洋红污染，按附近可靠实体颜色减少R/B；alpha、G、几何和红色流苏保持原值。默认关闭，避免给没有该问题的角色增加处理。24已使用并逐帧证明72张透明形状完全不变，证据在24/processing/despill-validation.json；原始生成图不改。


## 2026-09-14：吕洞宾稳定定位与完整接入

对齐v3以同方向独立idle确定固定头部ROI和头顶Y；所有72帧共用一个scale，每帧只整数平移。世界根点仍为(256,471)，但步行时不同远近脚可围绕根点变化，不再把最低鞋像素强行锁死。独立验收按源RGBA重构平移结果，拒绝错位、裁断、改像素及错误参考元数据。旧角色v2仍按原规则验证。

本次修正了SE06腿部遮挡和摆臂、NE头型，以及S/N/E/SE独立站立比例。追加边缘清理显式使用4px边缘及12px颜色参考；全部72帧alpha、G通道、位置和受保护红色不变。默认去色仍2px/6px，旧默认输出54次真实帧比较逐像素一致；细发梢中无可靠参考的像素未强行改色。

最终源：`E:/work/image/qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin`。81PNG已接入，alignmentVersion=3；导入前资源留存在 `Docs/ArtEvidence/v12-natural-lu/before-import/`。新运行结果是独立副本127/127 EditMode和8/8 PlayMode，副本81PNG、启用记录及357个C#文件在启动前与正式项目一致。真实城市图为 `Docs/ArtEvidence/v12-natural-lu/tianyong-24_lu_dongbin.png`。这些是离线游戏测试，不是整批8位角色的美术完成声明。


## 狮鼓护卫：本轮接入记录

25 狮鼓护卫已完成 64 张真实行走、8 张独立站立和 v3 定位验收，81 PNG 已接入并验证 SHA。城市截图已人工查看。独立副本定向测试 127/127 EditMode、8/8 PlayMode 通过。代码使用上次通过的 357 文件基线；第一次使用当前保存主工程的尝试因 4 个缺失的公会枚举编译失败，记录保留，原工程公会文件未改。这不是当前主工程全量编译通过声明。证据：E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\25-lion-guard\summary.json。


## 23/24/25 当前代码联合回归

2026-09-14 13:13 UTC，23灯穗小使、24吕洞宾、25狮鼓护卫已完成本轮修正并接入。先前公会枚举缺失已由当前工程补齐；本次360个C#与246个人物资源文件在启动前逐一匹配，127/127 EditMode、8/8 PlayMode通过。独立副本运行，不操作用户已打开的Unity场景。证据：E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\23-25-current-code\summary.json。其他五位仍在本轮制作/验收中。
