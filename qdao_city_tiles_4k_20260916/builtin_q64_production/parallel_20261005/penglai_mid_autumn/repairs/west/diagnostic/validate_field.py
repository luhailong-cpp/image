from pathlib import Path
import json,numpy as np
from PIL import Image
P=Path(__file__).parent;f=np.load(P/'anchored-flow.npy');yy,xx=np.mgrid[:1254,:742].astype(np.float32)
u=xx+f[:,:,0];v=yy+f[:,:,1]
duy,dux=np.gradient(u);dvy,dvx=np.gradient(v);det=dux*dvy-duy*dvx
z=det[850:,115:215]
r=json.loads((P/'anchored-record.json').read_text(encoding='utf-8'))
r['flowJacobianInAppliedRegion']=dict(min=float(z.min()),median=float(np.median(z)),max=float(z.max()),foldedPixelCount=int((z<=0).sum()))
r['visualReview']['finding']='At native scale the dark joint and roof-face highlight cross the old/new boundary continuously; return at new x100 shows no abrupt structural doubling. Existing painted highlight curvature retained. No missing roof component in this endpoint scope. Other seam regions are not accepted by this trial.'
r['extrapolation']='Old-left-only Farneback median x590:615 with explicit measured endpoint correspondences oldY→rawY [1121→1129,1169→1179,1210→1207,1235→1237], dx=0 for those anchors; source-sampling displacement is smoothly returned to existing production field by new x100.'
(P/'anchored-record.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(metrics=r['metrics'],jacobian=r['flowJacobianInAppliedRegion'])))
