from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
N=Path(__file__).parent;Q=N/'review-bottom-row-v1'
idx=json.loads((Q/'inspection-index.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
v={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'inspectionIndex':{'file':str(Q/'inspection-index.json'),'sha256':sha(Q/'inspection-index.json')},'sources':{'r07_c09':idx['frozenLocalCheckpoint']['fragment'],'r08_c09':idx['frozenProspectiveBottom']},'nativeScale':1,'actualVisualInspection':True,'coveredNativeRegion':[0,2957,4096,4096],'coveredPixels':4665344,'cropCount':7,'localBottomRowAccepted':True,'south4096pxAccepted':True,'wholeTileAccepted':False,'formalAccepted':False,'findings':['Viewed every filled pixel via three overlapping native1536-or-smaller crops, and full south boundary with256pixels on both sides via four overlapping native crops.','Internal patch joins at tile x155,1179,2203,2957 have no visible artificial vertical seam, rail break or double profile.','South joint and material continuations are visually consistent across complete4096px, including left slim joint, central rail butt joint, cloud panel and slate inset corner.','Canonical broad layout maintained; all production detail originates from actual native AI outputs with recorded limited registration where used.'],'pending':['North2957 rows not filled','West r07_c08 external neighbour unavailable','Full external boundaries, geometry/navigation and runtime acceptance pending']}
(Q/'visual-review.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
print(sha(Q/'visual-review.json'))
