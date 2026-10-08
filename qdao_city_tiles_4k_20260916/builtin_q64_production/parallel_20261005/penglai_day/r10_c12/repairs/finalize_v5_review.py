from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
rec=json.loads((D/'candidate-record-v5.json').read_text(encoding='utf-8'))
v2=np.array(Image.open(D/'r10_c12-candidate-v2.png'));v5=np.array(Image.open(rec['file']))
assert not np.any(v2[:900]!=v5[:900])
qa=[]
for p in sorted((D/'qa-v4').glob('*full-native.png')):
 qa.append({'file':str(p),'sha256':sha(p),'actuallyViewed':True,'scale':'1:1','finding':'Reviewed all six full internal native seam lines; main structure continuous. x3072 roof edge within y<900 explicitly remains for parent north integration.'})
for n in ['wood1024','wood2048']:
 p=D/'qa-v5'/(n+'-before-after-native.png');qa.append({'file':str(p),'sha256':sha(p),'actuallyViewed':True,'scale':'1:1','finding':'New bounded return mask removes old stepped wood highlight. Narrow lateral support preserves adjacent wall/beam material; no earlier broad-mask warm blotch.'})
p=D/'qa-v4/roof1024-before-after-native.png';qa.append({'file':str(p),'sha256':sha(p),'actuallyViewed':True,'scale':'1:1','finding':'Both roof diagonal highlight notches repaired; same mask and pixels used in v5.'})
p=D/'qa-v5/nine-junctions-native.png';qa.append({'file':str(p),'sha256':sha(p),'actuallyViewed':True,'scale':'1:1','finding':'All nine 384x384 native junctions viewed. Foliage, canopy stripe order, pottery motifs, beam intersections and paving continuous. Earlier return blotch absent.'})
for r in rec['repairs']:
 assert sha(r['source'])==r['sourceSHA256'];assert sha(r['mask'])==r['maskSHA256']
 r['actuallyViewed']=True
 for suffix in ['.generation.json']:
  p=Path(r['source']+suffix);a=json.loads(p.read_text(encoding='utf-8'));assert sha(a['toolResultPath'])==a['sha256']
  a['visualFinding']='Native 1254 square output actually viewed. Local artifact healed, expected geometry and primary painted style preserved. Only precise candidate-mask pixels used; full AI crop is not substituted wholesale.';write(p,a)
rec['visualReview']={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Full v4 native-line inspection plus all v5 mask return crops and v5 nine-junction board; unchanged areas inherited by pixel identity. Native crops are never upscaled.','evidence':qa,'scopePassed':'Local changes within y>=900 ready for parent native map integration. This is not north seam, full-city or client acceptance.','pending':['Parent north seam cross-tile integration','Parent y<900 roof x3072 microstep','Parent external edges and client acceptance'],'north900UnchangedFromV2':True}
write(D/'candidate-record-v5.json',rec)
write(D/'visual-review-v5.json',dict(rec['visualReview'],candidateFile=rec['file'],candidateSHA256=rec['sha256']))
print(json.dumps({'file':rec['file'],'sha256':rec['sha256'],'changedPixels':rec['changedPixelCount'],'changedXYXY':rec['changedXYXY'],'sourceAndMaskHashesVerified':True}))
