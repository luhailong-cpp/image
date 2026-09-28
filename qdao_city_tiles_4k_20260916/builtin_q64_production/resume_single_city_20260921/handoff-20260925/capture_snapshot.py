from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, io, json, subprocess, tomllib
from PIL import Image

REPO=Path("E:/work/image")
ART=REPO/"qdao_city_tiles_4k_20260916"
SESSION=ART/"builtin_q64_production/resume_single_city_20260921"
OUT=SESSION/"handoff-20260925"
AUTO=Path("C:/Users/luyua/.codex/automations/automation-3/automation.toml")
sha=lambda data: hashlib.sha256(data).hexdigest()
now=lambda: datetime.now(timezone.utc).isoformat()
def mapped(p):
    s=str(p).replace("\\","/")
    old="D:/luyuan/wuxingqitan/image"
    if s.lower().startswith(old.lower()+"/"): return REPO/s[len(old)+1:]
    return Path(s)
tracked={}
def record(p):
    p=Path(p); key=str(p)
    if key in tracked: return tracked[key]
    if not p.is_file(): return {"file":key,"exists":False}
    data=p.read_bytes()
    item={"file":key,"exists":True,"bytes":len(data),"sha256":sha(data),"modifiedAtUtc":datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat()}
    if p.suffix.lower() in (".json",".md",".csv",".txt",".toml",".py"):
        item["lfNormalizedSha256ForHistoricalComparisonOnly"]=sha(data.replace(b"\r\n",b"\n"))
    tracked[key]=item
    return item
def readjson(p):
    record(p)
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def png(p,expected,size):
    p=mapped(p); info=record(p)
    assert info["exists"],str(p)
    assert info["sha256"]==expected,(str(p),"SHA mismatch")
    with Image.open(p) as im:
        im.load()
        assert im.format=="PNG" and im.size==size,(str(p),im.format,im.size)
        pixels=list(im.size); mode=im.mode
    return {"file":str(p),"sha256":info["sha256"],"pixels":pixels,"mode":mode,"fullyDecoded":True,"shaMatchesExpected":True}
def git(*args):
    return subprocess.run(["git",*args],cwd=REPO,text=True,encoding="utf-8",capture_output=True,check=True).stdout.strip()
def writejson(name,obj):
    p=OUT/name
    assert not p.exists(),str(p)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

captured=now()
session=readjson(SESSION/"session-state.json")
ledger=readjson(SESSION/"current-coverage-ledger.json")
assert len(ledger["tiles"])==256 and len(ledger["seams"])==480 and len(ledger["junctions"])==225
roots={}
for p in (ART/"status.json",ART/"production_catalog.json",ART/"builtin_q64_production/current-batch.json"):
    data=readjson(p)
    roots[str(p)]={"activeProductionRun":data.get("activeProductionRun"),"source":record(p)}
csvpath=SESSION/"handoff-20260921/candidate-coordinates.csv"
record(csvpath)
rows=list(csv.DictReader(io.StringIO(csvpath.read_text(encoding="utf-8-sig"))))
candidates=[]
localrows=[]
for row in rows:
    checked=png(row["file"],row["sha256"],(4096,4096))
    checked.update({"tile":row["tile"],"historicalFile":row["file"],"role":"candidate_not_production_tile","formalAccepted":False,
        "pixelRectXYWH":[int(row[k]) for k in ("pixelX","pixelY","pixelWidth","pixelHeight")],
        "worldRectXZW H".replace(" ",""):[float(row[k]) for k in ("worldX","worldZ","worldWidth","worldHeight")]})
    candidates.append(checked)
    local=dict(row);local["historicalFile"]=row["file"];local["file"]=checked["file"]
    localrows.append(local)
assert len(candidates)==8
with (OUT/"candidate-coordinates-local.csv").open("x",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(localrows[0]));w.writeheader();w.writerows(localrows)

native=[]; patchstates={}
for tile in ("r08_c07","r08_c08","r08_c09"):
    td=SESSION/("next_tile_"+tile)
    h=readjson(td/"handoff-state.json")
    record(td/"HANDOFF.md"); record(td/"plan.json")
    patchstates[tile]={"selectedCount":h["selectedPatchCount"],"missing":h["missingOrNeedsRegeneration"],"suggestedNextOrder":h["suggestedNextOrder"]}
    for p in h["selectedPatches"]:
        checked=png(p["file"],p["sha256"],(1254,1254))
        checked.update({"tile":tile,"patch":p["id"],"versionStem":p.get("versionStem"),"historicalFile":p["file"],"role":"selected_native_detail_not_production_tile","formalAccepted":False})
        rp=p.get("record")
        if isinstance(rp,dict): rp=rp.get("file") or rp.get("path")
        if rp:
            checked["record"]=record(mapped(rp))
            checked["historicalRecord"]=rp
            checked["historicalRecordExpectedSha256"]=p.get("recordSha256")
            checked["recordRawShaMatchesHistorical"]=checked["record"].get("sha256")==p.get("recordSha256")
        native.append(checked)
assert len(native)==16
nrows=[]
for n in native:
    nrows.append({"tile":n["tile"],"patch":n["patch"],"versionStem":n.get("versionStem"),"file":n["file"],"sha256":n["sha256"],"width":1254,"height":1254,"historicalFile":n["historicalFile"],"record":n.get("record",{}).get("file"),"recordSha256":n.get("record",{}).get("sha256"),"recordRawShaMatchesHistorical":n.get("recordRawShaMatchesHistorical"),"formalAccepted":False})
