# 04 山岳守卫 · 最终库存与来源只读审计

快照时间：2026-10-03T20:20:04.134439+00:00。脚本仅读取正式PNG、sidecar、原生图、提示词、提交和回执；只在本目录写入文字审计结果。

## 技术核验

- 正式图 196/196：run128、hit12、attack24、cast32。缺槽 0，额外槽 0。
- 硬错误 0；字段规范提醒 15，详见下表与JSON。
- 逐张核对正式文件SHA、1024×1024 PNG RGBA、透明通道范围，与sidecar一致。
- 当前原生来源可用 196/196；原生1254×1254 RGBA及SHA已实测，符合原生至少1024要求。每张正式RGBA像素与全画布LANCZOS缩放原生的重现一致。
- 正式文件SHA重复组 0；RGBA像素重复组 0；原生SHA重复组 0。这只能排除完全重复，不证明姿态独立或动画合格。

## 模型与时间证据

- 196张配置目标均为 GPT Image 2.5 Sunburst / max。实际提交model/quality均null，实际返回型号/质量均null并说明未确认；未发现用配置目标冒充实际返回或使用不存在的型号质量选择器。
- 提示词、submission、receipt均存在；保存的提示词文本与提交内容一致。已有SHA字段均匹配。
- 未发现提交开始、完成、导出时间倒置。2份sidecar开始时间为null（attack E01/E06），submission仍留attemptedAt边界；不补造精确出图时间。
- 11份hit的generatedAt来自PNG C2PA文本候选；记录已注明未独立验签，不据此确认型号或质量。

## 来源链与已清理历史输入

- 历史输入引用按出现次数：775项仍有相同字节；61项正式路径后来换版、旧SHA均有retired记录；14项旧PNG已删除，均能查到历史来源及cleanup文字记录。
- 上述历史输入可用性不等于当前原生来源缺失。当前196张nativeSource均在；审计未删除或恢复任何图。
- 证据文件的现算SHA已写入本审计JSON；原始sidecar/submission/receipt保持不动。

| 正式槽 | 缺少独立SHA的记录 | 审计现算SHA |
| --- | --- | --- |
| frames/hit/E/frame_01.png | prompt：provenance/hit/E_frame_01_20261002_attempt02.prompt.txt | `764795c19a543772d4e49372ff1d017fbee3469d3332a36834514a07b4413b9c` |
| frames/hit/E/frame_02.png | prompt：provenance/hit/E_frame_02_20261002_attempt02.prompt.txt | `c155d2c53a75e6b2db85313b450111dba47605bf72c81e91b2b8970b31693cbe` |
| frames/hit/E/frame_03.png | prompt：provenance/hit/E_frame_03_20261002_attempt05.prompt.txt | `cf3300b1194e93fceebc305319aeec8c5e26a2387594fd273ffcdf212adbed27` |
| frames/hit/E/frame_04.png | prompt：provenance/hit/E_frame_04_20261002_attempt03.prompt.txt | `d2f78901a75f655fa5ab183c960b0ebabb9469f83ef7bd9861ae9a8a31519463` |
| frames/hit/E/frame_05.png | prompt：provenance/hit/E_frame_05_20261002_attempt01.prompt.txt | `c8b438cc9507ba64341b27f861ae6cc2fba18c909c27d26633815cf004e1cec3` |
| frames/hit/W/frame_01.png | prompt：provenance/hit/W_frame_01_20261002_attempt02.prompt.txt | `acdb10ae88cf3c7f83c5d3ea0dab6d93740ec3eb1b0df7c56ff66c65503f3bbc` |
| frames/hit/W/frame_02.png | prompt：provenance/hit/W_frame_02_20261002_attempt01.prompt.txt | `0a24a060a41a16b10c21c9a9d252f92e1ee37fa7d216808d14c64f7955cda666` |
| frames/hit/W/frame_03.png | prompt：provenance/hit/W_frame_03_20261002_attempt02.prompt.txt | `2696325730f517f44638523a21c9458c8f48bc49da41b05080ff3fde3b4f5c78` |
| frames/hit/W/frame_04.png | prompt：provenance/hit/W_frame_04_20261002_attempt01.prompt.txt | `f63cb38fd4f36fc223dccee5dfe18c17a2590c6ff2f667b06b63fa24064b2321` |
| frames/hit/W/frame_05.png | prompt：provenance/hit/W_frame_05_20261002_attempt01.prompt.txt | `2716ce3c630210d458c308a3454486b186004318ac70fde4e4b07353afec4142` |
| frames/hit/W/frame_06.png | prompt：provenance/hit/W_frame_06_20261002_attempt01.prompt.txt | `d6302be3dd2cbd42d69b38a0e92670cf31edeeda8cf3bfbe1901195bec41bf32` |
| frames/run/NW/frame_04.png | submission：provenance/run/NW_04_attempt_03.submission.json | `33d81a9aed21a8418cb12e94bb736223e878c2351be1d250a926f2adb3cf4eb2` |
| frames/run/NW/frame_04.png | receipt：provenance/run/NW_04_attempt_03.receipt.json | `cc5d1f9c3919ec9182b85d38b5994986b4d3f902e921e68827e61b2ddb1af1c0` |
| frames/run/W/frame_04.png | submission：provenance/run/W_04_attempt_03.submission.json | `a68aa2d5b91f9b973a915b09fbce96c6b57ef555f021bfb1ff3ed28fc3aa0043` |
| frames/run/W/frame_04.png | receipt：provenance/run/W_04_attempt_03.receipt.json | `47e3a93df498df17754bc7a0407c1eb1a1b2bbc474658542f3d83aabe64aeb20` |

