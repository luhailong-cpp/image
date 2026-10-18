from pathlib import Path
import json,hashlib,datetime,shutil,sys
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;O=D/'W01-second-bottom-transition-20261016'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def verify(e):assert sha(e['path'])==e['sha256'],e['path'];return Path(e['path'])
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def write(p,j):assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,a):assert not p.exists();Image.fromarray(a).save(p);return ev(p)
idx=read(D/'trial-v1/trial-index.json');base=rgb(verify(idx['base']));working=base.copy();union=np.zeros((4096,4096),bool);steps=[]
for step in idx['steps']:
 co=read(verify(step))
 for k in ('actualNative','receipt','preparation','alpha','minimumErrorPaths','core','context'):verify(co[k])
 native=rgb(co['actualNative']['path']);assert native.shape==(1254,1254,3)
 a=np.array(Image.open(co['alpha']['path']));x0,y0,x1,y1=co['destinationCoreBox'];u0,v0,u1,v1=co['nativeCrop'];cut=native[v0:v1,u0:u1]
 scalar=working.copy()
 for yy in range(y1-y0):
  for xx in range(x1-x0):
   w=int(a[yy,xx])
   for c in range(3):scalar[y0+yy,x0+xx,c]=(int(working[y0+yy,x0+xx,c])*(255-w)+int(cut[yy,xx,c])*w+127)//255
 expected=rgb(co['core']['path']);assert np.array_equal(expected,scalar)
 support=np.zeros_like(union);support[y0:y1,x0:x1]=a>0;union|=support
 assert np.array_equal(scalar[~support],working[~support]);assert np.array_equal(scalar[3712:],base[3712:])
 ctx=rgb(co['context']['path']);assert np.array_equal(ctx[115:4211,115:4211],scalar)
 working=scalar;steps.append(dict(id=co['id'],composition=step,scalarPixelReplayExact=True,outsideMaskExact=True,south384PixelsExact=True))
write(D/'trial-v1/independent-replay-20261016.json',dict(reviewer='/root/assembly_resume',recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),base=idx['base'],steps=steps,finalCore=idx['finalCore'],exact=True,outsideUnionExact=bool(np.array_equal(working[~union],base[~union])),south384PixelsExact=True,formalAccepted=False))
src=Path(sys.argv[1]);im=Image.open(src);assert im.size==(1254,1254) and (im.mode!='RGBA' or im.getextrema()[3]==(255,255))
dest=O/('actual-native-'+sha(src)[:16]+'.png');assert not dest.exists();shutil.copyfile(src,dest)
prep=read(O/'preparation.json');write(O/'receipt.json',dict(schemaVersion=1,tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,modelEvidence='Builtin returned image and original output path only; no model or quality metadata.',originalOutputPath=str(src),originalSha256=sha(src),savedNative=ev(dest),savedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),width=1254,height=1254,format='PNG',mode=im.mode,preparation=ev(O/'preparation.json'),request=ev(O/'request.json'),prompt=ev(O/'prompt.txt'),references=prep['references'],resizedAfterGeneration=False,formalAccepted=False))
assert np.array_equal(working,rgb(verify(prep['base'])))
native=rgb(dest);u0,v0,u1,v1=prep['nativeCrop'];x0,y0,x1,y1=prep['destinationCoreBox'];cut=native[v0:v1,u0:u1];old=working[y0:y1,x0:x1]
err=np.mean((old.astype(float)-cut.astype(float))**2,axis=2);hh,ww=err.shape
def dp(cost):
 h,w=cost.shape;score=cost.copy();back=np.zeros((h,w),np.int16)
 for x in range(1,w):
  for y in range(h):
   ya=max(0,y-1);yb=min(h,y+2);q=ya+int(np.argmin(score[ya:yb,x-1]));score[y,x]+=score[q,x-1];back[y,x]=q
 p=np.empty(w,np.int16);p[-1]=np.argmin(score[:,-1])
 for x in range(w-1,0,-1):p[x-1]=back[p[x],x]
 return p
alpha=np.ones((hh,ww),float);paths={}
for side,width in {'top':8,'bottom':3,'right':10}.items():
 e=err[:width,:] if side=='top' else err[-width:,:][::-1] if side=='bottom' else err[:,-width:][:,::-1].T
 p=dp(e);paths[side]=p
 dep=np.arange(hh if side!='right' else ww)[:,None];a=np.clip((dep-p[None,:])/3,0,1)
 if side=='bottom':a=a[::-1]
 elif side=='right':a=a[::-1].T
 alpha=np.minimum(alpha,a)
a=np.rint(alpha*255).astype(np.uint8);trial=D/'trial-v2';trial.mkdir(exist_ok=False);save(trial/'alpha-crop.png',a);np.savez_compressed(trial/'minimum-error-paths.npz',**paths)
output=working.copy();aa=a.astype(np.uint32)[...,None];output[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-aa)+cut.astype(np.uint32)*aa+127)//255).astype(np.uint8)
scalar=working.copy()
for yy in range(hh):
 for xx in range(ww):
  w=int(a[yy,xx])
  for c in range(3):scalar[y0+yy,x0+xx,c]=(int(working[y0+yy,x0+xx,c])*(255-w)+int(cut[yy,xx,c])*w+127)//255
assert np.array_equal(output,scalar)
support=np.zeros((4096,4096),bool);support[y0:y1,x0:x1]=a>0
assert np.array_equal(output[~support],working[~support]);assert np.array_equal(output[3712:],base[3712:])
core=save(trial/'candidate-4096.png',output);ctx=rgb(verify(prep['baseContext']));ctx[115:4211,115:4211]=output;context=save(trial/'context-4326.png',ctx)
target=rgb(O/'target-1254.png');target[750:870,627:780]=output[3592:3712,:153]
local=save(trial/'composed-local-1254.png',target);evidence=[]
for name,box in {'left-boundary':[531,690,723,930],'right-boundary':[684,690,876,930],'top-boundary':[563,686,844,814],'bottom-boundary':[563,806,844,934]}.items():
 xx0,yy0,xx1,yy1=box;e=save(trial/(name+'-100pct.png'),target[yy0:yy1,xx0:xx1]);e.update(boxInTarget=box,scale='1:1');evidence.append(e)
co=dict(schemaVersion=1,id='W01-second-bottom-transition',status='trial_pending_visual_qa',base=prep['base'],baseContext=prep['baseContext'],actualNative=ev(dest),receipt=ev(O/'receipt.json'),preparation=ev(O/'preparation.json'),nativeCrop=prep['nativeCrop'],destinationCoreBox=prep['destinationCoreBox'],alpha=ev(trial/'alpha-crop.png'),minimumErrorPaths=ev(trial/'minimum-error-paths.npz'),seamWidths=dict(top=8,bottom=3,right=10),fadePixels=3,blendArithmetic='(old*(255-alpha)+native*alpha+127)//255; RGB integers',resampling=False,RGBColorCorrection=False,independentScalarReplayExact=True,outsideMaskExact=True,south384PixelsExact=True,core=core,context=context,local=local,evidence=evidence,formalAccepted=False,published=False)
write(trial/'composition.json',co);print(json.dumps(dict(native=ev(dest),core=core,context=context,composition=ev(trial/'composition.json'),replay=ev(D/'trial-v1/independent-replay-20261016.json'))))

