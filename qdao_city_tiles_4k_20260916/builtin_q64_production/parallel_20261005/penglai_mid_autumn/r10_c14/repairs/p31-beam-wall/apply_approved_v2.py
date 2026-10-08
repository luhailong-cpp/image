from pathlib import Path
import json,hashlib,sys,copy,shutil
from datetime import datetime,timezone
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];ROOT=T.parent
sys.path.insert(0,str(ROOT/"tools"));import finalize_scoped as f
OLD="0bbb59af2bb936e4d27945ea77240a56f0d34d4f887a24e4664c4ceb7d6a9e8c"
NEW="963d29bf2b73c9ff400d29689a43023135b7653e0cd0159b80f7fc0d6b6f70f3"
H=D/"history-before-v2-application";assert not H.exists(),"Already applied or history collision"
ctx=f.context("r10_c14",OLD);C=ctx["candidate"];proposal=D/"v2-proposal-candidate.png";assert f.sha(proposal)==NEW
old_required=f.requirements(ctx)
newctx=dict(ctx,image=f.open_image(proposal),finalsha=NEW,references={**ctx["references"],"current":{"file":str(C),"sha256":NEW}})
required=f.requirements(newctx)
reports={n:f.read(T/"qa"/n) for n in ["horizontal-review.json","external-review.json","root-review.json"]}
recipes={
"west-beam-attachment-native.png":{"canvasPixels":[1254,1200],"pieces":[{"source":"west","cropLTRB":[3776,2896,4096,4096],"pasteXY":[0,0]},{"source":"current","cropLTRB":[0,2896,934,4096],"pasteXY":[320,0]}]},
"northwest-four-tile-corner.png":{"canvasPixels":[640,640],"pieces":[{"source":"northwest","cropLTRB":[3776,3776,4096,4096],"pasteXY":[0,0]},{"source":"north","cropLTRB":[0,3776,320,4096],"pasteXY":[320,0]},{"source":"west","cropLTRB":[3776,0,4096,320],"pasteXY":[0,320]},{"source":"current","cropLTRB":[0,0,320,320],"pasteXY":[320,320]}]}}
expected={k:v for k,v in required.items()}
for report in reports.values():
 for field in ["items","mainQA","supplementalQA"]:
  for item in report.get(field,[]):
   path=Path(item["file"]);k=f.key(path)
   assert f.sha(path)==item["sha256"],"Report image changed before apply"
   if k not in expected:
    if path.name in recipes:item["reproduction"]=recipes[path.name]
    expected[k]=dict(path=path,image=f.extra_image(newctx,path,item),operation=item.get("reproduction",item.get("operation",{})),roles=list(newctx["references"]))
checks=[]
for k,e in expected.items():
 path=e["path"];actual=f.open_image(path);same=actual.size==e["image"].size and actual.tobytes()==e["image"].convert("RGB").tobytes()
 checks.append(dict(file=str(path),oldPngSha256=f.sha(path),pixelsUnchanged=same,oldPixelSha256=hashlib.sha256(actual.tobytes()).hexdigest(),newPixelSha256=hashlib.sha256(e["image"].convert("RGB").tobytes()).hexdigest()))
bykey={f.key(r["file"]):r for r in checks}
assert [Path(r["file"]).name for r in checks if not r["pixelsUnchanged"] and f.key(r["file"]) in required]==["internal-x1024-full.png"]
for path in [T/"output/manifest.json",T/"progress.json",T/"qa/final-local-review.json"]:
 if path.exists():assert f.read(path).get("scopedLocalSeamsPassed") is not True
# Freeze original text before any mutation, including all current QA source records.
snap_paths=[ctx["generation"],T/"plan.json",T/"output/manifest.json",T/"progress.json",T/"qa/final-local-review.json"]
snap_paths += list((T/"qa").rglob("*.json"))
snap=[]
for path in snap_paths:
 if not path.exists():continue
 dest=H/path.relative_to(T);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest);snap.append(dict(originalFile=str(path),snapshot=f.ref(dest)))
