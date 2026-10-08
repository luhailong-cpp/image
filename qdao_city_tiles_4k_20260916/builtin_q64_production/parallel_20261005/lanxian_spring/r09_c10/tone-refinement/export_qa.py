from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent; T=O.parent; Q=O/'qa'; H=115; N=4326
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def runs(v):
 p=np.flatnonzero(v)
 if not len(p):return []
 chunks=np.split(p,np.flatnonzero(np.diff(p)>1)+1)
 return [[int(x[0]),int(x[-1])+1] for x in chunks]
src=np.array(Image.open(T/'selected/extended4326.png')); dst=np.array(Image.open(O/'extended4326.png'))
delta=dst.astype(np.int16)-src.astype(np.int16); ch=np.any(delta,axis=2)
im=Image.fromarray(dst); scopes={}
for axis in ['vertical','horizontal']:
 for s in [1024,2048,3072]:
  e=s+H
  for kind,offsets,width in [('seam',[0],256),('returns',[-320,320],64)]:
   w=width*len(offsets)*4; sheet=Image.new('RGB',(w,1082),(25,25,25)); boxes=[]
   for oi,offset in enumerate(offsets):
    for j in range(4):
     a=j*1082;b=min(N,a+1082)
     box=(e+offset-width//2,a,e+offset+width//2,b) if axis=='vertical' else (a,e+offset-width//2,b,e+offset+width//2)
     crop=im.crop(box)
     if axis=='horizontal': crop=crop.transpose(Image.Transpose.ROTATE_90)
     sheet.paste(crop,((oi*4+j)*width,0)); boxes.append(list(box))
   f=f'{axis}-{s}-{kind}-1to1.png'; sheet.save(Q/f);scopes[f]={'source':'extended4326.png','boxesExtendedLTRB':boxes,'cropPixelsUnscaled':True,'horizontalStripsQAOnlyRotationDegrees':90 if axis=='horizontal' else 0}
north=T.parent/'r08_c10/selected-v2'; nn=Image.open(north/'core4096.png').convert('RGB')
for state,path in [('before',T/'selected/core4096.png'),('after',O/'core4096.png')]:
 s=Image.open(path).convert('RGB')
 for j in range(4):
  z=Image.new('RGB',(1024,384)); z.paste(nn.crop((j*1024,3904,(j+1)*1024,4096)),(0,0));z.paste(s.crop((j*1024,0,(j+1)*1024,192)),(0,192));z.save(Q/f'north-{j+1}-{state}.png')
edge={}
for name,m,along in [('north',ch[:H,:],1),('south',ch[-H:,:],1),('west',ch[:,:H],0),('east',ch[:,-H:],0)]:
 collapse=m.any(axis=0 if along==1 else 1)
 edge[name]={'changedPixels':int(m.sum()),'alongEdgeChangedHalfOpenRangesExtended':runs(collapse),'alongEdgeChangedHalfOpenRangesCoreCoordinates':[[a-H,b-H] for a,b in runs(collapse)]}
# Cross-neighbor overlap metrics are evidence, not a geometry acceptance claim.
ns=np.array(Image.open(north/'extended4326.png'))
ref=ns[4096:4326,115:4211]
evidence={'northCoreSha256':sha(north/'core4096.png'),'northExtendedSha256':sha(north/'extended4326.png'),'north115HaloAndFirst64CoreRowsByteUnchanged':bool(np.array_equal(src[:179],dst[:179])),'northNeighborOverlapComparison':{'sameWorld230Rows':'neighbor extended4096:4326 versus this extended0:230; x115:4211','beforeMeanAbsRGB':float(np.abs(src[:230,115:4211].astype(np.float32)-ref).mean()),'afterMeanAbsRGB':float(np.abs(dst[:230,115:4211].astype(np.float32)-ref).mean()),'beforeMedianAbsRGB':float(np.median(np.abs(src[:230,115:4211].astype(np.float32)-ref))),'afterMedianAbsRGB':float(np.median(np.abs(dst[:230,115:4211].astype(np.float32)-ref)))} }
metrics=[]
classes=np.array(Image.open(O/'material-labels4326.png'))
for axis in ['vertical','horizontal']:
 a,b,c=(src,dst,classes) if axis=='vertical' else (src.transpose(1,0,2),dst.transpose(1,0,2),classes.T)
 for s in [1024,2048,3072]:
  e=s+115
  for mat in [1,2,3,4]:
   same=np.all(c[:,e-3:e+3]==mat,axis=1)
   ga=np.max(np.abs(np.diff(a[:,e-5:e].astype(np.float32),axis=1)),axis=(1,2))
   gb=np.max(np.abs(np.diff(a[:,e:e+5].astype(np.float32),axis=1)),axis=(1,2))
   valid=same&(ga<7)&(gb<7)
   if valid.sum()<20:continue
   ds=[]
   for z in [a,b]:
    d=z[:,e:e+3].astype(np.float32).mean(1)-z[:,e-3:e].astype(np.float32).mean(1)
    ds.append({'medianRGBStep':np.median(d[valid],axis=0).tolist(),'medianAbsStep':float(np.median(np.abs(d[valid]))),'meanAbsStep':float(np.mean(np.abs(d[valid])))})
   metrics.append({'axis':axis,'coreSeam':s,'material':mat,'samples':int(valid.sum()),'before':ds[0],'after':ds[1]})
record={'scopes':scopes,'outerStrips':edge,'northBoundary':evidence,'seamMetrics':metrics,'imageSHA256':{f:sha(O/f) for f in ['core4096.png','extended4326.png','preview1254.png']}}
(Q/'scope-and-metrics.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'outerStrips':edge,'northBoundary':evidence,'metrics':metrics},indent=2))
