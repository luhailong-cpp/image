from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
items=[('r10_c02', 'pipeline/output/68ed540e96c6b98d/assembly.json', 'pipeline/output/68ed540e96c6b98d/left-worker-qa-resume20261016-v01/worker-review-and-repair-queue.json'), ('r15_c05', 'pipeline/output/28e1055ea7823560/assembly.json', 'pipeline/qa/resume-20261016-v01/review.json')]
catalog=read(B/"current-candidates.json")
for tile,aa,qq in items:
 ap=B/tile/aa;qa=B/tile/qq;a=read(ap);v=read(qa)
 assert a["tile"]==tile and a["verifiedNativeCount"]==16 and not a["formalAccepted"] and not v.get("formalAccepted",False)
 for k,size in [("output",(4096,4096)),("contextOutput",(4326,4326))]:
  e=a[k];assert sha(e["file"])==e["sha256"]
  with Image.open(e["file"]) as im:assert im.size==size
 catalog["tiles"][tile]={"tile":tile,"source":"native-full16-worker-reviewed-candidate","assembly":str(ap),"assemblySha256":sha(ap),"candidate":a["output"],"context":a["contextOutput"],"coreWorldBox":a["selectedCoreWorldBox"],"verifiedNativeSlots":16,"sourceResampling":False,"internalPassed":False,"externalPassed":False,"formalAccepted":False,"workerReview":str(qa),"workerReviewSha256":sha(qa),"adoptionScope":"Actual output/context hashes and dimensions checked; worker actual visual QA remains failed. No acceptance inferred."}
catalog["updatedAtUtc"]=now
(B/"current-candidates.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
tiles=[]
for r in range(9,17):
 for c in range(1,9):
  t=f"r{r:02d}_c{c:02d}";td=B/t;sp=td/"refinement/selection.json";sel=read(sp) if sp.exists() else {};n=0;missing=[]
  for pr in range(1,5):
   for pc in range(1,5):
    pid=f"p{pr:02d}_{pc:02d}";rp=td/sel.get(pid,f"native/{pid}.png.generation.json")
    if not rp.exists():missing.append(pid);continue
    d=read(rp);assert Path(d["file"]).is_file() and [d["width"],d["height"]]==[1254,1254] and d["nativePixelsPreserved"] and not d["resizedAfterGeneration"];n+=1
  tiles.append({"tile":t,"selectedNativeSlots":n,"missingPatchIds":missing,"candidateRegistered":t in catalog["tiles"],"formalAccepted":False})
n=sum(t["selectedNativeSlots"] for t in tiles);f=sum(t["selectedNativeSlots"]==16 for t in tiles)
counts={"selectedNativePatchCount":n,"fullyCovered4kCount":f,"complete4kCandidateCount":len(catalog["tiles"]),"nativeCoverageCompleteTileCount":f,"partialTileCount":sum(0<t["selectedNativeSlots"]<16 for t in tiles),"untouchedTileCount":sum(t["selectedNativeSlots"]==0 for t in tiles),"remainingCorePatchCount":1024-n,"missingFullTileCount":64-f,"remainingTilesWithout4kCandidates":64-len(catalog["tiles"]),"internalPassed4kCount":0,"externalPassed4kCount":0,"formalAcceptedCount":0}
snapshot=B/"pipeline-tools/current-slot-counts-20261016-v02.json";assert not snapshot.exists()
snapshot.write_text(json.dumps({"snapshotUtc":now,"scope":"Only current selected spatial slots; no historical receipts/versions/outputs rescan. Prior unchanged verification reused; two new actual full candidates hashed and dimension checked. Coverage is not acceptance.","counts":counts,"tiles":tiles},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
progress=read(B/"progress.json");progress.update(counts);progress.update(updatedAtUtc=now,status="native_production_in_progress",productionInProgress=True,generationStopped=False,networkBlocked=False,holdNewImageGeneration=False,activeTile="r14_c06",activeCoordinate="r14_c06:p03_02",countsSnapshotUtc=now,countsSnapshot=str(snapshot),countsSnapshotMayHaveAdvanced=True,productionLines=4)
progress["workerStatus"]={"reportedAtUtc":now,"productionLines":4,"activeGenerationWorkers":["root","sw_left_resume_20261016","sw_right_resume_20261016","sw_col5_resume_20261016"],"activeGenerationTiles":["r14_c06","r10_c02/r10_c03","r11_c08/r12_c08","r13_c01"],"source":"Original four lanes resumed; actual successful included builtin returns, no paid API."}
progress["zoneDeliverySummary"]={"targetDeduplicatedTiles":64,"full16Native4kCandidates":f,"internalCheckedPassed":0,"formalAccepted":0,"missingNativePatchCount":1024-n,"countsSnapshotUtc":now}
(B/"progress.json").write_text(json.dumps(progress,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"counts":counts,"newCandidatePaths":[catalog["tiles"][i[0]]["candidate"]["file"] for i in items],"snapshot":str(snapshot)},ensure_ascii=False))

