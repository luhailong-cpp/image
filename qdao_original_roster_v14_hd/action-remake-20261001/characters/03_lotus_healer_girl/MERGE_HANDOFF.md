# 03 莲花医者 · 本机交接

更新：2026-10-03T22:06:00.922679-04:00。仅写本角色目录；未操作Git、共享配置、其他角色或客户端。

当前已选入并导出 **164/196 帧** 1024×1024 RGBA 候选；库存另含尚未选入的原生在制稿。实际已有图片的槽位为 179/196；重试版本不重复计作槽位。美术与动态尚未全部通过，客户端未接入/未运行。

| 动作 | 方向 | 已选/目标 | 试播时长 ms | 状态 |
| --- | --- | ---: | ---: | --- |
| run | E | 16/16 | 1200 | 候选待审 |
| run | NE | 16/16 | 1200 | 候选待审 |
| run | N | 16/16 | 1200 | 候选待审 |
| run | NW | 16/16 | 1200 | 候选待审 |
| run | W | 16/16 | 1200 | 候选待审 |
| run | SW | 0/16 | — | 待补 |
| run | S | 16/16 | 1200 | 候选待审 |
| run | SE | 0/16 | — | 待补 |
| hit | E | 6/6 | 240 | 候选待审 |
| hit | W | 6/6 | 240 | 候选待审 |
| attack | E | 12/12 | 360 | 候选待审 |
| attack | W | 12/12 | 360 | 候选待审 |
| cast | E | 16/16 | 720 | 候选待审 |
| cast | W | 16/16 | 720 | 候选待审 |

## 预览与来源

[全部动作](preview/actions.html)读取[选帧清单](review/all-actions-selection.json)，每槽指向真实独立原生来源及SHA。导出只做完整原生画布1254→1024等比缩小，translation=(0,0)，保留透明度；没有镜像、复制、形变或插值填槽。旧E01/E05的复用保留旧来源记录，旧512 walk未冒充新的高清run。

逐图实际模型和质量未披露即null，逐图prompt/job/receipt/generation记录保存目标、实际参数、回执与SHA。[source-index.csv](review/source-index.csv)列出当前选中来源；[技术检查](review/all-actions-technical-verification.json)仅证明文件/尺寸/唯一性，不能替代动作验收。

## 根点、时长与事件

[root-and-timing.json](review/root-and-timing.json)逐组记录固定原生根点、1024导出根点、规范化pivot及逐帧时长；这些是离线诊断值，尚未在客户端采用。透视远近脚允许不同屏幕高度，不能通过逐帧最低脚移动伪造落地。

[action-events.json](review/action-events.json)记录已有实图候选的接触/离地、受击、普攻接触与施法释放帧，缺失的事件明示待核查。跑步离线正常1×为1200ms=16×75ms；正式客户端周期仍null；受击/普攻/施法保持240/360/720ms。

## 当前待核查项

以下按本次选帧的真实问题记录汇总；包含待连播核对项，不将全部问题等同于确定错误。后续修图应先检查当前source/hash，避免按淘汰版本重复修改。

### run / E

- E01：近右鞋尖仍抬起，全底承重应由后续帧完成
- E02：头与脸相对E01横向偏移仍需动态复核；鞋底最低1159距地面5px
- E03：灯体已恢复尺寸；与E04灯体横向跨度仍偏大；后摆鞋随修稿下移，需看03→04连贯性
- E04：支撑底约1180，较固定诊断线低16原生像素；需连播核查03→04→05
- E05：沿用历史优选姿势；头部上升不明显；与E04支撑点衔接待验
- E06：身体起伏较少，但两鞋已与地面有间隙
- E07：前鞋离地29px，需检查前伸速度是否过快
- E08：前鞋距地面约4px；128px画布只约0.4px，临落地与接触难分
- E09：鞋底最低1165比虚拟地面低1px；首接触候选
- E10：鞋底1168低4px；头下压约14px，已修复灯具截边
- E11：支撑鞋中心625偏目标更后，但09→12已单调后移
- E12：右灯从原过前位置回到腰前，接13更连贯；支撑底1183仍低于诊断线19原生像素
- E13：灯从原极后位置回到中间摆幅；须连播核查12→13→14速度
- E14：前脚离地69px来自屈膝，身体起伏较小；需检查13→14连续性
- E15：原任务号14实际更适合15槽；独立生成，未复制另一个槽；头顶65较14的70高5px
- E16：原提示为临落地，实际heel最低1164，接触事件提前到16；与01鞋位置/角度衔接仍需复核

### run / NE

