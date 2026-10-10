"""Reproducible native-pixel r10_c15 assembly and visual-QA preparation.

No generation, source resizing, registration, color correction, acceptance, or
production-status mutation. All files written by this script stay in this task.
Incomplete inputs may only produce transparent progress previews.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[3]
TILE = ROOT / "r10_c15"
HELPER = PROJECT / "tianyong_festival_hd_20260910/seam_helpers.py"
GRID, CORE, HALO = 4, 1024, 115
OVERLAP, PATCH, FINAL, EXTENDED = 230, 1254, 4096, 4326
GLOBAL_ORIGIN = (57344, 36864)
OUT = TILE / "output"
QA = TILE / "qa" / "assembly"
MASKS = TILE / "qa" / "assembly-masks"
ART = OUT / "r10_c15.png"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def writable(path):
    path = Path(path).resolve()
    if not path.is_relative_to(TILE.resolve()):
        raise ValueError(f"Output outside assigned task: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_json(path, value):
    path = writable(path)
    temp = path.with_name(path.name + ".writing")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def save_image(path, image):
    path = writable(path)
    temp = path.with_name(path.name + ".writing")
    image.save(temp, format="PNG")
    temp.replace(path)
    return {"file": str(path), "sha256": sha(path), "pixels": list(image.size)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_path(value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def validate_source(row, column):
    name = f"r{row:02d}_c{column:02d}"
    path = TILE / "native" / (name + ".png")
    record_path = Path(str(path) + ".generation.json")
    require(record_path.is_file(), f"Missing source record: {record_path}")
    record = load_json(record_path)
    digest = sha(path)
    require(source_path(record["file"]) == path.resolve(), f"Source path mismatch: {name}")
    require(record.get("sha256") == digest, f"Source SHA256 mismatch: {name}")
    require([record.get("width"), record.get("height")] == [PATCH, PATCH],
            f"Recorded dimensions must be {PATCH} square: {name}")
    require(record.get("route") == "builtin", f"Unexpected generation route: {name}")
    require(record.get("resizedAfterGeneration") is False and record.get("finalArtUpscaled") is False,
            f"Explicit no-resize/no-upscale evidence required: {name}")
    require(record.get("generatedAt"), f"Missing generation timestamp: {name}")
    submitted = record.get("submittedParameters", {})
    for key in ("model", "quality"):
        require(key in submitted and submitted[key] is None, f"Unexpected exposed selector claim: {name}/{key}")
    require("actualModel" in record and record["actualModel"] is None,
            f"Unexpected returned-model claim: {name}")
    require("actualQuality" in record and record["actualQuality"] is None,
            f"Unexpected returned-quality claim: {name}")
    evidence = record.get("evidence", {})
    require(evidence.get("toolResultSha256") == digest, f"Raw tool-result hash mismatch: {name}")
    raw = source_path(evidence["toolResultSourcePath"])
    if raw.is_file():
        require(sha(raw) == digest, f"Raw tool-result bytes changed: {name}")
    prompt = source_path(record["prompt"])
    require(prompt.is_file() and sha(prompt) == record.get("promptSha256"), f"Prompt evidence mismatch: {name}")
    require(prompt.read_text(encoding="utf-8-sig").strip(), f"Empty prompt: {name}")
    references = record.get("references", [])
    require(len(references) >= 2, f"Missing input/style reference roles: {name}")
    for ref in references:
        ref_path = source_path(ref["file"])
        require(ref.get("role") and ref.get("sha256"), f"Incomplete reference evidence: {name}")
        if ref.get("availability") == "superseded":
            # An AI edit may replace its own canonical input after the rejected
            # pixels are removed. Verify its preserved record, never pretend the
            # current canonical bytes revalidate that historical input image.
            historical_path = source_path(ref["historicalRecord"])
            require(historical_path.is_relative_to(ROOT.resolve()),
                    f"Historical edit record outside assigned task: {name}")
            require(historical_path.is_file() and sha(historical_path) == ref.get("historicalRecordSha256"),
                    f"Historical reference record mismatch: {historical_path}")
            historical = load_json(historical_path)
            require(historical.get("sha256") == ref["sha256"] and
                    source_path(historical["file"]) == ref_path,
                    f"Historical record does not identify edited input: {name}")
            require(ref.get("pixelValidation") == "historical-record-only-not-current-pixels",
                    f"Historical reference lacks explicit validation limitation: {name}")
        else:
            require(ref_path.is_file() and sha(ref_path) == ref["sha256"], f"Reference evidence mismatch: {ref_path}")
    require([str(source_path(p)) for p in submitted.get("referenced_image_paths", [])] ==
            [str(source_path(ref["file"])) for ref in references], f"Submitted reference order mismatch: {name}")
    with Image.open(path) as image:
        image.load()
        require(image.format == "PNG" and image.size == (PATCH, PATCH), f"Expected native {PATCH} PNG: {name}")
        require(image.mode in ("RGB", "RGBA"), f"Unexpected pixel mode: {name}/{image.mode}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), f"Non-opaque native patch: {name}")
        pixels = np.asarray(image.convert("RGB")).copy()
    x, y = (column - 1) * CORE, (row - 1) * CORE
    info = {
        "id": name, "row": row, "column": column, "file": str(path), "sha256": digest,
        "pixels": [PATCH, PATCH], "recordFile": str(record_path), "recordSha256": sha(record_path),
        "toolResultSourcePath": str(raw), "toolResultSha256": digest,
        "toolResultStillAvailable": raw.is_file(), "savedNativeMatchesRecordedToolResultBytes": True,
        "promptFile": str(prompt), "promptSha256": sha(prompt), "references": references,
        "configTarget": record.get("configSnapshot"), "submittedModel": None, "submittedQuality": None,
        "actualModel": None, "actualQuality": None, "generatedAt": record["generatedAt"],
        "extendedRectXYWH": [x, y, PATCH, PATCH],
        "globalRectXYWH": [GLOBAL_ORIGIN[0] - HALO + x, GLOBAL_ORIGIN[1] - HALO + y, PATCH, PATCH],
        "resampled": False, "upscaled": False,
    }
    return pixels, info


def load_sources():
    arrays, entries, missing = {}, [], []
    for row in range(1, GRID + 1):
        for column in range(1, GRID + 1):
            path = TILE / "native" / f"r{row:02d}_c{column:02d}.png"
            if not path.is_file():
                missing.append(path.stem)
                continue
            arrays[row, column], entry = validate_source(row, column)
            entries.append(entry)
    return arrays, entries, missing


def source_coverage(arrays):
    counts = np.zeros((EXTENDED, EXTENDED), dtype=np.uint8)
    for row, column in arrays:
        x, y = (column - 1) * CORE, (row - 1) * CORE
        counts[y:y + PATCH, x:x + PATCH] += 1
    core = counts[HALO:HALO + FINAL, HALO:HALO + FINAL]
    return counts, {
        "extendedPixels": EXTENDED * EXTENDED, "extendedCoveredPixels": int(np.count_nonzero(counts)),
        "extendedUncoveredPixels": int(np.count_nonzero(counts == 0)),
        "finalPixels": FINAL * FINAL, "finalCoveredPixels": int(np.count_nonzero(core)),
        "finalUncoveredPixels": int(np.count_nonzero(core == 0)),
        "fullCoverage": bool(np.all(counts)), "maxOverlapSources": int(counts.max()),
    }


def preview(arrays, entries, missing):
    # Non-overlapping source cores only: no fill, inference, or candidate assembly.
    canvas = Image.new("RGBA", (FINAL, FINAL), (0, 0, 0, 0))
    for (row, column), pixels in arrays.items():
        core = Image.fromarray(pixels[HALO:HALO + CORE, HALO:HALO + CORE])
        canvas.paste(core, ((column - 1) * CORE, (row - 1) * CORE))
    native_info = save_image(OUT / "progress-native-transparent.png", canvas)
    small = canvas.resize((1024, 1024), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(small)
    for row in range(1, GRID + 1):
        for column in range(1, GRID + 1):
            if (row, column) in arrays:
                continue
            x, y = (column - 1) * 256, (row - 1) * 256
            draw.rectangle((x + 1, y + 1, x + 254, y + 254), outline=(255, 50, 70, 255), width=2)
            draw.text((x + 12, y + 12), f"MISSING r{row:02d}_c{column:02d}", fill=(255, 50, 70, 255))
    small_info = save_image(OUT / "current-preview.png", small)
    result = {
        "updatedAtUtc": utc_now(), "kind": "incomplete-progress-preview" if missing else "unassembled-core-preview",
        "nativePatchesPresent": len(arrays), "nativePatchesRequired": 16, "missing": missing,
        "fullTileCandidateProduced": False, "countsAsCompleteTile": False,
        "formalAccepted": False, "visualInspectionPerformedByScript": False,
        "nativePreview": {**native_info, "resized": False, "unknownPixelsAreTransparent": True,
                          "opaquePixels": len(arrays) * CORE * CORE},
        "displayPreview": {**small_info, "scale": 0.25, "previewOnly": True, "missingRegionsAnnotated": True},
        "nativeSources": entries,
    }
    save_json(OUT / "progress-preview.json", result)
    return result


def load_seam_function():
    spec = importlib.util.spec_from_file_location("existing_native_seam_helper", HELPER)
    require(spec is not None and spec.loader is not None, f"Cannot load seam helper: {HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._minimum_vertical_seam


def statistics(values):
    values = np.asarray(values)
    return {"mean": float(values.mean()), "p50": float(np.percentile(values, 50)),
            "p95": float(np.percentile(values, 95)), "max": float(values.max())}


def seam_alpha(path, width=OVERLAP):
    # Exactly two partly mixed pixels per row; all other pixels are exact inputs.
    # No blur/filter is applied to either art or mask. Integer weights are saved.
    distance = np.arange(width, dtype=np.int32)[None, :] - path[:, None]
    alpha = np.where(distance <= -2, 0, np.where(distance == -1, 64,
                     np.where(distance == 0, 191, 255))).astype(np.uint8)
    require(np.all(np.sum((alpha > 0) & (alpha < 255), axis=1) <= 2), "Transition exceeds two pixels")
    return alpha


def blend(left, right, alpha):
    weight = alpha.astype(np.uint32)[..., None]
    result = ((left.astype(np.uint32) * (255 - weight) + right.astype(np.uint32) * weight + 127) // 255).astype(np.uint8)
    require(np.array_equal(result[alpha == 0], left[alpha == 0]), "Base-only pixels changed")
    require(np.array_equal(result[alpha == 255], right[alpha == 255]), "Incoming-only pixels changed")
    identical = np.all(left == right, axis=2)
    require(np.array_equal(result[identical], left[identical]), "Identical overlap pixels changed")
    return result


def append(base, incoming, seam_fn, label, orientation, rect):
    require(base.shape[0] == incoming.shape[0], f"Different seam lengths: {label}")
    left, right = base[:, -OVERLAP:], incoming[:, :OVERLAP]
    path = seam_fn(left, right)
    require(path.shape == (left.shape[0],), f"Invalid seam result: {label}")
    require(np.all((path >= 0) & (path < OVERLAP)), f"Seam escaped overlap: {label}")
    require(np.all(np.abs(np.diff(path)) <= 1), f"Discontinuous seam path: {label}")
    alpha = seam_alpha(path)
    mixed = blend(left, right, alpha)
    result = np.concatenate((base[:, :-OVERLAP], mixed, incoming[:, OVERLAP:]), axis=1)
    mask = alpha if orientation == "vertical" else alpha.T
    mask_info = save_image(MASKS / (label + ".png"), Image.fromarray(mask))
    npz_path = writable(MASKS / (label + ".npz"))
    with npz_path.open("wb") as stream:
        np.savez_compressed(stream, alpha_u8=mask, seam_offsets=path.astype(np.int32),
                            overlap_rect_extended_xywh=np.asarray(rect, dtype=np.int32),
                            transition_width_pixels=np.asarray(2, dtype=np.int32))
    delta = np.abs(left.astype(np.int16) - right.astype(np.int16)).astype(np.float32).mean(axis=2)
    idx = np.arange(len(path))
    band_mean = delta.mean(axis=1)
    detail = {
        "id": label, "orientation": orientation, "overlapRectExtendedXYWH": rect,
        "overlapPixels": OVERLAP, "pathLength": len(path), "pathOffsetMin": int(path.min()),
        "pathOffsetMax": int(path.max()), "transitionWidthPixels": 2,
        "alphaDefinition": "0 for x<=seam-2; 64 at seam-1; 191 at seam; 255 for x>=seam+1",
        "maskMeaning": "0 retains existing composite; 255 takes incoming source; values 64 and 191 are the only mixtures",
        "maskPng": mask_info, "maskNpz": {"file": str(npz_path), "sha256": sha(npz_path)},
        "overlapRGBMeanAbsoluteDifference": statistics(delta),
        "selectedPathRGBMeanAbsoluteDifference": statistics(delta[idx, path]),
        "diagnosticFlags": {"overlapMeanDifferenceAbove24": bool(delta.mean() > 24),
                            "pathP95DifferenceAbove48": bool(np.percentile(delta[idx, path], 95) > 48),
                            "linesMeanDifferenceAbove40": int(np.count_nonzero(band_mean > 40))},
        "diagnosticThresholdsAreNotAcceptanceCriteria": True,
        "visualReview": "pending", "registration": False, "colorCorrection": False,
        "imageBlur": False, "maskBlur": False, "imageResampling": False,
    }
    save_json(MASKS / (label + ".json"), detail)
    return result, detail


def assemble(arrays, seam_fn):
    rows, seams = [], []
    for row in range(1, GRID + 1):
        combined = arrays[row, 1]
        for column in range(2, GRID + 1):
            rect = [(column - 1) * CORE, (row - 1) * CORE, OVERLAP, PATCH]
            combined, info = append(combined, arrays[row, column], seam_fn,
                                    f"vertical_r{row:02d}_c{column - 1:02d}_c{column:02d}", "vertical", rect)
            seams.append(info)
        require(combined.shape == (PATCH, EXTENDED, 3), "Wrong assembled row size")
        rows.append(combined)
    combined = rows[0]
    for row in range(2, GRID + 1):
        # Reuse the existing top-to-bottom seam routine by swapping spatial axes.
        transposed, info = append(combined.transpose(1, 0, 2), rows[row - 1].transpose(1, 0, 2),
                                  seam_fn, f"horizontal_r{row - 1:02d}_r{row:02d}", "horizontal",
                                  [0, (row - 1) * CORE, EXTENDED, OVERLAP])
        combined = transposed.transpose(1, 0, 2)
        seams.append(info)
    require(combined.shape == (EXTENDED, EXTENDED, 3), "Wrong extended-context dimensions")
    return combined, seams


def checked_north():
    plan = load_json(TILE / "plan.json")
    entry = plan['neighbors']['north']
    require(entry.get('bindingStatus') == 'bound' and entry.get('sha256'), 'North neighbor is not yet bound')
    path = Path(entry["file"])
    require(path.is_file() and sha(path) == entry["sha256"], "North baseline missing or SHA256 changed")
    with Image.open(path) as image:
        image.load()
        require(image.size == (FINAL, FINAL), "North baseline dimensions are not 4096 square")
        image = image.convert("RGB")
    return image, {"file": str(path), "sha256": sha(path), "tile": "r09_c15", "globalRect": entry['globalRect'], "formalAccepted": False}


def write_qa(candidate, extended, north):
    items = []

    def crop(name, box, kind):
        image = candidate.crop(box)
        info = save_image(QA / (name + ".png"), image)
        items.append({**info, "kind": kind, "source": str(ART), "sourceRectXYXY": list(box),
                      "resized": False, "pixelScale": 1, "visualInspection": "pending"})

    def band(name, image, orientation, box, sources):
        require(image.size == ((256, FINAL) if orientation == "vertical" else (FINAL, 256)), "Bad full-band dimensions")
        sheet, pieces = Image.new("RGB", (1024, 1024)), []
        for part in range(4):
            source_box = (0, part * 1024, 256, (part + 1) * 1024) if orientation == "vertical" else (part * 1024, 0, (part + 1) * 1024, 256)
            destination = (part * 256, 0) if orientation == "vertical" else (0, part * 256)
            sheet.paste(image.crop(source_box), destination)
            pieces.append({"bandRectXYXY": list(source_box), "sheetOriginXY": list(destination)})
        info = save_image(QA / (name + ".png"), sheet)
        items.append({**info, "kind": "complete-native-seam-band", "orientation": orientation,
                      "logicalBandPixels": list(image.size), "bandSourceRectXYXY": box,
                      "sources": sources, "pieces": pieces, "coveredLengthPixels": FINAL,
                      "resized": False, "pixelScale": 1, "visualInspection": "pending"})

    for boundary in range(1, GRID):
        pos = boundary * CORE
        box = (pos - 128, 0, pos + 128, FINAL)
        band(f"internal-vertical-x{pos}-full", candidate.crop(box), "vertical", list(box), [str(ART)])
        box = (0, pos - 128, FINAL, pos + 128)
        band(f"internal-horizontal-y{pos}-full", candidate.crop(box), "horizontal", list(box), [str(ART)])
    for row in range(1, GRID):
        for column in range(1, GRID):
            x, y = column * CORE, row * CORE
            crop(f"intersection-x{x}-y{y}", (x - 256, y - 256, x + 256, y + 256), "internal-four-way-intersection")
    for name, x, y in (("nw", 0, 0), ("ne", FINAL - 512, 0),
                       ("sw", 0, FINAL - 512), ("se", FINAL - 512, FINAL - 512)):
        crop(f"corner-{name}", (x, y, x + 512, y + 512), "tile-corner")
    common = Image.new("RGB", (FINAL, 256))
    common.paste(north.crop((0, FINAL - 128, FINAL, FINAL)), (0, 0))
    common.paste(candidate.crop((0, 0, FINAL, 128)), (0, 128))
    band("north-r09-r10-common-edge-full", common, "horizontal", [0, -128, FINAL, 128],
         [{"tile": "r09_c15", "rectXYXY": [0, 3968, 4096, 4096]},
          {"tile": "r10_c15", "rectXYXY": [0, 0, 4096, 128]}])
    # Exact 115-pixel shared context: paired sheets expose geometry/color differences.
    old_overlap = north.crop((0, FINAL-HALO, FINAL, FINAL))
    new_overlap = extended.crop((HALO, 0, HALO + FINAL, HALO))
    pair = Image.new("RGB", (FINAL, 256), (32, 32, 32))
    pair.paste(old_overlap, (0, 0))
    pair.paste(new_overlap, (0, 128))
    band("north-halo-comparison-full", pair, "horizontal", None,
         [{"tile": "r09_c15", "rectXYXY": [0, 3981, 4096, 4096], "bandY": 0},
          {"file": "extended-context.png", "rectXYXY": [115, 0, 4211, 115], "bandY": 128}])
    info = save_image(QA / "overview-preview-1024.png", candidate.resize((1024, 1024), Image.Resampling.LANCZOS))
    items.append({**info, "kind": "downsampled-overview-only", "scale": 0.25, "notNativePixelQA": True})
    return items


def boundary_diagnostics(candidate, extended, north):
    pixels, old = np.asarray(candidate), np.asarray(north)
    delta = np.abs(pixels[0].astype(np.int16) - old[-1].astype(np.int16)).mean(axis=1)
    nearby = np.concatenate((np.abs(np.diff(pixels[:128].astype(np.int16), axis=0)).mean(axis=2).ravel(),
                             np.abs(np.diff(old[-128:].astype(np.int16), axis=0)).mean(axis=2).ravel()))
    halo_delta = np.abs(old[-HALO:].astype(np.int16) - np.asarray(extended)[:HALO, HALO:HALO + FINAL].astype(np.int16)).mean(axis=2)
    return {
        "northAdjacentPixelRGBMeanAbsoluteDifference": statistics(delta),
        "northNearbyVerticalGradient": statistics(nearby),
        "northHaloSameCoordinateRGBMeanAbsoluteDifference": statistics(halo_delta),
        "diagnosticFlags": {"boundaryMeanAboveTwiceNearbyMean": bool(delta.mean() > 2 * max(float(nearby.mean()), 1)),
                            "haloMeanDifferenceAbove24": bool(halo_delta.mean() > 24)},
        "northBoundaryHasNotBeenBlendedOrCorrected": True,
        "thresholdsAreNotAcceptanceCriteria": True, "visualReview": "pending",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--preview", action="store_true", help="Write transparent core progress previews only; never a tile candidate")
    modes.add_argument("--validate-only", action="store_true", help="Check all present source provenance and report missing patches; write nothing")
    args = parser.parse_args(argv)
    arrays, entries, missing = load_sources()
    if args.validate_only:
        print(json.dumps({"validatedPatches": len(entries), "missing": missing, "complete": not missing}, indent=2))
        return 0
    current_manifest = OUT / "assembly-manifest.json"
    if current_manifest.is_file():
        current = load_json(current_manifest)
        require(current.get("status") != "complete-tile-producer-reviewed",
                "Stable reviewed output is protected. --validate-only is safe; use an explicit dedicated repair workflow for further changes.")
    if args.preview:
        result = preview(arrays, entries, missing)
        print(json.dumps({"preview": result["displayPreview"]["file"], "validatedPatches": len(entries), "missing": missing}, indent=2))
        return 0
    require(not missing, "Assembly refused: missing " + ", ".join(missing) + "; use --preview for transparent progress")
    counts, coverage = source_coverage(arrays)
    require(coverage["fullCoverage"], "Incomplete pixel coverage; no candidate may be written")
    north, north_info = checked_north()
    seam_fn = load_seam_function()
    combined, seams = assemble(arrays, seam_fn)
    extended = Image.fromarray(combined)
    candidate = extended.crop((HALO, HALO, HALO + FINAL, HALO + FINAL))
    require(candidate.size == (FINAL, FINAL), "Wrong candidate dimensions")
    qa = write_qa(candidate, extended, north)
    diagnostics = boundary_diagnostics(candidate, extended, north)
    coverage_info = save_image(MASKS / "source-coverage-counts.png", Image.fromarray(counts))
    extended_info = save_image(OUT / "extended-context.png", extended)
    candidate_info = save_image(ART, candidate)
    manifest = {
        "createdAtUtc": utc_now(), "appearance": "donghai_day", "tile": "r10_c15",
        "status": "complete-pixel-candidate-pending-visual-review", "formalAccepted": False,
        "wholeCityComplete": False, "clientAcceptance": False, "visualInspectionPerformedByScript": False,
        "script": {"file": str(Path(__file__).resolve()), "sha256": sha(Path(__file__))},
        "seamHelper": {"file": str(HELPER), "sha256": sha(HELPER), "function": "_minimum_vertical_seam"},
        "parameters": {"grid": [GRID, GRID], "core": CORE, "halo": HALO, "overlap": OVERLAP,
                       "patchPixels": [PATCH, PATCH], "extendedPixels": [EXTENDED, EXTENDED],
                       "cropXYXY": [HALO, HALO, HALO + FINAL, HALO + FINAL],
                       "globalRectXYWH": [*GLOBAL_ORIGIN, FINAL, FINAL],
                       "order": "assemble each row left-to-right, then rows top-to-bottom",
                       "transitionWidthPixels": 2, "registration": False, "colorCorrection": False,
                       "spatialResampling": False, "imageBlur": False, "maskBlur": False,
                       "noUpscaling": True, "singleNative4KGeneration": False,
                       "sourcePixelsUnchangedOutsideNarrowBlendTransitions": True},
        "coverage": {**coverage, "countMask": coverage_info, "all16SourcesValidated": True,
                     "coverageProvesPresenceOnlyNotQuality": True},
        "nativeSources": entries, "northBaseline": north_info, "seams": seams,
        "output": candidate_info, "extendedContext": extended_info,
        "boundaryDiagnostics": diagnostics, "qa": qa,
        "qaCoverage": {"completeInternalVerticalSeams": 3, "completeInternalHorizontalSeams": 3,
                       "internalIntersections": 9, "tileCorners": 4, "completeNorthCommonEdge": True,
                       "allNativeQASheetsAtMost1536PixelsPerDimension": True,
                       "nativePixelQAResized": False, "inspectionStatus": "pending"},
    }
    save_json(OUT / "assembly-manifest.json", manifest)
    save_json(QA / "manifest.json", {"qa": qa, "coverage": manifest["qaCoverage"],
                                    "candidateSha256": candidate_info["sha256"], "visualInspection": "pending"})
    print(json.dumps({"candidate": candidate_info, "manifest": str(OUT / "assembly-manifest.json"),
                      "qaDirectory": str(QA), "formalAccepted": False}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, FileNotFoundError) as error:
        raise SystemExit(f"ERROR: {error}") from error