## 边距诊断与实际查看

alpha>0边距≤8px有158张；154张最外边存在低透明度像素，最外边alpha最大仅27/255。不能用最低非零alpha像素判断脚着地或主体被裁。

| 槽位 | alpha>127右边距 | 实际查看 |
| --- | ---: | --- |
| frames/attack/E/frame_05.png | 3 px | 杖首金色尖端距右边窄，但尖端完整，未见主体被画布平切。 |
| frames/attack/E/frame_06.png | 5 px | 杖首金色尖端距右边窄，但尖端完整，未见主体被画布平切。 |
| frames/run/SE/frame_12.png | 8 px | 待实际查看 |
| frames/run/SE/frame_13.png | 5 px | 盾下流苏靠右，外沿完整，未见主体被画布平切。 |
| frames/run/SW/frame_04.png | 1 px | 盾下流苏靠右，外沿完整，未见主体被画布平切。 |

这4项为窄边距提示，当前观察不构成切断阻断。没有以阈值自动批准美术。

## 节奏、状态与交接边界

- sidecar快照状态：{"candidate_pending_visual": 83, "visual_passed": 113}；这是声明统计，不自动补写通过状态。
- sidecar帧时长统计：{"attack/30": 24, "cast/45": 32, "hit/40": 12, "run/30": 98, "run/None": 30}。run有30张显式runTiming试播记录；旧30ms字段仍有98张。最终交接须明确480ms旧基线、640/720/800ms试播与客户端值未确认。
- 当前manifest已将run480标作legacy_480_baseline_trials_pending、客户端跑步时长null。网页默认720ms明确标作待审。战斗240/360/720ms为规格值；这不是客户端实测通过。
- 196张根锚点(512,928)为声明的画布目标，未做实际骨骼/根点像素校准；不得据此声称完成客户端注册。
- 所有客户端状态均未接入。完整动态、根位置及接地感由根窗口继续验收，本审计不将数量/SHA/PNG格式等同动作通过。
- 审计快照后如有新图替换或sidecar统一，需要重跑本目录final_inventory_audit.py刷新结果。S02/S03已核对当前attempt02（3c59e675… / a5e09a06…）。
- 本快照W03：`9bcc956c225500ba17610512db9585e94532aa735ee1f0b1f5f9967d0afb33da`，原生`provenance/run/W_03_grounding_final01.png`。后续替换版本不在本快照范围。

[完整逐图JSON](final_inventory_audit_20261003.json) · [可重跑只读脚本](final_inventory_audit.py)
