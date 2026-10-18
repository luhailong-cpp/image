from pathlib import Path
import json,sys,hashlib
p=Path(sys.argv[1]);r=json.loads(p.read_text(encoding='utf-8-sig'))
assert len(r['references'])==4
q=Path(__file__).resolve().parent/'guides/quiet-native-stone-20261016-v01.png'
r['references'].append({'file':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'role':'quiet native stone MATERIAL ONLY; exact target geometry only image1'})
r['referenced_image_paths']=[x['file'] for x in r['references']]
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,ensure_ascii=False))
