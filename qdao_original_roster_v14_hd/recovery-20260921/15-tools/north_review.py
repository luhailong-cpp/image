from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1]
out=R/'15-review';out.mkdir(exist_ok=True)
for d in ['N','NE']:
 rows=[(i,R/'15-delivery-preview/runtime/walk'/d/f'{i:02}.png') for i in range(1,17)]
 rows=[(i,p) for i,p in rows if p.exists()]
 for bg,name in [((240,234,220),'light'),((24,34,44),'dark')]:
  sheet=Image.new('RGB',(1024,1120),bg);s=ImageDraw.Draw(sheet)
  feet=Image.new('RGB',(1360,1040),bg);f=ImageDraw.Draw(feet)
  seam=Image.new('RGB',(1024,512),bg);sd=ImageDraw.Draw(seam)
  for i,p in rows:
   im=Image.open(p).convert('RGBA');x=((i-1)%4)*256;y=((i-1)//4)*280
   small=im.resize((256,256),Image.Resampling.LANCZOS);sheet.paste(small,(x,y+24),small);s.text((x+8,y+5),f'{d}{i:02}',fill=(80,160,180))
   crop=im.crop((342,710,682,970));xf=((i-1)%4)*340;yf=((i-1)//4)*260;feet.paste(crop,(xf,yf),crop);f.text((xf+8,yf+5),f'{d}{i:02}',fill=(80,160,180))
   if i in [15,16,1,2]:
    xx=[15,16,1,2].index(i)*256;seam.paste(small,(xx,24),small);crop=im.crop((384,730,640,962));seam.paste(crop,(xx,280),crop);sd.text((xx+8,5),f'{d}{i:02}',fill=(80,160,180))
  sheet.save(out/f'{d}-candidates-{name}.png');feet.save(out/f'{d}-feet-{name}.png');seam.save(out/f'{d}-seam-{name}.png')
 (out/f'{d}-review-sources.json').write_text(json.dumps([{'frame':i,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for i,p in rows],indent=2),encoding='utf-8')
