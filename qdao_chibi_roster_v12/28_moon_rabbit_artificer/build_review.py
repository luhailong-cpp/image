from PIL import Image,ImageDraw
from pathlib import Path
ROOT=Path(__file__).resolve().parent
for dirs in [('N','S'),('E','W'),('NE','SW'),('NW','SE')]:
 out=Image.new('RGB',(2048,2048),'#cec8b9')
 for row,d in enumerate(dirs):
  for i in range(8):
   with Image.open(ROOT/'walk'/d/f'{i+1:02d}.png') as opened: im=opened.convert('RGBA')
   out.paste(im,(i%4*512,(row*2+i//4)*512),im)
   ImageDraw.Draw(out).text((i%4*512+12,(row*2+i//4)*512+8),f'{d} {i+1:02d}',fill='black')
 out.thumbnail((1500,1500));out.save(ROOT/'processing'/('-'.join(dirs)+'-final-review.jpg'),quality=88)
out=Image.new('RGB',(2048,1024),'#cec8b9')
for i,d in enumerate(['N','NE','E','SE','S','SW','W','NW']):
 with Image.open(ROOT/'idle'/f'{d}.png') as opened: im=opened.convert('RGBA')
 out.paste(im,(i%4*512,i//4*512),im);ImageDraw.Draw(out).text((i%4*512+12,i//4*512+8),d,fill='black')
out.thumbnail((1500,1500));out.save(ROOT/'processing/idle-final-review.jpg',quality=88)
print('Wrote four direction pairs and idle review from actual final PNGs')
