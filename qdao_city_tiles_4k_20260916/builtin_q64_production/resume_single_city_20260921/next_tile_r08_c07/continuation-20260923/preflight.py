from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys, os
TILE=Path(__file__).resolve().parents[1]
REPO=TILE.parents[3]
ident=sys.argv[1]
request=TILE/'requests'/f'{ident}.request.json'
raw=request.read_bytes()
obj=json.loads(raw.decode('utf-8-sig'))
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out=Path(__file__).resolve().parent/(ident+'-'+stamp)
out.mkdir(exist_ok=False)
(out/'original-request.json').write_bytes(raw)
aliases=[]
for i,p in enumerate(obj['referenced_image_paths']):
    if not Path(p).exists() and Path(p).name=='guild-overview.png':
        new=REPO/'designs/gameplay-ui/04-guild.png'
        digest=hashlib.sha256(new.read_bytes()).hexdigest()
        assert digest=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
        aliases.append({'oldPath':p,'actualInputPath':str(new),'sha256':digest,'reason':'Concurrent deduplication; current designs index names byte-identical canonical asset'})
        obj['referenced_image_paths'][i]=str(new)
raw=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
(out/'request.json').write_bytes(raw)
config=(REPO/'config/image-generation.json').read_bytes()
(out/'config-snapshot.json').write_bytes(config)
refs=[{'path':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in obj['referenced_image_paths']]
(out/'preflight.json').write_text(json.dumps({'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'requestSha256':hashlib.sha256(raw).hexdigest(),'configSha256':hashlib.sha256(config).hexdigest(),'references':refs,'inputAliases':aliases,'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'formalAccepted':False},indent=2),encoding='utf-8')
plan_path=TILE/'plan.json'
before=plan_path.read_bytes()
plan=json.loads(before.decode('utf-8-sig'))
patch=next(p for p in plan['patches'] if p['id']==ident)
assert patch['status']=='prepared'
patch['submittedImages']=obj['referenced_image_paths']
patch['requestFile']=str(out/'request.json')
patch['preflight']=str(out/'preflight.json')
(out/'plan.before.json').write_bytes(before)
data=(json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
tmp=out/'plan.new.json';tmp.write_bytes(data)
assert plan_path.read_bytes()==before, 'Concurrent plan change'
os.replace(tmp,plan_path)
print(json.dumps({'directory':str(out),'request':obj}))
