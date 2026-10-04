# 水龙书生图片保留与清理计划

仅准备清单，本工具没有删除功能，本次未删除图片。

计划时间（UTC）：2026-10-03T23:37:12.900435+00:00
当前交付技术检查通过：True

## 执行前置条件

- root 完成最终选帧与实际视觉/动态审阅；不是由本脚本自动认定。
- 最终运行 build_delivery.py --write --replace 和 render_sequence_previews.py；刷新关键姿态图。
- 运行 final_delivery_check.py --write-report --write-retention-plan，技术错误清零，所有必要图片存在。
- 删除前重新核实计划中每条路径仍在角色目录内、SHA 未改变；实际删除由 root 负责。
- 删除后再次运行核验；历史原图路径允许缺失，但 runtime/当前预览/来源文字必须完整。

## 当前数量

{"presentImageCount": 240, "historicalAbsentCount": 514, "byDecision": {"keep_current_delivery_preview": 44, "keep_final_runtime": 196}, "candidateDeleteBytes": 0}

196 张 runtime 保留；每组最新 contact、跑步主选 weighted720/slow、战斗 normal/slow、当前关键姿态图保留。均匀节奏比较继续由 HTML 直接读取 runtime，不必保留全部比较 GIF。

所有 sources 原图及历史 audit/review 诊断图在最终核验后列为删除候选；JSON 内逐图保存当前 SHA、原生成记录路径及模型/质量/参考文字。引用旧原图路径不构成永久保留像素的理由。

历史来源文字不改写成“文件仍在”。清理源图后不能再运行依赖原生输入的 build_delivery；成品检查用 final_delivery_check，HTML/GIF可从 runtime 重建。

仅处理本角色目录，不处理宿主缓存、共享参考或其他角色。保留全部逐图 JSON、提示词、清理文字、交接文档与必要脚本。

## 缺少的必要图片

- 无

## 暂缓处理项

- 无

完整逐图路径、SHA、字节数和决定见 retention-plan.json。
