> 2026-09-17最新指示：用户已允许内置GPT Image 2，并指定9adcf929原人物包。新美术基线/16帧工作转入 `../qdao_original_roster_v13`。此目录保留之前吕洞宾专用准备、已通过代码测试和真实V12基线，不继续冒用它的原64奇数帧规则处理另一套人物。

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

Unity使用本任务独占副本`E:/work/tmp/qdao-v13-verify-20260917`。实际输入快照是[run3完整快照](runtime-validation/input-snapshot-run3.json)，包括4690个保存文件及逐文件SHA。完整结果见[验证汇总](runtime-validation/summary.json)与[验证范围说明](runtime-validation/README.md)。

- 本次最终运行：EditMode **300/300**，PlayMode **20/20**，均0失败、0跳过。之前失败的两轮记录保留，未覆盖。
- 真实天墉城沙盒中，八位角色实际均为V12/8帧，八向资源完整、独立idle正常。吕洞宾真实控制器速度9、周期约480ms、周期距离4.32世界单位；实际移动约4.8单位，观测到8个姿势并回到站立图。[实际场景截图](runtime-validation/contract-run3/city-captures/tianyong-24_lu_dongbin.png)
- 16帧新代码的时序、同ID降级、缓存和停步行为由测试覆盖；16帧测试素材仅在内存生成。**这不是新64张过渡动作已绘制或真实V13已运行的证明。**
- 输入复核发现隔离场景运行使动态字体`QdaoBody SDF.asset`变化，已记录前后SHA；正式工程同时有其他任务的UI/地图改动，均保留且不宣称在本次快照内验证。未来发布前必须完成新输入快照与一致性验证。
- 浏览器对比预览脚手架47项检查通过，72张既有动作/idle可载入，64个新增位置明确缺失；不是完整V13动画视觉验收。

后续必须完成真实64张补绘、先S/E自检、再其余六向、全部16帧视觉与数值核验，使用真实新素材在隔离Unity里运行，然后按对应SHA发布到正式V13目录并验证。V12全套保留可回退。后续步骤见[继续任务说明](CONTINUE_V13.md)。
