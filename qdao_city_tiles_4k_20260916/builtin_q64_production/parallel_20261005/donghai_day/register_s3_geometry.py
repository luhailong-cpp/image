from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;D=R/'r07_c15/repairs/unified';F=D/'south-masked/s3';sys.path.insert(0,str(D/'python-deps'));import cv2
p=np.asarray(Image.open(F/'edited-native.png').convert('RGB'));t=np.asarray(Image.open(F/'composition-reference.png').convert('RGB'))
def edges(row):
 v=row.astype(float);warm=v[:,0]>v[:,2]+20
 end=np.where(np.diff(warm.astype(int))==-1)[0][-1]+1
 left=np.argmin(v.mean(axis=1)[200:700])+200
 return [left,end]
ys=np.arange(681,821);pe=np.array([edges(p[y]) for y in ys]);te=np.array([edges(t[y]) for y in ys])
ps=[np.polyfit(ys,pe[:,k],2) for k in range(2)];ts=[np.polyfit(ys,te[:,k],2) for k in range(2)]
Y,X=np.mgrid[:796,:1254].astype(np.float32);mapx=X.copy();rows=[];start=380
for y in range(start,796):
 s=np.array([np.polyval(c,y) for c in ps]);target=np.array([np.polyval(c,y) for c in ts])
 if y<681:
  w=(y-start)/(681-start);w=w*w*(3-2*w);target=s+np.clip(target-s,-80,80)*w
 s=np.clip(s,1,1252);target=np.clip(target,1,1252)
 assert np.all(np.diff(s)>5) and np.all(np.diff(target)>5)
 mapx[y]=np.interp(np.arange(1254),[0,*target,1253],[0,*s,1253]);rows.append({'y':y,'sourceEdges':s.tolist(),'targetEdges':target.tolist()})
out=cv2.remap(p,mapx,Y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
Image.fromarray(out).save(F/'registered-upper.png')
np.savez_compressed(F/'semantic-registration.npz',map_x=mapx.astype(np.float16),map_y=Y.astype(np.float16))
meta={'operation':'Bounded monotone horizontal registration of existing broad-beam inner groove and outer silhouette. Known halo measured at each row, fit degree2; fade to zero at y380. No vertical warp.','sourceSha256':hashlib.sha256((F/'edited-native.png').read_bytes()).hexdigest(),'targetSha256':hashlib.sha256((F/'composition-reference.png').read_bytes()).hexdigest(),'maxDisplacement':float(np.abs(mapx-X).max()),'sourceEdgePolynomials':np.asarray(ps).tolist(),'targetEdgePolynomials':np.asarray(ts).tolist(),'fittedRows':[681,821],'appliedRows':[start,796],'sampling':'bilinear local registration','rowKnots':rows,'authoritativeHaloTransition':{'rows':[681,796],'weight':'smoothstep0to1; exact target last row'}}
(F/'semantic-registration.json').write_text(json.dumps(meta,indent=2))
out=out.astype(float);w=np.linspace(0,1,115);w=w*w*(3-2*w);out[681:796]=out[681:796]*(1-w[:,None,None])+t[681:796]*w[:,None,None];out=np.rint(out).astype('uint8')
Image.fromarray(out).save(F/'halo-matched-upper.png')
south=np.asarray(Image.open(R/'r08_c15/output/r08_c15.png').convert('RGB'));sheet=Image.new('RGB',(1254,500));sheet.paste(Image.fromarray(out[-300:]),(0,0));sheet.paste(Image.fromarray(south[:200,2048:3302]),(0,300));sheet.save(D/'qa-probes/s3-semantic-halo-common-edge.png')
print(meta['maxDisplacement'])

