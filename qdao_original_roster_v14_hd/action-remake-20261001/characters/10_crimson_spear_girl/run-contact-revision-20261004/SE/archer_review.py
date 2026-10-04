from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).parents[2]
ar=root.parent/'09_bamboo_archer_girl'
for direction in ['SE','SW']:
 out=Image.new('RGB',(1600,1000),(210,212,219));d=ImageDraw.Draw(out)
 for idx in range(1,17):
  p=ar/f'runtime/run/{direction}/{idx:02d}.png'
  if not p.exists():continue
  im=Image.open(p).crop((230,600,830,1000)).resize((400,260))
  x=((idx-1)%4)*400;y=((idx-1)//4)*250
  out.paste(im,(x,y),im);d.text((x+8,y+8),f'{direction} {idx:02d}',fill='black')
 out.save(root/f'run-contact-revision-20261004/{direction}/archer-reference.jpg')
