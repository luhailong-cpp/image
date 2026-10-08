"""Replay day seam ownership on lantern native patches, without color adjustment.

Only shared-assembly/output and shared-assembly/qa receive derived files. Import
validate_inputs(), load_day_masks(), assemble(), blend(), and write_outputs()
for later scoped experiments. assemble(overlap_transform=...) accepts a hook
returning (existing_overlap, incoming_overlap, JSON_metadata); the CLI never
supplies this hook. Exact shared masks preserve source ownership, not proof that
an AI edit retained every contour. Visual geometry and color QA remain required.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DAY = ROOT.parent / "donghai_day"
TILE = ROOT / "r08_c13"
BASE = TILE / "shared-assembly"
OUT, QA = BASE / "output", BASE / "qa"
DAY_MANIFEST = DAY / "r08_c13/output/assembly-manifest.json"
DAY_MASKS = DAY / "r08_c13/qa/assembly-masks"
CORE, HALO, PATCH, OVERLAP, EXTENDED, FINAL = 1024, 115, 1254, 230, 4326, 4096


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_path(first, second):
    return Path(first).resolve() == Path(second).resolve()


def load_helpers():
    """Reuse existing QA writers without changing their file or output files."""
    path = ROOT / "r08_c13/assemble_c13_native.py"
    spec = importlib.util.spec_from_file_location("lantern_c13_core_qa_helpers", path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    # In-memory configuration only. The source module remains untouched.
    module.OUTPUT, module.QA = OUT, QA
    return module


def load_rgb(path, expected_hash, expected_size):
    data = Path(path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected_hash, f"SHA mismatch: {path}")
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        require(image.size == expected_size and image.mode in ("RGB", "RGBA"), f"Invalid native image: {path}")
        if image.mode == "RGBA":
            require(image.getchannel("A").getextrema() == (255, 255), f"Non-opaque image: {path}")
        return np.asarray(image.convert("RGB")).copy()


def validate_inputs():
    """Return lantern arrays, day arrays and immutable evidence for all 16."""
    manifest_hash = sha(DAY_MANIFEST)
    preflight = read(TILE / "qa/assembly-preflight.json")
    require(manifest_hash == preflight["dayManifest"]["sha256"], "Day manifest changed from the reviewed c13 geometry contract")
    manifest = read(DAY_MANIFEST)
    cleanup_path = ROOT / "audit/duplicate-cache-cleanup.json"
    cleanup = read(cleanup_path)
    cleanup_entries = {str(Path(e["recordFile"]).resolve()): e for e in cleanup["entries"] if e.get("status") == "deleted"}
    require(manifest["parameters"]["order"] == "assemble each row left-to-right, then rows top-to-bottom", "Unknown day assembly order")
    for key in ("registration", "colorCorrection", "spatialResampling", "imageBlur", "maskBlur"):
        require(manifest["parameters"][key] is False, f"Unsupported day geometry/processing field: {key}")
    require(manifest["parameters"]["globalRectXYWH"] == [49152, 28672, 4096, 4096], "Wrong day tile coordinates")
    require(manifest["coverage"]["fullCoverage"] is True, "Day source coverage incomplete")
    for key, expected in {"core": CORE, "halo": HALO, "overlap": OVERLAP, "patchPixels": [PATCH, PATCH], "extendedPixels": [EXTENDED, EXTENDED], "cropXYXY": [115, 115, 4211, 4211]}.items():
        require(manifest["parameters"][key] == expected, f"Day parameter mismatch: {key}")
    day_entries = {entry["id"]: entry for entry in manifest["nativeSources"]}
    require(len(day_entries) == 16, "Day manifest requires 16 distinct native sources")
    arrays, day_arrays, entries = {}, {}, []
    for row in range(1, 5):
        for column in range(1, 5):
            name = f"r{row:02}_c{column:02}"
            path = TILE / "native" / f"{name}.png"
            record_path = Path(str(path) + ".generation.json")
            record = read(record_path)
            require(same_path(record["file"], path), f"Lantern record path mismatch: {name}")
            require(record["width"] == PATCH and record["height"] == PATCH, f"Wrong recorded dimensions: {name}")
            require(record.get("route") == "builtin" and record.get("resizedAfterGeneration") is False, f"Missing native built-in evidence: {name}")
            require(record.get("finalArtUpscaled") is not True, f"Upscaled source: {name}")
            arrays[row, column] = load_rgb(path, record["sha256"], (PATCH, PATCH))
            require(record.get("evidence", {}).get("toolResultSha256", record.get("evidence", {}).get("sha256")) == record["sha256"], f"Tool result hash mismatch: {name}")
            raw = record.get("evidence", {}).get("toolResultSourcePath")
            require(isinstance(raw, str) and raw, f"Missing actual tool path: {name}")
            if Path(raw).is_file():
                require(sha(raw) == record["sha256"], f"Available tool-result bytes differ: {name}")
                raw_evidence = {"status": "present-and-byte-identical"}
            else:
                deleted = cleanup_entries.get(str(record_path.resolve()))
                require(deleted is not None, f"Missing tool cache without recorded retention cleanup: {name}")
                require(same_path(deleted["originalToolResultSourcePath"], raw), f"Cleanup original path differs: {name}")
                require(same_path(deleted["nativeFile"], path), f"Cleanup retained path differs: {name}")
                require(all(deleted[key] == record["sha256"] for key in ("verifiedNativeSha256", "verifiedCacheSha256", "retainedNativeSha256AfterDeletion")), f"Cleanup byte-identity proof differs: {name}")
                require(deleted["retainedRecordSha256AfterDeletion"] == sha(record_path), f"Record changed since cache cleanup: {name}")
                raw_evidence = {"status": "byte-identical-cache-deleted-under-retention-policy", "auditFile": str(cleanup_path), "auditSha256": sha(cleanup_path), "deletedAtUtc": deleted["deletedAtUtc"], "receiptRecreated": False}
            refs, submitted = record["references"], record["submittedParameters"]
            require(len(refs) == len(submitted["referenced_image_paths"]) and len(refs) >= 3, f"Incomplete actual references: {name}")
            for ref, actual_path in zip(refs, submitted["referenced_image_paths"]):
                require(same_path(ref["file"], actual_path) and sha(ref["file"]) == ref["sha256"], f"Changed/unsubmitted reference: {name}")
            require(all(submitted.get(key, "missing") is None for key in ("model", "quality")), f"Unexpected model/quality selector claim: {name}")
            require(all(record.get(key, "missing") is None for key in ("actualModel", "actualQuality")), f"Unexpected actual model/quality claim: {name}")
            require(sha(record["prompt"]) == record["promptSha256"], f"Prompt changed after generation: {name}")
            day_path = DAY / "r08_c13/native" / f"{name}.png"
            geometry = record["geometryMatchedTo"]
            require(same_path(geometry["file"], day_path), f"Wrong day geometry coordinate: {name}")
            day_entry = day_entries[name]
            require(same_path(day_entry["file"], day_path) and geometry["sha256"] == day_entry["sha256"], f"Day source differs from assembly manifest: {name}")
            day_arrays[row, column] = load_rgb(day_path, geometry["sha256"], (PATCH, PATCH))
            day_record_path = Path(str(day_path) + ".generation.json")
            require(same_path(day_entry["recordFile"], day_record_path) and sha(day_record_path) == day_entry["recordSha256"], f"Day sidecar changed since assembly: {name}")
            day_record = read(day_record_path)
            require(day_record["sha256"] == geometry["sha256"], f"Day generation hash mismatch: {name}")
            require(record["references"] and same_path(record["references"][0]["file"], day_path) and record["references"][0]["sha256"] == geometry["sha256"], f"Primary day reference mismatch: {name}")
            require(same_path(record["submittedParameters"]["referenced_image_paths"][0], day_path), f"Submitted primary reference mismatch: {name}")
            entries.append({"id": name, "file": str(path), "sha256": record["sha256"], "pixels": [PATCH, PATCH],
                            "recordFile": str(record_path), "recordSha256": sha(record_path),
                            "dayGeometry": {"file": str(day_path), "sha256": geometry["sha256"], "recordFile": str(day_record_path), "recordSha256": sha(day_record_path)},
                            "extendedRectXYWH": [(column - 1) * CORE, (row - 1) * CORE, PATCH, PATCH],
                            "sourceResized": False, "geometryVisuallyAccepted": False,
                            "toolResultSourcePath": raw, "toolResultAvailable": Path(raw).is_file(),
                            "toolResultAvailabilityEvidence": raw_evidence,
                            "allActualReferenceHashesVerified": True,
                            "submittedModel": None, "submittedQuality": None, "actualModel": None, "actualQuality": None})
    require(sha(DAY_MANIFEST) == manifest_hash, "Day manifest changed during validation; rerun against a stable snapshot")
    return arrays, day_arrays, entries, manifest, manifest_hash


def load_day_masks(manifest):
    """Validate PNG+NPZ hashes and exact alpha orientation from the day manifest."""
    expected = {}
    for row in range(1, 5):
        for column in range(2, 5):
            expected[f"vertical_r{row:02}_c{column-1:02}_c{column:02}"] = ("vertical", [(column - 1) * CORE, (row - 1) * CORE, OVERLAP, PATCH], (PATCH, OVERLAP))
    for row in range(2, 5):
        expected[f"horizontal_r{row-1:02}_r{row:02}"] = ("horizontal", [0, (row - 1) * CORE, EXTENDED, OVERLAP], (OVERLAP, EXTENDED))
    seams = {item["id"]: item for item in manifest["seams"]}
    require(set(seams) == set(expected), "Day mask label set differs from required 15 seams")
    masks, evidence = {}, []
    for label, (orientation, rect, shape) in expected.items():
        entry = seams[label]
        require(entry["orientation"] == orientation and entry["overlapRectExtendedXYWH"] == rect, f"Mask coordinate mismatch: {label}")
        png, npz = Path(entry["maskPng"]["file"]), Path(entry["maskNpz"]["file"])
        require(png.resolve().is_relative_to(DAY_MASKS.resolve()) and npz.resolve().is_relative_to(DAY_MASKS.resolve()), f"Mask outside day mask directory: {label}")
        require(sha(png) == entry["maskPng"]["sha256"] and sha(npz) == entry["maskNpz"]["sha256"], f"Mask hash mismatch: {label}")
        with Image.open(png) as image:
            image.load()
            require(image.mode == "L", f"Mask is not an 8-bit grayscale PNG: {label}")
            alpha_png = np.asarray(image).copy()
        with np.load(npz, allow_pickle=False) as archive:
            alpha = archive["alpha_u8"].copy()
            offsets = archive["seam_offsets"].copy()
            require(archive["overlap_rect_extended_xywh"].tolist() == rect and int(archive["transition_width_pixels"]) == 2, f"NPZ metadata mismatch: {label}")
        require(alpha.dtype == np.uint8 and alpha.shape == shape and np.array_equal(alpha, alpha_png), f"Mask bytes/orientation mismatch: {label}")
        require(set(np.unique(alpha)).issubset({0, 64, 191, 255}), f"Unexpected mask values: {label}")
        distance = np.arange(OVERLAP)[None, :] - offsets[:, None]
        recreated = np.where(distance <= -2, 0, np.where(distance == -1, 64, np.where(distance == 0, 191, 255))).astype(np.uint8)
        if orientation == "horizontal":
            recreated = recreated.T
        require(np.array_equal(alpha, recreated), f"Mask does not match recorded day seam offsets: {label}")
        masks[label] = alpha
        evidence.append({"id": label, "orientation": orientation, "overlapRectExtendedXYWH": rect,
                         "maskPng": entry["maskPng"], "maskNpz": entry["maskNpz"], "shapeHW": list(shape),
                         "exactDayAlphaReused": True, "maskMeaning": entry["maskMeaning"]})
    count_info = manifest["coverage"]["countMask"]
    require(sha(count_info["file"]) == count_info["sha256"], "Day source-coverage mask hash mismatch")
    expected_count = np.zeros((EXTENDED, EXTENDED), np.uint8)
    for row in range(4):
        for column in range(4):
            expected_count[row*CORE:row*CORE+PATCH, column*CORE:column*CORE+PATCH] += 1
    with Image.open(count_info["file"]) as image:
        require(np.array_equal(np.asarray(image), expected_count), "Day source coverage differs from exact 16 native rectangles")
    return masks, evidence


def blend(existing, incoming, alpha):
    require(existing.shape == incoming.shape and existing.shape[:2] == alpha.shape, "Blend orientation/dimensions mismatch")
    weight = alpha.astype(np.uint32)[..., None]
    return ((existing.astype(np.uint32) * (255 - weight) + incoming.astype(np.uint32) * weight + 127) // 255).astype(np.uint8)


def append_with_mask(base, incoming, alpha, label, orientation, overlap_transform=None):
    """Return combined pixels and optional transform evidence; never resample."""
    if orientation == "vertical":
        existing, new = base[:, -OVERLAP:], incoming[:, :OVERLAP]
    else:
        existing, new = base[-OVERLAP:, :], incoming[:OVERLAP, :]
    detail = {"id": label, "orientation": orientation, "colorAdjustment": False}
    if overlap_transform is not None:
        original_shape = existing.shape
        existing, new, transform_info = overlap_transform(existing.copy(), new.copy(), alpha.copy(), label, orientation)
        require(existing.shape == new.shape == original_shape and existing.dtype == new.dtype == np.uint8, "Overlap transform changed dimensions/dtype")
        detail.update(colorAdjustment=True, transform=transform_info)
    mixed = blend(existing, new, alpha)
    if orientation == "vertical":
        result = np.concatenate((base[:, :-OVERLAP], mixed, incoming[:, OVERLAP:]), axis=1)
    else:
        result = np.concatenate((base[:-OVERLAP, :], mixed, incoming[OVERLAP:, :]), axis=0)
    return result, detail


def assemble(arrays, masks, overlap_transform=None):
    rows, operations = [], []
    for row in range(1, 5):
        combined = arrays[row, 1]
        for column in range(2, 5):
            label = f"vertical_r{row:02}_c{column-1:02}_c{column:02}"
            combined, info = append_with_mask(combined, arrays[row, column], masks[label], label, "vertical", overlap_transform)
            operations.append(info)
        require(combined.shape == (PATCH, EXTENDED, 3), "Wrong row assembly dimensions")
        rows.append(combined)
    combined = rows[0]
    for row in range(2, 5):
        label = f"horizontal_r{row-1:02}_r{row:02}"
        combined, info = append_with_mask(combined, rows[row-1], masks[label], label, "horizontal", overlap_transform)
        operations.append(info)
    require(combined.shape == (EXTENDED, EXTENDED, 3), "Incomplete extended canvas")
    return combined, operations


def export_wide_qa(helpers, candidate, core):
    results = []
    for axis in ("x", "y"):
        for boundary in (1024, 2048, 3072):
            for part in range(4):
                box = ((boundary - 256, part * 1024, boundary + 256, (part + 1) * 1024) if axis == "x" else
                       (part * 1024, boundary - 256, (part + 1) * 1024, boundary + 256))
                results.append(helpers.save_image(QA / f"{axis}{boundary}-wide512-part{part+1:02}.png", core.crop(box), {
                    "operation": "native 512-wide full-path-and-return QA segment", "finalArt": False,
                    "derivedFrom": [candidate], "crops": [helpers.source_crop(candidate, box, (0, 0))],
                    "coveredLengthPixels": 1024, "combinedFourSegmentsLength": 4096,
                    "bandWidthPixels": 512, "resized": False, "rotated": False,
                    "inspectionScope": "All four segments together cover the full seam and both sides of the shared 230-pixel overlap",
                }))
    return results


def write_outputs(combined, entries, mask_evidence, manifest_hash, operations, replay_verified):
    helpers = load_helpers()
    west, west_info = helpers.load_west()
    extended = Image.fromarray(combined)
    core = extended.crop((115, 115, 4211, 4211))
    provenance = {"operation": "Exact day seam alpha applied to matching lantern native sources",
                  "derivedFrom": entries, "dayMasks": mask_evidence,
                  "dayManifest": {"file": str(DAY_MANIFEST), "sha256": manifest_hash},
                  "completePixelCandidate": True, "finalArt": False, "artResampled": False,
                  "sourceOwnershipIdenticalToDay": True, "dayReplayPixelIdentical": replay_verified,
                  "crossAppearanceContoursVisuallyAccepted": False,
                  "colorAdjustment": any(item["colorAdjustment"] for item in operations),
                  "operations": operations, "stateFilesModified": False}
    extended_info = helpers.save_image(OUT / "extended-context-unreviewed.png", extended,
                                       {**provenance, "globalRectXYWH": [49037, 28557, 4326, 4326]})
    candidate = helpers.save_image(OUT / "r08_c13-shared-unreviewed.png", core,
                                   {**provenance, "cropFromExtendedXYXY": [115, 115, 4211, 4211], "globalRectXYWH": [49152, 28672, 4096, 4096]})
    preview = helpers.save_image(OUT / "preview-1024.png", core.resize((1024, 1024), Image.Resampling.LANCZOS),
                                 {"operation": "quarter-size overview only", "derivedFrom": [candidate], "finalArt": False, "completePixelCandidate": False, "previewScale": 0.25, "notNativePixelQA": True})
    qa = helpers.export_qa(core, candidate, west, west_info)
    qa += export_wide_qa(helpers, candidate, core)
    manifest = {**provenance, "createdAtUtc": helpers.now(), "appearance": "donghai_lantern", "tile": "r08_c13",
                "status": "shared-mask-complete-pixel-candidate-unreviewed", "formalAccepted": False, "wholeCityComplete": False,
                "script": {"file": str(Path(__file__).resolve()), "sha256": sha(__file__)},
                "qaHelper": {"file": str(ROOT / "r08_c13/assemble_c13_native.py"), "sha256": sha(ROOT / "r08_c13/assemble_c13_native.py")},
                "westSource": west_info,
                "extendedContext": extended_info, "candidate": candidate, "preview": preview, "qa": qa,
                "qaCoverage": {"internalFullLength256Bands": 6, "internalFullLength512Bands": 6, "wideBandSegments": 24, "internalJunctions": 9, "tileCorners": 4, "westCommonEdgeLength": 4096, "allVisualReviewPending": True}}
    helpers.atomic_write(OUT / "shared-assembly-manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true", help="Validate sources, masks and day pixel replay; write nothing")
    args = parser.parse_args()
    arrays, day_arrays, entries, day_manifest, manifest_hash = validate_inputs()
    masks, mask_evidence = load_day_masks(day_manifest)
    day_replay, _ = assemble(day_arrays, masks)
    expected_day = load_rgb(day_manifest["extendedContext"]["file"], day_manifest["extendedContext"]["sha256"], (EXTENDED, EXTENDED))
    require(np.array_equal(day_replay, expected_day), "Shared mask replay differs from exact day extended pixels")
    del day_replay, expected_day, day_arrays
    require(sha(DAY_MANIFEST) == manifest_hash, "Day manifest changed during validation")
    if args.validate_only:
        print(json.dumps({"validatedNativePatches": len(entries), "validatedSharedMasks": len(masks), "dayReplayPixelIdentical": True}))
        return 0
    combined, operations = assemble(arrays, masks)
    manifest = write_outputs(combined, entries, mask_evidence, manifest_hash, operations, True)
    print(json.dumps({"candidate": manifest["candidate"], "extendedContext": manifest["extendedContext"], "manifest": str(OUT / "shared-assembly-manifest.json"), "qaImages": len(manifest["qa"]), "colorAdjustment": False, "formalAccepted": False}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(f"Shared assembly refused: {error}") from error
