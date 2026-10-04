from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1]
for d in ['SW','NW']:
 out=Image.new('RGBA',(1280,1360),(232,237,229,255));draw=ImageDraw.Draw(out)
 legs=Image.new('RGBA',(1600,1280),(232,237,229,255));ld=ImageDraw.Draw(legs)
 fs=[]
 for i in range(1,17):
  p=r/f'runtime/run/{d}/{i:02d}.png';im=Image.open(p);a=im.getchannel('A')
  x=((i-1)%4)*320;y=((i-1)//4)*340
  out.alpha_composite(im.resize((320,320)),(x,y+20));draw.text((x+10,y+4),f'{d} {i:02d}',fill=(0,0,0))
  x=((i-1)%4)*400;y=((i-1)//4)*320
  legs.alpha_composite(im.crop((240,600,840,1024)).resize((400,283)),(x,y+25));ld.text((x+10,y+5),f'{d} {i:02d}',fill=(0,0,0))
  fs.append({'frame':i,'file':p.relative_to(r).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'mode':im.mode,'alphaExtrema':a.getextrema()})
 out.save(r/f'audit/{d}-finish-contact.png');legs.save(r/f'audit/{d}-finish-legs.png')
 (r/f'audit/{d}-finish-technical.json').write_text(json.dumps({'direction':d,'uniqueSha256':len(set(x['sha256'] for x in fs)),'frames':fs},ensure_ascii=False,indent=2),encoding='utf-8')
 ims=[Image.open(r/f'runtime/run/{d}/{i:02d}.png') for i in range(1,17)]
 ims[0].save(r/f'audit/{d}-finish-75ms.apng',save_all=True,append_images=ims[1:],duration=75,loop=0,disposal=1,blend=0)
print('SW/NW evidence images, timing APNG, SHA checks refreshed.')

