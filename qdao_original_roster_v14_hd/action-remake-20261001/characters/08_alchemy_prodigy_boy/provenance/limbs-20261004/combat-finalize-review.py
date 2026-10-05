"""Complete the follow-up sequence review; root task owns runtime export."""
import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat()
reason='07的左瓶在背侧，原08立即跳回胸前，与09同位，缺少身侧回摆过渡。08 v2将左手/瓶移到身侧中间位，承接07→08→09；右手丹炉、脚与原攻击相位保持。'
source='generation/limbs-20261004/combat/attack-E-08-v2.png'
selection={'attack/E/08':{'source':source,'reason':reason,'staticReviewed':True}}
(P/'combat-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding='utf-8')
for v in [1,2]:
 sidecar=ROOT/f'generation/limbs-20261004/combat/attack-E-08-v{v}.png.generation.json'
 rec=json.loads(sidecar.read_text(encoding='utf-8'))
 for ref in rec['references']:
  fp=Path(ref['path']);ref['sha256']=hashlib.sha256(fp.read_bytes()).hexdigest()
  if Path(str(fp)+'.generation.json').exists():ref['generationRecord']=str(Path(str(fp)+'.generation.json'))
 rec['visualStatus']='rejected_duplicate_bottle' if v==1 else 'static_sequence_reviewed'
 rec['staticReview']={'reviewedAt':stamp,'accepted':v==2,'notes':'v1新增身侧瓶但旧胸前瓶未消失，拒用。' if v==1 else reason,'registrationMetrics':'provenance/limbs-20261004/combat-qa/attack-E-08-registration.json','noClientDynamicCertification':True}
 sidecar.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 job=P/f'combat-attack-E-08-v{v}.job.json';jobrec=json.loads(job.read_text());jobrec['references']=rec['references'];job.write_text(json.dumps(jobrec,ensure_ascii=False,indent=2),encoding='utf-8')
report=json.loads((P/'combat-review.json').read_text(encoding='utf-8'))
report['initialReview']={'status':report['status'],'retainedFrames':68,'selectedReplacements':0,'qualification':'初次结论限于单帧肢体结构；后续连续轨迹复核发现attack/E08回摆缺过渡，以下新结论取代初次全保留。'}
report['reviewedAt']=stamp
report['status']='offline_sequence_review_complete_one_candidate_ready_for_root_export'
report['selectedReplacements']=1;report['retainedFrames']=67
report['failedGroupsBeforeRepair']=['attack/E'];report['problemFramesBeforeRepair']=['attack/E/08']
report['failedGroups']=['attack/E'];report['problemFrames']=['attack/E/08']
report['currentRuntimeNote']='当前runtime尚未由本子任务修改；根任务合并combat-selection后方可将上面的待合并组清零。'
report['unresolvedIssuesAfterCandidateReview']=[]
report['method'].extend(['再次按六组01→末帧顺序逐段追踪肩—肘—腕—道具和遮挡交接，区分攻击/施法相位的大位移与没有中间位的换边。','对attack/E04–12逐张读取1024原图，定位07→08药瓶从背侧直接跳胸前；生成v2并查看07/旧08/新08/09完整画布并排，确认只保留一个瓶。'])
report['findings'][0]='单帧审阅未发现腿脚反折或左右换持；连续轨迹复核补充发现attack/E08缺少药瓶身侧回摆过渡，已准备v2替换候选，其他67帧保留。'
report['findings'][-1]='原有68槽SHA互不相同。本次仅attack/E08进行了两次内置AI编辑；v1双瓶拒用，v2通过静态连续性审阅，逐图模型/参数/receipt/提示词记录齐全。'
report['findings'].append(reason)
groupnotes={
 'hit/E':{'rightCauldron':'01托炉预备→02/03靠胸缩臂保护→04/05随躯干回收→06恢复；手掌持续托底。','leftBottle':'各帧均握在胸前一带，随躯干后仰和复位小幅移动，无胸前/背侧突然换边。','occlusion':'两臂交错区域保持同一遮挡关系，抬炉保护和恢复的大位移对应受击相位。','decision':'retain_all_6'},
 'hit/W':{'rightCauldron':'01前托→02/03收炉近胸→04再次前伸→05/06恢复，肘腕始终连到远侧右肩。','leftBottle':'始终在近侧胸前握持，02/03随缩身靠近炉，没有突然穿越前臂。','occlusion':'03双手靠近但仍分别托炉/握瓶，04展开恢复可沿袖口追踪，未缺失中间遮挡。','decision':'retain_all_6'},
 'attack/E':{'rightCauldron':'01准备→02/03收炉蓄势→04快速推出→05/06命中随动→07–11收回→12复位；03→04是攻击加速，11→12为恢复前托，不强行插帧。','leftBottle':'04胸前→05身侧→06/07背侧→08 v2身侧→09胸前→10–12恢复。原08直接回胸，已用身侧独立姿态替换候选。','occlusion':'v2去除旧胸前瓶和手，只有一瓶、一只握瓶左手；身侧前臂被近侧右臂部分遮挡，恢复胸前前有中间位。','decision':'replace_08_with_v2_retain_other_11'},
 'attack/W':{'rightCauldron':'01准备→02/03收臂→04快速前送→05/06前伸命中→07/08回收→09–12复位，右掌一直在炉底。','leftBottle':'整个序列保持近侧胸/腰前握持，随弓步躯干俯仰变化；没有突然跑到背后再跳回。','occlusion':'身前瓶与远侧送炉手遮挡分离，03→04送炉快变位是明确攻击相位而非换手。','decision':'retain_all_12'},
 'cast/E':{'rightCauldron':'01/02前送准备→03/04屈膝收蓄→05–07上举→08/09前送释放→10–14收回→15/16复位。','leftBottle':'均在胸前，05–09逐步被举起的右袖遮挡，只露瓶颈或握持部位，10后重新显露。','occlusion':'06/07原尺寸确认瓶颈/左握持被右袖遮住，前后遮挡方向一致；07→08大回落跟随释放动作，无另一位置突然出现瓶。','decision':'retain_all_16'},
 'cast/W':{'rightCauldron':'01预备→02–04屈膝蓄力→05–08渐举→09–11高位释放→12/13回落→14–16恢复。','leftBottle':'始终由近侧左手在胸前握持，随身体升降小幅位移，肩肘屈度保持。','occlusion':'高举段托炉手远离握瓶手，无遮挡交换；11→12大回落对应释法收势，腕掌附着不丢失。','decision':'retain_all_16'}
}
groups=[]
for group,details in groupnotes.items():
 count=6 if group.startswith('hit/') else 12 if group.startswith('attack/') else 16
 groups.append({'group':group,'frameCount':count,'adjacentPairsActuallyReviewed':[f'{n:02}→{n+1:02}' for n in range(1,count)],'previewSeamAlsoCompared':f'{count:02}→01','notes':details})
report['continuityReview']={'reviewedAt':stamp,'groups':groups,'consecutiveEdgesReviewed':62,'previewSeamsCompared':6,'method':'按相位的连续联系表、关键帧原尺寸和07/08/09候选并排；不是只按单帧是否有两只手判定。','browserPlaybackCheckedByThisSubtask':False,'noFrameDuplication':True,'frameCountsUnchanged':True,'combatTimingUnchanged':{'hitFrameMs':40,'attackFrameMs':30,'castFrameMs':45}}
for slot in report['slots']:
 slot['continuityReviewed']=True
 if slot['slot']=='attack/E/08':slot.update({'decision':'replace_with_candidate','proposedSource':source,'proposedSHA256':hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),'observation':reason,'staticReviewed':True})
report['qaImages']='provenance/limbs-20261004/combat-qa/*.jpg（共11张），为审阅用派生图；根任务合并并核查引用后可删除图片，保留JSON与脚本文字。'
(P/'combat-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'reviewedFrames':68,'reviewedAdjacentEdges':62,'selectedReplacements':1,'retainedFrames':67,'source':source}))
