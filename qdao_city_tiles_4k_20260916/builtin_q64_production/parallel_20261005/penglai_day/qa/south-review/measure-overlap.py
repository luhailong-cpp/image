from pathlib import Path
import numpy as np,json
from PIL import Image
ROOT=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day')
OUT=ROOT/'qa/south-review'
def grad(im):
 rgb=np.asarray(im,dtype=np.float32);g=rgb@np.array([.299,.587,.114],dtype=np.float32)
 gy,gx=np.gradient(g);return np.stack([gx,gy],axis=-1)
ims={f'p{r}{c}':Image.open(ROOT/'native'/f'p{r}{c}.png').convert('RGB')for r in[3,4]for c in range(1,5)}
pairs=[]
for r in[3,4]:
 for c in[1,2,3]:pairs.append((f'v-r{r}-c{c}-{c+1}',f'p{r}{c}',f'p{r}{c+1}',(1024,115,1254,1139),(0,115,230,1139)))
for c in range(1,5):pairs.append((f'h-r3-4-c{c}',f'p3{c}',f'p4{c}',(115,1024,1139,1254),(115,0,1139,230)))
results=[]
for key,a,b,abox,bbox in pairs:
 A=grad(ims[a].crop(abox));B=grad(ims[b].crop(bbox));mag=np.sqrt((A*A).sum(-1));threshold=max(3.,float(np.percentile(mag[10:-10,10:-10],95)))
 mask=mag>threshold;mask[:10]=False;mask[-10:]=False;mask[:,:10]=False;mask[:,-10:]=False
 yy,xx=np.where(mask);av=A[yy,xx]
 scores=[]
 for dy in range(-8,9):
  for dx in range(-8,9):
   diff=np.abs(av-B[yy+dy,xx+dx])
   score=float(np.minimum(diff,20).mean())
   scores.append((score,dx,dy))
 best=min(scores);bounded=min(x for x in scores if x[1]*x[1]+x[2]*x[2]<=16);zero=next(x for x in scores if x[1:]==(0,0))
 results.append({'id':key,'leftOrUpper':a,'rightOrLower':b,'leftOrUpperBoxLTRB':abox,'rightOrLowerBoxLTRB':bbox,'gradientFeaturePixels':len(xx),'gradientThreshold':threshold,'bestUnboundedDxDy':list(best[1:]),'bestUnboundedScore':best[0],'bestWithin4DxDy':list(bounded[1:]),'bestWithin4Score':bounded[0],'zeroScore':zero[0],'warning':'Diagnostic only. B is sampled at coordinate+dx/dy to compare A. Repainted texture and parallel-line ambiguity mean this is not proof of geometric offset; no correction applied.'})
(OUT/'overlap-gradient-diagnostic.json').write_text(json.dumps({'method':'Native unresampled overlap, luminance gradient features95thpercentile; exhaustive integer translations±8px; mean clipped gradient L1; comparison with Euclidean displacement≤4px','results':results},indent=2),encoding='utf8')
print(json.dumps([{'id':r['id'],'best':r['bestUnboundedDxDy'],'bounded4':r['bestWithin4DxDy'],'score':round(r['bestUnboundedScore'],3),'score4':round(r['bestWithin4Score'],3)}for r in results],indent=2))


