from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;D=R/'r10_c16/repairs/north-integrated-color-v3';Q=D/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected='38f9ab047e8dccca8e49e2db392465f42d9447b5edcf4b2aa4d9432ea94304a4'
assert sha(D/'candidate.png')==expected
names=['n2-full-joint','n3-full-joint','n2-left-vertical','n2-n3-overlap-vertical','n3-right-vertical']+[f'insertion-bottom-{i}' for i in range(1,5)]+[f'prefix-transition-{i}' for i in range(1,4)]
paths=[Q/(n+'.png') for n in names]+[Q/'assembly'/(n+'.png') for n in ['north-r09-r10-common-edge-full','overview-preview-1024','corner-ne','corner-nw','corner-se','corner-sw']]
v={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','candidateSha256':expected,'actualVisualInspection':True,'result':'pass','scope':'Full north common boundary, native insertion strips, three original overlap prefix transitions, overview and four corners. West boundary remains pending final r10_c15. Internal six bands and nine crosses covered separately.','observations':['Wood uprights and hanging cloth continue naturally across the north common boundary.','No old straight water color strip remains in the north-right section.','Insertion side and bottom strips have continuous geometry and tonal transitions.','The bucket, rope and water prefix transitions no longer show a sharp guide-strip cut.'],'viewedSheets':[{'file':str(p),'sha256':sha(p),'nativePixelQA':'overview' not in p.name} for p in paths],'formalAccepted':False,'clientAcceptance':False}
(D/'root-north-review.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(expected)
