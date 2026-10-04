from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((ROOT/'review.json').read_text(encoding='utf-8-sig'))
assert len(review['frames'])==196 and not review['staleReviews']
rows=[]
for r in review['frames']:
 p=ROOT/'runtime'/(r['slot']+'.png')
 assert r['sha256']==sha(p),str(p)
 rows.append({'slot':r['slot'],'sha256':r['sha256'],'reviewFile':r['sourceReviewFile'],'evidence':r.get('footOrientation') or r.get('toeKneeAnkleEvidence') or r.get('toeAxisEvidence') or r.get('evidence'),'overallStaticStatus':r.get('status'),'dynamicApproval':False})
out={'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'09_bamboo_archer_girl only: eight run directions plus E/W hit, attack, cast','actualRuntimePng':196,'currentRunDefaultMs':1200,'oldRunBaselineMs':480,'perFrameRunMs':75,'newPromptTemplateAssumedCorrect':False,'referenceNote':'User retracted both all moon-shadow directions and vertical directions as universally correct; each current direction assessed independently.','reviewScope':'Current full-body contact sheets, enlarged feet and frame sequence pose reading. Correct existing foot orientation retained; no mechanical leg narrowing or frame translation. See source reviews for per-frame limits.','supplementalSouthFootReview':{'file':'audit/foot-axis-20261003.md','sha256':sha(ROOT/'audit/foot-axis-20261003.md'),'scope':'run/W,S,SE; current 48 frame hashes in the report; no confirmed outward ankle twist. This newer targeted review supplements original broader reviews.'},'dynamicVisualAcceptance':False,'clientIntegration':'not_integrated','clientRuntimeAcceptance':'not_tested','frames':rows,'reviewFiles':[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'review-parts').glob('*.json'))]}
(ROOT/'audit/foot-grounding-closeout.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'framesBoundToCurrentSha':len(rows),'reviewSequences':len(review['sequences']),'dynamicApproval':False}))
