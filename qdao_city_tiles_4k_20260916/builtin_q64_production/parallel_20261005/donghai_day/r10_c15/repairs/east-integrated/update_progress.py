from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_day');T=R/'r10_c15'
for n in ['progress.json','current-work.json']:
 p=T/n;d=json.loads(p.read_text());d.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),phase='east-guide-repaired-north-color-and-common-edge-in-progress',candidate='repairs/east-integrated/candidate.png',candidateSha256='e27d76d08c9725bdca0525b45faa8d6ee3f1c2388bfd29e99507559d2450897f',internalReviewScope='y>=700 passed producer and root independent af950 review; new east x3780..4096,y3300..4096 native correction separately reviewed, root pending',pending=['north joint bounded color correction by fill15_left','east common edge color match by root','final candidate merge and independent QA'])
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
d={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidateSha256':'56aa9499341914dbf11e50fe2d405e768c5874120ee873dc8a4763ae00db40a7','result':'needs-local-color-correction','actualViewed':['north-left-insertion.png','north-middle-insertion.png','north-right-insertion.png','north-wide-2.png'],'findings':[{'rect':[1024,0,1500,200],'issue':'North shared y0 warm-to-gray straight color cutoff, geometry continuous.'},{'rect':[2130,0,2160,190],'issue':'Patch overlap termination has vertical capstone/stone-face color step.'},{'rect':[3090,500,3430,707],'issue':'Mild gray floor tone difference near lower insertion.'}],'assignedTo':'fill15_left','canonicalUnchanged':True}
(T/'repairs/north-integrated-v2/visual-review.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Updated scoped progress and north review.')

