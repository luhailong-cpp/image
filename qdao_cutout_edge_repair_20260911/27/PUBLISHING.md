# 27 当前批次的受保护发布

本文件及 `tools/publish_approved_batch.py` 是发布辅助，不代表 51 个媒体已经通过验收。工具不会自动发布。

当前生产目录：`qdao_chibi_roster_v11/27_ink_kite_ranger/`。原始 99 个文件的基线在 `production-baseline.json`；准备与发布时均检查每个原 SHA。发现并行变化即停止，不覆盖新版。

最终视觉入口为 `staged-v2/processing/final-visual-approval.json`：

```json
{
  "schema": "qdao.visual-approval.v1",
  "status": "approved",
  "approved_utc": "UTC timestamp",
  "reviewer": "root",
  "files": [
    {"path": "portrait.png", "sha256": "actual current SHA-256"}
  ]
}
```

`files` 必须严格包括 51 个相对 `staged-v2` 的媒体路径：1 立绘、32 单帧、8 strip、8 GIF 和 2 张 4×4 表。示例仅展示结构，不是有效审批。这里的 approved 表示本任务视觉验收，不要求用户重复确认。

准备前应由制作任务完成 `generation-final.json`，`records` 包含 9 个最终接受的处理输入，逐条按输入 `sha256` 匹配。

- 原生输入：真实 `source`/`sha256`、`prompt_file`/`prompt_sha256`、原生尺寸与参考来源。`prompt` 若为正文不会当路径使用。
- 拼接输入：`source_type: "assembled_2x2_from_native_generations"`、`assembled: true`、`native_generation: false`。顶层画布尺寸不计作一张原生生图。
- 拼接输入的 `generation_lineage.frames` 包含 4 条 `raw_source`、`raw_sha256`、`raw_native_size`、`source_box`、`whole_canvas_scale`、`target_box`、`prompt_file` 与 `prompt_sha256`。
- `generation_lineage.raw_artifacts` 明确每张实际原生图的 `path`、`sha256`、`native_size`、`prompt_file` 与 `prompt_sha256`。这些路径相对本修复批次目录；文件必须真实存在。工具复制到正式 `sources/frame-originals/` 与 `prompts/frame-originals/`，并重映射当前引用。
- 拼接输入没有单一生图提示词时，工具生成明确标注为 assembly recipe 的兼容说明；逐帧真正使用的 AI 提示词原样保留。

执行顺序：

```powershell
python -X utf8 qdao_cutout_edge_repair_20260911/27/tools/publish_approved_batch.py inspect
python -X utf8 qdao_cutout_edge_repair_20260911/27/tools/publish_approved_batch.py prepare
python -X utf8 qdao_cutout_edge_repair_20260911/27/tools/publish_approved_batch.py publish
```

`inspect` 只检查并保存预检记录。`prepare` 必须在原画、处理记录和 51 媒体已齐且当前 SHA 视觉通过后运行，只在修复目录创建正式发布载荷与冻结计划。`publish` 才备份并逐文件原子替换。它再次检查审批 SHA、全部输入/输出 SHA 和生产基线，随后复核 51 媒体尺寸、32 帧脚点、strip/表格逐像素拼接、GIF 四帧及 120 ms 时长，并检查正式来源和提示词真实存在。

当前 9 个处理输入、使用中的提示词、逐方向 processing 与当前 manifest/STATUS/README 一并发布。旧 source/raw、rejected 候选及旧未用流程保留为历史。`sources/cardinal_assembled.png` / `diagonal_assembled.png` 保持兼容时更新为新帧拼接表，元数据明确其非原生生图来源。

当前重建入口是 `tools/process_new_batch.py`：先在修复目录暂存，再验收和受保护发布。正式目录旧 `assemble_directions.py` 等为历史流程，不能未经复核覆盖当前交付。辅助脚本不操作 Git 或实际客户端。

准备阶段还会复核完整发布载荷：拼接输入从保存的真实原画、source_box、等比缩放和 target_box 重新排版，与接受的 2×2 输入逐像素一致；逐帧 prompt SHA、原生尺寸与实际复制路径一致。assembly spec 与 helper 若在来源链中记录，会复制并校验。这些准备检查未通过时，正式文件不会被替换。

正式来源引用也复制实际参考图、参考图提示词与裁格记录；当前引用指向真实正式路径。原生裁格参考可按 source_box 逐像素复核。参考图片仅作为参考时，不增加 native_generation_count。
