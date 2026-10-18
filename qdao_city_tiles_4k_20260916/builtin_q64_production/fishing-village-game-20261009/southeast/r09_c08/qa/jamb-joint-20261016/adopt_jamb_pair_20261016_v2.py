"""Prepared for root execution. Author has NOT executed adoption.

Usage: python adopt_jamb_pair_20261016_v2.py --adopt
Without --adopt, prints usage and exits without writes.
Two separate JSON files cannot be replaced in one OS atomic operation.
This uses pair preflight, durable backups/journal, per-file atomic replacement,
and conditional rollback if either installation/verification fails.
"""
from pathlib import Path
import argparse,copy,hashlib,json,os,shutil,uuid
import numpy as np
from PIL import Image
from verify_jamb_pair_independent_20261016_v2 import Q,Z,EXPECTED,PINS,sha,read,pixels,new_json,now,verify_current

def write_bytes_new(path,data):
 with path.open('xb') as f:
  f.write(data);f.flush();os.fsync(f.fileno())
def source_guard(report,all_sources,before):
 for tile,raw in before.items():assert (Z/tile/'selected-patches.json').read_bytes()==raw,('Concurrent canonical change',tile)
 for p in report['patches']:assert sha(p['source'])==p['sourceSha256'] and sha(p['candidate'])==p['candidateSha256']
 for sources in all_sources.values():
  for p in sources:assert sha(p['file'])==p['sha256']
 for name,digest in PINS.items():assert sha(Q/name)==digest,('Pinned artifact changed',name)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--adopt',action='store_true');args=parser.parse_args()
 if not args.adopt:
  print('Prepared only. Run with --adopt to verify and adopt both patches, rebuild both 4096 candidates, and reuse unchanged internal QA.');return
 destinations={t:Z/t/'processed/jamb-joint-20261016-v2' for t in EXPECTED}
 assert all(not p.exists() for p in destinations.values()),'Version directory already exists; do not overwrite. Inspect prior transaction.'
 lock=Q/'jamb-v1-surface-v2-adoption.lock'
 write_bytes_new(lock,json.dumps({'startedAtUtc':now(),'pid':os.getpid()}).encode())
 committed=[];before={};after_bytes={};txn=uuid.uuid4().hex
 try:
  report,before,selections,assemblies,all_sources=verify_current()
  source_guard(report,all_sources,before)
  prepared=[];after={};temp={};stamp=now()
  for item in report['patches']:
   tile=item['tile'];pid=item['patch'];T=Z/tile;D=destinations[tile];D.mkdir(parents=True,exist_ok=False)
   backup=D/'selected-patches-before-jamb-joint-20261016-v2.json';write_bytes_new(backup,before[tile]);assert sha(backup)==item['selectionSha256']
   patch=D/f'{pid}-jamb-v1-surface-v2-native.png';shutil.copyfile(item['candidate'],patch);assert sha(patch)==item['candidateSha256']
   patchderivation={'operation':'Copy of verified same-coordinate binary-mask native candidate','source':item['candidate'],'sourceSha256':item['candidateSha256'],'original':item['source'],'originalSha256':item['sourceSha256'],'maskProof':str(Q/'jamb-v1-surface-v2-proof.json'),'independentReplay':str(D/'adoption-time-independent-replay.json'),'actualModel':None,'actualQuality':None,'noResampling':True,'noBlur':True,'noBlend':True,'noWarp':True}
   new_json(patch.with_suffix('.png.derivation.json'),patchderivation)
   selection=copy.deepcopy(selections[tile]);selection['patches'][pid]=patch.relative_to(T).as_posix()
   assert all(selection['patches'][p]==rel for p,rel in selections[tile]['patches'].items() if p!=pid)
   full=D/f'{tile}-jamb-v1-surface-v2-candidate-4096.png'
   Image.fromarray(assemblies[tile]).save(full)
   saved=pixels(full);assert saved.shape==(4096,4096,3) and np.array_equal(saved,assemblies[tile])
   current_sources=[]
   for p,rel in sorted(selection['patches'].items()):
    file=T/rel;a=pixels(file);x,y=(int(p[2])-1)*1024,(int(p[1])-1)*1024
    assert a.shape==(1254,1254,3) and np.array_equal(a[115:1139,115:1139],saved[y:y+1024,x:x+1024])
    current_sources.append({'patch':p,'file':str(file),'sha256':sha(file),'crop':[115,115,1139,1139],'destination':[x,y],'pixelExact':True})
   new_json(full.with_suffix('.png.derivation.json'),{'operation':'16 exact selected native core crops','createdAtUtc':stamp,'file':str(full),'sha256':sha(full),'dimensions':[4096,4096],'sources':current_sources,'resamplingApplied':False,'layoutPixelsUsed':False,'formalAccepted':False})
   # Old evidence files remain untouched; current-source crops were replayed by verifier.
   reuse=D/'internal-QA-pixel-reuse.json'
   new_json(reuse,{'tile':tile,'createdAtUtc':stamp,'candidate':str(full),'candidateSha256':sha(full),'evidence':report['internalEvidence'][tile],'unchangedEvidenceCount':33,'newVisualPassClaimed':False,'previousInternalReview':selections[tile].get('internalReview'),'previousActiveReview':selections[tile].get('activeReview'),'internalReady':False,'formalAccepted':False,'note':'Preserve previous visual findings and failures. Pixel equality only permits reusing previous checks; it does not convert pending/failed QA into a pass.'})
   new_json(D/'adoption-time-independent-replay.json',report)
   oldcandidate=selection.get('candidate')
   if oldcandidate:selection.setdefault('historicalCandidates',[]).append({'candidate':oldcandidate,'candidateSha256':selection.get('candidateSha256',sha(oldcandidate)),'replacedAtUtc':stamp,'reason':'Exact same-coordinate jamb surface and narrow gray trim repair adopted in one selected core; new candidate assembled from all 16 current cores.'})
   # Preserve stale prior display paths as history, not as current assembled outputs.
   if selection.get('readyForExternalQA'):
    selection.setdefault('historicalReadyForExternalQA',[]).append(selection['readyForExternalQA']);selection['readyForExternalQA']=str(full)
   pending=selection.setdefault('pendingIssues',[]);assert isinstance(pending,list)
   for issue in pending:
    if isinstance(issue,dict) and issue.get('id')=='window-right-jamb-color-seam':
     issue['status']='resolved_local_surface';issue['resolutionEvidence']=str(Q/'jamb-v1-surface-v2.adoption-instructions.json');issue['resolvedAtUtc']=stamp
   pending_ids={i.get('id') for i in pending if isinstance(i,dict)}
   for issue in [
    {'id':'jamb-right-brown-trim-tone','status':'pending','description':'Brown upright farther right outside frame x1022 retains a tone discontinuity at global y36864; outside bounded jamb/gray-trim repair.'},
    {'id':'jamb-joint-external-qa','status':'pending','description':'Root to update affected external segments/corner. Local jamb surface pass does not pass the whole edge.'}]:
    if issue['id'] not in pending_ids:pending.append(issue)
   selection.update({'candidate':str(full),'candidateSha256':sha(full),'updatedAt':stamp,'status':'full_native_jamb_joint_adopted_other_QA_pending','internalReady':False,'formalAccepted':False,'materialPending':True,'internalEvidenceReuse':str(reuse),'jambJointAdoption':{'adoptedAtUtc':stamp,'transactionId':txn,'pairedTiles':list(EXPECTED),'localJambGeometryPassed':True,'parentAdoptionTriggeredByExplicitExecution':True,'wholeTilePassed':False,'review':str(Q/'jamb-v1-surface-v2.adoption-instructions.json'),'independentReplay':str(D/'adoption-time-independent-replay.json'),'sourceProof':str(Q/'jamb-v1-surface-v2-proof.json'),'previousSelection':str(backup),'previousSelectionSha256':sha(backup),'actualModel':None,'actualQuality':None}})
   after[tile]=selection;after_bytes[tile]=(json.dumps(selection,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
   temp[tile]=D/f'selected-patches-prepared-{txn}.json';write_bytes_new(temp[tile],after_bytes[tile])
   prepared.append({'tile':tile,'patch':pid,'patchFile':str(patch),'patchSha256':sha(patch),'candidate':str(full),'candidateSha256':sha(full),'backup':str(backup),'backupSha256':sha(backup),'newSelectionSha256':hashlib.sha256(after_bytes[tile]).hexdigest(),'reusedEvidenceCount':33})
  journal={'transactionId':txn,'preparedAtUtc':stamp,'status':'pair_prepared_not_committed','separateFileAtomicReplacements':True,'osAtomicAcrossBothFiles':False,'prepared':prepared,'internalReady':False,'formalAccepted':False,'gitOperations':False}
  new_json(Q/f'jamb-v1-surface-v2-adoption-{txn}-prepared.json',journal)
  source_guard(report,all_sources,before)
  for tile in EXPECTED:
   # Verify all canonical files against before/installed snapshots immediately before each replacement.
   for t in EXPECTED:
    expected=after_bytes[t] if t in committed else before[t]
    assert (Z/t/'selected-patches.json').read_bytes()==expected,('Concurrent selection update detected',t)
   os.replace(temp[tile],Z/tile/'selected-patches.json');committed.append(tile)
  assert all((Z/t/'selected-patches.json').read_bytes()==after_bytes[t] for t in EXPECTED)
  completed=dict(journal,status='both_patch_selections_committed_and_both_full4096_rebuilt',completedAtUtc=now())
  new_json(Q/f'jamb-v1-surface-v2-adoption-{txn}-completed.json',completed)
  for tile,D in destinations.items():new_json(D/'adoption-completed.json',completed)
  print(json.dumps(completed,ensure_ascii=False))
 except Exception as exc:
  rollback=[]
  for tile in reversed(committed):
   canonical=Z/tile/'selected-patches.json'
   if canonical.read_bytes()==after_bytes[tile]:
    restore=destinations[tile]/f'selected-patches-rollback-{txn}.json';write_bytes_new(restore,before[tile]);os.replace(restore,canonical);rollback.append({'tile':tile,'status':'restored_original_selection'})
   else:rollback.append({'tile':tile,'status':'concurrent_change_preserved_manual_review_required'})
  new_json(Q/f'jamb-v1-surface-v2-adoption-{txn}-failed.json',{'failedAtUtc':now(),'error':str(exc),'transactionId':txn,'committedBeforeFailure':committed,'rollback':rollback,'stagedImagesPreserved':True})
  raise
 finally:
  # Remove only this process's exact coordination marker; preserve all image/evidence files.
  if lock.exists() and read(lock).get('pid')==os.getpid():lock.unlink()

if __name__=='__main__':main()
