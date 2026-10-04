from pathlib import Path
from PIL import Image,ImageDraw
import json
B=Path(__file__).resolve().parents[2]
for direction in ['NE','SE']:
 p=B/'grounding4'/direction/'selection-new.json'
 if not p.exists():continue
 rows=json.loads(p.read_text(encoding='utf-8'))
 c=Image.new('RGB',(1440,960),(226,226,219));d=ImageDraw.Draw(c)
 for i,src in enumerate(rows):
  im=Image.open(B/src).convert('RGBA');im=im.crop((250,655,800,1010));im.thumbnail((350,216))
  x=i%4*360;y=i//4*240;c.paste(im,(x+(360-im.width)//2,y+24),im);d.text((x+5,y+4),f'{direction} {i+1:02d} '+src.split('/')[-1],fill='black')
 c.save(B/'grounding4'/direction/'pairs-contact.jpg',quality=96)
