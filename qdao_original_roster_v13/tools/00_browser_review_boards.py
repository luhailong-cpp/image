from PIL import Image,ImageDraw
from pathlib import Path
r=Path(r'E:\work\image\qdao_original_roster_v13\review\00_reference_topright_boy\browser-final-candidate')
for d in ['N','NE','E','SE','S','SW','W','NW']:
 ims=[Image.open(r/f'{d}-large-canvas-{n:02d}.png').convert('RGB') for n in [1,5,9,13]]
 w,h=ims[0].size;sheet=Image.new('RGB',(w*2,(h+24)*2),(38,44,45));draw=ImageDraw.Draw(sheet)
 for i,im in enumerate(ims):
  x=(i%2)*w;y=(i//2)*(h+24);sheet.paste(im,(x,y));draw.text((x+10,y+h+4),f'{d} / {[1,5,9,13][i]:02d}',fill='white')
 sheet.save(r/f'{d}-large-keys.jpg',quality=87)
 print(d,sheet.size)
