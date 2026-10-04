import sys,json,hashlib,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location('exp',R/'tools/export_frame.py');e=importlib.util.module_from_spec(sp);sp.loader.exec_module(e)
for action,dirs in [('cast',['E','W']),('run',['W'])]:
 for d in dirs:
  for n in range(1,17):
   if action=='cast': ver={('E',4):3,('E',9):3,('E',13):2}.get((d,n),1)
   else: ver=2 if n==3 or 7<=n<=15 else 1
   src=R/action/'staging'/f'{action}-{d}-{n:02}-v{ver}.png'
   if not src.exists(): print('missing',src);continue
   rec=Path(str(src)+'.generation.json')
   if not rec.exists():
    old=R/'provenance'/f'{action}-{d}-{n:02}-v{ver}.generation.json'
    if old.exists():rec.write_text(old.read_text(encoding='utf-8'),encoding='utf-8')
   e.run(src,R/action/d/f'{n:02}.png')
  p=R/action/d/'preview-review';p.mkdir(exist_ok=True)
  sheet=Image.new('RGB',(1280,1400),'#e5e8e8');draw=ImageDraw.Draw(sheet)
  for n in range(1,17):
   src=R/action/d/f'{n:02}.png';im=Image.open(src).convert('RGBA').resize((320,320))
   x=((n-1)%4)*320;y=((n-1)//4)*350
   sheet.paste(im,(x,y),im);draw.text((x+6,y+322),f'{action} {d} {n:02}',fill='#203040')
   draw.line((x+176,y,x+176,y+320),fill='#c77777',width=1);draw.line((x,y+294,x+320,y+294),fill='#668877')
  sheet.save(p/'contact.jpg',quality=94)

