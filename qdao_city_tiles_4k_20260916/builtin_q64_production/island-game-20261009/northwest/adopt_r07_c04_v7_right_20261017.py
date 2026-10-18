from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):
 p=Path(p);return dict(path=p.as_posix(),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def verify(p):assert sha(p['path'])==p['sha256'],p['path']
now=datetime.now(timezone.utc).isoformat()
handoffpath=Z/'qa/r07_c04_v7_internal_delta_root_20261016/root_handoff.json'
assert sha(handoffpath)=='609dc655315e2fecb4904cef508ccdc7ef201edb6ac23418c68e08cdbb84c5b2'
h=read(handoffpath)
for k in ['candidate','record','qaIndex','fullRepairCrop','mask','priorGeometryClosure','strictReplay','outer115Delta']:verify(h[k])
idx=read(h['qaIndex']['path']); tile=np.array(Image.open(h['candidate']['path']).convert('RGB'))
prioridx=read(idx['priorIndex']['path']);verify(idx['priorIndex'])
old={Path(x['path']).name:x for x in prioridx['seamAndJunctionCrops']}
checks=[]
for c in idx['seamAndJunctionCrops']:
 verify(c);a=np.array(Image.open(c['path']).convert('RGB'));x0,y0,x1,y1=c['tileCropBoxHalfOpen'];assert np.array_equal(a,tile[y0:y1,x0:x1])
 p=old[Path(c['path']).name];verify(p)
 eq=np.array_equal(a,np.array(Image.open(p['path']).convert('RGB')))
 checks.append(dict(crop=pin(c['path']),tileCropBoxHalfOpen=c['tileCropBoxHalfOpen'],currentPixelsVerified=True,unchangedFromV6=eq,geometryStatus='PASS',reviewBasis='Exact pixel reuse of prior 33 geometry closure' if eq else 'Actually viewed original 480x1139; broad joints remain continuous, grain boundary softened with no new hard selection boundary'))
assert len(checks)==33 and sum(x['unchangedFromV6'] for x in checks)==32
selpath=Z/'qa/r07_c04_south_grain_root_20261016_a01_mask_v1/mask_selection.json';sel=read(selpath)
for k in ['target','repair','mask','combinedCrop']:verify(sel[k])
a=np.array(Image.open(sel['target']['path']).convert('RGB'));b=np.array(Image.open(sel['repair']['path']).convert('RGB'));m=np.array(Image.open(sel['mask']['path']));c=np.array(Image.open(sel['combinedCrop']['path']).convert('RGB'))
assert set(np.unique(m)).issubset({0,255}) and np.array_equal(c,np.where((m==255)[:,:,None],b,a))
out=Z/'qa/r07_c04_v7_right_adoption_20261017.json'
record=dict(createdAtUtc=now,reviewer='right_continuation',candidate=h['candidate'],record=h['record'],qaIndex=h['qaIndex'],rootHandoff=pin(handoffpath),strictReplay=h['strictReplay'],priorGeometryClosure=h['priorGeometryClosure'],full1254IndependentReview=dict(maskSelection=pin(selpath),target=sel['target'],repair=sel['repair'],mask=sel['mask'],combined=sel['combinedCrop'],actuallyViewedAtNativeScale=True,all1572516PixelsExactBinarySelection=True,geometryStatus='PASS',localMaterialIssueStatus='RESOLVED',observation='At local (509,1115), the old vertical granularity cutoff is removed; nearby irregular stone grain and coarse joint contours remain continuous. Full 1254 mask boundary and changed LR crop inspected at original scale before restart, hashes rechecked unchanged now.'),cropReviews=checks,geometryPassCount=33,internalGeometryClosurePassed=True,materialStatus='PENDING_FULL_MATERIAL_REVIEW',internalClosurePassed=False,formalAccepted=False,explicitOwnerAdoption=True,outer115Delta=h['outer115Delta'],anchorNotice='South115 changed 31941 pixels relative to v6. North/west/east115 unchanged. Use v7 actual south edge for future work.',limits=['Only local grain issue is resolved. No whole-tile material or external seam acceptance is asserted.'])
with out.open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
statepath=Z/'right-current-selection-20261012.json';state=read(statepath);before=copy.deepcopy(state);t=state['tiles']['r07_c04'];assert t['candidate']['sha256']=='c3957a2f411950d1bdd324ac8a1e60fee136fade0fe9cbf3cbb1a60b7ddfa9a7'
backup=Z/'qa/right_selection_before_r07c04_v7_adoption_20261017.json'
with backup.open('xb') as f:f.write(statepath.read_bytes())
t.setdefault('candidateHistory',[]).append(dict(candidate=t['candidate'],record=t['record'],geometryClosureRecord=t['geometryClosureRecord'],status='superseded_by_explicitly_adopted_root_v7_local_grain_repair'))
t.update(candidate=h['candidate'],record=h['record'],qaIndex=h['qaIndex'],geometryClosureRecord=pin(out),ownerAdoptionRecord=pin(out),internalGeometryClosurePassed=True,internalClosurePassed=False,formalAccepted=False,nativeReview33Count=33,materialStatus='PENDING_FULL_MATERIAL_REVIEW',pendingFindings=[dict(status='full_material_review_pending',note='The previously listed south grain cutoff is locally resolved in v7. Full-tile material and external seam acceptance remain pending.')],southAnchorChangedFromV6=True,anchorChangeNote=record['anchorNotice'])
state['updatedAtUtc']=now
for k,v in before['tiles'].items():
 if k!='r07_c04':assert state['tiles'][k]==v
statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(adoption=pin(out),state=pin(statepath),candidate=h['candidate'],geometryPassCount=33,formalAccepted=False)))

