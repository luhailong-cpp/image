from pathlib import Path
from PIL import Image
import numpy as np,json
r=Path(r'E:\work\image\qdao_chibi_roster_v12\candidate-natural-body\29_he_xiangu')
def measure(p):
 a=np.array(Image.open(p).convert('RGBA'));fg=a[:,:,3]>8;top=int(np.where(fg)[0].min());dark=fg & (a[:,:,:3].mean(2)<90);widths=[]
 for row in dark[top+15:top+120]:
  x=np.where(row)[0]
  if len(x):widths.append(int(x[-1]-x[0]+1))
 return float(np.percentile(widths,90)),top
o={}
for d in ['N','NE','E','SE','S','SW','W','NW']:
 idle=measure(r/'idle'/f'{d}.png');walk=[measure(r/'walk'/d/f'{i:02d}.png')[0] for i in range(1,9)]
 o[d]={'idle_dark_head_p90':idle[0],'walk_dark_head_p90':walk,'mean_walk_to_idle':float(np.mean(walk)/idle[0])}
(r/'review/head-size-review.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o))

