from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).parents[2]
for direction in ['SE','SW']:
 out=Image.new('RGB',(1600,1000),(210,212,219));d=ImageDraw.Draw(out)
 for idx in range(1,17):
  im=Image.open(root/f'runtime/run/{direction}/{idx:02d}.png')
  im=im.crop((260,630,810,990)).resize((400,260))
  x=((idx-1)%4)*400;y=((idx-1)//4)*250
  out.paste(im,(x,y),im);d.text((x+8,y+8),f'{direction} {idx:02d}',fill='black')
 out.save(root/f'run-contact-revision-20261004/{direction}/feet-original.jpg')
