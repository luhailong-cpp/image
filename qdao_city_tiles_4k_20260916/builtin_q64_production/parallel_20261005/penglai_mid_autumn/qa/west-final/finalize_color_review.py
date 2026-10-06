from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];QA=Path(__file__).parent;OUT=ROOT/'output/r09_c13';TR=QA/'color-trial'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
at=datetime.now(timezone.utc).isoformat();r=read(QA/'review.json');m=read(OUT/'manifest.json');g=read(OUT/'r09_c13.png.generation.json');tr=read(TR/'trial-record.json')
assert sha(OUT/'r09_c13.png')==r['source']['sha256']==m['sha256']==g['sha256']
newly_viewed=['shared-full.png','return-x100-full.png','return-x256-full.png','endpoints.png','repair-crossing-1100.png','internal-crossing-1024.png','shared-unrotated-1.png','shared-unrotated-2.png']
for q in r['qa']:
    n=Path(q['file']).name
    if n in newly_viewed:
        q.update(actuallyViewed=True,viewedAt=at,viewTool='view_image detail=original',viewScale=1)
        if n in ['return-x100-full.png','return-x256-full.png']:
            q.update(verdict='pass_at_requested_return_edge',finding='The inspected return edge is smooth, with no added line or abrupt color-field ending. It does not establish acceptance of every old/new shared-edge region visible elsewhere in the strip.')
        elif n in ['repair-crossing-1100.png','internal-crossing-1024.png']:
            q.update(verdict='pass_in_scope',finding='The corrected paving and y-crossing retain native contours and texture; no new horizontal color band is visible. Color returns smoothly before newx256.')
        elif n=='shared-unrotated-2.png':
            q.update(verdict='pass_in_applied_color_scope',finding='Tiley1100..1600 same paving surface now matches naturally. Fade-in/out ranges introduce no new abrupt band. Unmodified regions beyond the applied range are not newly accepted.')
        elif n in ['shared-unrotated-1.png','endpoints.png']:
            q.update(verdict='limited_color_pass_north_contour_protected',finding='Reliable same-material north supports were corrected without visible banding. Northy50..300 retains original post-shadow/rail pixels because the old left gradient is a contour. A pure brightness-step interpretation there was not justified. South endpoint is unchanged by this color operation.')
        else:
            q.update(verdict='limited_color_scope_pass',finding='Paving color defect in the applied core is improved and the new field has no abrupt return. Full shared-edge acceptance remains false pending north contour triage and residual unmodified color differences.')
    assert q['actuallyViewed']
    side=Path(q['file']+'.generation.json');s=read(side);s.update(actuallyViewed=True,viewedAt=q['viewedAt'],visualReview=dict(verdict=q['verdict'],finding=q['finding']));write(side,s)
for q in tr['qa']:
    side=Path(q['file']+'.generation.json');s=read(side);s.update(actuallyViewed=True,viewedAt=q['viewedAt'],visualReview=dict(verdict=q['verdict'],finding=q['finding']));write(side,s)
resolved=dict(id='W-COLOR-02',status='resolved_in_named_core',newTileYRange=[1100,1600],finding='Native visual inspection confirms natural same-material continuity, without moving the paving joint. RGB median jump changed from[-25,-15,13] to[0,0,0].',evidence=['shared-unrotated-2.png','color-trial/paving-all.png','return-x256-full.png'])
remaining=[dict(id='W-NORTH-CONTOUR-01',reclassifies='W-COLOR-01',status='needs_contour_triage_not_more_color',newTileRectXYWH=[0,50,12,250],globalRectXYWH=[49152,32818,12,250],finding='The old support falls on a narrow post shadow and rail intersection. At representativey150 and200, old last-column R gradients are14/24 while the old/new R jump is25..27. This is partly a natural contour rather than a flat material color mismatch. It was protected unchanged. No claim of missing structure or necessary AI redraw is supported yet.',evidence=['shared-unrotated-1.png','color-trial/north-all.png']),dict(id='W-RESIDUAL-COLOR-03',status='outside_applied_color_scope',newTileRectXYWH=[0,1696,2,804],globalRectXYWH=[49152,34464,2,804],finding='Small shared-edge tonal differences remain farther down the paving after the bounded correction returns to zero. These pixels were not modified; broader field application would require same-material support verification near the approaching rail.',evidence=['return-x100-full.png','shared-full.png'])]
r.update(reviewedAt=at,result='bounded_color_scope_passed_remaining_seam_triage',appliedColorScopePassed=True,scopedLocalSeamsPassed=False,wholeTileAccepted=False,
    formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False,defects=remaining,resolvedDefects=[resolved],
    reviewBasis='Eight changed/new native QA images were actually re-viewed after merge; eight unchanged native crops retain identical PNG SHA and prior actual visual review. All five color-trial crops were actually viewed before merge.',
    recommendedNextStep='Triage north post/rail contour separately before any geometry change. If extending color correction downward, verify same-material support through the rail approach. Do not suppress contour errors with larger color offsets.',
    colorCorrectionLimits=dict(maxRGB=32,actualMaxRGB=tr['actualMaximumColorCorrectionRGB'],geometryDisplacement=0,artworkResampling=False,artworkBlurred=False,xReturn=256),
    remainingPureColorVsStructureUncertainty='Northy50..300 is not proven to be a missing component; no AI redraw is recommended solely from the boundary color metric.')
write(QA/'review.json',r)
m.update(updatedAt=at,status=r['result'],qa=r['qa'],westFinalQA=ref(QA/'review.json'),appliedColorScopePassed=True,scopedLocalSeamsPassed=False,remainingScopedDefects=remaining,resolvedScopedDefects=[resolved],formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False)
write(OUT/'manifest.json',m)
g.update(updatedAt=at,qa=ref(QA/'review.json'),appliedColorScopePassed=True,scopedLocalSeamsPassed=False,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False)
write(OUT/'r09_c13.png.generation.json',g)
reject=OUT/'evidence/rejected-color-trial1.record.json';rej=read(reject);rej.update(rejected=True,reason='Support crossed the post-shadow contour; native trial visibly produced horizontal color bands. Never applied to production. Superseded trial pixels were not retained as backup images.');write(reject,rej)
print(json.dumps(dict(outputSha256=sha(OUT/'r09_c13.png'),reviewSha256=sha(QA/'review.json'),appliedColorScopePassed=True,scopedLocalSeamsPassed=False)))
