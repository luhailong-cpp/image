from workflow import *
import sys
r=read(ROOT/'production-resume-20261012.json')
for arg in sys.argv[1:]:
 tid,rev=arg.split('=',1);f=ROOT/'tiles'/f'{tid}.candidate-{rev}.png';assert f.exists();q=ROOT/'qa'/f'{tid}-{rev}'
 proof=read(q/'source-proof.json');assert sha(f)==proof['candidateSha256'] and proof['sourceReplayMismatch']==0
 e={'tile':tid,'candidate':str(f),'sha256':sha(f),'fullyCovered':True,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'status':'full_candidate_pending_local_repair_or_review','sourceProof':str(q/'source-proof.json')}
 for name in ['actual-review.json','left-visual-review.json','internal-review.json']:
  if (q/name).exists():e['review']=str(q/name);break
 r['pendingCandidates']=[x for x in r['pendingCandidates'] if x['tile']!=tid]+[e]
full={x['tile'] for x in r['currentAdoptedCandidates']+r['pendingCandidates']};missing=[f'r{rr:02}_c{cc:02}' for rr in range(8,15) for cc in range(8,15) if f'r{rr:02}_c{cc:02}' not in full];r['remainingWithoutFullCandidate']=missing;c=r['counts'];adopt=r['currentAdoptedCandidates']
c.update(generatedNativeCount=len(list((ROOT/'native').glob('*.png'))),fullyCovered4kCount=len(full),complete4kCount=len(full),internalPassed4kCount=sum(bool(x.get('internalPassed')) for x in adopt),externalPassed4kCount=sum(bool(x.get('externalPassed')) for x in adopt),localArtworkAcceptanceReadyCount=sum(bool(x.get('localArtworkAcceptanceReady')) for x in adopt),formalAcceptedCount=0,missingNative4kCount=49-len(full),fullCandidatePendingRepairOrReviewCount=len(r['pendingCandidates']))
for name in ['production-resume-20261012.json','progress.json','production-state.json','current-zone-counts-20261013.json']:
 d=r if name=='production-resume-20261012.json' else read(ROOT/name)
 if 'counts' in d:d['counts']=dict(c)
 else:d.update(c)
 for key,val in [('currentAdoptedCandidates',adopt),('pendingCandidates',r['pendingCandidates']),('remainingWithoutFullCandidate',missing),('missingNativeTiles',missing)]:
  if key in d:d[key]=val
 d.update(updatedAt=now(),updatedAtUtc=now(),status='active_builtin_native_continuation',generationStopped=False);write(ROOT/name,d)
print(json.dumps(c))
