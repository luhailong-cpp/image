from pathlib import Path
from PIL import Image
import json,hashlib,datetime
T=Path(__file__).resolve().parent;B=T/'qa/core-baseline/588fc5b6ec5cfe33a86a';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sel=json.loads((T/'selected-native.json').read_text(encoding='utf-8-sig'));assembly=json.loads((B/'assembly.json').read_text(encoding='utf-8-sig'))
old=json.loads((T/'qa/left-column-v20261012/visual-review.json').read_text(encoding='utf-8-sig'))
for e in old['viewedAtNativePixels'][:3]:assert sha(B/Path(e['file']).name)==e['sha256']
findings=[
{'priority':'P1','id':'unexpected-roof','box':[1100,2940,2680,3710],'detail':'Gold-trimmed turquoise roof introduced where layout indicates ground band and foliage; do not propagate to neighbors. Needs local AI replacement with ground and existing foliage.','repairAttempts':0},
{'priority':'P2','id':'orphan-grout-p13','box':[2048,0,2600,1024],'detail':'Orphan grout segments near west/north context transition inside p13.','repairAttempts':0},
{'priority':'P2','id':'orphan-grout-p23','box':[2048,1024,2600,2048],'detail':'Short disconnected grout near upper-left p23.','repairAttempts':0},
{'priority':'P2','id':'p32-material-leaf-cut','box':[950,2048,1280,3150],'detail':'Hard material boundary and vertical cut leaf cluster at x1024 in lower p32; v2 fixed unrequested paving ornaments, remaining boundary.','repairAttemptsForOrnaments':1,'repairAttemptsForBoundary':0},
{'priority':'P2','id':'p33-grout','box':[1950,1850,2600,2850],'detail':'Grout phase step at p23/p32/p33 intersection and disconnected seam in upper-left p33.','repairAttempts':0},
{'priority':'P2','id':'p34-grout','box':[2950,2800,3350,3120],'detail':'Orphan lower-left grout plus phase shift at p33/p34 boundary near y3000.','repairAttempts':0},
{'priority':'P2','id':'p44-band-and-grout','box':[2960,2940,3380,3700],'detail':'Cool-gray paving strip and grout start at vertical x3072 cut against p43; keep unpassed.','repairAttempts':0}]
newwindows=[]
for patch,filename in sel.items():
 v=filename.removesuffix('.png')
 q=T/'qa/resume-20261016'/(v+'-quick-review.json')
 if q.exists():
  r=json.loads(q.read_text(encoding='utf-8-sig'));assert r['nativeSha256']==sha(T/'native'/filename)
  for e in r['joins']:
   assert sha(e['file'])==e['sha256'];newwindows.append(e)
cross=[{'file':str(p),'sha256':sha(p)} for p in sorted(B.glob('intersection-*-100pct.png'))]
review={'tile':T.name,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':str(B/'r08_c15-core-baseline.candidate.png'),'candidateSha256':sha(B/'r08_c15-core-baseline.candidate.png'),'selectedCoreCount':16,'nativeVersionCount':21,'allReferenceBytesReverified':True,'reusedHashIdenticalReview':str(T/'qa/left-column-v20261012/visual-review.json'),'reusedInternalPairCount':3,'newInternalPairsReviewed':21,'internalPairsReviewed':24,'expectedInternalPairs':24,'intersectionsReviewed':9,'viewedNewNativeJoinWindows':newwindows,'viewedIntersections':cross,'findings':findings,'internalPassed':False,'externalPassed':False,'formalAccepted':False}
(T/'qa/resume-20261016/baseline-review-v1.json').write_text(json.dumps(review,indent=2)+'\n')
p=T/'tile-progress.json';j=json.loads(p.read_text(encoding='utf-8-sig'));j.update(nativePatchCount=16,selectedCoreCount=16,generatedNativeCount=21,completeCandidateCount=1,candidate=review['candidate'],candidateSha256=review['candidateSha256'],internalPassed4kCount=0,externalPassed4kCount=0,formalAcceptedCount=0,status='complete-candidate-unpassed-layout-and-seams',inflightRequests=[],nativeSources=[{'patch':k,'file':str(T/'native'/v),'sha256':sha(T/'native'/v)} for k,v in sel.items()],remainingFindings=findings,qaReview=str(T/'qa/resume-20261016/baseline-review-v1.json'));p.write_text(json.dumps(j,indent=2)+'\n')
R=T/'layout-only/repairs';R.mkdir(exist_ok=True)
src=B/'r08_c15-core-baseline.candidate.png'
f=R/'roof-remove-left-local-v1-20261016.input.png';assert not f.exists();Image.open(src).crop((900,2842,2154,4096)).convert('RGB').save(f)
(R/'roof-remove-left-local-v1-20261016.input.json').write_text(json.dumps({'file':str(f),'sha256':sha(f),'source':str(src),'sourceSha256':sha(src),'crop':[900,2842,2154,4096],'method':'native integer crop only'},indent=2)+'\n')
print(str(f))

