import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sheet=Image.new('RGB',(1600,800),(32,46,50));d=ImageDraw.Draw(sheet);sources=[]
for i in range(16):
 p=ROOT/'runtime/run/E'/f'{i:02d}.png'
 im=Image.open(p).convert('RGBA')
 # One common window on every frame, preview only. Never mutates runtime.
 crop=im.crop((180,700,880,1015)).resize((400,180),Image.Resampling.LANCZOS)
 x=(i%4)*400;y=(i//4)*200
 sheet.paste(crop,(x,y),crop)
 ground=y+(941.6875-700)*180/315
 d.line((x,ground,x+399,ground),fill=(171,153,77))
 d.text((x+8,y+184),f'E / {i:02d}',fill=(255,240,214))
 sources.append({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out=ROOT/'review/run_E_feet_contact_20261003.png';sheet.save(out)
(ROOT/'review/run_E_feet_contact_20261003.json').write_text(json.dumps({'sources':sources,'commonCrop':[180,700,880,1015],'purpose':'diagnostic foot direction contact sheet only','runtimeMutated':False,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

