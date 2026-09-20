import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,r'E:/work/image/qdao_original_roster_v13/tools')
import pipeline as p
root=Path(r'E:/work/image/qdao_original_roster_v13')
rows=[]
for batch,grid in [('idle-eightdir-v3',(2,4)),('walk-S-rightboot-pair-v2',(1,2)),('walk-S-leftboot-pair-v3',(1,2))]:
 im=p.imread(root/'generation/04_mountain_guardian_boy'/batch/'raw.png'); rs,cs=grid
 for i in range(rs*cs):
  r,c=divmod(i,cs); box=[round(c*im.width/cs),round(r*im.height/rs),round((c+1)*im.width/cs),round((r+1)*im.height/rs)]
  a=np.array(im.crop(box));a[:,:,3][a[:,:,3]<=8]=0;k=p.KEYER.remove_bg_magenta(Image.fromarray(a).copy(),100,150)
  b=p.cropbox(k); rows.append({'batch':batch,'i':i,'native':im.size,'cell':k.size,'boundary':bool(p.edge_touch(k)),'bbox':b,'height_normalized_at_084':round((b[3]-b[1])*512/max(k.size)*.84,1),'edge_alpha_max':max(int(a[0,:,3].max()),int(a[-1,:,3].max()),int(a[:,0,3].max()),int(a[:,-1,3].max()))})
print(json.dumps(rows,indent=2))
