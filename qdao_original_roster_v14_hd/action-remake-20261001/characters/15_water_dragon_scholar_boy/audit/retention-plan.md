# 水龙书生图片保留与清理计划

仅准备清单，本工具没有删除功能，本次未删除图片。

计划时间（UTC）：2026-10-05T10:03:26.132533+00:00
当前交付技术检查通过：True

## 执行前置条件

- root 已完成当前选帧和实际静态审阅；动态未完成时保留当前入选原生设计，不宣称最终动态验收通过。
- 只从当前 runtime 刷新预览；不要全量重建已清理的旧 sources。
- 运行 final_delivery_check.py --write-report --write-retention-plan，技术错误清零，所有必要图片存在。
- 删除前重新核实计划中每条路径仍在角色目录内、SHA 未改变；实际删除由 root 负责。
- 删除后再次运行核验；历史原图路径允许缺失，但 runtime/当前预览/来源文字必须完整。

## 当前数量

{"presentImageCount": 355, "historicalAbsentCount": 885, "byDecision": {"keep_current_delivery_preview": 44, "keep_final_runtime": 196, "keep_current_design_input": 115}, "candidateDeleteBytes": 0}

196 张 runtime 保留；每组最新 contact、跑步主选 uniform960/slow、战斗 normal/slow、当前关键姿态图保留。HTML固定960ms/圈，保留正常、慢速和逐帧检查。

当前入选且仍在使用的原生设计在最新动态复核完成前保留；淘汰 sources 及历史 audit/review 诊断图列为删除候选。JSON 内逐图保存当前 SHA、原生成记录路径及模型/质量/参考文字。

历史来源文字不改写成“文件仍在”。清理源图后不能再运行依赖原生输入的 build_delivery；成品检查用 final_delivery_check，HTML/GIF可从 runtime 重建。

仅处理本角色目录，不处理宿主缓存、共享参考或其他角色。保留全部逐图 JSON、提示词、清理文字、交接文档与必要脚本。

## 缺少的必要图片

- 无

## 暂缓处理项

- 无

完整逐图路径、SHA、字节数和决定见 retention-plan.json。
