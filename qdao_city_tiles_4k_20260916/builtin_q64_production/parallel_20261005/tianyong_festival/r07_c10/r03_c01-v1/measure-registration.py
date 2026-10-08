from pathlib import Path
import numpy as np,json
from PIL import Image
D=Path(__file__).parent;C=np.array(Image.open(D/'context.png').convert('RGB')).mean(2);R=np.array(Image.open(D/'repair-v1/native.png').convert('RGB')).mean(2)
C=np.gradient(C,axis=0);R=np.gradient(R,axis=0);out=[]
for x in range(20,1240,30):
 c=C[1048:1228,x-4:x+5]
 if np.max(abs(c))<2:continue
 scores=[float(np.mean(abs(c-R[1048+s:1228+s,x-4:x+5]))) for s in range(-24,25)]
 out.append({'x':x,'dy':int(np.argmin(scores))-24,'score':min(scores),'score0':scores[24],'peak':float(np.max(abs(c)))})
(D/'registration-measurements.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
