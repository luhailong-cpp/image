from pathlib import Path
from PIL import Image
import hashlib,json
T=Path(__file__).resolve().parent.parent
O=T/'review'/'p02_03-recheck-after-upper-fix-20261016'
O.mkdir(exist_ok=False)
versions=['p01_03_v20261016T203925_nativefix_c5d5b00d','p02_03_v20261016T192951_c60a3f55','p03_03_v20261016T200306_01ce9fc6']
sources=[T/'native'/f'{v}.png' for v in versions]
images=[Image.open(p).convert('RGB') for p in sources]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
outputs=[]
for i,name in enumerate(['top','bottom']):
    pair=Image.new('RGB',(1254,512))
    pair.paste(images[i].crop((0,883,1254,1139)),(0,0))
    pair.paste(images[i+1].crop((0,115,1254,371)),(0,256))
    p=O/f'{name}-core-pair.png';pair.save(p)
    outputs.append({'path':str(p),'sha256':sha(p),'seamY':256,'resize':False})
report={'sources':[{'path':str(p),'sha256':sha(p)} for p in sources],'outputs':outputs,'formalAccepted':False,'visualQA':'pending'}
(O/'evidence.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
