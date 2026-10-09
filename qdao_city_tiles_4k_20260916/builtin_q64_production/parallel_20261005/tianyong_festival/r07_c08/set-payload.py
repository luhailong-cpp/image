from pathlib import Path
import json,hashlib,sys
D=Path(__file__).parent/sys.argv[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
payload=read(D/'actual-payload.json');(D/'prompt.txt').write_text(payload['prompt'],encoding='utf-8');req=read(D/'request.json');req['payload']=payload;save(D/'request.json',req)
p=read(D/'preparation.json');p['references']=[{'file':v,'sha256':sha(v),'role':r} for v,r in zip(payload['referenced_image_paths'],['input only: approximate canonical guide in unknown plus exact native anchors; no guide pixels in final','exact real native context','approved primary style'])];save(D/'preparation.json',p)
q=D/'coarse-layout-with-native-anchors-reference-only.png';save(Path(str(q)+'.generation.json'),{'file':str(q),'sha256':sha(q),'operation':'Input only: exact native context over approximate canonical guide; no guide pixels permitted in final','derivedFrom':[{'file':str(D/v),'sha256':sha(D/v)} for v in ['context.png','layout-reference-only.png']],'newModelCalls':0,'actualModel':None,'actualQuality':None})
