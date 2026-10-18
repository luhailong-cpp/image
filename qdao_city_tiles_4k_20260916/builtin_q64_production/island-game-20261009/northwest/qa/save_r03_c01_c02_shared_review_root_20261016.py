from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1];qd=Z/'qa/r03_c01_v11_r03_c02_v7_shared_root_20261016'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
qp=qd/'qa_index.json';q=json.loads(qp.read_text());assert sha(qp)=='2af2ffc3f6c6f47994df676eae00bbbf1d76c16ae7c873cb9c90c1e152fca6bd'
notes=[('PENDING','PENDING','Along shared x=240 near y730-800, leaf/rock tone and contour step reveal a vertical join. Upper cliff outline broadly aligns.'),('PENDING','PENDING','Shared x=240 bisects the stone finial and pedestal. Abrupt light/material change across finial; pedestal moulding lip has a small offset near shared local y650-700.'),('PASS','PENDING','Major wall, foliage and diagonal path geometry continue. Pale stone texture or brightness remains visibly split at the upper border.'),('PENDING','PENDING','Diagonal paving grout at shared x=240 near local y35 has a short step. Remaining planter, flowers and lower stone balustrade contours align.')]
reviews=[]
for a,(g,m,n) in zip(q['items'],notes):
 assert sha(a['path'])==a['sha256'];reviews.append({**a,'actuallyViewedAtNativeScale':True,'geometryStatus':g,'materialStatus':m,'observation':n})
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','qaIndex':{'path':qp.as_posix(),'sha256':sha(qp)},'left':q['left'],'right':q['right'],'sharedEdgePixelsCovered':4096,'reviews':reviews,'sharedGeometryAccepted':False,'sharedMaterialAccepted':False,'formalAccepted':False,'note':'This is shared outer-edge QA. The separate 33 internal seam passes remain valid for unchanged tile pixels; they do not constitute cross-tile acceptance. No image edited by this review.','nextRepairGroups':['Upper leaf and stone boundary','Finial lighting and pedestal moulding join','Lower paving grout step']}
op=qd/'root_review.json';assert not op.exists();op.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'path':op.as_posix(),'sha256':sha(op)}))
