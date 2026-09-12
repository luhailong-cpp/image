"""Package only approved final assets, manifests, prompts and review records."""
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
import json, hashlib
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'validation.json').read_text(encoding='utf8'))
assert r['status']=='passed' and r['passed_characters']==8 and r['verified_frames']==256
paths={ROOT/'README.md',ROOT/'DESIGN_BRIEF.md',ROOT/'manifest.json',ROOT/'validation.json',ROOT/'roster-overview.jpg',ROOT/'movement-overview.gif'}
for row in r['characters']:
    role=ROOT/row['slug']
    for a in row['artifacts']:
        p=ROOT/a['path']; assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],p
        paths.add(p)
    for name in ['README.md','STATUS.md','manifest.json','qc.json','delivery-verification.json']:
        if (role/name).exists():paths.add(role/name)
    for folder in ['prompts','processing']:
        d=role/folder
        if d.exists():
            for p in d.rglob('*'):
                if p.is_file() and (p.suffix in ['.json','.txt','.md'] or p.name=='visual-review.jpg' or (p.name.startswith('festival-edge-') and p.suffix=='.jpg')): paths.add(p)
assert all('24_crane_hermit' not in p.parts for p in paths)
out=ROOT/'qdao-roster-v11-final.zip'
with ZipFile(out,'w') as z:
    for p in sorted(paths):
        assert p.is_file(),p
        z.write(p,p.relative_to(ROOT).as_posix(),compress_type=ZIP_STORED if p.suffix in ['.png','.jpg','.gif'] else ZIP_DEFLATED)
with ZipFile(out) as z:
    assert z.testzip() is None
record={'file':out.name,'size_bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'entries':len(paths),'final_media':408,'portraits':8,'walk_frames':256,'archive_test':'passed','excludes':'rejected character and raw/history image candidates','source_note':'Original generation source images and deterministic build scripts remain in the project; this zip delivers approved engine images, previews, prompts and records.'}
(ROOT/'download.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record,ensure_ascii=False))
