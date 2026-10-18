from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pin=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def verify(p):assert sha(p['path'])==p['sha256'],p['path']
Q=Z/'qa/r05_c05_v2_internal_delta_review_20261017';ip=Q/'qa_index.json'
assert sha(ip)=='f61e2598154f0f69f16c71473867096fada8f1ebc9cce4e6d20bbab2fe58515f'
idx=read(ip)
for k in ['candidate','record','baseline','priorIndex']:verify(idx[k])
strictp=Q/'strict_native_replay.json';strict=read(strictp)
assert strict['status']=='base_native_coverage_reverified' and strict['proof']['fullNativeCoverage'] is True and strict['proof']['verifiedPixelCount']==16777216 and strict['proof']['priorRepairCount']==1
rootp=Z/'qa/r05_c05_mask_v2_root_independent_20261017.json'
assert sha(rootp)=='0dd375104ba446d9b5a59f0e777d03f4901b497f0f1033dea1bcb3d21cb73d17'
oldownerp=Z/'qa/r05_c05_v1_owner_left_right12_junction9_review_20261016.json'
oldtbp=Z/'qa/r05_c05_v1_top_bottom12_independent_connected_20261016.json'
assert sha(oldownerp)=='0ef9a8da61e70e242c5473c968606fb6ebb35317db801b926dd7f1245634525d'
assert sha(oldtbp)=='14a92391bbabbb06241fcf49d17c0103e6b5bebe083e325e39c8ec2ece7937c1'
om={Path(c['path']).name:c for c in read(oldownerp)['items']}
tm={Path(c['path']).name:c for c in read(oldtbp)['crops']}
tile=Image.open(idx['candidate']['path']).convert('RGB')
baseline=Image.open(idx['baseline']['path']).convert('RGB')
reviews=[]
for c in idx['seamAndJunctionCrops']:
 verify(c);box=c['tileCropBoxHalfOpen'];cur=np.array(tile.crop(box))
 assert np.array_equal(cur,np.array(Image.open(c['path']).convert('RGB')))
 same=np.array_equal(cur,np.array(baseline.crop(box)))
 assert same==c['reusedUnchangedV1Crop']
 name=Path(c['path']).name
 if same:
  old=tm[name] if name.startswith('top-bottom') else om[name]
  assert old['sha256']==c['sha256']
  geom=old['review']['geometry'] if name.startswith('top-bottom') else old['geometry']
  assert geom=='PASS'
  basis=pin(oldtbp if name.startswith('top-bottom') else oldownerp)
  method='Exact current pixels and hash unchanged; reuse prior native geometry PASS'
 else:
  basis=pin(rootp)
  method='Owner viewed complete current crop at original resolution; root independently viewed the full1254 combined repair including all changed pixels and mask boundaries. Does not claim a connected v2 TB review.'
 reviews.append(dict(crop=pin(c['path']),tileCropBoxHalfOpen=box,currentTilePixelsExact=True,geometryStatus='PASS',unchangedPixelReuse=same,ownerViewedCurrentAtNativeScale=not same,reviewEvidence=basis,method=method,materialStatus='PENDING'))
assert len(reviews)==33 and sum(r['unchangedPixelReuse'] for r in reviews)==28
selp=Z/'qa/r05_c05_r2r3_grout_shadow_a01_mask_v2/mask_selection.json';sel=read(selp)
for k in ['target','repair','mask','combinedCrop']:verify(sel[k])
crop=np.array(tile.crop([0,1600,1254,2854]));assert np.array_equal(crop,np.array(Image.open(sel['combinedCrop']['path']).convert('RGB')))
assert all(x==0 for x in idx['outer115ChangedPixelCounts'].values())
now=datetime.now(timezone.utc).isoformat()
out=Q/'r05_c05_v2_geometry_delivery_20261017.json'
d=dict(createdAtUtc=now,tileId='r05_c05',reviewer='right_continuation',candidate=idx['candidate'],record=idx['record'],qaIndex=pin(ip),strictNativeReplay=pin(strictp),originalSourceCount=16,repairSourceCount=1,repairPixelCount=745933,independentFull1254MaskReview=pin(rootp),ownerLR2Junction1Review=pin(Q/'owner_changed_lr2_junction1_review.json'),priorOwner21=pin(oldownerp),priorIndependentTB12=pin(oldtbp),currentCropReviews=reviews,ownerChangedNativeCropCount=5,unchangedNativeCropReuseCount=28,geometryPassCount=33,internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',formalAccepted=False,additionalConnectedV2TBReview='not required for this closure basis and not yet received when recorded',resolvedFindings=['Three coarse grout blind/misaligned ends in r2-r3 west section now meet coherent slab junctions.','Straight rectangular shadow/material cutoff at tile y2163 removed without new hard selection edge.'],pendingFindings=[dict(status='material_pending',note='Dense repetitive fine grid and microtexture on stone fields requires material review; not counted PASS.'),dict(status='external_seam_pending',edge='west upper segment',note='Known cross4K upper-west paving alignment remains pending. The v2 repair preserves all four outer115 strips exactly.'),dict(status='other_external_edges_not_accepted',note='No formal neighboring-tile or cross-zone acceptance is asserted.')],outer115ChangedPixelCounts=idx['outer115ChangedPixelCounts'],generationRoute='builtin image_gen.imagegen',actualModel=None,explicitOwnerAdoption=True)
with out.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
sp=Z/'right-current-selection-20261012.json';s=read(sp);before=copy.deepcopy(s);t=s['tiles']['r05_c05']
assert t['candidate']['sha256']=='b0a9f4bef308ebe9899b5324497767cfd8d07b197c168837f998150efb38801e'
assert s['tiles']['r07_c04']['candidate']['sha256']=='0a6708ddd6da15499c92ce9a98696e024f20f164a99a69be9ccbdb2d7e91fef6'
backup=Z/'qa/right_selection_before_r05c05_v2_adoption_20261017.json'
with backup.open('xb') as f:f.write(sp.read_bytes())
t.setdefault('candidateHistory',[]).append(dict(candidate=t['candidate'],record=t['record'],status='superseded_by_native_grout_shadow_repair_v2'))
t.update(candidate=idx['candidate'],record=idx['record'],qaIndex=pin(ip),geometryClosureRecord=pin(out),internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',formalAccepted=False,nativeReview33Count=33,pendingFindings=d['pendingFindings'],strictNativeReplay=pin(strictp),ownerAdoptionRecord=pin(out))
for c in t['cells']:c['selection']='selected_native_for_candidate_material_and_external_pending'
s['updatedAtUtc']=now
for k,v in before['tiles'].items():
 if k!='r05_c05':assert s['tiles'][k]==v
sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(delivery=pin(out),state=pin(sp),candidate=idx['candidate'],record=idx['record'],qaIndex=pin(ip),geometryPassCount=33,formalAccepted=False)))

