# 27 号新批次确定性处理

此工具只处理 `../sources/` 中已生成、已确认的新原画，输出到本修复批次的独立暂存目录。不会修改正式 `qdao_chibi_roster_v11/27_ink_kite_ranger/`，也不会把旧帧、比例中间稿或现有动作复制成新交付。

## 输入和运行

从 `E:/work/image` 运行，建议所有命令显式使用同一个 `--output-dir`：

```powershell
python -X utf8 qdao_cutout_edge_repair_20260911/27/tools/process_new_batch.py portrait --output-dir qdao_cutout_edge_repair_20260911/27/staged-v2
python -X utf8 qdao_cutout_edge_repair_20260911/27/tools/process_new_batch.py direction S --output-dir qdao_cutout_edge_repair_20260911/27/staged-v2
python -X utf8 qdao_cutout_edge_repair_20260911/27/tools/process_new_batch.py assemble --output-dir qdao_cutout_edge_repair_20260911/27/staged-v2
```

`portrait` 只读取 `sources/portrait_raw.png`。`direction S` 只读取 `sources/walk_S_2x2.png`；其余方向依次使用 `SW/W/NW/N/NE/E/SE`。九张原图齐全后，`build` 可以完整处理全部输入；`assemble` 只校验已处理原图和输出的哈希、拼方向表并写总清单，不重新切图。

`portrait-proportion-intermediate.png` 不在任何默认输入列表内。最终原图更新后必须重新处理其对应立绘或方向。工具自身、RGB 清边器、项目脚点函数或 GIF 编码器改变后，也必须重新处理，以免拼入不同算法版本的暂存。

## 输出合同

- 立绘：`portrait.png`，1024 × 1024 RGBA。保留原图画布比例，等比缩放及居中填充，不按人体区域变形。
- 动作：`walk/{方向}/01.png` 至 `04.png`，512 × 512 RGBA。原图 2 × 2 按左上、右上、左下、右下读取，每方向四帧共用一个等比缩放，使最大可见身高为 420 像素；脚点为 `(256,471)`。不镜像、不旋转、不复制、不补造动作。
- 每方向 `strip.png` 为 2048 × 512，`walk.gif` 为 4 帧 × 120 ms；GIF 只有二值透明度，PNG 保留抗锯齿 Alpha。
- `walk-cardinal.png`、`walk-diagonal.png` 为 2048 × 2048；行顺序分别为 `S,W,E,N` 和 `SW,NW,NE,SE`。
- `manifest.json` 记录 51 个最终媒体文件、原图真实尺寸及 SHA；`qc.json` 只报告机器检查结果。`processing/` 保存每源记录、每帧位移/缩放、去底统计、原生透明图及浅深底预览。

## 透明处理与验收边界

先从实际外边缘采样洋红底色，再以附近干净前景和底色的混合关系求覆盖率，并做 RGB 反混合。交错发丝、风筝细绳的封闭洋红孔洞也参与处理。远离所有前景的压缩底色噪声清零；随后只对残余洋红边缘做同源邻色去污染，保留这一步之前已经求出的 Alpha。

此方法适用于 27 号灰黑头发、青玉衣饰、象牙白和少量正常红穗的既定配色；不要直接用于合法紫色角色。代码不通过删组件来隐藏缺陷。素材触碰切格线、缺少主体、出现多个大组件、同方向尺度变异系数超过 0.08 或出现完全重复帧时会停止，必须检查原图。它不会用变形或独立缩放每帧来绕过失败。

四个文件哈希不同并不意味着四个动作相位正确。最终仍须逐方向检查朝向、接触/经过/反侧接触/反侧经过的顺序，检查细发、风筝绳、红穗、完整脚部和浅深底边缘。机器通过后状态始终为 `passed_numeric_qc_pending_visual_review`，本工具不发布，也不把视觉审查自动标为通过。

项目原有 `process_roster.py` 的脚点与拼接函数、`generate2dsprite.py` 的 GIF 编码函数被只读复用。没有改动这两个原文件。
