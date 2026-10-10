from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(d,expected,names,scope,notes,filename):
 assert sha(d/'candidate.png')==expected
 out={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','candidateSha256':expected,'result':'pass','actualVisualInspection':True,'scope':scope,'observations':notes,'viewedSheets':[{'file':str(d/'qa'/n),'sha256':sha(d/'qa'/n)} for n in names],'formalAccepted':False,'clientAcceptance':False}
 (d/filename).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record(R/'r10_c15/repairs/east-integrated','e27d76d08c9725bdca0525b45faa8d6ee3f1c2388bfd29e99507559d2450897f',[n+'.png' for n in ['east-guide-detail','east-wall','east-left','east-top']],'Independent geometry review of repaired c15 east guide-strip and its left/top insertion. The physical x4096 common-edge color is explicitly excluded and remains a separate c16 correction.',['Old x3981 stone-mortar kink is removed.','Stone facet and narrow local highlight are consistent with the neighboring stone faces.','The left and top c15 insertion boundaries do not introduce displaced contours.'],'root-independent-east-geometry-review.json')
D=R/'r10_c16/repairs/west-color-v1'
names=[f'external/west-wide-{i}.png' for i in [2,3,4]]+['external/west-r10-c15-c16-common-edge-full.png']+[f'assembly/internal-horizontal-y{y}-full.png' for y in [1024,2048,3072]]+['assembly/corner-sw.png','assembly/overview-preview-1024.png']+[f'assembly/intersection-x{x}-y{y}.png' for y in [2048,3072] for x in [1024,2048,3072]]
record(D,'5089cf2e5fd0d00fdc5d73eac046bf41b9b816b3200523593f21f0f1fc9c9d87',names,'West common edge y>=700 and changed internal horizontal bands/SW corner; six lower intersections additionally viewed. Northern700 rows and northwest four-tile intersection remain pending the c15 north repair. Full-edge sheet was viewed but this report only passes its y>=700 portion.',['The old vertical color split through stone faces is removed.','Stone mortar, timber sides and rope geometry remain continuous.','The three changed horizontal QA bands, SW corner and six lower intersections show no new abrupt tonal cut or displaced contour.'],'root-west-scope-review.json')
print('Recorded scoped actual visual reviews')
