from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];QA=Path(__file__).parent;OUT=ROOT/'output/r09_c13'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
at=datetime.now(timezone.utc).isoformat();r=read(QA/'review.json');m=read(OUT/'manifest.json');g=read(OUT/'r09_c13.png.generation.json')
target=OUT/'r09_c13.png';assert sha(target)==r['source']['sha256']==m['sha256']==g['sha256']
assert sha(m['westSource'])==m['westSourceSha256']
defects=[
 dict(id='W-COLOR-01',kind='existing_shared_edge_color_step',severity='visible_native_seam',tileCoordinateConvention='x=0 shared edge; x<0 old c12, x>=0 current c13',newTileRectXYWH=[0,0,2,320],globalEdgeX=49152,globalYRange=[32768,33088],finding='Wood face has a warm/cool color step at the old/new cut. The timber contour remains connected. This region is unchanged by the approved endpoint correction.',evidence=['shared-unrotated-1.png','return-x100-full.png','endpoints.png'],supportingMedianRGBJump=[25.5,9,-12]),
 dict(id='W-COLOR-02',kind='existing_shared_edge_color_step',severity='visible_native_seam',newTileRectXYWH=[0,1100,2,500],globalEdgeX=49152,globalYRange=[33868,34368],finding='Paving shows a straight left-warm/right-cool cut through the painted surface; it is more apparent in the rotated full strips. No missing paving contour was found here. This region is unchanged by the approved endpoint correction.',evidence=['shared-unrotated-2.png','return-x100-full.png','shared-full.png'],supportingMedianRGBJump=[-25,-15,13])
]
for q in r['qa']:
    n=Path(q['file']).name
    if n=='shared-full.png':
        verdict='defects_remaining';finding='Continuous rail/paving/roof contours across the full edge; shared-edge color differences remain, including W-COLOR-01/02.'
    elif n=='return-x100-full.png':
        verdict='pass_at_requested_return_edge';finding='The return edge is sheet y160,480,800,1120 and has no abrupt contour jump. Visible color steps at sheet y260,580,900,1220 correspond instead to old/new x0, not x100; see W-COLOR-01/02.'
    elif n=='return-x500-full.png':
        verdict='pass_in_scope';finding='Full4096px x500 return edge: wood, paving, rail and roof contours continue without duplicate lines or a visible cut at the inspected return edge.'
    elif n.startswith('repair-crossing-'):
        verdict='pass_at_requested_crossing';finding='At image y160 the repair row handoff continues paving/rail contours without an added horizontal break; existing west shared-edge color issue is tracked separately.'
    elif n.startswith('internal-crossing-'):
        verdict='pass_at_requested_crossing';finding='At image y160 the internal y boundary through the west band shows continuous paving/rail/roof lines, without an added horizontal break; existing shared-edge color issue is tracked separately.'
    elif n=='endpoints.png':
        verdict='geometry_pass_color_defect_at_north';finding='North wood boundary contour and south roof dark joint/highlight connect at native scale. South endpoint geometry correction is confirmed. North shared-edge wood color difference W-COLOR-01 remains.'
    elif n=='endpoint-return-region.png':
        verdict='pass_in_scope';finding='Corrected roof dark joint and highlight align at shared x160; transition begins image y160 and returns at x260 without a new abrupt contour, doubling, or gap. Existing painted highlight curvature remains.'
    elif n=='shared-unrotated-1.png':
        verdict='defects_remaining';finding='Native wood and paving contours continue; at image x160 the wood color step W-COLOR-01 remains.'
    elif n=='shared-unrotated-2.png':
        verdict='defects_remaining';finding='Native paving contours continue; image x160 contains W-COLOR-02 across local y76..576 (tile y1100..1600).'
    else:
        verdict='geometry_pass';finding='Native rail/roof/paving contours continue without a missing component; shared-edge tone review is covered by the full strips. This does not independently approve all west-edge color matching.'
    q.update(actuallyViewed=True,viewedAt=at,viewTool='view_image detail=original',viewScale=1,verdict=verdict,finding=finding)
    side=Path(q['file']+'.generation.json');s=read(side);s.update(actuallyViewed=True,viewedAt=at,visualReview=dict(verdict=verdict,finding=finding));write(side,s)
r.update(reviewedAt=at,result='scoped_local_seams_not_passed_color_defects_remaining',scopedLocalSeamsPassed=False,endpointCorrectionGeometryPassed=True,
    returnEdgesPassed=[100,500],repairCrossingGeometryPassed=[1100,2050,3000],internalCrossingGeometryPassed=[1024,2048,3072],
    wholeTileAccepted=False,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False,
    reviewBasis='All15 native QA images were actually viewed, including full seam strips and unrotated supplemental strips. Metrics supplement these visual findings; they are not the acceptance basis.',
    defects=defects,recommendedNextStep='Correct shared-edge color using actual old-left support, preserving accepted geometry. Recheck native full shared edge afterward. No missing structure in the inspected west scope was identified; no new AI drawing is proposed for color-only residuals.',
    missingExternalNeighborQA=['north','south','east'],sourceHashReverified=True,oldWesternSourceHashReverified=True)
write(QA/'review.json',r)
m.update(qa=r['qa'],westFinalQA=dict(file=str(QA/'review.json'),sha256=sha(QA/'review.json')),updatedAt=at,status='scoped_local_seams_not_passed_color_defects_remaining',scopedLocalSeamsPassed=False,endpointCorrectionGeometryPassed=True,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False,remainingScopedDefects=defects)
write(OUT/'manifest.json',m)
g.update(qa=m['westFinalQA'],updatedAt=at,scopedLocalSeamsPassed=False,endpointCorrectionGeometryPassed=True,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False)
write(OUT/'r09_c13.png.generation.json',g)
print(json.dumps(dict(outputSha256=sha(target),viewedImages=len(r['qa']),result=r['result'],defects=[v['id'] for v in defects])))
