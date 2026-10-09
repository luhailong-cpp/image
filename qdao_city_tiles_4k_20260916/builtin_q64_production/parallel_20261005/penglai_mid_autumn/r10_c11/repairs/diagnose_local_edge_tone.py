from pathlib import Path
from PIL import Image
import numpy as np,json,sys,hashlib
T=Path(__file__).resolve().parent.parent;R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
cv=engine.base.cv_module()
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def grad(a):g=cv.cvtColor(a,cv.COLOR_RGB2GRAY).astype(np.float32);y,x=np.gradient(g);return np.hypot(x,y)
mode=sys.argv[1];yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
if mode=='p11':
 D=T/'repairs/p11-north-leaves';src=T/'native/p11.png';context=ar(D/'north-leaves-v1-target.png');host=D/'north-leaves-v1.png';flowp=D/'bounded-v1/flow.npy';known=yy<627;alpha=sm((1024-xx)/100)*sm((1027-yy)/128);alpha[known]=0;dist=yy-627
else:
 D=T/'repairs/p24-water-join/east-centered-v2';src=T/'repairs/p24-water-join/host-result.png';context=ar(D/'context.png');host=D/'host-result.png';flowp=D/'bounded/flow.npy';known=xx>=627;alpha=sm((xx-270)/128)*sm((yy-115)/80);alpha[known]=0;dist=626-xx
flow=np.load(flowp);aligned=cv.remap(ar(host),xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE);res=context.astype(np.float32)-aligned.astype(np.float32);safe=known&(grad(context)<12)&(grad(aligned)<12)&(np.max(np.abs(res),axis=2)<40);_,labels=cv.distanceTransformWithLabels((~safe).astype(np.uint8),cv.DIST_L2,5,labelType=cv.DIST_LABEL_PIXEL);weight=sm((256-dist)/224)
for sigma in [1,3]:
 out=D/f'local-tone-sigma{sigma}';out.mkdir(exist_ok=False);den=cv.GaussianBlur(safe.astype(np.float32),(0,0),sigma);measured=cv.GaussianBlur(res*safe[:,:,None],(0,0),sigma)/np.maximum(den[:,:,None],1e-6);lut=np.zeros((int(labels.max())+1,3),np.float32);lut[labels[safe]]=measured[safe];raw=cv.GaussianBlur(lut[labels],(0,0),sigma);tone=np.clip(raw,-18,18)*weight[:,:,None];matched=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8);reg=np.where(known[:,:,None],context,matched);mixed=np.clip(np.rint(context*(1-alpha[:,:,None])+reg*alpha[:,:,None]),0,255).astype(np.uint8);frame=Image.fromarray(mixed);frame.save(out/'joint-frame.png');proposal=Image.open(src).convert('RGB')
 if mode=='p11':proposal.paste(frame.crop((0,627,1024,1027)),(115,115));boxes=[('qa-join',(0,477,1024,817)),('qa-return',(0,897,1024,1157)),('qa-right-return',(884,447,1164,1157))]
 else:proposal.paste(frame.crop((0,0,627,1254)),(512,0));proposal.paste(Image.fromarray(context).crop((627,0,742,1254)),(1139,0));boxes=[('qa-join',(467,180,787,1254)),('qa-return',(190,135,510,1254)),('qa-lower',(320,840,927,1254))]
 p=out/(mode+'-proposal.png');proposal.save(p);np.save(out/'tone.npy',tone);used=alpha>0
 report=dict(script=ref(__file__),source=ref(src),sourceAI=ref(host),fixedFlow=ref(flowp),proposal=ref(p),trueSupport=mode,measurement='same material known-support residual only; Gaussian field sigma local; artwork itself not blurred; no boundary adjacent RGB invented',fieldSigma=sigma,flowUnchanged=True,maxAppliedTone=float(np.abs(tone[used]).max()),rawOver18Fraction=float(np.any(np.abs(raw[used])>18,axis=1).mean()),mechanicalReturn256=True,canonicalUnchanged=True,visualPass=False);write(out/'diagnostic.json',report)
 for path in [p,out/'joint-frame.png']:write(Path(str(path)+'.generation.json'),dict(**ref(path),derivedFrom=[ref(src),ref(host)],operation=ref(out/'diagnostic.json'),actualModel=None,actualQuality=None))
 for name,box in boxes:q=out/(name+'.png');frame.crop(box).save(q);write(Path(str(q)+'.generation.json'),dict(**ref(q),source=ref(out/'joint-frame.png'),cropLTRB=list(box),nativeScale=1,actuallyViewed=False))
 print(json.dumps(report))
