from workflow import *
tid='r13_c14';q=ROOT/'qa/r13_c14-right-full-20261016-v03';base=ROOT/'qa/r13_c14-right-full-20261016-v01';mid=ROOT/'qa/r13_c14-right-full-20261016-v02';src=ROOT/'tiles/r13_c14.candidate-right-full-20261016-v03.png';s=read(q/'seams.json')
for e in s['entries']:
 e.update(status='not_passed' if e['id'] in ['h41','v32'] else 'passed',reviewedAt=now(),reviewMode='hash_reused_from_viewed_v01' if sha(base/(e['id']+'.png'))==e['sha256'] else 'actual_v03_or_hash_identical_viewed_v02')
s.update(internalAccepted=False,passedCount=22);write(q/'seams.json',s)
write(q/'actual-review.json',{'candidateSha256':sha(src),'reviewedAt':now(),'seamsPassed':22,'seamsTotal':24,'junctionsPassed':8,'junctionsTotal':9,'remainingIssue':'Small hull/foam contour notch at tile[1139,3072], at newly adopted source right edge. Visible in h41/v32/junction31/overlay16right. Local repair in-flight.','reviewedChangedCuts':['h21','h31','h41','junction_11','junction_21','junction_31','v11','v21','v31','v32'],'hashIdenticalV02Reviewed':['h22','h32','v22','v23','junction_22'],'all8OverlayBoundsViewedOrHashReused':True,'internalAccepted':False,'externalAccepted':False,'formalAccepted':False})
d=read(ROOT/'progress-r13_c14.json');d.update(currentCandidate=str(src),currentCandidateSha256=sha(src),internalReview=str(q/'actual-review.json'),status='one_small_source_edge_notch_pending',inFlightRequestCount=1,inFlight=['r13_c14_repair_waterline_v01'],updatedAt=now());write(ROOT/'progress-r13_c14.json',d)

