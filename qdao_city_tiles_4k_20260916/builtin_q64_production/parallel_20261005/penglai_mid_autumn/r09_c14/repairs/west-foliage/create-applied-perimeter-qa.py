from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
T=Path(__file__).resolve().parents[2]
R=Path(__file__).resolve().parent
P=T/'output/r09_c14-candidate.png'
W=T.parent/'output/r09_c13/r09_c13.png'
Q=R/'applied-perimeter-qa'
Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=Image.open(P).convert('RGB')
w=Image.open(W).convert('RGB')
assert sha(P)=='26ef781afe2fe0d6d8352f4a6f57e88780b93a7ed26cb41411efbc35d44432dc'
sources=[{'file':str(P),'sha256':sha(P)},{'file':str(W),'sha256':sha(W)}]
specs=[
 ('top-return',[-128,1005,535,1165]),
 ('bottom-return',[-128,2189,535,2349]),
 ('right-return-upper',[375,1005,535,1677]),
 ('right-return-lower',[375,1677,535,2349]),
 ('upper-leaf-contact',[-128,1320,330,1800])
]
items=[]
for name,box in specs:
 x0,y0,x1,y1=box
 im=Image.new('RGB',(x1-x0,y1-y0))
 if x0<0:im.paste(w.crop((4096+x0,y0,4096,y1)),(0,0))
 im.paste(c.crop((max(0,x0),y0,x1,y1)),(max(0,-x0),0))
 f=Q/(name+'.png');im.save(f)
 record={'file':str(f),'sha256':sha(f),'createdAt':datetime.now(timezone.utc).isoformat(),'dimensions':list(im.size),'operation':'exact unrotated native crop; negative candidate x is immutable west neighbor','candidateRectLTRB':box,'pixelScale':1,'upscaled':False,'derivedFrom':sources if x0<0 else sources[:1],'generator':{'file':str(Path(__file__).resolve()),'sha256':sha(__file__)},'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None}
 Path(str(f)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 items.append({'file':str(f),'sha256':sha(f),'candidateRectLTRB':box})
(Q/'index.json').write_text(json.dumps({'candidate':sources[0],'fixedWest':sources[1],'items':items,'actuallyViewed':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(items))

