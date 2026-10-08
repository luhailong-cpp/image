from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
T=R/'r08_c15';Q=T/'qa/assembly'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
candidate=T/'output/r08_c15.png'
assert sha(candidate)=='78932febffe7da5557d8f07b2db4e6a8c510da27715b86bde06438b0987c2580'
initial=R/'r08_c14/output/r08_c14.png';current=R/'tiles/r08_c14.png'
a=np.array(Image.open(initial).convert('RGB'));b=np.array(Image.open(current).convert('RGB'))
assert np.array_equal(a[:,3968:],b[:,3968:])
names=['west-c14-c15-common-edge-full','corner-nw','corner-ne','corner-sw','corner-se']
record={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':{'file':str(candidate),'sha256':sha(candidate)},'reviewer':'root actual visual inspection through view_image','westNeighbor':{'file':str(current),'sha256':sha(current),'east128PixelsEqualBoundGuideSource':True},'checks':[{'file':str(Q/(n+'.png')),'sha256':sha(Q/(n+'.png')),'viewedAtNativeScale':True,'result':'pass','finding':'Continuous hull, rope, water and dock edge across common border; four corners have complete stable geometry.' if n.startswith('west-') else 'Complete corner pixels with coherent material and silhouette; no clipped artifact.'} for n in names],'scope':'Only complete native west common-edge band and four 512-square corners. Initial overview reveals internal material-shading and water-pattern mismatches; internal QA and fixes are in progress.','internalReviewAccepted':False,'formalAccepted':False,'wholeCityComplete':False}
out=T/'qa/west-corners-initial-review.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(out))
