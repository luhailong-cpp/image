from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
B=Path(__file__).resolve().parents[2]
tile,patch,attempt,base_attempt,prefix,*extra=sys.argv[1:]
allowed={f'r{r:02d}_c{c:02d}' for r in range(13,17) for c in range(1,5)}
assert tile in allowed
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
allocation=B/'pipeline-tools/internal-lower-left-allocation-20261016-v01.json'
assert sha(allocation)=='0109ebd54188f4f41fbba75d5ee18aeaf5402f53e5519fbb7f563cd755a4aad6'
T=B/tile;base=T/'pipeline/prompts'/f'{patch}.{base_attempt}.request.json';r=json.loads(base.read_text(encoding='utf-8-sig'))
request=T/'pipeline/prompts'/f'{patch}.{attempt}.request.json';prompt=request.with_name(f'{patch}.{attempt}.prompt.txt')
assert not request.exists() and not prompt.exists()
r['prompt']=prefix+'\n\n'+r['prompt'][r['prompt'].index('Use case:'):]
prompt.write_text(r['prompt'],encoding='utf-8')
r.update(promptFile=str(prompt),promptSha256=sha(prompt),preparedAtUtc=datetime.now(timezone.utc).isoformat(),contentBaseRequest={'file':str(base),'sha256':sha(base)},allocationEvidence={'file':str(allocation),'sha256':sha(allocation)})
r['references']=r['references'][:4]
if extra and extra[0]!='-':
 p=Path(extra[0]);r['references'][0]={'file':str(p),'sha256':sha(p),'role':'edit target: same-canvas native or continuity guidance; actually viewed before call'}
if len(extra)>1 and extra[1]!='-':
 p=Path(extra[1]);r['references'].append({'file':str(p),'sha256':sha(p),'role':extra[2] if len(extra)>2 else 'supporting geometry/style only, never final artwork'})
r['referenced_image_paths']=[x['file'] for x in r['references']]
r['actualModel']=None;r['actualQuality']=None
request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(request)
