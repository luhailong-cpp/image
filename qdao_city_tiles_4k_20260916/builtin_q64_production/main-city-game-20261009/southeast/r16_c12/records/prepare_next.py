import json,hashlib,sys,subprocess
from pathlib import Path
t=Path(__file__).resolve().parents[1]
z=t.parent
root=Path(r"D:/work/image")
for rel in ("AGENTS.md","docs/MAP_PARALLEL_SPLIT_20261013.json"):
 p=root/rel
 raw=p.read_bytes()
 text=raw.decode("utf-8-sig")
 digest=hashlib.sha256(raw).hexdigest()
 print(json.dumps({"reread":str(p),"sha256":digest,"characters":len(text)},ensure_ascii=False),file=sys.stderr)
 if rel.endswith(".json"):
  split=json.loads(text)
  assert not any(t.name in b["tiles"] for b in split["batches"] if b["status"]=="allocated_root_reserved")
p=subprocess.run([sys.executable,"-X","utf8",str(z/"production_workflow_west_extension_20261016_v2.py"),"prepare",t.name,*sys.argv[1:]],capture_output=True,text=True,encoding="utf-8")
if p.returncode:
 print(p.stdout,p.stderr);sys.exit(p.returncode)
d=json.loads(p.stdout)
req=json.loads(Path(d["request"]).read_text(encoding="utf-8"))
print(json.dumps({"version":d["version"],"request":req,"anchors":[{k:a[k] for k in ("direction","sha256","sourceCrop","target")} for a in d["anchors"]]},ensure_ascii=False))
