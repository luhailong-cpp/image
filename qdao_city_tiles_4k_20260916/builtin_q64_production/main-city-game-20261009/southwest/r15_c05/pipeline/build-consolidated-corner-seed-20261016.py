from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parents[1]
seed=T/'pipeline/guides/p02_01.resume-20261016-v01.continuity-seed.png'
right=T/'native/p02_02.png';bottom=T/'native/p03_01.png'
out=T/'pipeline/guides/p02_01.consolidated-20261016-v02.continuity-seed.png'
assert not out.exists()
im=Image.open(seed).convert('RGB');r=Image.open(right).convert('RGB');b=Image.open(bottom).convert('RGB')
assert im.size==r.size==b.size==(1254,1254)
im.paste(r.crop((0,0,230,1254)),(1024,0))
im.paste(b.crop((0,0,1254,230)),(0,1024))
im.paste(Image.open(seed).crop((0,0,1254,230)),(0,0))
im.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d={'file':str(out),'sha256':sha(out),'pixels':[1254,1254],'category':'mechanical multi-neighbor continuity guidance only; never final artwork','resampling':False,'gameArt':False,'formalAccepted':False,'sources':[{'file':str(seed),'sha256':sha(seed),'operation':'base layout and top230 kept, upper priority'}, {'file':str(right),'sha256':sha(right),'sourceBox':[0,0,230,1254],'targetBox':[1024,0,1254,1254]}, {'file':str(bottom),'sha256':sha(bottom),'sourceBox':[0,0,1254,230],'targetBox':[0,1024,1254,1254]}],'nativeNeighborsAreProvisional':True,'cornerPriority':['upper','bottom','right']}
Path(str(out)+'.derivation.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d))
