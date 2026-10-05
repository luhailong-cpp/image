from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
raw=np.asarray(Image.open(OUT/'native.png').convert('RGB')).astype(float)
ctx=np.asarray(Image.open(OUT/'context.png').convert('RGB')).astype(float)
lum=lambda a: a@np.array([0.2126,0.7152,0.0722])
windows=[(70,180),(330,450),(450,570),(700,815),(840,960),(1100,1240)]
rows=[1028,1080,1140,1220]
measurements=[]
for y in rows:
    a=np.diff(lum(ctx[y-3:y+4]).mean(axis=0))
    b=np.diff(lum(raw[y-3:y+4]).mean(axis=0))
    for lo,hi in windows:
        edge=lo+int(np.argmax(np.abs(a[lo:hi])))
        nlo=max(lo,edge-40);nhi=min(hi,edge+41)
        sign=np.sign(a[edge])
        raw_edge=nlo+int(np.argmax(sign*b[nlo:nhi]))
        measurements.append({'y':y,'xSearchRange':[lo,hi],'contextStrongestEdgeX':edge,'rawSamePolarityStrongestEdgeX':raw_edge,'rawMinusContextX':raw_edge-edge,'method':'7-row mean luminance derivative; strongest matching polarity within40px; diagnostic only'})
data={'nativeSha256':hashlib.sha256((OUT/'native.png').read_bytes()).hexdigest(),'contextSha256':hashlib.sha256((OUT/'context.png').read_bytes()).hexdigest(),'measurements':measurements,'caveat':'No automatic registration or acceptance. Different local contrast can select different bevel subedges.'}
(OUT/'overlap-edge-diagnostic.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps(measurements))
