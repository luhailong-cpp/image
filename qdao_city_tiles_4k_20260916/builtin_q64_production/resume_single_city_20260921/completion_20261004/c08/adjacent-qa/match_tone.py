from pathlib import Path
from PIL import Image
import numpy as np,json,sys,hashlib
R=Path(__file__).resolve().parent;S=R.parents[2];sys.path.insert(0,str(S/"continuation_20261004/c07-recovery/vendor"));import cv2
O=R/"tone-v1";O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=json.loads((R/"bindings.json").read_text())["sources"];a={}
for k,v in bind.items():
 assert sha(v["file"])==v["sha256"];a[k]=np.array(Image.open(v["file"]).convert("RGB"))
notes=[]
for col in [7,8]:
 lk=[f"r{r:02d}_c{col:02d}" for r in [8,9]];rk=[f"r{r:02d}_c{col+1:02d}" for r in [8,9]]
 l=np.concatenate([a[k][:,-16:] for k in lk],axis=0).astype(np.float32);r=np.concatenate([a[k][:,:16] for k in rk],axis=0).astype(np.float32)
 lm=np.median(l[:,-5:-1],axis=1);rm=np.median(r[:,1:5],axis=1)
 sl=np.median(np.diff(l[:,-15:-5],axis=1),axis=1);sr=np.median(np.diff(r[:,5:15],axis=1),axis=1)
 j=rm-lm-6*(sl+sr)/2
 tx=np.maximum(np.max(np.std(l[:,-15:-5],axis=1),axis=1),np.max(np.std(r[:,5:15],axis=1),axis=1))
 valid=(tx<6)&(np.max(np.abs(j),axis=1)<30);idx=np.flatnonzero(valid);assert len(idx)>100
 vals=np.stack([np.interp(np.arange(8192),idx,j[idx,c]) for c in range(3)],axis=1).astype(np.float32)
 vals=cv2.medianBlur(vals.reshape(8192,1,3),5).reshape(8192,3);vals=cv2.GaussianBlur(vals,(1,0),sigmaX=0,sigmaY=5);vals=np.clip(vals,-24,24)
 d=np.arange(-192,192,dtype=np.float32)+.5;t=np.clip(1-np.abs(d)/192,0,1);t=t*t*(3-2*t);signed=np.where(d<0,.5,-.5)*t
 field=vals[:,None,:]*signed[None,:,None];np.save(O/f"boundary-c{col:02d}-field.npy",field.astype(np.float16))
 for i,(left,right) in enumerate(zip(lk,rk)):
  f=field[i*4096:(i+1)*4096]
  a[left][:,-192:]=np.rint(np.clip(a[left][:,-192:].astype(np.float32)+f[:,:192],0,255)).astype(np.uint8)
  a[right][:,:192]=np.rint(np.clip(a[right][:,:192].astype(np.float32)+f[:,192:],0,255)).astype(np.uint8)
 notes.append({"betweenColumns":[col,col+1],"validSampleCount":int(valid.sum()),"maxCorrection":float(np.abs(field).max()),"fieldFile":str(O/f"boundary-c{col:02d}-field.npy")})
outputs={}
for k,v in a.items():
 p=O/(k+".png");Image.fromarray(v).save(p);outputs[k]={"file":str(p),"sha256":sha(p),"pixels":[4096,4096]}
(R/"tone-bindings.json").write_text(json.dumps({"sources":outputs,"derivedFrom":bind,"operation":"Bounded RGB-only native seam matching ±192px, max12/255; continuous8192px estimator through row8/9 boundary. No source blur/resize/warp.","seams":notes,"formalAccepted":False},indent=2),encoding="utf-8")
print(json.dumps({"outputs":outputs,"seams":notes},indent=2))
