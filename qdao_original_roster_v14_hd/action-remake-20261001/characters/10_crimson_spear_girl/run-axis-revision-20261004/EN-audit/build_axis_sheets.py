from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for d in ('E','NE'):
 for start in (1,9):
  sheet=Image.new('RGB',(1200,1520),'#e5e6df');draw=ImageDraw.Draw(sheet);refs=[]
  for j,n in enumerate(range(start,start+8)):
   p=R/f'runtime/run/{d}/{n:02}.png';im=Image.open(p).convert('RGBA');crop=im.crop((250,665,820,985)).resize((600,337),Image.Resampling.LANCZOS)
   x=(j%2)*600;y=(j//2)*380;sheet.paste(crop,(x,y+38),crop);draw.text((x+16,y+7),f'{d}/{n:02}  current runtime',font=font,fill='#233b32')
   refs.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'generationRecord':str(p.relative_to(R)).replace('\\','/')+'.generation.json'})
  out=O/f'{d}-{start:02}-{start+7:02}-axis.jpg';sheet.save(out,quality=96)
  Path(str(out)+'.generation.json').write_text(json.dumps({'file':out.relative_to(R).as_posix(),'sha256':sha(out),'operation':'QA crop and contact-sheet composition only; fixed crop box [250,665,820,985]; no runtime edits','derivedFrom':refs},indent=2),encoding='utf-8')

