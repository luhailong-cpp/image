from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;D=T/'repairs/approved-sync-final';M=D/'output/integration-manifest.json';P=T/'repairs/approved-sync/qa/vertical-and-new-three-review.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
m=read(M);prior=read(P);names={Path(e['file']).stem for e in prior['actualViews']};actual=[];inherited=[]
for e in m['qa']:
 if e['name'] not in names:continue
 assert sha(e['file'])==e['sha256']
 if e['pixelIdenticalToPriorActualQa']:
  assert sha(e['previousQa']['file'])==e['previousQa']['sha256']
  assert np.array_equal(np.asarray(Image.open(e['file'])),np.asarray(Image.open(e['previousQa']['file'])))
  inherited.append(e)
 else:actual.append({**e,'actuallyViewed':True,'pixelScale':1})
assert len(actual)==16 and len(inherited)==15
refs=[x for e in m['repairs'] for x in [e['completion'],e['review'],e['native'],e['mask'],e['patchedWindow']]]+m['priorReviews']
assert all(sha(e['file'])==e['sha256'] for e in refs)
report={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_c13_repairs','candidate':m['candidate'],'integrationManifest':ref(M),'priorActualReview':ref(P),'scope':'12 complete vertical seam parts, all four tile corners, and three additional source windows plus their four returns','actuallyReviewedChangedWindows':actual,'actualChangedCount':16,'inheritedPixelIdenticalWindows':inherited,'inheritedCount':15,'result':'pass for internal local repair scope; actual western shared-edge integration remains pending','observations':['The two left-water splice defects are gone and the warm reflection continues naturally.','The vessel hull waterline is continuous across the repaired step.','The wooden plank paint, blue painted bevel and roof fabric now meet continuously, retaining object contours.','Four corners and all unaffected windows inherit prior actual review only after exact pixel equality.'],'remainingOutsideScope':[{'id':'western-source-water-line','tileRectXYXY':[0,3120,128,3250],'finding':'Protected west128 still contains a DAY-inherited near-horizontal crop line around y3187. This must be checked/fixed together with actual c14/c15 shared-edge blending. Not marked passed.'}],'referenceAudit':{'verifiedReferences':len(refs),'mismatchCount':0},'formalAccepted':False,'globalRegistryModified':False}
(D/'qa/vertical-and-new-three-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'review':ref(D/'qa/vertical-and-new-three-review.json'),'actual':len(actual),'inherited':len(inherited),'referenceAudit':report['referenceAudit']}))
