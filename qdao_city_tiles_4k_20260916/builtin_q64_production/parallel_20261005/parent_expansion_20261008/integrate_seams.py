from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
E=Path(__file__).resolve().parent
O=E/'integration-v2';O.mkdir(exist_ok=True);(O/'qa').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=E/'integration-v1/assembled.png';a=Image.open(base).convert('RGBA')
sources=[]
def feather_rect(box,w):
 y,x=np.mgrid[:1254,:1254];l,t,r,b=box
 d=np.minimum.reduce([x-l,r-x,y-t,b-y]);return np.clip(d/w,0,1)
for name,xy,box,w in [('seam-12',(400,850),(540,50,750,1244),40),('seam-23',(1510,1160),(458,20,625,1220),32)]:
 p=E/name/'native.png';g=Image.open(p).convert('RGBA');assert g.size==(1254,1254)
 before=a.crop((*xy,xy[0]+1254,xy[1]+1254))
 mask=Image.fromarray((feather_rect(box,w)*255).round().astype('uint8'))
 joined=Image.composite(g,before,mask);a.paste(joined,xy)
 mp=O/(name+'-mask.png');mask.save(mp)
 sources.append(dict(file=str(p),sha256=sha(p),generationRecord=str(p)+'.generation.json',pasteXY=xy,mask=dict(file=str(mp),sha256=sha(mp)),nativeScale=1,resampling=False))
out=O/'r08_c10.png';a.save(out)
rec=dict(file=str(out),sha256=sha(out),width=4096,height=4096,operation='Two AI native seam corrections applied through bounded 32/40px texture blend masks. No geometric resampling or resizing.',derivedFrom=[dict(file=str(base),sha256=sha(base),generationRecord=str(E/'integration-v1/assembly.json'))]+sources,actualModel=None,actualQuality=None,formalAccepted=False)
(O/'r08_c10.png.generation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
qas=[]
for name,box in [('seam12-upper',(930,870,1150,1450)),('seam12-cross',(880,1450,1240,1850)),('seam12-lower',(920,1780,1160,2250)),('seam23-upper',(1950,870,2200,1350)),('seam23-center',(1920,1280,2250,1830)),('seam23-bottom',(1920,1800,2300,2250)),('seam23-tail',(1920,2180,2250,2470))]:
 q=O/'qa'/(name+'.png');a.crop(box).save(q);qas.append(dict(file=str(q),sha256=sha(q),cropLTRB=box,nativeScale=1,actuallyViewed=False))
(O/'manifest.json').write_text(json.dumps(dict(createdAt=datetime.now(timezone.utc).isoformat(),output=rec,qa=qas,coveragePixels=int((np.asarray(a)[:,:,3]==255).sum()),status='pending_visual_review_and_outer_repairs',formalAccepted=False),indent=2),encoding='utf-8')
pr=a.copy();pr.thumbnail((1024,1024));pr.save(O/'preview.png')
print(json.dumps({'file':str(out),'sha256':sha(out),'qa':len(qas)}))
