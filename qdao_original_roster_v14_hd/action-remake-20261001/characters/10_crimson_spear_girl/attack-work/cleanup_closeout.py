from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl").resolve()
references=set()
for f in [R/"source-selection.json",R/"attack-work/selection.json",R/"run-NE-work/selection.json",R/"run-E-grounding-work/selection.json",R/"attack-W-grounding-work/selection.json"]:
 if f.exists():
  data=json.loads(f.read_text(encoding="utf-8")); references.update(str((R/v).resolve()).lower() for v in data["slots"].values())
m=json.loads((R/"manifest.json").read_text(encoding="utf-8"))
references.update(str((R/x["file"]).resolve()).lower() for x in m["slots"] if x.get("file"))
files=["run-NE-work/run-NE-13-v4.png","attack-work/attack-E-03-ground-v1.png","attack-work/attack-E-03-ground-v2.png","attack-work/attack-W-03-ground-v1.png","attack-work/attack-E-03-feet-v2.png","attack-work/attack-W-03.png","attack-work/attack-W-09.png","attack-work/attack-E-01-v2.png","attack-work/attack-E-12-v4.png","attack-work/attack-W-06-v2.png"]
log=[]
for rel in files:
 p=(R/rel).resolve()
 assert p.is_relative_to(R) and p.suffix==".png"
 if not p.exists():continue
 if str(p).lower() in references:
  log.append({"file":rel,"status":"kept-current-reference"});continue
 recp=Path(str(p)+".generation.json")
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 if recp.exists():
  rec=json.loads(recp.read_text(encoding="utf-8"));rec.update(status="superseded-or-rejected-image-deleted-text-preserved",deletedAtUtc=datetime.now(timezone.utc).isoformat(),deletionReason="Replacement selected and old PNG absent from active local/root selections and current manifest primary slots. All prompt/receipt/model/source text retained.");recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 p.unlink();log.append({"file":rel,"sha256":sha,"status":"deleted-png-text-preserved"})
out={"checkedAt":datetime.now(timezone.utc).isoformat(),"entries":log}
(R/"attack-work/cleanup-closeout-20261004.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=True))

