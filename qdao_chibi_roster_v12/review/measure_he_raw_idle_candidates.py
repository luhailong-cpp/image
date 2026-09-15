from pathlib import Path
from PIL import Image
import numpy as np,json
p=Path(r'E:\work\image\qdao_chibi_roster_v12\review\he_xiangu_natural_walk\idle-proportion-fixes')
def m(im):
 a=np.array(im.convert('RGB'));fg=~((a[:,:,0]>165)&(a[:,:,1]<120)&(a[:,:,2]>150));top=int(np.where(fg)[0].min());dark=fg&(a[:,:,:3].mean(2)<90);width=[]
 for row in dark[top+15:top+120]:
  x=np.where(row)[0]
  if len(x):width.append(x[-1]-x[0]+1)
 return float(np.percentile(width,90))
o={}
for name,dirs,grid in [('N-S-SE-SW',['N','S','SE','SW'],(2,2)),('E-W',['E','W'],(2,1))]:
 ref=Image.open(p/(name+'-walk-reference.png')).resize((grid[0]*443,grid[1]*443));new=Image.open(p/(name+('-idle-final-raw.png' if name!='E-W' else '-idle-candidate-raw.png'))).resize((grid[0]*443,grid[1]*443))
 for i,d in enumerate(dirs):
  box=(i%grid[0]*443,i//grid[0]*443,(i%grid[0]+1)*443,(i//grid[0]+1)*443);a=m(ref.crop(box));b=m(new.crop(box));o[d]={'walk':a,'new_idle':b,'ratio':b/a}
print(json.dumps(o))
(p/'new-idle-head-metrics.json').write_text(json.dumps(o,indent=2)+'\n')

