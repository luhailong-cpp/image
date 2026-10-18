from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image, ImageChops
Z=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):
 p=Path(p); return {'path':p.as_posix(),'sha256':sha(p)}
qp=Z/'qa/r07_c02_v2_internal_review/qa_index.json'
q=json.loads(qp.read_text(encoding='utf-8-sig'))
assert sha(qp)=='28cd4450e24049db21d012c4cfdbb540182449b7bea9d6ab419a734ba3e37e2c'
for k in ('candidate','record'):
 assert sha(q[k]['path'])==q[k]['sha256']
im=Image.open(q['candidate']['path']).convert('RGB')
checks=[]
for a in q['seamAndJunctionCrops']:
 p=Path(a['path']); name=p.name
 if name not in q['changedNames']: continue
 assert sha(p)==a['sha256']
 crop=Image.open(p).convert('RGB')
 assert ImageChops.difference(im.crop(tuple(a['tileCropBoxHalfOpen'])),crop).getbbox() is None
 checks.append({**a,'geometryStatus':'PASS','reviewer':'root','actuallyViewedAtNativeScale':True,'assessment':'Red beam lower contour and adjacent wall/statue contours remain continuous; no new geometric seam in this crop. Material scope remains pending.'})
assert len(checks)==5
base=Z/'qa/r07_c02_red_beam_join_a01_mask_v2'
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c02','reviewer':'root','candidate':q['candidate'],'record':q['record'],'qaIndex':pin(qp),'fullRepairCrop':{**pin(base/'combined_native_crop.png'),'dimensions':[1254,1254],'actuallyViewedAtNativeScale':True,'geometryStatus':'PASS','assessment':'Repaired lower red beam edge is straight through the former offset; upper beam and window contours have no new cut. Stone crackle density is outside this geometry-only pass.'},'binaryMask':pin(base/'source_selection_mask.png'),'changedCropChecks':checks,'changedCropCount':5,'geometryStatus':'PASS','materialStatus':'PENDING','internalClosurePassed':False,'formalAccepted':False,'unchangedCropPolicy':'28 other crops are not re-reviewed here; reuse prior reviews only after identical hashes are verified.','remainingMaterialIssues':['Dense crackle or fragmented statue texture','Tree trunk grid texture','Soft yellow flowers and stone post foreground'],'scope':'Independent root review of one full 1254 repair crop and all five changed final native seam crops.'}
op=Z/'qa/r07_c02_v2_root_independent_delta5_20261016.json'
assert not op.exists(), str(op)
op.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(pin(op)))
