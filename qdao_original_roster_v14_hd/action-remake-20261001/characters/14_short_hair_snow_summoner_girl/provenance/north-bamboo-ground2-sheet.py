import json,sys,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
for d in sys.argv[1:] or ['N','NE','NW']:
 candidates={}
 for p in sorted((R/'provenance').glob('north-bamboo-ground2-batch*-receipts.json'),key=lambda p:int(p.name.split('batch')[1].split('-')[0])):
  for rc in json.loads(p.read_text(encoding='utf-8')):
   q=rc['q'];src=R/'run/staging'/(q['id']+'-registered.png')
   if q['direction']==d and src.exists():candidates[int(q['frame'])]=src
 out=Image.new('RGB',(2048,2200),'#667579');dr=ImageDraw.Draw(out);refs=[]
 for i in range(1,17):
  p=candidates.get(i,R/'run'/d/f'{i:02}.png');im=Image.open(p).convert('RGBA').resize((512,512));x=(i-1)%4*512;y=(i-1)//4*550;out.paste(im,(x,y+30),im)
  dr.text((x+10,y+9),f'{d}{i:02} P{((i-1)%8)//2+1} '+('candidate' if i in candidates else 'formal'),fill='white');refs.append({'frame':i,'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 out.save(R/'run/staging'/f'north-bamboo-ground2-proposed-{d}.jpg');(R/'run/staging'/f'north-bamboo-ground2-proposed-{d}.jpg.sources.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
 print(d+': '+str(len(candidates))+' candidates, remaining formal only; visual acceptance pending')
