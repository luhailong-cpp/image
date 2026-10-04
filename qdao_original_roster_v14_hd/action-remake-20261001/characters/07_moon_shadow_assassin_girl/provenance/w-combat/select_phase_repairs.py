import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl").resolve()
out=[]
for action,num in [("attack",11),("cast",2),("cast",11)]:
 old=ROOT/"staging"/action/"W"/f"{num:02d}.png"
 new=ROOT/"staging"/action/"W"/f"{num:02d}-v2.png"
 oldrec=Path(str(old)+".generation.json")
 newrec=Path(str(new)+".generation.json")
 for p in [old,new,oldrec,newrec]:
  assert p.resolve().is_relative_to(ROOT)
  assert p.exists(),p
 rec1=json.loads(oldrec.read_text(encoding="utf-8"))
 rec2=json.loads(newrec.read_text(encoding="utf-8"))
 assert hashlib.sha256(new.read_bytes()).hexdigest()==rec2["sha256"]
 rec1["retentionStatus"]="superseded_image_removed_after_v2_verified"
 rec1["replacedBySHA256"]=rec2["sha256"]
 history=ROOT/"provenance"/"w-combat"/f"{action}-W-{num:02d}.superseded-v1.generation.json"
 history.write_text(json.dumps(rec1,ensure_ascii=False,indent=2),encoding="utf-8")
 new.replace(old)
 rec2["file"]=str(old)
 rec2["originalStagingName"]=str(new)
 rec2["selectedFor"]="phase transition repair"
 rec2["supersedes"]={"sha256":rec1["sha256"],"generationRecord":str(history)}
 oldrec.write_text(json.dumps(rec2,ensure_ascii=False,indent=2),encoding="utf-8")
 newrec.unlink()
 out.append({"file":str(old.relative_to(ROOT)),"sha256":rec2["sha256"],"removedImageSHA256":rec1["sha256"],"historicalRecord":str(history.relative_to(ROOT))})
(ROOT/"provenance"/"w-combat"/"phase-repair-selection.json").write_text(json.dumps({"selectedAt":datetime.now(timezone.utc).isoformat(),"userTimezone":"America/New_York","files":out},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=False,indent=2))

