from pathlib import Path
import json,hashlib
z=Path(__file__).resolve().parent
stem='r05_c05_s01_01_a02';ip=z/f'guides/{stem}.input.json';rp=z/f'guides/{stem}.references.json'
d=json.loads(ip.read_text());refs=json.loads(rp.read_text());assert len(refs)==4
p=z/'native/r05_c05_s01_01_a01.png';g=p.with_suffix('.png.generation.json');fi=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
target={**fi(p),'nativeSize':[1254,1254],'role':'same-coordinate initial native candidate to edit; preserve all areas except upper west grout mismatch','generationRecord':fi(g)}
refs=[target]+refs;d['inputs']=refs;d['inputCount']=5;d['imageGenReferencedImagePaths']=[x['path'] for x in refs];d['editSource']=target;d['operation']='same-coordinate edit native candidate with exact approved west edge layout guide';d['newUnsubmittedReferencePolicy']='native edit target prepended to fresh a02 guide plus three approved refs; no old images changed'
ip.write_text(json.dumps(d,indent=2)+'\n');rp.write_text(json.dumps(refs,indent=2)+'\n')
print(json.dumps([x['path'] for x in refs]))

