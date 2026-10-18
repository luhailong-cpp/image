from pathlib import Path
import hashlib,json
from PIL import Image
T=Path(__file__).resolve().parents[1]
src=T.parent/'r13_c13/candidate/r13_c13-4k-candidate-repaired.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(src)=='db5f956694c700b16094eb532ad9097e8a54f4a19d14797325f6fbd0ca18971f'
out=T/'review/east-seed-context-20261016.png'
with Image.open(src) as im:
 assert im.size==(4096,4096)
 crop=im.crop((0,909,600,2163))
 with out.open('xb') as f:crop.save(f,format='PNG')
record={'source':str(src),'sourceSha256':sha(src),'sourceCrop':[0,909,600,2163],
 'output':str(out),'sha256':sha(out),'resized':False,
 'role':'read-only native east-neighbor evidence; not new generated art'}
out.with_suffix('.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))

