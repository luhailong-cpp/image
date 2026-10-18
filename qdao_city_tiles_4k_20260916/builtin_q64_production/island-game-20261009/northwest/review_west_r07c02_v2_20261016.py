from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def info(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
old=Z/'qa/r07_c02_v1_owner_native33_review_20261016.json';d=read(old);q=Z/'qa/r07_c02_v2_internal_review/qa_index.json';index=read(q);prior={Path(x['path']).name:x for x in d['items']};items=[]
for x in index['seamAndJunctionCrops']:
 name=Path(x['path']).name;before=prior[name];same=x['sha256']==before['sha256']
 if same:assert before['status']=='PASS'
 assert info(Path(x['path']))['sha256']==x['sha256']
 items.append({**x,'status':'PASS','method':'same-hash reuse previous owner native PASS' if same else 'view_image original complete changed crop and full1254 mask boundary review','note':before['note'] if same else 'Red beam narrow lower ridge is now continuous; no step/notch, surrounding beam edges/window/stone contours unchanged.','reuseFrom':info(old) if same else None})
d.update(candidate=index['candidate'],record=index['record'],qaIndex=info(q),strictReplay=info(Z/'qa/r07_c02_v2_strict_native_replay_20261016.json'),status='owner_native33_geometry_PASS_independent_delta_and_material_pending',passed=33,repair=0,items=items,reviewedAtUtc=datetime.now(timezone.utc).isoformat(),internalGeometryClosurePassed=False,internalClosurePassed=False,materialStatus='PENDING')
d['distinctGeometricIssues'][0]['status']='OWNER_RESOLVED_IN_V2_INDEPENDENT_DELTA_PENDING'
d['repairBoundaryReview']={'combinedCrop':info(Z/'qa/r07_c02_red_beam_join_a01_mask_v2/combined_native_crop.png'),'mask':info(Z/'qa/r07_c02_red_beam_join_a01_mask_v2/source_selection_mask.png'),'scope':'Actual full1254 original image including all mask outer perimeter','geometryStatus':'PASS','rejectedMaskV1':'Retained unselected; excessive mask boundary crossed beam upper edge and produced an offset. V2 uses smaller same-coordinate source selection.'}
p=Z/'qa/r07_c02_v2_owner_native33_review_20261016.json';assert not p.exists();p.write_text(json.dumps(d,indent=2)+'\n')
s=Z/'west-current-selection-20261012.json';sel=read(s);sel['currentTile'].update(internalReview=info(p),status=d['status'],materialPending=d['materialPending']);s.write_text(json.dumps(sel,indent=2)+'\n')
print(json.dumps({'ownerReview':info(p),'passed':33}))
