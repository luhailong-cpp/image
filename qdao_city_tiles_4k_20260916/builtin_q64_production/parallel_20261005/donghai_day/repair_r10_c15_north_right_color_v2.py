"""Same-geometry bounded RGB field at repaired north wooden joint only."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
import assembly_r10_c15 as a
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/north-right-color-v2';Q=D/'qa'
S=T/'repairs/north-right-integrated-v2/candidate.png';EXPECTED='ccf305b9fdb3074224517766a1c25c76ef3d893e2881af2625b42c03b51d872b'
N=R/'r09_c15/output/r09_c15.png';NS='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff'
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def raw(x):return hashlib.sha256(x.tobytes()).hexdigest()
def smooth(x):
 for _ in range(3):
  z=np.pad(x,((8,8),(0,0)),mode='edge');x=sum(z[i:i+len(x)] for i in range(17))/17
 return x
assert a.sha(S)==EXPECTED and a.sha(N)==NS
base=rgb(S);north=rgb(N);x0=3180;w=4096-x0;h=400
edge=np.median(north[-3:,x0:].astype(np.float32),axis=0)-np.median(base[:3,x0:].astype(np.float32),axis=0)
edge=np.clip(smooth(edge),-32,32)
exactEdge=np.clip(north[-1,x0:].astype(np.float32)-base[0,x0:].astype(np.float32),-32,32)
x=np.clip(np.arange(w,dtype=np.float32)/104,0,1);x=x*x*(3-2*x)
y=np.clip(1-np.arange(h,dtype=np.float32)/(h-1),0,1);y=y*y*(3-2*y)
short=np.clip(1-np.arange(h,dtype=np.float32)/48,0,1);short=short*short*(3-2*short)
field=(y[:,None,None]*edge[None,:,:]+short[:,None,None]*(exactEdge-edge)[None,:,:])*x[None,:,None]
material=np.clip((base[:h,x0:,0].astype(np.float32)-base[:h,x0:,2].astype(np.float32)-10)/35,0,1)
field=np.clip(field*material[:,:,None],-32,32)
image=base.copy();image[:h,x0:]=np.clip(np.rint(base[:h,x0:].astype(np.float32)+field),0,255).astype(np.uint8)
assert np.array_equal(image[h:],base[h:]) and np.array_equal(image[:,:x0],base[:,:x0])
out=a.save_image(D/'candidate.png',Image.fromarray(image));ex=rgb(S.parent/'extended-context.png');assert np.array_equal(ex[115:4211,115:4211],base);ex[115:4211,115:4211]=image
ei=a.save_image(D/'extended-context.png',Image.fromarray(ex));D.mkdir(parents=True,exist_ok=True);np.savez_compressed(D/'rgb-field.npz',field=field,edgeDelta=edge,materialWeight=material,sourceRect=np.array([x0,0,4096,h]))
a.QA=Q/'assembly';a.ART=D/'candidate.png';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(north));pair=np.concatenate([north,image],axis=0);extra=[]
for name,b in [('north-right-wide',[2842,3796,4096,4566]),('north-right-joint',[3100,3976,4096,4296])]:
 extra.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(pair[b[1]:b[3],b[0]:b[2]])),sourceRectInNorthPair=b,resized=False))
for name,b in [('north-right-left-insertion',[3060,0,3350,727]),('north-right-bottom-insertion',[3100,490,4096,727]),('color-lower-transition',[3180,280,4096,520])]:
 extra.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(image[b[1]:b[3],b[0]:b[2]])),sourceRectXYXY=b,resized=False))
a.save_json(D/'manifest.json',{'createdAtUtc':a.utc_now(),'baseline':{'file':str(S),'sha256':EXPECTED},'candidate':out,'extendedContext':ei,'north':{'file':str(N),'sha256':NS},'field':{'file':str(D/'rgb-field.npz'),'sha256':a.sha(D/'rgb-field.npz'),'rect':[x0,0,4096,h],'cap':32,'actualMaximum':float(np.max(np.abs(field))),'xLeftSmoothFade':104,'ySmoothFade':h,'xEdgeSmoothing':'17px box three times; field only','material':'continuous warm R-B weight; no hard class boundary','exactBoundaryResidual':'bounded per-column actual row RGB residual, smooth 48px vertical decay; artwork not resampled'},'qa':qa,'insertionQA':extra,'east627BelowY700RawRGBSha256':raw(image[700:,3469:]),'imageResampling':False,'imageBlur':False,'geometryUnchanged':True,'formalAccepted':False,'visualReview':'pending'})
print(json.dumps({'candidate':out,'east627BelowY700RawRGBSha256':raw(image[700:,3469:])}))
