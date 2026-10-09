from pathlib import Path
import json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r09_c11/r04_c01-v1')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):return {'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
base=read(D/'request.json')
p=D/'joint-repair-v1/native.png.generation.json';g=read(p);g.update(configSnapshot=base['configSnapshot'],submittedParameters=base['submittedParameters'],actualModel=None,actualQuality=None,observedCompletionAtUtc=read(D/'joint-repair-v1/tool-receipt.json')['observedAtUtc'],references=[ref(Path(q)) for q in read(D/'joint-repair-v1/request.json')['payload']['referenced_image_paths']]);save(p,g)
p=D/'joint-repair-v2/native.png.generation.json';g=read(p);g.update(observedCompletionAtUtc=read(D/'joint-repair-v2/tool-receipt.json')['observedAtUtc'],upstreamGenerationRecords=[ref(D/'joint-repair-v1/native.png.generation.json')]);save(p,g)
p=D/'join-v3/assembly.json';g=read(p);g['repairGeneration']=ref(D/'joint-repair-v2/native.png.generation.json');save(p,g)
p=D/'join-v3/joined.png.generation.json';g=read(p);g['generationRecords']=[ref(D/'native.png.generation.json'),ref(D/'joint-repair-v1/native.png.generation.json'),ref(D/'joint-repair-v2/native.png.generation.json')];g['assembly']=ref(D/'join-v3/assembly.json');save(p,g)
p=D/'join-v3/manifest.json';g=read(p);g['assembly']=ref(D/'join-v3/assembly.json');save(p,g)
print(json.dumps(ref(p)))
