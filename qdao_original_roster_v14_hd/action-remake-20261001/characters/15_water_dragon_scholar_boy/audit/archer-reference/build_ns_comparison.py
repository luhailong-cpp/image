from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[2]
a=b.parent/'09_bamboo_archer_girl'
out=Path(__file__).resolve().parent
sources=[]
for di in ['N','S']:
 for group in range(4):
  sh=Image.new('RGB',(1152,1200),(32,40,51));dr=ImageDraw.Draw(sh)
  for r in range(4):
   n=group*4+r+1;an=((n+7)%16)+1 if di=='N' else n
   for ci,(char,root,number) in enumerate([('15',b,n),('09',a,an)]):
    p=root/'runtime/run'/di/f'{number:02d}.png';im=Image.open(p).convert('RGBA')
    assert im.size==(1024,1024),str(im.size)
    x=ci*256;y=r*300
    panel=Image.new('RGBA',(256,256),(32,40,51,255));panel.alpha_composite(im.resize((256,256)))
    sh.paste(panel.convert('RGB'),(x,y+24))
    dr.text((x+6,y+5),f'{char} {di}{number:02d}',fill='white')
    crop=im.crop((200,660,824,1015));crop.thumbnail((320,250))
    panel=Image.new('RGBA',(320,250),(32,40,51,255));panel.alpha_composite(crop,((320-crop.width)//2,8))
    x=512+ci*320;sh.paste(panel.convert('RGB'),(x,y+24))
    dr.text((x+6,y+5),f'{char} {di}{number:02d} lower-body',fill='white')
    sources.append({'character':char,'direction':di,'frame':number,'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  sh.save(out/f'ns-{di}-compare-{group+1}.png')
(out/'ns-visual-inputs.json').write_text(json.dumps({'reviewedAt':datetime.now(timezone.utc).isoformat(),'mapping':'N按支撑腿左右相位相差8槽对照；S先同槽对照。仅用于诊断不改帧序。','diagnostics':'whole-canvas thumbnail + fixed crop; no registration, no per-frame normalization, no pose edit','sources':sources},ensure_ascii=False,indent=2),encoding='utf-8')
print('8 comparison sheets written; 64 runtime inputs')

