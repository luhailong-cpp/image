# 继续吕洞宾16帧及补充道童任务

这是未完成任务的接续记录。原要求位于 `E:/work/image/qdao_chibi_roster_v12/NEXT_TASK_LU_16_FRAMES.md`，本任务0/64新增绘制，未正式启用V13。不要重复初始化覆盖已保存成果。

1. 后续绘图先读[统一设置](../config/image-generation.json)与[执行策略](../docs/IMAGE_MODEL_POLICY.md)。用户已授权内置生图，2026-09-18 已核对官方新版开放公告；原 planning 中因旧帮助页产生的模型待确认项已撤销，不继续阻塞内置绘图。API 单独计费授权不变；角色基线和此目录是否继续使用仍按当前任务指示。
2. 同时确认补充道童的基线选择：用户点名的 `character_move_8dir` 为4帧大头短身版，游戏已有不同身形的8帧版。详见extra-character-baseline-audit.md和comparison。两者不能混用；当前游戏周期约615.38ms，16帧保持步频需要约38.46ms而非30ms；指定4帧版补至16需96新帧。
3. 已冻结吕洞宾V12的64张walk到奇数位置，8idle与portrait逐字节保留；48张A/B/idle参考板准备好，提示方案在planning/lu-inbetween-prompts.md。先看S/E参考，授权后生成真正过渡动作，保存实际工具响应、原图、提示词与来源SHA。不得复制/变形旧图冒作新动作。
4. 按tools/README.md的batch格式导入，整格统一归一化、透明清理和整数平移。先完成S/E各16帧并以正常/放大播放审查；针对问题重绘。合格后完成其余6向。奇数旧图、肖像、idle均不改变。
5. assemble、同步preview与独立verify覆盖全部145PNG及来源链。人工视觉记录要具体检查承重/穿插/配饰/帧15→16→01。完整合格后才执行approve.py封存验收状态与SHA。
6. 客户端核心代码已实现，当前正式资源仍V12。实际验证run3为300EditMode+20PlayMode通过，仅V12真实资源和内存夹具。测试副本 `E:/work/tmp/qdao-v13-verify-20260917` 与完整输入、真实V12速度基线均保存。请读runtime-validation/README.md，不把旧结果当V13。
7. 完整素材通过后按tools/PUBLISH.md暂存到隔离工程。其他任务仍在修改正式项目，刷新相关代码时保留他们工作。记录完整真实输入快照，处理并如实记录Unity动态字体的运行后变化，再跑两个平台并观察真实V13/16帧及其余7位V12。需与真实V12 baseline比速度/周期/FramesPerUnit、核对完整库存与条带8192导入。
8. 只有真正V13验证通过后，按同一候选SHA执行正式publish；它应保留V12、旧V13备份与GUID、最后写appearance.json。继续正式接入验证及最终截图/报告。脚本默认dryrun，当前从未approve/stage/publish。

本轮场景测试输入文件自身不再修改。V12源图和现有正式启用状态不覆盖。V13预览服务曾在localhost:8873运行，仅展示不完整状态；若端口失效可按tools/README重启，只服务V13目录。
