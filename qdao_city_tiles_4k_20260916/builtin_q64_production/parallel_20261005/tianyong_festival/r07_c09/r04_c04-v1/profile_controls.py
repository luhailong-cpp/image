from pathlib import Path
from PIL import Image
import json,numpy as np
D=Path(__file__).parent
C=np.array(Image.open(D/'context.png').convert('RGB')).mean(axis=2)
N=np.array(Image.open(D/'repair-v2/native.png').convert('RGB')).mean(axis=2)
def peaks(a,limit):
 a=np.convolve(a,np.ones(5)/5,'same');g=np.gradient(a)
 pos=[i for i in range(limit[0],limit[1]) if abs(g[i])>1.8 and abs(g[i])==max(abs(g[max(i-6,0):i+7]))]
 return [(int(i),round(float(g[i]),2)) for i in pos]
rows=[]
for x in (1050,1100,1150,1200):rows.append({'edge':'right','x':x,'C':peaks(C[:,x-3:x+4].mean(axis=1),(20,1230)),'N':peaks(N[:,x-3:x+4].mean(axis=1),(20,1230))})
for y in (1145,1165,1190,1220):rows.append({'edge':'bottom','y':y,'C':peaks(C[y-3:y+4].mean(axis=0),(650,1230)),'N':peaks(N[y-3:y+4].mean(axis=0),(650,1230))})
(D/'profile-peaks.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
