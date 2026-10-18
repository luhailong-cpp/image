from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
from datetime import datetime,timezone
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
def pin(p):
 p=Path(p);return dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
idxp=Z/'qa/r06_c02_v2_internal_review/qa_index.json';idx=json.loads(idxp.read_text())
im=Z/'tiles/r06_c02_candidate-v2_4096.png';rp=im.with_suffix('.native-repair.json')
assert pin(im)['sha256']=='96a279346ae40fa92cc6c6c0f024c75ef11ed7a623ffbc62daf483a376f7eaec'
assert pin(idxp)['sha256']=='cb251df9703050e306c5ae7c7d66491c459f9748ec86d33d7bf43f2b5a0e3848'
a=np.asarray(Image.open(im).convert('RGB'));notes=json.loads((Z/'qa/r06_c02_v2_connected_native33_notes_20261016.json').read_text())['items']
items=[]
assert len(notes)==len(idx['seamAndJunctionCrops'])==33
for n in notes:
 c=idx['seamAndJunctionCrops'][n['i']];assert pin(c['path'])['sha256']==c['sha256']
 l,t,r,b=c['tileCropBoxHalfOpen'];assert np.array_equal(a[t:b,l:r],np.asarray(Image.open(c['path']).convert('RGB')))
 items.append(dict(name=Path(c['path']).name,crop=c,geometry='PASS',materialStatus='PENDING_ROOT_REPORTED_SURFACE_LIMITS',note=n['note'],actualCurrentPixelIdentityVerified=True))
d=Z/'qa/r06_c02_yellow_foliage_band_a02_mask_v1';m=json.loads((d/'mask_selection.json').read_text())
for k in ['target','repair','mask','combinedCrop']:assert pin(m[k]['path'])['sha256']==m[k]['sha256']
target=np.asarray(Image.open(m['target']['path']).convert('RGB'));raw=np.asarray(Image.open(m['repair']['path']).convert('RGB'));mask=np.asarray(Image.open(m['mask']['path']))==255;combined=np.asarray(Image.open(m['combinedCrop']['path']).convert('RGB'))
assert np.array_equal(combined[mask],raw[mask]) and np.array_equal(combined[~mask],target[~mask])
rr=json.loads(rp.read_text());l,t,r,b=rr['cropBox'];assert np.array_equal(a[t:b,l:r],combined)
report=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='/root/connected_continuation',candidate=pin(im),record=pin(rp),qaIndex=pin(idxp),viewDetail='original',geometryPassed=33,standardCropCount=33,items=items,repairMaskReview=dict(source=pin(d/'mask_selection.json'),combined=pin(m['combinedCrop']['path']),mask=pin(m['mask']['path']),geometry='PASS',scope='Full 1254 crop including selected foliage and all mask boundaries inspected; previous leaf band cut absent; branches, flower and leaf silhouettes continuous.',sourcePixelReplay=True),internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',materialIssues=['Root reported fine grid texture in upper paving','Root reported soft background detail in southwest flower canopy'],formalAccepted=False,sourceImagesModified=False)
p=Z/'qa/r06_c02_v2_independent_native33_connected_20261016.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(pin(p)))

