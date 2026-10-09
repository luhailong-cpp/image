from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent;T=D.parents[1]
def ref(p):return dict(file=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
items=[]
def seen(rel,verdict,review):
 p=D/rel;items.append(dict(**ref(p),actuallyViewed=True,nativeScale=1,reviewer='/root/r09c14_row3_resume',verdict=verdict,review=review))
for n in ['qa-north-join','qa-return-y400','qa-return-x1024','qa-left-platform']:
 seen('current-only-v4/bounded/'+n+'.png','not_approved','Current-only AI removes the join over most width, but right fade restores the old horizontal tone step; left gap also receives an additional small leaf center, requiring root composition review. No overall pass.')
seen('masked-v2/host-result.png','rejected','Wide mask relocated leaf centers and introduced large substitute clusters. Never promoted or consumed.')
for n in ['qa-north-join','qa-return-y400','qa-return-x1024','qa-left-platform']:
 seen('thin-v3/bounded/'+n+'.png','not_approved','Restoring immutable true north clips newly interpreted leaf highlights at the contact; straight seam remains. Returns alone are insufficient for pass.')
for s in [1,3]:seen(f'local-tone-sigma{s}/qa-join.png','rejected','Local residual tone field does not solve the geometry/material contact; sigma1 introduces vertical tone streaks and sigma3 leaves a ruler-straight join. Helpers and production unchanged.')
for n in ['v4-qa-p11-north','v4-qa-p12-north','v4-qa-owner-x1024','raw-qa-p12-north','raw-qa-p13-north']:
 seen('row1-ownership-review/'+n+'.png','fail','Actual NE row1 ownership and original bounded registration reproduce visible north join. p11 body-only repair is recolored against stale approximate native halo; p12 and p13 separately retain real north material/tone steps.')
seen('row1-ownership-review/raw-qa-p14-north.png','pass_scoped_view','Previously approved p14 remains visually continuous through north rock and water in this partial-row reproduction; no new approval of whole tile.')
seen('current-only-v4/exact-north/qa-p11-north.png','partial_improvement_pending','Restoring exact immutable NORTH support before original production registration preserves continuous leaves for approximately local x0..900. Right fade still reaches old p11/p12 north band. Whole patch is not approved.')
seen('current-only-v4/exact-north/qa-owner-x1024.png','fail','The residual y0 line crosses current tile x~924..1324, including actual p12 ownership beyond x1024. Further p11-only fading cannot solve p12 north pixels.')
canonical=[ref(T/'native'/f'p1{c}.png') for c in range(1,5)];assert canonical[0]['sha256']=='6f0c9fd4eb3f68c34fd299cf9b98f12be3134598c645f23bd29dafa87a2c227f'
record=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),script=ref(__file__),canonicalSources=canonical,plan=ref(T/'plan.json'),items=items,allCanonicalPNGsUnchanged=True,noProductionAssemblyWritten=True,scopedPass=False,approvedForPromotion=False,remainingIssues=['Right-side fade still returns to known bad north join at p11/p12 boundary.','p12 north join is a separate true source defect in production preview.','p13 north foliage/rock join is separately visible in production preview.','Small left leaf center introduced by current-only-v4 requires composition approval or targeted refinement.'],proposal=ref(D/'current-only-v4/exact-north/p11-proposal.png'),productionReproduction=ref(D/'current-only-v4/exact-north/diagnostic.json'),nextAction='Root visual review and explicit scope for p12/p13; retain current p11 as unpromoted proposal. Do not generate p21 or other dependents from stale input.')
write(D/'iteration-review-20261009.json',record);print(json.dumps(dict(review=ref(D/'iteration-review-20261009.json'),actuallyViewedImageCount=len(items),scopedPass=False)))
