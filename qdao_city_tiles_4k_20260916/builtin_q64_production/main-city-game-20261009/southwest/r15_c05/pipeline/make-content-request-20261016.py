from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
T=Path(__file__).resolve().parents[1]
patch,attempt,base_attempt,prefix,*extra=sys.argv[1:]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=T/'pipeline/prompts'/f'{patch}.{base_attempt}.request.json'
r=read(base)
prompt=T/'pipeline/prompts'/f'{patch}.{attempt}.prompt.txt'
request=T/'pipeline/prompts'/f'{patch}.{attempt}.request.json'
assert not prompt.exists() and not request.exists()
r['prompt']=prefix+'\n\n'+r['prompt'][r['prompt'].index('Use case:'):]
prompt.write_text(r['prompt'],encoding='utf-8')
r.update(promptFile=str(prompt),promptSha256=sha(prompt),preparedAtUtc=datetime.now(timezone.utc).isoformat(),contentBaseRequest={'file':str(base),'sha256':sha(base)})
r['references']=r['references'][:4]
if extra:
 p=Path(extra[0]);r['references'].append({'file':str(p),'sha256':sha(p),'role':'approved wider wall geometry only, nearest enlarged QA layout context, not game art'})
r['referenced_image_paths']=[x['file'] for x in r['references']]
r['actualModel']=None;r['actualQuality']=None
request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(request)
