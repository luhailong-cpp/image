from pathlib import Path
from PIL import Image
import json,hashlib,datetime,subprocess,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
maps={'S':['01-v1','02-v2','03-v2','04-v1','07-v2','06-v3','07-v4','08-v4','09-v1','10-v1','11-v1','12-v1','13-v3','14-v2','15-v3','16-v7'],'SE':['01-v1','02-v2','03-v1','04-v2','05-v3','06-v2','07-v3','08-v4','09-v1','10-v1','11-v3','11-v2','13-v2','14-v2','15-v2','16-v3'],'SW':['01-v2','02-v1','03-v1','04-v2','05-v2','06-v3','07-v2','08-v2','09-v2','10-v3','11-v6','12-v2','13-v1','14-v1','15-v1','16-v2']}
notes={'S':{7:'07-v4：右后小腿稍伸，靴面朝S，鞋前部接地候选；后跟抬起仍较含蓄。',8:'08-v4：右后踝继续伸展，前掌朝S，左前脚准备换脚；不是最低像素对齐。',15:'15-v3：左后小腿下伸，鞋前部压低，右前脚底可见仍腾空。',16:'16-v7：左后腿已从高收改为下伸，鞋前部仍支持候选，右前靴准备接01。'},'SE':{2:'02-v2：右剑腕回到向左上斜举，已消除02孤立水平剑角；原膝踝支撑不变。',16:'16-v3：左后小腿真实下伸，前掌最低、后跟较高，右前靴保持待落地；比16-v2不再高收遮膝。'},'SW':{1:'近左腿前伸落地，远右腿后收；右剑前、近左符后。',2:'左前鞋全底边落地，左膝微压，远右靴后收。',3:'左靴接近体下，右腿腾空；右剑腕与左符腕开始回收。',4:'04-v2：左靴近体下受载；剑腕回到腰前中位、剑刃较竖，使03至05的回收连续。',5:'05-v2：左支撑腿在髋后，右膝抬起；近左符袖接近肩，远剑在腰后被发部分遮挡，接06后摆。',6:'06-v3：近左袖跨胸接符修正，左靴体后仍低位支撑，右膝前抬。',7:'07-v2：近左袖跨胸接符，左后小腿伸展至后鞋，右前靴鞋底可见尚未承重。',8:'08-v2：左后靴低位后支撑，右前靴下摆；右剑远侧后摆未交换。',9:'09-v2：右前靴落地，左后腿回收；近左符袖跨胸，远剑后摆。',10:'10-v3：保留两手连接，右前膝进一步压缩，左后靴小幅回收；三手10-v2拒绝。',11:'11-v6：右支撑近体下，左膝前通过；远剑腕实际回到腰中段、近左符袖跨胸，已去除旧11-v4额外靴。',12:'12-v2：右鞋仍体下支撑，左膝前抬；两手中位，归属正确。',13:'右后鞋支撑、左膝前抬；左符回到近侧后方，右剑前摆。',14:'右支撑腿向后伸，左前腿开始下伸，两鞋顺SW。',15:'右后鞋前部较低承重候选，左前靴底朝镜头尚在摆动。',16:'16-v2：后右靴下伸，前左靴近落地，头胸回向01的闭环位置；剑尖不再贴左边。'}}
allseq={}
for d,versions in maps.items():
 p=R/f'review/run-{d}-selection.json';s=json.loads(p.read_text('utf-8-sig')) if p.exists() else {'schemaVersion':1,'characterId':'01_ice_sword_girl','direction':d,'action':'run','canvasSize':[1024,1024],'nativeCanvasSize':[1254,1254],'referenceCharacter':'09_bamboo_archer_girl_current_user_confirmed'}
 old={f['frame']:f for f in s.get('frames',[])};frames=[]
 for i,v in enumerate(versions,1):
  source=f'drafts/run/{d}/{v}.png';im=Image.open(R/source);record=source+'.generation.json';j=json.loads((R/record).read_text('utf-8-sig'));assert im.size==(1254,1254) and im.mode=='RGBA';assert j['sha256']==sha(R/source)
  evidence=notes.get(d,{}).get(i,old.get(i,{}).get('notes','逐帧支撑观察待核'))
  foot=('left' if i<=8 else 'right') if d=='SW' else ('right' if i<=8 else 'left')
  frames.append({'frame':i,'path':source,'sourcePath':source,'sha256':sha(R/source),'nativeSize':list(im.size),'generationRecord':record,'candidatePath':f'candidate/run/{d}/{i:02}.png','durationMs':75,'status':'selected_for_preview','actualModel':None,'actualQuality':None,'notes':evidence,'actualContact':{foot:'support_candidate',('right' if foot=='left' else 'left'):'swing_or_precontact_candidate','confidence':'manual_visual_candidate_pending_1x','evidence':evidence}})
 assert len(set(f['sha256'] for f in frames))==16
 s.update(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),artStatus='needs_sequence_review',frames=frames,candidateExportCount=16,formalExportCount=0,clientIntegrated=False,clientRuntimeVerified=False,timing={'uniformCycleMs':1200,'frameDurationsMs':[75]*16,'offlineDefaultApplied':True,'clientVerified':False},events={'kind':'manual_visual_candidates_not_accepted','requestedStructure':{'firstFoot':'left' if d=='SW' else 'right','firstSupport':[[1,2],[3,4],[5,6],[7,8]],'secondSupport':[[9,10],[11,12],[13,14],[15,16]],'positions':['front_landing','body_approaching_support','body_passing_support','rear_push_off']},'eightConsecutiveSupportVerified':False},positionPairsVerified=False,dynamicArtAccepted=False,issues=['Latest repaired source selection exported for real browser 1x and step review; not yet accepted.'])
 write(p,s);subprocess.run([sys.executable,str(R/'tools/export_selected_sequence.py'),p.relative_to(R).as_posix()],check=True)
 for f in frames:f['candidateSha256']=sha(R/f['candidatePath']);f['candidateGenerationRecord']=f['candidatePath']+'.generation.json'
 write(p,s);allseq[d]=s
(R/'review/south-sequences.js').write_text('window.SOUTH_SEQUENCES = '+json.dumps(allseq,ensure_ascii=False)+';\n',encoding='utf-8')
print('Exported S SE SW:48 independent frames, source hashes and candidate records bound.')
