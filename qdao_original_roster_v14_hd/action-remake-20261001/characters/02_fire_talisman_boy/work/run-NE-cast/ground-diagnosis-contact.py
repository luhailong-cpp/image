from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(__file__).resolve().parents[2];other=root.parent/'09_bamboo_archer_girl'
rows=[]
for name,source in [('02',root/'frames/run/NE'),('09',other/'runtime/run/NE')]:
 sheet=Image.new('RGB',(1600,1720),'#283344');draw=ImageDraw.Draw(sheet)
 for n in range(1,17):
  p=source/f'{n:02}.png';im=Image.open(p).convert('RGBA');x=((n-1)%4)*400;y=((n-1)//4)*430
  thumb=im.resize((400,400),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y),thumb);draw.line((x,y+371,x+399,y+371),fill='#657885');draw.text((x+8,y+405),f'{name} NE{n:02}',fill='white')
  rows.append({'character':name,'frame':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 sheet.save(root/'work/run-NE-cast'/f'{name}-NE-ground-current.jpg',quality=96)
(root/'records/run-NE-cast-support-diagnosis-snapshot-20261004.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('02 and09 readonly16-frame contacts written')
