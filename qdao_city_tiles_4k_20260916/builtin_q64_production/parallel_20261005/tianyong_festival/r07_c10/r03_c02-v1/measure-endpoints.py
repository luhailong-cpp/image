from PIL import Image
from pathlib import Path
import numpy as np
D=Path(__file__).parent
for filename in ['context.png','native.png','repair-v1/native.png']:
 a=np.array(Image.open(D/filename).convert('RGB')).mean(2)
 print(filename)
 for y in [1130,1160,1190,1220,1240]:
  row=a[y-2:y+3].mean(0);g=np.gradient(row);inds=np.argsort(abs(g[250:700]))[-6:]+250
  print(y,sorted([(int(x),round(float(g[x]),1)) for x in inds]))
