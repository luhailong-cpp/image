from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json
from datetime import datetime,timezone
D=Path(__file__).parent;T=D.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp=T/'source-checkpoint.json'
assert sha(cp)=='1c786a95044e418d2304e19ab535141a6494f34242e7f562a9189f239e8c7244'
s=json.loads(cp.read_text(encoding='utf-8'))['fragment']
assert sha(s['file'])==s['sha256']
im=Image.open(s['file']).convert('RGBA'); a=np.array(im)
assert im.size==(4096,4096) and np.all(a[:,:,3]==255)
(D/'source-checkpoint.json').write_bytes(cp.read_bytes())
index=[];covered=np.zeros((4096,4096),bool)
for r,y in enumerate([0,1280,2560],1):
 for c,x in enumerate([0,1280,2560],1):
  box=[x,y,x+1536,y+1536];p=D/f'full-r{r}-c{c}.png'
  im.crop(box).save(p);covered[y:y+1536,x:x+1536]=True
  index.append({'id':f'full-r{r}-c{c}','image':info(p),'tileLocalLTRB':box,'nativeScale':1,'pixels':[1536,1536]})
assert covered.all()
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCheckpoint':info(D/'source-checkpoint.json'),'source':s,'nativeScale':1,'everyPixelIncluded':True,'coveragePixels':int(covered.sum()),'opaquePixels':int((a[:,:,3]==255).sum()),'images':index,'standardSeams':[1024,2048,3072],'actualPlacementSeams':[909,1139,1933,2163,2957,3187],'scalePolicy':'All review views are exact 1536x1536 source crops with no resizing, overlapping by256 pixels. Both axes use starts0,1280,2560, fully covering4096x4096 including all named seam crossings.'}
(D/'review-image-index.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'crops':len(index),'everyPixelIncluded':True,'source':s}))
