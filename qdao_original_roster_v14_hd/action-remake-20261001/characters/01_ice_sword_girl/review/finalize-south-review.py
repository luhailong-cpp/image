from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
play=read(R/'review/south-preview-verification.json');assert play['passed'] and not play['errors']
ind=read(R/'review/south-final-independent-review.json');assert ind['agentVisualReviewPassed'] and not ind['remainingRequiredImageRepairs']
observations={
 'S':[
  '01右前腿伸向视线，02右膝稍压，右靴面从前伸到平落；左后靴回收。',
  '03/04右支撑靠近身体投影，左膝依次向前通过，04右膝进一步弯曲。',
  '05/06右支撑在髋后，右靴保持低置；左膝由抬起到小腿前摆。',
  '07/08右后小腿下伸，后靴鞋前部支持；左前靴底可见且继续前伸。正前投影中的提跟较含蓄。',
  '09/10左前靴落地后受压，右后膝弯曲回收。',
  '11/12左支撑靠近体下，右膝继续通过，左右膝高度及摆臂不同。',
  '13/14左后靴仍支持，右膝升起后小腿前伸，14两靴职责可区分。',
  '15/16左后小腿向下伸、鞋前部低置；右前靴露底逐步接近落地，16接01。'
 ],
 'SE':[
  '01右前腿伸出，02右膝压缩、前靴落平，左靴在后收起。',
  '03/04右支撑逐渐接近髋下、膝屈曲变化，左后脚向前通过。',
  '05/06右支撑来到髋后，左膝前抬后小腿向前摆出。',
  '07/08右后靴前部低置、后跟提高，左前靴继续前摆并向落地下降。',
  '09/10左前靴着地后膝压缩，右后腿弯曲回收，姿态不同。',
  '11/12左支撑靠近身体投影，右后腿向前通过；12膝屈曲更明显。',
  '13/14左支撑移到髋后，右膝抬起到前摆伸腿，鞋轴顺SE。',
  '15/16左后小腿伸展、前掌压低后跟高；右前靴鞋底边可见，16下降准备接01。'
 ],
 'SW':[
  '01左前靴伸出，02左膝受压而前靴落平，右后腿收起。',
  '03/04左靴接近体下、膝压变化，右后脚通过，右剑腕从外侧收至腰前。',
  '05/06左支撑在髋后、右膝前抬，两帧膝踝和袖腕姿态不同。',
  '07/08左后小腿下伸到鞋前部支撑，右前靴底可见，08继续向落地摆下。',
  '09/10右前靴落地，10右膝进一步压缩，左后靴小幅回收。',
  '11/12右支撑近体下，左膝向前通过；右剑腕回到腰中后前摆，左符袖仍接近肩。',
  '13/14右后靴支撑，左膝由前抬到小腿下伸，右后腿伸展增加。',
  '15/16右后鞋前部低置，左前靴底先可见后下摆准备落地，16与01首尾接续。'
 ]}
