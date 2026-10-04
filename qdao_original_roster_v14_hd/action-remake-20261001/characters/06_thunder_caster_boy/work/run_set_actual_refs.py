import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
stem,spec=sys.argv[1:3]
p=ROOT/'work'/(stem+'.png.generation.json');r=json.loads(p.read_text(encoding='utf-8'))
inputs=json.loads((ROOT/spec).read_text(encoding='utf-8'))
r['references']=[{'path':i['path'],'role':i['role'],'sha256':hashlib.sha256(Path(i['path']).read_bytes()).hexdigest()} for i in inputs]
r['submittedParameters']['referenced_image_paths']=[i['path'] for i in inputs]
r['submittedParameters']['prompt']=(ROOT/r['prompt']).read_text(encoding='utf-8')
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(p.name)

