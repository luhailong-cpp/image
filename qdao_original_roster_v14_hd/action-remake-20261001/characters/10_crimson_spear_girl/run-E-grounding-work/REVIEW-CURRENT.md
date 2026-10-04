# E跑步当前选图与动作复核

16槽当前唯一来源以selection.json为准。全部原生1254×1254 RGBA、每张独立内置生图、有逐图来源记录。当前为静态逐图与联系表审阅后选用，**不是用户最终验收**；正常动态预览由总任务继续核对。

- E01：far-left final push。Far LEFT back forefoot finishes push; near RIGHT knee forward. Rearsole native1174, heel raised.
- E02：right-leading rising flight。Both feet airborne, near RIGHT thigh forward foreground; trailing left folded, all soles <=1101.
- E03：right-leading flight。Near RIGHT front shin extends; far LEFT folded behind; soles<=1112.
- E04：right-leading pre-contact。Right foot descends, sole1151, about14px above common1165. Low pre-contact not high flight.
- E05：right initial contact。Near RIGHT in front contacting flat sole1163; far LEFT folded back.
- E06：right compression。06-v4 headscale matches neighbors. Near RIGHT thigh down in foreground covering far LEFT; right sole1168 flat, far left raised forward.
- E07：right late support。Near RIGHT rearward/down foreground thigh, heel begins raise and forefoot planted.
- E08：right push-off。Near RIGHT thigh remains foreground as leg extends rear, far LEFT reaches front behind.
- E09：right final push。Near RIGHT rear forefoot, far LEFT leading shin extended. Heel raised, toe direction EAST.
- E10：left-leading rising flight。10-v4 retains near RIGHT round foreground knee and backward fold, far LEFT boot forward behind. All soles<=1104.
- E11：left-leading flight。Near RIGHT folded-back foreground over far LEFT leading thigh; front foot suspended, all soles<=1112.
- E12：left-leading pre-contact。Same occlusion as11/13; far LEFT sole1133, descending towards contact.
- E13：left initial contact。Near RIGHT folded-back knee foreground, far LEFT supporting front shin visible behind; left sole1164.
- E14：left compression。14-v3 same upperbody size as06-v4; near RIGHT forward thigh foreground covers far LEFT support thigh, far LEFT sole1158 flat.
- E15：left late support。Far LEFT rear support, near RIGHT forward foreground; heel raises into push, toe EAST.
- E16：left push-off。16-v4 square, same headsize. Far LEFT rear extended, near RIGHT forward foreground; leads to01.

旧06-v3及14=06-v2存在人体比例偏小，已由06-v4/14-v3替换。10-v2前脚垂低、10-v3腿层次交换失败，已拒用；10-v4保留近右后折腿遮挡远左前腿。16-v3是横幅输出，拒用；当前16-v4原生方图。

脚掌检查采用膝-踝-鞋长轴与E前进向关系，保持合理踝屈伸；不以缩小腿间距代替纠正外撇。月影没有被用户确认完整正确方向，仅参考具体已查看图的动作结构。

统一配准建议：原生共同虚拟地面y1165、骨盆投影x约700；整1254画布缩为860，直接在1024画布alpha_composite的方向常量translation=(32,143)，约映射到根点(512,942)。若先以(82,82)居中，则额外位移(-50,+61)。不能逐帧最低脚贴地，不能bbox自适应缩放。


全16 alpha>=32主体没有触边；E11枪尖边距仅2px原生，已实际看完整尖端，统一导出留足周边。文字记录actualModel/actualQuality仍null，配置目标不能当作实际返回。


最新用户要求：跑步16帧均匀75ms，整圈1200ms。当前预览不再提供480/640/720/800旧档，也不分相位权重；慢放、暂停、逐帧保留。历史生图prompt/receipt不改写，普攻30ms不变。
