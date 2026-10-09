from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_day');D=R/'r10_c15/repairs/north-right-color-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=['north-right-wide','north-right-joint','north-right-left-insertion','north-right-bottom-insertion','color-lower-transition']
d={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(D/'candidate.png'),'result':'pass','scope':'new right-north native joint x3284..4096,y0..627 and bounded tone x3180..4096,y0..400; remaining left north color field pending','observations':['Original diagonal bridge rail flat cutoff at north border is repaired by native inpainting, connected to immutable r09 core.','Left blue-gray upright stone and brown capstone retained from base to avoid new insertion step.','Wood post boundary tone is continuous after bounded same-geometry RGB field; exact per-column residual limited to wood post, avoiding diagonal rail contour.','Lower color decay and native insertion do not introduce new straight bands or contour gaps.'],'actualViewedSheets':[{'file':str(D/'qa'/(n+'.png')),'sha256':sha(D/'qa'/(n+'.png')),'passed':True} for n in names],'east627RawRGBSha256':'2ab517d53af189736ec6ed75b0d34863582582dc58ffbd0a231f2c843f34d29b','east627BelowY700RawRGBSha256':'7b748b6091d838a6b86bc4a7d65e5097d2bba90d6ffc413fc69f9b2e9dacafaa','formalAccepted':False}
(D/'visual-review.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(sha(D/'visual-review.json'))

