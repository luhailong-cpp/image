from PIL import Image,ImageDraw
from pathlib import Path
r=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy")
names=['16-v1','01-v1','02-v2','03-v2','05-v8','06-v4','07-v2','08-v4','09-v5','08-v3','10-v2','11-v1','13-v4','14-v2','15-v2','16-v2']
for lower in [False,True]:
 w,h=(314,370) if not lower else (400,330)
 canvas=Image.new('RGB',(4*w,4*h),(234,233,226));draw=ImageDraw.Draw(canvas)
 for i,n in enumerate(names):
  im=Image.open(r/'generation/run/NE'/(n+'.png')).convert('RGBA')
  if lower: im=im.crop((350,830,1030,1254));im.thumbnail((390,290))
  else: im.thumbnail((314,314))
  x=(i%4)*w+(w-im.width)//2;y=(i//4)*h+35
  canvas.paste(im,(x,y),im);draw.text(((i%4)*w+8,(i//4)*h+8),f'{i+1:02} {n} '+('R' if i<8 else 'L')+' '+(['front','front','middle','middle','middle','middle','rear','rear'][i%8]),fill=(0,0,0))
 target=r/'review/grounding-fourframes'/('NE-candidate-'+('legs' if lower else 'full')+'.jpg');canvas.save(target,quality=93)
print('derived review only')

