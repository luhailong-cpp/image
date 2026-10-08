from PIL import Image
from pathlib import Path
import numpy as np,json
O=Path(__file__).resolve().parent
j=np.array(Image.open(O/'joined.png')).astype(float)
print('Means x222..229 / x230..237')
for y in range(35,101):
 a=j[y,222:230].mean(0);b=j[y,230:238].mean(0)
 if y%2==0:print(y,np.round(a,1).tolist(),np.round(b,1).tolist(),np.round(b-a,1).tolist())
Image.open(O/'joined.png').crop((190,0,310,160)).save(O/'topjoin-native.png')
