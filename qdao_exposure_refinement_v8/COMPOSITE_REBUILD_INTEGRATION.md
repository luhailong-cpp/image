# 已暂存复合图重建接入

## 执行位置

在 `refine_library.py stage` 全部完成、`processing.json.status=staged` 后，发布前运行：

```powershell
python qdao_exposure_refinement_v8/tools/rebuild_staged_composites.py
```

可传 `--node` 或 `--sharp` 指向已安装运行时。模块不编辑 `refine_library.py`，不安装依赖，不调用任何图片 API，不写正式素材或原始备份。1.1 版完成 25 个候选、20 个 staged 文件、31 条记录的完整重建；1.2 版随后仅对全库验收指出的 9 个 staged 文件、13 条含别名记录补充极薄边缘保护。正式原文件未修改。

## 范围和来源

读取 `svg_raster_pairs.json` 的 21 个 SVG 派生 PNG 候选，加上其中记录的 4 张旧 RGB 选服别名。当前 `processing.json` 中合计 25 个显式目标、20 个原始 SHA 分组、31 条包含复制别名的记录。

21 个直接候选包括两张控件总览、两张 HUD、八张旧透明分层与兼容别名，以及九张带 viewBox 比例适配的高分辨原子控件。`svg` 输入由正式路径映射为 processing 记录中的 staged 文件；SVG 型 overlays 同样复用 staged。需要缩放的栅格道童 overlays 则从 backup 按原尺寸、原插值核缩放，再应用冻结清单中的同一个 character 曲线，避免 Lanczos 负权重反向抬高邻近暗像素。`png` 改为对应 backup 文件，作为原尺寸、模式、alpha 和透明 RGB 合同。调用已有 `render_svg_pairs.mjs`，产物只放 `review/rebuilt/svg_pairs/`。

四张旧 RGB 选服图由同一配方重建：2560×1080 主城 + 原有 `#EFF5DA`、25% 遮罩 + base SVG、右上角道童、controls SVG 的合成层 + 原文字 labels SVG。道童设计位置仍为 `[2042,30,310,310]`。脚本先用全部 backup 来源重建原版，要求与原图逐像素一致，才接受 graded 来源的新合成结果。

## 验收和失败行为

对每个唯一结果逐像素检查：画布、RGB/RGBA 模式、alpha、完全透明像素的隐藏 RGB。所有可见像素的 sRGB 加权亮度与线性亮度都不得高于对应原图，并检查与全库验收定义相同的新增压黑像素（alpha>0、原 sRGB 亮度≥8/255、新亮度≤1/255）。任何增亮都会记录数量、最大幅度及最多八个坐标和前后 RGB，并使本轮失败；模块不使用 `min` 或钳暗修饰合成错误。

所有候选通过后才开始替换 staged 文件。出现渲染、原版配方、增亮或透明度问题时，原 staged 文件及 `processing.json` 保持原样，详细结果保存在 `review/rebuilt/composite_rebuild_report.json`。

## 别名和处理清单

依据 `original_sha256` 处理全体别名；同 SHA 的不同候选若生成不同 bytes 会失败。通过后把每个 SHA 的统一输出写回所有对应 staged 路径，并更新该 SHA 的每一条 processing 记录：`output_sha256`、`changed`、`composite_rebuilt=true`、`recipe`。`status` 保持 staged，随后可沿原流程验收和发布。

写入目标严格限制在 `v8/staged/`。原图和 backups 只有读取权限逻辑。替换前写事务清单 `review/rebuilt/composite_rebuild_transaction.json`；若中途终止，再次运行会核对原/新哈希及 processing 清单哈希后完成原事务，避免清单与部分 staged 文件不同步。`processing.json` 使用临时文件原子替换。

## 已完成的独立检查

语法检查通过，内嵌 Node 合成代码通过 `node --check`。小型临时 PNG 检查覆盖合法降亮、单个增亮像素、alpha 改动、隐藏 RGB 改动、RGBA/RGB 模式改动、RGB 原样及禁止将备份作为 stage 写入目标；全部通过。检查未读取未完成的 stage 作为重建输入，也未改 processing 或正式素材。结果见 `review/composite_module_selftest.json`。

原始 21 个 SVG 重建配方此前已验证为 PNG 字节 SHA 完全一致，基线见 `svg_raster_pairs_baseline_direct.json`、`svg_raster_pairs_baseline_layers.json` 和 `svg_raster_pairs_baseline_wrappers.json`。


