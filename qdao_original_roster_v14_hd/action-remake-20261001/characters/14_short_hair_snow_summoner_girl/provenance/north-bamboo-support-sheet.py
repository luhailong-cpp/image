from PIL import Image,ImageDraw
from pathlib import Path
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl")
for d in ['N','NE','NW']:
 fs=['01','02','03','04','09','10','11','12']
 out=Image.new('RGB',(4*512,2*550),'#677578');dr=ImageDraw.Draw(out)
 for i,f in enumerate(fs):
  im=Image.open(R/'run'/d/(f+'.png')).convert('RGBA').resize((512,512));x=i%4*512;y=i//4*550;out.paste(im,(x,y+30),im);dr.text((x+10,y+10),d+' '+f,fill='white')
 out.save(R/'run/staging'/f'north-bamboo-support-{d}.jpg')

