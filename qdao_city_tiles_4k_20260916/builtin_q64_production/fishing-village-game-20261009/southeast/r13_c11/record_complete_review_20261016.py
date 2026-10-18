from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageChops
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast");T=Z/"r13_c11";Q=T/"qa"/"complete-20261016-v1";J=T/"qa"/"rockfoot-joint-20261016"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2),encoding="utf8")
m=read(Q/"manifest.json");proof=read(Q/"independent-replay-proof.json")
assert sha(proof["candidate"])==proof["candidateSha256"]
for s in m["sources"]:assert sha(s["file"])==s["sha256"]
issues=[{"id":"rockfoot-flat-cut","location":"p22 south left section, global y51200 x41984..42300","status":"pending","detail":"Canonical rock toe is clipped flat. Joint-v1 corrects geometry and foam but its replacement perimeter material is not yet accepted; joint-v2 perimeter cleanup did not improve."},{"id":"foam-cut-p32-west","location":"p31/p32 seam x41984, upper third y51200..51700","status":"pending","detail":"Two foam trails end at vertical core seam. Same best joint-v1 reconnects them, pending local perimeter polish."},{"id":"internal-water-material","location":"p13/p14, p23/p33, p31/p41, p32/p33, p32/p42, p42/p43; related water crossings","status":"pending","detail":"Native water caustic density/loop scale/luminance differs across some core edges."},{"id":"external-west-rock-water","location":"x40960 y49152..51200, west segments 1-2 and y50176 cross","status":"pending","detail":"Submerged stone shapes and highlights truncate or change abruptly across tile boundary."},{"id":"external-west-south-material","location":"other west/south available native segments and 6 crosses","status":"pending","detail":"Water material scale and tone remain uneven; south segment4 stone/foam structure continuous but material not universally accepted."},{"id":"external-north-east","status":"pending_missing_sources","detail":"Zone-local source reader has no complete neighboring core sets at north/east."}]
obs=[]
for e in m["evidence"]:
 name=Path(e["file"]).stem
 assert sha(e["file"])==e["sha256"]
 geometry=name not in ("p22--p32","p31--p32","cross-r2-c1")
 obs.append(dict(id=name,file=e["file"],sha256=e["sha256"],nativeVisuallyInspected=True,geometryReady=geometry,materialReady=False if (not geometry or any(s["patch"] in ["p13","p14","p23","p24","p31","p32","p33","p34","p41","p42","p43","p44"] for s in e["sources"])) else True))
report=dict(tile="r13_c11",createdAt=datetime.now(timezone.utc).isoformat(),candidate=proof["candidate"],candidateSha256=proof["candidateSha256"],nativeCoreCount=16,rawReplayPixelDifference=0,proof=str(Q/"independent-replay-proof.json"),internalEvidenceCount=33,observations=obs,externalReview=dict(manifest=str(T/"qa"/"external-20261016-v1"/"manifest.json"),nativeSegmentsViewed=8,nativeCrossesViewed=6,availableEdges=["west","south"]),pendingIssues=issues,internalReady=False,formalAccepted=False,materialPending=True,actualModel=None)
write(Q/"visual-review.json",report)
s=T/"selected-patches.json";before=sha(s);b=T/"selected-before-complete-review-20261016-v1.json";assert not b.exists();b.write_bytes(s.read_bytes());d=read(s)
d.update(status="complete_native_candidate_internal_geometry_material_pending",candidate=proof["candidate"],candidateSha256=proof["candidateSha256"],nativeCoreCount=16,internalReady=False,formalAccepted=False,materialPending=True,internalReview=str(Q/"visual-review.json"),pendingIssues=issues,updatedAt=datetime.now(timezone.utc).isoformat());write(s,d)
write(Q/"selection-metadata-transition.json",dict(beforeSha256=before,afterSha256=sha(s),patchMapChanged=False))
for ver in ["v1","v2"]:
 a=read(J/f"joint-{ver}-adoption-instructions.json")
 for p in a["patches"]:assert sha(p["original"])==p["originalSha256"] and sha(p["file"])==p["sha256"]
a=np.load(J/"joint-v1-proof.npz");replay=a["original"].copy();replay[a["mask"]]=a["raw"][a["mask"]];assert np.array_equal(replay,a["result"])
a2=np.load(J/"joint-v2-proof.npz");replay2=a2["original"].copy();replay2[a2["maskV1"]]=a2["rawV1"][a2["maskV1"]];replay2[a2["maskV2"]]=a2["rawV2"][a2["maskV2"]];assert np.array_equal(replay2,a2["result"])
write(J/"final-review-20261016-v1.json",dict(bestCandidate="v1",canonicalChanged=False,geometry="rockfoot and foam defects corrected locally",material="pending top stone grain line and mask left/bottom caustic boundaries",v2="perimeter cleanup did not improve; retain v1",attempts=2,doNotRetryThisPointImmediately=True,provenanceReplay="PASS",v1Proof=str(J/"joint-v1-proof.npz"),v2Proof=str(J/"joint-v2-proof.npz"),currentCanonicalSelectionSha256=sha(s),sourceHashStabilityVerified=True,formalAccepted=False))
# independent r14 water seam native input, no alteration to source selection
sys.path.insert(0,str(Z));from review_external_seams import Sources
U=Z/"r14_c11"/"qa"/"water-joint-20261016";U.mkdir(exist_ok=False)
box=[40845,55693,42099,56947];ss=Sources();im,parts,missing=ss.extract(box);assert im is not None and not missing and im.size==(1254,1254)
p=U/"input-native.png";im.save(p);write(U/"input-native.derivation.json",dict(file=str(p),sha256=sha(p),globalBox=box,sources=parts,classification="AI input and QA only",resamplingApplied=False))
print(json.dumps(dict(r13Review=str(Q/"visual-review.json"),r13Candidate=proof["candidate"],r14Input=str(p))))

