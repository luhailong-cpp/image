# 年轻吕洞宾 V13：制作工作区

本目录正在制作，尚未发布。不要把工具准备、旧帧拷贝或程序测试视为64张实绘动作已经完成。

## 当前已完成

- 从批准的 V12 `candidate-stable-body/24_lu_dongbin` 接手，核实 manifest SHA `3dbc699023fd7fe6f45304fd91ecea2f088e107d4c727d375dc1b23c31e68c68`。
- 64张旧走路PNG按字节复制到新序列奇数位，8张独立idle与肖像按字节保留，共73张。[准备核验](setup-validation.json)同时检查48张参考板的192个源格。
- [手工补帧提示方案](planning/lu-inbetween-prompts.md)和每批A/B/idle参考板；第一批位于`references/S/first-half`。
- [处理与独立验证工具](tools/README.md)：完整格归一化、透明清理、整数平移、固定idle头部ROI、来源链、面积CV和16格条带。
- [8/16同步预览](http://127.0.0.1:8873/)可显示旧8帧和真实的待补状态。完整周期480ms；不填充缺失动作。
- 客户端加入独立V13=16帧/30ms契约、V13→同ID V12→V11回退、缓存修订、专用idle和窄范围8192条带支持，尚未启用新的素材版本。

## 当前等待

[本次模型核对](planning/model-resolution-20260917.md)发现官方内置入口仍标注GPT Image 2，无型号/质量选择参数；项目要求最新最高能力2.5 Sunburst。本任务已向用户询问：本次明确允许内置2，或授权2.5 Sunburst API最高质量单独计费。未收到答复前不进行依赖该选择的新增生图，不声称切换模型成功。

新增实绘帧：0/64。当前candidate的manifest/QC是incomplete；无正式V13 appearance.json。

## 补充道童

用户补充的实际目录是`E:/work/image/character_move_8dir`。它与年轻吕洞宾不同，且有两个造型不完全相同的基线：指定目录4帧大头短身版，和游戏现用8帧较瘦长版。见[基线审计](extra-character-baseline-audit.md)与[对比图](extra-character-baseline-review/baseline-S-E.jpg)。已询问基线；尚未对其做依赖选择的生图或接入。原4帧建议周期480ms；游戏8帧实际周期约615.38ms，不能同时声称强制30ms又保留其原步频。

## 本次验证

Unity使用本任务独占副本`E:/work/tmp/qdao-v13-verify-20260917`。源项目输入快照见`runtime-validation/input-snapshot-run1.json`。当前验证使用已批准V12素材和仅存在内存的16帧测试夹具；即使测试通过，也不是新动作已绘制或V13素材已启用的证明。各平台结果以本次XML和后续summary.json为准，不引用V12历史通过次数。

后续必须完成真实64张补绘、先S/E自检、再其余六向、全部16帧视觉与数值核验，使用真实新素材在隔离Unity里运行，然后按对应SHA发布到正式V13目录并验证。V12全套保留可回退。
