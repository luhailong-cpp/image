from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
D=ROOT/'r09_c08/r04c04-east-repair'; O=D/'registered-v1'; assert O.resolve().is_relative_to(ROOT)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def meta(p):
 im=Image.open(p).convert('RGB'); return {'path':str(p),'sha256':sha(p),'width':im.width,'height':im.height,'rgbSha256':hashlib.sha256(im.tobytes()).hexdigest()}
processing=json.loads((O/'processing.json').read_text())
manifest=json.loads((O/'qa-export.json').read_text())
notes={
 'east-row4':'固定端的 9px 深色上缘跳变和尖 V 已消除；弧线平顺减速接入东邻，边缘连通无缺口。局部手绘明暗仍有轻微差别，未形成贯穿石面的竖直曝光带。',
 'patch-full':'从原画过渡到 AI 修复段，再到固定东端，只有单条连续石槽；无分叉、重复线、硬台阶或明显锐角。',
 'guide-x3981':'guide x3981 所在原像素条带中曲线与底材连续，未见新的条带。',
 'internal-y3072':'上方行接缝处保留原始像素关系，石槽与底材连续。',
 'patch-entry-x640':'补丁起点权重由0平顺增加，原画端无断槽或轮廓跳位。',
 'patch-entry-x780':'补丁权重达到1的位置未见重复石槽、接缝印痕或色带。',
 'patch-outer-bottom':'下部边界为原有低对比石面，未见矩形边框或曝光跳变。',
 'guide-y3187':'横向参考过渡位置的斜槽与平面连续，未见横向断线或色带。'
}
cropmaps={
 'guide-x3981':[960,115,1088,1139], 'patch-entry-x640':[576,115,704,400],
 'patch-entry-x780':[716,115,844,400], 'patch-full':[576,115,1254,400],
 'patch-outer-bottom':[576,300,1254,420], 'guide-y3187':[115,166,1139,294]
}
candidate=O/'candidate1254.png'; cp=meta(candidate)
views=[]
for e in manifest['boards']:
 p=Path(e['path']); assert sha(p)==e['sha256']; assert meta(p)['rgbSha256']==e['rgbSha256']
 e.update(actualViewCompleted=True,viewTool='tools.view_image',detail='original',viewCount=1,observation=notes[e['id']],status='no-actionable-defect-seen')
 if e['id'] in cropmaps:
  e['sourceMappings']=[{'source':cp,'sourceCrop':cropmaps[e['id']],'destinationBox':[0,0,e['width'],e['height']]}]
 elif e['id']=='east-row4':
  e['sourceMappings']=[{'source':cp,'sourceCrop':[883,115,1139,1139],'destinationBox':[0,0,256,1024]},{'source':meta(ROOT/'r09_c09/selected/core4096.png'),'sourceCrop':[0,3072,256,4096],'destinationBox':[256,0,512,1024]}]
 else:
  e['sourceMappings']=[{'source':meta(ROOT/'r09_c08/native/r03_c04.png'),'sourceCrop':[115,1011,1139,1139],'destinationBox':[0,0,1024,128]},{'source':cp,'sourceCrop':[115,115,1139,243],'destinationBox':[0,128,1024,256]}]
 views.append(e)
orig=np.asarray(Image.open(D/'original/native/r04_c04.png').convert('RGB'))
current=np.asarray(Image.open(ROOT/'r09_c08/native/r04_c04.png').convert('RGB'))
assert np.array_equal(orig,current), 'Original native must not be overwritten by this task'
native=Image.open(candidate).convert('RGB'); gray=np.asarray(native).mean(2)
spans={}
for x in [1138,1139]:
 ys=np.where(gray[150:330,x]<160)[0]+150; spans[str(x)]=[int(ys[0]),int(ys[-1])]
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'candidate':cp,'processingPath':str(O/'processing.json'),'processingSha256':sha(O/'processing.json'),'reviewer':'/root/c08_east_qa','actualOriginalPixelViews':8,'views':views,'automaticAcceptance':False,'status':'Repair candidate passes this local visual review; parent review / ingestion pending.','wholeTileAccepted':False,'originalNativeUnmodified':True,'supportingGeometryEvidence':{'darkSpanAtNativeX1138':spans['1138'],'darkSpanAtNativeX1139':spans['1139'],'darkUpperEdgeJump':spans['1139'][0]-spans['1138'][0],'darkLowerEdgeJump':spans['1139'][1]-spans['1138'][1],'note':'Measured supporting evidence only; actual visual review performed independently.'},'rawAiAttempt':{'file':str(D/'ai-attempt01/native/r04_c04.png'),'status':'Unregistered native AI repaint failed fixed-end alignment and is not selected directly.','generationRecord':str(D/'ai-attempt01/native/r04_c04.png.generation.json'),'rawEastBoardActualViewed':True,'rawEastBoard':meta(D/'attempt01-east-row4.png')},'nativeCallsForThisRepair':1}
(O/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ai_record=json.loads((D/'ai-attempt01/native/r04_c04.png.generation.json').read_text(encoding='utf-8-sig'))
generation={'schemaVersion':1,'file':str(candidate),'sha256':sha(candidate),'width':1254,'height':1254,'format':'PNG','mode':'RGB','createdAt':datetime.now(timezone.utc).isoformat(),'isDerived':True,'operation':processing['operation'],'derivedFrom':[{'path':str(D/'original/native/r04_c04.png'),'sha256':sha(D/'original/native/r04_c04.png'),'generationRecord':str(D/'original/native/r04_c04.png.generation.json')},{'path':str(D/'ai-attempt01/native/r04_c04.png'),'sha256':sha(D/'ai-attempt01/native/r04_c04.png'),'generationRecord':str(D/'ai-attempt01/native/r04_c04.png.generation.json')},{'path':str(ROOT/'r09_c09/selected/extended4326.png'),'sha256':sha(ROOT/'r09_c09/selected/extended4326.png'),'deliveryRecord':str(ROOT/'r09_c09/selected/delivery.manifest.json')}],'processingRecord':str(O/'processing.json'),'processingSha256':sha(O/'processing.json'),'reviewRecord':str(O/'review.json'),'reviewSha256':sha(O/'review.json'),'configSnapshot':ai_record['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'note':'This derived image did not invoke a model; the native AI input actual submitted parameters are in its own generation record.'},'actualModel':None,'actualQuality':None,'unverifiedReason':'No model invocation for registration/compositing. Native builtin input models and qualities are host-managed and undisclosed.','status':'Candidate only; not yet replacing root native.'}
(O/'candidate1254.png.generation.json').write_text(json.dumps(generation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':cp,'reviewSha256':sha(O/'review.json'),'processingSha256':sha(O/'processing.json'),'generationSha256':sha(O/'candidate1254.png.generation.json'),'geometry':report['supportingGeometryEvidence']},indent=2))
