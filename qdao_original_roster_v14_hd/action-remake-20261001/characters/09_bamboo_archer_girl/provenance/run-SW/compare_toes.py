import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
base=Path(__file__).resolve().parents[2]
other=base.parent/'07_moon_shadow_assassin_girl'
rows=[]
for action,count,direction,out in [('run',16,'SW',base/'provenance/run-SW'),('hit',6,'W',base/'provenance/combat-W'),('attack',12,'W',base/'provenance/combat-W'),('cast',16,'W',base/'provenance/combat-W')]:
 sheet=Image.new('RGB',(1536,200*((count+3)//4)*2),(235,239,235));d=ImageDraw.Draw(sheet)
 for n in range(1,count+1):
  for role,root,folder in [('09',base,'runtime'),('07',other,'frames')]:
   p=root/folder/action/direction/f'{n:02}.png'
   im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,(235,239,235,255));bg.alpha_composite(im)
   # Diagnostic lower-body crop only; original animation frames are untouched.
   w,h=im.size;crop=bg.crop((int(w*.15),int(h*.48),int(w*.82),h)).convert('RGB').resize((260,180))
   x=(n-1)%4*384;y=((n-1)//4*2+(role=='07'))*200
   sheet.paste(crop,(x+62,y));d.text((x+5,y+182),f'{role} {action}/{direction}/{n:02}',fill=(20,35,20))
   rows.append({'role':role,'action':action,'direction':direction,'frame':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 sheet.save(out/f'{action}-toe-comparison.png')
(base/'provenance/run-SW/toe-comparison-sources.json').write_text(json.dumps({'note':'Read-only reference comparison. 07 formal sources resolved from its manifest frames paths; no runtime directory exists. Crops are diagnostic only.','sources':rows},ensure_ascii=False,indent=2),encoding='utf-8')
