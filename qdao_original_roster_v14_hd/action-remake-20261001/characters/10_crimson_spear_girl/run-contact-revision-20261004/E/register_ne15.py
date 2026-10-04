from pathlib import Path
from PIL import Image
import json,hashlib,math
R=Path(__file__).resolve().parents[2]
D=R/'run-contact-revision-20261004/NE/15-rear-v1'
src=D/'native.png'; target=R/'run-contact-revision-20261004/NE/14-rear-v4/native.png'
P=[(647,360),(363,331),(747,790),(1230,1027)]
Q=[(538,467),(309,445),(621,816),(1004,1006)]
n=len(P); pm=[sum(p[k] for p in P)/n for k in (0,1)];qm=[sum(p[k] for p in Q)/n for k in (0,1)]
s=sum((p[k]-pm[k])*(q[k]-qm[k]) for p,q in zip(P,Q) for k in (0,1))/sum((p[k]-pm[k])**2 for p in P for k in (0,1))
t=[qm[k]-s*pm[k] for k in (0,1)]
errors=[math.dist((s*p[0]+t[0],s*p[1]+t[1]),q) for p,q in zip(P,Q)]
assert max(errors)<10
im=Image.open(src).convert('RGBA');f=1024/1254;size=round(1254*s*f);out=Image.new('RGBA',(1024,1024));out.alpha_composite(im.resize((size,size),Image.Resampling.LANCZOS),(round(t[0]*f),round(t[1]*f)))
p=D/'registered.png';out.save(p)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
meta={'file':p.relative_to(R).as_posix(),'sha256':sha(p),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','operation':'technical uniform registration of already independently AI-generated pose; no new animation frame created from registration','nativeEvidence':{'file':src.relative_to(R).as_posix(),'sha256':sha(src),'size':[1254,1254],'generationRecord':str(src.relative_to(R))+'.generation.json'},'derivedFrom':{'file':src.relative_to(R).as_posix(),'sha256':sha(src),'generationRecord':str(src.relative_to(R))+'.generation.json'},'registration':{'reference':target.relative_to(R).as_posix(),'referenceSHA256':sha(target),'method':'least-squares uniform scale and translation, manually identified head jewel, spear jewel, waist jade, spear butt anchors; no rotation/warp and no foot anchor','sourceAnchors':P,'targetAnchors':Q,'scaleAt1254':s,'translateAt1254':t,'residualPixels':errors,'maxAcceptedResidual':10,'outputResize':f},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed image generation response does not expose model/quality; this operation introduces no image generation','status':'registered-needs-visual-review'}
Path(str(p)+'.generation.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(json.dumps(meta['registration']))

