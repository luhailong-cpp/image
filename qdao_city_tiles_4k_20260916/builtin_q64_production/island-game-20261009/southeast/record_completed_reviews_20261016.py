from workflow import *
from PIL import Image
q=ROOT/'qa'/'r08_c10-wall-recover-20261013-v02';w=read(q/'worker-review.json');sp=read(q/'source-proof.json');cf=Path(w['candidate']);assert sha(cf)==w['candidateSha256']==sp['candidateSha256'];assert sp['coveredPixels']==16777216 and sp['sourceReplayMismatch']==0
write(q/'root-internal-review-20261016.json',{'tile':'r08_c10','candidate':str(cf),'candidateSha256':sha(cf),'internalPassed':True,'externalPassed':False,'localArtworkAcceptanceReady':False,'formalAccepted':False,'sourceProof':str(q/'source-proof.json'),'workerReview':str(q/'worker-review.json'),'workerReviewSha256':sha(q/'worker-review.json'),'worker24Seams9JunctionsPassed':True,'rootViewedChangedSeams':['h33','h41','v24','v31','v34'],'rootViewedChangedJunctions':['junction_23','junction_31','junction_33'],'rootViewedNative':['r08_c10_p41_v02.png','r08_c10_p34_v03.png'],'rootViewedPreview':True,'retainedMinorVariation':'Small paving texture/shade differences without blocking internal contour gaps; final external review remains pending.','pending':'external_E_p24_wall_foot remains not passed after two attempts; actual north/west/south and outer-corner review incomplete','reviewedAt':now()})
q2=ROOT/'qa'/'r11_c12-complete-corners-20261016';m=read(q2/'manifest.json')
notes={'NW':'Broad paving slab contours continuous through all four quadrants.','NE':'Connected leaf network through corner; minor painted shade variation retained.','SW':'Single gold finial, collar and wooden base continuous.','SE':'Gold panel edge and adjacent water continuous.'}
for e in m['entries']:e.update(status='visual_passed',viewedAt=now(),observation=notes[e['id']])
m.update(externalPassed=True,localArtworkAcceptanceReady=True,formalAccepted=False,reviewedAt=now());write(q2/'manifest.json',m)
r=read(ROOT/'production-resume-20261012.json')
entry=next(x for x in r['currentAdoptedCandidates'] if x['tile']=='r11_c12');entry.update(externalPassed=True,localArtworkAcceptanceReady=True,externalReview=str(q2/'manifest.json'),pending='main coordinator final acceptance')
pending=[('r13_c13','r13_c13.candidate-right-full-20261013-v01.png','r13_c13-right-full-20261013-v01/actual-review.json'),('r14_c11','r14_c11.candidate-resume-20261013-v01.png','r14_c11-resume-20261013-v01/left-visual-review.json'),('r14_c13','r14_c13.candidate-right-full-20261016-v01.png','r14_c13-right-full-20261016-v01/actual-review.json')]
for tid,name,review in pending:
 f=ROOT/'tiles'/name
 if not f.exists():continue
 with Image.open(f) as im:assert im.size==(4096,4096)
 e={'tile':tid,'candidate':str(f),'sha256':sha(f),'fullyCovered':True,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'status':'full_candidate_pending_local_repair','review':str(ROOT/'qa'/review) if (ROOT/'qa'/review).exists() else None}
 r['pendingCandidates']=[x for x in r.get('pendingCandidates',[]) if x['tile']!=tid]+[e]
r.update(currentTile='r08_c13',activeCoordinates=['r08_c13','r09_c10','r13_c10','r14_c13'],inFlight=False,inFlightRequests=[],nextStep='Root r08c13 12 of16 native coordinates; finish four central cores, review and repair post join. Internal workers continue their preserved assignments.',updatedAt=now(),lastError=None)
for name in ['production-resume-20261012.json','progress.json','production-state.json','current-zone-counts-20261013.json']:
 d=r if name=='production-resume-20261012.json' else read(ROOT/name)
 if 'currentAdoptedCandidates' in d:d['currentAdoptedCandidates']=r['currentAdoptedCandidates']
 if 'pendingCandidates' in d:d['pendingCandidates']=r['pendingCandidates']
 d.update(currentTile=r['currentTile'],inFlight=False,inFlightRequests=[],nextStep=r['nextStep'],lastError=None,updatedAt=now())
 write(ROOT/name,d)
print('Recorded reviewed r08c10 and r11c12; registered saved full pending candidates.')