f.write(H/"history-index.json",dict(createdAt=f.now(),replacedImage=dict(file=str(C),sha256=OLD,status="Canonical image replaced after root approval; original full-image PNG not duplicated here. Text provenance is retained; source native patches and repair before-frame remain."),snapshots=snap,immutableAssembly=f.ref(ctx["assemblyPath"])))
auth=dict(recordedAt=f.now(),reviewer="/root",authorizationSource="Parent collaboration NEW_TASK authorizes application of exact proposal SHA",proposal=f.ref(proposal),actuallyViewed=True,nativeScale=1,viewTool="view_image detail original",viewedFiles=[f.ref(D/n) for n in ["v2-qa-detail.png","v2-qa-wall-post-joint.png","v2-qa-repair-surround.png","v2-proposal-frame.png"]],verdict="local_repair_pass",review="Root actually viewed all four native images: beam-wall defect repaired; main post, left/right rails, dock planks and stone joint continuous.",approvedForApplication=True,finalApproval=False)
f.write(D/"root-v2-application-authorization.json",auth)
# Immutable source assembly and native AI source records remain untouched.
shutil.copyfile(proposal,C);assert f.sha(C)==NEW
oldgen=f.read(ctx["generation"])
newgen=dict(file=str(C),sha256=NEW,createdAt=f.now(),width=4096,height=4096,format="PNG",derivedFrom=[dict(file=str(C),sha256=OLD,replacedAtCanonicalPath=True,generationHistory=f.ref(H/"output/r10_c14-candidate.png.generation.json")),f.ref(D/"host-result.png")],operation=dict(kind="Root-approved local AI wall repair composited at native scale",proposal=f.ref(proposal),mapping=f.ref(D/"mapping.json"),alpha=f.ref(D/"v2-composite-alpha.png"),checks=f.ref(D/"v2-proposal-checks.json"),rootAuthorization=f.ref(D/"root-v2-application-authorization.json")),sourceAssembly=f.ref(ctx["assemblyPath"]),originalAssemblyCandidateSha256=OLD,submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None,modelEvidence="Mechanical derivative of original 16 native AI images and saved local builtin AI repair. Each source's original actual model/quality null and exact request record remain unchanged.",productionPixels=True,formalAccepted=False,navigationVerified=False,clientVerified=False)
f.write(ctx["generation"],newgen)
def rebind(obj):
 if isinstance(obj,dict):return {k:rebind(v) for k,v in obj.items()}
 if isinstance(obj,list):return [rebind(v) for v in obj]
 return NEW if obj==OLD else obj
# Rewrite only changed current QA PNGs. Bind every unchanged derivative to the
# new candidate using an explicit exact-pixel proof and retained prior text.
for k,e in expected.items():
 path=e["path"];rec=bykey[k];gp=Path(str(path)+".generation.json");g=f.read(gp) if gp.exists() else {}
 if not rec["pixelsUnchanged"]:e["image"].convert("RGB").save(path)
 g=rebind(g);g.update(file=str(path),sha256=f.sha(path),currentCandidate={"file":str(C),"sha256":NEW},reboundAt=f.now(),sourceCandidateTransition=dict(previousSha256=OLD,currentSha256=NEW,pixelsUnchanged=rec["pixelsUnchanged"],priorGenerationHistory=str(H/gp.relative_to(T)) if gp.exists() else None))
 if not rec["pixelsUnchanged"]:g.update(actuallyViewed=False,verdict="pending_visual_QA")
 f.write(gp,g);rec["currentPngSha256"]=f.sha(path)
