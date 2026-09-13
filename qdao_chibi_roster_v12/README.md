# V12 八方向八帧人物动作

制作中。本目录不覆盖已验收的 V11 图片；未通过数值与视觉验收的角色不能发布到游戏。

风格为道家 Q 版：Q 只说明人物比例和画法，服饰、发髻与法器要有道家依据；不能把泛泛国风当作道家。本轮延续已验收的角色身份，不使用“幻想风格”替代用户指定风格。

每位角色交付 64 张真实走路动作、8 张独立自然站立图和延续同一人物身份的肖像（默认沿用 V11，可按本轮道家服饰修正使用新肖像）。八个方向为 N、NE、E、SE、S、SW、W、NW。每方向按 01→08 循环，参考帧时长 60ms，一轮 480ms。脚底像素锚点为左上坐标 (256,471)，单帧 512×512 RGBA，拼接条 4096×512。

原画使用内置 image_gen。脚本仅做去洋红底、提取原画单格、透明清理、共同缩放、脚底平移对齐和导出，不绘制、镜像、重复或插值生成姿势。独立站立图不能来自走路帧复制。

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

运行时准备方案见 CLIENT_CONTRACT.md。处理工具和运行时代码已准备；当前尚未发布任何 V12 角色。

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
