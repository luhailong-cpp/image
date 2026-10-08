from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
# Correct only freshly prepared own sidecar newline typo; no source images touched.
for p in D.glob("qa-current-fullwidth-*.png.generation.json"):
 txt=p.read_text()
 if txt.endswith("\\n"):p.write_text(txt[:-2]+"\n",encoding="utf-8")
 json.loads(p.read_text())
call=D/"stage2-preview/draft.call.json";data=read(call);data.pop("NOT_SUBMITTED",None);data.pop("rebuildRequired",None);write(call,data)
now=datetime.now(timezone.utc).isoformat();manifest=T/"output/manifest.json";old=read(manifest);source=Path(old["file"]);assert sha(source)=="3ca7d1d8b5711e0b8d315fe9f3c0a4fe5f032ba3dc2555edfa9854eca6dc2be2"
items=[]
for name,verdict,review in [
("qa-source-northwest-native.png","fail","Actual r09_c12/r10_c12 pixels alone show an obvious straight material/color boundary through broad water cells at the north join. No pending p14 pixels present."),
("qa-source-next-native.png","partial_pass","Only beginning of x1024..2048 retains the western source defect; later water and wall join do not exhibit the same ruler-straight color band."),
("four-quadrant-context1254.png","fail","True old northern quadrant/source contact has the straight band. Unapproved p14 draft reproduces its compatible continuation on left; this does not excuse source failure."),
("qa-current-fullwidth-1.png","fail","x0..1024 native north seam shows continuous straight color/shape cutoff."),
("qa-current-fullwidth-2.png","partial_pass","x1024..2048: remaining line near western beginning, visually fading/ending around x1100; x1152..1408 inspected separately. No same straight defect through wall at east."),
("qa-current-fullwidth-3.png","pass_local","x2048..3072 native roof/wall segments show connected contours/material with no same straight seam."),
("qa-current-fullwidth-4.png","pass_local","x3072..4096 native roof planes remain continuous, no same straight seam."),
("qa-current-fullwidth-5.png","fail_left_only","x960..1600 close view: straight boundary clear at left; ends as the curved bright reflection/wave region takes over, approximately x1100..1152."),
("qa-current-fullwidth-6.png","pass_local","x1152..1408 narrow original view: no continuous straight cutoff across this strip; bright reflection and blue cells coherent."),
("stage2-preview/context.png","planning_only","Native follow-on context covers E x384..1638 with 627 true northern rows; must rebuild lower-side overlap from stage1 proposal before submission."),
("stage2-preview/edit-target.png","planning_only","Hole E x512..1352, y0..216; original north627 rows and right stone wall protected. No AI call made.")]:
 items.append(dict(**ref(D/name),actuallyViewed=True,nativeScale=1,verdict=verdict,review=review))
