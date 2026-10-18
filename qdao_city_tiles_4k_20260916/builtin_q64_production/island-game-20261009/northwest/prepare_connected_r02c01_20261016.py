"""Prepare r02_c01 guides from explicitly pinned current candidate edge pixels only."""
from pathlib import Path
from types import SimpleNamespace
import argparse,json,hashlib,datetime
from PIL import Image
import prepare_zone_patch as prepare
Z=Path(__file__).resolve().parent
ROOT=Z.parents[3]
EXT=ROOT/"qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/island-west-residences"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {"path":Path(p).as_posix(),"sha256":sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,v):
 with Path(p).open("x",encoding="utf-8") as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write("\n")
p=argparse.ArgumentParser()
p.add_argument("--row",type=int,required=True);p.add_argument("--col",type=int,required=True);p.add_argument("--attempt",default="a01")
for di in ("left","right","top","bottom"):p.add_argument("--"+di)
a=p.parse_args()
split=read(ROOT/"docs/MAP_PARALLEL_SPLIT_20261013.json")
reserved=[t for b in split["batches"] if b["map"]=="island-game-20261009" and b["status"]=="allocated_root_reserved" for t in b["tiles"]]
assert "r02_c01" not in reserved
south=Z/"tiles/r03_c01_candidate-v11_4096.png";southrec=south.with_suffix(".native-repair.json")
assert sha(south)=="0686b42815ff39b6d262675feaa14e74065a4143f85a7f1ebb9d8473ecbe1256"
assert sha(southrec)=="63eb1f535bbd06c842585129a259236e71b9067f24fad7283bd5eedf1407042b"
eastselection=EXT/"selection/r02_c02_selection-v01-20261016.json"
eastrec=EXT/"tiles/r02_c02_candidate-v1_4096.assembly.json"
er=read(eastrec)
assert Path(er["manifest"]["path"]).resolve()==eastselection.resolve() and er["manifest"]["sha256"]==sha(eastselection)
east=Path(er["output"]["path"]);assert sha(east)==er["output"]["sha256"]=="17104bf8b3a3cd2de6597f3e61b5c3647e6c4e942426a1e3a47b759dfc0bfe8a"
sel=read(eastselection)
assert sel["tileId"]=="r02_c02" and sel["uniqueNativeCoreCoverage"]==16
cache=Z/"guides/r02_c01_fixed_neighbor_anchors_20261016.json"
if not cache.exists():
 conflicts=[]
 for sub in ("native","guides","prompts","receipts","tiles"):
  conflicts += [p.as_posix() for p in (Z/sub).glob("r02_c01*") if p.is_file()]
 assert not conflicts,conflicts
 entries=[]
 for side,source,record in (("south",south,southrec),("east",east,eastrec)):
  im=Image.open(source).convert("RGB");assert im.size==(4096,4096)
  for i in range(1,5):
   offset=max(0,min((i-1)*1024-115,2842))
   box=[offset,0,offset+1254,1254] if side=="south" else [0,offset,1254,offset+1254]
   path=Z/f"guides/r02_c01_fixed_{side}_{i:02d}_anchor_20261016.png"
   assert not path.exists();im.crop(box).save(path)
   origin=[0,8192] if side=="south" else [4096,4096]
   entries.append({**pin(path),"nativeSize":[1254,1254],"side":side,"index":i,"coreOffset":(i-1)*1024-offset,"globalBox":[origin[0]+box[0],origin[1]+box[1],origin[0]+box[2],origin[1]+box[3]],"kind":"exact_current_formal_tile_crop_reference_only","derivedFrom":{"image":pin(source),"record":pin(record),"tileCropBoxHalfOpen":box},"resizing":False,"registration":False,"pixelSynthesis":False})
 write(cache,{"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"southImage":pin(south),"southRecord":pin(southrec),"eastImage":pin(east),"eastRecord":pin(eastrec),"eastSelection":pin(eastselection),"eastStatus":sel["status"],"eastFormalAccepted":False,"anchors":entries,"conflictsBeforeCreation":conflicts,"split":pin(ROOT/"docs/MAP_PARALLEL_SPLIT_20261013.json"),"externalDirectoriesReadOnly":True,"policy":"Only actual core115 neighbor edges; never obsolete outside-core halo. Current eastern candidate is not falsely promoted to accepted."})
 data=read(cache)
 state=Z/"connected-coast-current-selection-20261016.json"
 assert not state.exists()
 write(state,{"schemaVersion":1,"owner":"/root/connected_continuation","allocatedBy":"/root explicit task 2026-10-16","tileId":"r02_c01","status":"production_started","anchors":pin(cache),"expectedCores":16,"selectedNative":[],"inflight":[],"internalGeometryClosurePassed":False,"internalClosurePassed":False,"materialStatus":"PENDING","formalAccepted":False})
else:data=read(cache)
assert data["southImage"]==pin(south) and data["eastImage"]==pin(east)
original=prepare.load_neighbor
def load(stem,direction,target,contract):
 if stem not in ("fixed-south-core","fixed-east-core"):return original(stem,direction,target,contract)
 side="south" if stem=="fixed-south-core" else "east"
 index=a.col if side=="south" else a.row
 e=next(x for x in data["anchors"] if x["side"]==side and x["index"]==index)
 assert sha(e["path"])==e["sha256"]
 k=e["coreOffset"];b=target["globalBox"]
 if side=="south":
  crop=[k,0,k+1024,115];dest=[115,1139];tb=[115,1139,1139,1254];gb=[b[0]+115,b[1]+1139,b[0]+1139,b[1]+1254]
 else:
  crop=[0,k,115,k+1024];dest=[1139,115];tb=[1139,115,1254,1139];gb=[b[0]+1139,b[1]+115,b[0]+1254,b[1]+1139]
 return ({**e,"direction":direction,"sourceZone":"northwest" if side=="south" else "island-west-residences","sourceCrop":crop,"destination":dest,"targetLocalBox":tb,"globalOverlapBox":gb,"coordinateEvidence":pin(cache),"resized":False,"sameTile":False,"role":"Explicit current neighbor actual core115 native edge; candidate status preserved","haloPolicy":"Only1024 length actual core edge, no unverified outside-core corners"},Image.open(e["path"]).convert("RGB"))
prepare.load_neighbor=load
if a.row==4:a.bottom="fixed-south-core"
if a.col==4:a.right="fixed-east-core"
r=prepare.prepare(SimpleNamespace(tile_row=2,tile_col=1,subrow=a.row,subcol=a.col,attempt=a.attempt,left=a.left,right=a.right,top=a.top,bottom=a.bottom,output_dir=None))
ip=Path(r["input"]["path"]);rp=Path(r["references"]["path"]);d=read(ip);refs=read(rp)
if len(refs)==5:
 omitted=refs[4];refs=refs[:4]
 d["generationReferenceStrategy"]={"actualSubmittedCount":4,"fullNeighborNotSubmitted":omitted,"reason":"Exact native overlap pixels already present in guide. Omit whole-neighbor view to avoid composition copying; full coordinate evidence retained."}
 d["inputs"]=refs;d["imageGenReferencedImagePaths"]=[x["path"] for x in refs];d["inputCount"]=4
 ip.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 rp.write_text(json.dumps(refs,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"guide":r["guide"]["path"],"input":pin(ip),"references":pin(rp),"inputs":[x["path"] for x in refs],"globalBox":d["globalBox"],"coreBox":d["coreBox"]}))

