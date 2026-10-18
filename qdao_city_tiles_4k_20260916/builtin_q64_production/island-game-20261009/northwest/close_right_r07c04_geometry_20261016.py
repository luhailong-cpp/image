import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
z=Path(__file__).resolve().parent;q=z/'qa/r07_c04_v6_internal_delta_review'
fi=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
index=read(q/'qa_index.json');p=Path(index['candidate']['path']);arr=np.array(Image.open(p).convert('RGB'))
notes={
'left-right_r01_c03-c04_100pct.png':'Rear cap and large slab joints continuous.',
'left-right_r02_c01-c02_100pct.png':'Orphan floral arc removed; panel and canopy continuous.',
'left-right_r02_c03-c04_100pct.png':'Rear cap, floral relief and foliage continuous.',
'left-right_r03_c01-c02_100pct.png':'Wall foot and three coarse paving junctions continuous.',
'left-right_r03_c02-c03_100pct.png':'Column, base and garden boundary intact.',
'left-right_r04_c01-c02_100pct.png':'Coarse paving geometry closed. Non-blocking old material granularity boundary near tile(909,3957) retained for later material review.',
'left-right_r04_c02-c03_100pct.png':'Lower middle grout now connects into coherent stone grid.',
'junction_r01-r02_c03-c04_100pct.png':'Cap intrusion removed; complete straight cap and stone joints.',
'junction_r02-r03_c01-c02_100pct.png':'Clean panel, coherent corner and wall-foot line.',
'junction_r02-r03_c02-c03_100pct.png':'Column geometry and relief edges intact.',
'junction_r03-r04_c01-c02_100pct.png':'Paving T junction and diagonal coarse edges closed.',
'junction_r03-r04_c02-c03_100pct.png':'Lower-middle paving joint closed without blind end.'}
owner=[]
for item in index['seamAndJunctionCrops']:
 f=Path(item['path']);n=f.name
 assert fi(f)['sha256']==item['sha256']
 x0,y0,x1,y1=item['tileCropBoxHalfOpen']
 assert np.array_equal(np.array(Image.open(f).convert('RGB')),arr[y0:y1,x0:x1])
 if n in notes:owner.append({**item,'status':'PASS_GEOMETRY','fullNativeViewed':True,'viewMethod':'view_image detail original','note':notes[n]})
assert len(owner)==12
orec={'candidate':fi(p),'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'right_continuation','scope':'Only 7 changed LR +5 changed junction crops, whole original native images viewed.','passCount':12,'items':owner,'materialAcceptance':False,'formalAccepted':False}
op=q/'owner_changed12_geometry_review_20261016.json'
with op.open('x',encoding='utf-8') as f:json.dump(orec,f,ensure_ascii=False,indent=2);f.write('\n')
tbp=z/'qa/r07_c04_v6_changed_top_bottom7_independent_connected_20261016.json';tb=read(tbp)
assert tb['passed']==7 and tb['candidate']['sha256']==fi(p)['sha256']
old21p=z/'qa/assembly_r07_c04_candidate-v1_4096/right_native21_review_20261013.json';old21=read(old21p)
old12p=z/'qa/r07_c04_v1_independent_top_bottom12_review_20261013.json';old12=read(old12p)
oldmap={Path(x['path']).name:x for x in old21['items']+old12['items']}
reused=[]
for item in index['seamAndJunctionCrops']:
 if not item['reusedUnchangedV1Crop']:continue
 n=Path(item['path']).name;old=oldmap[n];assert old['sha256']==item['sha256']
 if 'status' in old:assert old['status']=='pass'
 else:assert not old['knownRepairScopeAssociations']
 reused.append({**item,'status':'PASS_GEOMETRY_REUSED_EXACT_PIXELS','priorReview':fi(old21p if n.startswith(('left-right','junction')) else old12p)})
assert len(reused)==14
vp=q/'native_replay_validation.json';validation=read(vp)
assert validation['status']=='base_native_coverage_reverified' and validation['proof']['verifiedPixelCount']==16777216 and validation['proof']['priorRepairCount']==5
base=np.array(Image.open(z/'tiles/r07_c04_candidate-v1_4096.png').convert('RGB'))
edges={side:int(np.count_nonzero(np.any(a!=b,axis=2))) for side,a,b in [('north115',arr[:115],base[:115]),('south115',arr[-115:],base[-115:]),('west115',arr[:,:115],base[:,:115]),('east115',arr[:,-115:],base[:,-115:])]}
assert all(x==0 for x in edges.values())
material={'status':'nonblocking_material_review_pending','tileBoxHalfOpen':[880,3850,1070,4096],'note':'Old irregular stone grain granularity transition around tile(909,3957), unchanged from v1; no open coarse grout geometry. Not marked material PASS.'}
rec={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tileId':'r07_c04','candidate':fi(p),'candidateRecord':fi(z/'tiles/r07_c04_candidate-v6_4096.native-repair.json'),'nativeSourceCount':16,'nativeRepairCount':5,'status':'NATIVE_16_COMPLETE_INTERNAL_GEOMETRY_33_PASS_MATERIAL_REVIEW_PENDING','internalGeometryClosurePassed':True,'internalClosurePassed':False,'formalAccepted':False,'formalAcceptedCount':0,'nativeScale100Percent':True,'standardCropCount':33,'newlyReviewedChangedCropCount':19,'exactPixelPriorReviewsReused':14,'ownerChanged12':fi(op),'independentChanged7':fi(tbp),'reusedItems':reused,'lastTwoRepairBoundaryIndependentReview':fi(z/'qa/r07_c04_two_a02_repairs_independent_mask_review_20261013.json'),'nativeReplayValidation':fi(vp),'fullNativeCoverage':True,'verifiedPixelCount':16777216,'external115PixelDeltasFromV1':edges,'externalEdgesValidated':False,'pendingMaterialObservation':material,'actualModel':None,'modelEvidence':'Builtin imagegen returned no actual model metadata; no 2.5 claim.','method':{'finalArtResized':False,'pixelSynthesis':False,'feathering':False,'guidePixelsFinal':False},'preview':index['preview']}
rp=q/'r07_c04_v6_geometry_delivery_20261016.json'
with rp.open('x',encoding='utf8') as f:json.dump(rec,f,ensure_ascii=False,indent=2);f.write('\n')
sp=z/'right-current-selection-20261012.json';s=read(sp);other=json.dumps(s['tiles']['r06_c04'],sort_keys=True)
t=s['tiles']['r07_c04'];t.setdefault('candidateHistory',[]).append({'candidate':t['candidate'],'record':t['record'],'status':'superseded_by_verified_v6'})
t.update(candidate=fi(p),record=rec['candidateRecord'],assembled4k=True,internalGeometryClosurePassed=True,internalClosurePassed=False,formalAccepted=False,geometryClosureRecord=fi(rp),nativeReview33Count=33,pendingFindings=[material])
s['updatedAtUtc']=datetime.now(timezone.utc).isoformat()
assert other==json.dumps(s['tiles']['r06_c04'],sort_keys=True)
sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'delivery':fi(rp),'ownerReview':fi(op),'state':fi(sp),'nativeReplay':fi(vp),'image':fi(p),'external115PixelDeltas':edges}))

