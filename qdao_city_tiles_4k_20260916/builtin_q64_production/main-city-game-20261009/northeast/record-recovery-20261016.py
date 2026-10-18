from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;now=datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
T=Z/'r01_c14';Q=T/'qa/local-repair-20261016'
c=read(Q/'M02-composition-v2.json')
save(Q/'M02-attempt2-review.json',{'tile':T.name,'issue':'M02-central-wall-course-jumps','attempt':2,'reviewedAtUtc':now,'native':c['source'],'nativeSha256':c['sourceSha256'],'candidate':c['candidate'],'candidateSha256':c['candidateSha256'],'adopted':False,'reviewedWindows':[{ 'file':str(Q/('M02-v2-'+n+'.png')),'sha256':sha(Q/('M02-v2-'+n+'.png'))} for n in ['top','bottom','left','right']],'findings':['Boundary geometry is substantially better preserved than attempt1.','Central ledge becomes sloped then abruptly steps at local x845; upper mortar courses still terminate unnaturally across central transition. Not sufficient to mark repaired.'],'status':'deferred_unpassed_after_two_native_attempts','bestRetained':c['baseCandidate'],'nextStep':'Continue independent missing cores; preserve both native attempts and compositions.'})
review=read(T/'qa/internal-review-v20261016.json')
review['p2Issues'][1].update({'nativeEditAttempts':2,'status':'deferred_unpassed_baseline_retained','attemptReviews':[str(Q/'M02-attempt1-review.json'),str(Q/'M02-attempt2-review.json')]})
review['updatedAtUtc']=now
save(T/'qa/internal-review-after-M02-v20261016.json',review)
tp=read(T/'tile-progress.json');tp.update({'inflightGeneration':None,'fullInternalReview':str(T/'qa/internal-review-after-M02-v20261016.json'),'updatedAt':now});save(T/'tile-progress.json',tp)
T=Z/'r01_c13';Q=T/'qa/recovery-20261016'
records=read(Q/'east-new-sources.json')
for rec in records:rec.update({'visualReviewed':True,'finding':'Wall courses and clipped gold finial contours continuous; small material grain differences pending full-tile review.','internalAcceptance':False})
joins=[]
for sig,pair in [('b2c46e2acf31e4e8','p14-p24'),('05a0c65be80b55e8','p24-p34'),('1d172d41c1f702b4','p34-p44')]:
    q=T/'qa/quick-native-joins'/sig;f=q/(pair+'.png')
    joins.append({'pair':pair,'sources':read(q/'sources.json')['sources'],'window':str(f),'windowSha256':sha(f),'visualReviewed':True,'finding':'Stone courses and object outlines continuous at native resolution; restrained local material variation pending full review.'})
save(Q/'new-core-quick-review.json',{'reviewedAtUtc':now,'east':records,'internalJoins':joins,'selectedCores':4,'formalAcceptedCount':0})
tp=read(T/'tile-progress.json');tp.update({'inflightGeneration':['p23-v20261016','p33-v20261016'],'updatedAt':now});save(T/'tile-progress.json',tp)
cp=read(Z/'resume-checkpoint-20261016.json');cp.update({'updatedAtUtc':now,'rootSelected':['p14','p24','p34','p44'],'rootInflight':['r01_c13/p23-v20261016','r01_c13/p33-v20261016'],'rootRepairReason':'M02 two attempts deferred unpassed; baseline retained. Native output route recovered after reboot.','networkPermissionStatus':'builtin native generation succeeded after reboot','actualModel':None});cp['previousRootTile']['review']='r01_c14/qa/internal-review-after-M02-v20261016.json';save(Z/'resume-checkpoint-20261016.json',cp)
print('Saved source-bound QA and recovery checkpoint.')
