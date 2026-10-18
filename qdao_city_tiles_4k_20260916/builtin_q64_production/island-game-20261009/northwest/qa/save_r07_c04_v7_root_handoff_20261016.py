from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
qd=Z/'qa/r07_c04_v7_internal_delta_root_20261016';qp=qd/'qa_index.json';q=json.loads(qp.read_text())
assert q['changedNames']==['left-right_r04_c01-c02_100pct.png'] and len(q['unchangedNames'])==32
strict=Z/'qa/r07_c04_v7_strict_native_replay_root_20261016.json';s=json.loads(strict.read_text(encoding='utf-8-sig'))
assert s['status']=='base_native_coverage_reverified' and s['proof']['verifiedPixelCount']==16777216
items=[]
for x in q['seamAndJunctionCrops']:
 assert sha(x['path'])==x['sha256']
 if Path(x['path']).name in q['changedNames']:
  items.append({**x,'rootActuallyViewedAtNativeScale':True,'geometryStatus':'PASS','materialStatus':'IMPROVED_AWAITING_INDEPENDENT_REVIEW','note':'Broad diagonal slab outlines retained; lower stone grain vertical cut is reduced in the selected local native repair. No global material pass claimed.'})
maskdir=Z/'qa/r07_c04_south_grain_root_20261016_a01_mask_v1'
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tileId':'r07_c04','reviewer':'root','candidate':q['candidate'],'record':q['record'],'qaIndex':pin(qp),'fullRepairCrop':{**pin(maskdir/'combined_native_crop.png'),'actuallyViewedAtNativeScale':True,'dimensions':[1254,1254],'geometryStatus':'PASS','materialStatus':'IMPROVED_AWAITING_INDEPENDENT_REVIEW'},'mask':pin(maskdir/'source_selection_mask.png'),'rootChangedCropReview':items,'unchangedCropCount':32,'priorGeometryClosure':pin(Z/'qa/r07_c04_v6_internal_delta_review/r07_c04_v6_geometry_delivery_20261016.json'),'strictReplay':pin(strict),'outer115Delta':pin(qd/'outer115_delta.json'),'internalGeometryClosurePassed':True,'internalClosurePassed':False,'materialStatus':'PENDING','formalAccepted':False,'note':'South outer115 has 31,941 changed pixels; north/west/east115 unchanged. Right owner must explicitly adopt this candidate after independent local material review. Root did not mutate right selection state.','generationRoute':'builtin image_gen.imagegen','actualModel':None}
op=qd/'root_handoff.json';assert not op.exists();op.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(pin(op)))
