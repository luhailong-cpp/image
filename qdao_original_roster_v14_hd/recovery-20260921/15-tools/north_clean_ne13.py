from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];p=R/'15-delivery-preview/runtime/walk/NE/13.png';s=p.with_suffix('.png.generation.json');rec=json.loads(s.read_text(encoding='utf-8'));a=np.array(Image.open(p).convert('RGBA'));prior=hashlib.sha256(p.read_bytes()).hexdigest()
# Explicitly reviewed detached gray speck, wholly outside the body at final xy=355:366,927:933.
area=a[900:970,320:420];mask=area[:,:,3]>0;ys,xs=np.nonzero(mask);assert len(xs)==44 and (xs.min()+320,ys.min()+900,xs.max()+321,ys.max()+901)==(355,927,366,933)
area[mask]=0
out=R/'15-generation/NE13-walk-v1/processing-fixed088-v1/final-speck-clean-v2.png';Image.fromarray(a).save(out);p.write_bytes(out.read_bytes())
record={'operation':'remove_reviewed_detached_background_speck','roi':[320,900,420,970],'changedVisiblePixels':44,'changedBBox':[355,927,366,933],'preCleanSha256':prior,'postCleanSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'geometryChange':False,'poseChange':False,'translationChange':False,'reviewedAgainst':'15-review/NE-feet-light.png and dark equivalent','createdAt':datetime.now(timezone.utc).isoformat()}
rec['sha256']=record['postCleanSha256'];rec['operation']['postCleanup']=record;rec['operation']['finalAfterCleanupPath']=str(out);s.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8');(R/'15-review/NE13-speck-cleanup.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