- NE不是纯E或纯N；脚跟视角和鞋尖透视依照斜后相机核验，俯仰露底不自动判外撇
- 01-v1/01-v2、09-v1/09-v2、07-v1、14-v1未选；14-v1右鞋外偏已用14-v2修复。
- NE03：前摆幅度偏小，需连播看支撑阶段是否停顿
- NE04：灯的前摆跨度比03大，须检查03→04连接
- NE06：双腿的遮挡随前后交替变化，需连播核对支撑腿归属
- NE09：另一半周期头部中心比01偏左约60px，未做整图平移
- NE12：原文件13-v1实际仍处在左前足后蹬，不能按提示词标腾空

### run / N

- N01：One image does not prove running dynamics or a seamless cycle.
- N01：No north N02–N16 images generated in this subtask.
- N01：No whole-image move/resize or scripted pixel edit applied.
- N01：07 Moon Shadow was not used as an approved reference.
- N02：Compression is modest and visible chiefly in right knee/cloth; do not infer full dynamic loading from one frame.
- N03：Arm middle pose is incomplete; flask remains forward/high. Head top remains near prior raised head, do not claim requested head height locked.
- N04：Rear right sole is broad and exact toe-contact event is ambiguous; preserve as late support/toe-off candidate rather than assert planted pixels. Head remains higher than N01.
- N05：Requested toe-off and shortening of trailing right leg are not clear: right foot remains very low and upper body is lower, not rising. Treat as uncertain late-support/toe-off, not confirmed flight.
- N06：Lamp and bottle both spread laterally more than prior frame; retain as candidate but compare arm path and apparent prop scale in cycle.
- N07：Left heel has reached a very low position comparable to contact depth, so this may already be near-contact rather than intended mid-flight. Keep phase uncertain for sequence review.
- N08：Lift exceeds requested25px; exact measured gap is recorded separately. Earlier07→08 transition still needs full-cycle review.
- N09：Cleanup also changed framing/body extent and lowered left support shoe from prior1091 to roughly1144; do not claim all locked geometry preserved. No clipping/toe-out observed.
- N10：Right recovery sole remains strongly exposed with only small positional progression. Lamp vertical step is substantial and needs cycle review.
- N11：Right passing foot did not descend as much as requested; this reads early passing rather than a fully established mid-support. Arm transition from10 is fairly large.
- N12：Exact toe contact is ambiguous from full exposed left sole; left foot is low and body rises a lot versus11. Do not claim precise grounding or late-support duration.
- N13：Head rises notably versus12 and prop/body position shifts; the trajectory needs cycle review. No clipping or toe-out observed.
- N14：Body lowered from13 instead of apex rise; right foot/arm changes are large. Better suited to later extension slot; an intermediate pose is needed before this image.
- N15：Do not reorder this before14: requested midpoint failed, actual foot extended further.
- N15：Flask rose instead of the requested intermediate lowering, so13→14→15 arm progression reverses sharply.
- N15：Foot axes remain north; no hand swap or clipping observed.
- N16：Lift exceeds requested25px; gap recorded separately. Earlier15→16 body/arm transition still needs cycle review.

### run / NW

- NW01：Single image cannot prove first heel contact or depth registration. Trailing near shoe projects lower than the distant contact shoe, which is expected depth difference and must not be globally aligned.
- NW01：Use as NW camera/scale master, check leg identity and arm paths in full cycle.
- NW02：Head registration drifts slightly; load compression subtle but avoids old opposite-direction arm jump.
- NW03：Near-left swing foot advances high/front faster than requested;02→03 remains a large swing-through.
- NW03：Far-right contact cannot be proved from exposed tilted sole alone; stance trajectory depth remains provisional.
- NW03：Most right arm/lamp is occluded; mother-frame shoulder ownership and one visible flask chain support anatomical assignment, but hand itself is hidden.
- NW04：Far-right shoe exposes substantial sole from pitch; exact toe-off/contact cannot be inferred from lowest alpha alone.
- NW05：Far right shoe still very low; final toe-off not visually secure. First definite flight should be judged from a later frame, not assumed here.
- NW06：Far-right shoe still projects low in the image; absolute screen y is not ground-contact evidence in this rear perspective.
- NW06：05→06 off-ground transition requires loop review.
- NW07：Actual lift is smaller than prompt60; measure returned07→08→09 instead.
- NW07：06→07 changes near-left shoe from raised sole to upper/leading view rapidly.
- NW08：Requested25px lift is not assumed exact; measure actual returned shoe.
- NW08：Leading-shoe pitch changed slightly; inspect08→09.
- NW09：First contact versus early support remains a static inference; use as second-half contact candidate. Rear sole visibility is normal pitch, not lateral toe-out.
- NW10：Subtle loading rather than strong down-bob; measure and review as a contact/loading candidate.
- NW11：Lamp traverses a large projected horizontal distance versus10, though partly hidden; verify timing. Far passing shoe yaw is foreshortened and needs sequence context, not automatically wrong.
- NW12：Lamp rear swing is a large screen-space movement from occluded 11.
- NW12：Near-left support toe/heel contact is not fully unambiguous; do not label exact toe-off from prompt.
- NW13：Requested80px rear-shoe lift produced a smaller actual vertical change.
- NW13：No exact ground plane can be inferred from lowest image pixel alone; observed initial-flight candidate.
- NW14：Near-left trailing shoe extended lower instead of requested tuck;13→14→15 rear-heel trajectory needs cycle review.
- NW14：Far-right upper/sole pitch transition14→15 remains abrupt.
- NW15：Small forward shoe slightly changes pitch, requiring14→15→16 review.
- NW15：Exact requested35px lift not assumed successful.
- NW16：Requested25px lift not assumed exact; inspect actual16→01 shoe descent.
- NW16：Some skirt/pant folds and far-shoe pitch changed.

