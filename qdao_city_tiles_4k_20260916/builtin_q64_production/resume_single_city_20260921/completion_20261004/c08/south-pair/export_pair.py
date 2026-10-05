from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;C=R.parent;O=R/"candidate-v1";Q=O/"qa"
O.mkdir(exist_ok=True);Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=json.loads((R/"base.json").read_text());n=np.array(Image.open(base["north"]).convert("RGB"));s=np.array(Image.open(base["south"]).convert("RGB"));strip=np.array(Image.open(R/"strip-04.png").convert("RGB"))
assert sha(base["north"])==base["northSha256"] and sha(base["south"])==base["southSha256"]
n2=n.copy();s2=s.copy();n2[3469:]=strip[:627];s2[:627]=strip[627:]
items=[]
for name,a,old in [("r08_c08",n2,n),("r09_c08",s2,s)]:
 p=O/(name+".png");Image.fromarray(a).save(p)
 d=np.any(a!=old,axis=2);yy,xx=np.where(d)
 items.append({"file":str(p),"sha256":sha(p),"size":[4096,4096],"changedPixels":int(d.sum()),"changedBoundsLTRB":[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]})
 Image.fromarray(a).resize((1024,1024)).save(O/(name+"-overview-only.png"))
for axis in ["x","y"]:
 for k in [1024,2048,3072]:
  tiles=[]
  for t in range(4):
   if axis=="x":tile=n2[t*1024:(t+1)*1024,k-160:k+160].transpose(1,0,2)
   else:tile=n2[k-160:k+160,t*1024:(t+1)*1024]
   tiles.append(tile)
  Image.fromarray(np.concatenate(tiles,axis=0)).save(Q/f"{axis}{k}-full.png")
junc=np.zeros((1536,1536,3),np.uint8)
for iy,y in enumerate([1024,2048,3072]):
 for ix,x in enumerate([1024,2048,3072]):junc[iy*512:(iy+1)*512,ix*512:(ix+1)*512]=n2[y-256:y+256,x-256:x+256]
Image.fromarray(junc).save(Q/"nine-intersections.png")
for name,a,y in [("north-return-y3469",n2,3469),("south-return-y627",s2,627)]:
 Image.fromarray(np.concatenate([a[y-192:y+192,i*1024:(i+1)*1024] for i in range(4)],axis=0)).save(Q/(name+".png"))
pair=np.concatenate([n2[-192:],s2[:192]],axis=0)
Image.fromarray(np.concatenate([pair[:,i*1024:(i+1)*1024] for i in range(4)],axis=0)).save(Q/"south-full4096.png")
for i,x in enumerate([1100,2048,2996]):
 Image.fromarray(strip[:,x-192:x+192]).save(Q/f"overlap-{i+1}.png")
t=np.array(Image.open(C/"tone-candidate-v2/r08_c08.png").convert("RGB"))
report={"outputs":items,"derivedFrom":base,"pairedStrip":{"file":str(R/"strip-04.png"),"sha256":sha(R/"strip-04.png")},"operation":"Native row copy only: north bottom627 + south top627 from native1254 paired strip. No upscale.","invariants":{"northOutsideBottom627Unchanged":bool(np.array_equal(n2[:3469],n[:3469])),"southOutsideTop627Unchanged":bool(np.array_equal(s2[627:],s[627:])),"northFirst3469RowsEqualPreviouslyInspectedToneV2":bool(np.array_equal(n2[:3469],t[:3469])),"allNine512pxIntersectionCropsEqualToneV2":bool(np.array_equal(junc,np.concatenate([np.concatenate([t[y-256:y+256,x-256:x+256] for x in [1024,2048,3072]],axis=1) for y in [1024,2048,3072]],axis=0)))},"formalAccepted":False,"scope":"c08 internal continuity and paired south join only; all other external joins require current-neighbor rebind."}
(O/"assembly.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
