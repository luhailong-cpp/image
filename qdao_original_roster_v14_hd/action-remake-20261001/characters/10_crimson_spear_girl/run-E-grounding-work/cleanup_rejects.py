from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parent; R=B.parent
active=set()
for sf in [B/"selection.json",R/"source-selection.json"]:
 if sf.exists():
  raw=json.loads(sf.read_text(encoding="utf-8-sig"))
  for value in raw.get("slots",{}).values():
   if isinstance(value,str): active.add((R/value).resolve())
rejects={"run-E-07-v2.png":"wrong thigh occlusion","run-E-08-v2.png":"wrong thigh occlusion","run-E-10-v2.png":"low hanging forward boot, inadequate flight","run-E-10-v3.png":"leg layer swapped incorrectly","run-E-12-v3.png":"wrong thigh occlusion","run-E-13-v2.png":"repeated leading leg","run-E-14-v2.png":"upperbody scale/position mismatch","run-E-16-v3.png":"1388x1133 landscape wrong canvas"}
log=[]
rejects.update({"run-E-06-v2.png":"superseded phase14: upperbody too small, current14-v3", "run-E-06-v3.png":"superseded phase06: upperbody too small, current06-v4", "run-E-16-v2.png":"superseded by square16-v4 with improved upperbody continuity"})
for name,reason in rejects.items():
 p=(B/name).resolve()
 assert p.parent==B
 if p in active: log.append({"file":name,"status":"retained-active-selection","reason":reason});continue
 record=Path(str(p)+".generation.json")
 if p.exists() or record.exists():
  sha=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else json.loads(record.read_text(encoding="utf-8"))["sha256"]
  if p.exists(): p.unlink()
  if record.exists():
   x=json.loads(record.read_text(encoding="utf-8"));x["imageRetained"]=False;x["status"]="rejected-source-image-removed";x["rejectionReason"]=reason;x["deletedAt"]=datetime.now(timezone.utc).isoformat();record.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
  log.append({"file":name,"sha256":sha,"status":"deleted-reject-image-text-kept","reason":reason})
for rec in B.glob("*.png.generation.json"):
 x=json.loads(rec.read_text(encoding="utf-8"))
 for ref in x.get("references",[]): ref["imageRetained"]=Path(ref["file"]).exists()
 rec.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"cleanup-rejects-20261003.json").write_text(json.dumps({"at":datetime.now(timezone.utc).isoformat(),"activeSelectionFiles":["selection.json","../source-selection.json"],"images":log},ensure_ascii=False,indent=2),encoding="utf-8")
selection=json.loads((B/"selection.json").read_text())["slots"]
der={"file":"contact-current.jpg","operation":"contact sheet: each selected full1254canvas scaled uniformly to320, arranged4x4 withlabels and virtualground guide; no sprite source modified","derivedFrom":[{"slot":s,"file":p,"sha256":hashlib.sha256((R/p).read_bytes()).hexdigest(),"generationRecord":p+".generation.json"} for s,p in selection.items()],"actualModel":None,"actualQuality":None,"notNewGeneration":True}
(B/"contact-current.jpg.generation.json").write_text(json.dumps(der,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(log,ensure_ascii=False))