finding=dict(createdAt=now,tile="r10_c12",candidate=ref(source),north=ref(old["northSource"]),items=items,scopedPass=False,issueCount=1,issues=[dict(id="current-northwest-source-boundary",physicalGlobalY=36864,clearAffectedLocalX=[0,1100],conservativeReviewAndRepairLocalX=[0,1352],currentFailure="Straight color/material transition and locally interrupted wave continuity at actual N join.",rightEndAssessment="Approximately1100..1152 by raw 1:1 close views, not a claim of exact pixel defect segmentation. Stage2 conservatively includes current E to1352 and return to1384; wall and roof farther east excluded.",sourceBoundarySamples=ref(D/"source-boundary-numerical.json"))],priorQAWasActuallyPerformed=True,priorQAOutcomeSupersededOnlyForCurrentNorthwestFinding=True,formalAccepted=False)
write(D/"source-review.json",finding)
liveNames={"plan.json","manifest.json","progress.json","frozen-neighbors.json","neighbor-revalidation.json","delivery-index.json","continuation-20261008.json","current-preview.png.generation.json"}
hits=[]
target="r10_c12/output/r10_c12.png";sourceSHA=sha(source)
def walk(v,path=""):
 if isinstance(v,dict):
  for k,x in v.items():yield from walk(x,path+"."+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from walk(x,path+"["+str(i)+"]")
 elif isinstance(v,str) and (target in v.replace("\\","/") or v==sourceSHA):yield path
for p in R.rglob("*.json"):
 rel=p.relative_to(R);parts=set(rel.parts)
 if p.name not in liveNames or any(x in parts for x in ["repairs","evidence","native","history","pilot-transparent"]):continue
 if any("history" in x or "before-" in x for x in rel.parts):continue
 try:fields=list(walk(read(p)))
 except Exception:continue
 if fields:hits.append(dict(record=ref(p),fields=fields))
write(D/"consumer-migration-plan.json",dict(createdAt=now,sourceCurrent=ref(source),prospectiveChangedRegion=dict(tile="r10_c12",localLTRB=[0,0,1384,320],proposalOnly=True),observedLiveRecordHits=hits,consumers=[
dict(id="r10_c11",effect="True E first115 top region changes; current p14 proposal known E/NE seam must be re-extracted from new jointly repaired E.",currentRecords=[str(R/"r10_c11/plan.json"),str(R/"r10_c11/references/east-native115.png.generation.json")],needed="After root approval: TEXT snapshot frozen plan, explicit source-version migration record; regenerate actually used E context and new request/current-generation provenance without rewriting previous imagegen request. Keep approved old p14 combined as derivation input only. No downstream native exists yet; block consumption until new N/E/NE boundary QA.",frozenPlanUnchangedNow=True),
dict(id="r10_c13",effect="Whole W source file SHA changes, but actual consumed eastmost115/320 of r10_c12 must stay byte-identical because repair confined x<1384.",currentRecords=[str(R/"r10_c13/plan.json"),str(R/"r10_c13/output/manifest.json"),str(R/"r10_c13/frozen-neighbors.json"),str(R/"r10_c13/neighbor-revalidation.json")],needed="Prove raw right320 and right115 exact pixels unchanged. Append current neighbor revalidation/new whole-source SHA and update live manifest metadata with prior source ref/reuse proof. Original frozen-at records, native requests and immutable native-assembly keep historical SHA. Existing c13 QA pixel reviews can reuse exact PNG hashes; don't claim newly viewed. Do not regenerate c13 image or propagate to r11_c13 if consumed strips unchanged."),
dict(id="r10_c12-own",effect="Final source SHA and north QA change.",needed="Current image generation/manifest/progress/final-local-review and source repair link updated only after root approval. Preserve immutable original assembly/old AI requests. Rebuild full4096 north seam+return256+first internal crossings+NW corner+all local return QA; exact-hash reuse internal/E/S portions when unchanged."),
dict(id="root-overview",effect="Delivery source SHA, scoped count, previews become stale on source mutation/reopening.",currentRecords=[str(R/"delivery-index.json"),str(R/"progress.json"),str(R/"current-preview.png.generation.json"),str(T/"current-preview.png.generation.json")],needed="Root refreshes status counts now; after pixel promotion regenerate affected overview previews and accurate source hash metadata."),
dict(id="r11_c13",effect="Agent4 confirms only r10_c13 directly consumed; no direct r10_c12 reference.",needed="No migration when c13 PNG unchanged.")
],preserveHistorical=["native/*.request.json","all old AI prompt/call/generation receipts","output/native-assembly.json and other original assembly reports","frozen sourceAtFreeze fields"],automaticPropagationForbidden=True,productionImagesUnchanged=True))
# Parent specifically authorized only this current manifest scope withdrawal, not PNG/plan/p14 changes.
snapshot=D/"manifest-before-source-reopen.json";assert not snapshot.exists();shutil.copyfile(manifest,snapshot)
assert sha(snapshot)==sha(manifest)
old["scopedLocalSeamsPassed"]=False;old["status"]="reopened_for_northwest_source_tone_repair";old["updatedAt"]=now
old["northScopedQA"].update(result="reopened_for_northwest_source_tone_repair",priorActualReviewPreservedIn=ref(snapshot),sourceReinspection=ref(D/"source-review.json"),reopenedAt=now)
old["sourceScopeReopened"]=dict(finding=ref(D/"source-review.json"),priorManifest=ref(snapshot),scope="northwest portion of northern shared seam only; existing internal scoped reviews not withdrawn",priorQAActuallyViewedRecordsRetained=True,sourcePNGUnchanged=True,parentAuthorization="Root message: source defect proven permits scopedLocalSeamsPassed false/status reopened_for_northwest_source_tone_repair; text snapshot required; no PNG/plan/p14/immutable assembly modification.")
write(manifest,old)
write(D/"scope-reopen-result.json",dict(updatedManifest=ref(manifest),snapshot=ref(snapshot),finding=ref(D/"source-review.json"),sourcePNGUnchanged=ref(source),r10c11FrozenPlan=ref(R/"r10_c11/plan.json"),r10c11ProductionP14=ref(R/"r10_c11/native/p14.png"),noImageGenerationInThisScript=True,rootMustRefreshProgressAndDeliveryCounts=True,tileProgressStillPriorHistoricalStatusPendingRootRefresh=True))
print(json.dumps(dict(manifest=ref(manifest),finding=ref(D/"source-review.json"),consumers=ref(D/"consumer-migration-plan.json"))))

