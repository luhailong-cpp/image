"""Read-only v2 snapshot and native-correction compatibility validation."""
from pathlib import Path
import importlib.util,json,sys,copy
from types import SimpleNamespace
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
Z=Path(__file__).resolve().parent

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
old=load("old_west",Z/"production_workflow_west_extension_20261016.py")
new=load("new_west",Z/"production_workflow_west_extension_20261016_v2.py")
require=new.require
require(old.sha(old.__file__)=="bd2fec860c321993a8fff79305b15a43fe510c1d0bc06d376068ef7c1fe96a6b","Frozen west changed")
frozen_native=Z/"r13_c12/native_correction_workflow_20261016_v1.py"
require(new.sha(frozen_native)=="ced8ecb4eb0c4be932ebbf3dcd81748dae349d1505e50c8f26403eebd7a77ac3","Frozen correction helper changed")
r15=Z/"r15_c12"
records=sorted((r15/"records").glob("*.preparation.json"),key=lambda p:p.stat().st_mtime,reverse=True)[:4]
risk=[]
def snapshot_stats(value, depth=0):
    if isinstance(value,dict):
        children=[snapshot_stats(v,depth+(k=="snapshot")) for k,v in value.items()]
        return (sum(x[0] for x in children)+(1 if "snapshot" in value else 0),max([depth]+[x[1] for x in children]))
    if isinstance(value,list):
        children=[snapshot_stats(v,depth) for v in value]
        return (sum(x[0] for x in children),max([depth]+[x[1] for x in children]))
    return (0,depth)
for p in records:
    d=new.read(p);count,depth=snapshot_stats(d)
    risk.append({"path":str(p),"bytes":p.stat().st_size,"embeddedSnapshotCount":count,"maximumSnapshotNesting":depth})
native_record=r15/"native/p03_04_v20261016T152242_fcf1a9c4.png.generation.json"
parent_prep=r15/"records/p03_04_v20261016T152242_fcf1a9c4.preparation.json"
immutable=[]
for path in (native_record,parent_prep):
    entry=new.remember(path)
    require(set(entry)=={"path","sha256"},"Immutable JSON was embedded")
    require(entry["sha256"]==new.sha(path),"Immutable reference SHA differs")
    immutable.append({"path":str(path),"sourceBytes":path.stat().st_size,"v2ReferenceBytes":len(json.dumps(entry).encode())})
state_checks=[]
for path in (r15/"progress.json",r15/"active-native-map.json",Z/"r15_c13/candidate/latest-assembly.json"):
    entry=new.remember(path);raw=new.read(path)
    require(entry["sha256"]==new.sha(path) and entry["snapshotPolicy"]=="compact_mutable_selection_state_v2","Mutable snapshot SHA/policy differs")
    require("selectionSnapshots" not in json.dumps(entry),"Mutable snapshot reembedded recursive lineage")
    if path.name=="active-native-map.json":require(entry["snapshot"]==raw,"Active mapping snapshot differs")
    elif raw.get("candidate"):
        candidate=raw["candidate"]
        require(entry["snapshot"]["candidate"]==({k:candidate[k] for k in ("path","sha256","size") if k in candidate} if isinstance(candidate,dict) else candidate),"Selected candidate pointer lost")
    state_checks.append({"path":str(path),"sourceBytes":path.stat().st_size,"v2SnapshotBytes":len(json.dumps(entry).encode()),"keys":sorted(entry["snapshot"])})
sources=[]
for tile in sorted(new.ALLOWED_TILES):
    a=old.outer_anchor(tile,old.coordinate(tile,"p02_04"),"right")
    b=new.outer_anchor(tile,new.coordinate(tile,"p02_04"),"right")
    require(a[1]["path"]==b[1]["path"] and a[1]["sha256"]==b[1]["sha256"],"Selected actual core changed")
    require(np.array_equal(np.asarray(a[0]),np.asarray(b[0])),"Anchor pixel difference")
    sources.append({"tile":tile,"samePathAndShaAndPixels":True,"sha256":b[1]["sha256"]})
co=new.coordinate("r15_c12","p04_04")
guide=r15/"layout-only/p04_04-layout-only.png"
with Image.open(guide) as image:a=image.convert("RGB");b=a.copy()
anchors_old=old.collect_anchors("r15_c12",co,a)
anchors_new=new.collect_anchors("r15_c12",co,b)
require(np.array_equal(np.asarray(a),np.asarray(b)),"Target pixels changed due to metadata policy")
normalized=lambda aa:[{k:v for k,v in x.items() if k!="selectionSnapshots"} for x in aa]
require(normalized(anchors_old)==normalized(anchors_new),"Source geometry/conflict policy changed")
for anchor in anchors_new:
    for entry in anchor["selectionSnapshots"]:
        if entry["path"].endswith(".generation.json") or entry["path"].endswith(".preparation.json"):
            require(set(entry)=={"path","sha256"},"Nested immutable evidence embedded")
