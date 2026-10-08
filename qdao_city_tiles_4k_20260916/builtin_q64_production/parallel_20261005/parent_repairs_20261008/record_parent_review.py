from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
views={'west-upper':['union-v2-whole-local.png'],
       'east-lower':['center.png','north.png','south.png','west.png','east.png'],
       'corner-left-return':['diagonal-center.png','horizontal-center.png'],
       'corner-right-return':['center-before-after.png','return-top.png','return-bottom.png','return-left.png','return-right.png']}
notes={
 'west-upper':'Triangle, selected gold trim step and slab horizontal step improved. No new hard patch boundary in displayed local crop. Existing upper vertical slab tone boundary outside mask remains.',
 'east-lower':'All five current native boards actually viewed; former short vertical line removed and extended return smooth. Real grout and perpendicular divider unchanged.',
 'corner-left-return':'Both target native centers actually viewed, diagonal grout and horizontal curved strips continuous. Four return conclusions rely on the named subagent visual review.',
 'corner-right-return':'Before/after center and all four native return strips actually viewed. Three arcs now cross the former vertical cut smoothly with no new localized contour kink. Upper ground tone outside the mask remains unreviewed.'}
data=[]
for name,boards in views.items():
    review=R/name/'review.json'; bind=R/name/('binding.json' if name in ['west-upper','corner-right-return'] else 'bindings.json')
    data.append(dict(branch=name,limitedRepairAcceptedForMerge=True,note=notes[name],
       fullSharedEdgeAccepted=False,formalAccepted=False,review=str(review),reviewSha256=sha(review),
       bindings=str(bind),bindingsSha256=sha(bind),
       parentActuallyViewed=[{'file':str(R/name/'qa'/b),'sha256':sha(R/name/'qa'/b),'detail':'original'} for b in boards]))
(R/'parent-reviewed-scopes.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
    reviewer='/root',reviewScope='Only specific repair windows; subagent original-pixel return reviews remain scoped to their reports.',branches=data),indent=2),encoding='utf-8')
print('Recorded 4 limited parent reviews; no complete edge or formal acceptance claimed.')
