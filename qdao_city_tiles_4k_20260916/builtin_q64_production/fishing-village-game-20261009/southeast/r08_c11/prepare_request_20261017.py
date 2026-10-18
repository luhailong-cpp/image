from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
T=Path(__file__).resolve().parent
R=T.parents[4]
A=R/'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
pid,version,guide,neighbor=sys.argv[1:5]
prompt=(T/f'{pid}-{version}.prompt.txt').read_text(encoding='utf-8-sig')
rules=(R/'AGENTS.md').read_text(encoding='utf-8-sig')
split=read(R/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert '2.0' in rules
assert not any(b.get('status')=='allocated_root_reserved' and b.get('map')=='fishing-village-game-20261009' and T.name in b['tiles'] for b in split['batches'])
refs=[str(T/'layout-only'/guide),str(A/'donghai-natural-stone-clear-routes-v10.png'),str(A/'donghai-natural-stone-detail-v1.png'),str(A/'user-references-20261009/mail-daoist-style.jpg'),neighbor]
roles=['exact target framing and actual selected-core constraint, guide only','approved full map layout only','approved material/daylight, not coordinate crop','approved Daoist painterly style only, exclude UI/night/text','actual adjacent selected native reference, do not copy its unselected halo as boundary']
request={'tool':'image_gen__imagegen','route':'builtin','prompt':prompt,'referenced_image_paths':refs,'referenceRoles':{str(i+1):r for i,r in enumerate(roles)},'referenceHashes':{str(i+1):sha(Path(p)) for i,p in enumerate(refs)},'transparent_background':False,'preparedAt':datetime.now(timezone.utc).isoformat(),'model':None,'quality':None,'actualModel':None,'actualQuality':None,'rulesRead':{'AGENTS.md':sha(R/'AGENTS.md'),'parallelSplit':sha(R/'docs/MAP_PARALLEL_SPLIT_20261013.json')}}
write(T/f'{pid}-{version}.request.json',request)
print(json.dumps(request,ensure_ascii=False))
