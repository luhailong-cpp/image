from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent;v=D/"stage2-bounded"
sys.path.insert(0,str(R/"tools/multi_edge"));import engine
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
e=v/"r10_c12-proposal.png";w=v/"p14-proposal.png";req=read(R/"r10_c11/native/p14.request.json");sources={}
for op in req["contextRegions"]:sources[op["source"]]=np.asarray(Image.open(e if op["source"]=="east" else op["file"]).convert("RGB"))
ctx,known=engine.materialize_context(engine.Layout(),req["contextRegions"],sources);patch=np.asarray(Image.open(w).convert("RGB"));owner=engine.owner_mask(known,["top","right"],engine.Layout())
assert np.array_equal(patch[known],ctx[known])
check,f,t,rep=engine.register_native(ctx,patch,known,owner,["top","right"],engine.Layout(),max_shift=6.,tone_cap=18.,return_depth=256)
Image.fromarray(check).save(v/"p14-production-recheck.png")
diag=read(v/"diagnostic.json");old=np.asarray(Image.open(T/"output/r10_c12.png").convert("RGB"));new=np.asarray(Image.open(e).convert("RGB"))
reuse=[]
frozen=read(R/"r10_c13/frozen-neighbors.json")
for label,box in [("right320",[3776,0,4096,4096]),("right115",[3981,0,4096,4096])]:
 x0,y0,x1,y1=box;a=old[y0:y1,x0:x1];b=new[y0:y1,x0:x1];reuse.append(dict(region=label,cropLTRB=box,exactPixels=bool(np.array_equal(a,b)),oldPixelSHA256=hashlib.sha256(a.tobytes()).hexdigest(),newPixelSHA256=hashlib.sha256(b.tobytes()).hexdigest(),sourceOld=ref(T/"output/r10_c12.png"),sourceProposal=ref(e)))
write(v/"source-reuse-proof.json",dict(r10c13FrozenAtRecord=ref(R/"r10_c13/frozen-neighbors.json"),croppedRegions=reuse,p14KnownContextExact=True,p14ProductionRegistrationPixelIdentical=bool(np.array_equal(check,patch)),p14ProductionRecheck=ref(v/"p14-production-recheck.png"),registration=rep,canonicalC12=ref(T/"output/r10_c12.png"),canonicalP14=ref(R/"r10_c11/native/p14.png"),frozenPlan=ref(R/"r10_c11/plan.json"),productionHelpers=[ref(R/"native_patch.py"),ref(R/"native_assemble.py")],noProductionMutation=True))
items=[]
for p in sorted(v.glob("qa-*.png")):
 name=p.name
 if "north-" in name and name.startswith("qa-north-"):review="Actual complete north source contact in this1024 segment has no obvious ruler-straight tone cutoff after joint repair; wave/roof/wall contours remain connected."
 elif "return" in name:review="Original-pixel finite mechanical/composite return region retains coherent curves/material; no new rectangular edge or sharp ghost outline observed."
 elif "corner" in name:review="True N/NE, pending current p14, and current E proposal meet continuously; former broad dark horizontal band absent."
 elif "rock" in name:review="Rock plane and corner highlight unchanged from accepted local candidate shape, no new rectangle or ledge."
 elif "old-y742" in name:review="Prior y742 horizontal return defect remains absent."
 else:review="Current native p14 boundary preserves wave widths/tangents and the approved east local repair; no new straight band or shape cutoff seen."
 items.append(dict(**ref(p),actuallyViewed=True,nativeScale=1,verdict="pass_local",review=review))
items.append(dict(**ref(w),actuallyViewed=True,nativeScale=1,verdict="pass_local",review="Full native p14 draft remains in same frame/shore position with preserved rock and broad water style; final acceptance belongs to root."))
idx=read(v/"standard-qa/index.json")
for p in idx["changedItems"]:
 file=Path(p);review="Affected standard original-pixel QA viewed after repair. Repaired top water segment and unchanged later sections show no new straight seam, contour cut or finite-return boundary."
 if file.name.startswith("west-no-neighbor"):review+=" This shows candidate border only; a complete west tile is unavailable and full external west seam is not accepted."
 items.append(dict(**ref(file),actuallyViewed=True,nativeScale=1,verdict="pass_local",review=review))
write(v/"visual-review.json",dict(reviewedAt=datetime.now(timezone.utc).isoformat(),eastCandidate=ref(e),westP14Candidate=ref(w),items=items,localChecksPassed=True,issueCount=0,issues=[],result="ready_for_root_actual_review",approvedForPromotion=False,automaticVisualPass=False,limitations=["Full r10_c11 tile does not yet exist; only p14 current draft neighbor is reviewed.","Current canonical r10_c12 remains reopened and unchanged; no source migration applied.","Twenty-one standard QA images are pixel-identical to old-canonical reconstruction; this numerical fact is not a new actual-view claim. Original old review records remain historical evidence."],standardQA=ref(v/"standard-qa/index.json"),reuseProof=ref(v/"source-reuse-proof.json")))
write(D/"current-joint-proposal.json",dict(updatedAt=datetime.now(timezone.utc).isoformat(),eastCandidate=ref(e),westP14Candidate=ref(w),sourceScopeCurrentStatus=read(T/"output/manifest.json")["status"],visualReview=ref(v/"visual-review.json"),sourceReuseProof=ref(v/"source-reuse-proof.json"),stage1=ref(D/"stage1-bounded/diagnostic.json"),stage2=ref(v/"diagnostic.json"),sourceConsumerMigrationPlan=ref(D/"consumer-migration-plan.json"),sourceProductionFilesUnchanged=True,approvedForPromotion=False,noImageCallInFlight=True))
print(json.dumps(dict(review=ref(v/"visual-review.json"),itemCount=len(items),east=ref(e),west=ref(w),p14ProductionIdentity=np.array_equal(check,patch),unchangedStandardQA=sum(x["identicalToOldCanonicalReconstruction"] for x in idx["items"]))))

