from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,hashlib,json
r=Path(__file__).resolve().parents[2];out=r/'full-limb-review-20261004/west-audit'
names=['07-v2','08-v2','11-v2','12-v3'];o=Image.new('RGB',(1600,920),(236,235,224));d=ImageDraw.Draw(o);inputs=[]
for n,name in enumerate(names):
 p=r/'full-limb-review-20261004/run-NW'/name/'native.png';im=Image.open(p);a=np.array(im);inputs.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for k,box in enumerate([(345,480,460,615),(595,920,850,1140)]):
  tile=im.crop(box).resize((345,405) if k==0 else (390,336),Image.Resampling.NEAREST);o.paste(tile,(n*400,25 if k==0 else 450),tile)
 d.text((n*400+5,5),name,fill=(0,0,0));print(name)
 for y,x1,x2 in [(510,355,420),(530,365,430),(550,380,450),(970,610,800),(990,620,810),(1030,635,825)]:
  row=a[y,x1:x2];mask=(row[:,3]>128)&(row[:,:3].max(axis=1)<110);xs=np.where(mask)[0]+x1;groups=[]
  for x in xs:
   if groups and x==groups[-1][-1]+1:groups[-1].append(int(x))
   else:groups.append([int(x)])
  print(y,[(g[0],g[-1]) for g in groups])
fp=out/'NW-root-4-candidates-rod-crops.jpg';o.save(fp,quality=98)
fp.with_suffix('.jpg.generation.json').write_text(json.dumps({'kind':'diagnostic-crops','method':'Fixed native crops and nearest enlargement; no asset edit','inputs':inputs},indent=2),encoding='utf-8')
