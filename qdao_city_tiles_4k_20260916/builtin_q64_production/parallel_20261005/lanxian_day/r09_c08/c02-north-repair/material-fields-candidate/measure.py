from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08/c02-north-repair');a=np.array(Image.open(D/'candidate-v4/candidate1254.png')).astype(float)
up=np.median(a[113:115],axis=0);lo=np.median(a[115:117],axis=0);d=up-lo
for label,ra in [('orange',(0,430)),('leaves',(1000,1254))]:
 x0,x1=ra
 print(label,'rgbdiff sample',[(x,up[x].tolist(),lo[x].tolist(),d[x].tolist()) for x in range(x0,x1,20)])
 print('quantiles',np.quantile(d[x0:x1],[0,.1,.5,.9,1],axis=0).tolist())

