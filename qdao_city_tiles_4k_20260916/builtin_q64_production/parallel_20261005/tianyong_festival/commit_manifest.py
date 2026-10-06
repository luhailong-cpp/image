"""Commit one reviewed native patch manifest and all coupled return strips.

Usage: python commit_manifest.py FINAL/manifest.json v007 --checkpoint-sha SHA
Validation is completed before any image/state write. --validate-only is read-only.
The version directory is published as a set, then source-checkpoint.json is the
last root pointer switched. This script never writes an upstream source image.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

import numpy as np
from PIL import Image

TASK = Path(__file__).resolve().parent
TILE_SIZE = 4096
ACTIVE = "r08_c10"
BOTTOM = "r09_c10"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def info(path):
    p = Path(path).resolve()
    return {"file": str(p), "sha256": sha(p)}


def write(path, data):
    path = Path(path).resolve()
    path.relative_to(TASK)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checked_ref(ref):
    require(isinstance(ref, dict) and "file" in ref and "sha256" in ref, "Missing file/SHA reference")
    p = Path(ref["file"]).resolve()
    require(sha(p) == ref["sha256"].lower(), f"Source SHA changed: {p}")
    return p


def box(value, name):
    require(isinstance(value, (list, tuple)) and len(value) == 4, f"Invalid {name}")
    require(all(type(v) is int for v in value), f"Noninteger {name}")
    l, t, r, b = value
    require(l < r and t < b, f"Empty {name}")
    return list(value)


def contains(outer, inner):
    return outer[0] <= inner[0] and outer[1] <= inner[1] and outer[2] >= inner[2] and outer[3] >= inner[3]


def tile_origin(tile):
    match = re.fullmatch(r"r([0-9]{2})_c([0-9]{2})", tile)
    require(match is not None, f"Invalid tile name: {tile}")
    row, column = map(int, match.groups())
    require(1 <= row <= 16 and 1 <= column <= 16, "Tile outside256-tile city")
    return [(column-1)*TILE_SIZE, (row-1)*TILE_SIZE]


def image_record(ref):
    p = checked_ref(ref)
    with Image.open(p) as image:
        image.load()
        pixels = np.asarray(image.convert("RGBA")).copy()
    h, w = pixels.shape[:2]
    # Full tiles use their own tile coordinates. sourceTileLocalBox in old
    # preparation records may instead describe their position relative to c10.
    if "tileLocalLTRB" in ref:
        bounds = box(ref["tileLocalLTRB"], "tileLocalLTRB")
    elif (w, h) == (TILE_SIZE, TILE_SIZE):
        bounds = [0, 0, TILE_SIZE, TILE_SIZE]
    elif "sourceTileLocalBox" in ref:
        bounds = box(ref["sourceTileLocalBox"], "sourceTileLocalBox")
    else:
        raise ValueError(f"Unlocated partial source: {p}")
    require((bounds[2] - bounds[0], bounds[3] - bounds[1]) == (w, h), f"Source dimensions/offset disagree: {p}")
    require(contains([0, 0, TILE_SIZE, TILE_SIZE], bounds), f"Source is not in own tile coordinates: {p}")
    require(np.all((pixels[:, :, 3] == 0) | (pixels[:, :, 3] == 255)), f"Partial alpha in native source: {p}")
    return {"ref": deepcopy(ref), "pixels": pixels, "box": bounds}


def roi(record, bounds, allow_missing=False):
    result = np.zeros((bounds[3] - bounds[1], bounds[2] - bounds[0], 4), dtype=np.uint8)
    own = record["box"]
    if not allow_missing:
        require(contains(own, bounds), f"Requested ROI outside source: {record['ref']['file']} {bounds}")
    overlap = [max(own[0], bounds[0]), max(own[1], bounds[1]), min(own[2], bounds[2]), min(own[3], bounds[3])]
    if overlap[0] < overlap[2] and overlap[1] < overlap[3]:
        l, t, r, b = overlap
        result[t-bounds[1]:b-bounds[1], l-bounds[0]:r-bounds[0]] = record["pixels"][t-own[1]:b-own[1], l-own[0]:r-own[0]]
    return result


def entries(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    require(isinstance(value, dict), "Candidate set must be an object or array")
    if "candidates" in value:
        return entries(value["candidates"])
    if "file" in value and "sha256" in value and "tile" not in value:
        return entries(read(checked_ref(value)))
    return [{**v, "tile": k} for k, v in value.items()]


def build_plan(manifest_path, version, expected_checkpoint):
    manifest_path = manifest_path.resolve()
    manifest_path.relative_to(TASK)
    checkpoint_path = TASK / "source-checkpoint.json"
    handoff_path = TASK / "handoff.json"
    require(sha(checkpoint_path) == expected_checkpoint.lower(), "Current checkpoint changed; review ownership before committing")
    checkpoint_ref, handoff_ref = info(checkpoint_path), info(handoff_path)
    previous, handoff, manifest = read(checkpoint_path), read(handoff_path), read(manifest_path)
    require(re.fullmatch(r"v[0-9]{3,}", version) is not None, "Version must be v followed by at least three digits")
    output = TASK / ACTIVE / "current" / version
    require(not output.exists(), f"Version already exists: {output}")
    require(manifest.get("nativeScale") == 1, "Manifest is not native-scale")
    require(manifest.get("localVisualAccepted", manifest.get("localAccepted", False)) is True, "Manifest is not locally accepted")
    review_ref = manifest.get("visualReview", info(manifest_path.parent / "visual-review.json"))
    review_path = checked_ref(review_ref)
    review = read(review_path)
    require(review.get("localVisualAccepted", review.get("localAccepted", False)) is True, "Visual review is not locally accepted")
    joined_path = checked_ref(manifest["joined"])
    with Image.open(joined_path) as image:
        joined = np.asarray(image.convert("RGBA")).copy()
    require(np.all(joined[:, :, 3] == 255), "Reviewed joined image has transparency")
    window = box(manifest["windowTileLocalLTRB"], "windowTileLocalLTRB")
    require(joined.shape[:2] == (window[3]-window[1], window[2]-window[0]), "Joined dimensions do not match its native window")
    reviewed_image = review.get("image", review.get("output"))
    require(reviewed_image and checked_ref(reviewed_image) == joined_path and reviewed_image["sha256"] == manifest["joined"]["sha256"], "Review is for a different joined image")
    if "core" in manifest:
        core_path = checked_ref(manifest["core"])
        c = box(manifest["coreTileLocalLTRB"], "coreTileLocalLTRB")
        require(contains(window, c), "Core is outside reviewed window")
        with Image.open(core_path) as image:
            core = np.asarray(image.convert("RGBA"))
        require(np.array_equal(core, joined[c[1]-window[1]:c[3]-window[1], c[0]-window[0]:c[2]-window[0]]), "Core is not an exact joined crop")

    # Latest handoff baselines first; local committed ownership always wins.
    candidates = {}
    for item in entries(handoff.get("baselineCandidates")) + entries(handoff.get("currentCandidates")):
        require(re.fullmatch(r"r[0-9]{2}_c[0-9]{2}", item.get("tile", "")) is not None, "Invalid candidate tile")
        candidates[item["tile"]] = deepcopy(item)
    for item in entries(previous.get("candidateSet")):
        candidates.setdefault(item["tile"], deepcopy(item))
    for item in entries(previous.get("coupledNeighbors")):
        candidates[item["tile"]] = deepcopy(item)
    candidates[ACTIVE] = {**deepcopy(previous["fragment"]), "tile": ACTIVE}
    candidates[BOTTOM] = {**deepcopy(previous["bottom"]), "tile": BOTTOM}
    require("r08_c09" in candidates and "r09_c09" in candidates, "Missing latest coupled baseline")
    for item in candidates.values():
        checked_ref(item)

    patches = manifest.get("patches", [])
    require(patches and all(p.get("mustApplyTogether") is True for p in patches), "Manifest must contain an indivisible patch set")
    records, parsed, proofs = {}, [], []
    asset_refs = [info(manifest_path), manifest["joined"], review_ref]
    for patch in patches:
        require(patch.get("nativeScale") == 1, "Patch requests resizing")
        tile = patch["destinationTile"]
        require(tile in candidates, f"No current source for destination {tile}")
        destination = box(patch["destinationTileLTRB"], "destinationTileLTRB")
        require(contains([0, 0, TILE_SIZE, TILE_SIZE], destination), "Patch outside tile")
        crop = box(patch["cropFromJoinedLTRB"], "cropFromJoinedLTRB")
        require(contains([0, 0, joined.shape[1], joined.shape[0]], crop), "Asset crop outside joined")
        require((crop[2]-crop[0], crop[3]-crop[1]) == (destination[2]-destination[0], destination[3]-destination[1]), "Patch would require scale")
        active_origin, destination_origin = tile_origin(ACTIVE), tile_origin(tile)
        crop_world = [active_origin[i%2]+window[i%2]+crop[i] for i in range(4)]
        destination_world = [destination_origin[i%2]+destination[i] for i in range(4)]
        require(crop_world == destination_world, "Joined crop and destination refer to different world coordinates")
        asset_path = checked_ref(patch["asset"])
        with Image.open(asset_path) as image:
            asset = np.asarray(image.convert("RGBA")).copy()
        require(np.array_equal(asset, joined[crop[1]:crop[3], crop[0]:crop[2]]), f"Patch is not an exact joined crop: {asset_path}")
        require(np.all(asset[:, :, 3] == 255), "Patch is not opaque native artwork")
        if tile not in records:
            records[tile] = image_record(candidates[tile])
        current_roi = roi(records[tile], destination, allow_missing=True)
        prior = patch.get("requiredPriorSource")
        if prior:
            required = image_record(prior)
            old_roi = roi(required, destination)
            require(np.array_equal(current_roi, old_roi), f"Current source ROI differs from required prior; refuse stale overwrite: {tile} {destination}")
            proofs.append({"tile": tile, "destinationTileLTRB": destination, "currentSource": candidates[tile], "requiredPriorSource": prior, "currentSourceBox": records[tile]["box"], "requiredSourceBox": required["box"], "exactROIEqual": True, "rgbaPixelSha256": hashlib.sha256(current_roi.tobytes()).hexdigest(), "wholeSourcesDifferButROIEquals": prior["sha256"] != candidates[tile]["sha256"], "rollbackToPriorImage": False})
            asset_refs.append(prior)
        else:
            require(np.all(current_roi[:, :, 3] == 0), f"Unconditional new patch would overwrite known native pixels: {tile} {destination}")
            proofs.append({"tile": tile, "destinationTileLTRB": destination, "currentSource": candidates[tile], "allDestinationPixelsPreviouslyMissing": True})
        parsed.append({"tile": tile, "box": destination, "pixels": asset, "specification": patch})
        asset_refs.append(patch["asset"])

    outputs, unchanged = {}, []
    for tile, original in records.items():
        selected = [p for p in parsed if p["tile"] == tile]
        bounds = original["box"].copy()
        for p in selected:
            q = p["box"]
            bounds = [min(bounds[0],q[0]), min(bounds[1],q[1]), max(bounds[2],q[2]), max(bounds[3],q[3])]
        before = roi(original, bounds, allow_missing=True)
        result = before.copy()
        changed_mask = np.zeros(result.shape[:2], dtype=bool)
        for p in selected:
            q = p["box"]
            ys, xs = slice(q[1]-bounds[1],q[3]-bounds[1]), slice(q[0]-bounds[0],q[2]-bounds[0])
            overlap = changed_mask[ys,xs]
            require(np.array_equal(result[ys,xs][overlap], p["pixels"][overlap]), "Conflicting overlapping patches")
            result[ys,xs] = p["pixels"]
            changed_mask[ys,xs] = True
        require(np.array_equal(result[~changed_mask], before[~changed_mask]), "Unchanged pixels were modified")
        outputs[tile] = {"pixels": result, "box": bounds, "beforeCovered": int(np.count_nonzero(before[:,:,3] == 255)), "covered": int(np.count_nonzero(result[:,:,3] == 255))}
        unchanged.append({"tile": tile, "source": candidates[tile], "preservedPixelCount": int((~changed_mask).sum()), "outsidePatchesPixelIdentical": True, "nativeScale": 1})
    require(ACTIVE in outputs, "No active-tile patch in manifest")
    require(sha(checkpoint_path) == checkpoint_ref["sha256"] and sha(handoff_path) == handoff_ref["sha256"], "Ownership changed during validation")
    return {"manifest": manifest, "manifestRef": info(manifest_path), "reviewRef": review_ref, "checkpoint": previous, "checkpointRef": checkpoint_ref, "handoff": handoff, "handoffRef": handoff_ref, "candidates": candidates, "outputs": outputs, "proofs": proofs, "unchanged": unchanged, "assetRefs": asset_refs, "out": output}


def commit(plan):
    out = plan["out"]
    token = uuid.uuid4().hex
    lock_path = TASK / ".commit-manifest.lock"
    # Exclusive create; a stale lock is left for explicit inspection, never stolen.
    lock = lock_path.open("x", encoding="utf-8")
    try:
        lock.write(json.dumps({"version": out.name, "startedAtUtc": now(), "pid": os.getpid()})); lock.flush(); lock.close()
        require(sha(TASK/"source-checkpoint.json") == plan["checkpointRef"]["sha256"], "Checkpoint changed before staging")
        stage = out.parent / ("." + out.name + "-staging-" + token)
        stage.mkdir(parents=True, exist_ok=False)
        future_info = lambda name: {"file": str(out/name), "sha256": sha(stage/name)}
        write(stage/"source-checkpoint-input.json", plan["checkpoint"])
        write(stage/"handoff-input.json", plan["handoff"])
        write(stage/"roi-proofs.json", {"proofs": plan["proofs"], "nativeScale": 1, "olderSourceUsedOnlyForROIVerification": True})
        write(stage/"unchanged-pixels-proof.json", {"tiles": plan["unchanged"]})
        candidates = deepcopy(plan["candidates"])
        modified = {}
        for tile, record in plan["outputs"].items():
            name = tile + ("-fragment.png" if tile == ACTIVE else ".png")
            pixels = record["pixels"]
            image = Image.fromarray(pixels, "RGBA")
            if tile != ACTIVE:
                require(np.all(pixels[:,:,3] == 255), f"External tile has missing pixels: {tile}")
                image = image.convert("RGB")
            image.save(stage/name)
            with Image.open(stage/name) as check:
                require(np.array_equal(np.asarray(check.convert("RGBA")), pixels), "PNG save changed native pixels")
            item = {**candidates[tile], **future_info(name), "tile": tile, "pixels": list(image.size), "nativeScale": 1, "formalAccepted": False, "generationRecord": str(out/(name+".generation.json"))}
            if tile == ACTIVE:
                item["tileLocalLTRB"] = record["box"]
                item["partialFragment"] = True
            candidates[tile] = item
            modified[tile] = item
        candidate_list = [candidates[k] for k in sorted(candidates)]
        candidate_document = {"createdAtUtc": now(), "candidates": candidate_list, "sourcePrecedence": ["handoff.baselineCandidates", "handoff.currentCandidates", "checkpoint.coupledNeighbors", "checkpoint.fragment/bottom", "this reviewed manifest"], "handoffInput": future_info("handoff-input.json"), "priorCheckpoint": future_info("source-checkpoint-input.json"), "formalAccepted": False}
        write(stage/"candidate-set.json", candidate_document)
        active = plan["outputs"][ACTIVE]
        operation = {"createdAtUtc": now(), "operation": "Indivisible native1:1 patch-set placement onto latest owned sources; original pixels outside patches unchanged", "manifest": plan["manifestRef"], "visualReview": plan["reviewRef"], "inputCheckpoint": plan["checkpointRef"], "inputHandoff": plan["handoffRef"], "sourceInputs": [plan["candidates"][k] for k in sorted(plan["outputs"])], "patches": plan["manifest"]["patches"], "outputs": modified, "roiProofs": future_info("roi-proofs.json"), "unchangedPixels": future_info("unchanged-pixels-proof.json"), "candidateSet": future_info("candidate-set.json"), "newMissingPixelsFilledInsideTile": active["covered"]-active["beforeCovered"], "coveredNativeTilePixels": active["covered"], "newModelCalls": 0, "nativeScale": 1, "complete4KTilesAdded": 0, "localAccepted": True, "formalAccepted": False}
        write(stage/"assembly.json", operation)
        for tile, item in modified.items():
            name = Path(item["file"]).name
            write(stage/(name+".generation.json"), {"file": item["file"], "sha256": item["sha256"], "derivedAtUtc": now(), "generatedAt": None, "actualModel": None, "actualQuality": None, "derivedFrom": [plan["candidates"][tile], plan["manifest"]["joined"]], "manifest": plan["manifestRef"], "assembly": future_info("assembly.json"), "newModelCalls": 0, "nativeScale": 1, "operation": "Exact native patch placement, no resize or generation", "formalAccepted": False})
        previous = plan["checkpoint"]
        coupled = {item["tile"]: item for item in entries(previous.get("coupledNeighbors"))}
        for tile, item in modified.items():
            if tile not in (ACTIVE, BOTTOM):
                coupled[tile] = item
        checkpoint = {**deepcopy(previous), "createdAtUtc": now(), "version": out.name, "resumeAuthorizedByUser": True, "sourcePairVerified": True, "fragment": modified[ACTIVE], "bottom": candidates[BOTTOM], "coupledNeighbors": coupled, "baselineSet": future_info("handoff-input.json"), "candidateSet": candidate_list, "candidateSetRecord": future_info("candidate-set.json"), "evidence": [future_info("assembly.json"), plan["reviewRef"], future_info("roi-proofs.json")], "formalAccepted": False, "geometryAndNavigationAcceptance": False, "complete4KTilesAdded": 0}
        write(stage/"source-checkpoint.json", checkpoint)
        canvas = Image.new("RGBA", (TILE_SIZE,TILE_SIZE), (0,0,0,0))
        canvas.paste(Image.fromarray(active["pixels"], "RGBA"), tuple(active["box"][:2]))
        canvas.thumbnail((1024,1024), Image.Resampling.LANCZOS)
        canvas.save(stage/"current-preview.png")
        preview_root = TASK/"current-preview.png"
        preview_record = {"file": str(preview_root), "sha256": sha(stage/"current-preview.png"), "checkpointVersion": out.name, "derivedFrom": [modified[ACTIVE]], "operation": "Progress-only downsample; missing areas transparent; never final artwork", "newModelCalls": 0, "formalAccepted": False}
        write(stage/"current-preview.png.generation.json", preview_record)
        native_calls = len(list(TASK.rglob("native.png.generation.json")))
        progress = read(TASK/"progress.json") if (TASK/"progress.json").exists() else {}
        progress.update(updatedAtUtc=now(), appearance="tianyong_festival", status="native_expansion_in_progress", targetTiles=256, activeTile=ACTIVE, checkpointVersion=out.name, nativeCallsInThisTask=native_calls, newCompleteTileCount=0, complete4KTilesAdded=0, formalAccepted=False, wholeCityComplete=False, clientAccepted=False, currentFragmentPixels=[active["pixels"].shape[1],active["pixels"].shape[0]], currentFragmentTileLocalLTRB=active["box"], coveredNativeTilePixels=active["covered"], tileCoverageFraction=active["covered"]/(TILE_SIZE*TILE_SIZE), sourceCheckpoint=str(TASK/"source-checkpoint.json"), currentPreview=str(preview_root), candidateSet=str(out/"candidate-set.json"), nextAction="Continue adjacent missing native patch and review every affected return.")
        write(stage/"progress.json", progress)
        if (TASK/"current-work.json").exists():
            write(stage/"previous-current-work.json", read(TASK/"current-work.json"))
        write(stage/"current-work.json", {**progress, "lastCommittedManifest": plan["manifestRef"], "lastCommit": str(out/"assembly.json")})
        # Revalidate all inputs before making this version visible. A prior source
        # may differ from current globally, but its exact ROI proof is mandatory.
        for ref in plan["assetRefs"] + list(plan["candidates"].values()):
            checked_ref(ref)
        require(sha(TASK/"source-checkpoint.json") == plan["checkpointRef"]["sha256"] and sha(TASK/"handoff.json") == plan["handoffRef"]["sha256"], "Sources changed during staging; staged evidence retained without pointer switch")
        require(not out.exists(), "Version appeared during staging")
        # Prepare root files before promoting the version. Checkpoint is the final
        # commit marker; consumers must use the version it references.
        names = ["current-preview.png", "current-preview.png.generation.json", "progress.json", "current-work.json", "source-checkpoint.json"]
        pending = {}
        for name in names:
            tmp = TASK/("."+name+"-"+token+".pending")
            with tmp.open("xb") as stream:
                stream.write((stage/name).read_bytes())
            pending[name] = tmp
        os.replace(stage, out)
        for name in names:
            os.replace(pending[name], TASK/name)
        require(sha(TASK/"source-checkpoint.json") == sha(out/"source-checkpoint.json"), "Checkpoint publication failed")
        print(json.dumps({"version": out.name, "sourceCheckpoint": info(TASK/"source-checkpoint.json"), "candidateSet": info(out/"candidate-set.json"), "newPixels": operation["newMissingPixelsFilledInsideTile"], "coveredPixels": active["covered"], "nativeCallsInThisTask": native_calls, "complete4KTilesAdded": 0, "formalAccepted": False}, ensure_ascii=False))
    finally:
        if not lock.closed:
            lock.close()
        lock_path.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("version")
    parser.add_argument("--checkpoint-sha", required=True)
    parser.add_argument("--validate-only", action="store_true", help="Check all pixel/source conditions without writing anything")
    args = parser.parse_args()
    plan = build_plan(args.manifest, args.version, args.checkpoint_sha)
    if args.validate_only:
        print(json.dumps({"valid": True, "writesPerformed": False, "output": str(plan["out"]), "modifiedTiles": list(plan["outputs"]), "roiProofs": plan["proofs"], "checkpoint": plan["checkpointRef"]}, ensure_ascii=False))
    else:
        commit(plan)


if __name__ == "__main__":
    main()
