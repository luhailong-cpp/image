"""Record actual local-return review and inherited shared-source open issue."""
from pathlib import Path
from datetime import datetime,timezone
import sys
sys.dont_write_bytecode=True
import json
import sync_c13_right_repairs as s
ROOT=Path(__file__).resolve().parent
DEST=s.DEST/'tone-matched'
m=s.read(DEST/'output/integration-manifest.json')
previous=s.read(ROOT/'r08_c13/west-final/qa/review.json')
for item in [m['output'],m['c12Unchanged']]+m['qa']:s.check(item['file'],item['sha256'])
report={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'shared_edge','status':'right-local-sync-scope-pass-common-paving-remains-open','candidate':m['output'],'c12Unchanged':m['c12Unchanged'],'integrationManifest':s.info(DEST/'output/integration-manifest.json'),'previousFullWestReview':s.info(ROOT/'r08_c13/west-final/qa/review.json'),'previousScopeCarryForward':'The entire pre-existing common-edge and left/right attachment review remains applicable outside the three exact DAY local repair rectangles. Pixel equality is explicitly verified outside the union. The center paving finding is not resolved or reclassified.',
'scope':{'actualViewedFiles':4,'nativeReturnImagePixels':[1254,1254],'localGeometryEdits':3,'unique1254ReturnRectangles':2,'sameRectangleForSteps1And2':True,'remainingCommonPavingReopened':True,'resize':False,'viewDetail':'original'},
'evidence':[{**q,'actuallyViewed':True,'viewDetail':'original','resized':False} for q in m['qa']],
'findings':[{'id':'C13-RIGHT-INSERTION-SYNC-01-03','status':'pass-in-reviewed-local-scope','finding':'All three actual DAY stone/grout edits are applied with their exact native crops and four-side masks. At the full native return perimeter, diagonal grout edges and rounded slab bevels remain continuous; no newly clipped or doubled contour is visible. Local RGB matching removes the jagged vertical paint boundary seen in the unmatched step02 composite, without changing mask paths, resampling artwork or moving geometry.','maximumFinalRgbChannelDelta':m['maximumFinalChannelDelta']}],
'remainingFindings':previous['remainingFindings'],'formalAccepted':False,'globalStateModified':False,'clientAcceptance':False,'dayReadOnly':True,'resampling':False,'geometryFlow':False,'outsideUnionChangedPixels':0,'nativeModelAndQuality':'Every conversion records actualModel=null and actualQuality=null because the builtin tool did not disclose these values.'}
s.write(DEST/'qa/review.json',report)
dep_path=ROOT/'r08_c13/repairs/west-common-edge/dependency-readiness.json';dep=s.read(dep_path)
dep['rightLocalSyncReview']=s.info(DEST/'qa/review.json');dep['latestFestivalC13Candidate']=m['output'];dep['latestFestivalC12Candidate']=m['c12Unchanged'];dep['status']='converted-composed-and-right-local-synced-common-paving-review-required'
dep['nextAction']='Parent independently reviews the recorded shared-source paving interruption. Any further geometry repair must use a shared DAY geometry contract; these candidates remain formally unaccepted.'
dep_path.write_text(json.dumps(dep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review':s.info(DEST/'qa/review.json'),'c13':m['output'],'c12':m['c12Unchanged'],'remainingFindings':len(report['remainingFindings'])},indent=2))
