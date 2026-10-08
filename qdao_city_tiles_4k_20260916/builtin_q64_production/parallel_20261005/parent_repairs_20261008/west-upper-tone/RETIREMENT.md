# 素材保留与历史路径状态

2026-10-08 按用户素材保留规则，计划仅保留 `final-output` 的两张最终候选、`final-qa` 的八张原尺寸检查图、当前 `final-joined.png`，以及安全迁移需要的原始局部 `context.png`、`mask.png`、`trim-mask.png`。逐个路径、清理前 SHA-256 和实际可用状态见 `retirement.json`。

实际状态：自动审批以 `blocked by policy` 拒绝了受限清单删除和单个绝对路径删除，**尚未删除任何图片**。当前 30 张 PNG 全部仍在，16 张仅标记为待退休；没有完成后的删除校验报告。

待退休的原始生成、拒稿和加工中间 PNG 已由最终像素替代，批准清理执行后无需保留图片备份。所有既有 provenance、prompt、receipt、manifest、review、generation record 和脚本文字原样保留。历史记录中的旧图片路径表示当时的来源身份，不是当前交付的运行依赖；图片是否仍可用以退休清单实际状态为准。

`assemble.py`、`prepare_trim_gap.py`、`finalize_review.py` 和 `trim-repair/crop.py` 均已停止使用，**不可再次运行**：其输入图计划退休，部分脚本可能先覆盖检查记录再遇到缺失输入。脚本仅作为历史方法证据保留。不要据此重建输出或重写已绑定 SHA 的记录。

后续迁移应使用保留的最终两图、原始局部、两张遮罩和记录的像素坐标，先验证输入 SHA，再创建新的迁移方案。现有通过范围仅为已检查局部；不代表整块、整城或客户端的正式验收。
