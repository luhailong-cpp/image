from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,os
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;R=T/'repairs';D=T/'review/root-final-batch-20261016';D.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inf(p):return {'path':str(p),'sha256':sha(p)}
def checked(v):p=Path(v['path']);assert sha(p)==v['sha256'],str(p);return p
def write_new(p,d):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
base=T/'candidate/r16_c16-4k-candidate-101a9801efaf54800416.png';assert sha(base)=='fa9ff5a51638c2664c2ffe690d93fd7fc5ca8bfc911867cdb532c13069f7fc5e'
base_ctx=T/'candidate/r16_c16-context-4326-101a9801efaf54800416.png';base_manifest=T/'candidate/r16_c16-assembly-101a9801efaf54800416.json'
paths=[R/'north-corner-20261016/trial-v1/composition.json',R/'west-joints-20261016/W01-v1/compact-mask-v2/composition.json',R/'right-courses-20261016/trial-mask-v3/selected-operation-proposal.json']
n,w,u=map(read,paths)
ops=[{'id':'N02','source':n['native'],'receipt':n['receipt'],'alpha':n['alpha'],'nativeCrop':n['sourceCrop'],'destinationCoreBox':n['destinationCoreBox'],'manifest':inf(paths[0])},{'id':'W01','source':w['native'],'receipt':w['receipt'],'alpha':w['alpha'],'nativeCrop':w['nativeCrop'],'destinationCoreBox':w['tilePlacement'],'manifest':inf(paths[1])},{**u['operations'][0],'id':'I01-upper','manifest':inf(paths[2])}]
old=np.array(Image.open(base).convert('RGB'));out=old.copy();used=np.zeros((4096,4096),bool)
for op in ops:
 s=checked(op['source']);a=checked(op['alpha']);checked(op['receipt']);im=Image.open(s);assert im.size==(1254,1254)
 src=np.array(im.convert('RGB').crop(op['nativeCrop']));alpha=np.array(Image.open(a));x,y,x1,y1=op['destinationCoreBox'];assert src.shape[:2]==alpha.shape==(y1-y,x1-x)
 assert not np.any(used[y:y1,x:x1]&(alpha>0));used[y:y1,x:x1]|=alpha>0
 dest=out[y:y1,x:x1];out[y:y1,x:x1]=((dest.astype('uint32')*(255-alpha[...,None])+src.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
assert np.array_equal(out[~used],old[~used])
replay=old.copy()
for op in reversed(ops):
 x,y,x1,y1=op['destinationCoreBox'];a=np.array(Image.open(checked(op['alpha'])),dtype='int64');b=np.array(Image.open(checked(op['source'])).convert('RGB').crop(op['nativeCrop']),dtype='int64');v=replay[y:y1,x:x1]
 for c in range(3):v[:,:,c]=((v[:,:,c].astype('int64')*(255-a)+b[:,:,c]*a+127)//255).astype('uint8')
assert np.array_equal(replay,out)
core=T/'candidate/r16_c16-4k-reviewed-local-repairs-20261016.png';context=T/'candidate/r16_c16-context-reviewed-local-repairs-20261016.png';assert not core.exists() and not context.exists()
Image.fromarray(out).save(core);ci=Image.open(base_ctx).convert('RGB');ci.paste(Image.fromarray(out),(115,115));ci.save(context)
pending=[{'id':'W02','status':'failed_deferred_after_two_native_attempts','box':[0,2380,650,3110],'description':'Original lower west coping height mismatch retained; both native repairs failed geometry/boundary QA.'},{'id':'I01-lower','status':'failed_deferred_after_two_native_attempts','box':[3150,2710,3470,3190],'description':'Original lower right wrap retained. Second correction still50px disconnected; not selected.'},{'id':'W03_W04','status':'pending_material_and_wall_grid','description':'West gold-to-stone transition and middle slab grid/material still unpassed.'},{'id':'M01','status':'pending_nonblocking_lighting_finish','box':[1975,1050,3160,1160],'description':'Front wall horizontal shadow band.'},{'id':'W01-watch','status':'improved_local_best_with_closure_and_material_watch','description':'Closed short coping end adopted after root native-scale check; entire west edge remains failed.'}]
qa={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','core':inf(core),'sourceQA':[inf(T/'review/independent-20261016/visual-qa.json'),inf(R/'north-corner-20261016/trial-v1/root-independent-qa-20261016.json'),inf(R/'west-joints-20261016/batch-visual-qa-root-reviewed.json'),inf(R/'right-courses-20261016/trial-mask-v3/refined-v1/visual-qa.json')],'rootActuallyViewed':{'N02':6,'W01_compact':4,'I01_upper':10},'rootLocalFindings':{'N02':'passed_real_north_registration_and_boundaries','W01':'accepted_local_best_closed_end_no_new_boundary_break_watch_retained','I01-upper':'passed_upper_wrap_and_mask_boundaries_no_orphan_grout'},'baseInternalEvidenceReuse':'42 native evidence crops reviewed by independent worker; areas outside selected masks remain byte-identical, adopted local repairs independently viewed by root. Lower-course and remaining finish defects are not passed.','internalArtQA':'pending_lower_right_course_and_lighting_finish','externalNeighborSeamQA':{'north':'local_pass_after_N02','west':'failed_W02_plus_W03_W04_pending','east':'map_border','south':'map_border'},'pending':pending,'formalAccepted':False}
qap=D/'root-selected-repairs-qa.json';write_new(qap,qa)
manifest=T/'candidate/r16_c16-assembly-reviewed-local-repairs-20261016.json'
data={'schemaVersion':1,'tile':T.name,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'complete_native_candidate_with_explicit_pending_repairs','parentAssembly':inf(base_manifest),'base':inf(base),'baseContext':inf(base_ctx),'candidate':{**inf(core),'size':[4096,4096]},'context':{**inf(context),'size':[4326,4326]},'selectedRepairs':ops,'selectedNativeCount':16,'selectedRepairCount':3,'blendArithmetic':'(old*(255-alpha)+native*alpha+127)//255 RGB integer','masksDisjoint':True,'outsideMaskExact':True,'independentReverseOrderChannelReplayExact':True,'resampling':False,'RGBColorCorrection':False,'contextPolicy':'Original halo retained; core updated exactly. External QA uses actual neighboring cores.','visualQA':inf(qap),'pending':pending,'actualModel':None,'formalAccepted':False}
write_new(manifest,data)
progress=T/'progress.json';latest=T/'candidate/latest-assembly.json';shutil.copy2(progress,D/'progress-before-final.json');shutil.copy2(latest,D/'latest-before-final.json')
p=read(progress);p.update(status=data['status'],updatedAt=data['createdAtUtc'],candidate=str(core),candidateSha256=sha(core),context=str(context),contextSha256=sha(context),assemblyManifest=str(manifest),activeNativeCount=16,selectedNativeCount=16,selectedRepairCount=3,missingNativeCount=0,internalArtQA=qa['internalArtQA'],externalNeighborSeamQA=qa['externalNeighborSeamQA'],pendingRepairs=pending,visualQA=str(qap),formalAccepted=False,nextStep='Keep W02/lower-right as failed; resolve remaining independent material/lighting items or continue separately assigned coordinates without modifying reserved coordinates.')
wrapper={'schemaVersion':1,'tile':T.name,'status':data['status'],'manifest':inf(manifest),'candidate':data['candidate'],'context':data['context'],'visualQA':inf(qap),'formalAccepted':False}
for path,record in [(progress,p),(latest,wrapper)]:
 tmp=path.with_suffix('.root-final.tmp');tmp.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,path)
print(json.dumps({'candidate':inf(core),'context':inf(context),'manifest':inf(manifest),'qa':inf(qap)}))
