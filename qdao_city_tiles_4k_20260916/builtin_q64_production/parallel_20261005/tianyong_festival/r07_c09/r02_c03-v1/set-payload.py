from pathlib import Path
import json,hashlib
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
p=read(D/'actual-payload.json');r=read(D/'request.json');r['payload']=p;save(D/'request.json',r);(D/'prompt.txt').write_text(p['prompt'],encoding='utf-8')
prep=read(D/'preparation.json');prep['references']=[{'file':f,'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest(),'role':role} for f,role in zip(p['referenced_image_paths'],['coarse layout with exact native anchors, INPUT ONLY','exact native anchors','approved actual painting style'])];save(D/'preparation.json',prep)
