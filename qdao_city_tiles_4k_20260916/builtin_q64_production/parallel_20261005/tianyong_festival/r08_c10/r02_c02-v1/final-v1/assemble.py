from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c02-v1/final-v1');D.mkdir(exist_ok=True);(D/'qa').mkdir(exist_ok=True)
P=D.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp_path=T/'source-checkpoint.json';cp=json.loads(cp_path.read_text(encoding='utf-8'))
assert sha(cp_path)=='be5236befc3ae8bbb65a66bc7304cb6827a53d730fb630ba9e2a63ebaad1dbf2'
(D/'source-checkpoint-input.json').write_bytes(cp_path.read_bytes())
c=np.array(Image.open(cp['fragment']['file']).convert('RGBA').crop((909,909,2163,2163)))
n=np.array(Image.open(P/'lower-repair-v3/native.png').convert('RGB')).astype(np.float32)
h,w=n.shape[:2];yy,xx=np.mgrid[:h,:w].astype(np.float32)
topdx=np.interp(np.arange(w),[0,180,450,800,1100,1253],[-1,-1,0,0,-1,-1]).astype(np.float32)
botdx=np.interp(np.arange(w),[0,180,450,800,1100,1253],[1,1,0,0,-1,-1]).astype(np.float32)
tf=np.clip((500-yy)/300,0,1);bf=np.clip((yy-1000)/200,0,1)
dx=tf*topdx[None,:]+bf*botdx[None,:];dy=np.zeros_like(dx)
reg=cv2.remap(n,xx+dx,yy,interpolation=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
tone=np.zeros_like(reg)
# Native source colors, low-frequency only, small <=12 RGB correction.
top_delta=np.median(c[155:220,:,:3].astype(float)-reg[155:220],axis=0).astype(np.float32)
top_delta=cv2.GaussianBlur(top_delta[None,:,:],(61,1),0)[0]
bottom_delta=np.median(c[1185:1226,:,:3].astype(float)-reg[1185:1226],axis=0).astype(np.float32)
bottom_delta=cv2.GaussianBlur(bottom_delta[None,:,:],(61,1),0)[0]
tone += np.clip(top_delta,-12,12)[None,:,:]*np.clip((450-yy)/250,0,1)[:,:,None]
tone += np.clip(bottom_delta,-12,12)[None,:,:]*np.clip((yy-1050)/150,0,1)[:,:,None]
reg=np.clip(reg+tone,0,255)
alpha=np.ones((h,w),np.float32)
alpha[:150]=0
alpha[150:230]=np.linspace(0,1,80)[:,None]
alpha[:230,:80]=0
# Interpolate horizontally from frozen top-left corner to top return; no changed pixels within80x230.
alpha[150:230,80:140]*=np.linspace(0,1,60)[None,:]
alpha[1170:1226]=np.linspace(1,0,56)[:,None]
alpha[1226:]=0
joined=np.round(reg*alpha[:,:,None]+c[:,:,:3]*(1-alpha[:,:,None])).clip(0,255).astype(np.uint8)
assert np.array_equal(joined[:230,:80],c[:230,:80,:3])
assert np.array_equal(joined[1226:],c[1226:,:,:3])
Image.fromarray(joined).save(D/'joined.png')
Image.fromarray(np.uint8(alpha*255)).save(D/'mask.png')
np.save(D/'flow.npy',np.stack([dx,dy],2));np.save(D/'tone.npy',tone)
qa={'top':(0,100,1254,360),'bottom':(0,1000,1254,1254),'left-full':(0,0,360,1254),'right-full':(954,0,1254,1254),'bottom-left':(0,850,600,1254),'bottom-right':(754,850,1254,1254)}
for name,b in qa.items():Image.fromarray(joined).crop(b).save(D/'qa'/f'{name}.png')
assembly={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCheckpoint':info(D/'source-checkpoint-input.json'),'native':info(P/'lower-repair-v3/native.png'),'sources':[info(P/'native.png'),info(P/'lower-repair-v2/native.png'),info(P/'lower-repair-v3/native.png'),cp['fragment']],'method':'NativeAI completed structure, bounded bilinear x registration, small low-frequency tone matching, explicit top and bottom overlap compositing. No rescale. Wrong lower broad panel replaced with actual AI complete rings.','nativeScale':1,'maxAbsDx':float(abs(dx).max()),'maxAbsDy':0,'maxAbsToneRGB':float(abs(tone).max()),'toneLimit':12,'field':info(D/'flow.npy'),'tone':info(D/'tone.npy'),'mask':info(D/'mask.png'),'joined':info(D/'joined.png'),'fixedTopLeft80x230Exact':True,'bottomLast28Exact':True,'qaCrops':qa,'reviewStatus':'pending-rootandagentvisual'}
(D/'assembly.json').write_text(json.dumps(assembly,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'joined.png.generation.json').write_text(json.dumps({'derivation':'registered-native-composite','file':str(D/'joined.png'),'sha256':sha(D/'joined.png'),'nativeScale':1,'nativeSources':assembly['sources'],'actualModel':None,'actualQuality':None,'assembly':info(D/'assembly.json'),'formalAccepted':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'joined':info(D/'joined.png'),'maxAbsDx':assembly['maxAbsDx'],'maxAbsToneRGB':assembly['maxAbsToneRGB']}))

