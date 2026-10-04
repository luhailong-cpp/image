from pathlib import Path
import json,hashlib
from PIL import Image
b=Path(__file__).resolve().parents[2]
slots=[('N',7),('N',8),('N',11),('N',14),('N',15),('S',2),('S',3),('S',10),('S',11),('S',14)]
rows=[]
for di,n in slots:
 p=b/'provenance/derived'/f'run-{di}-{n:02d}.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
 r=d['originalGenerationRecord'];h=Path(r['evidence']['hostOutput'])
 assert h.exists()
 sha=hashlib.sha256(h.read_bytes()).hexdigest()
 assert sha==r['sha256'],f'{di}{n}: host mismatch'
 assert Image.open(h).size==(1254,1254)
 runtime=b/d['file'];assert hashlib.sha256(runtime.read_bytes()).hexdigest()==d['sha256']
 rows.append({'direction':di,'frame':n,'hostTarget':str(h),'hostTargetSHA256':sha,'supersedes':{'file':d['file'],'sha256':d['sha256'],'source':d['derivedFrom']['path'],'sourceSHA256':d['derivedFrom']['sha256'],'generationRecord':d['derivedFrom']['generationRecord'],'derivedRecord':str(p.relative_to(b))},'retainedTransform':d['operation']})
(b/'audit/archer-reference/ns-targets.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'slot':f"{r['direction']}{r['frame']:02d}",'host':r['hostTarget']}for r in rows]))

