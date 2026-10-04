from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
rows=json.loads((R/'run/staging/south-bamboo-oblique-candidate-registration.json').read_text())['frames']
sel={r['formalTarget']:r['file'] for r in rows}
for d in ('SW','SE'):
 out=Image.new('RGB',(1600,1160),(232,236,237));draw=ImageDraw.Draw(out)
 for n in range(1,17):
  formal=f'run/{d}/{n:02}.png'; p=R/sel.get(formal,formal)
  im=Image.open(p).convert('RGBA').crop((240,700,880,1010)).resize((400,258))
  x=(n-1)%4*400;y=(n-1)//4*290
  out.paste(im,(x,y),im);draw.text((x+10,y+264),f'{d} {n:02} / P{((n-1)%8)//2+1} expected '+('LEFT' if n<=8 else 'RIGHT'),fill=(15,20,30))
 out.save(R/f'run/staging/south-bamboo-contact-{d}-legs-review.jpg',quality=96)

