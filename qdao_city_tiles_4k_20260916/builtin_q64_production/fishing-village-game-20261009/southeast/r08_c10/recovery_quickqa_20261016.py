from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent; Z=T.parent
Q=T/'qa'/'recovery-20261016-v1';Q.mkdir(parents=True,exist_ok=False)
def core(p):return Image.open(p).convert('RGB').crop((115,115,1139,1139))
records=[]
for pid,v in [('p41','v3'),('p43','v1'),('p44','v2')]:
    p=T/'native'/f'{pid}-{v}.png'; c=core(p)
    south=Z/'r09_c10'/'native'/f'p1{pid[2]}-v1.png'
    im=Image.new('RGB',(1024,512));im.paste(c.crop((0,768,1024,1024)),(0,0));im.paste(core(south).crop((0,0,1024,256)),(0,256));im.save(Q/f'{pid}-south.png')
    records.append({'candidate':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'south':str(south)})
im=Image.new('RGB',(512,1024));im.paste(core(T/'native/p43-v1.png').crop((768,0,1024,1024)),(0,0));im.paste(core(T/'native/p44-v2.png').crop((0,0,256,1024)),(256,0));im.save(Q/'p43-p44.png')
im=Image.new('RGB',(512,1024));im.paste(core(Z/'r08_c09/native/p44-v2.png').crop((768,0,1024,1024)),(0,0));im.paste(core(T/'native/p41-v3.png').crop((0,0,256,1024)),(256,0));im.save(Q/'p41-west.png')
(Q/'manifest.json').write_text(json.dumps({'method':'Unscaled native core strips only, seam at midpoint; QA only','records':records},indent=2),encoding='utf8')
print(str(Q))
