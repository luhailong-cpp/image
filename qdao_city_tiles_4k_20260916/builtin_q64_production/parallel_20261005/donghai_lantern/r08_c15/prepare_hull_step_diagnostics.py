from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_lantern")
D=ROOT/"r08_c15/repairs/hull-step-final"
D.mkdir(parents=True,exist_ok=True)
base=ROOT/"r08_c15/repairs/approved-sync/output/r08_c15.png"
day=ROOT/"r08_c15/source-contract-v2/snapshots/verified-day-output/70ce623a54fb8419-candidate.png"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(base)=="908df2ad815315cac373cf0ace48c0f2493e45b981b729ee28741cae5da82fa9"
assert sha(day)=="70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585"
W=[1960,2390,3214,3644]
for name,source in (("target",base),("day-geometry",day)):
 p=D/(name+".png"); assert not p.exists()
 Image.open(source).convert("RGB").crop(W).save(p)
 rec={"file":str(p),"sha256":sha(p),"pixels":[1254,1254],"generatedByAI":False,"operation":"exact native same-coordinate crop","derivedFrom":[{"file":str(source),"sha256":sha(source)}],"tileRectXYXY":W,"resized":False}
 Path(str(p)+".generation.json").write_text(json.dumps(rec,indent=2)+"\n",encoding="utf-8")
Q=ROOT/"r08_c15/repairs/approved-sync/qa"
roi=[2140,3820,2340,4096]
native=ROOT/"r08_c15/repairs/consolidated-sync/native/d-right-bottom.png"
for name,src,rect in (("pink-sliver-final",base,roi),("pink-sliver-native",native,[roi[0]-1421,roi[1]-2842,roi[2]-1421,roi[3]-2842]),("pink-sliver-day",day,roi)):
 p=Q/(name+".png")
 Image.open(src).convert("RGB").crop(rect).save(p)
 Path(str(p)+".generation.json").write_text(json.dumps({"file":str(p),"sha256":sha(p),"generatedByAI":False,"operation":"exact diagnostic crop; no resize","derivedFrom":[{"file":str(src),"sha256":sha(src)}],"sourceCropXYXY":rect,"tileRectXYXY":roi},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"window":W,"destination":str(D)}))

