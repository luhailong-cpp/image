from pathlib import Path
from PIL import Image
import numpy as np,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08')
for name,p in [('base',T/'c02-north-repair/original/native/r01_c02.png'),('east',T/'native/r01_c03.png')]:
 a=np.array(Image.open(p).convert('RGB')).astype(int);g=(a[:,:,1]>a[:,:,0]+10)&(a[:,:,1]>a[:,:,2]+10)
 result={}
 for x in ([1002,1006,1010,1014,1018,1022,1024,1026,1030,1034,1040] if name=='base' else [0,2,6,10,16,24]):
  rows=np.where(g[115:250,x])[0];result[x]=int(rows.max()+115) if len(rows) else None
 print(name,json.dumps(result))

