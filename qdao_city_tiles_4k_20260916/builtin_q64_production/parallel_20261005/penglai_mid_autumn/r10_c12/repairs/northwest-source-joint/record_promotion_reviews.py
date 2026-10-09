from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent;V=D/'stage2-bounded'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
old=read(V/'visual-review.json');oldby={Path(x['file']).name:x for x in old['items']}
idx=read(V/'standard-qa/index.json');items=[]
for x in idx['items']:
 p=Path(x['file']);assert sha(p)==x['sha256'];n=p.name
 if n in oldby:
  o=oldby[n];assert o['actuallyViewed'] and o['sha256']==sha(p)
  evidence=dict(kind='exact_image_review_reuse',originalReview=ref(V/'visual-review.json'),originalCandidate=old['eastCandidate'],reason='The already actually viewed PNG is exactly the same file and SHA; no pixels changed.',newActualView=False)
  review=o['review']
 else:
  assert x['identicalToOldCanonicalReconstruction']
  evidence=dict(kind='new_actual_original_view',reviewedAt=now,viewTool='view_image',viewDetail='original',notInferredFromNumericalEquality=True)
  review='Native full strips and junction inspected: continuous stone/wood/cloth/foliage outlines and broad paint, no obvious straight join, duplicate contour or return boundary. Absent neighbor scopes remain unverified.'
 items.append(dict(**ref(p),actuallyViewed=True,nativeScale=1,verdict='current_pixels_inspected_neighbor_unverified' if 'no-neighbor' in n else 'scoped_pass',review=review,reviewer='/root/r09c14_row3_resume',evidence=evidence,identicalToOldCanonicalReconstruction=x['identicalToOldCanonicalReconstruction']))
assert len(items)==27 and sum(x['evidence']['newActualView'] if 'newActualView' in x['evidence'] else True for x in items)==21
write(D/'promotion-standard-review.json',dict(recordedAt=now,candidate=ref(V/'r10_c12-proposal.png'),items=items,scopedPass=True,issueCount=0,issues=[],all27ActuallyViewed=True,changedSixReusedExactActualReview=True,unchanged21NewlyViewed=True,formalAccepted=False,missingExternalNeighbors=['west','east','south']))
names=[f'qa-north-{i}.png' for i in range(1,5)]+['qa-return-x1416.png','qa-return-y320.png','qa-true-four-image-corner.png','p14-proposal.png','qa-p14-north.png','qa-p14-east.png','qa-p14-ne-corner.png','qa-p14-north-return.png','qa-p14-east-return.png','qa-return-x416.png','qa-return-y256.png']
write(D/'root-joint-promotion-authorization.json',dict(recordedAt=now,reviewer='root',source='Explicit parent message reporting actual original-scale 15-image review and authorizing guarded promotion + consumer migration.',items=[dict(**ref(V/n),actuallyViewed=True,nativeScale=1,verdict='pass_local') for n in names],approvedEast=ref(V/'r10_c12-proposal.png'),approvedP14=ref(V/'p14-proposal.png'),approvedActions=['TEXT snapshots of all old current records','replace two approved PNGs','migrate current r10_c11 plan/E context and full p14 derivation while preserving original AI requests','migrate current r10_c12 generation/manifest/progress/QA','migrate r10_c13 current source metadata with exact pixel reuse, PNG and frozen-at/assembly unchanged'],forbidden=['delete','root progress writes','rewrite old AI request or immutable assembly','whole-city formal acceptance'],localVisualPass=True))
print('27 standard review entries and 15 root actual-view authorization entries saved')
