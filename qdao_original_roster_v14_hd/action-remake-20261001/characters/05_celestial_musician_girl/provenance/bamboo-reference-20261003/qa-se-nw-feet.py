from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
r=Path(__file__).resolve().parents[2];out=Path(__file__).parent
snapshot=json.loads((out/'SE-NW-source-snapshot.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
# Original-pixel fixed lower-leg crop, no asset mutation.
for d in ['SE','NW']:
 for start in [1,9]:
  cvs=Image.new('RGB',(1600,1480),(225,229,232));dr=ImageDraw.Draw(cvs)
  for i,n in enumerate(range(start,start+8)):
   for who,col in [('bamboo',0),('musician',1)]:
    row=next(x for x in snapshot['rows'] if x['character']==who and x['direction']==d and x['frame']==n)
    im=Image.open(row['path']).convert('RGBA').crop((220,680,1020,1000))
    x=col*800;y=i//2*370
    # two pages: each row paired by character, 4 numbered frames per page
    if i%2==1: continue
    cvs.paste(im,(x,y+35),im);dr.text((x+8,y+5),f'{who} {d}{n:02d} original px lower-leg',font=font,fill=(10,10,10))
  cvs.save(out/f'feet-{d}-{start:02d}-odd.jpg',quality=98)
  cvs=Image.new('RGB',(1600,1480),(225,229,232));dr=ImageDraw.Draw(cvs)
  for i,n in enumerate(range(start,start+8)):
   if i%2==0: continue
   for who,col in [('bamboo',0),('musician',1)]:
    row=next(x for x in snapshot['rows'] if x['character']==who and x['direction']==d and x['frame']==n)
    im=Image.open(row['path']).convert('RGBA').crop((220,680,1020,1000))
    x=col*800;y=i//2*370
    cvs.paste(im,(x,y+35),im);dr.text((x+8,y+5),f'{who} {d}{n:02d} original px lower-leg',font=font,fill=(10,10,10))
  cvs.save(out/f'feet-{d}-{start:02d}-even.jpg',quality=98)

