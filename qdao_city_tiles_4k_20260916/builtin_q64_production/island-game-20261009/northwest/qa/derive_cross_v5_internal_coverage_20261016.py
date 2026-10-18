from pathlib import Path
import json,hashlib,numpy as np,datetime
from PIL import Image
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
pin=lambda f:sha(f['path'])==f['sha256']
mp=Z/'qa/connected-r05-r06-current-v5.manifest.json';manifest=read(mp)
curr={};offsets={'r05_c03':(0,0),'r05_c04':(4096,0),'r06_c03':(0,4096),'r06_c04':(4096,4096)}
for t in manifest['tiles']:
 assert pin(t['image']) and pin(t['record']);curr[t['tileId']]=np.array(Image.open(t['image']['path']).convert('RGB'))
covered={k:np.zeros((4096,4096),bool) for k in curr};regions=[]
def add_region(ref,box,evidence,originY=0):
 assert pin(ref)
 original=np.array(Image.open(ref['path']).convert('RGB'))
 b=[box[0],box[1]+originY,box[2],box[3]+originY]
 assert original.shape[:2]==(b[3]-b[1],b[2]-b[0])
 accepted=[]
 for tid,(ox,oy) in offsets.items():
  x0,y0=max(b[0],ox),max(b[1],oy);x1,y1=min(b[2],ox+4096),min(b[3],oy+4096)
  if x0>=x1 or y0>=y1:continue
  cut=original[y0-b[1]:y1-b[1],x0-b[0]:x1-b[0]]
  if np.array_equal(cut,curr[tid][y0-oy:y1-oy,x0-ox:x1-ox]):
   covered[tid][y0-oy:y1-oy,x0-ox:x1-ox]=True;accepted.append(dict(tileId=tid,tileBox=[x0-ox,y0-oy,x1-ox,y1-oy]))
 if accepted:regions.append(dict(image=ref,clusterBox=b,review=info(evidence),exactCurrentIntersections=accepted))
cp=Z/'qa/r05r06_v5_geometry_closure_material_pending_20261013.json';closure=read(cp)
for q in closure['ownerItems']+closure['ownerBoundaryMargins']:
 assert q['geometry']=='PASS';add_region(q['output'],q['box'],cp)
ip=Z/'qa/r05r06_v5_independent_native_geometry_review_20261013.json'
for q in read(ip)['fullRepairCrops']:
 assert q['geometry']=='PASS';add_region(q['image'],q['box'],ip)
p4=Z/'qa/connected-r04-r05-final-v1/closure.json';c4=read(p4)
for q in c4['checks']+c4['wholeObjectNativeCrops']:
 assert q['visualPassed'];add_region(q['output'],q['box'],p4,-4096)
for q in c4['repairs']:
 assert q['nativeVisualPassed']
 p=Z/'guides'/f"{q['stem']}.input.json"
 add_region(q['combinedNativeImage'],read(p)['cropBox'],p4,-4096)
spec=[
('r05_c03','tiles/r05_c03_candidate-v8_4096.png','qa/r05_c03_v8_internal_closure/qa_index.json','qa/r05_c03_v8_internal_closure/review.json'),
('r05_c04','tiles/r05_c04_candidate-v4_4096.png','qa/r05_c04_v4_internal_closure/qa_index.json','qa/r05_c04_v4_internal_closure/visual_review.json'),
('r06_c03','tiles/r06_c03_candidate-v7_4096.png','qa/r06_c03_v7_internal_closure_20261012/qa_index.json','qa/r06_c03_v7_internal_closure_20261012/visual_review.json'),
('r06_c04','tiles/r06_c04_candidate-v1_4096.png','qa/assembly_r06_c04_candidate-v1_4096/qa_index.json','qa/r06_c04_v1_independent_root_vertical12_review_20261012.json')
]
O=Z/'qa/cross_v5_internal_coverage_delta_20261016';O.mkdir(exist_ok=False)
results=[]
for tid,bp,qp,rp in spec:
 prior=read(Z/rp);index=read(Z/qp);qs=index.get('seamAndJunctionCrops',index.get('qa',{}).get('seamAndJunctionCrops'))
 assert len(qs)==33;baseline=np.array(Image.open(Z/bp).convert('RGB'))
 passnames=None
 if tid=='r05_c03':assert prior['internalVisualAccepted']
 if tid=='r05_c04':assert prior['qa']['status']=='visual_pass_all33'
 if tid=='r06_c03':assert prior['nativeSeamGeometryPassed']==33
 if tid=='r06_c04':passnames={Path(q['path']).name for q in prior['items'] if q['independentRootStatus'] in ['PASS','GEOMETRY_PASS_MATERIAL_PENDING']}
 items=[]
 for q in qs:
  assert pin(q);box=q['tileCropBoxHalfOpen'];x0,y0,x1,y1=box
  old=np.array(Image.open(q['path']).convert('RGB'));assert np.array_equal(old,baseline[y0:y1,x0:x1])
  new=curr[tid][y0:y1,x0:x1];diff=np.any(old!=new,axis=2);cover=covered[tid][y0:y1,x0:x1]
  passed=(passnames is None or Path(q['path']).name in passnames)
  need=np.any(diff & ~cover) if passed else not cover.all()
  status='PENDING_NEW_NATIVE_VIEW' if need else ('PASS_UNCHANGED_PRIOR' if not diff.any() and passed else 'PASS_PRIOR_PLUS_EXACT_CURRENT_REVIEW_COVERAGE' if passed else 'PASS_EXACT_CURRENT_REVIEW_COVERAGE')
  output=dict(path=q['path'],sha256=q['sha256'])
  if need:
   out=O/f"{tid}__{Path(q['path']).name}";Image.fromarray(new).save(out);output=info(out)
  items.append(dict(name=Path(q['path']).name,tileCropBoxHalfOpen=box,dimensions=q['dimensions'],priorCrop=dict(path=q['path'],sha256=q['sha256']),priorGeometryPass=passed,changedPixels=int(diff.sum()),changedPixelsAlreadyReviewed=int((diff & cover).sum()),changedPixelsNotAlreadyReviewed=int((diff & ~cover).sum()),wholeCropAlreadyReviewed=bool(cover.all()),geometry=status,output=output))
 results.append(dict(tileId=tid,current=next(t for t in manifest['tiles'] if t['tileId']==tid),baseline=info(Z/bp),priorIndex=info(Z/qp),priorReview=info(Z/rp),items=items,pending=sum(x['geometry']=='PENDING_NEW_NATIVE_VIEW' for x in items),reusePassed=sum(x['geometry']!='PENDING_NEW_NATIVE_VIEW' for x in items)))
out=O/'coverage_index.json';data=dict(createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),operation='Native internal33 coverage on exact current cross v5; image output only for missing visual coverage',manifest=info(mp),coverageRule='A previously passed internal crop may be reused when all changed pixels are inside existing full-native passed regions verified identical to current pixels. If the baseline was not passed, the entire crop needs current passed coverage or a new native view.',existingCurrentPassedRegions=regions,tiles=results,materialStatus='PENDING',formalAccepted=False)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(index=info(out),counts=[dict(tileId=t['tileId'],pending=t['pending'],reused=t['reusePassed']) for t in results],newCrops=[x['output']['path'] for t in results for x in t['items'] if x['geometry']=='PENDING_NEW_NATIVE_VIEW'])))

