# N / NE / W 独立静态复核

> 后续修订见 [N后续修复交接](independent-run-n-ne-w-followup.md)。本文件保留首轮审核与48帧旧源快照；最新推荐以followup为准。

审核范围为开始时 selected-new 的48个原生选帧。三个16帧拼图已全部实际查看，并回到疑点原图检查；拼图→导出帧→原生 SHA 链48项一致。没有浏览器播放或动态通过结论。

可交接静态候选：N06-v5、NE04-v6、W16-v4。N12-v3仅条件候选，N14-v1 / N15-v1仍有尾段尺度疑点，N组不能整体标通过。未发现明确多肢或葫芦换手。N/NE前后半圈支撑交替可辨；W侧面遮挡仍需动态确认。

| 槽位 | 原稿问题 | 本轮结果 |
|---|---|---|
| N06 | 后脑、耳距、发带和上背明显偏大 | v5恢复05/07尺度；v4仍偏大，拒用 |
| N12 | 头背、葫芦偏大 | v3更接近13，但尾段尺度尚未统一，只作条件候选 |
| NE04 | 头、耳、发带明显偏大 | v4错换腿；v5头过小；v6保留05尺寸级别及正确左右腿，可供静态合入 |
| W16 | 相比15/01头脸、眼耳、葫芦明显偏小 | v4使用01-v2固定尺寸，修复跳档；近地脚和16→01仍待播放 |
| N14/15 | 后脑、耳距和发带相对05/07仍宽一档 | 未扩修；头顶高度不作为判断依据，保留总控复核项 |

## 本轮原生文件与 SHA

- **generation/run/N/06-v4.png** — rejected_scale_drift
  - SHA256: `b11d05c37294e755024bf5989a8a90460cbedf1a9eadf6563deb245a61b4ac43`
  - 虽略减小，后脑、发带、耳距仍明显宽于05/07，不能当作尺度修复完成。
- **generation/run/N/06-v5.png** — preferred_static_candidate
  - SHA256: `553be0ef3d9520c4bda300b90b66cd0a3386aabb37d978f4d31d03b8501075a1`
  - 仅用05/07正确尺度图；头背、葫芦与05/07相合，右鞋底后翻、左脚跟离地，双脚腾空可读。屈腿导致人物总高变短，不据总包围盒误判整体缩小。
- **generation/run/N/12-v3.png** — conditional_candidate_tail_scale_unresolved
  - SHA256: `d58e7e8d6e2681b28a8001ad743cef23a2dd58ccdc82d2d3a7f74a98d9d53d1a`
  - 后脑和背心更接近13-v1，较12-v2改善；左鞋后伸、右脚前收。13–15尾段仍比05/07宽，不能声称全N组尺度已一致；接地临界和12→13需播放复核。
- **generation/run/NE/04-v4.png** — rejected_leg_swap_and_scale
  - SHA256: `5722997ec066e09f0b76cf326c36acd79dd6f840711662aacd2099d961a230b7`
  - 最低后蹬鞋移到画面左，左右腿身份交换；头部仍偏大。
- **generation/run/NE/04-v5.png** — rejected_undersized_head
  - SHA256: `d686ba5fc82e5863d3915a77782219bedae2b8512e4c3061f5a5fa9bb36ac743`
  - 保住原腿位但头缩小过度，上半身也发生上移；不采纳。
- **generation/run/NE/04-v6.png** — preferred_static_candidate
  - SHA256: `1b33a0019f1a4d5f6695f1cee3f3b9b3cd0701955b004dad2d8948cb8be3166b`
  - 用03-v2主底、05-v5相邻姿态；头背、耳部和葫芦接近05-v5正确尺寸，画面右的右鞋后伸蹬离，画面左的左膝前提，右空手向前摆。前掌接触/离地临界仍待动态。
- **generation/run/W/16-v4.png** — preferred_static_candidate
  - SHA256: `7697e2da0a40701e11b2d15712e1b9d897fbe04cce3b46c44de409db60ad337c`
  - 用01-v2固定头脸、眼耳和葫芦尺寸，修复旧16-v2明显偏小，保持前脚向前、后腿后收及空右臂反摆。16→01实际落地可读性仍待播放；不把近地几像素诊断冒充动态通过。

## 核验与边界

- 7张本轮原生图均为1254×1254 RGBA，与宿主输出逐字节一致；prompt、request、receipt、generation记录与引用存在，SHA匹配。
- 实际模型、质量均为未确认；仅保留本批配置目标，没有将提示词或配置当成实际返回值。
- 未改变 selected-new、manifest、任何导出文件或其他方向；没有逐帧缩放、平移或脚底锁定。
- 完整48帧原始审核快照、原生SHA、逐次失败理由及只读透明度边界诊断见同名JSON。

