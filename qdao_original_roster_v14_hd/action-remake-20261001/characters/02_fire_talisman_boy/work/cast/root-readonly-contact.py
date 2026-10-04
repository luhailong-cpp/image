import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[2]
inv=json.loads((root/'inventory-root.json').read_text(encoding='utf-8'))
rows=[]
for action,d,count in [('attack','E',12),('attack','W',12),('run','E',16),('run','SE',16)]:
 grid=Image.new('RGB',(1600,420*((count+3)//4)),'#263142');draw=ImageDraw.Draw(grid)
 for n in range(1,count+1):
  if action=='attack' and d=='W' and n in [3,12]:continue
  f=next(f for f in inv['frames'] if f['action']==action and f['direction']==d and f['frame']==n)
  p=root/f['path'];im=Image.open(p).convert('RGBA');thumb=im.resize((400,400),Image.Resampling.LANCZOS)
  x=(n-1)%4*400;y=(n-1)//4*420;grid.paste(thumb,(x,y),thumb);draw.text((x+8,y+403),f'{action} {d}{n:02}',fill='white')
  sha=hashlib.sha256(p.read_bytes()).hexdigest()
  rows.append({'action':action,'direction':d,'frame':n,'path':f['path'],'sha256':sha,'inventory_sha256':f['sha256'],'native_evidence':f['native_evidence'],'inventoryMatches':sha==f['sha256']})
 grid.save(root/f'work/cast/cast-root-{action}-{d}-readonly-current.jpg',quality=95)
(root/'reviews').mkdir(exist_ok=True)
(root/'reviews/root-independent-snapshot-20261003.json').write_text(json.dumps({'capturedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'frames':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} root frame snapshots; no root frame/inventory changed')
