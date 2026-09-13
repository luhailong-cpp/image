# Decision classification audit

只读检查完成；仅更新本审计 JSON / MD，未修改图片、生产元数据、inventory 或 decisions。未替 v9 / 28 补修作最终哈希结案。

`decision-classification-audit.json` 的 `corrections` 数组包含 19 个唯一精确路径，均带 `path`、`decision`、`reason`、当前 `sha256` / `expected_sha256`、权威文件及字段，可供根任务合并：

- 2 张何仙姑 NE04 / SE04 实际选用的原画细胞源 → `retain_source_record`，与 manifest 声明哈希一致。
- 2 张 27 号兼容组装 → `retain_derived`。2048×2048 RGBA 与当前 32 张 512 帧按 manifest 方向顺序逐像素拼接完全一致；自身文件哈希也与 manifest 一致，不需重建。
- 8 张 v7 icons/source 原始图板 → `retain_source_record`，仍是现行 124 图标的记录来源。当前文件哈希与旧 records 的 raw_sha256 均不同：本报告保留两者并明确旧字段不能用作当前绑定，不改原始记录，也不据此断言图片失效。
- 4 张当前属性 v10 浏览器截图 → `retain_current_evidence`，保留当前证据身份，输入变化后重新渲染，不能绘改截图。
- 3 张韩湘子当前 QC 明确引用的检查图 → `retain_current_evidence`。QC 以路径关联，没有逐检查图哈希；本报告仅捕获当前字节哈希，不补造生产者视觉验收。

27 号 `compatibility_27_verification` 保存全部 32 个帧路径及哈希、两组行顺序和完整像素结果。旧 visual approval 中 8 条 review_evidence 路径在本检出中缺失，已单列为旧证据可移植性限制；不把它描述为当前 51 媒体失败，也不猜测替换成其他联系图。

正确保留的历史范围包括：v7 已归档 UI、v10 冻结 contracts 输入、属性旧 v1 / v2 预览，以及当前 QC 明确列入 historical_visual_review 的旧检查图。6 张 v10 母件、112 项已证实一致的派生和 94 项已被正确索引的 v11 来源未发现同类误排。

发布清单漏读路径已由根任务在脚本中修正；本审计不代运行最终账本或刷新全库哈希。
