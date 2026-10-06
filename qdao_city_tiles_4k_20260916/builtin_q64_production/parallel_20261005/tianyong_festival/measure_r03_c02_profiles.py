from pathlib import Path
import json
import numpy as np
from PIL import Image
d=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r03_c02-upper-v1')
n=np.asarray(Image.open(d/'native.png').convert('RGB'),float);c=np.asarray(Image.open(d/'context.png').convert('RGB'),float);j=np.asarray(Image.open(d/'joined.png').convert('RGB'),float)
windows=[(70,160),(320,400),(470,540),(735,810),(860,930),(1130,1210)]
pts=[]
for y in [397,430,470]:
 for l,r in windows:
  profiles=[]
  for a in [n,c,j]:
   p=a[y:y+3].mean(axis=(0,2));p=np.convolve(p,[.25,.5,.25],mode='same');profiles.append(np.diff(p))
  target=profiles[1][l+7:r-7]
  def best(p):
   scores=[]
   for dx in range(-6,7):
    q=p[l+7+dx:r-7+dx]
    scores.append((float(np.dot(target,q)/(np.linalg.norm(target)*np.linalg.norm(q))),dx))
   return max(scores)
  cn,dn=best(profiles[0]);cj,dj=best(profiles[2]);pts.append({'row':y,'window':[l,r],'nativeDx':dn,'nativeCorrelation':cn,'joinedDx':dj,'joinedCorrelation':cj})
report={'method':'Corresponding full bevel-gradient profiles, not competing single maximum peaks','points':pts,'maxJoinedAbsDx':max(abs(x['joinedDx']) for x in pts),'minJoinedCorrelation':min(x['joinedCorrelation'] for x in pts),'knownBelow497Exact':bool(np.array_equal(j[497:],c[497:])),'earlierSinglePeakMethodAmbiguous':True}
(d/'profile-correspondence.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))

