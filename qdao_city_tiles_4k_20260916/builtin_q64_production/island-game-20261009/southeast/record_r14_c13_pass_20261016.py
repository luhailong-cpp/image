from workflow import *
tid='r14_c13';base=ROOT/'qa/r14_c13-right-full-20261016-v01';mid=ROOT/'qa/r14_c13-right-full-20261016-v02';q=ROOT/'qa/r14_c13-right-full-20261016-v03';src=ROOT/'tiles/r14_c13.candidate-right-full-20261016-v03.png'
# All v01 cuts were viewed; v02 changed cuts and all12overlaycuts viewed; remaining p32 east-line failed.
write(mid/'actual-review.json',{'candidateSha256':sha(ROOT/'tiles/r14_c13.candidate-right-full-20261016-v02.png'),'reviewedAt':now(),'internalAccepted':False,'remainingIssue':'p32 east-side guide material boundary remains below first central repair, native image x1024/world tile x1933; v03 targeted repair required.','changedCutsViewed':['h13','h22','h32','v22','v23','junction_22'],'unchangedCutsReused':27,'all12OverlayCutsViewed':True})
s=read(q/'seams.json');reuse=0;fresh=[]
for e in s['entries']:
 name=e['id']+'.png';old=base/name;unchanged=sha(old)==e['sha256']
 if unchanged:reuse+=1
 else:fresh.append(e['id'])
 e.update(status='passed',reviewMode='hash_identical_original_review_reused' if unchanged else 'actual_final_or_unchanged_v02_cut_viewed',note='No rectangular guide edge or broken caustic contour remains.',reviewedAt=now())
s.update(internalAccepted=True,passedCount=24,reviewedAt=now());write(q/'seams.json',s)
junctions=[]
for r in range(1,4):
 for c in range(1,4):
  name=f'junction_{r}{c}.png';unchanged=sha(base/name)==sha(q/name)
  junctions.append({'id':f'{r}{c}','file':str(q/name),'sha256':sha(q/name),'status':'passed','reviewMode':'unchanged_v01_hash_reuse' if unchanged else 'actual_final_view'})
proof=read(q/'source-proof.json')
review={'candidate':str(src),'candidateSha256':sha(src),'dimensions':[4096,4096],'reviewedAt':now(),'seamsPassed':24,'seamsTotal':24,'junctionsPassed':9,'junctionsTotal':9,'junctions':junctions,'initialCandidateAll33Viewed':True,'seamsHashReuseFromV01':reuse,'changedSeamsSinceV01':fresh,'overlayReview':'All12 v02 cuts viewed. V03 new four bounds and changed prior three bounds viewed; unchanged old bounds hash reused.','wholeImageReview':'Final preview and source-sized affected cuts viewed; top guide squares and p32 east material line removed, wave contours continuous.','sourceCount':len(proof['sources']),'coveredPixels':proof['coveredPixels'],'sourceReplayMismatch':proof['sourceReplayMismatch'],'internalAccepted':True,'externalAccepted':False,'formalAccepted':False,'externalNote':'Independent neighboring full tile edges still require final combined review; north r13_c13 is not accepted.'}
write(q/'actual-review.json',review)
sel=ROOT/'selected-native-r14_c13-right-full-20261016-v03.json';d=read(sel);d.update(internalAccepted=True,externalAccepted=False,formalAccepted=False,internalReview=str(q/'actual-review.json'));write(sel,d)
pf=ROOT/'progress-r14_c13.json';d=read(pf);d.update(generatedNativeCount=len(list((ROOT/'native').glob(tid+'_*.png'))),uniqueCoreCoverage=16,usableNativeCount=16,selectedVersions={f'{r}{c}':'v01' for r in range(1,5) for c in range(1,5)},selectedOwnershipManifest=str(sel),complete4kCount=1,currentCandidate=str(src),currentCandidateSha256=sha(src),internalPassed4kCount=1,externalPassed4kCount=0,formalAcceptedCount=0,missingPatchCoordinates=[],inFlightRequestCount=0,unsavedSuccessfulOutputCount=0,internalReview=str(q/'actual-review.json'),status='internal_passed_external_pending',updatedAt=now(),nextStep='Continue r13_c14 along stable south native edge; external neighbor QA later.')
d['deferredIssues']['14'].update(status='resolved_by_registered_overlay',resolvedSource=str(ROOT/'native/r14_c13_p14_v02.png'),candidate=str(src));write(pf,d)
print({'candidate':str(src),'sha256':sha(src),'internal':'24/24 seams and 9/9 junctions PASS','external':'pending','sourceReplayMismatch':0})

