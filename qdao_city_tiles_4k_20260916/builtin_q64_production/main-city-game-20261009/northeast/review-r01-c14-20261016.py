from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;T=Z/'r01_c14';Q=T/'qa/core-baseline/3072ac5a7f7ddbf7faeb'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=read(Q/'assembly.json');sourceBy={s['id']:s for s in a['inputs']['nativeSources']}
reused={('p11','p12'):'c1ecad8e214e6f11/p11-p12.png',('p12','p13'):'1040e40a89ea6aed/p12-p13.png',('p13','p14'):'e428d8a6a02e04de/p13-p14.png',('p33','p34'):'3e22f5dd7a7cec17/p33-p34.png',('p41','p42'):'aaf18894e8bd9fcf/p41-p42.png',('p42','p43'):'45336c0d4b11fb25/p42-p43.png',('p43','p44'):'3614c34ea79c94f7/p43-p44.png',('p11','p21'):'0c2cf7977c36eb6c/p11-p21.png',('p14','p24'):'331c0795c09548fa/p14-p24.png',('p21','p31'):'e6f87448bd77f988/p21-p31.png',('p24','p34'):'1623dd53b845a7d1/p24-p34.png',('p31','p41'):'16212c966503886e/p31-p41.png',('p33','p43'):'1c289d3356e024e6/p33-p43.png',('p34','p44'):'853d6c6ff737b3b9/p34-p44.png'}
pairs=[]
for s in a['seams']:
 ids=s['sourceIds'];key=tuple(ids)
 if key in reused:
  w=T/'qa/quick-native-joins'/reused[key];ev=read(w.parent/'sources.json')
  assert [x['sha256'] for x in ev['sources']]==[sourceBy[x]['sha256'] for x in ids]
  reuse=True
 elif key==('p32','p42'):w=T/'qa/quick-20261016/p32-fix2-south-join.png';reuse=True
 else:w=Q/(s['axis']+'-'+ids[0]+'-'+ids[1]+'-join-100pct.png');reuse=False
 pairs.append({'sourceIds':ids,'sources':[{'file':sourceBy[x]['file'],'sha256':sourceBy[x]['sha256']} for x in ids],'reviewWindow':str(w),'windowSha256':sha(w),'hashUnchangedQuickReviewReused':reuse,'visualReviewed':True})
corners=[{'window':str(Q/f'intersection-r{r}-c{c}-100pct.png'),'sha256':sha(Q/f'intersection-r{r}-c{c}-100pct.png'),'visualReviewed':True} for r in range(1,4) for c in range(1,4)]
candidate=Q/'r01_c14-core-baseline.candidate.png'
review={'tile':'r01_c14','candidate':str(candidate),'candidateSha256':sha(candidate),'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'assembly':str(Q/'assembly.json'),'assemblySha256':sha(Q/'assembly.json'),'nativeCoreCount':16,'nativeGeneratedCount':20,'internalPairCountReviewed':24,'intersectionCountReviewed':9,'reusedUnchangedQuickPairCount':15,'newlyReviewedPairCount':9,'pairs':pairs,'intersections':corners,'layoutOverviewViewed':True,'layoutOverviewDisplayReducedOnly':True,'internalPassed4kCount':0,'formalAcceptedCount':0,'status':'complete_native_candidate_internal_defects_pending','p2Issues':[{'id':'M01-banner-horizontal-registration','detail':'At y3072, banner sides and gold ornament remain shifted horizontally between p32 and p42. Fix1 removed invented upper pillar; fix2 improved ornament vertical alignment but horizontal displacement remains.','nativeEditAttempts':2,'status':'deferred_unpassed_best_fix2_retained'},{'id':'M02-central-wall-course-jumps','detail':'At x2048 across y1024..3072, stone courses and broad ledge have abrupt heights/texture changes, strongest around intersection2048,2048 and lower wall.','nativeEditAttempts':0,'status':'pending'},{'id':'M03-context-material-bands','detail':'Narrow rectangular material/lighting transitions remain near native context bands around rows1024/2048, and local wall seam near x1024.','nativeEditAttempts':0,'status':'pending'}],'p3Notes':['Minor leaf-tip and grain variation in otherwise coherent vegetation joins.'],'sharedWorldEdges':'pending except quick south seed checks; whole map not accepted','actualModel':None,'route':'builtin'}
save(T/'qa/internal-review-v20261016.json',review)
p=read(T/'tile-progress.json');p.update({'candidate':str(candidate),'candidateSha256':sha(candidate),'completeCandidateCount':1,'internalPassed4kCount':0,'formalAcceptedCount':0,'fullInternalReview':str(T/'qa/internal-review-v20261016.json'),'status':review['status'],'pendingRepairs':[x['id'] for x in review['p2Issues']],'inflightGeneration':None,'updatedAt':datetime.now(timezone.utc).isoformat()});save(T/'tile-progress.json',p)
print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'reviewedPairs':24,'reviewedIntersections':9,'internalPassed':0,'pendingGroups':3}))

