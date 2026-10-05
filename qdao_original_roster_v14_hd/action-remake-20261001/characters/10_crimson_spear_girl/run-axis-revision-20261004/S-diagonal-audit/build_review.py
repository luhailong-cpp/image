from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
w=Path(__file__).parent
root=w.parents[1]
rows=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for direction in ['SE','SW']:
 for start in [1,9]:
  sheet=Image.new('RGB',(2200,800),(231,231,223))
  draw=ImageDraw.Draw(sheet)
  for i,n in enumerate(range(start,start+8)):
   p=root/f'runtime/run/{direction}/{n:02d}.png'
   im=Image.open(p).convert('RGBA')
   crop=im.crop((250,620,800,990))
   x=(i%4)*550;y=(i//4)*400
   sheet.paste(crop,(x,y+30),crop)
   draw.text((x+8,y+3),f'{direction} {n:02d} | fixed crop [250,620,800,990]',font=font,fill=(35,35,35))
   draw.line((x,y,x,y+400),fill=(150,150,145))
   rows.append({'frame':f'{direction}/{n:02d}','path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size)})
  sheet.save(w/f'{direction}-{start:02d}-{start+7:02d}-legs.jpg',quality=94)
(w/'source-evidence.json').write_text(json.dumps({'scope':'Read only runtime review; no generation and no runtime mutation','derivedOperation':'Fixed crop and montage solely for visual audit','frames':rows},indent=2),encoding='utf-8')
print('Generated four contact sheets and read-only source hashes.')