### run / W

- Head/torso registration drifts strongly left during reversed arm half-cycle; no programmatic compensation used.
- Contact shoe heights vary around provisional1179; technical files do not imply dynamic acceptance.
- 04→05 and11→12 arm travel jumps; lamp shrinks in11.
- 07 source08-v5 and08 source07-v3 are deliberately mapped by actual knee recovery then extension; no repeated image.
- All 16 sources unique independent built-in generations/AI edits, nativeRGBA; builtin actual model and quality undisclosed.
- W01：仅单帧基准获parent接受；完整循环仍未验收
- W02：身体压缩主要在膝部，头高相对01变化很小
- W03：头部未随承重降低；摆臂仍接近01前极值
- W04：04→05灯体从前方到后方跨度大，缺更充分髋侧通过；保留正确持物手优先于错手04-v2
- W05：相对01头眼明显向左漂约70px；手臂提前接近反向极值
- W06：相对01头眼左漂约80px；第一段腾空手臂变化偏小
- W07：实际抬脚大于指示，最低足隙约76px，属于膝回收而非计划晚腾空；头部仍左漂
- W08：前鞋过度向左伸出，08→09接触间隙落差较大；头水平与垂直注册仍漂
- W09：头眼仍较01左漂约80px；局部修正后接触底仍低于诊断地面约7px
- W10：承重底低于诊断地面约21px；头仍左漂；不可用整图移位掩盖
- W11：莲灯直径相对邻帧缩小；右侧头发靠近边缘；头向左漂
- W12：灯从11髋侧到12前方过渡偏大；支撑鞋稍朝下左，足轴需全圈核查
- W13：前腿伸展较14提前，13→14有回收反转；后鞋前掌轴需独立确认
- W14：后足仅约3px间隙，初腾空可信度弱；右侧发梢靠近画布边缘
- W15：前伸幅度大于16，15→16回收跨度；头部未出现计划约18px上升
- W16：16→01头顶仍有约12px变化；需按固定根点试播复核

### run / S

- S01：需连播核对16→01接触高度
- S02：膝部压缩幅度偏弱；前鞋比01约低13原生像素
- S03：支撑鞋底比01约低18原生像素
- S04：支撑脚随深度投影提高；不可用统一最低脚贴线
- S05：前掌蹬地需与04/06连播核查
- S07：手臂较06提前回摆，需核查06→07
- S08：近接触脚与09仅差数像素，小尺寸不易区分
- S10：保持左腿支撑，头顶及左右手方向与09一致
- S11：中支撑腿相位变化较小
- S12：抬身幅度大于另一侧，需核查11→12→13身体起伏
- S14：与原文件编号不同，重排的是独立实图，未补帧或复用
- S15：原14-v1右鞋更低于15-v2，归为临接触后一帧
- S16：实际已进入接触区，比01鞋底约低9原生像素

### hit / E

