"""Apply explicit hash-bound root reviews; never infer visual approval from technical validity."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
from contact_validation import validate_contact
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('directions',nargs='+',choices=['N','NE','E','SE','S','SW','W','NW']);args=a.parse_args()
root=read(R/'audit/bamboo-root-acceptance.json')['directions'];reviews=read(R/'review.json');base=read(R/'audit/bamboo-baseline.json')['frames']
for d in args.directions:
 contact=validate_contact(R,d)
 approval=root[d]
 assert approval['status']=='accepted_offline_after_user_feedback'
 assert len(approval['frames'])==16
 for f in approval['frames']:assert sha(R/f['file'])==f['sha256'],'Accepted artwork changed since review'
 phasepath=R/'run'/d/'grounding-review.json';phase=read(phasepath)
 if 'previousFeedbackReview' not in phase:
  phase['previousFeedbackReview']={k:v for k,v in phase.items() if k not in {'previousFeedbackReview','frames'}}
 phase.update({'status':'passed_offline_after_bamboo_reference_review','reviewedAt':approval['reviewedAt'],'selectedCycleMs':1200,'durationsMs':[75]*16,'independentReview':'See audit/bamboo-*-review.json and root SHA-bound acceptance','rootReview':'audit/bamboo-root-acceptance.json','remainingChecks':['Client world velocity, world-root and shadow/event validation after integration'],'clientValidated':False})
 phase['fourFrameContactReview']=f'audit/contact-{d}-review.json'
 phase['contactSpans']=contact['contacts']
 for n,f in enumerate(approval['frames'],1):
  slot=f['file'][:-4];meta=read(R/(f['file']+'.generation.json'))
  reviews[slot]={**reviews.get(slot,{}),'sha256':f['sha256'],'previousFeedbackSha256':base[slot]['sha256'],'visualStatus':'passed','reviewedAt':approval['reviewedAt'],'reviewer':'root with independent direction-agent static review','scope':approval['method'],'notes':approval['notes'],'rootAcceptance':'audit/bamboo-root-acceptance.json','clientValidated':False}
  row=phase['frames'][n-1]
  row.update({'file':f['file'],'frame':n,'sha256':f['sha256'],'selectedNative':meta['derivedFrom']['file'],'durationMs':75,'reviewStatus':'passed_offline_after_bamboo_reference_review'})
  if d=='W' and n in (6,14):row['phase']='forward_swing_flight'
  if d=='E':
   changes={6:('前伸腾空','近右前腿向前下方伸展，远左后腿屈膝回收。'),8:('近右脚开始落脚','近右前鞋首次转平落脚，远左后腿回收。'),9:('近右脚承重','延续08平底承重，不重复翘脚。'),12:('近右脚蹬离','近右腿向后蹬离，远左膝抬起前摆。'),14:('远左腿前伸下降','远左前腿前伸，近右后腿回收，导向15落脚。'),15:('远左脚开始落脚','远左前鞋转平开始落脚，近右后腿回收。'),16:('远左脚承重衔接','前鞋平缓承重并与01连续，不重复抬脚或下探。')}
   if n in changes:row['phase'],row['observation']=changes[n]
  meta['review']={'status':'passed_offline','reviewedAt':approval['reviewedAt'],'source':'review.json','sha256':f['sha256'],'clientValidated':False}
  save(R/(f['file']+'.generation.json'),meta)
 save(phasepath,phase)
save(R/'review.json',reviews)
print(json.dumps({'acceptedDirections':args.directions,'acceptedFrames':len(args.directions)*16}))

