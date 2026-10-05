from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
b=Path(__file__).resolve().parents[2]
out=b/'review'/'axis-N-NW'
out.mkdir(exist_ok=True)
files=[]
for direction in ('N','NW'):
 for mode in ('full240','legs'):
  w,h=(240,265) if mode=='full240' else (340,310)
  sheet=Image.new('RGB',(w*4,h*4),(220,223,224));d=ImageDraw.Draw(sheet)
  for n in range(1,17):
   p=b/'runtime'/'run'/direction/f'{n:02}.png'
   im=Image.open(p).convert('RGBA')
   if mode=='legs':im=im.crop((250,580,835,1024))
   im.thumbnail((w,h-26),Image.Resampling.LANCZOS)
   x=(n-1)%4*w+(w-im.width)//2;y=(n-1)//4*h+26
   sheet.paste(im,(x,y),im)
   d.text(((n-1)%4*w+7,(n-1)//4*h+7),f'{direction} {n:02}',fill='#111111')
   if mode=='full240':
    files.append({'direction':direction,'frame':n,'file':str(p.relative_to(b)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  sheet.save(out/f'{direction}-{mode}.png')
(out/'input-runtime-sha256.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf-8')
print('32 runtime frames inspected structurally; diagnostic sheets produced only, no original changed')

