from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];P=ROOT/"provenance"/"hit"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
obsolete=[P/"W_frame_03_20261002_attempt01.native.png",P/"W_frame_01_20261002_attempt01.native.png",P/"E_frame_04_20261002_attempt01.native.png",P/"E_frame_04_20261002_attempt02.native.png"]
assert len(list((ROOT/"frames"/"hit").glob("*/*.png")))==12
deleted=[]
for p in obsolete:
 p=p.resolve();assert p.is_relative_to(P.resolve())
 if p.exists():deleted.append({"path":str(p),"sha256":sha(p),"reason":"已被同槽修正成品替换；逐图文字来源保留"})
obsolete_set={str(p.resolve()).casefold() for p in obsolete}
for p in list(P.glob("*.generation.json"))+list((ROOT/"frames"/"hit").glob("*/*.generation.json")):
 r=read(p);changed=False
 original_file=r.get("file")
 if original_file:
  target=Path(original_file)
  if not target.is_absolute():target=ROOT/target
  if str(target.resolve()).casefold() in obsolete_set:r["fileRetained"]=False;r["artifactState"]="rejected_superseded_pixels_deleted";changed=True
 for ref in r.get("references",[]):
  if str(Path(ref["path"]).resolve()).casefold() in obsolete_set:
   ref["fileRetained"]=False;ref["readableEvidencePath"]=None;ref["retentionNote"]="被修正版本替换，像素删除；原始SHA及提交文字保留。";changed=True
 if changed:save(p,r)
for item in deleted:Path(item["path"]).unlink()
save(P/"cleanup_hit_selected12.json",{"updatedAt":datetime.now(timezone.utc).isoformat(),"selectedFrames":12,"deleted":deleted,"retainedNativeReason":"当前12帧待父线程动态终验，保留每帧唯一原生在制来源；最终清理由父线程合并验收后执行。"})
print(json.dumps({"deletedRejectedImages":len(deleted),"selectedFrames":12},ensure_ascii=False))

