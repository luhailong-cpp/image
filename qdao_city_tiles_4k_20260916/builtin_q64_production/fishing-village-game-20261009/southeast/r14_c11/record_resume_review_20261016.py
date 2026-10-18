from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageChops
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast");T=Z/"r14_c11";Q=T/"qa"/"water-joint-20261016";old=T/"qa"/"complete-20261013-v1"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf8")
m=read(old/"manifest.json");sel=read(T/"selected-patches.json")
for s in m["sources"]:assert sha(s["file"])==s["sha256"] and str(Path(s["file"]).resolve())==str((T/sel["patches"][s["patch"]]).resolve())
assert sha(sel["candidate"])==sel["candidateSha256"]=="80cb7dbe66f343f5a810bee4a12b168bdf1e4413c341d424f121b7afb0401df6"
for e in m["evidence"]:assert sha(e["file"])==e["sha256"]
raws=[]
for ver in ["v1","v2"]:
 a=np.load(Q/f"joint-{ver}-proof.npz");replay=a["original"].copy();replay[a["mask"]]=a["raw"][a["mask"]];assert np.array_equal(replay,a["result"]);assert np.array_equal(replay[~a["mask"]],a["original"][~a["mask"]])
 ins=read(Q/f"joint-{ver}-adoption-instructions.json")
 for s in ins["patches"]:assert sha(s["original"])==s["originalSha256"] and sha(s["file"])==s["sha256"]
 raws.append(dict(version=ver,raw=str(Q/f"joint-{ver}-raw.png"),rawSha256=sha(Q/f"joint-{ver}-raw.png"),proof=str(Q/f"joint-{ver}-proof.npz"),exactRawReplay=True,visualCropsViewed=[str(Q/f"{ver}-{side}.png") for side in ["seam","north","south","west","east"]]))
# North edge review reused from the identical r13 south evidence; validate pixel provenance source hashes.
north_m=read(Z/"r13_c11"/"qa"/"external-20261016-v1"/"manifest.json")
north=[]
for e in north_m["edges"]:
 if e["edge"]!="south":continue
 for part in e["segments"]:
  north.append(part)
# Verify referenced sources directly from generated south QA sidecars.
for i in range(1,5):
 q=read(Z/"r13_c11"/"qa"/"external-20261016-v1"/f"south-segment-{i}.qa.json")
 for s in q.get("sources",[]):assert sha(s["file"])==s["sha256"]
report=dict(tile="r14_c11",updatedAt=datetime.now(timezone.utc).isoformat(),nativeCoreCount=16,candidate=sel["candidate"],candidateSha256=sel["candidateSha256"],unchangedNativeSources=16,unchangedInternalEvidence=33,priorReviewReused=str(old/"visual-review.json"),priorReplayReused=str(old/"independent-replay-proof.json"),newNorthReview=dict(basis="r13_c11 south edge identical physical seam, 4 segments and3 crosses viewed natively in this agent",evidenceDirectory=str(Z/"r13_c11"/"qa"/"external-20261016-v1"),status="material_pending"),waterRepairAttempts=raws,bestSelectedVersion="unchanged original",repairDecision="Both local trials leave conspicuous new perimeter/caustic scale boundaries and do not improve acceptance. Preserve both attempts and canonical native sources. Defer this point after two attempts.",internalReady=False,formalAccepted=False,materialPending=True,actualModel=None)
write(Q/"final-review-20261016-v1.json",report)
s=T/"selected-patches.json";backup=T/"selected-before-review-20261016-v1.json";assert not backup.exists();backup.write_bytes(s.read_bytes())
sel["updatedAt"]=datetime.now(timezone.utc).isoformat();sel["latestRepairReview"]=str(Q/"final-review-20261016-v1.json")
sel["internalReady"]=False;sel["formalAccepted"]=False;sel["materialPending"]=True
sel["pendingIssues"]=[i for i in sel["pendingIssues"] if i["id"]!="external-north-east"]+[{"id":"external-north-material","status":"pending","description":"North r13_c11 now has16selected cores; four seams plus3crosses viewed and source-hash checked. Stone/foam continuity near east end is usable; water scale/tone remains pending."},{"id":"external-east","status":"pending_missing_sources","description":"Zone-local reader lacks east neighboring selected core set. South is canvas boundary."},{"id":"p31-p41-two-attempts","status":"pending_deferred_after_two","description":"Two 1254 native AI joint repairs did not remove density transition without new perimeter artifact; canonical original remains best selected."}]
write(s,sel)
# Assigned batch handoff, not zone totals.
r13=read(Z/"r13_c11"/"selected-patches.json")
handoff=dict(createdAt=datetime.now(timezone.utc).isoformat(),agent="/root/east_water_finish_20261016",assignedTiles=["r13_c11","r14_c11"],completedNativeCores=32,newlyGeneratedMissingCores=5,recoveredAlreadyReturnedCores=2,newAIRepairImages=4,actualModel=None,route="builtin image_gen__imagegen",resamplingAppliedToArt=False,canonicalRepairsAdopted=False,tiles=[dict(tile="r13_c11",candidate=r13["candidate"],candidateSha256=r13["candidateSha256"],coreCount=16,internalReady=False,formalAccepted=False,review=r13["internalReview"],bestRepairReview=str(Z/"r13_c11"/"qa"/"rockfoot-joint-20261016"/"final-review-20261016-v1.json")),dict(tile="r14_c11",candidate=sel["candidate"],candidateSha256=sel["candidateSha256"],coreCount=16,internalReady=False,formalAccepted=False,review=str(Q/"final-review-20261016-v1.json"))],nextStep="Assigned missing cores are complete. Pending geometry/material and external issues documented; two retries at each selected repair point reached stop rule. Parent may assign independent missing coordinate; this agent claims no new coordinates.")
write(Z/"east-water-batch-20261016-v1.json",handoff)
print(json.dumps(handoff))

