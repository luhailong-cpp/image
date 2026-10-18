from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter
T=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast")/"r13_c11";Q=T/"qa"/"rockfoot-joint-20261016"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2),encoding="utf8")
r=read(T/"joint-rockfoot-v2.receipt.json");raw=Path(r["sourcePath"]);saved=Q/"joint-v2-raw.png";assert not saved.exists();saved.write_bytes(raw.read_bytes())
b=np.array(Image.open(saved).convert("RGB"));assert b.shape==(1254,1254,3)
old=np.load(Q/"joint-v1-proof.npz");a=old["original"];v1=old["result"];m=Image.fromarray(old["mask"].astype("uint8")*255)
outer=np.array(m.filter(ImageFilter.MaxFilter(41)))>0;inner=np.array(m.filter(ImageFilter.MinFilter(41)))>0
band=outer&~inner;result=v1.copy();result[band]=b[band];union=old["mask"]|band
assert np.array_equal(result[~union],a[~union]);assert np.array_equal(result[old["mask"]&~band],v1[old["mask"]&~band])
Image.fromarray(result).save(Q/"joint-v2-bounded-frame.png");np.savez_compressed(Q/"joint-v2-proof.npz",original=a,rawV1=old["raw"],maskV1=old["mask"],rawV2=b,maskV2=band,result=result)
sel=read(T/"selected-patches.json");records=[];outsel=json.loads(json.dumps(sel));gx,gy=41473,50573
for pid in ["p21","p22","p31","p32"]:
 p=T/sel["patches"][pid];arr=np.array(Image.open(p).convert("RGB"));out=arr.copy()
 px=40960+(int(pid[2])-1)*1024-115;py=49152+(int(pid[1])-1)*1024-115
 x0=max(gx,px);y0=max(gy,py);x1=min(gx+1254,px+1254);y1=min(gy+1254,py+1254)
 localmask=np.zeros((1254,1254),bool)
 if x1>x0 and y1>y0:
  mm=union[y0-gy:y1-gy,x0-gx:x1-gx];localmask[y0-py:y1-py,x0-px:x1-px]=mm
  v=out[y0-py:y1-py,x0-px:x1-px];v[mm]=result[y0-gy:y1-gy,x0-gx:x1-gx][mm]
 assert np.array_equal(out[~localmask],arr[~localmask])
 dest=Q/f"{pid}-rockfoot-joint-v2.png";assert not dest.exists();Image.fromarray(out).save(dest)
 rec=dict(patch=pid,file=str(dest),sha256=sha(dest),original=str(p),originalSha256=sha(p),changedCorePixels=int(np.count_nonzero(np.any(arr[115:1139,115:1139]!=out[115:1139,115:1139],axis=2))),jointGlobalBox=[gx,gy,gx+1254,gy+1254],nativeGlobalBox=[px,py,px+1254,py+1254],raws=[{"path":str(Q/"joint-v1-raw.png"),"sha256":sha(Q/"joint-v1-raw.png")},{"path":str(saved),"sha256":sha(saved)}],proof=str(Q/"joint-v2-proof.npz"),exactSameCoordinateRawPixels=True,outsideMaskPixelDifference=0,resamplingApplied=False,blendApplied=False,actualModel=None)
 write(dest.with_suffix(".png.derivation.json"),rec);records.append(rec);outsel["patches"][pid]=dest.relative_to(T).as_posix()
write(Q/"joint-v2-selected-candidate.json",outsel);write(Q/"joint-v2-adoption-instructions.json",dict(selectionSha256=sha(T/"selected-patches.json"),patches=records,allMustAdoptTogether=True,canonicalChanged=False,geometryReview="pending",materialReview="pending"))
for name,box in {"center":[250,400,1050,1000],"top":[280,380,1010,580],"bottom":[280,1065,920,1254],"left":[250,440,450,1220],"right-upper":[840,440,1040,860],"right-lower":[750,740,950,1220],"step":[760,710,1030,900]}.items():Image.fromarray(result).crop(box).save(Q/f"v2-{name}.png")
print(json.dumps({"output":str(Q/"joint-v2-bounded-frame.png"),"rawSha256":sha(saved),"rawV1RetainedInside":True,"outsideUnionPixelDifference":0}))

