from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
findings={
 'west1':'Doorpost double edge removed and step joints redrawn coherently in the AI output; blend/registration return and exact old-left boundary still require masked merge inspection.',
 'west2':'Central paving seam and abrupt tone boundary are visually repaired in output; surface brushwork changed outside requested ROI, so only masked right-side pixels may be used.',
 'west3':'Rail meets the rounded post coherently in output, but the AI also moved the long paving joint on the left half to connect it. Exact x627 edge correspondence is NOT accepted; right-only masked insertion must be checked and may need a narrow targeted redraw.',
 'west4':'Orange roof ridge and tile highlights connected, and rail/post transition redrawn; old context is not pixel-identical and must remain original during masked merge.'
}
records=[]
for i in range(1,5):
    pid=f'west{i}';p=ROOT/f'{pid}.png';target=ROOT/f'{pid}-target.png'
    r=json.loads((ROOT/f'{pid}.png.generation.json').read_text(encoding='utf-8'))
    a=np.array(Image.open(p).convert('RGB'));b=np.array(Image.open(target).convert('RGB'))
    assert a.shape==b.shape==(1254,1254,3)
    diff=np.abs(a.astype(np.int16)-b.astype(np.int16));changed=np.any(diff!=0,axis=2)
    records.append(dict(id=pid,file=str(p),sha256=sha(p),pixels=[1254,1254],generationRecord=str(ROOT/f'{pid}.png.generation.json'),globalRectXYWH=r['globalRectXYWH'],target=str(target),targetSha256=sha(target),actuallyViewed=True,reviewScale='1254px native tool output',leftContextIdentical=not bool(changed[:,:627].any()),leftContextMeanAbsDifference=float(diff[:,:627].mean()),leftContextChangedPixelFraction=float(changed[:,:627].mean()),findings=findings[pid],sourceOnly=True,merged=False,formalAccepted=False))
out=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),nativeGenerationCount=4,records=records,allOutputsNative1254=True,noResizing=True,sourceCandidateSha256='8dad0387e60b7fd0d695c5907b5d637515fa5d72d0caf78856b40346c01c7908',sourceOldC12Sha256='59b31c2d193a71fdfe516ad9d51c6d2bfea3881f5670dd9f53ba2a612ad59fd2',scope='Review of each complete native AI repair output, not merged seam acceptance.',requiredNext='Root performs limited registration and right-only masked merge, retains exact old c12, then checks the entire shared edge and ROI returns. West3 paving joint needs special attention.',complete4KTileCount=0,formalAccepted=False)
(ROOT/'review.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps([dict(id=r['id'],pixels=r['pixels'],sha256=r['sha256'],leftContextMeanAbsDifference=round(r['leftContextMeanAbsDifference'],3)) for r in records]))
