from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).parent;P=D.parent
ims={n:np.array(Image.open(p).convert('RGB')).mean(2) for n,p in [('current',P/'context-v015.png'),('repair',P/'left-lower-repair-v1/native.png'),('joined',D/'joined.png')]}
out={}
for x in [130,150,180,200,230,250,300,350,400,425,450,500,550,600]:
 out[x]={}
 for name,a in ims.items():
  f=a[:,max(0,x-2):x+3].mean(1);g=np.diff(f)
  vals=np.argsort(abs(g[1050:1150]))[-5:]+1050
  out[x][name]=[(int(v),round(float(g[v]),2)) for v in sorted(vals)]
print(json.dumps(out,indent=2))
