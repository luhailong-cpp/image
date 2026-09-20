from PIL import Image,ImageDraw
from pathlib import Path
r=Path(r'E:\work\image\qdao_original_roster_v13\review\00_reference_topright_boy\browser-final-candidate')
for d in ['N','NE','E','SE','S','SW','W','NW']:
 ims=[Image.open(r/f'{d}-large-canvas-{n:02d}.png').convert('RGB') for n in [15,16,1]]
 w,h=ims[0].size;sheet=Image.new('RGB',(w*3,h+28),(38,44,45));draw=ImageDraw.Draw(sheet)
 for i,im in enumerate(ims):sheet.paste(im,(i*w,0));draw.text((i*w+10,h+4),f'{d} / {[15,16,1][i]:02d}',fill='white')
 sheet=sheet.resize((1100,round(sheet.height*1100/sheet.width)));sheet.save(r/f'{d}-seam-review.jpg',quality=88)
