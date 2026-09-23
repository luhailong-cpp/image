from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
P=Path(__file__).resolve().parent.parent
ident=sys.argv[1]
assert ident in ['r03_c04.v2','r04_c01.v2','r04_c02.v2','r04_c03.v2','r04_c04.v2']
sha=lambda data:hashlib.sha256(data).hexdigest()
planbytes=(P/'plan.json').read_bytes();plan=json.loads(planbytes)
patch=next(x for x in plan['patches'] if x['id']==ident.split('.')[0])
requestpath=Path(patch['request']);requestbytes=requestpath.read_bytes();request=json.loads(requestbytes)
assert requestpath.name==ident+'.request.json'
assert not (P/patch['outputFile']).exists()
assert not (P/'requests'/f'{ident}.receipt.json').exists()
original_request_bytes=requestbytes
mapping=[]
for index, path in enumerate(request['referenced_image_paths']):
    if not Path(path).exists():
        canonical=P.parents[3]/'designs/gameplay-ui/04-guild.png'
        assert path.endswith('designs\\guild-ui-v2\\source\\guild-overview.png')
        assert sha(canonical.read_bytes())=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
        mapping.append({'historicalPath':path,'actualSubmittedPath':str(canonical),'sha256':sha(canonical.read_bytes()),'meaning':'Byte-identical confirmed design under retained canonical path; historical duplicate was removed during this run'})
        request['referenced_image_paths'][index]=str(canonical)
requestbytes=(json.dumps(request,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
refs=[{'path':p,'sha256':sha(Path(p).read_bytes())} for p in request['referenced_image_paths']]
root=P/'continuation-20260923'/('preflight-'+ident+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
root.mkdir(exist_ok=False)
(root/'request.json').write_bytes(requestbytes)
(root/'original-request.json').write_bytes(original_request_bytes)
(root/'plan.json').write_bytes(planbytes)
configpath=P.parents[3]/'config/image-generation.json'
configbytes=configpath.read_bytes()
(root/'config.json').write_bytes(configbytes)
metadata={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'id':ident,'originalRequestPath':str(requestpath),'originalRequestSha256':sha(original_request_bytes),'requestSha256':sha(requestbytes),'requestSnapshot':str(root/'request.json'),'references':refs,'referencePathMapping':mapping,'configPath':str(configpath),'configSha256':sha(configbytes),'configSnapshot':json.loads(configbytes),'planSha256':sha(planbytes),'actualModel':None,'actualQuality':None,'generatedAt':None,'submittedModel':None,'submittedQuality':None,'route':'builtin_image_gen','responseExpected':'undisclosed exact backend model and quality; save real tool result'}
(root/'preflight.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preflight':str(root/'preflight.json'),'request':request},ensure_ascii=False))
