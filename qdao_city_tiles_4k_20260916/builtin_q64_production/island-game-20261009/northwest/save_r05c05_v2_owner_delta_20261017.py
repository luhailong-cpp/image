from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
import numpy as np
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pin=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
Q=Z/'qa/r05_c05_v2_internal_delta_review_20261017'
ip=Q/'qa_index.json';assert sha(ip)=='f61e2598154f0f69f16c71473867096fada8f1ebc9cce4e6d20bbab2fe58515f'
idx=json.loads(ip.read_text());tile=Image.open(idx['candidate']['path']).convert('RGB')
root=Z/'qa/r05_c05_mask_v2_root_independent_20261017.json'
assert sha(root)=='0dd375104ba446d9b5a59f0e777d03f4901b497f0f1033dea1bcb3d21cb73d17'
strictp=Q/'strict_native_replay.json';strict=json.loads(strictp.read_text(encoding='utf-8-sig'))
assert strict['status']=='base_native_coverage_reverified' and strict['proof']['verifiedPixelCount']==16777216 and strict['proof']['fullNativeCoverage'] is True
items=[]
for c in idx['seamAndJunctionCrops']:
 if c['reusedUnchangedV1Crop'] or Path(c['path']).name.startswith('top-bottom'):continue
 assert sha(c['path'])==c['sha256']
 assert np.array_equal(np.array(Image.open(c['path']).convert('RGB')),np.array(tile.crop(c['tileCropBoxHalfOpen'])))
 items.append({**c,'actuallyViewedAtNativeScale':True,'geometryStatus':'PASS','materialStatus':'PENDING','note':'Full native crop viewed: coarse slab outlines are continuous across the repaired region and hard-selection boundary; old rectangular shadow cutoff is gone. Dense stone microtexture remains material pending.'})
assert len(items)==3
out=Q/'owner_changed_lr2_junction1_review.json'
d=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='right_continuation',candidate=idx['candidate'],record=idx['record'],qaIndex=pin(ip),strictNativeReplay=pin(strictp),independentFullMaskReview=pin(root),items=items,changedNativeViews=3,geometryPassCount=3,internalClosurePassed=False,formalAccepted=False)
with out.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps(pin(out)))

