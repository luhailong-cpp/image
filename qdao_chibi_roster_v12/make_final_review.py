"""Compose actual final sprites on solid backgrounds for human QA; no sprite mutation."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse
p=argparse.ArgumentParser();p.add_argument('--character',required=True);a=p.parse_args();c=Path(__file__).resolve().parent/a.character;o=c/'processing';o.mkdir(exist_ok=True)
for dirs in [('N','S'),('E','W'),('NE','SW'),('NW','SE')]:
 out=Image.new('RGBA',(1536,1536),(213,208,193,255));dr=ImageDraw.Draw(out)
 for j,d in enumerate(dirs):
  for i in range(8):
   im=Image.open(c/'walk'/d/f'{i+1:02}.png').convert('RGBA');im=im.resize((384,384),Image.Resampling.LANCZOS);x=(i%4)*384;y=(j*2+i//4)*384;out.alpha_composite(im,(x,y));dr.text((x+10,y+10),f'{d}{i+1:02}',fill=(20,20,20,255))
 out.convert('RGB').save(o/f'root-review-{dirs[0]}-{dirs[1]}.jpg',quality=90)
out=Image.new('RGBA',(1536,768),(213,208,193,255));dr=ImageDraw.Draw(out)
for i,d in enumerate(['N','NE','E','SE','S','SW','W','NW']):
 im=Image.open(c/'idle'/f'{d}.png').convert('RGBA').resize((384,384),Image.Resampling.LANCZOS);x=(i%4)*384;y=(i//4)*384;out.alpha_composite(im,(x,y));dr.text((x+10,y+10),d,fill=(20,20,20,255))
out.convert('RGB').save(o/'root-review-idle.jpg',quality=90)
out=Image.new('RGBA',(1536,1024),(255,255,255,255));dr=ImageDraw.Draw(out)
for j,bg in enumerate([(24,36,39,255),(238,232,211,255)]):
 out.paste(bg,(0,j*512,1536,(j+1)*512))
 for i,f in enumerate([c/'walk/SW/04.png',c/'walk/NW/04.png',c/'portrait.png']):
  im=Image.open(f).convert('RGBA');im.thumbnail((512,512),Image.Resampling.LANCZOS);out.alpha_composite(im,(i*512,j*512))
out.convert('RGB').save(o/'root-review-edges.jpg',quality=92)
print(str(o))
