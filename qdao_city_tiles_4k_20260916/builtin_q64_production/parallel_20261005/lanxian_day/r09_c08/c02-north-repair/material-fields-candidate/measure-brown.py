from pathlib import Path
from PIL import Image
import numpy as np,json
a=np.array(Image.open(Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08/c02-north-repair/material-fields-candidate')/'v2/candidate1254.png')).astype(float);u=np.median(a[113:115],axis=0);l=np.median(a[115:117],axis=0)
for end in [80,100,145]:
 print('brownMedian',end,np.median(u[:end]-l[:end],axis=0).tolist())
for ch in range(3):
 x=l[:145,ch];y=u[:145,ch];coef=np.polyfit(x,y,1);pred=x*coef[0]+coef[1];print(ch,coef.tolist(),'resid',np.quantile(y-pred,[0,.1,.5,.9,1]).tolist())

