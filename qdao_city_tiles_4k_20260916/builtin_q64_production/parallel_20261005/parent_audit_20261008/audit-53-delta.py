from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageChops
import sys,json,hashlib,numpy as np
ROOT=Path('D:/work/image'); P=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005'; A=P/'parent_audit_20261008'
sys.path.insert(0,str(P/'penglai_mid_autumn/tools/deps'))
import cv2
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checked={}
def bind(v):
 p=Path(v.get('file') or v['path']);h=sha(p);assert h==v['sha256'],str(p);checked[p.as_posix()]=h;return p
def walk(v):
 if isinstance(v,list):
  for x in v:walk(x)
 elif isinstance(v,dict):
  if 'sha256' in v and isinstance(v.get('file') or v.get('path'),str):bind(v)
  for x in v.values():
   if isinstance(x,(dict,list)):walk(x)
now=datetime.now(timezone.utc).isoformat();I=read(A/'verified-current-index.json');assert I['summary']['completePixelCandidateCount']==51
# Existing detailed source/replay/QA audit is reused only with unchanged outputs and evidence.
la=read(A/'donghai-lantern-c13-source-audit.json');L=P/'donghai_lantern';ls=read(L/'current-selection.json');lr=read(L/'current-candidates.json');lan=[]
for k in ['manifestChain','nativeSources','ownerScopedReviews']:walk(la[k])
for t in la['tiles']:
 walk(t['core']);walk(t['generationRecord']);s=next(x for x in ls['candidates'] if x['tile']==t['tileId']);r=next(x for x in lr['candidates'] if x['tile']==t['tileId'])
 assert s['sha256']==r['sha256']==t['core']['sha256'];assert Path(s['file']).resolve()==Path(t['core']['path']).resolve();bind(s)
 lan.append(dict(appearance='donghai_lantern',tileId=t['tileId'],core=t['core'],generationRecord=t['generationRecord'],selectionSource=ref(L/'current-selection.json'),registry=ref(L/'current-candidates.json'),selectionSnapshot=s,priorSourceAndQAAudit=ref(A/'donghai-lantern-c13-source-audit.json'),unchangedPriorAuditInherited=True,qaEvidence=[r['review'] for r in la['ownerScopedReviews']],qaStatus=s['qaStatus'],remainingLimitations=la['remainingLimitations'],sourceCount=16,formalAccepted=False))
# New Mid-Autumn full coordinate: reconstruct only stored bounded registration, never generate or modify child files.
T=P/'penglai_mid_autumn/r09_c14';m=read(T/'output/manifest.json');walk(m);di=read(P/'penglai_mid_autumn/delivery-index.json');s=next(x for x in di['tiles'] if x['id']=='r09_c14');assert s['completePixelCoverage'];bind(s);assert s['sha256']==m['sha256'];g=read(str(m['file'])+'.generation.json');walk(g)
canvas=np.zeros((4326,4326,3),np.uint8);cov=np.zeros((4326,4326),bool)
for seed in m['seedRegions']:
 src=Image.open(m['neighbors'][seed['role']]['file']).convert('RGB').crop(seed['sourceCropLTRB']);x,y=seed['canvasPasteXY'];arr=np.asarray(src);canvas[y:y+arr.shape[0],x:x+arr.shape[1]]=arr;cov[y:y+arr.shape[0],x:x+arr.shape[1]]=True
