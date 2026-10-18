import json,hashlib,subprocess,sys
from pathlib import Path
Z=Path(__file__).resolve().parent.parent; Q=Z/'qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
jobs=json.loads((Q/'r14c06-c07-water-repair-jobs-v1.json').read_text())
m={'outputPrefix':'pair-r14c06-r14c07-v2','basePairTrace':ref(Q/'pair-r14c06-r14c07-v1-trace.json'),'repairs':[]}
for j in jobs:
 p=Z/'native'/f"{j['stem']}.png";g=Path(str(p)+'.generation.json')
 assert p.is_file() and g.is_file(),f"Native repair not finished: {j['id']}"
 d=json.loads(g.read_text(encoding='utf-8-sig'));assert d['sha256']==sha(p)
 m['repairs'].append({k:j[k] for k in ['id','contextBox','repairBounds','margin','source']}|{'repair':ref(p),'generationRecord':ref(g)})
p=Q/'pair-r14c06-r14c07-v2.manifest.json';assert not p.exists()
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,'-B',str(Q/'native-pair-layered-repair-compose.py'),'--manifest',str(p)],check=True)

