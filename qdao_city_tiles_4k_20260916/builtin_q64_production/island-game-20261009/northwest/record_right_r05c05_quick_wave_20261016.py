from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
fi=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
wave=sys.argv[1];items=[]
for stem in sys.argv[2:]:
 p=Z/'qa'/f'{stem}_quick_native_v1/index.json';d=json.loads(p.read_text());im=Z/'native'/f'{stem}.png'
 for e in d['items']:
  assert fi(Path(e['path']))['sha256']==e['sha256'] and fi(Path(e['neighbor']))['sha256']==e['neighborSha256'] and fi(im)['sha256']==e['imageSha256']
 items.append({'stem':stem,'image':fi(im),'index':fi(p),'full1254Viewed':True,'adjacentCropsViewedOriginal':[e['direction'] for e in d['items']],'quickGeometry':'pass_provisional','notWholeTileApproval':True})
out=Z/'qa'/f'r05_c05_{wave}_quick_review_20261016.json'
with out.open('x',encoding='utf8') as f:json.dump({'tile':'r05_c05','reviewer':'right_continuation','createdAtUtc':datetime.now(timezone.utc).isoformat(),'items':items,'pending':'Prior first source upper west cross-4K coarse grout offset remains pending; no new blocking layout fault seen in this wave. Material and whole33 still pending.','internalClosurePassed':False,'formalAccepted':False},f,indent=2)
print(json.dumps(fi(out)))
