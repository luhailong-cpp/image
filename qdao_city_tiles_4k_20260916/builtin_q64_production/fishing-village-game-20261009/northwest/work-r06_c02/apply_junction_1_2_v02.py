from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent.parent;W=B/'work-r06_c02'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
name='r06_c02_junction_1_2_v02';base=W/'joint-v1';O=W/'joint-v2';O.mkdir(exist_ok=True)
a=rd(base/'assembly.json');p=B/'native'/(name+'.png');g=rd(Path(str(p)+'.generation.json'))
old=np.asarray(Image.open(a['candidate']['file'])).copy();ids=np.asarray(Image.open(a['sourceIdMap']['file'])).copy()
new=np.asarray(Image.open(p));mask=np.ones((1254,1254),bool)
# Replay exactly the visually inspected hard-cut decisions, without blending.
for r in rd(W/'qa'/(name+'-edge60')/'mechanical.json')['directions']:
 d=r['direction'];cut=np.asarray(r['path']);take=np.arange(60)[None,:]>=cut[:,None] if d in 'nw' else np.arange(60)[None,:]<cut[:,None]
 if d=='n':mask[:60]=take.T
 elif d=='s':mask[-60:]=take.T
 elif d=='w':mask[:,:60]=take
 else:mask[:,-60:]=take
x,y=1421,397;sid=max(s['sourceId'] for s in a['sources'])+1
old[y:y+1254,x:x+1254][mask]=new[mask];ids[y:y+1254,x:x+1254][mask]=sid
a['sources'].append({'sourceId':sid,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(p)+'.generation.json'})
for s in a['sources']:
 yy,xx=np.where(ids==s['sourceId'])
 if not len(xx):continue
 im=np.asarray(Image.open(s['file']));box=s['globalNativeBox']
 assert np.array_equal(old[yy,xx],im[yy+20480-box[1],xx+4096-box[0]])
out=O/'r06_c02.candidate.png';mp=O/'r06_c02.source-id.png'
Image.fromarray(old).save(out);Image.fromarray(ids).save(mp)
a.update(candidate={'file':str(out),'sha256':sha(out)},sourceIdMap={'file':str(mp),'sha256':sha(mp)},proof={'pixels':16777216,'mismatches':0},status='candidate-pending-roof-top-and-patch-edge-repair',formalAccepted=False)
(O/'assembly.json').write_text(json.dumps(a,indent=2),encoding='utf-8')
Image.fromarray(old[y:y+1254,x:x+1254]).save(O/'joint.100pct.png')
print(json.dumps({'candidate':str(out),'sha256':sha(out),'mismatches':0}))
