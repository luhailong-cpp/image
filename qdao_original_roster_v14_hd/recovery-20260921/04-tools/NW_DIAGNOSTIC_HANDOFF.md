# 04 NW追加处理/诊断交接（2026-09-21）

本文件是本子任务当前入口，补充 RESULTS.md 的首批处理结果。公共管线、canonical候选、旧receipt和正式资源都未修改。新图片由主代理明确授权的内置工具生成，实际型号为host-managed-unverified；本子任务累计新增4次内置调用、0次收费API。

## 最新NW16槽取图映射

| 槽 | 使用来源 |
|---|---|
| 01/05/09/13 | V13/candidate/04_mountain_guardian_boy/walk/NW 原512文件，保留字节 |
| 02/03 | V14/candidate/04_mountain_guardian_boy/walk/NW 原已导入1024 |
| 04 | `recovery-20260921/04-generation/NW04-edge-v4/staging/candidate/04_mountain_guardian_boy/walk/NW/04.png`，由audit_05提供 |
| 06/07 | `04-tools/staging/candidate/04_mountain_guardian_boy/walk/NW`，edge-v2 |
| 08/10/11 | 同上，历史归档原图本机处理 |
| 12/14 | 同上，equipment-v2 |
| 15 | 同上，**NW15-pose-v3**，取代equipment-v2步态 |
| 16 | 同上，主代理NW16-pose-v3 |

**不能直接整树采用04-tools/staging：该树的NW04仍是已拒绝的edge-v2放大版本，必须用上表audit_05的独立v4覆盖选择。** 原处理树保留了每一次来源和拒稿；没有以新图删除旧证据。

## 三张法杖修复

本代理先目视每张NW12/14/15目标raw及历史NW11 raw，确认新三张把本来棕金实心底盘误画成透明镂空。各执行一次内置精准编辑，仅补回大型金环内棕金底盘，挂在下方的小玉环孔继续透明。

各归档位于 `recovery-20260921/04-generation/NW12-equipment-v2`、NW14-equipment-v2、NW15-equipment-v2；均含真实actual_request、精确prompt、原output_hint/default路径、复制的raw、provenance。原工具输出保留。三张原生1254，独立重建输出1024且不放大。

深浅底实际检查确认底盘恢复；人物比例基本保持。固定.84后主体高度12为799→800、14为781→783、15为798→800；body_scale变化分别+0.45%、+0.65%、+0.72%。详见 `review/equipment-v2-analysis.json`。这些编辑没有刻意改步态，故NW15在此阶段仍是高抬旧姿态，不能以装备修复代替走路批准。

## NW15步态修复（本阶段允许最多2次，实际仅1次）

主代理追加明确授权后，以NW15-equipment-v2为编辑目标、NW16-pose-v3为下一帧脚位参照，新生成 `04-generation/NW15-pose-v3`。左侧盾腿小腿伸低，左靴转为朝下，仅余薄鞋底；右侧承重靴保持落地，上半身和法器保持。

原生1254，.84统一处理后1024。主体高800→799，body_scale+0.268%，脚锚[512,942]。深浅底目视未见连续亮紫残边。独立单帧像素重建通过；没有复制或镜像相邻姿势，也没有程序插帧。输出SHA：

`30f6e596a78df07994d9431ea1ac815873a183aa3c63cb1634fd6a87edcef96a`

证据：`review/NW15-pose-v3-analysis.json`；来源绑定及结果在 staging角色树 `recovery-bindings/NW15-pose-v3-local-20260921/`。替换前的staging PNG、source record、manifest/qc/validation已在 `history/20260921T131903529904Z-NW15-pose-v3-local-20260921` 保存，旧source/processing批次仍在。

可进入新的完整循环审核；**未批准整个NW方向或人物**。已通知主代理与audit_06采用此版构建新review snapshot。

## NW16

原NW16-single-v1既有法杖镂空问题又呈双脚离地，应拒收。主代理NW16-pose-v3已实际归档/处理，右靴落地、左靴接近接触且未露出大底，法器底盘恢复。新输出SHA：

`08e8c76bc7eccb0557d87ccd9ef4b1306926ceb8f19f56befc0e90f20272dd4d`

本代理只负责其归档prompt/provenance、处理、单帧重建和深浅底检查；生图由主代理执行。旧v1与主代理v2拒稿都保留，不用它们完成槽位验收。

## 诊断预览与明确版本边界

- `NW-diagnostic-v1`：初始图集/GIF有效；HTML有window.frames名称冲突及字符串换行语法问题。
- `NW-diagnostic-v2`：修正frames冲突，但HTML仍有真实换行引起的SyntaxError；**此HTML不可用，也没有播放通过**。静态图集/GIF仅用于当时问题定位。
- `NW-diagnostic-v3`：生成器改raw HTML字符串并显式绑定DOM元素，完整内嵌JS经Node语法解析通过。
- `NW-diagnostic-v4`：包含NW04-edge-v4、12/14/15 equipment-v2、NW16-pose-v3；JS另经实际 `node --check` exit0，证据 `preview-validation.json`。深浅GIF逐项检查16帧、各30ms、总480ms，像素来源/SHA见diagnostic-manifest.json。主代理消息确认已在其真实浏览器打开v4并播放，帧号/图片变化正常。本子任务CUA查不到可用浏览器，因此不冒充本子任务实际浏览器验收。

**v4内部NW15是修步态前equipment-v2。最新NW15-pose-v3不回写旧预览；audit_06将另建新snapshot供主代理审核。** 早期诊断图的REVISE文字反映当时修图计划，不是当前批准状态。

生成器只读取真实PNG、按512/52与1024/104相同世界几何显示；为预览缩放、GIF色板和背景合成不生成新的动作素材，不把旧512输出改成高清。每个原文件路径/SHA和实际尺寸有记录。

## 验证边界

本阶段单帧重建通过与完整动作视觉通过分开。单次validation绑定导入当时manifest，后续增/换帧会令旧manifest字段过时，新review snapshot应重建当前集合；不能拿先前单帧报告直接作为新整个方向通过。

历史receipt的E:/与旧luyua默认原图路径迁移限制仍存在；本辅助保存真实迁移映射，没有修改旧回执或假造严格mixed assembly通过。整个04仍需SW补槽、全8方向30ms连播/首尾衔接与素材验收；无stage、Unity或正式发布结论。
