"""Compose four native festival repairs using the exact day integration masks.

No generation, seam optimization, registration, resampling, or automatic acceptance.
--validate-only reads all dependencies without writes. --compose writes only beneath
this appearance's r08_c11/west-repaired directory, and never publishes selection.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
DAY = ROOT.parent / "donghai_day"
TILE = ROOT / "r08_c11"
NATIVE = TILE / "repairs/west-common-edge/native"
DEST = TILE / "west-repaired"
OUT, QA, MASKS = DEST / "output", DEST / "qa", DEST / "masks"
EAST = TILE / "internal-repaired/output/r08_c11.png"
EAST_MANIFEST = EAST.parent / "internal-integration-manifest.json"
DAY_MANIFEST = DAY / "tiles/west-integration-manifest.json"
DAY_MANIFEST_SHA = "8e567ea69e365723e98fe607a2c33463550ac7857a49cd34b782a31bb9cce620"
STARTS = (0, 1024, 2048, 2842)
X0, X1, PATCH, H, W, EDGE = 3469, 4723, 1254, 4096, 8192, 150
ORIGIN = (36864, 28672)
EXPECTED_PARAMETERS = {
    "pairPixels": [W, H], "stripPixels": [PATCH, H],
    "stripPairRectXYXY": [X0, 0, X1, H], "patchYStarts": list(STARTS),
    "longitudinalOverlaps": [230, 230, 460], "insertionOverlapEachSidePixels": EDGE,
    "transitionWidthPixels": 2,
    "order": "top-to-bottom strip, then left and right insertion seams",
    "registration": False, "colorCorrection": False, "imageBlur": False,
    "maskBlur": False, "spatialResampling": False, "noUpscaling": True,
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def same(a, b):
    return Path(a).resolve() == Path(b).resolve()


def check(path, digest):
    require(Path(path).is_file() and sha(path) == digest, f"Missing or changed source: {path}")


def info(path):
    return {"file": str(Path(path).resolve()), "sha256": sha(path)}


def writable(path):
    path = Path(path).resolve()
    require(path.is_relative_to(DEST.resolve()), f"Write escapes own destination: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_json(path, data):
    writable(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rgb(path, size):
    with Image.open(path) as image:
        image.load()
        require(image.format == "PNG" and image.size == size, f"Wrong PNG dimensions: {path}")
        require(image.mode in ("RGB", "RGBA"), f"Wrong PNG mode: {path}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), f"Transparent ground source: {path}")
        return np.asarray(image.convert("RGB")).copy()


def save_image(path, pixels, metadata):
    image = Image.fromarray(pixels) if isinstance(pixels, np.ndarray) else pixels
    image.save(writable(path))
    result = {**info(path), "pixels": list(image.size)}
    save_json(str(path) + ".generation.json", {
        **result, "generatedByAI": False, "operation": "native pixel mechanical composition/crop",
        "resized": False, "artUpscaled": False, "formalAccepted": False, **metadata,
    })
    return {**result, "generationRecord": str(path) + ".generation.json"}


def load_day_contract():
    path = DAY_MANIFEST
    if not path.is_file() or sha(path) != DAY_MANIFEST_SHA:
        path = DAY / "r08_c11/repairs/west-leaf-01/previous-west-integration-manifest.json"
    check(path, DAY_MANIFEST_SHA)
    manifest = read(path)
    require(manifest["parameters"] == EXPECTED_PARAMETERS, "Day geometry/composition contract changed")
    require(not manifest["parameters"]["registration"], "Geometry flow requires explicit exact-field implementation")
    expected = {
        "strip-s1-s2": ("horizontal", [X0, 1024, X1, 1254]),
        "strip-s2-s3": ("horizontal", [X0, 2048, X1, 2278]),
        "strip-s3-s4": ("horizontal", [X0, 2842, X1, 3302]),
        "insert-left": ("vertical", [X0, 0, X0 + EDGE, H]),
        "insert-right": ("vertical", [X1 - EDGE, 0, X1, H]),
    }
    masks, entries = {}, []
    require({s["id"] for s in manifest["seams"]} == set(expected), "Wrong day seam set")
    for seam in manifest["seams"]:
        name = seam["id"]
        orientation, rect = expected[name]
        require(seam["orientation"] == orientation and seam["pairOverlapRectXYXY"] == rect, f"Wrong mask rect: {name}")
        for key in ("maskNpz", "maskPng"):
            check(seam[key]["file"], seam[key]["sha256"])
        with np.load(seam["maskNpz"]["file"], allow_pickle=False) as archive:
            require(set(archive.files) == {"alpha_u8", "seam_offsets", "pair_rect_xyxy", "transition_pixels"}, f"Unknown geometry field: {name}")
            alpha = archive["alpha_u8"].copy()
            offsets = archive["seam_offsets"].copy()
            require(archive["pair_rect_xyxy"].tolist() == rect and int(archive["transition_pixels"]) == 2, f"Invalid mask metadata: {name}")
        with Image.open(seam["maskPng"]["file"]) as im:
            require(np.array_equal(np.asarray(im), alpha), f"NPZ/PNG mask mismatch: {name}")
        require(alpha.dtype == np.uint8 and alpha.shape == (rect[3]-rect[1], rect[2]-rect[0]), f"Wrong alpha size: {name}")
        oriented = alpha if orientation == "vertical" else alpha.T
        require(offsets.shape == (oriented.shape[0],) and np.all(np.abs(np.diff(offsets)) <= 1), f"Invalid path: {name}")
        distance = np.arange(oriented.shape[1])[None, :] - offsets[:, None]
        reconstructed = np.where(distance <= -2, 0, np.where(distance == -1, 64, np.where(distance == 0, 191, 255))).astype(np.uint8)
        require(np.array_equal(oriented, reconstructed), f"Unexpected blend parameters: {name}")
        masks[name] = alpha
        entries.append({"id": name, "orientation": orientation, "pairOverlapRectXYXY": rect,
                        "sourceMaskNpz": seam["maskNpz"], "sourceMaskPng": seam["maskPng"],
                        "identicalDayAlpha": True, "transitionPartialPixels": 2,
                        "maskMeaning": "0 keeps earlier input; 255 takes later input; 64/191 integer blends",
                        "newSeamOptimization": False})
    return manifest, info(path), masks, entries


def load_inputs(day):
    handoff_path = ROOT / "handoff.json"
    west = [b for b in read(handoff_path)["baselineCandidates"] if b["tile"] == "r08_c10"]
    require(len(west) == 1, "Need one pinned c10 baseline")
    west = west[0]
    check(west["file"], west["sha256"])
    em = read(EAST_MANIFEST)
    east = em["candidate"]
    require(same(east["file"], EAST) and em["completePixelCandidate"] is True, "Internal-repaired candidate incomplete")
    check(EAST, east["sha256"])
    check(east["sidecar"], east["sidecarSha256"])
    er = read(east["sidecar"])
    require(er["sha256"] == east["sha256"], "East sidecar hash mismatch")
    baselines = [{**info(west["file"]), "tile": "r08_c10", "record": info(handoff_path)},
                 {**info(EAST), "tile": "r08_c11", "record": info(EAST_MANIFEST), "generationRecord": info(east["sidecar"])}]
    pair = np.concatenate((rgb(west["file"], (H, H)), rgb(EAST, (H, H))), axis=1)
    patches, entries = [], []
    day_sources = {p["id"]: p for p in day["nativeRepairSources"]}
    for index, y in enumerate(STARTS, 1):
        name, path = f"s{index}", NATIVE / f"s{index}.png"
        record_path = Path(str(path) + ".generation.json")
        record = read(record_path)
        check(path, record["sha256"])
        require(same(record["file"], path) and [record["width"], record["height"]] == [PATCH, PATCH], f"Wrong native record: {name}")
        require(record["tool"] == "image_gen.imagegen" and record["route"] == "builtin", f"Wrong route: {name}")
        require(record["resizedAfterGeneration"] is False and record["finalArtUpscaled"] is False, f"Resampled source: {name}")
        require(record["globalRectXYWH"] == [ORIGIN[0]+X0, ORIGIN[1]+y, PATCH, PATCH], f"Wrong geometry coordinates: {name}")
        refs, submitted = record["references"], record["submittedParameters"]
        require(len(refs) >= 3 and len(refs) == len(submitted["referenced_image_paths"]), f"References missing: {name}")
        for reference, actual in zip(refs, submitted["referenced_image_paths"]):
            require(same(reference["file"], actual), f"Reference order mismatch: {name}")
            check(reference["file"], reference["sha256"])
        geometry = day_sources[name]
        require(same(refs[0]["file"], geometry["file"]) and refs[0]["sha256"] == geometry["sha256"], f"Different day geometry source: {name}")
        match = record["geometryMatchedTo"]
        require(same(match["file"], geometry["file"]) and match["sha256"] == geometry["sha256"], f"Geometry bind mismatch: {name}")
        require(all(submitted.get(k, "missing") is None for k in ("model", "quality")) and
                all(record.get(k, "missing") is None for k in ("actualModel", "actualQuality")), f"Unsupported selector claim: {name}")
        evidence = record["evidence"]
        require(evidence["toolResultSha256"] == record["sha256"], f"Tool/native identity mismatch: {name}")
        raw = Path(evidence["toolResultSourcePath"])
        check(raw, record["sha256"])
        prompt = Path(record["prompt"]).read_text(encoding="utf-8-sig").strip()
        require(prompt == submitted["prompt"].strip(), f"Prompt submission mismatch: {name}")
        entries.append({"id": name, **info(path), "record": info(record_path),
                        "dayGeometry": {"file": geometry["file"], "sha256": geometry["sha256"]},
                        "toolResult": info(raw), "references": refs,
                        "submittedModel": None, "submittedQuality": None, "actualModel": None, "actualQuality": None,
                        "pairRectXYXY": [X0, y, X1, y+PATCH], "sourceResampled": False})
        patches.append(rgb(path, (PATCH, PATCH)))
    return pair, baselines, patches, entries


def blend(a, b, alpha):
    require(a.shape == b.shape and a.shape[:2] == alpha.shape, "Blend array dimensions differ")
    weight = alpha.astype(np.uint32)[..., None]
    result = ((a.astype(np.uint32)*(255-weight) + b.astype(np.uint32)*weight + 127)//255).astype(np.uint8)
    require(np.array_equal(result[alpha == 0], a[alpha == 0]) and np.array_equal(result[alpha == 255], b[alpha == 255]), "Blend altered exact input regions")
    return result


def compose(base, patches, masks):
    strip = patches[0].copy()
    for i in range(1, 4):
        overlap = len(strip) - STARTS[i]
        require(overlap == (230 if i < 3 else 460), "Wrong strip overlap")
        middle = blend(strip[-overlap:], patches[i][:overlap], masks[f"strip-s{i}-s{i+1}"])
        strip = np.concatenate((strip[:-overlap], middle, patches[i][overlap:]), axis=0)
    require(strip.shape == (H, PATCH, 3), "Wrong final strip dimensions")
    result = base.copy()
    result[:, X0:X1] = strip
    result[:, X0:X0+EDGE] = blend(base[:, X0:X0+EDGE], strip[:, :EDGE], masks["insert-left"])
    result[:, X1-EDGE:X1] = blend(strip[:, -EDGE:], base[:, X1-EDGE:X1], masks["insert-right"])
    require(np.array_equal(base[:, :X0], result[:, :X0]) and np.array_equal(base[:, X1:], result[:, X1:]), "Changed pixels outside repair")
    return result


def write_qa(pair, sources):
    image, items = Image.fromarray(pair), []
    def crop(name, rect, **extra):
        metadata = {"derivedFrom": sources, "pairRectXYXY": list(rect), "pixelScale": 1,
                    "visualInspection": "pending", **extra}
        items.append({**save_image(QA / f"{name}.png", image.crop(rect), metadata), **metadata})
    def vertical(name, center, width):
        rect = [center-width//2, 0, center+width//2, H]
        sheet = Image.new("RGB", (4*width, 1024))
        pieces = []
        for i in range(4):
            source = [rect[0], i*1024, rect[2], (i+1)*1024]
            sheet.paste(image.crop(source), (i*width, 0))
            pieces.append({"pairRectXYXY": source, "sheetOriginXY": [i*width, 0]})
        metadata = {"derivedFrom": sources, "pairRectXYXY": rect, "pieces": pieces,
                    "coveredLengthPixels": H, "pixelScale": 1, "resized": False,
                    "montageDividersAreNotArtSeams": True, "visualInspection": "pending"}
        items.append({**save_image(QA / f"{name}.png", sheet, metadata), **metadata})
    vertical("common-edge-full", 4096, 256)
    vertical("attachment-left-full", X0+EDGE//2, 384)
    vertical("attachment-right-full", X1-EDGE//2, 384)
    for index in range(1, 4):
        y, overlap = STARTS[index], (230 if index < 3 else 460)
        crop(f"strip-s{index}-s{index+1}", (X0-128, y-32, X1+128, y+overlap+32))
    for side, x in (("left", X0), ("right", X1)):
        crop(f"corner-{side}-top", (x-256, 0, x+256, 512))
        crop(f"corner-{side}-bottom", (x-256, H-512, x+256, H))
    crop("attachment-top-full", (X0, 0, X1, 256), outerNeighborPresent=False,
         limitation="Full changed top boundary on this pair only; north neighboring tiles not supplied")
    crop("attachment-bottom-full", (X0, H-256, X1, H), outerNeighborPresent=False,
         limitation="Full changed bottom boundary on this pair only; south neighboring tiles not supplied")
    crop("day-leaf-residual-focus", (3968, 1952, 4224, 2352),
         purpose="Inspect known old day WEST-LEAF-01 location; later day leaf edit is not part of four native festival sources")
    return items


def day_review_status():
    path = DAY / "r08_c11/repairs/west-common-edge/integration-qa/integration-review.json"
    review = read(path)
    status = {"originalFourPatchReview": {**info(path), "result": review["result"],
               "formalAccepted": review["formalAccepted"], "issues": review["issues"]},
              "doesNotEstablishFestivalVisualAcceptance": True}
    newer = DAY / "tiles/west-leaf-repair-manifest.json"
    if newer.is_file():
        leaf = read(newer)
        status["laterDayLeafRepair"] = {**info(newer), "formalAccepted": leaf["formalAccepted"],
            "pairRectXYXY": leaf["pairRectXYXY"], "generatedEdit": leaf["generatedEdit"],
            "notIncludedInThisFourPatchFestivalConversion": True,
            "visualReviewAfterLeafEdit": "No new review verified by this script"}
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--compose", action="store_true")
    args = parser.parse_args()
    day, contract, masks, seam_entries = load_day_contract()
    base, baselines, patches, sources = load_inputs(day)
    status = day_review_status()
    if args.validate_only:
        print(json.dumps({"nativeRepairs": len(patches), "exactDayMasks": len(masks), "writes": 0,
                          "baselines": baselines, "dayQA": status}, ensure_ascii=False, indent=2))
        return
    result = compose(base, patches, masks)
    dependencies = baselines + sources
    outputs = []
    for name, array, rect in (
        ("pair-r08_c10-c11", result, [0, 0, W, H]),
        ("r08_c10", result[:, :H], [0, 0, H, H]),
        ("r08_c11", result[:, H:], [H, 0, W, H]),
    ):
        path = OUT / f"{name}.png"
        saved = save_image(path, array, {"derivedFrom": dependencies, "pairRectXYXY": rect,
                           "globalOriginXY": list(ORIGIN), "dayGeometryContract": contract,
                           "artResampled": False, "colorCorrection": False, "visualReview": "pending"})
        require(np.array_equal(rgb(path, (array.shape[1], array.shape[0])), array), f"Saved pixels differ: {name}")
        outputs.append({"id": name, **saved, "pairRectXYXY": rect})
    for seam in seam_entries:
        for source_key, dest_key, suffix in (("sourceMaskNpz", "appliedMaskNpz", "npz"), ("sourceMaskPng", "appliedMaskPng", "png")):
            source = seam[source_key]
            path = MASKS / f"{seam['id']}.{suffix}"
            shutil.copyfile(source["file"], writable(path))
            check(path, source["sha256"])
            seam[dest_key] = info(path)
        save_json(MASKS / f"{seam['id']}.json", seam)
    qa = write_qa(result, outputs)
    for source in dependencies:
        check(source["file"], source["sha256"])
    manifest = {
        "createdAtUtc": datetime.now(timezone.utc).isoformat(), "appearance": "donghai_lantern",
        "status": "complete-pixel-candidates-pending-visual-review", "formalAccepted": False,
        "clientAcceptance": False, "wholeCityComplete": False, "selectionUpdated": False,
        "script": info(__file__), "dayGeometryContract": contract, "dayQA": status,
        "baselines": baselines, "nativeRepairSources": sources, "parameters": EXPECTED_PARAMETERS,
        "seams": seam_entries, "geometryFlow": {"applied": False, "reason": "Pinned day integration uses no flow or registration"},
        "colorCorrectionField": {"applied": False, "maximumAbsoluteDelta": 0, "fieldFile": None},
        "outputs": outputs, "sourceByteHashesUnchanged": True,
        "pixelVerification": {"outsideRepairExactlyIdentical": True, "outsideRepairChangedPixels": 0,
            "authorizedPairRectXYXY": [X0, 0, X1, H],
            "changedPixelsInsideRepair": int(np.count_nonzero(np.any(base[:, X0:X1] != result[:, X0:X1], axis=2))),
            "c10UnchangedOutsideLocalXYXY": [X0, 0, H, H], "c11UnchangedOutsideLocalXYXY": [0, 0, X1-H, H],
            "savedPNGPixelsExactlyEqualComputedCandidate": True},
        "qa": qa, "qaCoverage": {"commonEdgeLength": H, "leftAndRightFullAttachments": True,
            "topAndBottomFullChangedBoundaries": True, "outerNorthSouthNeighborsInspected": False,
            "horizontalOverlapBands": 3, "corners": 4, "knownDayLeafFocus": True,
            "pixelScale": 1, "inspectionStatus": "pending"},
    }
    save_json(OUT / "west-integration-manifest.json", manifest)
    save_json(QA / "manifest.json", {"outputs": outputs, "qa": qa, "coverage": manifest["qaCoverage"]})
    print(json.dumps({"outputs": outputs, "manifest": str(OUT / "west-integration-manifest.json"),
                      "visualInspection": "pending", "formalAccepted": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
