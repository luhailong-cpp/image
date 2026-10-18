import sys,json,hashlib
from pathlib import Path
rp,ref,role=sys.argv[1:];p=Path(rp).resolve();r=json.loads(p.read_text(encoding='utf-8-sig'));t=p.parents[2]
assert t.name==r['tile'] and t.parent==Path(__file__).resolve().parents[2]
assert r['tile'] in {'r10_c03','r10_c04'}|{f'r{a:02d}_c{b:02d}' for a in [11,12] for b in range(1,5)}
patch=r['coordinates']['id'];attempt=p.name.removeprefix(patch+'.').removesuffix('.request.json')
assert not (t/'pipeline/receipts'/(patch+'.'+attempt+'.receipt.json')).exists()
assert len(r['references'])==4 and len(r['referenced_image_paths'])==4
f=Path(ref).resolve();assert f.exists();h=hashlib.sha256(f.read_bytes()).hexdigest()
r['references'].append({'file':str(f),'sha256':h,'role':role});r['referenced_image_paths'].append(str(f))
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
