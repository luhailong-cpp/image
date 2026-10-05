from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parents[2];B=R.parent/'09_bamboo_archer_girl'
rows=[]
for d in ('S','SE','SW'):
 for kind,root,crop in [('snow',R/'run',(180,690,910,1024)),('bamboo',B/'runtime/run',(180,580,910,1024))]:
  out=Image.new('RGB',(1600,1160),(235,238,239));draw=ImageDraw.Draw(out)
  for n in range(1,17):
   p=root/d/f'{n:02}.png';im=Image.open(p).convert('RGBA');h=hashlib.sha256(p.read_bytes()).hexdigest()
   x=(n-1)%4*400;y=(n-1)//4*290
   leg=im.crop(crop);leg.thumbnail((390,260))
   out.paste(leg,(x+(400-leg.width)//2,y),leg);draw.text((x+12,y+267),f'{kind} {d}/{n:02} '+h[:10],fill=(15,20,25))
   rows.append({'subject':kind,'direction':d,'frame':n,'file':str(p),'sha256':h})
  out.save(R/f'run/staging/video-axis-{kind}-{d}-legs.jpg',quality=96)
 out=Image.new('RGB',(1280,1408),(235,238,239));draw=ImageDraw.Draw(out)
 for n in range(1,17):
  im=Image.open(R/f'run/{d}/{n:02}.png').convert('RGBA').resize((320,320));x=(n-1)%4*320;y=(n-1)//4*352
  out.paste(im,(x,y),im);draw.text((x+8,y+326),f'current {d}/{n:02}',fill=(15,20,25))
 out.save(R/f'run/staging/video-axis-snow-{d}-full.jpg',quality=95)
(R/'run/staging/video-axis-south-input-hashes.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(len(rows))

