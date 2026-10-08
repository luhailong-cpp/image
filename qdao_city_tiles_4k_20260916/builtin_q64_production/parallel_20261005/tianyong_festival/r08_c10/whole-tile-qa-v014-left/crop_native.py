from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;T=O.parent.parent;CPF=T/'r08_c10/current/v014/source-checkpoint.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
cp=json.loads(CPF.read_text(encoding='utf-8-sig'));ref=cp['fragment'];assert sha(ref['file'])==ref['sha256']
im=Image.open(ref['file']).convert('RGBA');assert im.size==(4096,4096);index=[]
def crop(n,b):
 p=O/(n+'.png');c=im.crop(b);c.save(p)
 record={**info(p),'derivedFrom':[ref],'operation':'Exact native crop; no transform, repaint, rescale or composition','nativeScale':1,'newModelCalls':0,'tileLocalLTRB':b,'fullyOpaque':bool(np.all(np.asarray(c)[:,:,3]==255)),'formalAccepted':False}
 (O/(n+'.png.generation.json')).write_text(json.dumps(record,indent=2),encoding='utf8');index.append(record)
for x in [0,1024,2048,3072]:crop(f'bottom-horizontal-x{x}',[x,2780,x+1024,3280])
for l,r,tag in [(709,1224,'x909-1024'),(1733,2248,'x1933-2048')]:
 for y in [0,1024,2048,3072]:crop(f'vertical-{tag}-y{y}',[l,y,r,y+1024])
for x,y in [(909,2957),(1024,3072),(1933,2957),(2048,3072),(1024,2048),(2048,2048),(3072,3072)]:crop(f'junction-x{x}-y{y}',[x-256,y-256,x+256,y+256])
crop('left-bottom-geometry',[0,1933,1139,3072])
crop('left-bottom-tail',[0,2957,1139,4096])
crop('center-bottom-geometry',[909,2330,2163,3584])
crop('suspect-x2163-y1980',[2020,1933,2300,2110])
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCheckpoint':info(CPF),'source':ref,'scope':'r08c10 native left and lower covered internal seams; no c09 audit in this package','crops':index,'rootCheckpointUnmodified':True,'onlyDerivedCropsWritten':True}
(O/'crop-index.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps({'crops':len(index),'source':ref['sha256'],'allSourceHashStillMatches':sha(ref['file'])==ref['sha256']}))
