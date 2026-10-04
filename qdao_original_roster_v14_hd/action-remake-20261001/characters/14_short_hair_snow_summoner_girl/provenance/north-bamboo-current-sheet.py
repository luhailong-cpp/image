from PIL import Image, ImageDraw
from pathlib import Path
import hashlib,json
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
for d in ['N','NE','NW']:
    out=Image.new('RGB',(2048,2200),'#677578');dr=ImageDraw.Draw(out);records=[]
    for i in range(16):
        f=f'{i+1:02}';p=R/'run'/d/(f+'.png');sha=hashlib.sha256(p.read_bytes()).hexdigest()
        im=Image.open(p).convert('RGBA').resize((512,512));x=i%4*512;y=i//4*550
        out.paste(im,(x,y+30),im);dr.text((x+10,y+10),d+' '+f+' '+sha[:12],fill='white')
        records.append({'file':str(p.relative_to(R)).replace('\\','/'),'sha256':sha})
    out.save(R/'run/staging'/f'north-bamboo-current-{d}.jpg')
    (R/'run/staging'/f'north-bamboo-current-{d}.jpg.sources.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Current 48-frame contact sheets created, source SHA recorded; formal images unchanged')
