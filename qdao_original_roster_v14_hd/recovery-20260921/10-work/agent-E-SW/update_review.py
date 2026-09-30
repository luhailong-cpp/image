from pathlib import Path
import json, sys
from datetime import datetime,timezone
base=Path(__file__).resolve().parent
gen=base.parents[1]/'10-generation'
attempt=sys.argv[1]
obs=json.loads((gen/attempt/'review-observation.json').read_text(encoding='utf-8'))
sha=json.loads((gen/attempt/'raw.png.generation.json').read_text(encoding='utf-8'))['sha256']
sel=json.loads((base/'selection.json').read_text(encoding='utf-8'))
reviewpath=base/'review-20260928.json'
rev=json.loads((reviewpath if reviewpath.exists() else base/'review-20260923.json').read_text(encoding='utf-8'))
if obs['decision']=='provisional_candidate':
    sel[obs['slot']]={'archive':attempt,'review':'provisional: '+obs['observation']+' Final30ms loop, edges, scale and anchor pending.'}
    rev['selected']=[x for x in rev['selected'] if x['slot']!=obs['slot']]+[{**obs,'archive':attempt,'sha256':sha}]
else:
    rev['rejected'].append({**obs,'archive':attempt,'sha256':sha})
rev['updatedAt']=datetime.now(timezone.utc).isoformat()
rev['missing']=[d+f'{n:02}' for d in ['E','SW'] for n in range(1,17) if d+f'{n:02}' not in sel]
for p,data in [(base/'selection.json',sel),(reviewpath,rev)]: p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected':len(sel),'missing':rev['missing']},ensure_ascii=False))
