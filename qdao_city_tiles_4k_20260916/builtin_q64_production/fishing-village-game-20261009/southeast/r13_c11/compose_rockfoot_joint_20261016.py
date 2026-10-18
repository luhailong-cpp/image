from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageChops
T=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast")/"r13_c11";Q=T/"qa"/"rockfoot-joint-20261016"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2),encoding="utf8")
receipt=read(T/"joint-rockfoot-v1.receipt.json");raw=Path(receipt["sourcePath"]);im=Image.open(raw).convert("RGB");assert im.size==(1254,1254)
saved=Q/"joint-v1-raw.png";assert not saved.exists();saved.write_bytes(raw.read_bytes());assert sha(saved)==sha(raw)
original=Image.open(Q/"input-native.png").convert("RGB");a=np.array(original);b=np.array(im)
mask=np.zeros((1254,1254),dtype=bool)
boxes=[[350,480,940,800],[350,800,850,1165]]
for x0,y0,x1,y1 in boxes:mask[y0:y1,x0:x1]=True
composed=a.copy();composed[mask]=b[mask]
assert np.array_equal(composed[~mask],a[~mask])
Image.fromarray(composed).save(Q/"joint-v1-bounded-frame.png")
Image.fromarray(mask.astype(np.uint8)*255).save(Q/"joint-v1-mask.png")
np.savez_compressed(Q/"joint-v1-proof.npz",mask=mask,raw=b,original=a,result=composed)
source=read(Q/"input-native.derivation.json");sel=read(T/"selected-patches.json");selected_sha=sha(T/"selected-patches.json");plan=read(T/"coordinate-plan.json")
patches={x["id"] if "id" in x else x["patch"]:x for x in plan["patches"]}
records=[];outsel=json.loads(json.dumps(sel))
for pid in ["p21","p22","p31","p32"]:
 p=T/sel["patches"][pid];base=Image.open(p).convert("RGB");arr=np.array(base);out=arr.copy()
 # raw input frame lies at these exact global coordinates
 gx,gy=41473,50573
 px=(11-1)*4096+(int(pid[2])-1)*1024-115;py=(13-1)*4096+(int(pid[1])-1)*1024-115
 x0=max(gx,px);y0=max(gy,py);x1=min(gx+1254,px+1254);y1=min(gy+1254,py+1254)
 localmask=np.zeros((1254,1254),dtype=bool)
 if x1>x0 and y1>y0:
  m=mask[y0-gy:y1-gy,x0-gx:x1-gx];localmask[y0-py:y1-py,x0-px:x1-px]=m
  v=out[y0-py:y1-py,x0-px:x1-px];v[m]=b[y0-gy:y1-gy,x0-gx:x1-gx][m]
 assert np.array_equal(out[~localmask],arr[~localmask])
 outpath=Q/f"{pid}-rockfoot-joint-v1.png";assert not outpath.exists();Image.fromarray(out).save(outpath)
 changed=int(np.count_nonzero(np.any(arr[115:1139,115:1139]!=out[115:1139,115:1139],axis=2)))
 rec=dict(patch=pid,file=str(outpath),sha256=sha(outpath),original=str(p),originalSha256=sha(p),changedCorePixels=changed,raw=str(saved),rawSha256=sha(saved),nativeGlobalBox=[px,py,px+1254,py+1254],jointGlobalBox=[gx,gy,gx+1254,gy+1254],maskBoxesInJoint=boxes,exactSameCoordinateRawPixels=True,outsideMaskPixelDifference=0,resamplingApplied=False,blendApplied=False,actualModel=None)
 write(outpath.with_suffix(".png.derivation.json"),rec);records.append(rec);outsel["patches"][pid]=outpath.relative_to(T).as_posix()
write(Q/"joint-v1-selected-candidate.json",outsel)
write(Q/"joint-v1-adoption-instructions.json",dict(selectionSha256=selected_sha,patches=records,allMustAdoptTogether=True,canonicalChanged=False,geometryReview="pending",materialReview="pending"))
# native evidence cuts covering boundary and corrected point
for name,box in {"center":[250,400,1050,1000],"top":[280,400,1010,560],"bottom":[280,1085,920,1245],"left":[270,440,430,1205],"right-upper":[860,440,1020,840],"right-lower":[770,760,930,1205],"step":[780,730,1010,880]}.items():Image.fromarray(composed).crop(box).save(Q/f"v1-{name}.png")
print(json.dumps({"rawSha":sha(saved),"records":records}))

