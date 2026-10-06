from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
d=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r03_c02-upper-v1')
n=np.asarray(Image.open(d/'native.png').convert('RGB'),float);c=np.asarray(Image.open(d/'context.png').convert('RGB'),float);j=np.asarray(Image.open(d/'joined.png').convert('RGB'),float)
windows=[(70,160),(320,400),(470,540),(735,810),(860,930),(1130,1210)]
rows=[397,430,470,496];points=[]
for y in rows:
 for l,r in windows:
  edge=lambda a:int(np.abs(np.diff(a[y].mean(axis=1)))[l:r].argmax()+l)
  xn,xc,xj=[edge(a) for a in [n,c,j]];points.append({'row':y,'window':[l,r],'native':xn,'context':xc,'joined':xj,'residual':xj-xc})
report={'edgeMeasurements':points,'maxResidual':max(abs(p['residual']) for p in points),'knownBelow497Exact':bool(np.array_equal(j[497:],c[497:]))}
(d/'upper-return-measurements.json').write_text(json.dumps(report,indent=2))
Image.open(d/'joined.png').crop((0,280,1254,530)).save(d/'qa/upper-return-1254x250.png')
print(json.dumps(report))

