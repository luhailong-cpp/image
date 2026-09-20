# 2026-09-19 Python 与 JSON 清理

检查范围为 `E:/work/image`。盘点了约6,081个 Python/JSON 文件，合计约299 MiB；数量和大小为本轮扫描时的值，制作中的目录仍会增加文件。

本轮删除10个一次性Python补丁脚本、33个失效批次 `selected.json`，合计378.38 KiB。文件已从本地删除，Git删除已暂存；本轮尚未提交或推送。逐项路径、哈希、删除依据及恢复所需基准提交见[JSON记录](CODE_METADATA_CLEANUP_20260919.json)。

## 已删除的脚本

- `qdao_chibi_roster_v12/review/apply_he_idle_revision.py`
- `qdao_chibi_roster_v12/review/correct_ranger_diagnostic_canvas.py`
- `qdao_chibi_roster_v12/review/fix_preview_image_retry.py`
- `qdao_chibi_roster_v12/review/adjust_preview_overview_layout.py`
- `qdao_chibi_roster_v12/review/parameterize_preview_qa.py`
- `qdao_chibi_roster_v12/review/diagnose_preview_qa.py`
- `qdao_chibi_roster_v12/review/extend_approved_candidates.py`
- `qdao_gpt_image2_refresh_v7/ui/update_builders.py`
- `qdao_gpt_image2_refresh_v7/ui/update_docs.py`
- `qdao_gpt_image2_refresh_v7/ui/harden_writes.py`

这些脚本只对既有源码执行一次性字符串补丁或旧版本迁移。修改已存在于现行实现中，没有其他工具调用这些脚本；旧V7说明中唯一的引用已更新。实际构建器和验证器保留。

33份JSON来自原版V13已被替换的旧处理批次：对应目录已无阶段PNG，记录的阶段路径全部已删除，也不在现行 `frame-sources.json` 的依赖中。当前批次、源图、生成回执及阶段映射均保留；为这33个具体路径添加忽略规则，避免旧批次复现时重新跟踪这些过期清单。

## 需要保留

- `config/image-generation.json`、运行配置、UI文案：控制项目行为。
- `manifest.json`、`frame-sources.json`、来源/生成回执：描述素材文件、哈希、生成和处理来源。
- `qc.json`、正式验证结果和运行输入快照：记录验证范围，支持后续审查与重现。
- 构建、导出、发布、验收Python与测试：仍有实际用途。
- 正在制作的V14、主城地图及其他任务当前改动：未纳入删除范围。

检查了补丁效果、调用引用、失效批次与现行来源映射的互斥关系；删除后18个关键工具、配置与映射文件SHA-256未变。未执行会改写素材的脚本。临时扫描文件在完成记录后清除。
