from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
root=Path(__file__).resolve().parents[2]
prov=root/"provenance"/"hit"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def save(p,obj): Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
final=root/"frames"/"hit"/"E"/"frame_03.png"
assert sha(final)=="272204657c7439d886b5b14ae0dab0e3d1b19738042e42c64414fdfaf0a57e0a"
with Image.open(final) as im:
 assert im.size==(1024,1024) and im.mode=="RGBA"
obsolete=[prov/"E_frame_03_20261002_attempt03.source.png",prov/"E_03_native_feda0582e05c.png",prov/"retired_E_frame_03_attempt04.png"]
deleted=[]
for p in obsolete:
 p=p.resolve()
 assert p.is_relative_to(prov.resolve()) and p.suffix==".png"
 if p.exists():
  deleted.append({"path":str(p),"sha256":sha(p),"reason":"后续attempt05关键帧已落盘并核实；保留旧文字来源"})
for name in ["E_frame_01_20261002_attempt01","E_frame_02_20261002_attempt01"]:
 p=prov/(name+".failure.json")
 record=read(p)
 record["references"]=[]
 for i,value in enumerate(record["submittedParameters"]["referenced_image_paths"],1):
  with Image.open(value) as im: dims=list(im.size)
  record["references"].append({"inputIndex":i,"path":value,"sha256":sha(value),"pixelDimensions":dims,"viewed":True,"passedToTool":True})
 save(p,record)
old3=prov/"E_frame_03_20261002_attempt03.generation.json"
r=read(old3);r["status"]="rejected_superseded_pixels_deleted";r["fileRetained"]=False;r["supersededBy"]="frames/hit/E/frame_03.png";save(old3,r)
old4=prov/"retired_E_frame_03_attempt04.generation.json"
r=read(old4);r["artifactState"]="superseded_pixels_deleted";r["fileRetained"]=False;r["historicalFile"]=r["file"];r["nativeSource"]["retained"]=False;r["supersededBy"]="frames/hit/E/frame_03.png";save(old4,r)
subpath=prov/"E_frame_03_20261002_attempt05.submission.json"
sub=read(subpath)
sub["editTarget"]["generationRecord"]=str(old4)
sub["editTarget"]["fileRetained"]=False
sub["editTarget"]["retentionNote"]="原始工具提交路径保留；该历史像素已被新关键帧替换并删除。上列SHA属于编辑前输入，当前同路径像素不同。"
save(subpath,sub)
recpath=final.with_suffix(".generation.json")
r=read(recpath)
r["references"][0]["readableEvidencePath"]=None
r["references"][0]["fileRetained"]=False
r["references"][0]["historicalGenerationRecord"]=str(old4)
r["references"][0]["retentionNote"]="已替换旧编辑目标，仅保留来源文字及SHA。"
r["evidence"]["submission"]["sha256"]=sha(subpath)
r["review"]["notes"]=["侧脸单眼、右手持杖、左盾远侧、屈膝受击姿态与两靴清楚，单帧视觉通过。","跨帧比例/锚点与动态仍待验；小玉环孔alpha=1残留待出口终验。"]
save(recpath,r)
cleanup={"updatedAt":datetime.now(timezone.utc).isoformat(),"finalVerified":{"path":str(final),"sha256":sha(final)},"deleted":deleted,"retainedCurrentNative":str(prov/"E_frame_03_20261002_attempt05.native.png"),"reason":"当前唯一采用关键帧仍需帧组/透明终验，保留其唯一原生在制来源；拒稿与被替换图删除。"}
save(prov/"cleanup_after_attempt05.json",cleanup)
for item in deleted: Path(item["path"]).unlink()
print(json.dumps({"deleted":len(deleted),"finalSha256":sha(final),"failedRequestsDocumented":2},ensure_ascii=False))

