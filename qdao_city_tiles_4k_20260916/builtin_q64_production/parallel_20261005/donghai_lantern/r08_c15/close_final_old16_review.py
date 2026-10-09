from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,numpy as np
from PIL import Image
T=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_lantern")/"r08_c15"
D=T/"repairs/approved-sync-final"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {"file":str(p),"sha256":sha(p)}
M=D/"output/integration-manifest.json"
j=read(M);assert j["candidate"]["sha256"]=="3d0b9871e8c95c88d0e9852f17b8dc9ae84c6c746f48605ac7c98628b67f2e25"
assert sha(j["candidate"]["file"])==j["candidate"]["sha256"]
prior=T/"repairs/approved-sync/qa/review-old16-repair-returns.json"
pj=read(prior);ids={g["id"] for g in pj["groups"]};old={Path(e["file"]).name:e for e in pj["windows"]}
groups=json.loads(r'''[{"start":0,"end":5,"status":"pass","finding":"Blue trim and awning material returns are continuous; warm reflection and timber grain repairs introduce no edge break."},{"start":5,"end":10,"status":"pass","finding":"Repaired awning paint and blue-panel light strokes return naturally to original material; no added cutoff."},{"start":10,"end":15,"status":"pass","finding":"Former hull-waterline step is gone and lower hull follows a continuous diagonal, with coherent dark rim and warm water reflections."},{"start":15,"end":20,"status":"pass","finding":"Previously sawtooth and vertical reflection splices now flow into continuous water brushwork; all left-water returns remain coherent."},{"start":20,"end":26,"status":"pass","finding":"Hull notch and overlapping water reflection defects are resolved in shared views. Mooring post and boardwalk contours remain intact."},{"start":26,"end":32,"status":"pass","finding":"Overlap views confirm smooth water and repaired contact line. Subtle lower-water pink reflection remains the previously classified non-structural variation."},{"start":32,"end":38,"status":"pass","finding":"Lantern-side timber material and blue trim reflection now transition cleanly; lamp geometry, shadows and boat contact remain connected."},{"start":38,"end":43,"status":"pass","finding":"Right-side return is continuous. Both repaired left-water reflection defects are absent in full and overlapping returns; pier silhouette remains exact."},{"start":43,"end":46,"status":"pass","finding":"Roof/awning changes return cleanly into original timber and trim; no new boundary or silhouette defect."}]''')
change=[];same=[]
for q in j["qa"]:
 name=Path(q["file"]).name
 if name not in old:continue
 assert sha(q["file"])==q["sha256"]
 e={**q,"scope":"old16-repair-returns"}
 if q["pixelIdenticalToPriorActualQa"]:
  o=old[name];assert sha(o["file"])==o["sha256"]
  assert np.array_equal(np.asarray(Image.open(q["file"])),np.asarray(Image.open(o["file"])))
  e.update(actualReviewInheritedFrom=o,inheritanceMethod="exact full-window RGB pixel equality; prior original-size actual view")
  same.append(e)
 else:
  e.update(actuallyViewed=True,viewTool="view_image",detail="original",visualReview="pass",newBlockingDefects=[])
  change.append(e)
assert len(change)==46 and len(same)==34
for g in groups:
 for e in change[g["start"]:g["end"]]:e["finding"]=g["finding"]
assert all("finding" in e for e in change)
report={"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"c14_shared_edge","candidate":j["candidate"],"extendedContext":j["extendedContext"],"manifest":ref(M),"priorActualReview":ref(prior),"status":"pass-old16-final-repair-returns","actualChangedWindowsViewed":46,"unchangedWindowsInheritedAfterExactRgbComparison":34,"totalOld16Coverage":80,"actualChangedViews":change,"unchangedInheritedViews":same,"resolvedFindings":["hull waterline notch restored to continuous DAY-authority tangent","water sawtooth reflection splice repaired","water narrow vertical reflection interruption repaired","blue board and roof/awning material returns continuous"],"nonblockingClassification":ref(T/"repairs/approved-sync/qa/lower-water-color-classification.json"),"pixelEditsMade":False,"scopeExclusions":["new3 repair sources","tile full internal seam groups","tile corners","9 junctions","west shared edge"]}
out=D/"qa/review-old16-repair-returns.json";assert not out.exists()
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"review":ref(out),"candidate":j["candidate"],"actualChanged":46,"inheritedExact":34}))

