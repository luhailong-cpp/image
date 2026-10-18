from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pin=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
p=Z/'qa/r03_coast_pair_paving_root_20261017_a01_mask_v1/mask_selection.json';s=json.loads(p.read_text())
for k in ['target','repair','mask','combinedCrop']:assert sha(s[k]['path'])==s[k]['sha256']
a=np.array(Image.open(s['target']['path']).convert('RGB'));b=np.array(Image.open(s['repair']['path']).convert('RGB'));m=np.array(Image.open(s['mask']['path']));c=np.array(Image.open(s['combinedCrop']['path']).convert('RGB'))
assert a.shape==b.shape==c.shape==(1254,1254,3)
assert set(np.unique(m)).issubset({0,255}) and np.array_equal(c,np.where((m==255)[:,:,None],b,a))
assert int((m==255).sum())==22390
out=Z/'qa/r03_coast_pair_paving_mask_v1_independent_right_20261017.json'
d=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='right_continuation',scope='Full1254 combined crop native-scale independent local geometry and binary-mask boundary review only.',selectionRecord=pin(p),target=s['target'],repair=s['repair'],mask=s['mask'],combined=s['combinedCrop'],actuallyViewedAtNativeScale=True,all1572516PixelsExactSourceSelection=True,repairPixelCount=22390,geometryStatus='PASS',note='The slab edge through local (626,150) is a single continuous diagonal groove with coherent bevel and no exposed step, blind end, double outline or hard mask cut. All four selected-region boundaries appear continuous in the full original-size image.',materialStatus='PENDING_NOT_REVIEWED_GLOBALLY',fullTileAccepted=False,formalAccepted=False)
with out.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps(pin(out)))

