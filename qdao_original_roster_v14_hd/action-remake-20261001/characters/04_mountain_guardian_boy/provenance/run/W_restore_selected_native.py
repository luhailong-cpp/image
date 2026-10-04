from pathlib import Path
import json,hashlib,re,shutil
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2].resolve()
NOW=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
formal=list((ROOT/"frames"/"hit").glob("*/*.generation.json"))+list((ROOT/"frames"/"run"/"W").glob("*.generation.json"))+list((ROOT/"frames"/"run"/"NW").glob("*.generation.json"))
restored=[];errors=[]
for mp in formal:
 j=read(mp); ns=j["nativeSource"];dest=(ROOT/ns["path"]).resolve()
 assert dest.parent in [ROOT/"provenance"/"hit",ROOT/"provenance"/"run"]
 paths=[]
 host=j.get("evidence",{}).get("originalHostSource")
 if host:paths.append(Path(host))
 rec=j.get("evidence",{}).get("receipt")
 if isinstance(rec,dict):rec=rec["path"]
 if rec:
  recp=Path(rec)
  if not recp.is_absolute():recp=ROOT/recp
  data=read(recp)
  def walk(v):
   if isinstance(v,str):
    for m in re.findall(r"(?:[A-Za-z]:[/\\][^\r\n]+?\.png)",v):
     # output_hint may contain first directory followed by as; use path beginning at last drive
     mm=re.findall(r"[A-Za-z]:[/\\]",m)
     if len(mm)>1:m=m[m.rfind(mm[-1]):]
     paths.append(Path(m))
   elif isinstance(v,dict):
    for vv in v.values():walk(vv)
   elif isinstance(v,list):
    for vv in v:walk(vv)
  walk(data)
 found=None
 for p in paths:
  if p.is_file() and sha(p)==ns["sha256"]:found=p;break
 if not found:
  errors.append({"frame":j["file"],"source":ns["path"],"hostCandidates":[str(p) for p in paths]});continue
 shutil.copyfile(found,dest)
 assert sha(dest)==ns["sha256"]
 restored.append({"path":str(dest.relative_to(ROOT)),"sha256":sha(dest),"originalHostSource":str(found),"restoredAt":NOW,"reason":"父线程动态终验仍需该帧唯一原生在制来源；仅恢复当前44张选中源，拒稿不恢复。"})
lookup={str((ROOT/x["path"]).resolve()).casefold():x for x in restored}
def walk_flags(obj):
 changed=False
 if isinstance(obj,dict):
  val=obj.get("file") or obj.get("path")
  if val:
   p=Path(val)
   if not p.is_absolute():p=ROOT/p
   k=str(p.resolve()).casefold()
   if k in lookup:
    obj["fileRetained"]=True;obj["restoredAt"]=NOW;obj["retentionNote"]="当前选中帧唯一原生在制来源，保留至父线程动态终验；前次删除与恢复记录均保留。"
    if "artifactState" in obj:obj["artifactState"]="selected_native_pending_dynamic_review"
    changed=True
  for v in list(obj.values()):
   if isinstance(v,(dict,list)):changed=walk_flags(v) or changed
 elif isinstance(obj,list):
  for v in obj:changed=walk_flags(v) or changed
 return changed
records=list((ROOT/"provenance"/"hit").glob("*.generation.json"))+[p for p in (ROOT/"provenance"/"run").glob("*.generation.json") if p.name.startswith(("W_","NW_"))]+formal
for p in records:
 j=read(p)
 if walk_flags(j):save(p,j)
save(ROOT/"provenance"/"run"/"W_NW_restore_selected_native_20261003.json",{"createdAt":NOW,"restored":restored,"errors":errors,"cleanupHistory":"先前89张像素清理后父线程通知动态仍需选中源，现仅恢复选中源。拒稿与中间图保持删除。宿主原图未改动。"})
print(json.dumps({"restored":len(restored),"errors":errors},ensure_ascii=False))

