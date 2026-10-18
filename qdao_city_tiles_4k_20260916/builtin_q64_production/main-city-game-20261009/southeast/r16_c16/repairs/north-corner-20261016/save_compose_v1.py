from pathlib import Path
import json,hashlib,datetime,shutil,sys
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def verify(e):assert sha(e['path'])==e['sha256'];return Path(e['path'])
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def wr(p,j):assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,a):assert not p.exists();Image.fromarray(a).save(p);return ev(p)
src=Path(sys.argv[1]);im=Image.open(src);assert im.size==(1254,1254) and (im.mode!='RGBA' or im.getextrema()[3]==(255,255))
dest=D/('actual-native-'+sha(src)[:16]+'.png');assert not dest.exists();shutil.copyfile(src,dest)
prep=rd(D/'preparation.json');wr(D/'receipt.json',dict(schemaVersion=1,tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,modelEvidence='Builtin returned image and original path; actual model and quality metadata not returned.',originalOutputPath=str(src),originalSha256=sha(src),savedNative=ev(dest),savedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),width=1254,height=1254,format='PNG',mode=im.mode,preparation=ev(D/'preparation.json'),request=ev(D/'request.json'),prompt=ev(D/'prompt.txt'),references=[prep['target'],prep['markedGuide']],resizedAfterGeneration=False,formalAccepted=False))
base=rgb(verify(prep['base']));native=rgb(dest);x0,y0,x1,y1=prep['destinationCoreBox'];u0,v0,u1,v1=prep['sourceCrop']
cut=native[v0:v1,u0:u1];old=base[y0:y1,x0:x1];err=np.mean((old.astype(float)-cut.astype(float))**2,axis=2);hh,ww=err.shape
def dp(e):
 h,w=e.shape;s=e.copy();back=np.zeros((h,w),np.int16)
 for x in range(1,w):
  for y in range(h):
   ya=max(0,y-1);yb=min(h,y+2);q=ya+int(np.argmin(s[ya:yb,x-1]));s[y,x]+=s[q,x-1];back[y,x]=q
 p=np.empty(w,np.int16);p[-1]=np.argmin(s[:,-1])
 for x in range(w-1,0,-1):p[x-1]=back[p[x],x]
 return p
alpha=np.ones((hh,ww),float);paths={};widths=dict(left=32,right=32,bottom=32)
for side,width in widths.items():
 e=err[:,:width].T if side=='left' else err[:,-width:][:,::-1].T if side=='right' else err[-width:,:][::-1]
 p=dp(e);paths[side]=p;dep=np.arange(ww if side!='bottom' else hh)[:,None];a=np.clip((dep-p[None,:])/6,0,1)
 if side=='left':a=a.T
 elif side=='right':a=a[::-1].T
 else:a=a[::-1]
 alpha=np.minimum(alpha,a)
a=np.rint(alpha*255).astype(np.uint8);O=D/'trial-v1';O.mkdir(exist_ok=False);alphaev=save(O/'alpha-crop.png',a);np.savez_compressed(O/'minimum-error-paths.npz',**paths)
aa=a.astype(np.uint32)[...,None];output=base.copy();output[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-aa)+cut.astype(np.uint32)*aa+127)//255).astype(np.uint8)
scalar=base.copy()
for yy in range(hh):
 for xx in range(ww):
  w=int(a[yy,xx])
  for c in range(3):scalar[y0+yy,x0+xx,c]=(int(base[y0+yy,x0+xx,c])*(255-w)+int(cut[yy,xx,c])*w+127)//255
assert np.array_equal(output,scalar)
support=np.zeros((4096,4096),bool);support[y0:y1,x0:x1]=a>0;assert np.array_equal(output[~support],base[~support])
core=save(O/'candidate-4096.png',output);ctx=rgb(verify(prep['baseContext']));ctx[115:4211,115:4211]=output;context=save(O/'context-4326.png',ctx)
north=rgb(verify(prep['north']));local=np.concatenate([north[3776:,750:2004],output[:934,750:2004]],axis=0)
evidence=[]
def qa(name,arr,box):
 e=save(O/(name+'.png'),arr);e.update(coordinateBox=box,scale='1:1',resampling=False);evidence.append(e)
qa('composed-local-1254',local,[750,-320,2004,934])
qa('north-core-join-q1-100pct',np.concatenate([north[3776:,1024:2048],output[:320,1024:2048]],axis=0),[1024,-320,2048,320])
for name,box in dict(left=[204,256,396,984],right=[804,256,996,984],bottom=[236,824,964,1016],top=[236,224,964,416]).items():
 x,y,xx,yy=box;qa(name+'-boundary-100pct',local[y:yy,x:xx],box)
co=dict(schemaVersion=1,tile='r16_c16',id='N02-north-corner',base=prep['base'],baseContext=prep['baseContext'],north=prep['north'],native=ev(dest),receipt=ev(D/'receipt.json'),preparation=ev(D/'preparation.json'),sourceCrop=prep['sourceCrop'],destinationCoreBox=prep['destinationCoreBox'],alpha=alphaev,minimumErrorPaths=ev(O/'minimum-error-paths.npz'),seamWidths=widths,fadePixels=6,blendArithmetic='(old*(255-alpha)+native*alpha+127)//255 RGB integer',resampling=False,RGBColorCorrection=False,independentScalarReplayExact=True,outsideMaskExact=True,northPixelsImmutable=True,contextPolicy='Only core section replaced; base outer halo retained. Actual north core join QA uses immutable real neighbor, not context halo.',core=core,context=context,evidence=evidence,status='trial_pending_visual_qa',formalAccepted=False,published=False)
wr(O/'composition.json',co);print(json.dumps(dict(native=ev(dest),core=core,context=context,composition=ev(O/'composition.json'))))

