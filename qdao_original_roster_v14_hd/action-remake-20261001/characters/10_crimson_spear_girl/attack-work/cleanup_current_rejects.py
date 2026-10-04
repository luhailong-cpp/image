from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
ROOT=B.parent
allowed=["attack-E-01-v2.png","attack-E-02-v2.png","attack-E-03-feet-v1.png","attack-E-03-v2.png","attack-E-04.png","attack-E-05.png","attack-E-06-v2.png","attack-E-06-v3.png","attack-E-06-v4.png","attack-E-06-v5.png","attack-E-07-v2.png","attack-E-08.png","attack-E-09.png","attack-E-10.png","attack-E-11.png","attack-E-11-feet-v1.png","attack-E-12-v4.png","attack-W-02.png","attack-W-02-feet-v1.png","attack-W-06-v2.png","attack-W-06-v3.png"]
own=json.loads((B/"selection.json").read_text(encoding="utf-8"))["slots"]
rsel=json.loads((ROOT/"source-selection.json").read_text(encoding="utf-8"))["slots"]
manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
protected={str((ROOT/v).resolve()).lower() for v in list(own.values())+list(rsel.values())+[r["file"] for r in manifest["slots"] if r.get("file")]}
log=[]
for fn in allowed:
 p=(B/fn).resolve()
 assert p.parent==B and p.suffix==".png"
 if not p.exists():continue
 if str(p).lower() in protected:log.append({"file":fn,"action":"kept-current-reference"});continue
 sha=hashlib.sha256(p.read_bytes()).hexdigest();recp=Path(str(p)+".generation.json")
 if recp.exists():
  rec=json.loads(recp.read_text(encoding="utf-8"));rec.update(status="superseded-or-rejected-image-deleted-text-preserved",deletedAtUtc=datetime.now(timezone.utc).isoformat(),deletionReason="Explicit local selected replacement exists and old PNG absent from local/root selection and current root manifest. Text model/quality/source record retained.");recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 p.unlink();log.append({"file":fn,"sha256":sha,"action":"deleted-png-text-preserved"})
(B/"cleanup-rejects-20261004.json").write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(log))

