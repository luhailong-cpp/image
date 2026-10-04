from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[2];A=B/'audit/archer-reference'
rows=json.loads((A/'nw-sw-supportfix-selection.json').read_text(encoding='utf-8'))['rows']
mapping={'run/NW/07':'run-NW-10-supportfix-v2','run/NW/08':'run-NW-08-supportfix-v4','run/NW/09':'run-NW-07-supportfix-v4','run/NW/10':'run-NW-09-supportfix-v1','run/NW/11':'run-NW-11-final-transition-v2'}
def thumb(path,size=384):
 im=Image.open(path).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda v:0 if v<=8 else v))
 rt=Image.new('RGBA',(1024,1024));rt.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
 return rt.resize((size,size),Image.Resampling.LANCZOS)
for mode in ['old','new']:
 out=Image.new('RGB',(1536,832),(225,228,226));draw=ImageDraw.Draw(out)
 for i,f in enumerate(range(7,15)):
  r=next(x for x in rows if x['slot']==f'run/NW/{f:02}')
  key=mapping.get(r['slot'],r['candidateKey']) if mode=='new' else r['candidateKey']
  im=thumb(B/'sources/new'/f'{key}.png')
  x=i%4*384;y=i//4*416
  out.paste(im,(x,y+28),im);draw.text((x+4,y+5),f'NW {f:02} {mode}: {key}',fill='black')
 out.save(A/f'ns-final-nwsw-NW-reorder-{mode}.png')
print('wrote comparison')

