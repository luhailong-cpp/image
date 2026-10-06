# 原生波前片段拼接工具

入口：同目录 `native_assemble.py`。工具不会生图，不导入旧脚本的运行入口，不写根 progress/current-work/current-preview，也不自动标记验收通过。

当前只完成工具与小型内存坐标检查；尚未执行 r10_c13 生产拼接。

## 使用

在此 ROOT 目录下，以项目可用的 Python（Pillow、NumPy，以及 `tools/deps` 中的 OpenCV）运行：

```powershell
python native_assemble.py selfcheck
python native_assemble.py assemble --tile r10_c13 --preflight
python native_assemble.py assemble --tile r10_c13 --registration bounded --max-shift 6 --tone-cap 18 --return-depth 256
```

`--preflight` 只校验输入。必须存在 `r10_c13/native/p11.png` 至 `p44.png` 及各自 `.png.generation.json`；工具核验 SHA、1254原生尺寸、不透明、未放大和全局范围。缺片时不写输出。先前候选／字段／QA已存在时拒绝覆盖。

`--registration none` 使用原生二值归属，不配准、不校色；仍保留零场与遮罩。默认 bounded 仅做有限原生重采样与校色，不能修复缺失结构。6px是默认实现参数而非用户硬限；当前参数范围0–12px，色差上限0–32，每次实际值均记录。发现场折叠则停止发布候选，保存失败记录。

## 坐标与处理

16张片段按逐行顺序读取，满足左、上依赖。每张1254=115+1024+115；在4326画布位置 `((列−1)×1024,(行−1)×1024)`，最终裁 `[115,115,4211,4211)`。本片核心 `[115,115,1139,1139)` 对应1024核心，内部名义分界位于片段115，非0或230。

`plan.json` 的 northCandidate、westCandidate 直接读取最终旧邻4096图，分别用底115和右115作真实支持；northWestCandidate 可选，缺失则左上115²不声称有真实旧邻支持。外部115支持与内部230支持分别记录。

光流仅从已覆盖的真实支持估计、向新侧有限外推，向量幅值截断并在核心内指定 return-depth 回零。校色仅取低梯度且色差接近的支持区，平滑的是校正场，不模糊画作。拼接使用二值像素归属，不用羽化遮挡几何。每片保留 mask、support-mask、flow、colorCorrection 及实际位移、RGB范围、场雅可比、来源哈希。

## 输出

- `r10_c13/output/r10_c13-candidate.png`：4096候选，实际像素全部来自原生片段与记录的有限重采样／校色。
- `r10_c13/output/native-assembly.json`、候选 `.generation.json`：派生链、参数、字段和状态。
- `r10_c13/output/native-fields/`：16组实际归属、真实支持、位移和色彩场。
- `r10_c13/qa/native-candidate/`：6条完整4096内部缝、9个320²交点；实际旧north/west共边各4096；新侧 return-depth 返回线；东／南缺邻边明确标未验。各图只裁切和90°旋转，保持原像素，无缩放。

所有QA初始 `actuallyViewed=false`，候选保持 `scopedLocalSeamsPassed=false`、formal/client/nav=false。必须实际逐张查看后再由后续任务记录局部验收；强错位或缺结构应原生AI补绘，不能提高色差或位移去遮挡。后续上下文从最终验收的4K图裁取。
