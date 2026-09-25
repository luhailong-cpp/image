from pathlib import Path
from PIL import Image
import hashlib,json,datetime
S=Path(__file__).resolve().parent.parent
A=S.parent.parent
T=S/'next_tile_r08_c07'
Q=T/'continuation-20260923/qa-repair-20260923'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'file':p.relative_to(A).as_posix(),'sha256':sha(p)}
def save(p,o):
    with p.open('x',encoding='utf-8') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
idx=Q/'interiors-current/index.json'
review=json.loads(idx.read_text())
candidate=Path(review['candidate']['file'])
assert sha(candidate)==review['candidate']['sha256']
for item in review['items']:
    assert sha(Path(item['file']))==item['sha256']
    item.update(reviewStatus='reviewed_no_visible_clarity_or_interior_artifact_failure',reviewMethod='Codex root viewed this entire 1024x1024 crop at original pixel detail')
review.update(reviewedAtUtc=now,reviewer='Codex root',scope='All sixteen non-overlapping 1024px interiors of current 4096 candidate; crisp rounded paving, gold inlay and carved symbols; no new visible interior failure. Does not prove world layout/navigation or unreviewed neighbors.',geometryComparedToOriginalLayout=False,sourceIndex=ref(idx))
rv=Q/'interiors-current/visual-review.json'
save(rv,review)
assert Image.open(candidate).size==(4096,4096)
assert sha(candidate)=='7e60bc705c1b750cad18bffa9f486f7be680835c1ee3bf0f692f0202325699e6'
selection={
 'schemaVersion':1,'selectedAtUtc':now,'tile':'r08_c07','appearance':'tianyong_festival',
 'candidate':{**ref(candidate),'pixels':[4096,4096]},
 'record':ref(Q/'repaired-v1/repair.json'),
 'assembly':ref(T/'continuation-20260923/versions/hard-core-20260923T075129893416Z/assembly.json'),
 'review':ref(Q/'c07-review.json'),'interiorReview':ref(rv),
 'status':'selected_candidate_partial_local_review_not_production_accepted',
 'internalFullSeamsReviewed':6,'internalJunctionsReviewed':9,'interiorRegionsReviewed':16,
 'externalFullEdgesReviewed':1,'externalEdgesPending':3,'externalFourTileJunctionsPending':4,
 'actualModel':None,'actualQuality':None,'backendModelVerified':False,
 'accepted':False,'formalArtAcceptancePassed':False,'clientRuntimeAccepted':False,
 'sourceArtUpscaled':False,'selectionReason':'Native-detail assembly with successful localized pseudo-seam repair. Selected over failed hard-core predecessor; local visual evidence is not whole-city acceptance.'}
save(T/'latest-candidate.json',selection)
print(json.dumps({'selection':str(T/'latest-candidate.json'),'sha256':sha(T/'latest-candidate.json'),'interiorReview':ref(rv)},ensure_ascii=False))
