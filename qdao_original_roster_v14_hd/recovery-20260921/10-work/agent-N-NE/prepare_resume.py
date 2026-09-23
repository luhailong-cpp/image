from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, argparse
HERE=Path(__file__).resolve().parent
RECOVERY=HERE.parents[1]
ROOT=HERE.parents[3]
p=argparse.ArgumentParser();p.add_argument('spec');a=p.parse_args()
spec=json.loads(Path(a.spec).read_text(encoding='utf-8-sig'))
out=RECOVERY/'10-generation'/spec['attempt'];out.mkdir(exist_ok=False)
refs=[RECOVERY/'10-work/references/identity-inspection-1024.png',ROOT/'designs/jubaozhai-ui/02-characters.png']+[RECOVERY/'10-generation'/s/'raw.png' for s in spec.get('refs',[])]
roles=['authoritative-original-identity','confirmed-main-style']+spec.get('roles', ['same-direction-anatomy-camera-reference']*len(spec.get('refs',[])))
prompt=spec['prompt'];(out/'prompt.txt').write_bytes(prompt.encode('utf-8'))
request={'status':'prepared_for_submission','character':'10_crimson_spear_girl','slot':spec['slot'],'startedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen__imagegen','actual_request':{'prompt':prompt,'referenced_image_paths':[r.as_posix() for r in refs]},'submittedParameters':{'model':None,'quality':None},'configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8')),'referenceRoles':roles,'reference_bindings_at_start':[{'path':r.as_posix(),'sha256':hashlib.sha256(r.read_bytes()).hexdigest(),'purpose':role} for r,role in zip(refs,roles)]}
(out/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive':out.as_posix(),'actual_request':request['actual_request']},ensure_ascii=False))
