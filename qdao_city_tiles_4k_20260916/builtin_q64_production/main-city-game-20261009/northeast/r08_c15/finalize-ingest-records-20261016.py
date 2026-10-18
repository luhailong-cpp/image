from pathlib import Path
import json,hashlib,datetime
from PIL import Image
T=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
coords=json.loads((T/'coordinates.json').read_text(encoding='utf-8-sig'))
for version in ['p32-v20261016-v2','p24-v20261016']:
 d=T/'native'/(version+'.png');q=T/'prompts'/(version+'.request.json');r=T/'prompts'/(version+'.receipt.json');meta=Path(str(d)+'.generation.json')
 assert d.exists() and not meta.exists()
 req=json.loads(q.read_text(encoding='utf-8-sig'));receipt=json.loads(r.read_text(encoding='utf-8-sig'));source=Path(receipt['sourceOutputPath']);assert sha(d)==sha(source)
 with Image.open(d) as im:size=list(im.size);fmt=im.format;im.verify()
 record={'file':str(d),'sha256':sha(d),'generatedAt':receipt['receivedAt'],'nativeSize':size,'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen','route':'builtin','sourceOutputPath':str(source),'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Tool did not disclose actual model or quality.','prompt':str(T/'prompts'/(version+'.txt')),'request':str(q),'references':[{'file':p,'sha256':sha(p),'role':req['referenceRoles'][i]} for i,p in enumerate(req['referenced_image_paths'])],'evidence':str(r),'coordinates':next(x for x in coords['patches'] if x['id']==version.split('-')[0]),'dimensionsMatch1254Plan':size==[1254,1254],'resized':False,'status':'native-candidate-awaiting-seam-review','recoveryNote':'Native copy succeeded before ingest metadata missing referenceRoles error; verified byte-identical saved output and finalized missing record without rewriting image.'}
 meta.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'version':version,'sha256':sha(d)}))
# Correct pointers only, never image bytes.
for meta in (T/'native').glob('*v20261016*.png.generation.json'):
 j=json.loads(meta.read_text(encoding='utf-8-sig'));v=meta.name.removesuffix('.png.generation.json')
 j['prompt']=str(T/'prompts'/(v+'.txt'));j['evidence']=str(T/'prompts'/(v+'.receipt.json'))
 assert Path(j['prompt']).exists() and Path(j['evidence']).exists()
 meta.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')

