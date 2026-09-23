from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[3]
P=R/'qdao_original_roster_v14_hd/recovery-20260921/05-delivery-preview/revisions/complete-review-v1'
O=R/'qdao_original_roster_v14_hd/recovery-20260921/05-audit/root-static'
O.mkdir(exist_ok=True)
for d in ['NE','SE','SW','W']:
 for mode,c in [('dark',(30,38,46)),('light',(240,238,228))]:
  im=Image.new('RGB',(1920,1200),c); draw=ImageDraw.Draw(im)
  for i in range(16):
   a=Image.open(P/f'runtime/walk/{d}/{i+1:02d}.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
   a=a.crop((280,650,760,920 if d=='NE' else 920))
   # all boot bottoms at942; include full region
   a=Image.open(P/f'runtime/walk/{d}/{i+1:02d}.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS).crop((280,660,760,950))
   x,y=(i%4)*480,(i//4)*300
   im.paste(a,(x,y+10),a); draw.text((x+5,y),f'{d}{i+1:02d}',fill='white' if mode=='dark' else 'black')
  im.save(O/f'{d}-legs-{mode}.png')
print(O)