native=[]
yy,xx=np.mgrid[0:1254,0:1254].astype(np.float32)
for q in m['patches']:
 n=np.asarray(Image.open(bind(q['source'])).convert('RGB'));assert n.shape==(1254,1254,3);ng=read(bind(q['generation']));assert ng['actualModel'] is None and ng['actualQuality'] is None;bind(ng)
 walk(ng['references']);assert sha(ng['prompt'])==ng['promptSha256'];assert Path(ng['prompt']).read_text(encoding='utf-8-sig').strip()==ng['submittedParameters']['prompt'].strip()
 e=ng['evidence'];host=Path(e['sourceOutputPath']);assert e['sourceOutputSha256']==q['source']['sha256'];assert not host.exists() or sha(host)==q['source']['sha256']
 fields=q['fields'];mask=np.asarray(Image.open(fields['mask']['file']).convert('L'));assert set(np.unique(mask))<={0,255};own=mask>0;flow=np.load(fields['flow']['file']);tone=np.load(fields['colorCorrection']['file']);assert float(np.linalg.norm(flow,axis=2).max())<=6.00001
 aligned=cv2.remap(n,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE);matched=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8);zero=(flow==0).all(2)&(tone==0).all(2);matched[zero]=n[zero]
 x,y=q['canvasXY'];view=canvas[y:y+1254,x:x+1254];view[own]=matched[own];cov[y:y+1254,x:x+1254]=True
 native.append({'source':q['source'],'generation':q['generation'],'actualModel':None,'actualQuality':None,'nativePixels':[1254,1254],'maximumDisplacement':float(np.linalg.norm(flow,axis=2).max())})
core=np.asarray(Image.open(m['file']).convert('RGB'));assert core.shape==(4096,4096,3);assert np.array_equal(core,canvas[115:4211,115:4211]);assert cov[115:4211,115:4211].all()
qa=[]
for name in ['root-review.json','horizontal-review.json','external-review.json']:
 f=T/'qa'/name;review=read(f);walk(review);assert review['candidate']['sha256']==m['sha256'];items=[]
 for item in review['items']:
  assert item['actuallyViewed'];p=Path(item['file']);qg=read(str(p)+'.generation.json');walk(qg);assert any(v['sha256']==m['sha256'] for v in qg.get('sources',qg.get('derivedFrom',[]))) or name=='external-review.json'
  # Hash bindings preserve the original reviewer verdict, including known failures.
  items.append({'image':ref(p),'generation':ref(str(p)+'.generation.json'),'ownerActuallyViewed':True,'ownerVerdict':item['verdict']})
 qa.append({'review':ref(f),'items':items,'independentVisualReinspection':False})
peng=dict(appearance='penglai_mid_autumn',tileId='r09_c14',core=ref(m['file']),generationRecord=ref(str(m['file'])+'.generation.json'),selectionSource=ref(P/'penglai_mid_autumn/delivery-index.json'),selectionSnapshot=s,sourceManifest=ref(T/'output/manifest.json'),sourceCount=16,nativeSources=native,storedFieldAssemblyPixelExact=True,fullyCovered=True,qaEvidence=[q['review'] for q in qa],qaBindings=qa,qaStatus='complete_native_pixels; internal scoped QA passed; west foliage seam failed and under active repair',remainingLimitations=['West foliage silhouettes explicitly fail the current native shared-edge review; active local AI repair is not yet selected.','North, east and south neighbors unavailable; whole tile, city and client not accepted.'],formalAccepted=False)
tp=P/'tianyong_festival/progress.json';progress=read(tp)
proof={'createdAtUtc':now,'baseParentIndex':ref(A/'verified-current-index.json'),'status':'two_new_coordinates_and_one_existing_coordinate_update_source_bound','changes':lan+[peng],'newCoordinateCount':2,'sameCoordinateUpdateCount':1,'expectedTotal':53,'checkedFiles':checked,'excludedPartial':{'appearance':'tianyong_festival','tile':progress['activeTile'],'coverageFraction':progress['tileCoverageFraction'],'progress':ref(tp)},'parentOverlayPreserved':ref(A/'parent-repair-current-overlay-v3.json'),'formalAcceptedCount':0,'childModified':False}
dest=A/'selected-53-source-audit.json';dump(dest,proof);print(json.dumps({'audit':ref(dest),'newCoordinates':2,'sameCoordinateUpdates':1,'expectedTotal':53,'checkedFileCount':len(checked)}))
