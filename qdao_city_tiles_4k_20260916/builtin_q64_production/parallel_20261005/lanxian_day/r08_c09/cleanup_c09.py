from pathlib import Path
import json, hashlib, sys
from datetime import datetime, timezone
from PIL import Image, ImageChops

BASE = Path(r"D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel_20261005\lanxian_day").resolve()
ROOT = (BASE / "r08_c09").resolve()
NEXT = (BASE / "r08_c10").resolve()
MANIFEST = ROOT / "cleanup-manifest.json"
EXPECTED = {
    "core": "f234b170956464dd3233207d38d6520d5388942b771a5b25c32683c4cecfdbeb",
    "extended": "2a4b8d427435f5595d179c63530b2e9bfa62656436b28f082bdbdedefbde860e",
}
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p):
    with p.open("rb") as f: return hashlib.file_digest(f, "sha256").hexdigest()
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def safe(p):
    p = Path(p)
    r = p.resolve(strict=True)
    assert r.is_relative_to(ROOT) and r != ROOT, f"OUTSIDE SCOPE: {p}"
    assert not p.is_symlink() and p.is_file(), f"NOT ORDINARY FILE: {p}"
    return r
def filemeta(p, pixels=False):
    p = p.resolve()
    d = {"absolutePath": str(p), "sha256": sha(p), "bytes": p.stat().st_size}
    if pixels:
        with Image.open(p) as im: d.update(pixels=list(im.size), mode=im.mode, format=im.format)
    return d
def walk(obj, trail="$", parent=None):
    if isinstance(obj, dict):
        yield trail, obj, parent
        for k, v in obj.items(): yield from walk(v, trail+"."+k, obj)
    elif isinstance(obj, list):
        for i, v in enumerate(obj): yield from walk(v, trail+"["+str(i)+"]", parent)
    else: yield trail, obj, parent
def sourcepath(s):
    if not isinstance(s, str): return None
    ss = s.replace("\\", "/")
    if ss.startswith("r08_c09/"): return BASE / ss
    if len(ss)>2 and ss[1:3]==":/": return Path(s)
    return None
def scan_next():
    active, historical, files = {}, [], []
    for p in sorted(NEXT.rglob("*.json")):
        obj = read(p)
        files.append(filemeta(p))
        for trail, val, parent in walk(obj):
            q = sourcepath(val)
            if q is None or q.suffix.lower() != ".png": continue
            q = q.resolve()
            if not q.is_relative_to(ROOT): continue
            ref = {"record": str(p), "jsonPointer": trail, "path": str(q)}
            if ".eastContextReview.boards[" in trail:
                ref.update(role="historical_original_pixel_review_evidence", currentFileRequired=False)
                historical.append(ref)
            else:
                ref.update(role="active_neighbor_context", currentFileRequired=True)
                if isinstance(parent, dict) and parent.get("sha256"): ref["declaredSha256"] = parent["sha256"]
                active.setdefault(str(q), []).append(ref)
    return active, historical, files
