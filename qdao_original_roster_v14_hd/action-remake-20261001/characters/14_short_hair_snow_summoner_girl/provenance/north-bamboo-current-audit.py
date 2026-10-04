import json,hashlib,copy
from pathlib import Path
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
now=datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
phaseN=[
 ('left_contact','left','左腿在髋下低位，右膝屈曲回收，鞋尖沿N轴；不是前后两端分配的证明。'),
 ('left_absorb','left','左腿低位承重，髋膝略收，右后跟回收。'),
 ('left_mid_support','left','左腿中支撑，膝接近伸直；右腿回收。不得沿用旧强压膝标签。'),
 ('left_support_exit','left','左低靴保持髋下附近，右膝/后跟更高；右掌摆低。'),
 ('left_stance_exit','left','左腿向支撑后段伸出，右腿回收；低靴接近虚拟地面。'),
 ('unresolved_flight',None,'当前正式仍是旧direct-v2：头身偏大且两个大鞋底同时后向，拒作最终飞行姿态；root负责替换。'),
 ('right_approach_air','none','右前腿向地面下伸、左后跟折起，前腿显示靴面；还未进入承重。'),
 ('right_approach','none','右腿继续前伸准备接地，左腿回收；未把最低像素当已承重。'),
 ('right_contact','right','右低腿进入支撑，左后跟回收；右掌在低位。'),
 ('right_absorb','right','右腿低位承重，左膝屈曲；root-v9右掌约590，连接肩肘腕。'),
 ('right_mid_support','right','右腿中支撑，膝接近伸直；左腿回收。不得沿用旧强压膝标签。'),
 ('right_support_exit','right','右低腿仍靠髋下，左后跟回收，进入退出段。'),
 ('right_stance_exit','right','右腿低位伸展退出，左膝前向回收；低靴接近虚拟地面。'),
 ('left_drive_air','none','短暂腾空；左前腿主要露靴面、右后腿露鞋底，不是两只大鞋底并列。'),
 ('left_approach_air','none','左前腿下伸靠近地面、右后跟折起；比14下降，未计承重。'),
 ('left_approach','none','左腿前伸准备接地，右腿回收；未计承重。')]
observations={
 'N':{'supportRuns':[{'leg':'left','frames':[1,2,3,4]},{'leg':'right','frames':[9,10,11,12]}],
 'spatial':'低位支撑集中于髋下；05/13为支撑后段，06–08/14–16交换或前伸。当前实图不证明每脚空间前2/中4/后2。',
 'pending':['N06由root重画；当前正式旧direct-v2不可收','空间中间/旁边分配定义仍待人类明确','最终1200ms动画复验']},
 'NE':{'supportRuns':[{'leg':'left','frames':[1,2,3,4]},{'leg':'right','frames':[9,10,11,12]}],
 'spatial':'01–04左、09–12右低靴集中在髋下。05/13后段退出；06–08/14–16前后腿交换/前伸，不能直接用改标签满足空间分配。',
 'pending':['空间中间/旁边分配定义及相应实图验收；既有方向/身份通过不等于新空间要求通过']},
 'NW':{'supportRuns':[{'leg':'left','frames':[2,3,4,5]},{'leg':'right','frames':[9,10,11]}],
 'spatial':'01为空中交叉，不能计为左接地。02–05左支撑集中髋下；09–11右支撑。12右腿向后下方斜伸，靴底仰角使接地不明确；13同为退出/交换，未凑入支撑。',
 'pending':['NW12可能需要实际姿态修复；上一准备步骤中断，未提交新图','空间中间/旁边分配定义仍待人类明确']}}
allframes=[];reports={}
for d in ['N','NE','NW']:
 rows=[]
 for i in range(1,17):
  p=R/'run'/d/f'{i:02}.png';m=read(Path(str(p)+'.generation.json'));sha=hashlib.sha256(p.read_bytes()).hexdigest()
  assert sha==m['sha256']==m['registrationTransform']['outputSha256'],(d,i)
  if d=='N' and i==10:assert sha=='812fe97861e8703fa4ce735ced64efc3cebb095499984b8a7bcecf858ef616f5'
  support=next((x['leg'] for x in observations[d]['supportRuns'] if i in x['frames']),None)
  if d=='N':phase,side,obs=phaseN[i-1]
  else:
   side=support
   phase='visible_support' if support else 'stance_exit' if i in [5,13] else 'leg_exchange_or_approach'
   if d=='NW' and i==5:phase='visible_support'
   if support:obs=f'{support}低靴在髋下附近支撑，另一膝屈曲回收；不同帧的膝角、足位置、躯干/袖形不同，非复制帧。'
   elif d=='NW' and i==1:obs='两脚交叉、鞋底/鞋面处于回收交换；不计低位支撑。'
   elif d=='NW' and i==12:obs='右腿后下斜伸，鞋底部分朝镜头，靴底不够平稳；接地不明确，不计为已验证支撑。'
   else:obs='前后腿交换、退出或接近地面；未仅依据相位标签计为已验证支撑。'
  row={'file':f'run/{d}/{i:02}.png','sha256':sha,'durationMs':75,'selectedNative':m['derivedFrom']['file'],
       'phase':phase,'supportLeg':support,'visiblePhaseSide':side,'observation':obs,
       'reviewStatus':'rejected_current_formal_pending_root_replacement' if d=='N' and i==6 else 'static_pending_root_preview',
       'newSpatialRequirementStatus':'awaiting_user_spatial_definition','registrationTransform':m['registrationTransform']}
  rows.append(row);allframes.append(row)
 assert len(set(x['sha256'] for x in rows))==16
 report={'schemaVersion':1,'direction':d,'recordedAt':now,'reviewer':'north_run','status':'static_pending_root_preview',
  'cycleDurationMs':1200,'frameDurationMs':75,'newSpatialRequirementStatus':'awaiting_user_spatial_definition',
  'criterionPassed':False,'criterionNote':'Observed contact runs are descriptive evidence, not acceptance of the new spatial 2/4/2 requirement. No existing four-contact pass is asserted.',
  'evidence':{'currentContactSheet':f'run/staging/north-bamboo-current-{d}.jpg','sourceShaList':f'run/staging/north-bamboo-current-{d}.jpg.sources.json','actualVisualReview':True},
  **observations[d],'frames':rows}
 reports[d]=report;save(R/'audit'/f'contact-{d}-review.json',report)
