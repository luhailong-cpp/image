from pathlib import Path
import json,hashlib,copy
from PIL import Image
import numpy as np
from datetime import datetime,timezone
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p);return dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def assertpin(v):assert pin(v['path'])['sha256']==v['sha256'],v
def save(p,d):
 assert not p.exists(),p;p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');return pin(p)
now=datetime.now(timezone.utc).isoformat()
# Final strict replay is parsed, not inferred from an apply exit status.
log=Z/'qa/r06_c04_cross_v7_final_strict_native_replay_20261016.log'
raw=log.read_text(encoding='utf-8-sig');dec=json.JSONDecoder();vals=[]
while raw.strip():
 raw=raw.lstrip();v,n=dec.raw_decode(raw);vals.append(v);raw=raw[n:]
policy=next(v['depthPolicy'] for v in vals if 'depthPolicy' in v)
strict=next(v for v in vals if v.get('status')=='base_native_coverage_reverified')
assert strict['proof']['fullNativeCoverage'] is True and strict['proof']['verifiedPixelCount']==16777216
strictPin=save(Z/'qa/r06_c04_cross_v7_final_strict_native_replay_20261016.json',dict(createdAtUtc=now,runner=pin(Z/'qa/run_native_with_cross_strict_memo_depth128_20261016.py'),rawLog=pin(log),depthPolicy=policy,result=strict,visualAcceptance=False))
# Preserve root's independently reported local review with all actual pins.
rr=read(Z/'qa/r06_c04_cross_v7_root_mask_review_notes_20261016.json')
for e in rr['items']:
 for a,b in [('combinedPath','combined'),('maskPath','mask'),('maskRecordPath','maskRecord')]:e[b]=pin(e.pop(a))
rr['createdAtUtc']=now
rootPin=save(Z/'qa/r06_c04_cross_v7_root_independent_mask_review_20261016.json',rr)
baseManifestPath=Z/'qa/connected-r05-r06-current-v5.manifest.json'
oldman=read(baseManifestPath);man=copy.deepcopy(oldman)
newpath=Z/'tiles/connected-r05-r06-cross-v7/r06_c04_internal-southmid-v1_4096.png';newrec=newpath.with_suffix('.native-repair.json')
for t in man['tiles']:
 if t['tileId']=='r06_c04':t['image']=pin(newpath);t['record']=pin(newrec)
 for k in ['image','record']:assertpin(t[k])
man.update(createdAtUtc=now,version='v7',supersedesManifest=pin(baseManifestPath),change='Two internal r06c04 grout repairs only; all other current tiles and all four outer115 edges retained.',independentGeometryAllPassed=False,materialStatus='PENDING',formalAccepted=False)
mp=Z/'qa/connected-r05-r06-current-v7.manifest.json';manifestPin=save(mp,man)
old={t['tileId']:np.asarray(Image.open(t['image']['path']).convert('RGB')) for t in oldman['tiles']}
cur={t['tileId']:np.asarray(Image.open(t['image']['path']).convert('RGB')) for t in man['tiles']}
masks=[];records=[]
for path in [Z/'tiles/connected-r05-r06-cross-v6/r06_c04_internal-westmid-v1_4096.native-repair.json',newrec]:
 r=read(path);assertpin(r['output']);assertpin(r['mask']);assertpin(r['repairSource'])
 mask=np.asarray(Image.open(r['mask']['path']))==255;rawimg=np.asarray(Image.open(r['repairSource']['path']).convert('RGB'))
 l,t,ri,b=r['cropBox']
 selected=np.zeros((4096,4096),bool);selected[t:b,l:ri]=mask
 masks.append(selected);records.append(pin(path))
 srcbase=np.asarray(Image.open(r['base']['image']['path']).convert('RGB'));expected=srcbase.copy();expected[t:b,l:ri][mask]=rawimg[mask]
 assert np.array_equal(expected,np.asarray(Image.open(r['output']['path']).convert('RGB')))
assert not np.any(masks[0]&masks[1])
changes=np.any(cur['r06_c04']!=old['r06_c04'],axis=2);assert not np.any(changes&~(masks[0]|masks[1]))
# Pin exact full native reviewed crops and verify current identities.
for e,box in zip(rr['items'],[[397,953,1651,2207],[1421,2842,2675,4096]]):
 l,t,r,b=box;assert np.array_equal(cur['r06_c04'][t:b,l:r],np.asarray(Image.open(e['combined']['path']).convert('RGB')))
 e['tileCropBoxHalfOpen']=box
