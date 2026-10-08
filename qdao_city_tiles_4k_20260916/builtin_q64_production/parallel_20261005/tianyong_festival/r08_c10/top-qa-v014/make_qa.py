from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
cp=json.loads((T/'r08_c10/current/v014/source-checkpoint.json').read_text(encoding='utf-8-sig'));r=cp['fragment'];assert sha(r['file'])==r['sha256']
im=Image.open(r['file']).convert('RGBA');a=np.array(im)
assert np.all(a[:1139,:,3]==255)
spec=[]
for i,x in enumerate([0,1024,2048,2842],1):spec.append((f'row1-window-{i}',[x,0,x+1254,1139]))
for x in [909,1933,2957]:spec.append((f'join-x{x}',[x-200,0,x+350,1139]))
for i,x in enumerate([0,1024,2048,2842],1):spec.append((f'top-{i}',[x,0,x+1254,240]));spec.append((f'lower-return-{i}',[x,909,x+1254,1254]))
qa=[]
for name,box in spec:
 out=P/(name+'.png');im.crop(box).save(out)
 rec={**ref(out),'derivedFrom':[r],'operation':'Native1:1 crop; transparent missing pixels preserved','nativeScale':1,'tileLocalLTRB':box,'globalLTRB':[36864+box[0],28672+box[1],36864+box[2],28672+box[3]],'newModelCalls':0,'formalAccepted':False}
 (P/(name+'.png.generation.json')).write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');qa.append(rec)
(P/'qa-index.json').write_text(json.dumps({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':r,'sourceCheckpoint':ref(T/'r08_c10/current/v014/source-checkpoint.json'),'reviewScopeTileLocalLTRB':[0,0,4096,1139],'opaqueKnownPixels':4096*1139,'qa':qa,'formalAccepted':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qaDir':str(P),'source':r,'count':len(qa)}))
