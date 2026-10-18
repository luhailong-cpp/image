from workflow import *
from PIL import Image
import subprocess,sys
for tid,rev in [('r08_c13','root-full-20261016-v02'),('r08_c12','v16-foliage-20261016'),('r09_c10','wall-oct16-v01')]:
 q=ROOT/'qa'/f'{tid}-{rev}';candidate=ROOT/'tiles'/f'{tid}.candidate-{rev}.png';proof=read(q/'source-proof.json');assert sha(candidate)==proof['candidateSha256'];assert proof['sourceReplayMismatch']==0
 for s in proof['sources']:assert sha(Path(s['file']))==s['sha256']
 review={'tile':tid,'candidate':str(candidate),'candidateSha256':sha(candidate),'internalPassed':True,'externalPassed':False,'formalAccepted':False,'sourceProof':str(q/'source-proof.json'),'reviewer':'root','reviewedAt':now(),'seamCount':24,'junctionCount':9,'pending':'Actual full neighboring edges and four-tile corners remain required.'}
 if tid=='r08_c13':
  sm=read(q/'seams.json');reuse=sum(e['status']=='passed_hash_reuse_actual_core_strip' for e in sm['entries'])
  for e in sm['entries']:
   if e['status']=='pending_visual_review':
    if e['id'] in ['h32','h33']:assert e['sha256']==sha(ROOT/'qa/r08_c13-root-full-20261016-v01'/f"{e['id']}.png")
    e.update(status='passed_actual_visual_review',reviewer='root')
  write(q/'seams.json',sm)
  review.update(nativeSpec=str(ROOT/'qa/r08_c13-root-full-20261016-v02.spec.json'),seamsReusedByExactHash=reuse,newSeamsViewed=24-reuse,junctionsViewed=9,repairOuterEdgesViewed=4,wholePreviewViewed=True,finding='Pillar shaft step repaired in registered whole-joint native edit; all visible contours connect. Minor paving brush/stone-shape variation at junction32 retained without blocking edge break.')
 elif tid=='r08_c12':
  sm=read(q/'seams.json')
  for e in sm['entries']:
   if e['id'] in ['h43','v34']:e.update(status='passed_actual_visual_review',reviewer='root')
  write(q/'seams.json',sm);im=Image.open(candidate).convert('RGB');old=Image.open(ROOT/'tiles/r08_c12.candidate-v15.png').convert('RGB');j=[]
  for rr in range(1,4):
   for cc in range(1,4):
    box=[cc*1024-256,rr*1024-256,cc*1024+256,rr*1024+256];same=im.crop(box).tobytes()==old.crop(box).tobytes();assert same or (rr,cc)==(3,3);j.append({'id':f'{rr}{cc}','status':'passed','mode':'unchanged_previous_v15_pixels' if same else 'root_actual_view'})
  review.update(nativeSpec=str(ROOT/'qa/r08_c12-v16-foliage-20261016.spec.json'),seamsReusedByExactPixels=22,newSeamsViewed=2,junctions=j,repairOuterEdgesViewed=['left=h43','top=v34','east4-actual','south4-actual'],finding='Confirmed vertical clipped leaf line at old tile x3981 repaired. Actual E4 and S4 adjoining foliage contours viewed continuous. Full external status remains pending.')
 else:
  worker=read(q/'internal-review.json');assert worker['candidateSha256']==sha(candidate)
  review.update(workerReview=str(q/'internal-review.json'),workerEvidence='24 seams and 9 junctions passed; unchanged exact hashes reused by worker.',rootViewed=['preview','h21','h31','v11','v21','v31'],finding='Independent whole-image and five affected original-size seam checks confirm worker review. Other unchanged worker checks reused.',pending='East1 old source interior foliage/material line remains NOTpassed; west/south and complete external corners remain pending.')
 rf=q/'root-internal-review-20261016.json';write(rf,review)
 subprocess.run([sys.executable,str(ROOT/'adopt_candidate_review_20261013.py'),str(rf)],check=True)
 p=read(ROOT/f'progress-{tid}.json');p['inFlight']=False;write(ROOT/f'progress-{tid}.json',p)
