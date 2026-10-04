from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent
B=Path(__file__).resolve().parent
allowed=[
"run-NE-09.png","run-NE-11.png","run-NE-13.png","run-NE-13-v3.png","run-NE-13-v4.png","run-NE-14.png","run-NE-14-v2.png","run-NE-14-v3.png","run-NE-16.png"
]
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
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 record=Path(str(p)+".generation.json")
 if record.exists():
  r=json.loads(record.read_text(encoding="utf-8"));r.update(status="rejected-image-deleted-text-record-preserved",deletedAtUtc=datetime.now(timezone.utc).isoformat(),deletionReason="Known superseded wrong support side, ground height, cropped weapon, or airborne-leg failure; absent from current selection/root manifest.")
  record.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
 p.unlink();log.append({"file":fn,"sha256":sha,"action":"deleted-reject-png-text-preserved"})
(B/"cleanup-rejects-20261004.json").write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(log))

