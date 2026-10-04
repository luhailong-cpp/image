import json,hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
root=Path(__file__).resolve().parent
notes={
'cast-E-01':'聚势起点。面朝右、两手握同杆、双端红缨及双脚可辨；当前衣摆偏飘、宽站较原idle明显。根锚和比例未统一。',
'cast-E-03':'下沉聚势，膝弯和宽站可读。较E01身体位置右移，需修正固定根锚；不能原样判动态通过。',
'cast-E-05':'举枪聚力，双手与双端枪完整。身体/脚接近画布底，较E01存在尺度/位置波动，需修正。',
'cast-E-07':'高举蓄力，完整两手可辨。枪尖接近上缘；头身较相邻帧存在缩放/位置差，需后续独立重绘修正，不以逐帧bbox缩放解决。',
'cast-E-09':'E释放关键，向右弓步、双手贯通同杆、两端红缨完整。原生图静态结构可用；根锚和邻帧连续待验收。',
'cast-W-09':'W释放关键v4，脸与鼻尖朝左，左近侧高握/右远侧低握，保持W idle原枪轴向，双脚可辨。身体比例/根锚及邻帧连续待验收。'
}
entries=[]
for p in sorted(root.glob('cast-?-??.png')):
 im=Image.open(p)
 recp=Path(str(p)+'.generation.json')
 r=json.loads(recp.read_text(encoding='utf-8'))
 review={'status':'candidate','visualInspection':notes[p.stem],'staticAnatomy':'provisionally_readable','identity':'preserved','scaleAnchor':'unverified_requires_correction','dynamic':'not_tested_incomplete_sequence','client':'not_integrated'}
 r['review']=review
 recp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 entries.append({'file':p.name,'record':recp.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(im.size),'mode':im.mode,'alphaExtrema':list(im.getchannel('A').getextrema()),'review':review})
existing={e['file'] for e in entries}
missing=[f'cast-{d}-{n:02}.png' for d in ['E','W'] for n in range(1,17) if f'cast-{d}-{n:02}.png' not in existing]
status={'updatedAt':datetime.now(timezone.utc).isoformat(),'character':'10_crimson_spear_girl','action':'cast','expected':32,'presentCandidateCount':len(entries),'formalExportCount':0,'visualPassedCount':0,'dynamicPassedCount':0,'successfulImagegenOutputsIncludingRejected':9,'rejectedImageCountDeleted':3,'failedCalls':3,'directions':{'E':{'expected':16,'present':[1,3,5,7,9]},'W':{'expected':16,'present':[9]}},'durationMs':720,'frameDurationMs':45,'releaseFrame':9,'targetRootAnchor':[512,942],'targetCanvas':[1024,1024],'actualNativeCanvas':[1254,1254],'anchorStatus':'not aligned; no per-frame bbox scaling or lowest-foot grounding applied','generationRoute':'builtin','actualModel':None,'actualQuality':None,'stopReason':'E02首次network error，唯一重试connection failed；本轮停止重复请求，保留真实缺槽，不用API/CLI绕过。','entries':entries,'missing':missing,'client':'not integrated; local client absent'}
(root/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'present':len(entries),'missing':len(missing),'formal':0,'passed':0,'files':[e['file'] for e in entries]},ensure_ascii=False))

