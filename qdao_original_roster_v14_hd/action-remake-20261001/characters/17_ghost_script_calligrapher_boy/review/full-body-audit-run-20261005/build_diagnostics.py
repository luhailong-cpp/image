from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
b=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent
allframes=[]
for direction in ['N','NE','E','SE','S','SW','W','NW']:
 frames=[]
 for n in range(1,17):
  p=b/'runtime'/'run'/direction/f'{n:02}.png'
  im=Image.open(p);im.load()
  assert im.size==(1024,1024) and im.mode=='RGBA',(p,im.size,im.mode)
  frames.append(im.copy())
  allframes.append({'direction':direction,'frame':n,'file':p.relative_to(b).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'mode':im.mode})
 for mode in ['full240','arms','legs']:
  crop=None if mode=='full240' else ((0,325,1024,850) if mode=='arms' else (220,600,880,1024))
  w,h=(240,264) if mode=='full240' else ((480,272) if mode=='arms' else (330,236))
  sheet=Image.new('RGB',(w*4,h*4),(223,227,228));d=ImageDraw.Draw(sheet)
  for i,frame in enumerate(frames):
   src=frame if crop is None else frame.crop(crop)
   src=src.copy();src.thumbnail((w,h-24),Image.Resampling.LANCZOS)
   x=i%4*w+(w-src.width)//2;y=i//4*h+24
   sheet.paste(src,(x,y),src);d.text((i%4*w+8,i//4*h+6),f'{direction}{i+1:02}',fill='#111111')
  sheet.save(out/f'{direction}-{mode}.png')
(out/'input-runtime-sha256.json').write_text(json.dumps(allframes,indent=2)+'\n',encoding='utf-8')
print('128 actual runtime PNGs: 1024 RGBA; hashes saved;24 diagnostic sheets;no source mutations')
