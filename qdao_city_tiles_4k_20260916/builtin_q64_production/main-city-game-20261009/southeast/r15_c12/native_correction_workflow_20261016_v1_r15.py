#!/usr/bin/env python3
"""r15_c12 only: prepare a native-based correction target; never call imagegen.
The frozen west workflow remains unchanged. Plain west preparations and native
corrections are both explicitly validated by this helper's assembly entry point.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True

TILE = "r15_c12"
T = Path(__file__).resolve().parent
ZONE = T.parent
WEST_PATH = ZONE / "production_workflow_west_extension_20261016_v2.py"
WEST_SHA = "84e83c232fe872ab6a460f7a73f525fb5c96a3935e325aeff60b90f1c51a8cea"
require_hash = hashlib.sha256(WEST_PATH.read_bytes()).hexdigest()
if require_hash != WEST_SHA:
    raise ValueError("Frozen west helper changed; inspect before loading")
spec = importlib.util.spec_from_file_location("_r15c12_frozen_west", WEST_PATH)
west = importlib.util.module_from_spec(spec)
spec.loader.exec_module(west)
NATIVE, CORE, HALO, OVERLAP, TILE_SIZE, CONTEXT = west.NATIVE, west.CORE, west.HALO, west.OVERLAP, west.TILE_SIZE, west.CONTEXT
PATCHES, CONTRACT = west.PATCHES, west.CONTRACT
sha, read, require, now = west.sha, west.read, west.require, west.now
atomic_json, write_png_exclusive = west.atomic_json, west.write_png_exclusive
coordinate, verified_native, status_ok = west.coordinate, west.verified_native, west.status_ok
valid_anchor_order = west.valid_anchor_order

def tile_parts(tile, *, writable=True):
    require(not writable or tile == TILE, "Native-correction helper writes only r15_c12")
    return west.tile_parts(tile, writable=writable)

def tile_dir(tile):
    tile_parts(tile)
    return west.tile_dir(tile)

def progress(tile, status, **extra):
    tile_dir(tile)
    return west.progress(tile, status, **extra)

def make_checker():
    guards = {}
    def checked(path, expected=None):
        path = Path(path).resolve()
        digest = sha(path)
        require(expected is None or digest == expected, "Recorded hash differs: " + str(path))
        require(str(path) not in guards or guards[str(path)] == digest, "Input changed: " + str(path))
        guards[str(path)] = digest
        return digest
    return checked, guards

def local_path(value, *, local=False):
    path = Path(value)
    path = (path if path.is_absolute() else T / path).resolve()
    require(not local or path.is_relative_to(T), "Evidence escaped r15_c12")
    return path

def pasted_anchors(base, prep, checked):
    """Replay exactly the stored directions/order, including conflict precedence."""
    require(valid_anchor_order(prep["anchors"], prep["anchorOrder"]), "Invalid four-way anchor order")
    image = base.copy()
    for a in prep["anchors"]:
        checked(a["path"], a["sha256"])
        west.validate_anchor_geometry(TILE, prep["coordinates"], a)
        x0, y0, _, _ = a["target"]
        with Image.open(a["path"]) as src:
            image.paste(src.convert("RGB").crop(a["sourceCrop"]), (x0, y0))
    return image

def validate_plain_target(prep, checked):
    """Original enlarged geometry guide is validated only in the plain branch."""
    require(not prep.get("nativeCorrectionOf"), "Correction target cannot be treated as an overview-derived guide")
    target_ref = prep["references"][-1]
    target = local_path(target_ref["path"], local=True)
    checked(target, target_ref["sha256"])
    derivation_path = Path(str(target) + ".derived.json")
    checked(derivation_path)
    d = read(derivation_path)
    require(d.get("sha256") == target_ref["sha256"] and d.get("anchors") == prep["anchors"]
            and d.get("anchorOrder") == prep["anchorOrder"], "Plain target derivation differs")
    layout = local_path(d["layoutSource"], local=True)
    checked(layout, d["layoutSourceSha256"])
    layout_record = Path(str(layout) + ".derived.json")
    checked(layout_record)
    lr = read(layout_record)
    require(lr.get("sha256") == sha(layout) and lr.get("artCanvasBox") == prep["coordinates"]["contextBox"]
            and lr.get("derivedFrom", {}).get("sha256") == prep["references"][0]["sha256"], "Plain layout lineage differs")
    with Image.open(layout) as image:
        require(image.size == (NATIVE, NATIVE), "Plain guide size differs")
        replay = pasted_anchors(image.convert("RGB"), prep, checked)
    with Image.open(target) as image:
        require(image.size == (NATIVE, NATIVE) and np.array_equal(np.asarray(replay), np.asarray(image.convert("RGB"))),
                "Original anchored layout guide cannot be replayed")
    return {"targetKind": "layout_plus_native_anchors", "targetSha256": target_ref["sha256"], "pixelReplayExact": True}

def validate_parent(version, checked):
    require(re.fullmatch(r"p0[1-4]_0[1-4]_v[A-Za-z0-9_-]+", version), "Invalid parent version")
    prep_path = T / "records" / f"{version}.preparation.json"
    prep_sha = checked(prep_path)
    parent = west.validate_preparation(T, version)
    require(not parent.get("nativeCorrectionOf"), "Nested native corrections are not supported in v1")
    checked(parent["configFile"], parent["configSha256"])
    for reference in parent["references"]:
        checked(reference["path"], reference["sha256"])
    native = T / "native" / f"{version}.png"
    record_path = Path(str(native) + ".generation.json")
    record_sha = checked(record_path)
    record = read(record_path)
    native_sha = checked(native, record["sha256"])
    require(record["id"] == version and record["tile"] == TILE and record["logicalPatch"] == parent["logicalPatch"]
            and local_path(record["file"], local=True) == native.resolve()
            and record["coordinates"] == parent["coordinates"], "Parent generation identity differs")
    require(record.get("tool") == "image_gen.imagegen" and record.get("route") == "builtin"
            and record.get("actualModel") is None and record.get("actualQuality") is None
            and record.get("resizedAfterGeneration") is False and record.get("finalArtUpscaled") is False,
            "Parent must be unscaled actual builtin native")
    require(record.get("references") == parent["references"] and record.get("anchors") == parent["anchors"],
            "Parent generation references differ")
    e = record["evidence"]
    require(local_path(e["preparation"], local=True) == prep_path.resolve() and e["preparationSha256"] == prep_sha
            and e["originalSha256"] == native_sha, "Parent preparation/original evidence differs")
    for field in ("request", "prompt"):
        checked(parent[field], parent[field + "Sha256"])
    require(local_path(e["request"], local=True) == local_path(parent["request"], local=True)
            and e["requestSha256"] == parent["requestSha256"] and record["promptSha256"] == parent["promptSha256"],
            "Parent request/prompt evidence differs")
    submitted = record["submittedParameters"]
    require(submitted.get("referenced_image_paths") == [r["path"] for r in parent["references"]]
            and submitted.get("model") is None and submitted.get("quality") is None
            and submitted.get("transparent_background") is False, "Parent submitted parameters differ")
    receipt_path = local_path(e["receipt"], local=True)
    receipt_sha = checked(receipt_path, e["receiptSha256"])
    receipt = read(receipt_path)
    require(status_ok(receipt.get("status")) and receipt.get("tool", "image_gen.imagegen") == "image_gen.imagegen"
            and receipt.get("actualModel") is None and receipt.get("actualQuality") is None
            and not receipt.get("resizedAfterGeneration") and not receipt.get("finalArtUpscaled"), "Parent receipt not successful actual generation")
    for key in ("sourceSha256", "outputSha256", "sha256"):
        require(not receipt.get(key) or receipt[key] == native_sha, "Parent receipt output hash differs")
    original = local_path(e["originalOutputPath"])
    if original.exists():
        checked(original, native_sha)
    with Image.open(native) as image:
        require(image.format == "PNG" and image.size == (NATIVE, NATIVE) and image.mode == record["mode"]
                and image.mode in ("RGB", "RGBA") and (image.mode != "RGBA" or image.getextrema()[3] == (255,255)),
                "Parent is not opaque native1254")
        native_image = image.convert("RGB")
    plain_replay = validate_plain_target(parent, checked)
    lineage = {"version": version, "path": str(native), "sha256": native_sha,
               "parentGenerationRecord": {"path": str(record_path), "sha256": record_sha},
               "parentPreparation": {"path": str(prep_path), "sha256": prep_sha},
               "parentReceipt": {"path": str(receipt_path), "sha256": receipt_sha},
               "originalReferences": parent["references"], "originalRequest": {"path": parent["request"], "sha256": parent["requestSha256"]},
               "originalPrompt": {"path": parent["prompt"], "sha256": parent["promptSha256"]},
               "parentArtStatus": record.get("status"), "parentArtAcceptanceInherited": False,
               "parentGenerationSucceeded": True, "originalAnchoredGuideReplay": plain_replay,
               "sourceUse": "Known seam-failed native retained only as correction input; this does not select or accept it"}
    return parent, native_image, lineage

def validate_target(prep, checked, evidence_path=None):
    correction = prep.get("nativeCorrectionOf")
    if not correction:
        return validate_plain_target(prep, checked)
    require(prep.get("workflowExtension") == "r15c12-native-correction-20261016-v1", "Unknown native correction kind")
    helper = prep["nativeCorrectionHelper"]
    checked(helper["path"], helper["sha256"])
    parent, native, lineage = validate_parent(correction["version"], checked)
    require(correction == lineage, "Correction parent lineage differs")
    require(prep["coordinates"] == parent["coordinates"] and prep["anchors"] == parent["anchors"]
            and prep["anchorOrder"] == parent["anchorOrder"] and prep["references"][:3] == parent["references"][:3],
            "Native correction changed inherited coordinate/reference/anchor authority")
    tr = prep["references"][-1]
    target = local_path(tr["path"], local=True)
    require("native-edit-preparation" in target.parts and target != local_path(correction["path"]),
            "Correction target must be a distinct native-based preparation")
    checked(target, tr["sha256"])
    target_record_path = local_path(prep["nativeEditTarget"]["path"], local=True)
    checked(target_record_path, prep["nativeEditTarget"]["sha256"])
    d = read(target_record_path)
    require(d.get("targetKind") == "actual_native_plus_reapplied_anchors" and d.get("layoutOnly") is False
            and "layoutSource" not in d and d.get("sourceNative") == {"path": correction["path"], "sha256": correction["sha256"]}
            and d.get("anchors") == prep["anchors"] and d.get("anchorOrder") == prep["anchorOrder"]
            and d.get("target") == tr and d.get("target",{}).get("path") == str(target)
            and d.get("sourceNativeResized") is False and d.get("nativeAnchorResized") is False,
            "Native edit target provenance differs")
    replay = pasted_anchors(native, prep, checked)
    with Image.open(target) as image:
        require(image.format == "PNG" and image.size == (NATIVE,NATIVE)
                and np.array_equal(np.asarray(replay), np.asarray(image.convert("RGB"))), "Native-based target pixel replay failed")
    coverage = np.zeros((NATIVE,NATIVE), dtype=bool)
    for a in prep["anchors"]:
        x0,y0,x1,y1 = a["target"]; coverage[y0:y1,x0:x1] = True
    require(np.array_equal(np.asarray(replay)[~coverage], np.asarray(native)[~coverage]), "Pixels outside anchor rectangles changed")
    return {"targetKind": d["targetKind"], "targetSha256": tr["sha256"], "pixelReplayExact": True,
            "outsideAnchorsEqualsActualParent": True, "originalFourReferencesPreserved": True,
            "originalParentGuideReplayExact": True, "actualParentNativeSha256": correction["sha256"],
            "anchorOrder": prep["anchorOrder"], "formalAccepted": False}

def validate_preparation(t, version):
    require(Path(t).resolve() == T, "Native correction validation scope differs")
    prep = west.validate_preparation(t, version)
    checked, guards = make_checker()
    checked(t / "records" / f"{version}.preparation.json")
    validate_target(prep, checked)
    for filename,digest in guards.items():
        require(sha(filename) == digest, "Input changed during target replay")
    return prep

def prepare(parent_version, instructions):
    tile_dir(TILE)
    checked, guards = make_checker()
    checked(WEST_PATH, WEST_SHA); checked(__file__)
    parent, native, lineage = validate_parent(parent_version, checked)
    instructions_path = Path(instructions).resolve()
    checked(instructions_path)
    local = instructions_path.read_text(encoding="utf-8-sig").strip()
    require(local, "Correction instructions must be explicit and nonempty")
    contract, resume, refs, resume_path = west.current_authority()
    require(refs == parent["references"][:3], "Current three references differ; inspect instead of silently switching")
    checked(CONTRACT); checked(resume_path)
    checked(west.RULES); checked(west.SPLIT)
    patch = parent["logicalPatch"]
    version = patch + "_v" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_nativefix_" + uuid.uuid4().hex[:8]
    out = T / "native-edit-preparation" / version
    out.mkdir(parents=True, exist_ok=False)
    target = pasted_anchors(native, parent, checked)
    target_path = out / "native-plus-original-anchors-target.png"
    write_png_exclusive(target_path, target)
    target_ref = {"path": str(target_path), "sha256": sha(target_path), "dimensions": [NATIVE,NATIVE],
                  "role": "LAST IMAGE / sole EDIT TARGET: actual prior native with original integer native anchors reapplied; not enlarged layout"}
    target_record = {"schemaVersion":1,"targetKind":"actual_native_plus_reapplied_anchors","layoutOnly":False,
                     "target":target_ref,"sourceNative":{"path":lineage["path"],"sha256":lineage["sha256"]},
                     "anchors":parent["anchors"],"anchorOrder":parent["anchorOrder"],
                     "sourceNativeResized":False,"nativeAnchorResized":False,
                     "operation":"Copy actual native RGB1254, then integer crop/paste original prep anchors in stored order; no warping or drawing",
                     "deliverable":False,"actualModel":None,"actualQuality":None}
    target_record_path = out / "native-edit-target.json"
    atomic_json(target_record_path,target_record,exclusive=True)
    anchor_text = "\n".join(f'{a["direction"]}: fixed target rectangle {a["target"]}; source crop {a["sourceCrop"]}.' for a in parent["anchors"])
    prompt = f"""Use case: precise-object-edit. Produce one actual native opaque1254x1254 corrected map patch, {TILE}/{patch}.
