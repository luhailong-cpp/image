from pathlib import Path
from PIL import Image
import numpy as np,json,sys,hashlib
R=Path(__file__).resolve().parent;S=R.parents[2];sys.path.insert(0,str(S/"continuation_20261004/c07-recovery/vendor"));import cv2
O=R/"tone-v2";O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=json.loads((R/"tone-bindings.json").read_text())["sources"];a={k:np.array(Image.open(v["file"]).convert("RGB")) for k,v in bind.items()}
notes=[]
for col in [7,9]:
 lk=f"r08_c{col:02d}";rk=f"r09_c{col:02d}"
 l=a[lk][-16:].transpose(1,0,2).astype(np.float32);r=a[rk][:16].transpose(1,0,2).astype(np.float32)
 lm=np.median(l[:,-5:-1],axis=1);rm=np.median(r[:,1:5],axis=1)
 sl=np.median(np.diff(l[:,-15:-5],axis=1),axis=1);sr=np.median(np.diff(r[:,5:15],axis=1),axis=1)
 j=rm-lm-6*(sl+sr)/2
 tx=np.maximum(np.max(np.std(l[:,-15:-5],axis=1),axis=1),np.max(np.std(r[:,5:15],axis=1),axis=1))
 valid=(tx<6)&(np.max(np.abs(j),axis=1)<30);idx=np.flatnonzero(valid);assert len(idx)>100
 vals=np.stack([np.interp(np.arange(4096),idx,j[idx,c]) for c in range(3)],axis=1).astype(np.float32)
 vals=cv2.medianBlur(vals.reshape(4096,1,3),5).reshape(4096,3);vals=cv2.GaussianBlur(vals,(1,0),sigmaX=0,sigmaY=5);vals=np.clip(vals,-24,24)
 d=np.arange(-192,192,dtype=np.float32)+.5;t=np.clip(1-np.abs(d)/192,0,1);t=t*t*(3-2*t);signed=np.where(d<0,.5,-.5)*t
 field=(vals[:,None,:]*signed[None,:,None]).transpose(1,0,2);np.save(O/f"boundary-row8-c{col:02d}-field.npy",field.astype(np.float16))
 a[lk][-192:]=np.rint(np.clip(a[lk][-192:].astype(np.float32)+field[:192],0,255)).astype(np.uint8)
 a[rk][:192]=np.rint(np.clip(a[rk][:192].astype(np.float32)+field[192:],0,255)).astype(np.uint8)
 notes.append({"between":[lk,rk],"validSampleCount":int(valid.sum()),"maxCorrection":float(np.abs(field).max())})
outputs={}
for k,v in a.items():
 p=O/(k+".png");Image.fromarray(v).save(p);outputs[k]={"file":str(p),"sha256":sha(p),"pixels":[4096,4096]}
(R/"tone-v2-bindings.json").write_text(json.dumps({"sources":outputs,"derivedFrom":bind,"operation":"Bounded RGB-only native horizontal seam matching ±192px, max12/255. No source blur/resize/warp.","seams":notes,"formalAccepted":False},indent=2),encoding="utf-8")
Q=O/"qa";Q.mkdir(exist_ok=True)
for col in [7,8,9]:
 pair=np.concatenate([a[f"r08_c{col:02d}"][-192:],a[f"r09_c{col:02d}"][:192]],axis=0)
 Image.fromarray(np.concatenate([pair[:,i*1024:(i+1)*1024] for i in range(4)],axis=0)).save(Q/f"horizontal-c{col:02d}-full.png")
print(json.dumps(notes))
