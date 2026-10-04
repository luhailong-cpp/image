import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2];other=root.parent/'09_bamboo_archer_girl'
rows=[]
for d in ['E','W']:
 sheet=Image.new('RGB',(1600,1680),'#263142');draw=ImageDraw.Draw(sheet)
 for n in range(1,17):
  p=other/'runtime/cast'/d/f'{n:02}.png';im=Image.open(p).convert('RGBA');im.thumbnail((400,400))
  x=((n-1)%4)*400;y=((n-1)//4)*420;sheet.paste(im,(x,y),im);draw.text((x+8,y+403),f'09 cast {d}{n:02} - 45ms',fill='white')
  rows.append({'character':'09_bamboo_archer_girl','slot':f'cast/{d}/{n:02}','path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 sheet.save(root/'work/cast'/f'bamboo-cast-{d}-readonly.jpg',quality=95)
(root/'reviews/bamboo-cast-reference-snapshot-20261003.json').write_text(json.dumps({'readOnly':True,'files':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('two read-only contact sheets saved under 02 work/cast')
