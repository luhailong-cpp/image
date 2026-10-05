from repair import *
import numpy as np
a=np.array(Image.open(R/'target-native.png')).astype(float)
b=np.array(Image.open(R/'repair-v2.png')).astype(float)
for lo,hi in [(115,230),(380,540),(540,650),(700,800),(870,910),(920,1060),(1090,1139)]:
    print(lo,hi)
    for name,v in [('old',a[:,626]),('new',b[:,627])]:
        print(name,sorted([(round(float(np.linalg.norm(v[y]-v[y-1])),1),y) for y in range(lo,hi)],reverse=True)[:8])
