from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent.parent;A=S.parent.parent
out=S/'continuation-20260923/row8-neighbor-review-20260923T134322752332Z'
p=out/'index.json';raw=p.read_bytes();d=json.loads(raw.decode('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
findings={
 'r08_c07|r08_c08':('passed',['passed']*4,'All four native 1024 segments show continuous slab edges, rounded bevels and gold/ivory bands; no visible rectangular join at the x512 review centerline.'),
 'r08_c08|r08_c09':('failed',['pending','passed','failed','pending'],'Segment3 has a visible straight tone/material step at review x512 (shared tile boundary), especially on the broad slate plane. Segment1 gold joint irregularity and segment4 broad-circle tone remain conservatively pending. Full edge fails despite segment2 local continuity.'),
 'r08_c07|r09_c07':('passed',['passed']*4,'Full edge viewed with 512 native pixels on each side; slab joints, carvings and gilded border remain visibly connected; no new obvious straight seam found.'),
 'r08_c08|r09_c08':('failed',['pending','passed','failed','failed'],'Slanted cut ends near tile bottom are now rounded; segments3/4 still transition from clean upper stone to visibly mottled lower stone, failing the clean matching material requirement. Segment1 carving/finish remains pending; no whole-edge pass.'),
 'r08_c09|r09_c09':('failed',['failed','passed','pending','failed'],'Segments1/4 show strong cloudy mineral texture starting on the fixed lower neighbor. Segment2 geometry is locally continuous. Segment3 gold/material remains conservatively pending. Review uses selected r08 v2 and fixed r09 v6, not the separate proposed pair repair.'),
 'junction_r08_c07':('passed',['passed'],'Actual four selected SHA intersection viewed in 1024-square native context; long ivory band and surrounding slab boundaries cross the joint without a visible rectangular cut.'),
 'junction_r08_c08':('failed',['failed'],'Four-SHA context retains inconsistent lower-right cloud material versus clean upper stone and differs across the lower pair; broad junction material review fails even where the central outline is geometrically connected.')}
for tid,ref in d['sourceCandidates'].items():assert sha(A/ref['file'])==ref['sha256'],f'Candidate changed {tid}'
for item in d['items']:
    result,parts,notes=findings[item['id']]
    assert len(parts)==len(item['evidence'])
    item.update(result=result,finding=notes,reviewedAtOriginalPixels=True,wholeCityArtGatePassed=False)
    for proof,status in zip(item['evidence'],parts):
        assert sha(A/proof['file'])==proof['sha256']
        proof['reviewStatus']=status
d.update(reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='Codex root original-pixel image inspection',sourceIndex={'file':p.relative_to(A).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()},scope='Only the five available row8 neighboring edges and two complete four-tile junctions listed here. All other whole-city items remain pending unless independently evidenced.',counts={'edgesReviewed':5,'scopedEdgesPassed':2,'edgesFailed':3,'fourTileJunctionsReviewed':2,'scopedJunctionsPassed':1,'junctionsFailed':1},formalAccepted=False,runtimeAccepted=False)
dest=out/'visual-review.json'
with dest.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'review':str(dest),'sha256':sha(dest),'counts':d['counts']}))
