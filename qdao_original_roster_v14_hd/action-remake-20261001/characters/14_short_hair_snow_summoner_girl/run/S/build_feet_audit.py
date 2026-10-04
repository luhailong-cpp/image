from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2]
for d in ['S','SW','SE']:
 out=Image.new('RGB',(1600,900),(38,40,48));dr=ImageDraw.Draw(out)
 for n in range(1,17):
  im=Image.open(R/'run'/d/f'{n:02}.png').convert('RGBA').crop((200,665,800,985))
  im.thumbnail((396,207));x=(n-1)%4*400;y=(n-1)//4*225
  out.paste(im,(x,y+18),im);dr.text((x+4,y+3),f'{d}{n:02}',fill='white')
 out.save(R/'run/S'/f'foot-audit-{d}.jpg',quality=95)
out=Image.new('RGB',(1600,1260),(38,40,48));dr=ImageDraw.Draw(out)
for n in range(1,13):
 im=Image.open(R/'attack/E'/f'{n:02}.png').convert('RGBA');im.thumbnail((396,396));x=(n-1)%4*400;y=(n-1)//4*420;out.paste(im,(x,y+18),im);dr.text((x+4,y+3),f'attack E{n:02}',fill='white')
out.save(R/'run/S'/'attack-E-independent-review.jpg',quality=95)
