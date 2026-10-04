import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
r=Path(__file__).resolve().parents[2]
names=['16-v1','01-v1','02-v2','03-v2','05-v8','06-v4','07-v2','08-v4','09-v10','10-v7','10-v2','11-v1','13-v4','14-v2','15-v3','16-v3']
observations=[
'右腿向跑向前伸，右鞋跟/外缘初接触；左腿后折鞋底可见，空右臂后摆。',
'右前侧接触继续加载，脚掌趋平，右膝缓冲；左腿仍后折，空右臂后摆回程。',
'右脚向髋下回收进入中段，右膝明显屈曲承重；左脚仍在后方回收，右空手回到身侧。',
'右髋下承重，右膝稍伸，左膝开始经过；空右臂向前回摆的过渡姿态。',
'右脚继续髋下平掌支撑，左膝向前经过、抬鞋由整底转后跟，空右臂前摆。',
'右脚中段末承重，左膝更向前并部分遮挡左鞋；右鞋掌朝地，空右臂前摆。',
'近侧右腿斜向左下髋后伸展，前掌仍朝地、后跟抬起；远侧左膝前抬，空右臂前摆。',
'右后侧推蹬幅度变化，右鞋前掌端保持接触；左腿向前准备换脚，右空臂前摆稍伸。',
'远侧左腿从左髋沿右前方斜伸，在近侧右抬腿之后；左鞋落在裆部下方前侧，跟部接触、鞋尖微抬。右腿仍在画面右方抬起，空右臂前摆。',
'同一远侧左腿屈膝加载，左踝向髋收回约半鞋长，左鞋掌更平；右腿继续抬起，未交换支撑脚，空右臂保持前摆。',
'左脚进入髋下中段，左膝缓冲更深；右膝后折恢复，右鞋底仍可见，空右臂前摆回程。',
'左髋下持续支撑，右恢复腿收回，右鞋底面积减小；空右臂回到身侧。',
'左中段后半平掌承重、膝开始伸展，右膝向前经过，空右臂后摆。',
'左中段末支撑，右膝已在跑向前方，右鞋为侧面而非整鞋底；空右臂后摆。',
'远侧左腿由髋下向左下后伸，鞋跟提起、前掌端接触；近侧右膝前抬，空右臂保持后摆，左手抱葫芦。',
'远侧左腿后伸幅度增加，前掌端仍朝地接触；近侧右腿准备前落，空右臂保持后摆、左手抱葫芦。']
frames=[]
for i,(n,obs) in enumerate(zip(names,observations),1):
 src=r/f'generation/run/NE/{n}.png'; im=Image.open(src); digest=hashlib.sha256(src.read_bytes()).hexdigest()
 assert im.size==(1254,1254) and im.mode=='RGBA'
 record=src.with_suffix('.png.generation.json'); assert record.exists()
 position=['front','front','middle','middle','middle','middle','rear','rear'][(i-1)%8]
 frames.append({'slot':f'run/NE/{i:02}','frame':i,'durationMs':75,'source':src.relative_to(r).as_posix(),'sha256':digest,'supportFoot':'right' if i<=8 else 'left','supportPositionAlongRun':position,'positionPair':['front','front','middle-early','middle-early','middle-late','middle-late','rear','rear'][(i-1)%8],'staticContact':'visible_contact','confidence':'medium-high' if position=='middle' else 'medium','observation':obs,'leftHand':'holds golden gourd continuously','rightHand':'empty swing','generationRecord':record.relative_to(r).as_posix(),'actualModel':None,'actualQuality':None})
assert len({x['sha256'] for x in frames})==16
data={'schemaVersion':1,'direction':'NE','status':'static_candidate_complete_dynamic_unverified','createdAt':datetime.now(timezone.utc).isoformat(),'rule':'per foot front2 + middle4 (two adjacent position pairs) + rear2; displacement along NE run axis, not outward foot rotation','frameDurationMs':75,'cycleDurationMs':1200,'nativeCanvas':[1254,1254],'rgba':True,'uniqueSources':16,'globalSelectionChanged':False,'formalExportsChanged':False,'dynamicVisualVerified':False,'staticMethod':'native images plus all16 full-canvas and lower-body contact sheets; actual thigh overlap, knee/ankle continuity, heel/sole shape and hand continuity, not prompt labels or alpha extrema','frames':frames,'hardStaticDefectsRemaining':[],'limitations':['Transparent sprite geometry supports visual contact judgement but does not calibrate world ground.','NE upper body has existing loading compression at slots03/11; no deterministic translation or per-frame fitting used.','No browser/client dynamic playback inspected; runtime slip and presentation acceptance remain unverified.'],'rejectedCandidates':{'09-v6/09-v7/10-v3/10-v4':'previous retries wrong stance leg or insufficient actual forward advance; not selected','09-v8/10-v5':'planted foreground leg starts near right hip and repeats right stance, rejected despite requested left pose','09-v9/10-v6':'left identity preserved but left shoe remains spatially beneath hip, insufficient front position','15-v2/16-v2':'left gourd hand or empty right arm changed; replaced by15-v3/16-v3'},'newFinalCandidates':{'09-v10':'left forward landing with far-left hip continuity','10-v7':'distinct subsequent left loading and flatter sole'}}
p=r/'generation/run/NE/selection-middle4-side2-20261004.json'; p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(r/'review/grounding-fourframes/NE-static-evidence-middle4-side2.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for file,op in [('NE-candidate-full.jpg','fixed native whole-canvas uniform thumbnail,4x4 labeled diagnostic montage'),('NE-candidate-legs.jpg','same fixed lower body crop(350,830,1030,1254) per native frame,4x4 labeled diagnostic montage')]:
 path=r/'review/grounding-fourframes'/file
 path.with_suffix(path.suffix+'.derivation.json').write_text(json.dumps({'file':path.relative_to(r).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'operation':op,'derivedFrom':[{'source':f['source'],'sha256':f['sha256'],'generationRecord':f['generationRecord']} for f in frames]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('NE selected16 unique nativeRGBA1254, right01-08/left09-16,75ms each,1200ms; global files untouched')