old_bytes=len(json.dumps(anchors_old).encode())
new_bytes=len(json.dumps(anchors_new).encode())
require(new_bytes<old_bytes/10,"Snapshot reduction unexpectedly small")
existing_versions=[
    (Z/"r13_c12","p02_04_v20261016T133928_b0df564e"),
    (Z/"r15_c12","p03_04_v20261016T152242_fcf1a9c4"),
    (Z/"r13_c12","p01_04_v20261016T155304_nativefix_50db3192")]
for t,v in existing_versions:new.validate_preparation(t,v)
adapter=new.native_correction_adapter("r13_c12")
correction_version=existing_versions[-1][1]
adapter.validate_preparation(Z/"r13_c12",correction_version)
# In-memory prospective v2 preparation/derivation; no prepared file is mutated.
# This proves old correction-v1 validation consumes unchanged anchor semantics,
# while treating selectionSnapshots as evidence and not recursively requiring it.
prepared_old=new.read(parent_prep)
virtual=copy.deepcopy(prepared_old)
for anchor in virtual["anchors"]:
    anchor["selectionSnapshots"]=[new.remember(e["path"]) for e in anchor["selectionSnapshots"]]
virtual["selectionInputSnapshots"]=[new.remember(e["path"]) for e in virtual.get("selectionInputSnapshots",[])]
virtual["evidenceSnapshotPolicy"]="immutable_path_sha_and_compact_mutable_selection_state_v2"
original_read=adapter.west.read
prep_target=Path(virtual["references"][-1]["path"])
derivation_path=Path(str(prep_target)+".derived.json")
virtual_derivation=new.read(derivation_path)
virtual_derivation["anchors"]=virtual["anchors"]
def virtual_read(path):
    resolved=Path(path).resolve()
    if resolved==parent_prep.resolve():return copy.deepcopy(virtual)
    if resolved==derivation_path.resolve():return copy.deepcopy(virtual_derivation)
    return original_read(path)
adapter.west.read=virtual_read
try:
    # Frozen west validator itself is not scoped to the correction helper's tile.
    adapter.west.validate_preparation(r15,virtual["version"])
finally:adapter.west.read=original_read
# Test dispatcher with sentinels only: no assemble, ingest, active or progress write.
saved_read,saved_adapter,saved_plain=new.read,new.native_correction_adapter,new._assemble_plain
signals=[]
sentinel=SimpleNamespace(assemble=lambda tile:signals.append(["assemble_native",tile]) or "native",
                         ingest=lambda *args:signals.append(["ingest_native",args[0]]) or "native")
active_path=Z/"r13_c12/active-native-map.json"
def dispatch_read(path):
    if Path(path).resolve()==active_path.resolve():return {"p01_04":correction_version}
    return saved_read(path)
try:
    new.read=dispatch_read;new.native_correction_adapter=lambda tile:sentinel
    require(new.assemble("r13_c12")=="native","Native assembly dispatch failed")
    require(new.ingest("r13_c12",correction_version,"unused-test-only","unused-test-only")=="native","Native ingest dispatch failed")
    new.read=saved_read;new._assemble_plain=lambda tile:"plain"
    require(new.assemble("r15_c12")=="plain","Plain assembly dispatch failed")
finally:
    new.read=saved_read;new.native_correction_adapter=saved_adapter;new._assemble_plain=saved_plain
print(json.dumps({"status":"passed_read_only_no_generation_or_selection","helper":{"path":str(Path(new.__file__)),"sha256":new.sha(new.__file__)},
 "riskObserved":risk,"immutableEvidenceChecks":immutable,"compactStateChecks":state_checks,
 "actualEastSourcesUnchanged":sources,"inMemoryP04TargetPixelsUnchanged":True,
 "p04AnchorMetadataOldBytes":old_bytes,"p04AnchorMetadataV2Bytes":new_bytes,"metadataReductionPercent":round(100*(1-new_bytes/old_bytes),2),
 "oldPreparationsStillValidate":True,"existingNativeCorrectionV1StillValidates":True,
 "frozenCorrectionV1ValidatorAcceptsV2SnapshotSchemaInMemory":True,
 "futureAssemblyAndIngestDispatchChecks":signals,"dispatchCheckScope":"Sentinel-only routing; no actual ingestion or16-source assembly performed",
 "frozenHelpersUnchanged":True,"generatedImages":0,"preparedImagesWritten":0,"activeOrProgressWritten":False},indent=2))