with (OUT/"selected-native-patches-local.csv").open("x",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(nrows[0]));w.writeheader();w.writerows(nrows)

required=[
REPO/"AGENTS.md",REPO/"主城地图切图规范.md",ART/"README.md",
REPO/"docs/IMAGE_MODEL_POLICY.md",REPO/"config/image-generation.json",
REPO/"README.md",REPO/"designs/README.md",REPO/"docs/QDAO_ART_DIRECTION.md",
REPO/"docs/WUXING_QITAN_HANDOFF.md",REPO/"qdao_ui_redesign_v5/UI_SPEC.md",
ART/"主城美术详细交接-20260921.md",SESSION/"handoff-20260921/snapshot.json",
ART/"cleanup-current-assets/README.md",Path("E:/work/mmorpg-client/Docs/CityTilePublishing.md"),
Path("D:/luyuan/wuxingqitan/mmorpg-client/Docs/CityTilePublishing.md"),
REPO/"designs/guild-ui-v2/source/guild-overview.png",
REPO/"tianyong_festival_hd_20260910/tianyong_city_master_6144.png"]
missing=[]
for p in required:
    r=record(p)
    if not r["exists"]:missing.append(r)
run=SESSION/"continuation_20260924T104328050Z"
runfiles=[record(p) for p in sorted(run.iterdir()) if p.is_file()]
failure=readjson(run/"r08_c07-r02_c02.failed-call.json")
request=readjson(run/"r08_c07-r02_c02.request.json")
for p in request["referenced_image_paths"]:record(mapped(p))
config=readjson(REPO/"config/image-generation.json")
auto=tomllib.loads(AUTO.read_text(encoding="utf-8-sig"))
autoidentity={"id":auto["id"],"kind":auto["kind"],"name":auto["name"],"status":auto["status"],"targetThreadId":auto.get("target_thread_id"),"file":str(AUTO),"sha256":sha(AUTO.read_bytes())}
assert auto["status"]=="PAUSED"
pullfile=REPO/".git/codex-pull-20260924/state.json"
pullbytes=pullfile.read_bytes()
pull={"observedAtUtc":now(),"file":str(pullfile),"sha256":sha(pullbytes),"reportedState":json.loads(pullbytes),"completePullVerified":False,"note":"Mutable external task observation; re-read before continuation. Not proof that objects or worktree are complete."}
gitstate={"observedAtUtc":now(),"head":git("rev-parse","HEAD"),"localOriginMain":git("rev-parse","origin/main"),"headVsLocalOriginMain":git("rev-list","--left-right","--count","HEAD...origin/main"),"shortStatus":git("status","--short","--branch"),"remoteNetworkQueryPerformed":False}
for v in tracked.values():
    v["unchangedDuringCapture"]=Path(v["file"]).is_file() and sha(Path(v["file"]).read_bytes())==v["sha256"]
changed=[v["file"] for v in tracked.values() if not v["unchangedDuringCapture"]]
assert not changed,changed
snapshot={"schemaVersion":1,"capturedAtUtc":captured,"completedAtUtc":now(),"purpose":"handoff_only_not_art_acceptance","taskId":"01a0d2fd-acf8-7361-8198-24d339175bbe","workspaceRoot":str(REPO),"activeSession":str(SESSION),"counts":{"candidateCoordinates":8,"targetCoordinates":256,"coordinatesWithoutFullCandidate":248,"formalAcceptedTiles":0,"completeCityDeliveries":0,"selectedNativePatches":16,"newGeneratedImagesThisWindow":0,"ledgerTiles":len(ledger["tiles"]),"ledgerSeams":len(ledger["seams"]),"ledgerJunctions":len(ledger["junctions"])},"ledgerReportedCounts":ledger["counts"],"sessionReportedUpdateTime":session["updatedAtUtc"],"candidatePngValidation":"full_decode_dimensions_and_sha_match_not_visual_review","candidates":candidates,"selectedNativePatches":native,"patchContinuation":patchstates,"rootPointers":roots,"sourceRecords":list(tracked.values()),"sourcesChangedDuringCapture":changed,"missingRequiredFiles":missing,"thisWindowFiles":runfiles,"thisWindowGenerationFailure":{"file":str(run/"r08_c07-r02_c02.failed-call.json"),"startedAt":failure.get("startedAt"),"error":failure["error"],"outputFile":failure.get("outputFile"),"countAsGenerated":False},"configurationTargetSnapshot":config,"actualModel":None,"actualQuality":None,"automation":autoidentity,"pullObservation":pull,"git":gitstate,"limits":{"artVisualReviewPerformed":False,"layoutNavigationReviewPerformed":False,"runtimeReviewPerformed":False,"productionPublished":False,"historicalSourcesRestored":False,"sharedRecordsModified":False,"gitWritePerformedByThisCapture":False}}
writejson("snapshot.json",snapshot)
print(json.dumps({"output":str(OUT),"snapshotSha256":sha((OUT/"snapshot.json").read_bytes()),"counts":snapshot["counts"],"inputChanges":changed,"pull":pull["reportedState"],"automation":autoidentity["status"],"missingFiles":[r["file"] for r in missing]},ensure_ascii=False))
