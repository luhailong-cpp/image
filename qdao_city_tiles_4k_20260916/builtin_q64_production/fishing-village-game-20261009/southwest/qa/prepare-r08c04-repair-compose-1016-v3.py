import json,hashlib
from pathlib import Path
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
tr=q/'repair-r08c04-1016-v2-trace.json';t=json.loads(tr.read_text());a=q/'repair-r08c04-1016-v2-assembly-adapter.json'
assert not a.exists();a.write_text(json.dumps({'context':t['context'],'output':t['candidate'],'provenance':ref(tr),'purpose':'schema adapter only, exact existing context/candidate, no new art'},indent=2),encoding='utf-8')
stem='r08_c04_repair_b_1016_v2';r=json.loads((z/'native'/(stem+'.request.json')).read_text(encoding='utf-8-sig'))
m={'schemaVersion':1,'outputPrefix':'repair-r08c04-1016-v3','baseAssembly':ref(a),'expectedBaseCandidateSha256':t['candidate']['sha256'],'repairs':[{'id':'b2','tileContextBox':r['coordinates']['tileContextBox'],'repairBounds':[180,420,720,880],'margin':25,'source':ref(q/(stem+'-source-1254.png')),'repair':ref(z/'native'/(stem+'.png')),'generationRecord':ref(z/'native'/(stem+'.png.generation.json'))}]}
p=q/'repair-r08c04-1016-v3.manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2),encoding='utf-8')

