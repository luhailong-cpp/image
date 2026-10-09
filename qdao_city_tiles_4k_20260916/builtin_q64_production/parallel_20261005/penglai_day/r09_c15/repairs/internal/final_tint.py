import sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
import ai_helper as h
import integrate_west_v2 as w
O=h.O;src=O/'joint-candidate-west-final.png'
a=np.asarray(Image.open(src).convert('RGB'),np.float32);f=np.zeros_like(a)
for y in range(1070,1220):
 samples=[]
 for dy in range(-4,5):
  samples.append(a[y+dy-1,624]-a[y+dy+1,630])
 jump=np.clip(np.median(samples,axis=0)/2,-8,8)
 yf=min(1,(y-1070)/15,(1219-y)/15)
 for x in range(602,652):
  side=-1 if x<627 else 1;fade=max(0,1-abs(x-626.5)/25)
  if a[y,x,0]>a[y,x,1]*1.08 and a[y,x,1]>a[y,x,2]*1.3:f[y,x]=side*jump*fade*yf
out=np.clip(np.rint(a+f),0,255).astype('uint8');p=O/'joint-candidate-west-final2.png';Image.fromarray(out).save(p);fp=O/'wood-highlight-field.npz';np.savez_compressed(fp,field=f[1070:1220,602:652]);h.derived(p,[src],{'method':'bounded additiveRGB field on residual vertical wood highlight tint only; oblique samples follow rail slope; no image blur or resampling','fieldFile':str(fp),'fieldSHA':h.sha(fp),'maxAbsRGB':float(abs(f).max()),'cap':8,'bbox':[602,1070,652,1220],'imageResampling':False,'imageBlur':False})
w.export(p,O/'joint-mask-west-final.png','final2')
qa=O/'qa-highlight-final2.png';Image.fromarray(out).crop((460,1024,800,1310)).save(qa);h.derived(qa,[p],{'method':'native detail QA'})
