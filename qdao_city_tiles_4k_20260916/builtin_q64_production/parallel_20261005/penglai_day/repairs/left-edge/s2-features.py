from repair import *
import numpy as np
a=np.array(Image.open(R/'s2-target-native.png')).astype(float)
b=np.array(Image.open(R/'s2-repair-v1.png')).astype(float)
for lo,hi in [(115,170),(280,340),(820,910)]:
    print(lo,hi)
    for name,v in [('old',a[:,626]),('new',b[:,627])]:
        print(name,sorted([(round(float(np.linalg.norm(v[y]-v[y-1])),1),y) for y in range(lo,hi)],reverse=True)[:8])
