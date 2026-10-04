from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
r=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy")
maps={'N':['01-v4','16-v2','02-v2','03-v3','05-v4','06-v9','07-v3','08-v4','08-v2','09-v1','10-v2','05-v3','13-v4','03-v1','16-v3','15-v4']}
for d,names in maps.items():
 for lower in [False,True]:
  w,h=(314,370) if not lower else (400,330)
  canvas=Image.new('RGB',(4*w,4*h),(234,233,226));draw=ImageDraw.Draw(canvas)
  for i,n in enumerate(names):
   im=Image.open(r/'generation/run'/d/(n+'.png')).convert('RGBA')
   if lower: im=im.crop((360,830,960,1254));im.thumbnail((390,290))
   else: im.thumbnail((314,314))
   x=(i%4)*w+(w-im.width)//2;y=(i//4)*h+35
   canvas.paste(im,(x,y),im);draw.text(((i%4)*w+8,(i//4)*h+8),f'{i+1:02} {n} '+('R' if i<8 else 'L')+' '+(['front','front','middle','middle','middle','middle','rear','rear'][i%8]),fill=(0,0,0))
  target=r/'review/grounding-fourframes'/('N-candidate-'+('legs' if lower else 'full')+'.jpg');canvas.save(target,quality=93)
print('derived review only')