edges={}
for k,a in cur.items():
 b=old[k];edges[k]={}
 for name,cut in [('north',(slice(0,115),slice(None))),('south',(slice(-115,None),slice(None))),('west',(slice(None),slice(0,115))),('east',(slice(None),slice(-115,None)))]:
  delta=int(np.count_nonzero(np.any(a[cut]!=b[cut],axis=2)));assert delta==0
  edges[k][name]=dict(changedPixelCount=delta,rgbBytesSha256=hashlib.sha256(a[cut].tobytes()).hexdigest())
 if k!='r06_c04':assert np.array_equal(a,b)
# Build per-native-crop geometry coverage by old exact reviews plus new two exact crop reviews.
coverage=read(Z/'qa/cross_v5_internal_coverage_delta_20261016/coverage_index.json')
prior=read(Z/'qa/cross_v5_internal_coverage_delta_20261016/connected_internal33_review.json')
fresh={(e['tileId'],e['name']):e for e in prior['newNativeViews']}
pendingName='top-bottom_r03-r04_x3072-4096_100pct.png'
tiles=[]
for t in coverage['tiles']:
 k=t['tileId'];items=[]
 for e in t['items']:
  l,u,r,b=e['tileCropBoxHalfOpen'];a=cur[k][u:b,l:r];baseline=old[k][u:b,l:r]
  diff=np.any(a!=baseline,axis=2);changed=int(diff.sum())
  status=fresh[(k,e['name'])]['geometry'] if (k,e['name']) in fresh else 'PASS'
  if changed:
   assert k=='r06_c04' and not np.any(diff&~(masks[0]|masks[1])[u:b,l:r])
   status='PASS'
  if k=='r06_c04' and e['name']==pendingName:
   assert changed==0;status='REPAIR_REQUIRED'
  items.append(dict(name=e['name'],tileCropBoxHalfOpen=e['tileCropBoxHalfOpen'],currentRGBBytesSha256=hashlib.sha256(a.tobytes()).hexdigest(),changedPixelsVsV5=changed,geometry=status,evidence='prior exact current-v5 review' if changed==0 else 'prior unchanged pixels plus two independently passed native1254 repair crops, all changed pixels inside their explicit masks',priorCoverage=e))
 count=sum(x['geometry']=='PASS' for x in items)
 tiles.append(dict(tileId=k,current=next(q for q in man['tiles'] if q['tileId']==k),internal33GeometryPassed=count,internal33Total=33,internalGeometryClosurePassed=count==33,materialStatus='PENDING',internalClosurePassed=False,fullVisualAccepted=False,formalAccepted=False,changedNativeCropCount=sum(x['changedPixelsVsV5']>0 for x in items),items=items))
assert [t['internal33GeometryPassed'] for t in tiles]==[33,33,33,32]
report=dict(createdAtUtc=now,manifest=manifestPin,priorManifest=pin(baseManifestPath),priorInternalCoverage=pin(Z/'qa/cross_v5_internal_coverage_delta_20261016/connected_internal33_review.json'),sourceApplications=records,rootIndependentMaskReview=rootPin,strictFinalReplay=strictPin,outer115Unchanged=edges,changedTilePixels=int(changes.sum()),tiles=tiles,sharedExternalSeams=dict(geometryPassed=17,total=17,reusedFrom=pin(Z/'qa/r05r06_v5_geometry_closure_material_pending_20261013.json'),basis='All tile external 240-pixel bands remain unchanged; current17 shared geometry proof retained.'),attemptAudit=pin(Z/'qa/r06_c04_internal_attempt_audit_20261016/attempt_decisions.json'),remainingGeometryIssue=dict(tileId='r06_c04',tileBoxHalfOpen=[3512,3022,3722,3152],nearTileXY=[3630,3072],crop=pendingName,status='REPAIR_REQUIRED_DEFERRED_AFTER_TWO_ATTEMPTS',note='Existing upper-left paving outline of lower large stone has a missing segment; no third native attempt this batch.'),internalGeometryPassed=131,internalStandardTotal=132,materialStatus='PENDING',fullVisualAccepted=False,formalAccepted=False)
for k in cur:
 a=cur[k];b=old[k]
 assert np.array_equal(a[:240],b[:240]) and np.array_equal(a[-240:],b[-240:]) and np.array_equal(a[:,:240],b[:,:240]) and np.array_equal(a[:,-240:],b[:,-240:])
rp=Z/'qa/r05r06_v7_internal_delta_closure_material_pending_20261016.json'
reportPin=save(rp,report)
print(json.dumps(dict(manifest=manifestPin,closure=reportPin,rootReview=rootPin,strict=strictPin,states=[{k:v for k,v in t.items() if k not in ['items','current']} for t in tiles]),ensure_ascii=False))

