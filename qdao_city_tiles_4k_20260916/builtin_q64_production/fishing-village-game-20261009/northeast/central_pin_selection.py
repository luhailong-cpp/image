import json,hashlib,sys
from pathlib import Path
Z=Path(__file__).resolve().parent
tile=sys.argv[1]
version=sys.argv[2] if len(sys.argv)>2 else "central-v1"
w=json.loads((Z/"records"/f"{tile}.working-selection.json").read_text())
assert set(w)=={f"{tile}_p{r}{c}" for r in range(1,5) for c in range(1,5)}
patches={}
for p,name in sorted(w.items()):
 f=Z/"native"/name
 h=hashlib.sha256(f.read_bytes()).hexdigest()
 g=json.loads(Path(str(f)+".generation.json").read_text())
 assert g["sha256"]==h
 patches[p]={"path":"native/"+name,"sha256":h}
out=Z/"records"/f"{tile}.selection-{version}.json"
assert not out.exists()
out.write_text(json.dumps({"schemaVersion":1,"tile":tile,"version":version,"reviewer":"/root/central_resume","status":"candidate_pending_full_internal_and_external_QA","formalAccepted":False,"patches":patches},indent=2)+"\n")
print(out)

