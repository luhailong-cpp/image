"""Save the actual visual review scope and latest left-neighbor comparison."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
O=Path(__file__).resolve().parent
T=O.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v004=T/'current/v004/r08_c10-fragment.png'
left=Image.open(v004).convert('RGBA').crop((1024,0,2278,1254))
left.save(O/'latest-v004-context.png')
joined=Image.open(O/'joined.png').convert('RGB')
board=Image.new('RGB',(468,857),(255,0,255))
board.paste(joined.crop((0,397,230,1254)),(0,0))
board.paste(left.convert('RGB').crop((0,397,230,1254)),(238,0))
board.save(O/'qa/v2-left-v004-comparison.png')
save(O/'latest-v004-context.png.generation.json',{'derivedFrom':[info(v004)],'operation':'Original-pixel crop [1024,0,2278,1254] from fragment whose tile origin is [909,1933], yielding patch tile box [1933,1933,3187,3187]. No new model call.','output':info(O/'latest-v004-context.png'),'nativePixelScale':1})
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'Codex audit_layout',
 'output':info(O/'joined.png'),
 'viewed':[info(O/'joined.png'),info(O/'qa/lower-return-1254x454.png'),info(O/'qa/right-return-354x1254.png')],
 'bottomRightLocalAccepted':True,
 'observations':['Former abrupt y1024 kinks are absent; lower contours change continuously over the wider transition, without abrupt width changes.',
 'Right cloud contours remain present and continuous, no broad optical-flow displacement.',
 'Exact source ownership verified for all original known context pixels; horizontal maximum19.733113, dy0.',
 'Seven signed-gradient contour residuals in source overlap have maximum0.795013px. This is a sampled check, not full4K acceptance.'],
 'latestLeftNeighbor':info(v004),
 'latestLeftComparison':info(O/'qa/v2-left-v004-comparison.png'),
 'latestLeftIssue':{'patchX':[192,216,224],'nativeBandTopY':[693,694,694],'v004BandTopY':[684,684,684],
                   'requiredOutputVerticalMovePx':[-9,-10,-10],'lowerBandEdgeMatches':True,
                   'description':'Existing broad horizontal stone band has a9..10px different top edge and matching bottom edge; horizontal-only registration cannot resolve it.'},
 'localAccepted':False,'integrationReady':False,'formalAccepted':False,
 'remaining':'Register latest left context under explicit vertical-shift allowance, then inspect all new return edges. Current image must not overwrite v004.'}
save(O/'visual-review.json',review)
a=json.loads((O/'assembly.json').read_text());a.update({'localAccepted':False,'bottomRightLocalAccepted':True,'integrationReady':False,'requiresVisualReview':False,'visualReview':info(O/'visual-review.json'),'latestLeftContextPending':True});save(O/'assembly.json',a)
g=json.loads((O/'joined.png.generation.json').read_text());g['assembly']=info(O/'assembly.json');save(O/'joined.png.generation.json',g)
print(json.dumps({'visualReview':info(O/'visual-review.json'),'integrationReady':False}))
