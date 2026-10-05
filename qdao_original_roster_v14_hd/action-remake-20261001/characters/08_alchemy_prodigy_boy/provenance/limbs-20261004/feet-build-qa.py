from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
original=Image.open(ROOT/'runtime/run/NE/13.png').convert('RGBA')
v1=Image.open(ROOT/'generation/limbs-20261004/feet-northeast/NE-13-v1.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
v2=Image.open(ROOT/'generation/limbs-20261004/feet-northeast/NE-13-v2.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
cells=[]
for label,im in [('NE13 old',original),('NE13 v1 rejected',v1),('NE13 v2 selected',v2)]:
 c=Image.new('RGB',(380,660),(237,233,216));d=ImageDraw.Draw(c);d.text((7,5),label,(15,45,40));small=im.resize((380,380),Image.Resampling.LANCZOS);c.paste(small,(0,24),small)
 boot=im.crop((330,780,520,970)).resize((247,247),Image.Resampling.NEAREST);c.paste(boot,(65,411),boot);cells.append(c)
board=Image.new('RGB',(1140,660),(237,233,216))
for i,c in enumerate(cells):board.paste(c,(i*380,0))
board.save(P/'feet-NE13-comparison.jpg',quality=95)
metrics={}
for label,im in [('v1',v1),('v2',v2)]:
 a=np.array(original);b=np.array(im);m=a[:750,:,3]>100;n=b[:750,:,3]>100
 bootA=a[840:970,330:530,3]>100;bootB=b[840:970,330:530,3]>100
 def bounds(mask):
  y,x=np.where(mask);return [int(x.min()+330),int(y.min()+840),int(x.max()+330),int(y.max()+840)]
 metrics[label]={'upperAlphaIoU':float((m&n).sum()/(m|n).sum()),'originalBootBounds':bounds(bootA),'candidateBootBounds':bounds(bootB)}
(P/'feet-registration.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics))
