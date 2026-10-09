from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image,ImageFilter,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
NATIVE=ROOT/'native'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def savejson(p,v): p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def feature(im):
 g=im.convert('L').filter(ImageFilter.GaussianBlur(0.7))
 a=np.asarray(g,dtype=np.float32)/255
 b=np.asarray(g.filter(ImageFilter.GaussianBlur(3)),dtype=np.float32)/255
 gy,gx=np.gradient(a)
 return np.stack([gx,gy,(a-b)*0.45],axis=2)
def bilinear(a,x,y):
 x0=np.floor(x).astype(int);y0=np.floor(y).astype(int)
 tx=(x-x0)[:,None];ty=(y-y0)[:,None]
 return (a[y0,x0]*(1-tx)+a[y0,x0+1]*tx)*(1-ty)+(a[y0+1,x0]*(1-tx)+a[y0+1,x0+1]*tx)*ty
def estimate(a,b,axis,part=None):
 h,w=a.shape[:2]
 yy,xx=np.mgrid[12:h-12:3,12:w-12:3]; x=xx.ravel();y=yy.ravel()
 if part is not None:
  t=y if axis=='horizontal' else x
  span=h if axis=='horizontal' else w
  ok=(t>=part*span/4)&(t<(part+1)*span/4);x=x[ok];y=y[ok]
 fa=a[y,x];weights=np.sqrt((fa[:,:2]**2).sum(axis=1))
 threshold=max(float(np.quantile(weights,.55)),.002)
 keep=weights>=threshold;x=x[keep];y=y[keep];fa=fa[keep];weights=weights[keep]
 weights=np.clip(weights/np.median(weights),.25,3)
 norm=np.sum(weights*np.sum(fa*fa,axis=1))+1e-10
 def score(dx,dy):
  fb=bilinear(b,x+dx,y+dy)
  nb=np.sum(weights*np.sum(fb*fb,axis=1))+1e-10
  dot=np.sum(weights*np.sum(fa*fb,axis=1))
  return float(1-dot/np.sqrt(norm*nb))
 scores=[(score(dx,dy),dx,dy) for dy in range(-8,9) for dx in range(-8,9)]
 first=min(scores)
 fine=[(score(dx,dy),dx,dy) for dy in np.arange(max(-8,first[2]-.75),min(8,first[2]+.75)+.01,.25) for dx in np.arange(max(-8,first[1]-.75),min(8,first[1]+.75)+.01,.25)]
 best=min(fine);zero=score(0,0)
 tensor=np.einsum('ni,nj,n->ij',fa[:,:2],fa[:,:2],weights)/weights.sum()
 vals,vecs=np.linalg.eigh(tensor);normal=vecs[:,1]
 ratio=float(vals[0]/max(vals[1],1e-10))
 precision=tensor/max(vals[1],1e-10)
 if ratio<.03:precision=np.outer(normal,normal)
 return dict(sampleCount=int(len(x)),bSampleOffsetXY=[float(best[1]),float(best[2])],suggestedRelativePlacementBminusA=[float(-best[1]),float(-best[2])],gradientMismatchAtZero=zero,gradientMismatchAtBest=best[0],relativeImprovement=float((zero-best[0])/max(zero,1e-10)),searchBoundaryHit=bool(abs(best[1])>=7.99 or abs(best[2])>=7.99),gradientTensorEigenvalueRatio=ratio,dominantEdgeNormalXY=normal.tolist(),translationPrecisionMatrix=precision.tolist(),apertureAmbiguous=bool(ratio<.03))

