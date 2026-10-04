import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2]
inv=json.loads((root/'inventory-root.json').read_text(encoding='utf-8'))
rows=[]
for d in ['E','W']:
 grid=Image.new('RGB',(1600,1260),'#263142');draw=ImageDraw.Draw(grid)
 for n in range(1,13):
  f=next(f for f in inv['frames'] if f['action']=='attack' and f['direction']==d and f['frame']==n)
  p=root/f['path'];im=Image.open(p).convert('RGBA');thumb=im.resize((400,400),Image.Resampling.LANCZOS)
  x=(n-1)%4*400;y=(n-1)//4*420;grid.paste(thumb,(x,y),thumb);draw.text((x+8,y+403),f'attack {d}{n:02}',fill='white')
  rows.append({'action':'attack','direction':d,'frame':n,'path':f['path'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'native_evidence':f['native_evidence']})
 grid.save(root/f'work/cast/cast-attack-{d}-readonly-current.jpg',quality=95)
(root/'records/cast-attack-readonly-snapshot-20261003.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('24 attack frame snapshots read; no attack file/inventory changed')
