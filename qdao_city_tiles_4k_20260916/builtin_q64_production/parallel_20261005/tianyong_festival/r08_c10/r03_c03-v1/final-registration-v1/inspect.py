from PIL import Image
from pathlib import Path
import numpy as np,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival')
O=T/'r08_c10/r03_c03-v1/final-registration-v1'
c=json.loads((T/'source-checkpoint.json').read_text(encoding="utf-8-sig"));a=Image.open(c['fragment']['file']).crop((1933,1933,3187,3187));a.save(O/'context.png')
ar=np.array(a);print([(y,np.flatnonzero(ar[y,:,3]==0)[[0,-1]].tolist() if np.any(ar[y,:,3]==0) else None) for y in [0,100,229,230,396,397,600,900,1023,1024,1253]])

