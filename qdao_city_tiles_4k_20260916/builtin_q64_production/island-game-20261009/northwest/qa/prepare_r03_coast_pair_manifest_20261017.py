from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
reviewp=Z/'qa/r03_c01_v11_r03_c02_v7_shared_root_20261016/root_review.json'
rv=json.loads(reviewp.read_text()); assert sha(reviewp)=='58c66c9d4b6b5999ba6bc51bb22c3cac57d7dec44b5006c35ef5735aed6c3929'
tiles=[]
for s in [rv['left'],rv['right']]:
 for k in ['image','record']:assert sha(s[k]['path'])==s[k]['sha256']
 tiles.append({'tileId':s['tileId'],'image':pin(s['image']['path']),'record':pin(s['record']['path'])})
out={'schemaVersion':1,'topology':'adjacent-pair-v1','createdAtUtc':datetime.now(timezone.utc).isoformat(),'tiles':tiles,'scope':'Only already produced r03c01/r03c02 shared-edge repair; no other coordinates read into crop or modified.','priorSharedReview':pin(reviewp),'formalAccepted':False}
op=Z/'qa/r03_coast_pair_current-v1_20261017.manifest.json';assert not op.exists();op.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(pin(op)))
