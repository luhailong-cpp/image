from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent.parent;A=B/'qa/r13-c06-water-repair-W08-v1';j=json.loads((A/'assembly.json').read_text());im=Image.open(A/j['context']['path']);rgb=np.asarray(im).astype(float)[:1766];ids=np.asarray(Image.open(A/j['sourceIdMap']['path']))[:1766];scores=np.zeros(ids.shape,float)
for axis in [0,1]:
    a=np.swapaxes(rgb,axis,1);s=np.swapaxes(ids,axis,1);d=np.mean(np.abs(a[:,1:]-a[:,:-1]),axis=2);boundary=s[:,1:]!=s[:,:-1];v=np.zeros_like(d);v[:,1:-1]=np.maximum(0,d[:,1:-1]-(d[:,:-2]+d[:,2:])/2);v*=boundary;v[d<3]=0;arr=np.zeros(s.shape);arr[:,1:]=v;scores=np.maximum(scores,np.swapaxes(arr,axis,1))
scores[:115]=0;scores[:,:115]=0;scores[:,4211:]=0
selected=[]
for k in np.argsort(scores.ravel())[::-1][:10000]:
    y,x=np.unravel_index(k,scores.shape)
    if scores[y,x]<=2:break
    if any((x-q['x'])**2+(y-q['y'])**2<220**2 for q in selected):continue
    box=[int(max(115,x-240)),int(max(115,y-180)),int(min(4211,x+240)),int(min(1766,y+180))];p=R/f'boundary-detail-{len(selected)+1}.png'
    if p.exists():assert np.array_equal(np.asarray(Image.open(p)),np.asarray(im.crop(box)))
    else:
        with p.open('xb') as f:im.crop(box).save(f,format='PNG')
    selected.append({'x':int(x),'y':int(y),'score':float(scores[y,x]),'box':box,'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    if len(selected)>=8:break
with (R/'boundary-diagnostics-v2.json').open('x') as f:json.dump({'note':'Numerical score chooses inspect-only crops; is not a pass/fail finding. No artwork modified. v1 was interrupted by JSON serialization error and retained.','regions':selected},f,indent=2)
print(json.dumps(selected))
