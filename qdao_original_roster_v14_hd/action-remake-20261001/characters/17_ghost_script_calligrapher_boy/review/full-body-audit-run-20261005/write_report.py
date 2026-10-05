from pathlib import Path
import json,hashlib,datetime
out=Path(__file__).resolve().parent
b=out.parents[1]
inputs=json.loads((out/'input-runtime-sha256.json').read_text(encoding='utf-8'))
directions={
 'N':{'arms':'后视右肩—右袖—右侧持笔手可追溯；左肩—左袖—左侧持卷手可追溯。01/02后摆、03–08前送、09/10反摆、11–16回收的近远关系未见左右身份互换。','legs':'正后视裤管—踝口—后跟关系逐帧检查；摆脚后折露底与支撑脚抬跟分开看。当前16已经收正左支撑靴，右预落地靴仍为窄底边；不沿用旧16的拒稿结论。','extra':'02笔杆上端被手/袖口遮挡，未据此断言断笔或断腕。07/08侧面露出不是横向横甩的充分证据。'},
 'NE':{'arms':'右肩近侧笔臂与左侧远卷臂分别连续，右手绕笔杆、左手持卷边；摆臂中有前后遮挡而未见握持侧交换。','legs':'沿斜向前进的髋部出腿、膝弯、踝口和鞋尖检查；支撑靴前掌朝右前，折膝摆脚可露底。07/08及15用当前已导出图复核，未见旧侧甩形态。','extra':'14–16两脚在画面上拉开主要对应斜向前后步幅；没有仅凭画面两鞋间距判为横向劈腿。'},
 'E':{'arms':'近侧右笔臂在前胸与身后间摆动；远侧左卷臂的肩端部分遮挡，但可从袖口及手持卷边/上杆继续追溯。03–05、10–12的中间臂均实际比较。','legs':'侧向髋—膝—踝链条与鞋头向右的侧影一致；后折脚的鞋底倾斜属于屈膝俯仰，未见同一脚突然横朝镜头。','extra':'11原图确认：近侧右手握笔、远侧左手握卷轴上杆，手指与杆相接，无悬空抓握。'},
 'SE':{'arms':'右笔臂从近侧肩跨前胸，左卷臂从远侧肩向后摆，不能按笔或卷位于画面哪边判左右。03/04/05与10/11/12逐帧核过。','legs':'支撑靴顺右前运动平面，膝弯时的鞋面缩短和踝屈伸未见横向折断；07/08、15/16前摆脚有正常翘趾露底。','extra':'04原图左肩后可见卷纸窄面、上下轴端及握持手，卷轴是被躯干遮挡，非丢失。'},
 'S':{'arms':'正面右手在画面左侧持笔、左手在画面右侧持空白卷轴；腕部均接于对应袖口，未见断腕、持物互换或额外手。','legs':'正前视膝—鞋带/踝口—鞋尖纵向检查；04/05支撑脚窄前掌/抬跟在原图可读，没有把鞋底轮廓相似作为保留理由。06–08、14–16保持另一摆脚向前，未见横向叉开。','extra':'04/05支撑靴原图单独复核；可见自然轻微转角，但未确证小腿向前而整只鞋掌横向外撇。'},
 'SW':{'arms':'近侧左卷臂可从右侧肩端追到前方卷手，远侧右笔臂绕身后再前送；06–07和10–12的遮挡转换逐帧比较，未见笔卷单纯左右换手。','legs':'两腿随左前运动平面前后交替；前摆靴朝左前，后支撑踝仍接于向后伸的裤管。07/08和15/16露底来自前摆翘趾，不是独立横扭。','extra':'11原图确认左手抓卷轴上杆、右手握笔杆，腕与袖口连通。'},
 'W':{'arms':'近侧左卷臂与远侧右笔臂在03/04及10/11/12经过中间姿态，沿肩—袖—腕追溯没有断接。手握笔杆/卷边，未见互换解剖侧。','legs':'两条腿的前后步幅仍在向左平面，鞋头朝左；后支撑脚抬跟与前摆翘趾未见踝口以下突然横向外翻。','extra':'04、11原图再看；不能因远侧臂被近侧袖遮住一段，就断言浮手。'},
 'NW':{'arms':'近侧左肩接卷臂、远侧右肩接笔臂，01–16持物身份持续；后视遮挡不影响可见袖口—手—杆连接。','legs':'支撑鞋前掌指向左前，后折摆脚斜纵向露底；当前15为新导出v4，14→15→16没有旧横向侧踢轮廓。','extra':'15原图再看；不把正常可见整块鞋底单独当成外翻证据。'}
}
native={('SE',4),('S',4),('S',5),('N',2),('W',4),('SW',11),('E',11),('W',11),('NE',7),('NE',15),('N',16),('NW',15)}
notes={('SE',4):'原图确认卷轴窄面与握手在肩后可见，遮挡成立。',('S',4):'原图核对支撑腿膝踝与窄前掌，未确证横向鞋掌。',('S',5):'同04，后延抬跟与外扭分开判读。',('N',2):'笔杆上端遮挡；持笔手仍与右袖和可见杆相接。',('W',4):'近卷远笔中间臂位置及腕袖连接复核。',('SW',11):'卷上杆握持与右笔握持均直接可见。',('E',11):'中间摆臂近右笔/远左卷来源可追溯。',('W',11):'中间摆臂腕部与袖口、笔杆/卷边连接可见。',('NE',7):'当前修正版摆脚，不采用旧图结论。',('NE',15):'当前修正版支撑鞋轴与小腿运动平面复核。',('N',16):'当前v10导出：左支撑靴收正，右摆靴窄底边保留。',('NW',15):'当前v4导出：斜纵向摆靴，非旧横向侧踢。'}
changed=[]
for row in inputs:
 p=b/row['file']; current=hashlib.sha256(p.read_bytes()).hexdigest()
 if current!=row['sha256']:changed.append({'file':row['file'],'old':row['sha256'],'current':current})
 row.update({'inspection':['full_body_240px','arm_torso_enlargement','hip_knee_ankle_shoe_enlargement','adjacent_sequence_comparison'],'newConfirmedDefects':[],'recommendation':'retain_current_pixels_no_new_confirmed_defect','formalAcceptance':False})
 if (row['direction'],row['frame']) in native:row['inspection'].append('native1024_individual_view')
 if (row['direction'],row['frame']) in notes:row['specificObservation']=notes[(row['direction'],row['frame'])]
