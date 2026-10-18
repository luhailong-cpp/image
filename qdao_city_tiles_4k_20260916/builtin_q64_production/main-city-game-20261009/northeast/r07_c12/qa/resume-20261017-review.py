from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
t=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['p21-v20261016','p33-fix1-v20261016','p33-fix2-v20261016']
r={'tile':'r07_c12','reviewedAt':datetime.now(timezone.utc).isoformat(),'route':'builtin','actualModel':None,'selectedCoreCount':9,'nativeVersionCount':11,'inflightGeneration':None,'reviewMethod':'actual native-sized integer core join crops; prior unchanged reviews reused','sources':[{ 'file':str(t/'native'/(n+'.png')),'sha256':sha(t/'native'/(n+'.png'))} for n in names],'findings':[{'patch':'p21','status':'quick_geometry_pass','note':'South diagonal slab joints continuous; mineral grain density remains for full-tile review.'},{'patch':'p33','status':'pending_P2_after_two_repairs','selected':'p33-fix2-v20261016.png','repairAttempts':2,'note':'Horizontal leaf clipping improved; east foliage continuous. South cream curb / blue paving shifts at join. Retain fix2 as working source, unpassed; no third repair in this pass.'},{'patch':'p34','status':'pending_P2','note':'Prior east lower pale/dark wall rectangular transition retained.'},{'patch':'p42','status':'held_geometry_conflict','note':'South neighbor blue band and east neighbor blue band disagree; no generation requested. See first-three-review-v20261016.json.'}],'internalPassed4kCount':0,'formalAcceptedCount':0}
out=t/'qa'/'resume-20261017-review.json'
assert not out.exists()
out.write_text(json.dumps(r,indent=2)+'\n')
v=json.loads((t/'tile-progress.json').read_text())
v.update(nativeVersionCount=11,lastReview=str(out),pendingCoordinates=['p42'],pendingRepairCoordinates=['p33','p34'],updatedAt=datetime.now(timezone.utc).isoformat())
(t/'tile-progress.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps({'report':str(out),'selected':v['selectedCoreCount'],'versions':11}))