## 1.1 修复与本轮执行结果

1.0 版第一次运行有 10 个候选失败，全部位于右上道童区域。原版配方仍能逐像素复现，源 hero 的 RGB 从未增加且 alpha 完全一致，因此不是资源错配或布局错误。最小 620×620 复现显示：先调色再 Lanczos 缩放会产生 6604 个增亮像素；负插值权重使邻近暗色反向抬升，低 alpha 的反预乘进一步放大未预乘 RGB。旧 RGB 屏幕最大亮度增加约 2.7152/255，不能用 1/255 容差忽略。

修复仅改变栅格 overlay 的处理顺序：原素材按原始内核和目标尺寸重采样，再应用同一冻结 character 曲线一次。坐标、尺寸、插值核、alpha、文字和合成配方保持原状；不再对已调色的 1024 hero 做第二次重采样。310、620、1240 三个最终尺寸共用此规则。修复后没有放宽零容差，也没有逐像素钳暗。

完整重建已通过：25 个候选的 sRGB 增亮、线性增亮、alpha 差异及隐藏 RGB 差异均为 0。20 个 staged 文件的哈希与更新后的 31 条含别名记录全部一致；31 个正式原文件的哈希仍等于原始 SHA。处理清单记录版本 `staged-svg-composites-1.1` 和具体源处理顺序。

诊断与执行证据位于 `review/rebuilt/`：`diagnostic_resampling/diagnosis.json`、`composite_rebuild_failed_original_order.json`、`composite_rebuild_report.json`、`composite_post_commit_verification.json`。诊断图片明确留在 review 下，仅用于回归比较，绝非正式素材。

## 1.2 极薄边缘保护与增量执行

全库验收指出 9 个复合组共 1,696 个新增压黑像素。实际检查表明全部 alpha 为 1、2 或 4；原 RGB 为 255、127、63 的通道组合，重建后归零。PNG 保存未预乘 RGB，一个预乘码值会在 alpha=1 时反预乘成 255，在 alpha=2/4 时成为 127/63，所以原裸 RGB 亮度多数很高，不能用原裸亮度≤.055 表示这些像素。它们的每通道实际预乘贡献均不超过一个 8 位色阶。

新增 `preserve_quantized_edges` 仅在原图满足 `1≤alpha≤4` 且 `max(R,G,B)×alpha≤255` 的像素保留精确原 RGB；所有透明度和位置保持原状。此 mask 由原图确定，同样保护未完全变黑但丢失某个色彩通道的边缘。超过一个预乘色阶的差异会被拒绝。它没有放宽验收阈值，也没有钳暗像素或改变正常高光。

本轮通过以下增量入口执行，只更新现有全库验收指出的复合组：

```powershell
python qdao_exposure_refinement_v8/tools/rebuild_staged_composites.py --repair-quantized-edges qdao_exposure_refinement_v8/staged_validation.json
```

结果：9 个 stage、13 条含别名记录更新，3,650 个极薄边缘像素恢复原 RGB，其中 1,696 个新增压黑全部归零。严格 sRGB/线性零增亮检查、全库验收同口径的压黑与暗部保留指标全部通过。额外逐像素验证证明 mask 外相对 1.1 结果完全不变，mask 内精确等于原图，alpha 完全不变。839 个唯一 staged 文件的 SHA 均与 processing 一致；未选中记录没有变化，13 个受影响正式原文件仍是原始 SHA。

真实 wrapper 最小验证先复现 2 个压黑失败，再确认保护后通过；合成边界验证保证 alpha>4、贡献>1色阶和普通不透明压黑不会被保护，过大差异会拒绝。证据：

- `review/rebuilt/composite_shadow_diagnosis_v1.2.json`：所有错误的 alpha、原/新 RGB、亮度、坐标和范围。
- `review/rebuilt/edge_repair_v1.2/protection_selftest.json`：真实与边界最小验证。
- `review/rebuilt/edge_repair_v1.2/post_commit_verification.json`：mask 外精确不变、全 stage 哈希一致、正式文件不变。
- `review/rebuilt/composite_rebuild_report.json`：当前 1.2 增量修复的前后严格检查及通用指标。
- `review/rebuilt/composite_rebuild_report_staged-svg-composites-1.1.json`：原 1.1 完整重建报告，独立归档保留。

新增保护已接入完整重建入口，后续完整重建也会采用同一规则。当前只做过上述 9 组增量写入，其余 stage 没有重编码。
