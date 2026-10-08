"""Record root's already performed original-pixel views; does not edit art."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
base=ROOT/'r09_c08/canopy-repair'
def ref(p):
 return {'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def scope(version,name,observation,requires_repair):
 p=base/version/name
 return {**ref(p),'pixels':list(Image.open(p).size),'actuallyViewed':True,
   'method':'tools.view_image(detail=original), no resizing or processed display',
   'observation':observation,'requiresRepair':requires_repair}

items=[
 scope('candidate-v5','qa-short-edge-real-join220x120.png','The earlier bright horizontal cut through the right side of the central leaf lobe is no longer actionable in this original-pixel crop. Mild rounded petal tonal transitions remain.',False),
 scope('candidate-v5','qa-canopy-mask-surround700x420.png','Canopy, trunk and adjacent stone remain coherent. No new rectangular patch bottom, needle-shaped masks or detached leaf fragments observed.',False),
 scope('candidate-v5','qa-real-north1254x512.png','Canopy continuity is suitable for continuing native production. Low-contrast horizontal ground-material transition outside the crown remains visible and requires full north-strip assessment at final tile QA.',False),
 scope('candidate-v5','qa-right-mask-edge160x290.png','No displaced crown contour or groove discontinuity in this crop. Low-contrast north-ground material transition remains for final strip assessment.',False),
 scope('candidate-v5','qa-bottom-mask-edge700x120.png','Trunk, paving and groove across the patch bottom show no rectangular clipping introduced by the repair.',False),
]
image=ref(base/'candidate-v5/candidate1254.png')
assert image['sha256']=='a8e8ece5cf8ea2a958536b2674e588451781b62129129750937abb55ec12a6fc'
out={
 'schemaVersion':1,'reviewer':'root','recordedAtUtc':datetime.now(timezone.utc).isoformat(),
 'candidate':image,'scope':'Canopy patch and immediate surrounds only; continuation approval, not final tile acceptance.',
 'actuallyViewedScopeCount':len(items),'checks':items,
 'canopyRequiresRepair':False,'approvedForDerivedNativeContinuation':True,
 'earlierRejectedCandidate':{'image':ref(base/'candidate-v4c/candidate1254.png'),
   'actuallyViewedFiles':[ref(base/'candidate-v4c'/n) for n in ['qa-short-edge-real-join220x120.png','qa-short-edge220x120.png','qa-real-north1254x512.png']],
   'reason':'The right lobe retained a short horizontal bright surface at the real north boundary; v5 uses explicit localized RGB bounds to address saturation after geometric registration.'},
 'remaining':['Full tile internal and neighbor QA after all sixteen cells exist.','Assess low-contrast north-ground transition across the whole true north join.'],
 'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False
}
p=base/'root-v5-review.json'
assert not p.exists()
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(ref(p)))
