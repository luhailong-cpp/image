from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;T=R/'r10_c16'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=T/'plan.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
s=T/'guides/local-structure.png';assert sha(s)=='09e7a8f6f0978278703277942db27c2ba080b654b5deccf8f8ad33ee933b16b5'
d.update(status='structure_reference_reviewed_native_pending',geometryStatus='Actual layout and AI structure viewed: existing pier, timbers, bucket, clipped hanging float, ropes, net and left stone steps retain source footprint. Guidance only; native and cross-tile geometry QA still required.')
d['boundaryPolicy']['sourceRightEdgeInspection']['visualReview']='Viewed reference crop: blue water continues to right edge, no black padding.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','inputActuallyViewed':True,'outputActuallyViewed':True,
 'structure':{'file':str(s),'sha256':sha(s)},'layout':{'file':str(T/'guides/local-layout.png'),'sha256':sha(T/'guides/local-layout.png')},
 'approvedStyleAttached':str(R.parents[3]/'designs/gameplay-ui/04-guild.png'),'result':'usable structural guidance; not final pixels','formalAccepted':False}
(T/'qa/structure-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
