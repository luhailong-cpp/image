from pathlib import Path
import json,hashlib,sys
B=Path(__file__).resolve().parents[1];p=Path(sys.argv[1]);assert p.is_relative_to(B)
r=json.loads(p.read_text(encoding='utf-8-sig'));assert len(r['references'])==4
ref=B/'pipeline-tools/native-quiet-gray-style-20261016-v01.png'
r['references'].append({'file':str(ref),'sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'role':'Native quiet natural stone surface only; exact crop from actual builtin p0301, copy no geometry or slab lines.'});r['referenced_image_paths']=[v['file'] for v in r['references']]
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))

