# 来源文字与历史快照

本目录保留逐次生成/编辑提示词、实传参考、提交、回执、原生SHA、淘汰版本文字记录及审查报告。过程报告里的 `fileRetained: true`、`candidate_pending_visual`、`pending_parent_review` 是报告生成时的快照，不会追改历史来冒充当时已通过。

最终当前状态以角色根目录 `review.json`、`manifest.delivery.json`、`runtime_timing.json` 及 `frames/` 旁逐图记录为准。2026-10-03根窗口已查看全部14组按序连图、修正关键帧和浏览器正常/慢速预览；当前196张SHA核准在 `audit/root_visual_approval_20261003.json`。

原生、拒稿、加工中间图按用户保留规则清理；实际删除结果以 `audit/final_image_retention_20261003.json` 为准。删除前的原生实测、正式图像素重现与SHA绑定在 `audit/export_precleanup_snapshot.json`。历史图路径仅保留追溯，不作为当前预览入口；当前可查看图片全部在 `frames/` 与 `preview/`。

`audit/grounding-audit-20261003` 的部分坐标是本轮脚向修正前快照。当前NW02支撑高度改善见 `run/NW_foot_axis_review_20261003.json`；不要将旧坐标或鞋底中位数当作物理地面。客户端未接入、世界脚滑未测的边界仍有效。

历史生成、注册、审核脚本用于解释过程，不应自动重跑覆盖正式成品；尤其不要重跑指定旧source的报告脚本。日常核对用 `tools/verify_delivery.py`；重建预览用 `tools/build_preview.py` 或 `tools/build_review_media.py`。
