from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
Z=Path(__file__).resolve().parent
fi=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
p=Z/'tiles/r05_c05_candidate-v1_4096.png';ip=Z/'qa/assembly_r05_c05_candidate-v1_4096/qa_index.json';d=json.loads(ip.read_text());im=Image.open(p).convert('RGB');items=[]
for e in d['seamAndJunctionCrops']:
 n=Path(e['path']).name
 if n.startswith('top-bottom'):continue
 q=Path(e['path']);assert fi(q)['sha256']==e['sha256'];assert np.array_equal(np.array(im.crop(e['tileCropBoxHalfOpen'])),np.array(Image.open(q).convert('RGB')))
 pending=n in ['left-right_r03_c01-c02_100pct.png','junction_r02-r03_c01-c02_100pct.png']
 items.append({**e,'reviewer':'right_continuation','reviewMethod':'complete original-resolution view','viewedOriginal':True,'exactCurrentTilePixelsVerified':True,'geometry':'PASS','appearance':'REPAIR' if pending else 'material_pending_not_formal','note':'Known straight horizontal shadow cut at tile y2163, x900..1140; planned native local repair.' if pending else 'No new disconnected structural outline or coarse grout found; repetitive stone microtexture remains pending where present.'})
assert len(items)==21
out=Z/'qa/r05_c05_v1_owner_left_right12_junction9_review_20261016.json'
with out.open('x',encoding='utf8') as f:json.dump({'candidate':fi(p),'record':fi(p.with_suffix('.assembly.json')),'qaIndex':fi(ip),'items':items,'nativeCropCount':21,'scope':'12 LR and9 junctions only; connected separately reviewed12 TB','knownExternalWestUpperGroutPending':True,'materialStatus':'PENDING','internalClosurePassed':False,'formalAccepted':False},f,indent=2)
print(json.dumps(fi(out)))