f.write(D/"application-v2-qa-proof.json",dict(createdAt=f.now(),oldCandidate={"file":str(C),"sha256":OLD},currentCandidate=f.ref(C),items=checks,changedPNGCount=sum(not r["pixelsUnchanged"] for r in checks),standardRequiredCount=len(required),standardChanged=["internal-x1024-full.png"],visualApprovalAutomatic=False))
proof=f.ref(D/"application-v2-qa-proof.json")
for name,report in reports.items():
 prior_path=H/"qa"/name;prior=f.ref(prior_path)
 report.update(candidate=f.ref(C),reboundAt=f.now(),previousReview=prior,sourceCandidateSha256=OLD,reuseEvidence=proof)
 for field in ["items","mainQA","supplementalQA"]:
  for item in report.get(field,[]):
   rec=bykey[f.key(item["file"])]
   if rec["pixelsUnchanged"]:
    item["reuse"]=dict(originalCandidateSha256=OLD,originalReview=prior,originalQAFileSHA256=item["sha256"],currentQAFileSHA256=rec["currentPngSha256"],pixelsUnchanged=True,reViewed=False,reason="Exact regenerated image bytes equal current stored QA pixels, and stored PNG SHA unchanged. Reuses original actual native-scale inspection, not a new viewing.",proof=proof)
   else:
    item["priorReview"]=dict(candidateSha256=OLD,report=prior,sha256=item["sha256"],actuallyViewed=item.get("actuallyViewed"),verdict=item.get("verdict"))
    item.update(sha256=rec["currentPngSha256"],actuallyViewed=False,verdict="pending_visual_QA",review="Current pixels changed after approved local repair; must actually re-view current image.")
 if name=="horizontal-review.json":
  report["resolvedKnownOutsideScopeIssue"]=report.pop("knownOutsideScopeIssue",None)
  report["resolvedKnownOutsideScopeIssue"]["resolution"]=f.ref(D/"root-v2-application-authorization.json")
 elif name=="root-review.json":
  report.update(scopedPass=False,issueCount=1,issues=["Inherited r09_c14 southwest truncated grout remains unresolved; current x1024 and detail reinspection pending after local repair."],localBeamWallRepairApproved=f.ref(D/"root-v2-application-authorization.json"))
 else:
  report.update(externalScopedPass=False,beamAttachmentScopedPassed=False,beamAttachmentCurrentPixelsPending=True)
 f.write(T/"qa"/name,report)
# The external detail index is derivation metadata, not an inspection report.
idx=T/"qa/external-details/index.json"
if idx.exists():
 data=rebind(f.read(idx))
 def update_items(o):
  if isinstance(o,dict):
   if isinstance(o.get("file"),str) and f.key(o["file"]) in bykey:
    r=bykey[f.key(o["file"])];o["sha256"]=r["currentPngSha256"]
   for v in o.values():update_items(v)
  elif isinstance(o,list):
   for v in o:update_items(v)
 update_items(data);data.update(reboundAt=f.now(),transitionProof=proof);f.write(idx,data)
manifest=copy.deepcopy(ctx["assembly"])
manifest.update(file=str(C),sha256=NEW,status="native_4K_candidate_local_repair_applied_pending_visual_QA",scopedLocalSeamsPassed=False,sourceManifest=f.ref(ctx["assemblyPath"]),assemblyCandidateSha256=OLD,currentCandidateGeneration=f.ref(ctx["generation"]),localRepairApplication=f.ref(D/"root-v2-application-authorization.json"),currentNeighbors={k:v for k,v in ctx["references"].items() if k!="current"},qa=[dict(file=str(e["path"]),sha256=f.sha(e["path"]),actuallyViewed=False,verdict="consult_current_review_reports") for e in required.values()],formalAccepted=False,clientVerified=False,navigationVerified=False,externalSeamsVerified={"north":False,"west":False,"east":False,"south":False},pendingReasons=["Reinspect changed x1024 full seam and beam attachment detail","Repair inherited north-corner source defect and repeat impacted neighbor/corner QA"],history=f.ref(H/"history-index.json"))
f.write(T/"output/manifest.json",manifest)
assert f.sha(ctx["assemblyPath"])==ctx["immutableMetadata"][1]["sha256"]
newctx=f.context("r10_c14",NEW);current=f.requirements(newctx)
for k,e in current.items():
 im=f.open_image(e["path"]);assert im.size==e["image"].size and im.tobytes()==e["image"].convert("RGB").tobytes()
f.write(D/"application-v2.json",dict(appliedAt=f.now(),candidate=f.ref(C),oldCandidateSha256=OLD,sourceProposal=f.ref(proposal),sourceAssemblyUnchanged=f.ref(ctx["assemblyPath"]),qaProof=proof,textHistory=f.ref(H/"history-index.json"),horizontalReusedCount=15,productionCandidateChanged=True,scopedAcceptanceWritten=False,formalAccepted=False,changedQA=[r["file"] for r in checks if not r["pixelsUnchanged"]]))
print(json.dumps(f.read(D/"application-v2.json")))

