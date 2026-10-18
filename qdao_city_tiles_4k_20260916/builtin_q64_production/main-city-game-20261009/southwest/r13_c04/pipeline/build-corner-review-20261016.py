from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
T=Path(__file__).resolve().parents[1];Q=T/'pipeline/qa/p01_04-corner-20261016-v01';Q.mkdir(parents=True,exist_ok=True)
paths=[T/'guides/p01_04.layout-only.png',T/'pipeline/returns/p01_04.right-seeded-20261016-v01.png']
panel=Image.new('RGB',(1000,624),(30,30,30));draw=ImageDraw.Draw(panel)
for i,p in enumerate(paths):
 c=Image.open(p).crop((500,650,1000,1254));out=Q/f'crop-{i+1}.png';assert not out.exists();c.save(out);panel.paste(c,(i*500,20));draw.text((i*500+5,3),['approved layout only','returned native'][i],fill='white')
out=Q/'compare.png';assert not out.exists();panel.save(out)
(Q/'manifest.json').write_text(json.dumps({'sourceFiles':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'cropBox':[500,650,1000,1254],'resampling':False,'gameArt':False,'formalAccepted':False},indent=2)+'\n',encoding='utf-8')
print(out)
