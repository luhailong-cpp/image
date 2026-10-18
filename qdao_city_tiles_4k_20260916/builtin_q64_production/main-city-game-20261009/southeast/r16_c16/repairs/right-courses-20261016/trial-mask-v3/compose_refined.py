from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
BASE=Path(__file__).resolve().parent;R=BASE.parent;D=BASE/'refined-v1';D.mkdir(exist_ok=False)
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def verify(e):assert sha(e['path'])==e['sha256'];return Path(e['path'])
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def save(p,a):assert not p.exists();Image.fromarray(a).save(p);return ev(p)
def wr(p,j):assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prior=rd(R/'trial-v2/composition.json');old=rgb(verify(prior['base']));op=prior['operations'][0];native=rgb(verify(op['source']));verify(op['receipt'])
xx0,yy0,xx1,yy1=op['destinationCoreBox'];target=old[yy0:yy1,xx0:xx1];err=np.mean((target.astype(float)-native.astype(float))**2,axis=2)
xs=np.arange(425,1254);topcent=np.rint(650+(xs-425)*(170-650)/(1254-425)).astype(int)
botcent=np.where(xs<=473,np.rint(1332-.45*xs),np.rint(1494-.667*xs)).astype(int)
def path_near(centres,offsets):
 costs=np.stack([err[np.clip(centres+off,0,1253),xs] for off in offsets])
 scores=costs.copy();back=np.zeros(scores.shape,np.int16)
 for i in range(1,len(xs)):
  for s in range(len(offsets)):
   a=max(0,s-1);b=min(len(offsets),s+2);p=a+np.argmin(scores[a:b,i-1]);scores[s,i]+=scores[p,i-1];back[s,i]=p
 p=np.empty(len(xs),np.int16);p[-1]=np.argmin(scores[:,-1])
 for i in range(len(xs)-1,0,-1):p[i-1]=back[p[i],i]
 return centres+offsets[p]
top=path_near(topcent,np.arange(0,25));bottom=path_near(botcent,np.arange(-2,3))
a=np.zeros((1254,1254),float);ys=np.arange(1254)[:,None]
a[:,xs]=np.minimum(np.clip((ys-top[None,:])/6,0,1),np.clip((bottom[None,:]-ys)/2,0,1))
a[:,xs]=np.minimum(a[:,xs],np.clip((xs[None,:]-425)/6,0,1))
alpha=np.rint(a*255).astype(np.uint8);ap=save(D/'upper-alpha.png',alpha);np.savez_compressed(D/'upper-minimum-error-paths.npz',x=xs,top=top,bottom=bottom,topSeed=topcent,bottomSeed=botcent)
out=old.copy();aa=alpha.astype(np.uint32)[...,None];out[yy0:yy1,xx0:xx1]=((target.astype(np.uint32)*(255-aa)+native.astype(np.uint32)*aa+127)//255).astype(np.uint8)
support=np.zeros((4096,4096),bool);support[yy0:yy1,xx0:xx1]=alpha>0;assert np.array_equal(out[~support],old[~support])
replay=old.copy()
for ch in range(3):replay[yy0:yy1,xx0:xx1,ch]=((target[:,:,ch].astype(np.int64)*(255-alpha.astype(np.int64))+native[:,:,ch].astype(np.int64)*alpha.astype(np.int64)+127)//255).astype(np.uint8)
assert np.array_equal(replay,out)
core=save(D/'candidate-upper-only-4096.png',out);ctx=rgb(verify(prior['baseContext']));ctx[115:4211,115:4211]=out;context=save(D/'context-upper-only-4326.png',ctx)
local=out[yy0:yy1,xx0:xx1];save(D/'upper-composed-local-1254.png',local)
evidence=[]
boxes={'upper-top-left':[390,350,880,770],'upper-top-right':[820,120,1254,500],'upper-bottom-left':[390,930,780,1254],'upper-bottom-middle':[730,720,1080,1080],'upper-bottom-right':[1000,560,1254,860],'upper-left-boundary':[340,600,520,1230],'upper-right-map-border':[1150,120,1254,880],'upper-corner':[390,990,600,1254],'upper-joint':[730,850,900,1050]}
for name,b in boxes.items():
 x,y,x1,y1=b;e=save(D/(name+'-100pct.png'),local[y:y1,x:x1]);e.update(localBox=b,scale='1:1',resampling=False);evidence.append(e)
newop=dict(id='upper',source=op['source'],receipt=op['receipt'],alpha=ap,minimumErrorPaths=ev(D/'upper-minimum-error-paths.npz'),destinationCoreBox=op['destinationCoreBox'],nativeCrop=[0,0,1254,1254],maskMethod='Min-error top cut, narrow min-error bottom path constrained at/above native bottom shadow. Original wall pixels resumed below that path. Left alpha6, top alpha6, bottom alpha2.',resampling=False,RGBColorCorrection=False)
co=dict(schemaVersion=1,recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),base=prior['base'],baseContext=prior['baseContext'],operations=[newop],core=core,context=context,blendArithmetic=prior['blendArithmetic'],outsideMaskExact=True,independentChannelReplayExact=True,sourceNativeUnmodified=True,lowerOperation='not adopted: lower actual native corner still has approximately50px drop between front and side cap top',lowerSource=prior['operations'][1]['source'],evidence=evidence,status='upper_mask_trial_pending_QA_lower_failed_pending',formalAccepted=False,published=False)
wr(D/'composition.json',co);print(json.dumps(dict(core=core,context=context,composition=ev(D/'composition.json'))))

