from PIL import Image,ImageDraw
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2]
for d in ('E','NE'):
 out=Image.new('RGB',(1280,960),'#d8dfdb'); draw=ImageDraw.Draw(out)
 sel=json.loads((R/'run-contact-revision-20261004'/d/'selection.json').read_text(encoding='utf-8-sig'))['slots']
 for n in range(1,17):
  key=f'run/{d}/{n:02}'; p=R/sel.get(key,f'runtime/run/{d}/{n:02}.png')
  im=Image.open(p).convert('RGBA').resize((1024,1024)); im=im.crop((250,690,820,985)); im.thumbnail((310,205))
  x=((n-1)%4)*320;y=((n-1)//4)*240
  out.paste(im,(x,y+30),im);draw.text((x+10,y+8),f'{d} {n:02}',fill='black')
 out.save(R/'run-contact-revision-20261004'/d/'feet-review.jpg')
