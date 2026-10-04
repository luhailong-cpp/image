from pathlib import Path
import json
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[2];A=B/'audit/archer-reference'
r=json.loads((A/'ns-pairs-review.json').read_text(encoding='utf-8'))['frames']
for d in ['N','S']:
 board=Image.new('RGB',(1536,1664),(225,228,226));draw=ImageDraw.Draw(board)
 for f in range(1,17):
  row=next(q for q in r if q['direction']==d and q['frame']==f)
  p=Path(row['source']);p=p if p.is_absolute() else B/p
  im=Image.open(p).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda v:0 if v<=8 else v))
  runtime=Image.new('RGBA',(1024,1024));runtime.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
  im=runtime.resize((384,384),Image.Resampling.LANCZOS)
  x=(f-1)%4*384;y=(f-1)//4*416
  board.paste(im,(x,y+28),im);draw.text((x+5,y+5),f'{d} {f:02}/16 75ms '+row['supportFoot']+' support',fill='black')
 board.save(A/f'ns-{d}-pairs-final-contact.png')
print('N/S final 16 full-frame contact boards written.')