files={p.stem:p for p in NATIVE.glob('p[1-4][1-4].png')}
files['p32']=NATIVE/'p32-v2.png'
images={k:Image.open(p).convert('RGB') for k,p in files.items()}
features={k:feature(im) for k,im in images.items()}
results=[]
for row in range(1,5):
 for col in range(1,5):
  aid=f'p{row}{col}'
  if aid not in images:continue
  for axis,br,bc in [('horizontal',row,col+1),('vertical',row+1,col)]:
   if br>4 or bc>4:continue
   bid=f'p{br}{bc}'
   if bid not in images:continue
   if axis=='horizontal': a=features[aid][:,1024:];b=features[bid][:,:230]
   else:a=features[aid][1024:,:];b=features[bid][:230,:]
   e=estimate(a,b,axis)
   segments=[estimate(a,b,axis,i) for i in range(4)]
   shifts=np.asarray([v['suggestedRelativePlacementBminusA'] for v in segments])
   spread=np.ptp(shifts,axis=0)
   normal=np.array(e['dominantEdgeNormalXY']);normal_spread=float(np.ptp(shifts@normal))
   e.update(dict(a=aid,b=bid,axis=axis,overlapPixels=230,segments=segments,segmentShiftRangeXY=spread.tolist(),segmentNormalShiftRange=normal_spread,nonTranslationRisk=bool(normal_spread>3 if e['apertureAmbiguous'] else np.max(spread)>3),scope='overlap-gradient-translation-diagnostic-only; not structural or visual acceptance'))
   results.append(e)

# Bound every complete patch translation independently to +/-4 native pixels.
# p11 fixed. Additional x=0 constraints for col1 preserve the external tile edge position.
names=sorted(images);index={n:i for i,n in enumerate(names)};pos=np.zeros((len(names),2))
edges=[]
for e in results:
 weight=max(.02,min(1,e['relativeImprovement']))/(1+max(e['segmentShiftRangeXY']))
 edges.append((index[e['a']],index[e['b']],np.array(e['suggestedRelativePlacementBminusA']),weight*np.array(e['translationPrecisionMatrix'])))
for iteration in range(250):
 old=pos.copy()
 for n,i in index.items():
  if n=='p11':continue
  rhs=np.zeros(2);lhs=np.eye(2)*.003
  for a,b,d,mat in edges:
   if i==b:rhs+=mat@(pos[a]+d);lhs+=mat
   if i==a:rhs+=mat@(pos[b]-d);lhs+=mat
  pos[i]=np.clip(np.linalg.solve(lhs,rhs),-4,4)
  if n[-1]=='1':pos[i,0]=0
 if np.max(np.abs(pos-old))<1e-6:break
for e in results:
 delta=pos[index[e['b']]]-pos[index[e['a']]]
 e['boundedGraphRelativeShiftXY']=delta.tolist()
 e['boundedGraphResidualXY']=(delta-np.array(e['suggestedRelativePlacementBminusA'])).tolist()

report=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Pillow grayscale Gaussian0.7 gradients plus0.45*highpass(radius3), native-space step3 edge samples, weighted cosine mismatch; integer +/-8 pair search then quarter-pixel refinement; bounded global least squares +/-4 per patch',sourceFiles=[dict(id=k,file=str(p),sha256=sha(p),pixels=images[k].size) for k,p in sorted(files.items())],missingPatches=[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in images],anchor='p11=(0,0), each col1 x=0; west tile edge still requires separate repair',patchBoundPixels=4,sourceUpscaling=False,sourcePixelsModified=False,proposedNativeImagesExported=False,formalAccepted=False,pairs=results,boundedPatchPlacementSuggestions={n:pos[i].tolist() for n,i in index.items()},limitations=['Translation is only a hypothesis; geometry absent or incompatible must be redrawn.','Strong disagreement among quarter-overlap shifts marks non-rigid geometry/photometric ambiguity; no blend or transform accepted.','No images/correction fields are integrated or exported by this diagnostic.','Suggested absolute offsets bounded; fitting residual retained.'])
savejson(OUT/'overlap-diagnostics.json',report)
print(json.dumps(dict(available=len(images),pairs=len(results),missing=report['missingPatches'],suggestions=report['boundedPatchPlacementSuggestions'],riskPairs=[dict(a=e['a'],b=e['b'],shift=e['suggestedRelativePlacementBminusA'],spread=e['segmentShiftRangeXY'],improvement=round(e['relativeImprovement'],3)) for e in results if e['nonTranslationRisk']]),indent=2))
