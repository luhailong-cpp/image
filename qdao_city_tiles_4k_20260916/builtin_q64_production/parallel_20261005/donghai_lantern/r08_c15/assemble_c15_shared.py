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
TILE = ROOT / "r08_c15"
BASE = TILE / "shared-assembly"
OUT, QA = BASE / "output", BASE / "qa"
DAY_MANIFEST = TILE / "source-contract-v2/snapshots/manifests/7f1ad0c868c6e3d2-previous-assembly-manifest.json"
DAY_MASKS = DAY / "r08_c15/qa/assembly-masks"
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
    path = ROOT / "r08_c15/assemble_c15_native.py"
    spec = importlib.util.spec_from_file_location("lantern_c15_core_qa_helpers", path)
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
    import c15_contract
    arrays, day_arrays, entries, manifest, manifest_hash, missing = c15_contract.validate_inputs(sys.modules[__name__])
    return arrays, day_arrays, entries, manifest, manifest_hash


def verify_day_replay(day_arrays, manifest, masks):
    import c15_contract
    return c15_contract.verify_day_replay(sys.modules[__name__], day_arrays, manifest, masks)


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
                  "sourceOwnershipIdenticalToDayNativeBase": True, "currentDayPostRepairsAppliedToFestival": False, "dayReplayPixelIdentical": replay_verified,
                  "requiredPostAssemblyRepairs": read(TILE / "source-contract-v2/source-contract.json")["insertionOperations"],
                  "dayReplayIncludesPostRepairs": False, "externalDayConsolidatedRepairsPending": True, "festivalCandidateIsNativeBaseOnly": True,
                  "crossAppearanceContoursVisuallyAccepted": False,
                  "colorAdjustment": any(item["colorAdjustment"] for item in operations),
                  "operations": operations, "stateFilesModified": False}
    extended_info = helpers.save_image(OUT / "extended-context-unreviewed.png", extended,
                                       {**provenance, "globalRectXYWH": [57229, 28557, 4326, 4326]})
    candidate = helpers.save_image(OUT / "r08_c15-shared-unreviewed.png", core,
                                   {**provenance, "cropFromExtendedXYXY": [115, 115, 4211, 4211], "globalRectXYWH": [57344, 28672, 4096, 4096]})
    preview = helpers.save_image(OUT / "preview-1024.png", core.resize((1024, 1024), Image.Resampling.LANCZOS),
                                 {"operation": "quarter-size overview only", "derivedFrom": [candidate], "finalArt": False, "completePixelCandidate": False, "previewScale": 0.25, "notNativePixelQA": True})
    qa = helpers.export_qa(core, candidate, west, west_info)
    qa += export_wide_qa(helpers, candidate, core)
    manifest = {**provenance, "createdAtUtc": helpers.now(), "appearance": "donghai_lantern", "tile": "r08_c15",
                "status": "shared-mask-complete-pixel-candidate-unreviewed", "formalAccepted": False, "wholeCityComplete": False,
                "script": {"file": str(Path(__file__).resolve()), "sha256": sha(__file__)},
                "qaHelper": {"file": str(ROOT / "r08_c15/assemble_c15_native.py"), "sha256": sha(ROOT / "r08_c15/assemble_c15_native.py")},
                "westSource": west_info,
                "extendedContext": extended_info, "candidate": candidate, "preview": preview, "qa": qa,
                "qaCoverage": {"internalFullLength256Bands": 6, "internalFullLength512Bands": 6, "wideBandSegments": 24, "internalJunctions": 9, "tileCorners": 4, "westCommonEdgeLength": 4096, "allVisualReviewPending": True}}
    helpers.atomic_write(OUT / "shared-assembly-manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return manifest


def main():
    import c15_contract
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true', help='Default: write only c15 JSON preflight evidence, allow missing native files')
    parser.add_argument('--validate-only', action='store_true', help='Alias for preflight; never produces image pixels')
    parser.add_argument('--assemble-base', action='store_true', help='Explicitly export all-16 shared-mask base; current DAY post-repair conversion remains a separate required step')
    args = parser.parse_args()
    if not args.assemble_base:
        print(json.dumps(c15_contract.preflight(sys.modules[__name__]), ensure_ascii=False, indent=2))
        return 0
    arrays, day_arrays, entries, day_manifest, manifest_hash = validate_inputs()
    masks, mask_evidence = load_day_masks(day_manifest)
    proof = verify_day_replay(day_arrays, day_manifest, masks)
    del day_arrays
    combined, operations = assemble(arrays, masks)
    manifest = write_outputs(combined, entries, mask_evidence, manifest_hash, operations, True)
    print(json.dumps({'candidate':manifest['candidate'], 'dayReplay':proof, 'formalAccepted':False},indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(f"Shared assembly refused: {error}") from error
