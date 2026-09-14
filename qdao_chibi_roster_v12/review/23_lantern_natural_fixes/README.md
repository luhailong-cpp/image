# 灯使自然步态候选（未发布）

角色：23_lantern_courier。仅在独立 candidate-stable-body 目录组装；未 seal，未发布。16 次内置 image_gen 真画，精修原审查指定的 19 张 walk。肖像与八张 idle 原画不变，保留雀斑圆脸、双辫、棉布披肩与实物纸灯的道家Q版身份，没有新增梦幻效果。

- 9 张头型：N01/05/06/07/08，W01/02，SW03/07；SW03同时恢复原参考上身尺度。
- 10 张低步态：E/SE/S/SW/W 的04、08；保留各格原本自由腿、支撑腿、空手摆臂与左手提灯。
- 45 张其余 walk + 8 idle = 53 原格 RGBA保持；正式原 source 与 portrait.png 文件SHA未改，见 source-retention.json。

北向头宽从147–179的两组变为178–183；W01/02从161变为181/183，同向其他帧172–179；SW03/07从176/179变为199/196，同向其余187–198。数字为源443等格头顶起100行的非洋红轮廓宽，不冒称脸部关键点。W05与SW05/06为原审查允许保留的小幅差异，继续在完整动画中复核，没有借机扩大重绘范围。

原画相位已经是 canonical anatomical RIGHT contact first，八向均结合01/05的髋腿遮挡与空手摆臂确认，并与原始相位提示交叉核对。未轮转，未镜像。phase-plan.json及两个phase-contact对比图保存依据。04是LEFT前伸、RIGHT支撑；08是RIGHT前伸、LEFT支撑。侧视不能只按画面前伸鞋在哪边认左右；提灯手始终为解剖LEFT。

低步态重画的自由大腿朝下、膝盖低于衣摆，鞋跟接近支撑地面。SW08二格首稿因髋部遮挡与04过于相似而排除，独立回原08重画，明确近LEFT支撑、远RIGHT低伸。E首稿以及SW08独立首稿脚跟仍较高，分别通过新原生绘制进一步降低。没有代码拉腿或合成复制步态。

原生图、提示、参考链、SHA、退稿与19个final-cell提取关系见generation-provenance.json。所有最终格都独立逆算为对应native-cell整幅等比LANCZOS到443方；无轮廓fit。每次绘制保留原生输出，未覆盖正式原图。

候选corrections.json仅列本轮19个新格；候选walk-*-original.png明确复制正式当前final原画作为基线（已包含历史正确修正），避免旧original回退。verify_rebuild_map.py已在内存重放装配规则，六张修改方向图逐像素重建一致。候选rebuild_candidate.py先重新拼装，再显式调用v3与独立verify；没有调用正式项目的旧rebuild.py。

处理参数：alignment-version3；沿用正式common scale1.0194174757281553；component-padding2；despill-radius4。全部72格共享同一个scale，只按同向idle固定头ROI整幅整数平移，world root(256,471)保持，允许脚底前后透视变化。最终导出状态与验收SHA在candidate-validation-summary.json生成后记录；数字通过不等于视觉封版。
