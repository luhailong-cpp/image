# 01 主城节庆地图 · 独立续作

内部资产 ID：`tianyong_festival`；不据此建立旧地名与原创命名的映射。

目标为 65536×65536、16×16 共256块，每块4096×4096。内置生图；不使用付费API。尚未完成整城或客户端验收，正式验收数为0。

当前入口：`source-checkpoint.json`、`progress.json`、`current-work.json`。父任务已在2026-10-05释放交接；本任务此前依据用户继续指令冻结稳定来源后续作。当前检查点优先于旧交接片段，不能回退已修补的底邻。新成果只写本目录，原目录只读。

## 已完成准备

- 阅读项目规范、风格、模型策略及原图交接；历史计划、风格图与六块历史候选的SHA已核对，见 `intake-verification.json`。这些历史候选不代表最终交接快照。
- 已查看 `designs/gameplay-ui/04-guild.png` 与原6144结构底图。`canonical-layout-preview-only.png` 仅是原图缩略检查，不是高清成品。
- 本任务已核对官方Images 2.5与Sunburst质量列表；配置目标为 `gpt-image-2.5-sunburst/max`。内置工具没有型号/质量选择器；实际版本和质量未知，见 `model-capability.json`。
- 已完成r08_c10的4096×4096原生合成候选，全块无透明缺口；九张重叠原像素裁图的完整内部检查见`full-review-v017/internal-review.json`。随后接入北邻r07_c10的四条返回带，仅改动r08_c10顶部61行；其余像素与v017一致，证明见`candidates/r08_c10/north-update-proof.json`。
- 现有全城13个不同坐标的完整4096候选，正式通过0；旧版本不能重复计数。最新全256坐标盘点见`inventory/current-candidate-inventory.json`，已逐文件核对哈希、尺寸和实际透明度，区分完整候选、局部在制和完全缺失。已导出候选及当时的完整候选集合见`candidates/r08_c10/r08_c10.png`和同目录`candidate-set.json`。后者是交付候选快照，当前制作来源以根`source-checkpoint.json`中的`candidateSet`为准；旧`inventory/remaining-production-inventory.json`仅是2026-10-05历史盘点，不改写它。六个coupled-v2候选须成组承接，任何局部邻块修复必须同步登记所有返回条。
- 当前制作已进入后续图块；请每次动态读取`progress.json`的`activeTile`、`coveredNativeTilePixels`和`tileCoverageFraction`，并用`source-checkpoint.json`定位实际片段。不能把旧r08_c10进度当作当前状态，也不能用外接矩形面积冒充完成面积。`current-preview.png`跟随当前在制图块，是进度缩略图，不是整城或交付候选。

## 候选快照与验收范围

r07_c10也已补齐4096×4096并清理一处多余裂纹；九张重叠1536原尺寸裁图覆盖全部像素、六条全长内部接缝、九个交点和实际拼接位置，见`r07_c10/full-review-v017/internal-review.json`。南侧整条边界已有来源一致性证明及原像素检查。r07_c09和r07_c11各已接入1,297,321个原生像素及所有关联返回条，仍为局部在制；r06_c10的立柱区域正在隔离重绘，未计为完整候选。当前已入检查点的盘点为13完整、2局部、241完全缺失，具体以最新inventory为准。

`candidates/r07_c10/r07_c10.png`保存第二张已完成并经过整块内部检查的候选。两张导出图已同步左右相邻片段的新返回条；更新先把已通过的manifest逐像素重放到上次导出，再与当前完整源逐像素比对。变化范围、旧版本的文字记录与SHA、局部检查在各自`updates/`和`delivery-status.json`登记。原整块检查不自动扩大为后续外部边界全部通过。

| 当前导出 | 逐图模型、质量和来源记录 |
|---|---|
| `candidates/r07_c10/r07_c10.png` | `candidates/r07_c10/r07_c10.png.generation.json` |
| `candidates/r08_c10/r08_c10.png` | `candidates/r08_c10/r08_c10.png.generation.json` |

以上均为多片原生合成后无损导出；实际内置模型版本和质量未披露，记录为未确认，不声称单次AI原生4096输出。

`candidates/r08_c10/r08_c10.png`保存r08_c10当前完整无损候选；其生成记录直接指向接入北侧返回带后的实际来源，并引用原内部检查和北边界检查。更新快照时只保留此最新版候选文件，不另存图片备份；旧来源与加工记录仍按项目保留策略核实处理。

该候选的左边、南边和北边已有局部原像素检查通过记录，具体来源、范围和限制见`candidates/r08_c10/delivery-status.json`。东邻及相关缺失角块、游戏最近镜头与跨块运行检查、导航与整城256块验收仍待完成；完整候选不等于正式验收通过。

## 制作与检查

`select_native_tile.py`依据真实相邻完整图切换制作坐标，保留所有已入检查点的局部片段；不把透明脚手架计为已绘像素。`commit_manifest.py --anchor-tile ... --anchor-side ...`核对邻接方向、世界坐标、旧ROI像素、不可拆分返回条和未改范围，再整体接入。只有实际下邻存在时`bottom`才是该图；不能用左邻伪装下邻。旧入口仍可使用原`--bottom-tile`参数。

`prepare_expansion.py` 根据已验证检查点准备明确坐标的透明在制上下文、布局参考和实际请求；运行需显式给出底邻及当前片段路径和SHA。原6144图片只提供结构引导，放大像素不得进入成品。

原生片按1024核心、115外圈延续；每个返回独立保存请求、真实工具结果、实际尺寸、SHA、来源角色及版本未知原因。图块内部六条全长缝、九个四片交点、完整共边及跨块四角必须实际查看再记录结果。缺失或未经检查的范围保持未完成。

局部几何错位以重绘处理；有限配准和局部色差匹配仅针对已有结构，并保存参数、遮罩、校正场与实看证据。片段不计完整4K，已有历史检查不能自动扩大为本次全块通过。
