from pathlib import Path
import json,hashlib,datetime,numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();info=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
ip=Z/'qa/r07_c04_v6_internal_delta_review/qa_index.json';q=json.loads(ip.read_text(encoding='utf-8-sig'));candidate=q['candidate'];assert sha(candidate['path'])==candidate['sha256']
tile=np.array(Image.open(candidate['path']).convert('RGB'));items=[x for x in q['seamAndJunctionCrops'] if not x['reusedUnchangedV1Crop'] and 'top-bottom_' in x['path']];assert len(items)==7
notes=["Railing cap, floral panel relief and foliage continuous.","Upper paving coarse joints and lower-left wall cap continuous.","Wall foot, narrow paving strip and adjacent slab joints continuous.","Large flower relief, cap and panel boundaries continuous.","Main paving grout network continuous across repaired central joins.","Broad paving slab network and red paper scraps continuous.","Stone verge and grass bed continuous without structural cutoff."]
for x,n in zip(items,notes):
 assert sha(x['path'])==x['sha256'];x0,y0,x1,y1=x['tileCropBoxHalfOpen']
 assert np.array_equal(tile[y0:y1,x0:x1],np.array(Image.open(x['path']).convert('RGB')))
 x.update(status='PASS',fullNativeViewed=True,method='view_image original full1024x480',note=n,exactCurrentPixelsVerified=True)
rp=Z/'qa/r07_c04_two_a02_repairs_independent_mask_review_20261013.json';old=json.loads(rp.read_text(encoding='utf-8-sig'))
for x in old['items']:
 for p in [x['combinedImage'],x['maskSelectionRecord'],*x['sourcePins'].values()]:assert sha(p['path'])==p['sha256']
out=Z/'qa/r07_c04_v6_changed_top_bottom7_independent_connected_20261016.json'
assert not out.exists()
out.write_text(json.dumps(dict(createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='connected_continuation',candidate=candidate,index=info(ip),status='SEVEN_CHANGED_TB_NATIVE_GEOMETRY_PASS',passed=7,repair=0,items=items,priorTwoMaskIndependentReview=dict(**info(rp),allPinnedHashesUnchanged=True,reusedWithoutReopening=True),scope='Only seven changed horizontal seams of exact v6; other26 items and external edges are separate records.',internalClosurePassed=False,formalAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(info(out)))