# Refresh N evidence only; preserve the earlier observations as an historical snapshot.
p=R/'run/N/grounding-review.json';g=read(p)
g.setdefault('reviewHistory',[]).append({'snapshotAt':now,'reason':'Replace stale pre-bamboo selectedNative/SHA and phase descriptions with current formal evidence; prior pass is not applicable to the new spatial criterion.','frames':copy.deepcopy(g['frames'])})
for old,row in zip(g['frames'],reports['N']['frames']):
 old.update({'sha256':row['sha256'],'selectedNative':row['selectedNative'],'phase':row['phase'],'supportSide':row['visiblePhaseSide'],
 'phaseEvidence':row['observation'],'durationMs':75,'registrationEvidence':row['registrationTransform'],
 'reviewStatus':row['reviewStatus'],'newSpatialRequirementStatus':'awaiting_user_spatial_definition'})
 n=int(Path(old['file']).stem)
 old['hands']='左臂抱一只狐，右肩袖到肘腕及托晶掌可追踪；未见额外手臂。'
 old['footAxis']='前后腿沿N推进轴；回收脚的鞋底俯仰与侧向外八分别审查。'
 if n==6:
  old['hands']='当前正式旧direct-v2未最终通过；root负责重画右臂过渡及上身体位。'
  old['footAxis']='两个完整大鞋底同时后向、前后腿可见面不正确；待root替换，不能沿用旧通过。'
 if n==10:old['hands']='实际看09→10v9→11，右掌约660→590→510连续上摆，肘腕连通，唯一右掌托唯一雪晶；静态过渡可接受，最终动画待root。'
g.update({'reviewStatus':'static_pending_root_preview','cycleDurationMs':1200,'updatedAt':now,'newSpatialRequirementStatus':'awaiting_user_spatial_definition',
 'remainingChecks':observations['N']['pending']})
save(p,g)
selected=read(R/'provenance/north-bamboo-native-selection.json')
summary={'schemaVersion':1,'recordedAt':now,'reviewer':'north_run','status':'incomplete_pending_root_N06_and_spatial_definition',
 'scope':['run/N','run/NE','run/NW'],'formalFrameCount':48,'cycleDurationMs':1200,'durationMsPerFrame':75,
 'formalShaAndMetadataVerified':48,'uniqueShaPerDirection':16,
 'actualModel':None,'actualQuality':None,'modelEvidenceNote':'Built-in tool did not expose actual model/version or quality; configuration targets are not actual invocation evidence.',
 'selectedNativeEdits':selected,'additionalSelectedDirectEdit':{'file':'run/NW/03.png','id':'north-bamboo-NW-03-v2','method':'direct_registered_canvas_redraw','globalScale':1.0,'inheritedCharacterScale':0.8},
 'rootOwnedSlots':{'N06':'pending actual replacement; current formal has known size/leg issues','N10':'root-v9 statically reviewed with09/11; current SHA below'},
 'frozenOwnNFrames':[3,7,11,14,15],
 'newSpatialRequirementStatus':'awaiting_user_spatial_definition','spatialCriterionPassed':False,
 'rejectedHistory':[
  {'batch':[1,2,3],'reason':'Most direct-canvas N edits enlarged head/body or gave wrong leg projection; NW03v2 only current selected direct edit besides pending bad N06.'},
  {'batch':[5,6],'reason':'N same-frame natives inherited large heads; some flight attempts showed two similar large soles toward camera.'},
  {'batch':[7],'reason':'Master-v5 fixed head/body, but flight frames retained extended low support;03/11 selected.'},
  {'batch':[8],'reason':'Master-v6 selected07/14/15.06 correct leg surfaces but upper body bob too high;10 arm swing jump later replaced byroot-v9.'}],
 'NW12NewGeneration':{'submitted':False,'reason':'Preparation aborted at environment reload; new spatial allocation pending; no batch9 receipt exists.'},
 'bitmapCleanupStatus':'pending final acceptance and release of root in-progress image references; no unique working image deleted',
 'reports':[f'audit/contact-{d}-review.json' for d in ['N','NE','NW']],
 'currentFrames':allframes}
save(R/'audit/bamboo-north-review.json',summary)
print('48 formal SHA verified. Contact reports and N grounding evidence refreshed. No formal PNG or metadata modified. New spatial criterion remains unpassed.')