def audit_delivery():
    dp = ROOT / "selected/delivery.manifest.json"
    d = read(dp)
    assert d["qualifiedComplete4KCandidate"] is True
    checked = []
    for k in ("core", "extended", "preview"):
        out = d["outputs"][k]; p = safe(out["file"]); m = filemeta(p, True)
        assert m["sha256"] == out["sha256"]
        assert m["pixels"] == out["pixels"]
        if k in EXPECTED: assert m["sha256"] == EXPECTED[k]
        checked.append(m)
    with Image.open(d["outputs"]["core"]["file"]) as core, Image.open(d["outputs"]["extended"]["file"]) as ext:
        assert ImageChops.difference(core.convert("RGB"), ext.crop((115,115,4211,4211)).convert("RGB")).getbbox() is None
    sources = d["sourceChain"]["nativeSources"]
    assert len(sources)==16 and len({x["cell"] for x in sources})==16
    native = []
    for s in sources:
        f=Path(s["file"]); g=Path(s["generationRecord"])
        assert sha(f)==s["sha256"] and sha(g)==s["generationRecordSha256"]
        rec=read(g)
        assert rec.get("sha256")==s["sha256"]
        assert "actualModel" in rec and "actualQuality" in rec and rec.get("generatedAt")
        if rec.get("role") != "reused_historical_native_fragment":
            assert rec.get("prompt") or rec.get("promptFile") or rec.get("promptSha256")
        native.append({"cell":s["cell"],"historicalSourcePng":str(f),"sha256":s["sha256"],"currentFileRequired":False,"generationRecord":str(g),"generationRecordSha256":sha(g)})
    pairs=[("file","sha256"),("path","sha256"),("generationRecord","generationRecordSha256"),("sourceJob","sourceJobSha256"),("toolResultPath","toolResultSha256")]
    verified={}
    for trail,val,_ in walk(d):
        if not isinstance(val,dict): continue
        for pk,hk in pairs:
            if isinstance(val.get(pk),str) and isinstance(val.get(hk),str):
                q=sourcepath(val[pk])
                if q is None: continue
                q=q.resolve()
                if not q.is_relative_to(ROOT): continue
                assert q.is_file(), f"Missing delivery reference: {q}"
                assert sha(q)==val[hk], f"Changed delivery reference: {q}"
                verified[str(q)]=filemeta(q)
    return d,{"delivery":filemeta(dp),"qualifiedComplete4KCandidate":True,"formalAcceptedUnchanged":d["formalAccepted"],"outputs":checked,"coreExactlyExtendedCenter":True,"nativeSourceEvidence":native,"verifiedDeliveryReferences":list(verified.values())}