- 全套仍为候选，未进行客户端事件/节奏/方向/接地验收。
- 部分双鞋朝向偏三分之四、宽站姿；鞋尖/膝/踝需同平面复核。
- 头身/道具存在AI逐帧漂移；固定画布未经逐帧配准。
- 03-v3受力峰值更明确；部分胸口偏向观众，支撑像素仍有漂移。
- E01：错误近侧大莲花及连带长穗已去掉；胸肩转向E侧身的改变不明显，仍有偏正面的残留。
- E01：支撑原位置大致保留；虚拟根点与实脚接地仍未动态核验。
- E02：后仰幅度偏小，未完全达到计划；不继续为小变化无限重试。
- E02：鞋和头仍有局部位置变化，整段接地与连贯性待验。
- E03：双鞋未严格像素锁定，支持区域有少量漂移；头发扩张较大，动作根点须按整组标定。
- E04：胸肩与脸仍带朝观者的斜角；方向未动态验收。
- E05：头部与初始01有横向/纵向位置变化，完整反应段衔接待验。
- E06：最终收势相较05变化较小但为独立实生成；未把它复制为idle。

### hit / W

- 候选完整不代表方向、支撑、节奏或客户端事件验收。
- 脚位、头发、道具存在逐帧AI重画差异；没有程序逐帧配准。
- 03有明确后仰/屈膝峰值；03→04回弹幅度较大，240ms节奏待动态验收。
- W01：实际胸面略偏向观众；固定动作根点尚未标定。
- W02：后移较小，鞋与01有轻微位置漂移。
- W03：发丝更接近右边缘，双鞋位置有少量漂移；视检未替代客户端验收。
- W04：03到04回正幅度较明显，240ms节奏需整段验证。
- W05：与04身体差小，主要表情/灯手变化。
- W06：嘴角略微笑，是否符合受击后状态需美术复核。

### attack / E

- 全套仍为候选，未进行客户端事件/节奏/方向/接地验收。
- 部分双鞋朝向偏三分之四、宽站姿；鞋尖/膝/踝需同平面复核。
- 头身/道具存在AI逐帧漂移；固定画布未经逐帧配准。
- 06灯距右边缘约5px；07灯穗低于诊断地面；后段回收路径仍需动态确认。
- E01：画面左后鞋长轴已转为向右；膝腿站距仍偏宽，未达预期明显收拢。
- E02：支撑宽度仍偏大；脚底与01存在位置差异，需整段动态复核。
- E03：右肘比计划更伸直，但仍可读为后摆峰值；接04的过渡需查看整段。
- E03：两鞋朝右可读，站距偏宽仍保留。
- E04：仍更接近后摆回收而非完全过髋中位，接05需要审查。
- E05：灯比v1更靠躯干，05→接触帧的轨迹仍需整体核验。
- E06：灯体右缘距画布仅约5px，需局部回收以保留安全边距。
- E07：灯穗垂到虚拟地面以下，需针对灯穗动势修正；不能移动整图。
- E08：由07前下极值回收的幅度较大，待整段动态核验。
- E09：灯穗接近前鞋，需动态检查道具/脚遮挡。
- E10：灯轨迹较09后移幅度较大；需整段动态检查。
- E11：灯穗接近或低于诊断地面；双鞋三分之四方向仍需复核。
- E12：终态灯位置与起始蓄力不同；动作状态切换需客户端验证。

### attack / W

- 候选完整不代表方向、支撑、节奏或客户端事件验收。
- 脚位、头发、道具存在逐帧AI重画差异；没有程序逐帧配准。
- 07后跟抬起、左前掌落地，斜轴可由俯仰解释，未见足够证据断定水平外撇；后鞋位置仍有漂移。
- 05发尾距右边缘约6px；04–06出手幅度/06事件150ms待动态检查。
- W01：相对cast目标整体轮廓略长、灯略小；固定动作标定及体量需整组检查。
- W02：灯穗/柄角度变化较大，刚体稳定性待检查。
- W03：与02幅度差较小，蓄力辨识主要依肘与灯角度。
- W04：实际伸幅已较大；03→04出手变化快，需360ms动态检查。
- W05：发尾距右边缘约6px；站姿和头部有轻微漂移。
- W06：05比06更上举，实际轨迹为下压接触，须按实际事件观察。
- W07：后鞋右后跟抬高、左前掌落地，二维斜长轴可由俯仰解释；未见足够证据判水平外撇，不据此强行改鞋。后鞋位置相较06有漂移，仍待支撑标定。
- W08：相对06脚位有漂移；并非逐帧配准结果。
- W09：灯柄形状收缩变化，刚体稳定性需复核。
- W10：灯形仍有AI细节差异，但较v1明显缩小/v2过大改善；未动态验收。
- W11：与12姿态差小；完整360ms尚未动态验收。
- W12：膝/鞋位置有细微变化，动作固定根点待标定。

### cast / E

