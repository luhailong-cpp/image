from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[2]
for d in ['S','SW','SE']:
 sheet=Image.new('RGB',(1536,1600),(38,43,51))
 entries=[]
 for n in range(1,17):
  p=R/'run'/d/f'{n:02}.png'; im=Image.open(p).convert('RGBA')
  tile=Image.new('RGBA',(384,400),(38,43,51,255));tile.alpha_composite(im.resize((384,384)),(0,16));dr=ImageDraw.Draw(tile);dr.text((5,2),f'{d} {n:02}',fill='white');dr.line((0,16+942*384/1024,384,16+942*384/1024),fill=(200,80,80),width=1);sheet.paste(tile.convert('RGB'),(((n-1)%4)*384,((n-1)//4)*400))
  entries.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'alphaBBox':im.getchannel('A').getbbox()})
 sheet.save(R/'run'/d/'current-contact.jpg',quality=94)
 (R/'run'/d/'technical.json').write_text(json.dumps(entries,indent=2))

