from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
B=Path(__file__).resolve().parents[2]
rows=json.loads((B/'audit/archer-reference/nw-sw-grounding-selection.json').read_text(encoding='utf-8-sig'))['rows']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for direction in ['NW','SW']:
 canvas=Image.new('RGB',(1280,1408),(225,230,227)); d=ImageDraw.Draw(canvas)
 for i,row in enumerate(r for r in rows if f'/{direction}/' in r['slot']):
  p=Path(row['file']); im=Image.open(p).convert('RGBA')
  if im.width==1254:
   out=Image.new('RGBA',(1024,1024)); out.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49));im=out
  thumb=im.resize((320,320),Image.Resampling.LANCZOS)
  x=i%4*320;y=i//4*352
  canvas.paste(thumb,(x,y+24),thumb)
  d.text((x+8,y+1),f"{direction} {i+1:02} {row['candidateKey'] or 'retained'}",font=font,fill=(20,35,35))
 canvas.save(B/f'audit/archer-reference/nw-sw-{direction}-grounding-contact.png')
