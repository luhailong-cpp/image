import os
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
q=ROOT/'qa'/'r10_c10-wall-oct17-v03';proof=read(q/'source-proof.json');oldq=ROOT/'qa'/'r10_c10-wall-oct16-v01';old=read(oldq/'seams.json');d=read(q/'seams.json');prev={e['id']:e for e in old['entries']}
failed={'h13':'Old paving endpoint remains; two prior local repairs exhausted.','h42':'Old paving endpoint remains; both newly tried overlays preserve another defect, not adopted.','v33':'Old diagonal paving endpoint remains; h42 overlay trials not adopted.','v22':'Central junction22 has a small zigzag corner offset at tile[2048,2048]; newly recognized and NOTpassed.','v23':'Same junction22 corner offset at the shared endpoint, NOTpassed.'}
for e in d['entries']:
 assert sha(Path(e['file']))==e['sha256'];same=e['sha256']==prev[e['id']]['sha256'];e.update(status='not_passed' if e['id'] in failed else 'passed',note=failed.get(e['id'],'Exact unchanged evidence reused.' if same else 'Changed area verified via native repair center and actual insertion edges; combined adjoining overlay boundary also viewed.'),evidenceBasis='same_hash_old_review' if same else 'actual_repair_center_edges_and_combined_junctions',reviewedAt=now())
write(q/'seams.json',d)
js=[]
for p in sorted(q.glob('junction_*.png')):
 js.append({'file':str(p),'sha256':sha(p),'status':'not_passed' if p.stem in ['junction_13','junction_22'] else 'passed','basis':'unchanged_hash_reuse' if sha(p)==sha(oldq/p.name) else 'actual_512px_review'})
review={'tile':'r10_c10','candidate':proof['candidate'],'candidateSha256':proof['candidateSha256'],'sourceProof':str(q/'source-proof.json'),'sourceReplayMismatch':0,'seamCount':24,'passedSeams':19,'notPassedSeams':failed,'junctions':js,'repairReviews':[str(ROOT/'qa'/'wall-oct16'/x/'review.json') for x in ['r10_c10_ov_v24_v01','r10_c10_ov_h21h31_v01','r10_c10_ov_h33_v01']]+[str(ROOT/'qa'/'wall-oct17'/'r10_c10_h32_roi'/'review.json')],'internalPassed':False,'formalAccepted':False,'reviewedAt':now(),'reviewer':'wall_oct17'};write(q/'internal-review.json',review)
p=ROOT/'progress-wall-oct16.json';d=read(p);d['completedCandidates']['r10_c10']={'file':proof['candidate'],'sha256':proof['candidateSha256'],'dimensions':[4096,4096],'sourceProof':str(q/'source-proof.json'),'internalReview':str(q/'internal-review.json'),'internalAccepted':False,'formalAccepted':False,'notPassedSeams':list(failed)};write(p,d)
s=ROOT/'selected-native-r10_c10-wall-oct17-v03.json';d=read(s);d['internalReview']=str(q/'internal-review.json');write(s,d)
p=ROOT/'progress-wall-oct17.json';d=read(p);d.update(latestCandidate=proof['candidate'],latestCandidateSha256=proof['candidateSha256'],inFlight=['r11_c10_p12_v01','r11_c10_p13_v02'],preparedNotStarted=[],updatedAt=now());write(p,d);print(json.dumps({'candidate':proof['candidate'],'sha256':proof['candidateSha256'],'passedSeams':19,'notPassedSeams':list(failed)}))
