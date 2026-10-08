from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from production import read,write,sha,now
F=ROOT/'r09_c15';out=F/'qa/root-structure-authorization.json'
assert not out.exists()
plan=read(F/'plan.json');idx=read(F/'qa/structure-index.json')
items=[]
for a in idx['items']:
 assert sha(a['file'])==a['sha256']
 items.append(dict(**a,actuallyViewed=True,verdict='macro_geometry_accepted_for_native_repainting',nativeScale=1 if 'segment' in a['file'] else None,displayNote='West segments viewed as 1024-square originals. Side-by-side auto-resized by host to2048x1024; both individual1254 sources were separately viewed.',scope='Planning geometry only; right half is deliberately enlarged guide, not native production QA.'))
constraints={
 'p11':'At the actual west native boundary retain the existing blue-violet cliff contour and face. Heal the straight x115 collage line into one continuous cliff/water scene. Do not add a horizon, sky or moon; the top is water surface of a continuous map.',
 'p21':'Continue the actual west rope-bound timber rail and post geometry without a step at x115. Preserve the existing ivory fabric on the west side and intended coral fabric to the right. A stitch boundary is not an object edge.',
 'p31':'Continue the existing west timber horizontal support and cropped post foot at the actual native endpoints. Keep foliage and paved floor continuous; smoothly transition lighting without a vertical material band.',
 'p41':'Continue each real western paving grout endpoint and the cropped foreground timber/round finial. Existing west paving is blue-violet; smoothly transition toward the single current lantern warm pool farther right. Do not create a hard vertical blue/orange light boundary.',
}
plan.update(stage='native_generation_authorized',rootReviewPending=False,nativePatchConstraints=constraints,allPlanningGuideHashesFrozen=True)
write(F/'plan.json',plan)
write(out,dict(reviewedAt=now(),reviewer='root',planningGeometryAccepted=True,rootReviewPending=False,items=items,planSha256=sha(F/'plan.json'),guideIndexSha256=sha(F/'guides/index.json'),currentNightStructure=plan['nightStructure'],fixed=['Removed invented sky, horizon and moon; water fills top crop again.','Retained source-night single lantern, red-brown stand and rounded jade base.'],nativeWorkRequired=['Fresh1254 native painting for every guide; do not use enlarged guides as production pixels.','Match true W cliff, rail, fabric, foliage, paving endpoints and smooth lighting; inspect all actual seams after assembly.'],formalAccepted=False,clientVerified=False,navigationVerified=False))
print(sha(F/'plan.json'))
