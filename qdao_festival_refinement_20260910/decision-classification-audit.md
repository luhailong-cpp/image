# 决策分类独立审计

发现 4 类需要更正的分类/理由，另 1 个发布入口漏项已由根任务在审计期间修正。此审计只核对来源和用途，不对仍在修补的 v9／28 做最终图片哈希结案。

|项|发现与处置|
|---|---|
|DCA-01|何仙姑 walk_NE_correction1.png、walk_SE_correction2.png 被称为未选候选，实际上当前 manifest 的 NE/SE selected_frame_sources[3] 选中了它们。补索引并保留为现行原生来源记录。|
|DCA-02|27 的 cardinal_assembled.png、diagonal_assembled.png 是 compatibility_assembly 指定的当前 4×4 兼容派生。应随已处理帧校验/重建，不能归未选原图。未在当前 edge_exports 发布记录中看到这两项，本审计不判断实际像素是否过期。|
|DCA-03|v10-preview 的桌面／手机四截图是当前展示导出，不能沿用历史排除理由。保留为 current preview evidence；输入变化则重新浏览器渲染，不直接修截图。v1/v2 旧稿的历史保留合法。|
|DCA-04|v7 icons/source/batch01–08 仍由现行批次记录映射全部 124 件物件。保留原图合理，但“都已被 v9/v10/festival 取代”的理由不准确，宜标现行原生来源证据。v7 UI 的历史归档有 README 与旧 builder 退出保护支持。|
|DCA-05|先前缺失/拼错选服与 prepared hero publication 入口；关闭审计时脚本已改用正确两条路径。随后重建 ledger 即可。|

通过的部分：6 张 v10 母图明确作为当前视觉来源保留；112 张当前 v10 fallback 派生由字节等同性进入 retain_derived；49 张冻结 contracts 输入按 README 保持；已索引的 94 张 v11 来源／加工输入使用 retain_source_record 合理；属性 v1/v2 历史页面有明确文档依据。

精确路径、manifest 字段、规则和逐项建议见 [JSON](decision-classification-audit.json)。只写本审计两份报告，未修改分类脚本、库存、图片或交接文档。