report={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'128 current formal run PNGs, static anatomical and adjacent-frame review only','method':'All24 diagnostic sheets actually viewed;12 targeted originals actually viewed. Hips/knees partly hidden by trousers/robe: only infer visible chains and occlusion, not exact unseen joint coordinates. Do not equate visible sole with twist or 2D stride separation with lateral abduction.','status':'read_only_review_complete_no_new_confirmed_repair_set','confirmedNewRepairFrames':[],'allDirectionsRecommendation':'Retain current pixels on this audit evidence; not global animation acceptance.','timing':{'frameCount':16,'frameMs':75,'cycleMs':1200,'framesCopiedOrRetimed':False},'directionFindings':directions,'frames':inputs,'runtimeChangedDuringAudit':changed,'uniqueInputHashes':len(set(r['sha256'] for r in inputs)),'limits':['This audit did not change runtime, manifest, selection or global acceptance.','No new image generation.','75ms real-time playback was not newly run by this subagent; previous playback belongs to root.','Natural knee bending, heel lift and consistent body bobbing are not rejected merely for coordinate differences.']}
# Supersedes the original overbroad retain-all finding after actual torso re-review.
repair_sets={'E':list(range(4,12)),'W':list(range(4,11))}
report['status']='corrected_torso_continuity_repairs_required'
report['correction']='原审查过于聚焦腕袖及握持，漏掉胸前/背肩视角族突变；撤回E/W全保留结论。'
report['confirmedNewRepairFrames']=[{'direction':d,'frame':f,'defect':'torso_front_back_camera_family_discontinuity'} for d,fs in repair_sets.items() for f in fs]
report['allDirectionsRecommendation']='E04–11 and W04–10 require upper-torso continuity repair; other earlier local observations retained, not global acceptance.'
report['timing']={'frameCount':16,'frameMs':60,'cycleMs':960,'basis':'Latest direct user correction relayed by root on 2026-10-05; root owns actual timing export.','framesCopiedOrRetimed':False}
report['limits']=['Historical source hashes retained; this report does not change runtime, manifest or acceptance.','Corrections are being generated outside this read-only audit; see review/torso-continuity-E-20261005.','Latest playback target is 60ms/frame; this static report does not certify playback.','Natural knee bending, heel lift and consistent body bobbing are not rejected merely for coordinate differences.']
directions['E']['arms']='03→04、11→12胸前/背肩视角突变已确认，须修04–11整段；固定近右笔臂、远左卷臂，以01/03/12胸前偏侧家族为基准，不交换持物。'
directions['W']['arms']='03→04、10→11胸前/背肩视角突变已确认，须修04–10整段；固定近左卷臂、远右笔臂，统一胸前偏侧家族。'
for row in inputs:
 if row['frame'] in repair_sets.get(row['direction'],[]):
  row['newConfirmedDefects']=['torso_front_back_camera_family_discontinuity']
  row['recommendation']='repair_upper_torso_keep_leg_phase_and_head'
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 八方向跑步手脚复核（2026-10-05）','','本次只读复核正式 runtime 的128张1024 RGBA。实际查看24张全身/手部/腿部联系表，并对12张疑点和最新修正版另看原尺寸；逐图SHA、检查层级及补充观察见 report.json。','','**本轮没有确证需要新增修图的帧，建议保留当前128张。** 这是本轮图像解剖与邻帧复核意见，不是全局动画验收，也不代替主代理75ms实播。','','按最新要求核对髋—膝—踝—鞋尖和前进平面；没有只用鞋底相似度、画面两脚间距或轻微轮廓变动作为依据。袍裤遮住的关节不伪造坐标。','','|方向|本轮建议|具体观察|','|---|---|---|']
for d,n in directions.items():lines.append(f'|{d}|01–16保留|{n["arms"]} {n["legs"]} {n["extra"]}|')
lines+=['','没有修改正式图、manifest、帧序、时长或验收状态；没有调用生图。16×75ms=1200ms保持。审查期间输入SHA变动数：'+str(len(changed))+'。', '','诊断图每方向含 -full240.png、-arms.png、-legs.png；它们只用于审查，不进入游戏资源。']
lines=['# 八方向跑步手脚复核更正（2026-10-05）','','**撤回原先128帧全保留结论。E04–11、W04–10存在胸前/背肩视角族突变，须修上身连续性。** 原审查关注腕袖和握持，漏掉躯干视角问题。实际复查后的逐帧问题仍绑定原输入SHA，见 report.json。','','修复统一为胸前偏侧家族，E近右笔臂/远左卷臂，W近左卷臂/远右笔臂；保留头位与每帧腿部相位。其他方向早期局部观察仅作静态记录，不构成全局验收。','','最新用户节奏为16×60ms=960ms，由root统一导出及实播；此前75ms/1200ms已被覆盖。本审查不修改runtime、manifest或验收。','','|方向|当前建议|具体观察|','|---|---|---|']
for d,n in directions.items():
 advice='04–11上身需修' if d=='E' else '04–10上身需修' if d=='W' else '原静态局部意见保留，非正式验收'
 lines.append(f'|{d}|{advice}|{n["arms"]} {n["legs"]} {n["extra"]}|')
lines+=['','诊断图只供审查。E新候选与来源在 review/torso-continuity-E-20261005；正式选择及动态验收由root完成。']
(out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'reviewed':len(inputs),'nativeOriginalViews':len(native),'uniqueHashes':report['uniqueInputHashes'],'changedDuringAudit':changed,'newConfirmedRepairFrames':report['confirmedNewRepairFrames']},ensure_ascii=False))
