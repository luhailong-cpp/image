from pathlib import Path
import sys,json,numpy as np
from PIL import Image
sys.path.insert(0,r'E:\work\image\qdao_chibi_roster_v12')
from edge_despill import shifted
p=Path(r'E:\work\image\qdao_chibi_roster_v12\candidate-stable-body\24_lu_dongbin\idle\NW.png');a=np.array(Image.open(p));r,g,b=(a[:,:,i].astype(int) for i in range(3));fg=a[:,:,3]>8;mag=(r-g>=12)&(b-g>=12)&(b*5>=r*4)&fg;dist=np.full(fg.shape,999)
for y in range(-8,9):
 for x in range(-8,9):
  d=x*x+y*y
  if d<=64: dist[shifted(~fg,y,x,True)]=np.minimum(dist[shifted(~fg,y,x,True)],d)
ys,xs=np.where(mag)
print(json.dumps({'remaining':len(xs),'depth':{str(round(float(np.sqrt(d)),2)):int(np.sum(mag&(dist==d))) for d in sorted(set(dist[mag]))},'samples':[[int(x),int(y),a[y,x].tolist(),round(float(np.sqrt(dist[y,x])),2)] for x,y in zip(xs[::max(1,len(xs)//12)],ys[::max(1,len(xs)//12)])]}))
