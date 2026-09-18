from PIL import Image
from pathlib import Path
import numpy as np,json
root=Path(r'E:/work/image/qdao_original_roster_v13/generation/04_mountain_guardian_boy'); result=[]
for batch in ['walk-S-interval-09-13-v1','walk-S-interval-13-01-v1']:
 im=Image.open(root/batch/'raw.png').convert('RGBA');a=np.asarray(im);W,H=im.size;info=[]
 for i in range(4):
  rr,c=divmod(i,2);v=a[round(rr*H/2):round((rr+1)*H/2),round(c*W/2):round((c+1)*W/2),3];e=np.concatenate([v[0],v[-1],v[:,0],v[:,-1]])
  info.append({'i':i,'edge_gt8':int((e>8).sum()),'edge_max':int(e.max()),'edge_gt32':int((e>32).sum()),'edge_gt128':int((e>128).sum())})
 result.append({'batch':batch,'size':im.size,'cells':info})
 bg=Image.new('RGBA',im.size,(255,0,255,255));bg.alpha_composite(im);bg.convert('RGB').resize((1000,1000)).save(root/batch/'reference-review.jpg',quality=90)
print(json.dumps(result,indent=2))
