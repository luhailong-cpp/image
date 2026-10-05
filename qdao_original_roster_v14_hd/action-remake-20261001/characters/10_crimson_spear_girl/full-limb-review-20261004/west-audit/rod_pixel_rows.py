from pathlib import Path
from PIL import Image
import numpy as np
import sys
r=Path(__file__).resolve().parents[2]
for name in (sys.argv[1:] or ['09-v4','10-v1','10-v2']):
 a=np.array(Image.open(r/'full-limb-review-20261004/run-NW'/name/'native.png'))
 print(name)
 for y,x1,x2 in [(500,350,410),(520,365,430),(540,380,445),(945,615,700),(960,625,740),(1030,700,805)]:
  row=a[y,x1:x2];mask=(row[:,3]>128)&(row[:,:3].max(axis=1)<110)
  xs=np.where(mask)[0]+x1
  groups=[]
  for x in xs:
   if groups and x==groups[-1][-1]+1:groups[-1].append(int(x))
   else:groups.append([int(x)])
  print(y,[(g[0],g[-1]) for g in groups])
