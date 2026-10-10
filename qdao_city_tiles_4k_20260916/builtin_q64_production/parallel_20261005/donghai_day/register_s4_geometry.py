from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;D=R/'r07_c15/repairs/unified';F=D/'south-masked/s4';sys.path.insert(0,str(D/'python-deps'));import cv2
p=np.asarray(Image.open(F/'edited-native.png').convert('RGB'));t=np.asarray(Image.open(F/'composition-reference.png').convert('RGB'))
def edges(row):
 v=row.astype(np.int16);warm=v[:,0]>v[:,2]+20
 d=np.diff(np.r_[False,warm,False].astype(np.int8));runs=[(s,e) for s,e in zip(np.where(d==1)[0],np.where(d==-1)[0]) if e-s>30]
 assert len(runs)==2 and runs[0][0]==0
 return [runs[0][1],runs[1][0],runs[1][1]]
ys=np.arange(681,821);pe=np.array([edges(p[y]) for y in ys]);te=np.array([edges(t[y]) for y in ys])
ps=[np.polyfit(ys,pe[:,k],2) for k in range(3)];ts=[np.polyfit(ys,te[:,k],2) for k in range(3)]
Y,X=np.mgrid[:796,:1254].astype(np.float32);mapx=X.copy();rows=[]
start=next(y for y in range(380,681) if np.all(np.diff([np.polyval(c,y) for c in ps])>20) and np.all(np.diff([np.polyval(c,y) for c in ts])>20))
for y in range(start,796):
 s=np.array([np.polyval(c,y) for c in ps]);target=np.array([np.polyval(c,y) for c in ts])
 if y<681:
  weight=(y-start)/(681-start);weight=weight*weight*(3-2*weight)
  # Extrapolate only bounded silhouette deltas, not grain-specific optical flow.
  delta=np.clip(target-np.array([np.polyval(c,y) for c in ps]),-80,80)*weight
  target=s+delta
 s=np.clip(s,1,1252);target=np.clip(target,1,1252)
 if not np.all(np.diff(s)>5) or not np.all(np.diff(target)>5):raise ValueError((y,s,target))
 mapx[y]=np.interp(np.arange(1254),[0,*target,1253],[0,*s,1253])
 rows.append({'y':y,'sourceEdges':s.tolist(),'targetEdges':target.tolist()})
out=cv2.remap(p,mapx,Y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
Image.fromarray(out).save(F/'registered-upper.png')
np.savez_compressed(F/'semantic-registration.npz',map_x=mapx,map_y=Y)
(F/'semantic-registration.json').write_text(json.dumps({'operation':'Bounded object-edge registration by monotone per-row horizontal coordinates. Fit physical beam and frame edges in authoritative halo and fade correction to zero at first valid two-object row.','maxDisplacement':float(np.abs(mapx-X).max()),'sourceEdgePolynomials':np.asarray(ps).tolist(),'targetEdgePolynomials':np.asarray(ts).tolist(),'fittedRows':[681,821],'appliedRows':[start,796],'sampling':'bilinear local registration','rowKnots':rows},indent=2))
south=np.asarray(Image.open(R/'r08_c15/output/r08_c15.png').convert('RGB'))
sheet=Image.new('RGB',(1254,400));sheet.paste(Image.fromarray(out[-200:]),(0,0));sheet.paste(Image.fromarray(south[:200,2842:4096]),(0,200));sheet.save(D/'qa-probes/s4-semantic-common-edge.png')
print(float(np.abs(mapx-X).max()))


# Final authoritative halo transition; used by refined candidate.
out=out.astype(float);w=np.linspace(0,1,115);w=w*w*(3-2*w);out[681:796]=out[681:796]*(1-w[:,None,None])+t[681:796]*w[:,None,None];out=np.rint(out).astype('uint8')
Image.fromarray(out).save(F/'halo-matched-upper.png')
