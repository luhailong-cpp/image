from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
E=Path(__file__).resolve().parent;T=E.parent/'tianyong_festival'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
progress=json.loads((T/'progress.json').read_text(encoding='utf-8-sig'));sel=Path(progress['candidateSet']);s=json.loads(sel.read_text(encoding='utf-8-sig'))
new=next(c for c in s['candidates'] if c['tile']=='r08_c10');old=T/'r08_c10/current/v015/r08_c10-fragment.png'
a=np.asarray(Image.open(old).convert('RGBA'));b=np.asarray(Image.open(new['file']).convert('RGBA'));d=np.any(a!=b,axis=2);y,x=np.where(d)
nativeAdded=(b[:,:,3]==255)&(a[:,:,3]!=255)
record=dict(checkedAt=datetime.now(timezone.utc).isoformat(),childProgress=progress,childSelection=dict(file=str(sel),sha256=sha(sel)),parentBoundBase=dict(file=str(old),sha256=sha(old)),childCurrent=new,changedPixels=int(d.sum()),newOpaquePixels=int(nativeAdded.sum()),changedBBox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None,decision='New child c03 is a competing independently drawn patch over parent c03; do not merge these geometries. Keep child selection unchanged; parent candidate remains explicitly separately selected and provenance-bound to v015. Parent includes native completion and localized repairs across its own selected geometry.',formalAccepted=False)
(E/'current/child-latest-comparison.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['changedPixels','newOpaquePixels','changedBBox','decision']}))