nonblocking={'S':['正前投影遮挡后跟，后支撑可由下伸小腿、朝S的低置鞋前部与前摆脚底区分；不能从二维图精确量出后跟离地高度。'],'SE':[],'SW':['04→05剑臂从腰前到腰后遮挡的变化相对集中；04-v2已内收，05-v2腰后部分遮挡、06-v3再展开，独立读图未见反向摆回/断手硬错。']}
allseq={};directions={}
for d in ('S','SE','SW'):
 p=R/f'review/run-{d}-selection.json';s=read(p);frames=s['frames'];assert len(frames)==16
 first='left' if d=='SW' else 'right';second='right' if d=='SW' else 'left'
 sources=[]
 for f in frames:
  for key,hkey in (('sourcePath','sha256'),('candidatePath','candidateSha256')):assert sha(R/f[key])==f[hkey]
  with Image.open(R/f['sourcePath']) as im:assert im.size==(1254,1254) and im.mode=='RGBA'
  with Image.open(R/f['candidatePath']) as im:assert im.size==(1024,1024) and im.mode=='RGBA'
  assert f['durationMs']==75
  foot=first if f['frame']<=8 else second;swing=second if f['frame']<=8 else first
  f['status']='offline_visual_review_passed'
  f['actualContact']={foot:'support_visually_inferred',swing:'swing_or_precontact_visually_inferred','confidence':'manual_native_and_browser_step_sequence_review','evidence':observations[d][(f['frame']-1)//2],'worldSpaceContactVerified':False}
  sources.append({'frame':f['frame'],'sourcePath':f['sourcePath'],'sha256':f['sha256'],'candidatePath':f['candidatePath'],'candidateSha256':f['candidateSha256']})
 assert len(set(f['sha256'] for f in frames))==16
 pairs=[{'frames':[i,i+1],'supportFoot':first if i<=8 else second,'relativePosition':('front_landing','body_approaching_support','body_passing_support','rear_push_off')[((i-1)//2)%4],'twoDistinctPosesVerified':True,'observation':observations[d][(i-1)//2]} for i in range(1,17,2)]
 s.update(reviewedAt=now,artStatus='offline_visual_review_passed',positionPairsVerified=True,dynamicArtAccepted=True,issues=[],remainingRequiredImageRepairs=[],nonBlockingObservations=nonblocking[d])
 s['events'].update(kind='manual_visual_confirmed_offline',eightConsecutiveSupportVerified=True,actualSupportFrames={first:list(range(1,9)),second:list(range(9,17))},observedPositionPairs=pairs)
 s['reviewEvidence']={'scope':'48 final native poses, browser step screenshots and real 1x frame event playback; offline sprite art only','browserReport':'review/south-preview-verification.json','browserReportSha256':sha(R/'review/south-preview-verification.json'),'contactSheet':f'review/south-{d}-browser-step-contact.png','independentTargetedReview':'review/south-final-independent-review.json','handOwnership':'anatomical_right_sword_left_talisman','shoeAxis':'follows travel axis; no outward-V foot pose identified','notClaimed':['continuous video visual perception from browser event timestamps','client runtime integration','world-space foot no-slip or physics contact']}
 write(p,s);allseq[d]=s
 directions[d]={'frameCount':16,'durationMs':1200,'actualSupportFrames':s['events']['actualSupportFrames'],'observedPositionPairs':pairs,'eightConsecutiveSupportVerified':True,'positionPairsVerified':True,'dynamicArtAccepted':True,'artAcceptanceScope':'offline sprite-art review','browserSeenCount':len(play['directions'][d]['seen']),'browserSkipped':play['directions'][d]['skipped'],'measuredCycleMs':play['directions'][d]['cycleMs'],'sources':sources,'remainingRequiredImageRepairs':[],'nonBlockingObservations':nonblocking[d],'preview':f'review/south-{d}-1x-1200ms.webp'}
(R/'review/south-sequences.js').write_text('window.SOUTH_SEQUENCES = '+json.dumps(allseq,ensure_ascii=False)+';\n',encoding='utf-8')
report={'schemaVersion':1,'characterId':'01_ice_sword_girl','completedAt':now,'scope':'run S SE SW; 48 final independent native imagegen poses','nativeCanvasSize':[1254,1254],'candidateCanvasSize':[1024,1024],'candidateCount':48,'formalPromotionOwnedBy':'root','preview':'review/south-preview.html','directions':directions,'remainingRequiredImageRepairs':[],'clientIntegrated':False,'clientRuntimeVerified':False,'worldGroundVerified':False,'actualModel':None,'actualQuality':None,'generationEvidence':'Each source .generation.json has exact source SHA, prompt/receipt and returned dimensions. Host does not expose model/quality. Candidate .generation.json links native SHA.','verificationReports':['review/south-preview-verification.json','review/south-final-independent-review.json'],'methodLimits':'Manual native and browser step interpretation establishes pictured pose support. Real Chrome1x confirms16ordered frames/no skips/~1200ms loops, not human-style continuous video perception or world ground physics.','doNotRebuildWithoutReReview':'build-south-current.py intentionally resets selections to pending after export. Current accepted source bindings are frozen here.'}
write(R/'review/south-completion-handoff.json',report)
historical=R/'review/recovery-SOUTH.json'
if historical.exists():
 old=read(historical);old['supersededBy']='review/south-completion-handoff.json';old['supersededAt']=now;write(historical,old)
(R/'review/south-completion-handoff.md').write_text('南向跑步三方向已完成离线美术验收，共48帧，原生1254×1254透明图独立生成，正式候选1024×1024RGBA。每方向16×75ms=1200ms。\n\nS、SE：右脚01–08连续支撑，左脚09–16连续支撑。SW：左脚01–08连续支撑，右脚09–16连续支撑。每半圈按01/02、03/04、05/06、07/08对应前落地、身体接近、身体通过、后蹬，各两种姿态；后半圈类推。\n\n最终选稿及逐图SHA见run-S/SE/SW-selection.json；实测每方向16帧顺序显示且无跳帧，循环1192–1211ms。浏览器逐帧图和原生图已核对，疑难后支撑与SW04→06另有独立读图通过。剩余必修图片项为空。\n\n非阻断观察：S正前投影中的后跟高度不如斜视易读；SW04→05前后遮挡转换较集中。客户端未接入，世界坐标落脚/无滑步未验证。\n\n离线预览：south-preview.html。动态预览：south-S-1x-1200ms.webp、south-SE-1x-1200ms.webp、south-SW-1x-1200ms.webp。\n\n请勿直接重跑build-south-current.py后跳过审计：该脚本会主动重置为待复核。完整证据及最终来源绑定见south-completion-handoff.json。\n',encoding='utf-8')
print(json.dumps({'passed':True,'finalCandidateCount':48,'remainingRequiredImageRepairs':[],'directions':list(directions)},ensure_ascii=False))
