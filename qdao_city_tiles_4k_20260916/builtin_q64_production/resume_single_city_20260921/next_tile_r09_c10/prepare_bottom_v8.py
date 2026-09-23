from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;Q=P/'repairs/external-prepared/bottom-single-edge-v8';Q.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((P/'repairs/external-prepared/bottom-double-line/prepared.json').read_text(encoding='utf-8'))
source=P/'repairs/versions/external-v7/r09_c10.png';record=source.parent/'repair.json'
core=np.array(Image.open(source).convert('RGB'));bottom=np.array(Image.open(r['neighbor']['file']).convert('RGB'))
context=np.concatenate([core[3469:,797:2051],bottom[:627,797:2051]],axis=0)
Image.fromarray(context).save(Q/'context-native-1254.png')
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
alpha=smooth((1-((xx-760)/530)**2-((yy-550)/390)**2)/.4)*smooth((1253-xx)/35)
alpha[yy>=627]=0
mask=np.rint(alpha*255).astype(np.uint8);Image.fromarray(mask).save(Q/'mask.png')
r.update({'id':'bottom-single-edge-v8','source':{'file':str(source),'sha256':sha(source)},'sourceRecord':{'file':str(record),'sha256':sha(record)},'context':{'file':str(Q/'context-native-1254.png'),'sha256':sha(Q/'context-native-1254.png')},'mask':{'file':str(Q/'mask.png'),'sha256':sha(Q/'mask.png')},'maskNote':'New core includes final row y=626; all actual neighbor rows y>=627 remain exactly zero mask. No arbitrary 30px freeze above true boundary.'})
(Q/'prepared.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
for version in ['external-v6','external-v7']:
 q=P/'repairs/versions'/version
 (q/'visual-review.json').write_text(json.dumps({'candidate':{'file':str(q/'r09_c10.png'),'sha256':sha(q/'r09_c10.png')},'externalVisualReviewPassed':False,'bottomBoundaryPassed':False,'leftTargetedRepairPassed':version=='external-v7','failure':'Bottom extra groove was extended in native output across fixed true neighbor; candidate-only mask leaves a tapering wedge at local x550,y615. Native generated geometry at boundary disagrees with actual neighboring core.','productionAccepted':False,'scopedLocalContinuityPassed':False},indent=2),encoding='utf-8')
