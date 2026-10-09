"""One approved joint repair; default validation only. No deletion or historical rewrites."""
from pathlib import Path
import argparse,copy,datetime,hashlib,io,json,sys
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent;W=R/'r10_c11';C=R/'r10_c13';V=D/'stage2-bounded'
sys.path.insert(0,str(R/'tools/multi_edge'));import engine
OLD='3ca7d1d8b5711e0b8d315fe9f3c0a4fe5f032ba3dc2555edfa9854eca6dc2be2'
NEW='4dc21b33dea8fa9a35e2c5a556e8495ecc9cda3e173457fb060682dd1b4a438b'
OLDW='e5029514592962bfbf3e5a565ac2a9d0de37d91e4f9bc7986fc2354ed5d5f9f3'
NEWW='96f4fb8808feedc00234386fb61d273436636d15ab1bb8549908ffb52634bebb'
E=T/'output/r10_c12.png';P=W/'native/p14.png';CP=C/'output/r10_c13-candidate.png'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(Path(p).read_bytes())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return dict(file=str(p),sha256=sha(p))
def arr(p):return np.asarray(Image.open(p).convert('RGB'))
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def jbytes(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(jbytes(v))
def png(im):
 b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def norm(p):return str(Path(p).resolve()).lower()
def replace_current_refs(v):
 if isinstance(v,dict):
  if norm(v.get('file','__none__'))==norm(E) and v.get('sha256')==OLD:v['sha256']=NEW
  for k,x in v.items():
   if k not in ['historical','sourceAtFreeze','frozenAt','sourceSha256AtFreeze']:replace_current_refs(x)
 elif isinstance(v,list):
  for x in v:replace_current_refs(x)
def verify_refs(v,skip=frozenset()):
 if isinstance(v,dict):
  if 'file' in v and 'sha256' in v and str(v['file']) not in skip:
   p=Path(v['file']);require(p.exists() and sha(p)==v['sha256'],'Changed/missing recorded reference '+str(p))
  for x in v.values():verify_refs(x,skip)
 elif isinstance(v,list):
  for x in v:verify_refs(x,skip)
def build():
 require(sha(E)==OLD and sha(P)==OLDW,'Canonical image changed or migration already applied')
 require(sha(V/'r10_c12-proposal.png')==NEW and sha(V/'p14-proposal.png')==NEWW,'Wrong approved proposal')
 a=read(D/'root-joint-promotion-authorization.json');require(a['localVisualPass'] and len(a['items'])==15,'Missing root actual review authorization');verify_refs(a)
 s=read(D/'promotion-standard-review.json');require(s['scopedPass'] and len(s['items'])==27,'Missing 27 standard reviews');verify_refs(s)
 for x in s['items']:require(x['actuallyViewed'] and x['nativeScale']==1 and x['verdict'] in ['scoped_pass','current_pixels_inspected_neighbor_unverified'],'Unreviewed standard QA')
 legacy=read(V/'source-reuse-proof.json');verify_refs(legacy)
 verify_refs(read(V/'diagnostic.json'));verify_refs(read(D/'stage1-bounded/diagnostic.json'))
 require(len(list((W/'native').glob('p[1-4][1-4].png')))==1,'Downstream p14 consumer exists; explicit migration must be expanded')
 old,new=arr(E),arr(V/'r10_c12-proposal.png');wp=arr(V/'p14-proposal.png');pl=read(W/'plan.json');n=Path(pl['northEastCandidate']);nw=Path(pl['northCandidate'])
 require(pl['eastCandidateSha256']==OLD,'Plan no longer at expected E source')
 require(sha(n)==pl['northEastCandidateSha256'] and sha(nw)==pl['northCandidateSha256'],'True N/NE changed')
 mask=np.any(old!=new,axis=2);ys,xs=np.where(mask);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 require(bbox==[0,0,1412,316],'Unexpected approved E change bounds')
 require(np.array_equal(wp[:115,:1139],arr(nw)[3981:,2957:]),'P14 true N support mismatch')
 require(np.array_equal(wp[:115,1139:],arr(n)[3981:,:115]),'P14 true NE mismatch')
 require(np.array_equal(wp[115:,1139:],new[:1139,:115]),'P14 true E mismatch')
 crop_proof=[]
 for width in [115,320,512]:
  b=[4096-width,0,4096,4096];u=old[:,4096-width:];v=new[:,4096-width:];require(np.array_equal(u,v),'C13 consumed strip changed')
  crop_proof.append(dict(cropLTRB=b,oldPixelSha256=digest(u.tobytes()),newPixelSha256=digest(v.tobytes()),exactPixels=True))
 index=read(V/'standard-qa/index.json');by={Path(x['file']).stem:x for x in index['items']};before={name:im for name,im,op,roles in engine.qa_images(Image.fromarray(old),{'north':Image.open(n).convert('RGB')},'NW',256)}
 current=list(engine.qa_images(Image.fromarray(new),{'north':Image.open(n).convert('RGB')},'NW',256));checks=[]
 for name,im,op,roles in current:
  rec=by[name];require(sha(rec['file'])==rec['sha256'] and np.array_equal(np.asarray(im),arr(rec['file'])),'C12 QA is stale '+name)
  same=np.array_equal(np.asarray(im),np.asarray(before[name]));require(same==rec['identicalToOldCanonicalReconstruction'],'Reuse proof changed '+name)
  checks.append(dict(name=name,sha256=rec['sha256'],matchesCurrentReconstruction=True,identicalToOldCanonical=same))
 require(len(checks)==27 and sum(not x['identicalToOldCanonical'] for x in checks)==6,'Wrong C12 QA delta count')
 cp=read(C/'plan.json');neighbors={role:Image.open(cp[key]).convert('RGB') for role,key in [('north','northCandidate'),('west','westCandidate'),('northwest','northWestCandidate')]};neighbors['west']=Image.fromarray(new)
 c13qa=[]
 for name,im,op,roles in engine.qa_images(Image.open(CP).convert('RGB'),neighbors,'NW',256):
  if name.startswith('four-tile-'):continue # Legacy corner is reproduced below at its recorded512 crop per tile.
  name=name.replace('return-plus256','return-256');p=C/'qa/native-candidate'/(name+'.png');require(np.array_equal(np.asarray(im),arr(p)),'C13 current QA changes '+name);c13qa.append(ref(p))
 require(len(c13qa)==27,'Wrong C13 QA coverage')
 corner=C/'qa/four-tile-corner.png';m=read(str(corner)+'.generation.json');q=Image.new('RGB',(1024,1024))
 for src,box,xy in zip(m['derivedFrom'],m['operation']['sourceCropLTRB'],[(0,0),(512,0),(0,512),(512,512)]):
  im=Image.fromarray(new) if norm(src['file'])==norm(E) else Image.open(src['file']).convert('RGB');q.paste(im.crop(box),xy)
 require(np.array_equal(np.asarray(q),arr(corner)),'C13 true corner changed');c13qa.append(ref(corner))
 for p in sorted((C/'qa/external-details').glob('west-unrotated-*.png')):
  rec=read(str(p)+'.generation.json');q=Image.new('RGB',tuple(rec['pixels']))
  for src in rec['sources']:
   im=Image.fromarray(new) if norm(src['file'])==norm(E) else Image.open(src['file']).convert('RGB');q.paste(im.crop(src['cropLTRB']),src['pasteXY'])
  require(np.array_equal(np.asarray(q),arr(p)),'C13 unrotated supplement changed');c13qa.append(ref(p))
 immutable=[R/'native_patch.py',R/'native_assemble.py',C/'frozen-neighbors.json',C/'output/native-assembly.json',W/'native/p14.request.json',W/'native/p14.call.json',W/'native/p14.prompt.txt',W/'native/p14-context.png',W/'native/p14-edit-target.png']
 immutable+=list(T.glob('assembly*/**/*.json'))
 immutable+=list((W/'native').glob('p14-*.png.generation.json'))
 immutable+=list((C/'native').glob('*.request.json'))
 immutable+=list(C.rglob('*.png'))
 protected={str(p):sha(p) for p in immutable if p.exists()};protected[str(n)]=sha(n);protected[str(nw)]=sha(nw)
 migration_path=D/'applied-source-migration.json';stamp=now();pending={};images={}
 def put(p,v):pending[p]=v
 proof=dict(createdAt=stamp,kind='explicit_root_authorized_source_version_migration',authorization=ref(D/'root-joint-promotion-authorization.json'),oldEast=dict(file=str(E),sha256=OLD,versionReplacedAtSamePath=True),newEast=dict(file=str(E),sha256=NEW),oldP14=dict(file=str(P),sha256=OLDW,versionReplacedAtSamePath=True),newP14=dict(file=str(P),sha256=NEWW),approvedProposals=[ref(V/'r10_c12-proposal.png'),ref(V/'p14-proposal.png')],oldSourceImmutableHistoryPreserved=True,c12ChangedBBoxLTRB=bbox,c13ConsumedPixels=crop_proof,c13ExactReconstructedQA=c13qa,c12Reconstruction=checks,p14KnownNENEExact=True,p14SecondBoundedRegistrationPixelIdentical=legacy['p14ProductionRegistrationPixelIdentical'],frozenAtRecordsUnchanged=True,noAutomaticVisualApproval=True,formalAccepted=False,rootProgressWrites=False)
 put(migration_path,proof);mref=dict(file=str(migration_path),sha256=digest(jbytes(proof)))
 def meta(p,im,sources,op):return dict(file=str(p),sha256=digest(png(im)),createdAt=stamp,width=im.width,height=im.height,format='PNG',derivedFrom=sources,operation=op,sourceVersionMigration=mref,productionPixels=False)
 images[E]=(V/'r10_c12-proposal.png').read_bytes();images[P]=(V/'p14-proposal.png').read_bytes()
 for dst,proposal,oldhash in [(E,V/'r10_c12-proposal.png',OLD),(P,V/'p14-proposal.png',OLDW)]:
  oldrec=read(str(dst)+'.generation.json');im=Image.open(proposal);g=dict(file=str(dst),sha256=sha(proposal),createdAt=stamp,width=im.width,height=im.height,format='PNG',derivedFrom=[dict(**ref(proposal),generation=ref(str(proposal)+'.generation.json'))],operation=dict(kind='approved_native_joint_AI_repair_exact_copy',sourceVersionMigration=mref,sourceUpscaling=False,resizedAfterGeneration=False,nativePixelScale=1),actualModel=None,actualQuality=None,modelEvidence='Derivative of builtin AI repairs; original source records retain unknown actual model/quality.',previousCurrentGeneration=dict(file=str(D/'text-history'/Path(str(dst)+'.generation.json').relative_to(R)),sha256=sha(str(dst)+'.generation.json'),imageSha256=oldhash),formalAccepted=False,sourceUpscaled=False,resizedAfterGeneration=False)
  if dst==P:g.update(nativeWorkflow=oldrec['nativeWorkflow'],globalPatchXYWH=oldrec['globalPatchXYWH'],status='native_joint_repair_passed_available_N_E_NE_and_local_returns_pending_full_tile_QA',productionPixels=True,originalImagegenRequest=ref(W/'native/p14.request.json'),sourceVersionMigration=mref)
  else:g.update(productionPixels=True,currentGameImage=str(E),scopedLocalSeamsPassed=True)
  put(Path(str(dst)+'.generation.json'),g)
 # Live E crop refreshed. Original request edit-target/context remain historical and byte-identical.
 for dst,im,op in [(W/'references/east-native115.png',Image.fromarray(new).crop((0,0,115,4096)),dict(kind='exact_native_context_crop',sourceCropLTRB=[0,0,115,4096],scale=1)),(W/'references/east-preview.png',Image.fromarray(new).resize((1254,1254),Image.Resampling.LANCZOS),dict(kind='downsampled_actual_neighbor_preview_only',scale=1254/4096))]:
  images[dst]=png(im);put(Path(str(dst)+'.generation.json'),meta(dst,im,[dict(file=str(E),sha256=NEW)],op))
 for dst in [W/'references/east-p44-round-post-native.png',W/'references/east-p44-round-post-native-focus.png']:
  gp=Path(str(dst)+'.generation.json');rec=read(gp);box=rec['operation']['sourceCropLTRB'];require(np.array_equal(np.asarray(Image.fromarray(new).crop(box)),arr(dst)),'P44 reference changed unexpectedly');replace_current_refs(rec);rec['sourceVersionMigration']=mref;rec['exactSamePixelsFromNewSource']=True;put(gp,rec)
 ctx=Image.new('RGBA',(1254,1254),(0,0,0,0));regions=copy.deepcopy(read(str(W/'native/p14-context.png')+'.generation.json')['operation']['regions'])
 for src in regions:
  if norm(src['file'])==norm(E):src['sha256']=NEW
  im=Image.fromarray(new).convert('RGBA') if norm(src['file'])==norm(E) else Image.open(src['file']).convert('RGBA');ctx.paste(im.crop(src['cropLTRB']),src['pasteXY'])
 cpath=W/'native/p14-current-context.png';require(not cpath.exists(),'Current migrated context exists');images[cpath]=png(ctx);put(Path(str(cpath)+'.generation.json'),meta(cpath,ctx,[dict(file=str(E),sha256=NEW),ref(nw),ref(n)],dict(kind='exact_current_support_context_after_source_migration',regions=regions,originalAIRequestInputsUnchanged=True)))
 pl['eastCandidateSha256']=NEW;pl['sourceVersionMigration']=mref;pl['currentNativeContext']=dict(p14=dict(file=str(cpath),sha256=digest(images[cpath])));put(W/'plan.json',pl)
 put(W/'qa/p14-joint-repair-current.json',dict(reviewedAt=stamp,candidate=dict(file=str(P),sha256=NEWW),originalActualViews=ref(V/'visual-review.json'),rootActualViews=ref(D/'root-joint-promotion-authorization.json'),sourceVersionMigration=mref,localNENECornerAndReturnsPassed=True,fullTileQAComplete=False,formalAccepted=False))
 # Replace current C12 QA pointer set, preserving legacy QA files and text reports.
 qa_dir=T/'qa/source-joint-current';require(not qa_dir.exists(),'Current joint QA directory exists');qa_items=[]
 standard_by={Path(x['file']).stem:x for x in s['items']}
 for name,im,op,roles in current:
  dst=qa_dir/(name+'.png');data=(V/'standard-qa'/(name+'.png')).read_bytes();images[dst]=data
  item=copy.deepcopy(standard_by[name]);item['originalViewedFile']=item['file'];item['file']=str(dst);item['copiedWithoutPixelChange']=True
  item['sources']=[dict(file=str(E),sha256=NEW)]+([ref(n)] if 'north' in roles else []);item['operation']=op;item['sourceVersionMigration']=mref;qa_items.append(item);put(Path(str(dst)+'.generation.json'),item)
 review=dict(reviewedAt=stamp,candidate=dict(file=str(E),sha256=NEW),items=qa_items,rootJointReview=ref(D/'root-joint-promotion-authorization.json'),originalJointReview=ref(V/'visual-review.json'),standardReview=ref(D/'promotion-standard-review.json'),sourceVersionMigration=mref,scopedLocalSeamsPassed=True,scope='all internal seams/returns/junctions plus full northern actual shared edge/return; partial western p14 joint only',fullExternalSeams={'north':True,'west':False,'east':False,'south':False},formalAccepted=False,navigationVerified=False,clientVerified=False,issues=[])
 put(T/'qa/final-local-review.json',review)
 manifest=read(T/'output/manifest.json');manifest.update(sha256=NEW,updatedAt=stamp,status='scoped_local_seams_passed_after_joint_source_repair',scopedLocalSeamsPassed=True,qa=qa_items,sourceVersionMigration=mref,formalAccepted=False,navigationVerified=False,clientVerified=False)
 manifest['previousOperationRecord']=dict(file=str(D/'text-history/r10_c12/output/manifest.json'),sha256=sha(T/'output/manifest.json'))
 manifest['operation']=dict(kind='approved_joint_source_repair_after_original_native_assembly',derivedProposal=ref(V/'r10_c12-proposal.png'),diagnostics=[ref(D/'stage1-bounded/diagnostic.json'),ref(V/'diagnostic.json')],limitedNumericalRegistration=dict(maxFlow=6,maxTone=18,returnDepth=256,minJacobian=.25),localAICompositeReturnDepth=320,changedBBoxLTRB=bbox,sourceVersionMigration=mref)
 manifest['northScopedQA']=dict(result='passed_after_joint_source_repair',scope='Full4096 shared edge, native return256 and local return320 actually viewed',oldNeighborUnchanged=True,review=dict(file=str(T/'qa/final-local-review.json'),sha256=digest(jbytes(review))))
 manifest['internalScopedQA']['currentRevalidation']=dict(file=str(T/'qa/final-local-review.json'),sha256=digest(jbytes(review)))
 manifest['fullExternalSeams']={'north':True,'west':False,'east':False,'south':False};manifest['sourceScopeReopened']['resolvedBy']=mref
 put(T/'output/manifest.json',manifest)
 progress=read(T/'progress.json');progress.update(updatedAt=stamp,stage=manifest['status'],sha256=NEW,scopedLocalSeamsPassed=True,sourceVersionMigration=mref);put(T/'progress.json',progress)
 if (T/'current-preview.png').exists():
  dst=T/'current-preview.png';size=Image.open(dst).size;im=Image.fromarray(new).resize(size,Image.Resampling.LANCZOS);images[dst]=png(im);put(Path(str(dst)+'.generation.json'),meta(dst,im,[dict(file=str(E),sha256=NEW)],dict(kind='current_candidate_preview_only',scale=size[0]/4096,notForVisualAcceptance=True)))
 # C13 production/QA PNGs are immutable; only live source/reuse metadata changes.
 cp['westCandidateSha256']=NEW
 if 'candidateSources' in cp:replace_current_refs(cp['candidateSources'])
 cp['sourceVersionMigration']=mref;put(C/'plan.json',cp)
 rv=read(C/'neighbor-revalidation.json')
 for x in rv:
  if norm(x['source'])==norm(E):x.update(currentSourceSha256=NEW,checkedAt=stamp,sourceVersionMigration=mref)
 put(C/'neighbor-revalidation.json',rv)
 cm=read(C/'output/manifest.json');replace_current_refs(cm['neighbors']);replace_current_refs(cm.get('qa',[]));cm['plan']['sha256']=digest(jbytes(cp));cm['sourceVersionMigration']=mref;cm['neighborRevalidation']=dict(file=str(C/'neighbor-revalidation.json'),sha256=digest(jbytes(rv)));put(C/'output/manifest.json',cm)
 # The explicit source migration is evidence for exact retained QA; do not claim new actual views.
 for gp in list((C/'qa').rglob('*.png.generation.json')):
  rec=read(gp)
  if OLD not in json.dumps(rec):continue
  replace_current_refs(rec);rec['sourceVersionMigration']=mref;rec['exactPixelsUnchangedUnderCurrentSource']=True;rec['newActualViewPerformed']=False;put(gp,rec)
 er=read(C/'qa/external-review.json');replace_current_refs(er['neighbors']);er['sourceVersionMigration']=mref;er['newActualViewPerformed']=False;er['reuseReason']='All27 standard sheets, true four-tile corner and4 western supplement images reproduce exactly under new W source. Original candidate, image SHA and actually-viewed times remain unchanged.';put(C/'qa/external-review.json',er)
 cr=read(C/'qa/final-local-review.json');cr['sourceVersionMigration']=mref
 for x in cr.get('independentReviews',[]):
  if norm(x['file'])==norm(C/'qa/external-review.json'):x['sha256']=digest(jbytes(er))
 put(C/'qa/final-local-review.json',cr)
 # Repoint current references to changed review metadata; original assembly is never touched.
 def refresh_doc_refs(obj):
  if isinstance(obj,dict):
   if 'file' in obj and 'sha256' in obj:
    for q,v in pending.items():
     if q in [C/'qa/external-review.json',C/'qa/final-local-review.json'] and norm(obj['file'])==norm(q):obj['sha256']=digest(jbytes(v))
   for val in obj.values():refresh_doc_refs(val)
  elif isinstance(obj,list):
   for val in obj:refresh_doc_refs(val)
 refresh_doc_refs(cm)
 for dst in pending:
  require(dst.suffix=='.json','Only JSON metadata supported')
  require(dst.is_relative_to(T) or dst.is_relative_to(W) or dst.is_relative_to(C),'Out-of-scope write')
 for dst in images:require(not dst.is_relative_to(C),'C13 PNG mutation forbidden')
 return dict(pending=pending,images=images,protected=protected,proof=proof,checks=checks)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--final-c12-sha');ap.add_argument('--final-p14-sha');args=ap.parse_args()
 work=build();pending=work['pending'];images=work['images'];allpaths=list(pending)+list(images);baseline={str(p):sha(p) if p.exists() else None for p in allpaths};require(len(baseline)==len(allpaths),'Duplicate write targets')
 summary=dict(validatedAt=now(),script=ref(Path(__file__)),approvedCandidates=[dict(file=str(E),sha256=NEW),dict(file=str(P),sha256=NEWW)],plannedMetadataWrites=len(pending),plannedImageWrites=len(images),before=baseline,protected=work['protected'],c12StandardQA=work['checks'],writesPerformed=False,mode='validate_only')
 if not args.apply:
  write(D/'migration-preflight.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['before','protected','c12StandardQA']},indent=2));return
 require(args.final_c12_sha==NEW and args.final_p14_sha==NEWW,'Explicit approved SHA arguments required')
 require(not (D/'migration-applied.json').exists() and not (D/'text-history').exists(),'Already applied or snapshot started; inspect partial transaction')
 pre=read(D/'migration-preflight.json');require(pre['before']==baseline and pre['protected']==work['protected'],'State changed since preflight');require(pre['script']['sha256']==sha(__file__),'Script changed since preflight')
 hist=D/'text-history';hist.mkdir();snap=[]
 # Exact TEXT snapshots before any canonical PNG replacement.
 for p in pending:
  if p.exists():
   q=hist/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());snap.append(dict(original=str(p),snapshot=ref(q)))
 # Protect additional current reports/references even where this migration leaves them intact.
 for p in [W/'native/p14.request.json',W/'native/p14.call.json',C/'frozen-neighbors.json',C/'qa/horizontal-review.json',T/'qa/registered/internal-review.json',D/'manifest-before-source-reopen.json']:
  q=hist/p.relative_to(R)
  if p.exists() and not q.exists():q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());snap.append(dict(original=str(p),snapshot=ref(q)))
 write(hist/'index.json',dict(createdAt=now(),snapshots=snap,oldImageVersionsReplacedNotDeleted=[dict(file=str(E),sha256=OLD),dict(file=str(P),sha256=OLDW)],imagesBackedUp=False))
 log=D/'migration-journal.json';journal=dict(startedAt=now(),status='applying',operations=[]);write(log,journal)
 try:
  for p,data in list(images.items())+[(p,jbytes(v)) for p,v in pending.items()]:
   expected=baseline[str(p)];require((sha(p) if p.exists() else None)==expected,'Concurrent write before mutation '+str(p));p.parent.mkdir(parents=True,exist_ok=True)
   journal['pendingWrite']=dict(file=str(p),oldSha256=expected,newSha256=digest(data));write(log,journal)
   p.write_bytes(data);require(sha(p)==digest(data),'Write verification failed '+str(p));journal['operations'].append(journal.pop('pendingWrite'));write(log,journal)
  for path,expected in work['protected'].items():require(sha(path)==expected,'Protected file changed '+path)
  require(sha(E)==NEW and sha(P)==NEWW,'Final canonical hash mismatch')
  # Reproduce applied QA using current canonical source, not proposal references.
  n=Path(read(T/'output/manifest.json')['northSource'])
  reproduced=[]
  for name,im,op,roles in engine.qa_images(Image.open(E).convert('RGB'),{'north':Image.open(n).convert('RGB')},'NW',256):
   p=T/'qa/source-joint-current'/(name+'.png');require(np.array_equal(np.asarray(im),arr(p)),'Applied QA stale '+name);reproduced.append(ref(p))
  require(read(W/'plan.json')['eastCandidateSha256']==sha(E),'C11 current E pointer stale');require(read(C/'plan.json')['westCandidateSha256']==sha(E),'C13 current W pointer stale')
  result=dict(completedAt=now(),status='applied_and_verified',canonicalAfter=[ref(E),ref(P),ref(CP)],metadataAfter=[ref(p) for p in pending],imageAfter=[ref(p) for p in images],migration=ref(D/'applied-source-migration.json'),history=ref(hist/'index.json'),c12All27AppliedQAReproduced=reproduced,c13All32QAReconstructedExact=True,protectedAllUnchanged=True,originalRequestsUnchanged=True,formalAccepted=False,noDeletion=True,rootProgressUntouched=True)
  write(D/'migration-applied.json',result);journal['status']='complete';journal['result']=ref(D/'migration-applied.json');write(log,journal)
  print(json.dumps(dict(status=result['status'],canonicalAfter=result['canonicalAfter'],metadataWrites=len(pending),imageWrites=len(images),c12QA=27,c13ExactQA=32),indent=2))
 except Exception as exc:
  journal['status']='failed_stop';journal['error']=repr(exc);write(log,journal);raise
if __name__=='__main__':main()
