from pathlib import Path
import json,hashlib
w=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
req=json.loads((w/'request.json').read_text(encoding='utf-8'))
for ref in req['references']:
 p=Path(ref['path']);assert sha(p)==ref['sha256'],str(p)+' input changed'
 record=Path(str(p)+'.generation.json')
 if record.exists():
  ref['generationRecord']=str(record)
  ref['recordSHA256']=sha(record)
(w/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['native.png.generation.json','review1024.png.generation.json']:
 p=w/name;rec=json.loads(p.read_text(encoding='utf-8'));rec['references']=req['references'];rec['status']='visually-reviewed-ready-for-integration';p.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
(w/'config-snapshot.json').write_text(json.dumps(req['configSnapshot'],indent=2),encoding='utf-8')
print('All runtime inputs unchanged; source generation-record hashes saved; final candidate records complete.')

