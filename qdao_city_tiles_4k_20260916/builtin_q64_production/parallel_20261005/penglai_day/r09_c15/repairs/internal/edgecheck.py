from pathlib import Path
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent
for n in ['post','rightpost']:
 a=np.asarray(Image.open(O/(n+'-edit-input.png')).convert('RGB'),np.float32);b=np.asarray(Image.open(O/(n+'-ai-v1-generated.png')).convert('RGB'),np.float32)
 for y in [300,400,450,500,600,650,700,750,800,900,1000]:
  def edges(t):
   d=np.mean(abs(np.diff(t[y],axis=0)),axis=1)
   ranges=[(480,550),(680,740)] if n=='rightpost' else [(500,560),(690,745)]
   return [lo+int(np.argmax(d[lo:hi])) for lo,hi in ranges]
  print(n,y,edges(a),edges(b))
