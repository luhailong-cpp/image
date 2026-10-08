from PIL import Image
import numpy as np,json
from pathlib import Path
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival');P=T/'r08_c10/r02_c02-v1'
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'))
c=np.array(Image.open(cp['fragment']['file']).convert('RGB').crop((909,909,2163,2163))).astype(float)
n=np.array(Image.open(P/'lower-repair-v3/native.png').convert('RGB')).astype(float)
for ys in [(0,100),(150,230),(1120,1180),(1180,1254)]:
 a=n[ys[0]:ys[1]]-c[ys[0]:ys[1]]
 print(ys,'mae',np.abs(a).mean(),'median',np.median(a,axis=(0,1)),'p95',np.percentile(np.abs(a),95))
for y in [180,210,1170,1200]:
 for l,r in [(20,240),(450,740),(770,1010),(1040,1240)]:
  vals=[]
  for dx in range(-8,9):
   aa=np.diff(c[y-8:y+9,l:r].mean(2),axis=1)
   bb=np.diff(n[y-8:y+9,l+dx:r+dx].mean(2),axis=1)
   vals.append((float(np.mean((aa-bb)**2)),dx))
  print(y,l,r,min(vals))

