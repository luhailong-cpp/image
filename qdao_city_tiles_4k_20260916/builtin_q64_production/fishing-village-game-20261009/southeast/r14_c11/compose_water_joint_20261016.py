from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
T=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast")/"r14_c11";Q=T/"qa"/"water-joint-20261016";ver=sys.argv[1]
def read(p):return json.loads(Path(p).read_text(encoding="utf8"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2))
r=read(T/f"joint-water-{ver}.receipt.json");raw=Path(r["sourcePath"]);saved=Q/f"joint-{ver}-raw.png";assert not saved.exists();saved.write_bytes(raw.read_bytes())
original=Image.open(Q/"input-native.png").convert("RGB");b=np.array(Image.open(saved).convert("RGB"));a=np.array(original);assert a.shape==b.shape==(1254,1254,3)
mask=np.zeros((1254,1254),bool);mask[430:830,115:1139]=True;result=a.copy();result[mask]=b[mask]
np.savez_compressed(Q/f"joint-{ver}-proof.npz",original=a,raw=b,mask=mask,result=result)
Image.fromarray(result).save(Q/f"joint-{ver}-bounded-frame.png")
sel=read(T/"selected-patches.json");outsel=json.loads(json.dumps(sel));records=[];gx,gy=40845,55693
for pid in ["p31","p41"]:
 p=T/sel["patches"][pid];arr=np.array(Image.open(p).convert("RGB"));out=arr.copy();px=40845;py=53248+(int(pid[1])-1)*1024-115
 x0=max(gx,px);y0=max(gy,py);x1=min(gx+1254,px+1254);y1=min(gy+1254,py+1254);lm=np.zeros((1254,1254),bool)
 mm=mask[y0-gy:y1-gy,x0-gx:x1-gx];lm[y0-py:y1-py,x0-px:x1-px]=mm
 v=out[y0-py:y1-py,x0-px:x1-px];v[mm]=b[y0-gy:y1-gy,x0-gx:x1-gx][mm]
 assert np.array_equal(out[~lm],arr[~lm])
 dest=Q/f"{pid}-water-joint-{ver}.png";Image.fromarray(out).save(dest)
 rec=dict(patch=pid,file=str(dest),sha256=sha(dest),original=str(p),originalSha256=sha(p),raw=str(saved),rawSha256=sha(saved),globalJointBox=[gx,gy,gx+1254,gy+1254],nativeGlobalBox=[px,py,px+1254,py+1254],maskBox=[115,430,1139,830],exactSameCoordinateRawPixels=True,outsideMaskPixelDifference=0,resamplingApplied=False,blendApplied=False,actualModel=None)
 write(dest.with_suffix(".png.derivation.json"),rec);records.append(rec);outsel["patches"][pid]=dest.relative_to(T).as_posix()
write(Q/f"joint-{ver}-selected-candidate.json",outsel);write(Q/f"joint-{ver}-adoption-instructions.json",dict(selectionSha256=sha(T/"selected-patches.json"),patches=records,canonicalChanged=False,allMustAdoptTogether=True))
for name,box in {"seam":[115,371,1139,883],"north":[115,350,1139,510],"south":[115,750,1139,910],"west":[35,350,195,910],"east":[1059,350,1219,910]}.items():Image.fromarray(result).crop(box).save(Q/f"{ver}-{name}.png")
print(json.dumps(dict(candidate=str(Q/f"joint-{ver}-bounded-frame.png"),rawSha256=sha(saved))))

