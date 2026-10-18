from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c11')
q=p/'qa/core-baseline/e7179e039686a05185ab'
a=json.loads((q/'assembly.json').read_text(encoding='utf-8-sig'))
h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sel=json.loads((p/'selected-native.json').read_text(encoding='utf-8-sig'))
for n in a['inputs']['nativeSources']:
 assert sel[n['id']]==Path(n['file']).name
 assert h(n['file'])==n['sha256']
src=q/'r08_c11-core-baseline.candidate.png'
dst=p/'candidates/r08_c11-native-4096-v20261016.png'
assert not dst.exists()
shutil.copy2(src,dst)
issues=[
 {'id':'north-path-junction','severity':'P2','location':[1024,1024],'problem':'Narrow horizontal shear through blue path curb and slab joints at first intersection. Geometry differs across core boundary.','evidence':['intersection-r1-c1-100pct.png'],'repairAttemptsThisBatch':0},
 {'id':'context-border-intrusions','severity':'P2','problem':'Rectangular context edges became paving borders inside p13/p21/p31/p41, with abrupt slab scale transitions. Not a clean approved map continuation.','evidence':['intersection-r1-c2-100pct.png','intersection-r2-c1-100pct.png','horizontal-p31-p41-join-100pct.png'],'repairAttemptsThisBatch':0},
 {'id':'middle-slab-joints','severity':'P2','location':[2048,2048],'problem':'At intersections r2c2 and r2c3 diagonal joints terminate at straight native patch boundaries; material scale also changes.','evidence':['intersection-r2-c2-100pct.png','intersection-r2-c3-100pct.png'],'repairAttemptsThisBatch':0},
 {'id':'bottom-slab-joints','severity':'P2','problem':'Bottom-row horizontal joins displace diagonal beveled joints, especially p33/p43; p32/p42 and p34/p44 remain unpassed. p34 already exhausted two repairs and is deferred.','evidence':['intersection-r3-c1-100pct.png','intersection-r3-c2-100pct.png','intersection-r3-c3-100pct.png'],'priorReview':'qa/p34-two-attempt-review-r3.json'},
 {'id':'material-grid-density','severity':'P2','problem':'Large differences in stone grain scale and warm orange fissures between source patches remain visible in the complete tile. Preserve as candidate only.','evidence':['r08_c11-core-baseline.candidate.png']}
]
windows=[x for x in a['artifacts'] if (x.get('kind')=='native-pixel-intersection-crop' or x.get('file','').endswith('-join-100pct.png'))] if 'artifacts' in a else []
# use exact reviewed files without inferring schema
files=sorted(q.glob('*-join-100pct.png'))+sorted(q.glob('intersection-*-100pct.png'))
assert len(files)==33
review={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r08_c11','status':'complete-native-4096-candidate-internal-unpassed','candidate':str(dst),'candidateSha256':h(dst),'nativeSize':[4096,4096],'assemblyManifest':str(q/'assembly.json'),'inputSignature':a['inputSignature'],'sourceHashesReverified':True,'selectedNativeCount':16,'nativeFileCount':22,'reviewedNativeJoinCount':24,'reviewedIntersectionCount':9,'reviewedWindows':[{'file':str(f),'sha256':h(f),'viewedAtNativeResolution':True} for f in files],'overviewViewOnly':True,'issues':issues,'internalPassed4kCount':0,'formalAcceptedCount':0,'operation':'byte-identical copy of existing integer native core assembly; no resampling, blur or programmatic artwork','priorDeferredIssueReused':'qa/p34-two-attempt-review-r3.json','next':'Do not redo exhausted p34 south. Prioritize other complete tile local repairs or independent missing tile from stable edge.'}
f=p/'qa/internal-review-v20261016.json'
assert not f.exists()
f.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pr=p/'tile-progress.json';v=json.loads(pr.read_text(encoding='utf-8-sig'));v.update(status='native_complete_internal_unpassed',completeCandidateCount=1,candidate=str(dst),candidateSha256=h(dst),review=str(f),assemblyManifest=str(q/'assembly.json'),pendingP2Count=len(issues),openP2=[i['id'] for i in issues],readyInternalPairsReviewed=24,completeIntersectionsReviewed=9,internalPassed4kCount=0,formalAcceptedCount=0,updatedAt=review['createdAt'])
pr.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':str(dst),'sha256':h(dst),'status':review['status'],'P2groups':len(issues)}))

