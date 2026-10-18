import json,hashlib
from pathlib import Path
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
a=q/'full-tile-r08_c04-1016-v1-assembly.json';ar=json.loads(a.read_text())
m={'schemaVersion':1,'outputPrefix':'repair-r08c04-1016-v2','baseAssembly':ref(a),'expectedBaseCandidateSha256':ar['output']['sha256'],'repairs':[]}
for key in 'abc':
 stem='r08_c04_repair_'+key+'_1016_v1';r=json.loads((z/'native'/(stem+'.request.json')).read_text(encoding='utf-8-sig'))
 m['repairs'].append({'id':key,'tileContextBox':r['coordinates']['tileContextBox'],'repairBounds':r['coordinates']['repairBounds'],'margin':25,'source':ref(q/(stem+'-source-1254.png')),'repair':ref(z/'native'/(stem+'.png')),'generationRecord':ref(z/'native'/(stem+'.png.generation.json'))})
p=q/'repair-r08c04-1016-v2.manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2),encoding='utf-8')

