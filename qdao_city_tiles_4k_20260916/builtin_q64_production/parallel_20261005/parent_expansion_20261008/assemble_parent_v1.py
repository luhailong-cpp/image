from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,numpy as np
E=Path(__file__).resolve().parent
T=E.parent/'tianyong_festival'
O=E/'integration-v1';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sel=T/'r08_c10/current/v015/candidate-set.json'
s=json.loads(sel.read_text(encoding='utf-8-sig'))
src=next(c for c in s['candidates'] if c['tile']=='r08_c10')
a=Image.open(src['file']).convert('RGBA')
patches=[]
for name,box,clip in [('r02_c01',(-115,909,1139,2163),(0,909,1024,2163)),('r02_c03',(1933,909,3187,2163),(2048,909,3187,2163))]:
 p=E/name/('edge-fix-v2/joined.png' if name=='r02_c01' else 'joined.png');im=Image.open(p).convert('RGBA')
 l,t,r,b=clip; crop=(l-box[0],t-box[1],r-box[0],b-box[1])
 a.paste(im.crop(crop),(l,t))
 patches.append(dict(file=str(p),sha256=sha(p),window=list(box),clip=list(clip),sourceCrop=list(crop)))
out=O/'assembled.png';a.save(out)
prev=a.copy();prev.thumbnail((1024,1024));prev.save(O/'preview.png')
for name,box in [('c01-c02-upper',(400,850,1654,2104)),('c02-c03-lower',(1510,1160,2764,2414))]:
 a.crop(box).save(O/(name+'.png'))
rec=dict(file=str(out),sha256=sha(out),generatedAt=datetime.now(timezone.utc).isoformat(),operation='native 1:1 mechanical provisional assembly; cut line at x1024 and2048, no acceptance',derivedFrom=[dict(file=src['file'],sha256=src['sha256'],generationRecord=src['generationRecord'])]+patches,sourceSelection=dict(file=str(sel),sha256=sha(sel)),coveragePixels=int((np.asarray(a)[:,:,3]==255).sum()),formalAccepted=False)
(O/'assembly.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps(rec))