Images1-3 are approved layout/material/style references only. Image4 (LAST) is the sole EDIT TARGET: an actual prior native1254 result with the original true neighboring anchors re-pasted at exact integer coordinates. This target is NOT a blocky layout crop. Preserve its existing composition, framing, slab sizes and painted detail; only repair the stated local seam geometry.
Do not recenter, shift the whole image, rotate, zoom, rescale, invent architecture, add blue bands or restart the stone grid. Preserve exact anchor pixels and extend their slab/grout boundaries across the editable side at matching position, tangent, width and value.
Inherited anchor order is {parent["anchorOrder"]}; later anchors win only their intersections. Preserve the final visible anchor pixels exactly:
{anchor_text}
Correction instructions:
{local}
Maintain the approved bright Taoist chibi painted map style and current natural grey/bluegrey paving. Output one full native1254 opaque PNG. No labels, frames, UI, figures, guides or enlarged layout pixels.
"""
    prefix = T / "records" / version
    prompt_path = Path(str(prefix)+".prompt.txt")
    with prompt_path.open("x",encoding="utf-8") as f:f.write(prompt)
    references = parent["references"][:3] + [target_ref]
    request = {"prompt":prompt,"referenced_image_paths":[r["path"] for r in references],"transparent_background":False}
    request_path = Path(str(prefix)+".request.json")
    atomic_json(request_path,request,exclusive=True)
    atomic_json(str(prefix)+".reference-evidence.json",references,exclusive=True)
    policy_path,policy = west.preparation_policy(T,version)
    preparation = {"schemaVersion":1,"tile":TILE,"logicalPatch":patch,"version":version,"preparedAt":now(),
        "coordinates":parent["coordinates"],"request":str(request_path),"requestSha256":sha(request_path),
        "prompt":str(prompt_path),"promptSha256":sha(prompt_path),"references":references,"anchors":parent["anchors"],
        "anchorOrder":parent["anchorOrder"],"localContent":parent["localContent"],
        "localContentEvidence":parent["localContentEvidence"],"correctionInstructions":{"path":str(instructions_path),"sha256":sha(instructions_path),"text":local},
        "configFile":str(policy_path),"configSha256":sha(policy_path),"configSnapshot":policy,
        "contractSnapshot":contract,"contractSha256":sha(CONTRACT),"resumeSnapshot":resume,"resumeSha256":sha(resume_path),
        "workflow":"west-extension-20261016","workflowExtension":"r15c12-native-correction-20261016-v1",
        "workflowSha256":WEST_SHA,"nativeCorrectionHelper":{"path":str(Path(__file__).resolve()),"sha256":sha(__file__)},
        "nativeCorrectionOf":lineage,"nativeEditTarget":{"path":str(target_record_path),"sha256":sha(target_record_path)},
        "selectionInputSnapshots":parent.get("selectionInputSnapshots",[]),
        "tool":"image_gen.imagegen","route":"builtin","actualModel":None,"actualQuality":None,"submittedModel":None,"submittedQuality":None,
        "status":"prepared_not_generated","formalAccepted":False,"activeSelectionChanged":False}
    for filename,digest in guards.items():require(sha(filename)==digest,"Input changed during correction preparation")
    prep_path = Path(str(prefix)+".preparation.json")
    atomic_json(prep_path,preparation,exclusive=True)
    report = validate(version)
    report_path = out / "preparation-validation.json"
    atomic_json(report_path,report,exclusive=True)
    return {"version":version,"request":str(request_path),"target":str(target_path),"preparation":str(prep_path),
            "validation":str(report_path),"activeSelectionChanged":False,"modelCalls":0}

def validate(version):
    prep = validate_preparation(T,version)
    checked, guards = make_checker()
    result = validate_target(prep,checked)
    return {"status":"passed_preparation_pixel_and_lineage_validation_only","version":version,
            "preparation":{"path":str(T/"records"/f"{version}.preparation.json"),"sha256":sha(T/"records"/f"{version}.preparation.json")},
            "targetValidation":result,"verifiedInputs":[{"path":p,"sha256":h} for p,h in guards.items()],
            "actualModel":None,"actualQuality":None,"formalAccepted":False,"modelCalls":0}

def ingest(version, source, receipt):
    """Only explicit invocation selects a received native; prepare/validate never do."""
    validate_preparation(T,version)
    return west._ingest_plain(TILE,version,source,receipt)



# Assembly copied from the frozen west helper; only target validation is extended.
def assemble(tile):
    """Build an immutable candidate from sixteen verified natives; never grant QA."""
    t = tile_dir(tile)
    guards = {}

    def checked(path, expected=None):
        path = Path(path).resolve()
        require(path.is_file(), f"Assembly input missing: {path}")
        digest = sha(path)
        if expected is not None:
            require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected), f"Invalid recorded hash: {path}")
            require(digest == expected, f"Assembly input changed: {path}")
        require(str(path) not in guards or guards[str(path)] == digest, f"Input changed during validation: {path}")
        guards[str(path)] = digest
        return digest

    def unchanged():
        for filename, digest in guards.items():
            require(Path(filename).is_file() and sha(filename) == digest, f"Input changed during assembly: {filename}")

    def evidence_path(value, *, local=False):
        require(isinstance(value, str) and bool(value), "Missing evidence path")
        path = Path(value)
        path = (path if path.is_absolute() else t / path).resolve()
        require(not local or path.is_relative_to(t.resolve()), f"Tile evidence path escaped tile: {path}")
        return path

    checked(WEST_PATH, WEST_SHA)
    checked(t / "initialization.json")
    initialization = read(t / "initialization.json")
    require(initialization.get("schemaVersion") == 1 and initialization.get("tile") == tile, "Invalid tile initialization")
    checked(CONTRACT)
    contract = read(CONTRACT)
    require(contract.get("artCanvasPixels") == [65536, 65536] and contract.get("formalTilePixels") == [TILE_SIZE, TILE_SIZE]
            and contract.get("rows") == 16 and contract.get("columns") == 16, "Artwork coordinate contract changed")
    plan = contract.get("nativePatchPlan", {})
    require((plan.get("expectedNativePixels"), plan.get("corePixels"), plan.get("haloPixels"), plan.get("subrows"), plan.get("subcolumns"))
            == (NATIVE, CORE, HALO, 4, 4) and plan.get("resizeFinalArtAllowed") is False, "Native composition contract changed")
    require(contract.get("builtinOnly") is True and contract.get("paidApiAllowed") is False, "Builtin-only composition required")
    checked(t / "coordinates.json")
    co = read(t / "coordinates.json")
    r, c = tile_parts(tile)
    x, y = (c - 1) * TILE_SIZE, (r - 1) * TILE_SIZE
    require(co.get("tile") == tile and co.get("coreBox") == [x, y, x + TILE_SIZE, y + TILE_SIZE]
            and co.get("contextBox") == [x - HALO, y - HALO, x + TILE_SIZE + HALO, y + TILE_SIZE + HALO]
            and co.get("patches") == [coordinate(tile, p) for p in PATCHES], "Tile coordinates changed")
    checked(t / "active-native-map.json")
    active = read(t / "active-native-map.json")
    require(set(active) == set(PATCHES), f"Exactly16 logical patches required; missing={sorted(set(PATCHES) - set(active))}; extra={sorted(set(active) - set(PATCHES))}")
    require(all(isinstance(v, str) for v in active.values()) and len(set(active.values())) == 16, "Active native versions must be sixteen distinct names")
    sources, pixels, native_hashes = [], [], set()
    for patch in PATCHES:
        version = active[patch]
        require(re.fullmatch(re.escape(patch) + r"_v[A-Za-z0-9_-]+", version), f"Invalid active version: {version}")
        prep_path = t / "records" / f"{version}.preparation.json"
        prep_sha = checked(prep_path)
        prep = validate_preparation(t, version)
        require(prep.get("logicalPatch") == patch and prep.get("tool") == "image_gen.imagegen" and prep.get("route") == "builtin", "Preparation identity/route mismatch")
        require(prep.get("actualModel") is None and prep.get("actualQuality") is None, "Preparation must not claim actual backend selectors")
        image, native, record = verified_native(t, patch)
        native_sha = checked(native, record.get("sha256"))
        record_path = Path(str(native) + ".generation.json")
        record_sha = checked(record_path)
        require(native_sha not in native_hashes, f"Same native output assigned twice: {version}")
        native_hashes.add(native_sha)
        require(record.get("id") == version and record.get("logicalPatch") == patch and record.get("tile") == tile
                and evidence_path(record.get("file"), local=True) == native.resolve(), "Native record identity mismatch")
        require(record.get("tool") == "image_gen.imagegen" and record.get("route") == "builtin", "Non-builtin native source")
        require([record.get("width"), record.get("height")] == [NATIVE, NATIVE] and record.get("format") == "PNG", "Native recorded dimensions/format changed")
        require(record.get("actualModel") is None and record.get("actualQuality") is None, "Actual builtin model/quality must remain unknown")
        with Image.open(native) as actual:
            actual.load()
            require(actual.mode in ("RGB", "RGBA") and actual.mode == record.get("mode"), f"Native mode differs: {version}")
            require(actual.mode != "RGBA" or actual.getextrema()[3] == (255, 255), f"Native has transparent pixels: {version}")
        evidence = record.get("evidence", {})
        require(evidence_path(evidence.get("preparation"), local=True) == prep_path.resolve(), "Wrong preparation evidence")
        require(evidence.get("preparationSha256") == prep_sha and evidence.get("originalSha256") == native_sha, "Preparation/original hash mismatch")
        receipt_path = evidence_path(evidence.get("receipt"), local=True)
        require(isinstance(evidence.get("receiptSha256"), str), "Missing immutable receipt hash")
        receipt_sha = checked(receipt_path, evidence.get("receiptSha256"))
        receipt = read(receipt_path)
        require(status_ok(receipt.get("status")) and receipt.get("tool", "image_gen.imagegen") == "image_gen.imagegen", "Missing successful builtin receipt")
        require(receipt.get("actualModel") is None and receipt.get("actualQuality") is None, "Receipt claims unverified actual backend values")
        require(not receipt.get("resizedAfterGeneration") and not receipt.get("finalArtUpscaled"), "Receipt reports resized output")
        for key in ("sourceSha256", "outputSha256", "sha256"):
            require(not receipt.get(key) or receipt[key] == native_sha, f"Receipt output hash mismatch: {key}")
        original = evidence_path(evidence.get("originalOutputPath"))
        original_present = original.is_file()
        if original_present:
            checked(original, native_sha)
        request_path = evidence_path(evidence.get("request"), local=True)
        prompt_path = evidence_path(record.get("prompt"), local=True)
        require(request_path == evidence_path(prep.get("request"), local=True)
                and prompt_path == evidence_path(prep.get("prompt"), local=True), "Preparation request/prompt paths differ")
        request_sha = checked(request_path, prep.get("requestSha256"))
        prompt_sha = checked(prompt_path, prep.get("promptSha256"))
        require(evidence.get("requestSha256") == request_sha and record.get("promptSha256") == prompt_sha, "Record request/prompt hashes differ")
        request = read(request_path)
        require(request.get("transparent_background") is False and "num_last_images_to_include" not in request, "Opaque explicit-reference request required")
        require(record.get("references") == prep.get("references") and record.get("anchors") == prep.get("anchors"), "Native preparation references/anchors differ")
        references = prep["references"]
        require(isinstance(references, list) and len(references) == 4, "Three style/layout references plus one anchored target required")
        prepared_contract = prep.get("contractSnapshot", {})
        for reference, field, hash_field in zip(references[:3],
                ("layoutReference", "detailStyleReference", "primaryStyleReference"),
                ("layoutSha256", "detailSha256", "primaryStyleSha256")):
            require(evidence_path(reference.get("path")) == evidence_path(prepared_contract.get(field))
                    and reference.get("sha256") == prepared_contract.get(hash_field), "Submitted style/layout reference differs from preparation contract")
        submitted = record.get("submittedParameters", {})
        require(submitted.get("referenced_image_paths") == request.get("referenced_image_paths")
                and submitted.get("transparent_background") is False
                and submitted.get("model") is None and submitted.get("quality") is None, "Submitted parameters differ")
        for ref in references:
            path = evidence_path(ref.get("path"))
            checked(path, ref.get("sha256"))
            with Image.open(path) as ref_image:
                require(list(ref_image.size) == ref.get("dimensions"), f"Reference dimensions changed: {path}")
            require(bool(ref.get("role")), f"Reference role missing: {path}")
        target_validation = validate_target(prep, checked, evidence_path)
        pixels.append(np.asarray(image).copy())
        sources.append({"logicalId": patch, "activeVersion": version, "native": str(native), "nativeSha256": native_sha,
                        "measuredSize": [NATIVE, NATIVE], "generationRecord": str(record_path), "generationRecordSha256": record_sha,
                        "generationRecordSnapshot": record, "preparation": str(prep_path), "preparationSha256": prep_sha,
                        "preparationSnapshot": prep, "receiptSha256": receipt_sha, "receiptSnapshot": receipt,
                        "requestSha256": request_sha, "requestSnapshot": request, "coordinates": coordinate(tile, patch),
                        "anchorGuideReplayVerified": True, "targetValidation": target_validation,
                        "nativeCorrectionOf": prep.get("nativeCorrectionOf"), "originalFilePresentAndVerified": original_present})

    # Import only the proven numeric join function, never historical preflight/output code.
    algorithm_path = ZONE / "assemble_candidate.py"
    algorithm_sha = checked(algorithm_path)
    checked(Path(__file__))
    spec = importlib.util.spec_from_file_location("_southeast_native_seam_algorithm", algorithm_path)
    require(spec is not None and spec.loader is not None, "Cannot load seam algorithm")
    algorithm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(algorithm)
    require(algorithm.OVERLAP == OVERLAP and algorithm.FEATHER_RADIUS == 2.0, "Seam algorithm parameters changed")
    seam_arrays, seams, strips = {}, [], []
    for row in range(4):
        strip = pixels[row * 4]
        for col in range(1, 4):
            strip, metric = algorithm.append_patch(strip, pixels[row * 4 + col], f"row{row+1:02d}_c{col:02d}_c{col+1:02d}", seam_arrays)
            seams.append(metric)
        require(strip.shape == (NATIVE, CONTEXT, 3), "Assembled row size changed")
        strips.append(strip)
    context = strips[0].transpose(1, 0, 2)
    for row in range(1, 4):
        context, metric = algorithm.append_patch(context, strips[row].transpose(1, 0, 2), f"rows_r{row:02d}_r{row+1:02d}", seam_arrays)
        seams.append(metric)
    context = context.transpose(1, 0, 2)
    require(context.shape == (CONTEXT, CONTEXT, 3), "Assembled context size changed")
    final = Image.fromarray(context[HALO:HALO + TILE_SIZE, HALO:HALO + TILE_SIZE].copy())
    identity = {"tile": tile, "activeMap": active, "inputs": guards, "algorithmSha256": algorithm_sha,
                "overlap": OVERLAP, "featherRadiusPixels": 2.0, "crop": [HALO, HALO, HALO + TILE_SIZE, HALO + TILE_SIZE]}
    version_hash = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    suffix = version_hash[:20]
    candidate_dir, review_dir = t / "candidate", t / "review" / f"assembly-{suffix}"
    manifest_path = candidate_dir / f"{tile}-assembly-{suffix}.json"
    unchanged()
    if manifest_path.exists():
        previous = read(manifest_path)
        require(previous.get("assemblyIdentitySha256") == version_hash, "Assembly filename hash collision")
        for item in [previous["context"], previous["candidate"], previous["seamPathsAndAlpha"], *previous["reviewImages"]]:
            require(Path(item["path"]).is_file() and sha(item["path"]) == item["sha256"], "Existing immutable assembly output changed")
        return {"tile": tile, "status": previous["status"], "alreadyAssembled": True, "candidate": previous["candidate"]["path"],
                "context": previous["context"]["path"], "manifest": str(manifest_path), "formalAccepted": False}
    candidate_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    def output_png(path, image):
        if not path.exists():
            write_png_exclusive(path, image)
        with Image.open(path) as saved:
            require(saved.size == image.size and np.array_equal(np.asarray(saved), np.asarray(image)), f"Saved output pixel mismatch: {path}")
        return {"path": str(path), "sha256": sha(path), "size": list(image.size)}

    context_output = output_png(candidate_dir / f"{tile}-context-4326-{suffix}.png", Image.fromarray(context))
    candidate_output = output_png(candidate_dir / f"{tile}-4k-candidate-{suffix}.png", final)
    review_items = []
    rectangles = {}
    for position in (CORE, CORE * 2, CORE * 3):
        rectangles[f"vertical-x{position}-full-height"] = [position - 256, 0, position + 256, TILE_SIZE]
        rectangles[f"horizontal-y{position}-full-width"] = [0, position - 256, TILE_SIZE, position + 256]
    for sy in (CORE, CORE * 2, CORE * 3):
        for sx in (CORE, CORE * 2, CORE * 3):
            rectangles[f"junction-x{sx}-y{sy}"] = [sx - 450, sy - 450, sx + 450, sy + 450]
    rectangles.update({"edge-north": [0, 0, TILE_SIZE, 256], "edge-south": [0, TILE_SIZE - 256, TILE_SIZE, TILE_SIZE],
                       "edge-west": [0, 0, 256, TILE_SIZE], "edge-east": [TILE_SIZE - 256, 0, TILE_SIZE, TILE_SIZE]})
    for label, box in rectangles.items():
        item = output_png(review_dir / f"{label}-100pct.png", final.crop(box))
        item.update(kind="native-pixel-crop", cropBoxIn4096=box, resized=False)
        review_items.append(item)
    overview = output_png(review_dir / "overview-preview-only.png", final.resize((1024, 1024), Image.Resampling.LANCZOS))
    overview.update(kind="downsampled-preview-only", resized=True, deliverable=False)
    review_items.append(overview)
    masks_path = review_dir / "seam-paths-and-alpha.npz"
    if masks_path.exists():
        with np.load(masks_path, allow_pickle=False) as saved_masks:
            require(set(saved_masks.files) == set(seam_arrays) and all(np.array_equal(saved_masks[key], value)
                    for key, value in seam_arrays.items()), "Existing seam arrays differ; preserve them and inspect")
    else:
        with masks_path.open("xb") as stream:
            np.savez_compressed(stream, **seam_arrays)
    masks = {"path": str(masks_path), "sha256": sha(masks_path), "arrayKeys": sorted(seam_arrays)}
    unchanged()
    manifest = {"schemaVersion": 1, "createdAt": now(), "tile": tile, "assemblyIdentitySha256": version_hash,
                "status": "candidate_pending_internal_and_external_visual_review", "formalAccepted": False,
                "internalArtQA": "pending", "externalNeighborSeamQA": "pending", "worldSize": None,
                "clientMappingValidated": False, "capacity5000Validated": False, "activeNativeMapSnapshot": active,
                "contractSnapshot": contract, "verifiedInputHashes": guards, "nativeSources": sources,
                "parameters": {"grid": [4, 4], "order": "row-major", "tileGlobalCoreBox": co["coreBox"],
                    "tileGlobalContextBox": co["contextBox"], "nativePixels": [NATIVE, NATIVE], "corePixels": CORE,
                    "haloPerSide": HALO, "adjacentOverlap": OVERLAP, "assembledSize": [CONTEXT, CONTEXT],
                    "finalCropBox": [HALO, HALO, HALO + TILE_SIZE, HALO + TILE_SIZE],
                    "method": "minimum-error seam; horizontal row joins, then vertical strip joins",
                    "algorithm": {"path": str(algorithm_path), "sha256": algorithm_sha, "function": "append_patch"},
                    "featherRadiusPixels": 2.0, "blendArithmetic": "(left*(255-alpha)+right*alpha+127)//255, uint32",
                    "sourceResampling": False, "sourceUpscaling": False, "registration": False, "colorMatching": False,
                    "globalBlur": False, "sharpening": False, "layoutOnlyPixelsComposited": False},
                "seamMetrics": seams, "seamPathsAndAlpha": masks, "context": context_output,
                "candidate": candidate_output, "reviewImages": review_items,
                "visualReview": {"status": "pending", "fullVerticalSeamBands": 3, "fullHorizontalSeamBands": 3,
                    "junctionCrops": 9, "externalEdgeCrops": 4, "required": "Inspect native seam/edge crops; numeric error and blending do not establish geometry continuity or formal acceptance"}}
    atomic_json(manifest_path, manifest, exclusive=True)
    atomic_json(candidate_dir / "latest-assembly.json", {"schemaVersion": 1, "tile": tile, "status": manifest["status"],
                "manifest": {"path": str(manifest_path), "sha256": sha(manifest_path)}, "assemblyIdentitySha256": version_hash,
                "context": context_output, "candidate": candidate_output, "formalAccepted": False})
    progress(tile, manifest["status"], candidate=candidate_output["path"],
             context=context_output["path"], assemblyManifest=str(manifest_path), complete4kCandidateCount=1,
             missingNativeCount=0, nextStep="Inspect all six full seam bands, nine junctions and four edges at 100%; verify neighboring tile seams before acceptance")
    return {"tile": tile, "status": manifest["status"], "nativeSourceCount": 16, "candidate": candidate_output["path"],
            "context": context_output["path"], "manifest": str(manifest_path), "reviewDirectory": str(review_dir), "formalAccepted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command",required=True)
    p=subs.add_parser("prepare");p.add_argument("parent_version");p.add_argument("instructions")
    p=subs.add_parser("validate");p.add_argument("version")
    p=subs.add_parser("ingest");p.add_argument("version");p.add_argument("source");p.add_argument("receipt")
    subs.add_parser("assemble")
    args=vars(parser.parse_args());command=args.pop("command")
    try:
        result=assemble(TILE) if command=="assemble" else globals()[command](**args)
        print(json.dumps(result,ensure_ascii=True,indent=2))
    except (ValueError,KeyError,FileNotFoundError) as exc:
        print(json.dumps({"error":str(exc),"formalAccepted":False},ensure_ascii=True),file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