- 全套仍为候选，未进行客户端事件/节奏/方向/接地验收。
- 部分双鞋朝向偏三分之四、宽站姿；鞋尖/膝/踝需同平面复核。
- 头身/道具存在AI逐帧漂移；固定画布未经逐帧配准。
- 08已修胸前瓶，实际为释放前短回收；12灯碗缩小；低垂灯穗接近鞋，动作固定根点待标定。
- E01：与02的灯位过渡仍需动态检查；双鞋仍偏三分之四。
- E02：右灯手由01身前移到偏后侧，幅度较大，01→02可能突跳；保留实图待全段比较。
- E03：右灯臂与02的空间变化非匀速；需检查前段手轨迹，不能以帧齐全判定通过。
- E04：鞋底相对初稿仍略有漂移；只记录，不以最低alpha强制贴地。
- E05：灯由03/04的前腹区域偏向胸侧，前段手轨迹需全段动态核验。
- E06：较06-v1更适合作为中段聚势；未完成动态验证。
- E07：瓶与灯柄重叠，肩肘遮挡仍需动态检查。
- E08：比请求的微收幅度大；07→08→09灯轨迹仍需整段确认，不能仅因持手正确判连续性通过。
- E09：不适合作为轻微举灯的06，拟按实际姿态用于09释放槽；需生成较小幅度的06替代。
- E09：源文件命名06，实际是完整释放，唯一选用于09；来源编号未伪改。
- E10：肩肘与灯瓶遮挡关系仍需整段检查；鞋面略偏向观众。
- E11：回收幅度较10大；脚底约比诊断地面低35像素，未配准。
- E12：灯碗相对邻帧明显缩小，需统一道具体量；已真实独立生成，非插值。
- E13：和14姿势差小；灯穗接近地面，脚底仍低于诊断线。
- E14：幅度不适合作为释放后短暂维持10，拟作为14收势槽，另补10。
- E14：源文件命名10，实际是收势，唯一选用于14；来源编号未伪改。
- E15：灯穗与前鞋重叠且偏低；不表示脚已贴地验收。
- E16：与15动作差很小但来源独立；灯穗贴近前鞋且低于诊断地面。

### cast / W

- 候选完整不代表方向、支撑、节奏或客户端事件验收。
- 脚位、头发、道具存在逐帧AI重画差异；没有程序逐帧配准。
- 06/07/08/09按实际相位唯一重排；原05-v1实际高举峰值选入09。
- 12灯体仍略偏小；13–16灯收势有外内小摆，尚未动态验收。
- W01：初始姿态平静，后续需要明确聚势和释放幅度。
- W02：灯相对01小幅缩小，刚体体量需整组复核。
- W03：头较02提前俯下，衔接为聚势变化；小幅脚位漂移仍需组级标定。
- W04：03到04灯再次向外且变大；连续性保留问题。
- W05：符合中段过渡，脸头相对初态略俯；须整段确认。
- W06：实际腕位比06低，拟唯一用于06以形成递进。
- W06：按实际腕/灯位置选序：源编号08-v1唯一用于槽06；来源prompt编号保留，不冒充原计划命中。
- W07：相较04伸幅较大，需补05过渡；无大型光效。
- W07：按实际腕/灯位置选序：源编号06-v1唯一用于槽07；来源prompt编号保留，不冒充原计划命中。
- W08：拟唯一选用于08，原请求07编号保留。
- W08：按实际腕/灯位置选序：源编号07-v1唯一用于槽08；来源prompt编号保留，不冒充原计划命中。
- W09：不作为05聚势；唯一选用于09峰值，另补05。
- W09：按实际腕/灯位置选序：源编号05-v1唯一用于槽09；来源prompt编号保留，不冒充原计划命中。
- W10：全灯距左边界35px，余量有限但未裁切。
- W11：前臂回收幅度较小，后续12收肘幅度较大。
- W12：灯体偏小，刚体体量仍需统一；记录残留而非宣称通过。
- W13：与12相比腕下降但灯略外移，转接待动态检查。
- W14：13→14灯外移较明显，保持候选问题。
- W15：14→15有短回收摆幅；非程序插帧。
- W16：终态较15灯再次略外移，连贯性尚待动态验收。

## 合并与保留

确认当前所需来源与1024候选完整后，按根AGENTS规定清理已淘汰图片，保留逐图文字证据和SHA；旧目录只读。另一电脑合并仅取本角色目录所需成品及配套记录。当前已只读确认 D:/work/mmorpg-client 存在；本任务仍只修改本角色素材，未接入或运行游戏内滑步/命中/释放验证。
