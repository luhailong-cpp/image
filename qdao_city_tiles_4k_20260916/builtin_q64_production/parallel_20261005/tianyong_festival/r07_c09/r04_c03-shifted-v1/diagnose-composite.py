from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
D=Path(__file__).parent;F=D/'final-v1';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
N=np.array(Image.open(D/'repair-v2/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'));G=np.array(Image.open(D/'layout-reference-only.png').convert('RGB'))
x,y=np.meshgrid(np.arange(1254),np.arange(1254));smooth=lambda v:(lambda t:t*t*(3-2*t))(np.clip(v,0,1))
w=np.where(C[:,:,3]==255,np.maximum(smooth((x-770)/160),smooth((y-1139)/61)),0)
J=np.rint(N*(1-w[:,:,None])+C[:,:,:3]*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('right',[690,0,1000,1254]),('bottom',[0,1010,1254,1254]),('corner',[680,1010,1000,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
def peaks(v,lo=0,hi=1254):
 v=np.convolve(v,np.ones(7)/7,mode='same');a=np.gradient(v);k=[i for i in range(max(lo,5),min(hi,1249)) if abs(a[i])>.6 and abs(a[i])==max(abs(a[i-5:i+6]))]
 return [[i,round(float(a[i]),2)] for i in k]
rec={'right':{},'bottom':{}}
for xx in [760,800,850,900,930]:
 rec['right'][xx]={label:peaks(A[:,xx-5:xx+6,:3].mean(axis=(1,2)),15,1130) for label,A in [('context',C),('native',N),('guide',G)]}
for yy in [1145,1165,1190,1220]:
 rec['bottom'][yy]={label:peaks(A[yy-3:yy+4,:,:3].mean(axis=(0,2)),5,1248) for label,A in [('context',C),('native',N)]}
(F/'profile-peaks.json').write_text(json.dumps(rec,indent=2))
print(json.dumps(rec))
