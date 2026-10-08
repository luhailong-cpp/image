from pathlib import Path
import json,sys,numpy as np
from PIL import Image
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
P=Path(__file__).resolve().parent
r=np.array(Image.open(P/'lower-repair-v2/native.png').convert('RGB')).mean(2).astype('float32')
c=np.array(Image.open(P/'context-latest.png').convert('RGBA'))[:,:,:3].mean(2).astype('float32')
g=lambda im:cv2.GaussianBlur(im,(0,0),1)
rx=np.gradient(g(r),axis=1);cx=np.gradient(g(c),axis=1)
ry=np.gradient(g(r),axis=0);cy=np.gradient(g(c),axis=0)
items=[]
def match(a,b,axis,pos,lo,hi):
 if axis=='x': A=a[pos-2:pos+3,lo:hi].mean(0);B=b[pos-2:pos+3,:].mean(0)
 else:A=a[lo:hi,pos-2:pos+3].mean(1);B=b[:,pos-2:pos+3].mean(1)
 mask=np.abs(A)>1;assert mask.sum()>3
 scores=[]
 for shift in range(-12,13):
  sample=B[lo+shift:hi+shift];scores.append((float(((A[mask]-sample[mask])**2).mean()),shift))
 score,shift=min(scores);items.append({'axis':axis,'position':pos,'searchWindow':[lo,hi],'sourceSamplingCorrection':shift,'mse':score,'edgePixels':int(mask.sum())})
for y in [100,150,200,228]:
 match(cx,rx,'x',y,40,300);match(cx,rx,'x',y,600,1000)
for y in [1025,1050,1100,1160]:
 match(cx,rx,'x',y,200,390);match(cx,rx,'x',y,380,650);match(cx,rx,'x',y,920,1040)
for x in [1025,1070,1130]:match(cy,ry,'y',x,590,820)
(P/'edge-measurements.json').write_text(json.dumps(items,indent=2),encoding='utf8');print(json.dumps(items))
