from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[2]
for d in ('E','NE'):
 D=R/'run-contact-revision-20261004'/d;sel=json.loads((D/'selection.json').read_text(encoding='utf-8-sig'))['slots'];sheet=Image.new('RGB',(1280,1400),'#d8dfdb');draw=ImageDraw.Draw(sheet);rows=[]
 for n in range(1,17):
  key=f'run/{d}/{n:02}';p=R/sel[key];im=Image.open(p).convert('RGBA');rawsha=hashlib.sha256(p.read_bytes()).hexdigest();im=im.resize((1024,1024),Image.Resampling.LANCZOS);x=((n-1)%4)*320;y=((n-1)//4)*350;small=im.resize((310,310));sheet.paste(small,(x,y+25),small);draw.text((x+10,y+6),key,fill='black');a=im.getchannel('A');rows.append({'slot':key,'file':sel[key],'sourceSHA256':rawsha,'size':Image.open(p).size,'mode':Image.open(p).mode,'exportedAlphaBBox32':a.point(lambda v:255 if v>=32 else 0).getbbox()})
 sheet.save(D/'full-review.jpg');assert len({x['sourceSHA256'] for x in rows})==16
 (D/'technical-review.json').write_text(json.dumps({'frames':rows,'uniqueSourceCount':16,'retention':'check-*.png are QA derivatives, remove after current runtime verified'},indent=2),encoding='utf-8')
