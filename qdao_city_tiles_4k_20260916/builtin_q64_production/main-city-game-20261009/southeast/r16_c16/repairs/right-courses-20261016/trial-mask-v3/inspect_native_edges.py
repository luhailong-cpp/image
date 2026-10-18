from PIL import Image
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parent
a=np.array(Image.open(R/'upper/attempt2/actual-native-a51fad637608632f.png').convert('RGB')).mean(axis=2)
items=[]
for x in [490,520,600,700,780,800,820,900,1000,1100,1200,1240]:
 c=round(1489-.677*x);ya=max(0,c-30);yb=min(1254,c+60);v=a[ya:yb,x];g=np.diff(v)
 items.append(dict(x=x,seed=c,minrow=ya+int(np.argmin(v)),minval=float(v.min()),maxPositiveGradientRow=ya+int(np.argmax(g)),values=[[y,round(a[y,x])] for y in range(ya,yb,5)]))
print(json.dumps(items))