def plan():
    assert not MANIFEST.exists(), "Existing manifest: do not overwrite"
    delivery,audit=audit_delivery()
    active,historical,nextfiles=scan_next()
    required={str((ROOT/"registration-west/v3/extended4326.png").resolve()),str((ROOT/"registration-west/v3/core4096.png").resolve())}
    assert required.issubset(set(active))
    allfiles=sorted(p for p in ROOT.rglob("*") if p.is_file())
    text_records=[]
    for p in allfiles:
        if p.suffix.lower()==".json": read(p)
        if p.suffix.lower()!=".png": text_records.append(filemeta(p))
    selected = {"core":delivery["outputs"]["core"],"extended":delivery["outputs"]["extended"]}
    entries=[]
    for p in allfiles:
        if p.suffix.lower()!=".png": continue
        p=safe(p); rel=p.relative_to(ROOT).as_posix(); m=filemeta(p,True)
        refs=active.get(str(p),[])
        for ref in refs:
            if "declaredSha256" in ref: assert m["sha256"]==ref["declaredSha256"]
        if rel.startswith("selected/"):
            action="retain"; use="selected_delivery_art_or_selected_QA"; reason="Preserve the entire selected directory."
        elif "mask" in p.name.lower():
            action="retain"; use="technical_repair_audit_mask"; reason="Technical mask is retained as bounded repair evidence."
        elif refs:
            action="retain"; use="active_r08_c10_neighbor_context"; reason="Current r08_c10 JSON uses this PNG; unique in-progress dependency."
        else:
            action="delete"; use=("historical_native_source" if rel.startswith("native/") else "guide_or_regional_intermediate" if rel.startswith(("guides/","regional/")) else "historical_QA_image" if "/qa/" in "/"+rel or rel.startswith("qa/") else "superseded_stage_or_candidate")
            reason="Selected complete 4K candidate is present and hash-verified; former source/intermediate has been superseded and its textual provenance is retained."
        m.update(relativePath=rel, action=action, usage=use, reason=reason,
                 currentFileRequired=action=="retain", activeReferences=refs,
                 supersededBySelected=selected if action=="delete" else None,
                 deletionStatus="pending" if action=="delete" else "retained")
        entries.append(m)
    manifest={"schemaVersion":1,"tile":"r08_c09","createdAtUtc":now(),"status":"planned_no_deletions",
        "scopeRoot":str(ROOT),"authorization":"User AGENTS.md retention preference dated 2026-09-23 and root task explicit cleanup instruction.",
        "preservationRules":["Entire selected directory","Technical PNG masks","Current r08_c10 source PNG dependencies","All JSON/txt and other non-PNG files, including npy/npz"],
        "historySemantics":"Retired PNG paths in source records remain historical provenance, not current required files. Existing immutable delivery retention text describes its pre-cleanup timestamp; this cleanup manifest supersedes that historical retention state.",
        "deliveryPreflight":audit,"activeReferenceAudit":{"nextTile":str(NEXT),"allJsonRecordsScanned":nextfiles,"activePngReferences":active,"historicalReviewReferences":historical},
        "preservedNonPngFiles":text_records,"pngFiles":entries,
        "summary":{"pngCount":len(entries),"plannedDeleteCount":sum(e["action"]=="delete" for e in entries),"plannedDeleteBytes":sum(e["bytes"] for e in entries if e["action"]=="delete"),"retainedPngCount":sum(e["action"]=="retain" for e in entries),"preservedNonPngCount":len(text_records),"activePngCount":len(active)}}
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":manifest["status"],"manifest":str(MANIFEST),"summary":manifest["summary"],"retainedPng":[e["relativePath"] for e in entries if e["action"]=="retain"]}))
def apply():
    m=read(MANIFEST); assert m["status"]=="planned_no_deletions"
    active,historical,nextfiles=scan_next()
    for e in m["pngFiles"]:
        p=safe(e["absolutePath"])
        assert sha(p)==e["sha256"] and p.stat().st_size==e["bytes"], f"Changed since plan: {p}"
        if e["action"]=="delete":
            assert str(p) not in active
            assert not p.is_relative_to(ROOT/"selected") and "mask" not in p.name.lower()
    for e in m["preservedNonPngFiles"]:
        assert sha(safe(e["absolutePath"]))==e["sha256"]
    m["status"]="deletion_in_progress";m["deletionStartedAtUtc"]=now()
    MANIFEST.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for e in m["pngFiles"]:
        if e["action"]!="delete":continue
        p=safe(e["absolutePath"]);assert sha(p)==e["sha256"]
        p.unlink()
        e["deletionStatus"]="deleted"; e["deletedAtUtc"]=now()
    active_after,history_after,files_after=scan_next()
    for path, refs in active_after.items():
        q=safe(path);actual=sha(q)
        for ref in refs:
            if "declaredSha256" in ref: assert actual==ref["declaredSha256"]
    for e in m["pngFiles"]:
        p=Path(e["absolutePath"])
        assert (not p.exists()) if e["action"]=="delete" else p.exists() and sha(p)==e["sha256"]
    for e in m["preservedNonPngFiles"]: assert sha(Path(e["absolutePath"]))==e["sha256"]
    m["status"]="completed";m["completedAtUtc"]=now()
    m["summary"].update(deletedCount=sum(e["deletionStatus"]=="deleted" for e in m["pngFiles"]),deletedBytes=sum(e["bytes"] for e in m["pngFiles"] if e["deletionStatus"]=="deleted"),allPreservedFilesUnchanged=True)
    m["postCleanupReferenceCheck"]={"checkedAtUtc":now(),"activePngCount":len(active_after),"allActivePngExistAndHashesMatch":True,"allJsonRecordsScanned":files_after,"historicalReviewPngStatus":"retired; inspection findings and hashes remain in JSON","noFilesOutsideScopeDeleted":True,"noDirectoriesDeleted":True}
    MANIFEST.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":m["status"],"manifest":str(MANIFEST),"summary":m["summary"],"activeReferenceCheck":{k:v for k,v in m["postCleanupReferenceCheck"].items() if k!="allJsonRecordsScanned"}}))
if __name__=="__main__":
    {"plan":plan,"apply":apply}[sys.argv[1]]()

