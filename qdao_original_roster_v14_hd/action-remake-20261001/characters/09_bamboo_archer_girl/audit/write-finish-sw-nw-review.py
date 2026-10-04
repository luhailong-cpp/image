import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
r=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
plans={
'SW':[
('right',[[16,1],[2,3],[4,5],[6,7]],[
'右脚位于身体前下方，16初接触到01加重，左腿后收；鞋面沿SW行进方向。',
'右脚转到身体经过位置，02膝部较深缓冲、03较直但未锁膝，左膝进入前摆。',
'右脚在身后较近处连续承重，04/05左膝前驱、右膝踝保留屈曲，靴底低。',
'右脚在更后位置持续支撑，06/07右踝蹬伸、左腿前摆幅度加大，未画成双脚同时飞行。']),
('left',[[8,9],[10,11],[12,13],[14,15]],[
'左脚从近髋的同一左短裤口向前落下，08/09脚跟与前掌低平；原右腿仍后收，未交换腿归属。',
'左脚转至身体下方持续承重，10缓冲到11身体经过，右膝前驱；两张膝踝与上肢变化可辨。',
'左脚在较近后部支撑，12/13左膝保留弹性，13已收回过早伸到末段的左靴。',
'左脚在更后位置蹬地，14/15前掌低位、右腿继续向前，15尚未提前改为右脚支撑。'])],
'NW':[
('left',[[15,16],[1,2],[3,4],[5,6]],[
'左脚15/16在髋前的左上投影位置落地，16更深加载；近左腿与远右腿连接清楚，右脚仍向后回收。',
'左脚01/02在身体下方低跟承重；与15/16相比落点更靠身下，两张肩肘及右脚回收不同。',
'左脚03/04在髋后较近处接触，右腿向前回收，04鞋底已由整片外露改为低跟支撑。',
'左脚05/06向后延展，前掌保持最低接触边、脚跟抬起；06保留原近左大腿归属，右腿前摆等待07落地。']),
('right',[[7,8],[9,10],[11,12],[13,14]],[
'右脚07/08从远髋在身体前方落地，近左腿交叠向后回收；窄修保留两条大腿原遮挡。',
'右脚09/10支撑靴已从原过前位置后收至髋下，脚跟与前掌低平；与07/08的前落点分开。',
'右脚11/12来自远右髋，在髋后较近处低跟承重；近左膝向前抬，12二次收回过后的右靴。',
'右脚13/14在更后位置前掌蹬地，脚跟抬起且鞋尖沿NW轴；左腿保持前驱，直到15才换成左支撑。'])]
}
for d,segments in plans.items():
 tech=json.loads((r/f'audit/{d}-finish-technical.json').read_text(encoding='utf-8'))
 assert len(tech['frames'])==16 and tech['uniqueSha256']==16
 positions=['A 前部落点','B 身体经过/髋下','C 近后支撑','D 更后蹬地']
 ss=[];mapping={}
 for foot,pairs,evidence in segments:
  ps=[]
  for k,pair in enumerate(pairs):
   ps.append({'frames':pair,'position':positions[k],'durationMs':150,'independentPoses':True,'evidence':evidence[k]})
   for f in pair:mapping[f]=(foot,k,evidence[k])
  ss.append({'foot':foot,'consecutiveContactFrames':sum(pairs,[]),'supportDurationMs':600,'positions':ps})
 frames=[]
 for f in tech['frames']:
  foot,k,evidence=mapping[f['frame']]
  assert f['size']==[1024,1024] and f['mode']=='RGBA' and f['alphaExtrema'][0]==0
  frames.append({'slot':f"run/{d}/{f['frame']:02d}",'frame':f['frame'],'file':f['file'],'sha256':f['sha256'],'status':'static_contact_reviewed_dynamic_pending','observedSupportFoot':foot,'position':positions[k],'evidence':evidence,'footOrientation':'沿SW前左下方向，鞋尖随膝踝，无独立侧向外撇。' if d=='SW' else '沿NW前左上方向，后视鞋跟与鞋底按透视可见，未把鞋掌旋向侧方。','staticContact':True,'isFlight':False,'dynamicVisualAcceptance':False})
 apng=Image.open(r/f'audit/{d}-finish-75ms.apng')
 durations=[]
 for i in range(apng.n_frames):apng.seek(i);durations.append(apng.info.get('duration'))
 assert apng.n_frames==16 and all(x==75 for x in durations)
 report={'reviewedAt':now,'action':'run','direction':d,'requirement':'同脚连续8帧接触，前部落点→身下→近后→更后四个渐变空间位置，每位置两张独立姿态','timing':{'frameMs':75,'frameCount':16,'cycleMs':1200,'pairMs':150},'segments':ss,'frames':frames,'evidenceFiles':[f'audit/{d}-finish-contact.png',f'audit/{d}-finish-legs.png',f'audit/{d}-finish-75ms.apng',f'audit/{d}-finish-technical.json'],'technical':{'uniqueSha256':16,'all1024Rgba':True,'apngFrames':16,'apngDurationsMs':durations,'wholeCanvasExportOnly':True,'noMirrorDuplicateInterpolationOrLowestFootAlignment':True},'staticPairedGroundStatus':'passed_static_pose_review','dynamicVisualAcceptance':False,'clientModified':False,'remainingIssues':['正常75ms动态顺滑、根锚点连续与首尾循环尚未通过动态观看验收。','未接入客户端或运行引擎验收。'],'reviewLimit':'已实际查看原图、最终整圈连图和下肢裁切；APNG仅验证结构和时长，未冒称已观看动态。','actualModel':None,'actualQuality':None,'unverifiedReason':'内置宿主管理，工具无型号/画质选择器且返回未披露。逐图请求/回执/来源均已保存。'}
 (r/f'audit/run-{d}-paired-ground-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 if d=='SW':
  p=r/'review-parts/run-SW.json';old=json.loads(p.read_text(encoding='utf-8'))
  for row in old.get('frames',[]):
   latest=next((f for f in frames if f['slot']==row.get('slot')),None)
   if latest:
    row['sha256']=latest['sha256'];row['observedSupportFoot']=latest['observedSupportFoot'];row['isFlight']=False;row['observedPhase']=latest['position'];row['status']='needs_review'
    row['evidence']=latest['evidence'];row['pairedGroundReview20261004']={'reviewedAt':now,'sha256':latest['sha256'],'status':'passed_static_pose_review','dynamicVisualAcceptance':False,'evidence':latest['evidence']}
  old['pairedGroundReviewFile']='audit/run-SW-paired-ground-review.json'
  old['dynamicVisualAcceptance']=False
  p.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
 print(d,tech['uniqueSha256'],'unique SHA; static pair review written; dynamic=False')

