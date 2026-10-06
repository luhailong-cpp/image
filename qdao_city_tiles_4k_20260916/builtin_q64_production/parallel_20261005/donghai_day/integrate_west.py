"""Join four native west-edge repairs and insert into immutable baseline tiles.

Only --validate-only is useful until s1..s4 and their source records exist.
Default execution creates candidate tiles and native-pixel QA, never acceptance.
There is no image generation, scaling, registration, blur, or color correction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

import assembly as native

ROOT = Path(__file__).resolve().parent
TILE = ROOT / "r08_c11"
REPAIR = TILE / "repairs" / "west-common-edge"
OUTPUT = ROOT / "tiles"
QA = REPAIR / "integration-qa"
MASKS = REPAIR / "integration-masks"
EAST = TILE / "output" / "r08_c11.png"
EAST_MANIFEST = TILE / "output" / "assembly-manifest.json"
EXPECTED_EAST_SHA = "c5c5c24746460d9e09c713d7549da8d7fdb168a0aef240611877c9d1e4641354"
STARTS = (0, 1024, 2048, 2842)
PATCH, HEIGHT, PAIR_WIDTH = 1254, 4096, 8192
X0, X1, EDGE_OVERLAP = 3469, 4723, 150
PAIR_GLOBAL_ORIGIN = (36864, 28672)

sha = native.sha
require = native.require
read_json = native.load_json
save_json = native.save_json
save_image = native.save_image


def rgb(path, expected_size):
    with Image.open(path) as image:
        image.load()
        require(image.format == "PNG" and image.size == expected_size, f"Wrong PNG dimensions: {path}")
        require(image.mode in ("RGB", "RGBA"), f"Unexpected source pixel mode: {path}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), f"Transparent ground pixels: {path}")
        return np.asarray(image.convert("RGB")).copy()


def same_path(left, right):
    return Path(left).resolve() == Path(right).resolve()


def check_hash(path, expected, label):
    require(Path(path).is_file() and sha(path) == expected, f"Missing/changed {label}: {path}")


def load_baseline():
    handoff_path = ROOT / "handoff.json"
    handoff = read_json(handoff_path)
    matches = [item for item in handoff["baselineCandidates"] if item["tile"] == "r08_c10"]
    require(len(matches) == 1, "Need exactly one immutable west baseline in handoff")
    west = Path(matches[0]["file"])
    check_hash(west, matches[0]["sha256"], "west baseline")
    check_hash(EAST, EXPECTED_EAST_SHA, "pinned east baseline")
    east_manifest = read_json(EAST_MANIFEST)
    require(east_manifest["output"]["sha256"] == EXPECTED_EAST_SHA and
            same_path(east_manifest["output"]["file"], EAST), "East assembly manifest identifies a different candidate")
    sources = [
        {"tile": "r08_c10", "file": str(west), "sha256": sha(west),
         "recordFile": str(handoff_path), "recordSha256": sha(handoff_path), "pairRectXYXY": [0, 0, 4096, 4096]},
        {"tile": "r08_c11", "file": str(EAST), "sha256": sha(EAST),
         "recordFile": str(EAST_MANIFEST), "recordSha256": sha(EAST_MANIFEST), "pairRectXYXY": [4096, 0, 8192, 4096]},
    ]
    pair = np.concatenate((rgb(west, (4096, 4096)), rgb(EAST, (4096, 4096))), axis=1)
    require(pair.shape == (HEIGHT, PAIR_WIDTH, 3), "Wrong baseline pair dimensions")
    return pair, sources


def load_patches(pair, baselines):
    patches, entries, missing = {}, [], []
    for index, y in enumerate(STARTS, 1):
        name = f"s{index}"
        path = REPAIR / f"{name}.png"
        if not path.is_file():
            missing.append(name)
            continue
        record_path = Path(str(path) + ".generation.json")
        record = read_json(record_path)
        digest = sha(path)
        require(same_path(record["file"], path) and record["sha256"] == digest, f"Source record mismatch: {name}")
        require([record.get("width"), record.get("height")] == [PATCH, PATCH] and record.get("format") == "PNG",
                f"Recorded native size/format mismatch: {name}")
        require(record.get("route") == "builtin" and record.get("tool") == "image_gen.imagegen",
                f"Unexpected source route: {name}")
        require(record.get("generatedAt") and record.get("resizedAfterGeneration") is False and
                record.get("finalArtUpscaled") is False, f"Missing time/native-size evidence: {name}")
        submitted = record.get("submittedParameters", {})
        require(all(key in submitted and submitted[key] is None for key in ("model", "quality")),
                f"Unexpected actual selector claim: {name}")
        require("actualModel" in record and record["actualModel"] is None and
                "actualQuality" in record and record["actualQuality"] is None, f"Unexpected returned-model claim: {name}")
        raw = Path(record["evidence"]["toolResultSourcePath"])
        require(record["evidence"]["toolResultSha256"] == digest, f"Native/tool-result identity mismatch: {name}")
        if raw.is_file():
            check_hash(raw, digest, "available raw tool result")
        prompt = Path(record["prompt"])
        check_hash(prompt, record["promptSha256"], "prompt")
        require(prompt.read_text(encoding="utf-8-sig").strip(), f"Empty source prompt: {name}")
        references = record["references"]
        require(len(references) >= 2 and all(ref.get("role") for ref in references), f"Missing source/style reference roles: {name}")
        require([str(Path(p).resolve()) for p in submitted.get("referenced_image_paths", [])] ==
                [str(Path(ref["file"]).resolve()) for ref in references], f"Reference submission order mismatch: {name}")
        for ref in references:
            check_hash(ref["file"], ref["sha256"], "reference")
        guide = REPAIR / f"{name}-input.png"
        require(same_path(references[0]["file"], guide), f"Wrong primary input: {name}")
        guide_record_path = Path(str(guide) + ".generation.json")
        guide_record = read_json(guide_record_path)
        require(same_path(guide_record["file"], guide) and guide_record["sha256"] == sha(guide) and
                guide_record.get("resized") is False, f"Invalid native guide record: {name}")
        require(guide_record.get("sourceBoxInPair") == [X0, y, X1, y + PATCH], f"Wrong guide coordinates: {name}")
        expected_sources = [{"file": item["file"], "sha256": item["sha256"]} for item in baselines]
        expected_guide = pair[y:y + PATCH, X0:X1].copy()
        if index > 1:
            require(index - 1 in patches, f"Previous repair required to verify {name} guide")
            previous_path = REPAIR / f"s{index - 1}.png"
            overlap = STARTS[index - 2] + PATCH - y
            expected_guide[:overlap] = patches[index - 1][-overlap:]
            expected_sources.append({"file": str(previous_path), "sha256": sha(previous_path)})
        derived = guide_record.get("derivedFrom", [])
        require(len(derived) == len(expected_sources) and all(
            same_path(actual["file"], expected["file"]) and actual["sha256"] == expected["sha256"]
            for actual, expected in zip(derived, expected_sources)), f"Guide dependency chain mismatch: {name}")
        require(np.array_equal(rgb(guide, (PATCH, PATCH)), expected_guide), f"Guide is not the exact recorded crop/native overlap: {name}")
        patches[index] = rgb(path, (PATCH, PATCH))
        entries.append({
            "id": name, "file": str(path), "sha256": digest, "pixels": [PATCH, PATCH],
            "recordFile": str(record_path), "recordSha256": sha(record_path),
            "toolResultSourcePath": str(raw), "toolResultSha256": digest, "rawToolResultAvailable": raw.is_file(),
            "savedSourceMatchesRecordedRawBytes": True, "configTarget": record.get("configSnapshot"),
            "submittedModel": None, "submittedQuality": None, "actualModel": None, "actualQuality": None,
            "prompt": str(prompt), "promptSha256": sha(prompt), "references": references,
            "guideRecord": str(guide_record_path), "guideRecordSha256": sha(guide_record_path),
            "guideExactlyEqualsBaselineCropAndPriorNativeOverlap": True,
            "pairRectXYXY": [X0, y, X1, y + PATCH],
            "globalRectXYXY": [PAIR_GLOBAL_ORIGIN[0] + X0, PAIR_GLOBAL_ORIGIN[1] + y,
                               PAIR_GLOBAL_ORIGIN[0] + X1, PAIR_GLOBAL_ORIGIN[1] + y + PATCH],
            "sourceResampled": False, "sourceUpscaled": False,
        })
    return patches, entries, missing


def join_overlap(earlier, later, orientation, pair_rect, label, seam_fn):
    """Blend two matching overlap arrays; mask values choose earlier/later input."""
    require(earlier.shape == later.shape and earlier.ndim == 3, f"Wrong overlap arrays: {label}")
    left = earlier if orientation == "vertical" else earlier.transpose(1, 0, 2)
    right = later if orientation == "vertical" else later.transpose(1, 0, 2)
    path = seam_fn(left, right)
    width = left.shape[1]
    require(path.shape == (left.shape[0],) and np.all((path >= 0) & (path < width)), f"Invalid seam path: {label}")
    require(np.all(np.abs(np.diff(path)) <= 1), f"Discontinuous seam: {label}")
    alpha = native.seam_alpha(path, width=width)
    blended = native.blend(left, right, alpha)
    mixed_per_line = np.sum((alpha > 0) & (alpha < 255), axis=1)
    require(np.all(mixed_per_line <= 2), f"More than two mixed pixels per path sample: {label}")
    mask = alpha if orientation == "vertical" else alpha.T
    result = blended if orientation == "vertical" else blended.transpose(1, 0, 2)
    difference = np.abs(left.astype(np.int16) - right.astype(np.int16)).mean(axis=2)
    path_difference = difference[np.arange(len(path)), path]
    mask_info = save_image(MASKS / f"{label}.png", Image.fromarray(mask))
    npz_path = native.writable(MASKS / f"{label}.npz")
    with npz_path.open("wb") as stream:
        np.savez_compressed(stream, alpha_u8=mask, seam_offsets=path.astype(np.int32),
                            pair_rect_xyxy=np.asarray(pair_rect, dtype=np.int32), transition_pixels=np.asarray(2))
    detail = {
        "id": label, "orientation": orientation, "pairOverlapRectXYXY": pair_rect,
        "overlapPixels": width, "pathLength": len(path), "pathMin": int(path.min()), "pathMax": int(path.max()),
        "transitionWidthPixels": 2, "maxActuallyMixedPixelsPerPathSample": int(mixed_per_line.max()),
        "alphaDefinition": "0 at offsets <= seam-2; 64 at seam-1; 191 at seam; 255 at offsets >= seam+1",
        "maskMeaning": "0 retains earlier input, 255 selects later input; only 64/191 are blends",
        "maskPng": mask_info, "maskNpz": {"file": str(npz_path), "sha256": sha(npz_path)},
        "inputOverlapRGBMeanAbsoluteDifference": native.statistics(difference),
        "selectedPathRGBMeanAbsoluteDifference": native.statistics(path_difference),
        "diagnosticFlags": {"overlapMeanAbove24": bool(difference.mean() > 24),
                            "selectedPathP95Above48": bool(np.percentile(path_difference, 95) > 48)},
        "metricsAreNotVisualAcceptance": True, "resampling": False, "registration": False,
        "colorCorrection": False, "imageBlur": False, "maskBlur": False, "visualReview": "pending",
    }
    save_json(MASKS / f"{label}.json", detail)
    return result, detail


def integrate(pair, patches, seam_fn):
    require(set(patches) == {1, 2, 3, 4}, "All four native repairs required")
    strip, seams = patches[1].copy(), []
    for index in range(2, 5):
        start = STARTS[index - 1]
        overlap = strip.shape[0] - start
        require(overlap == (230 if index < 4 else 460), "Unexpected longitudinal overlap")
        blended, entry = join_overlap(strip[-overlap:], patches[index][:overlap], "horizontal",
                                      [X0, start, X1, start + overlap], f"strip-s{index - 1}-s{index}", seam_fn)
        strip = np.concatenate((strip[:-overlap], blended, patches[index][overlap:]), axis=0)
        seams.append(entry)
    require(strip.shape == (HEIGHT, PATCH, 3), "Repair strip must be exactly 1254 by 4096")
    repaired = pair.copy()
    repaired[:, X0:X1] = strip
    left, entry = join_overlap(pair[:, X0:X0 + EDGE_OVERLAP], strip[:, :EDGE_OVERLAP], "vertical",
                               [X0, 0, X0 + EDGE_OVERLAP, HEIGHT], "insert-left", seam_fn)
    repaired[:, X0:X0 + EDGE_OVERLAP] = left
    seams.append(entry)
    right, entry = join_overlap(strip[:, -EDGE_OVERLAP:], pair[:, X1 - EDGE_OVERLAP:X1], "vertical",
                                [X1 - EDGE_OVERLAP, 0, X1, HEIGHT], "insert-right", seam_fn)
    repaired[:, X1 - EDGE_OVERLAP:X1] = right
    seams.append(entry)
    return repaired, seams


def raw_pixel_sha(pixels):
    return hashlib.sha256(pixels.tobytes()).hexdigest()


def pixel_verification(baseline, candidate):
    require(candidate.shape == baseline.shape == (HEIGHT, PAIR_WIDTH, 3), "Wrong integrated pair dimensions")
    left_same = np.array_equal(baseline[:, :X0], candidate[:, :X0])
    right_same = np.array_equal(baseline[:, X1:], candidate[:, X1:])
    require(left_same and right_same, "Pixels outside the authorized repair strip changed")
    return {
        "outsideRepairExactlyIdentical": True, "outsideRepairChangedPixels": 0,
        "authorizedChangeRectInPairXYXY": [X0, 0, X1, HEIGHT],
        "changedPixelsInsideRepair": int(np.count_nonzero(np.any(baseline[:, X0:X1] != candidate[:, X0:X1], axis=2))),
        "unchangedRegions": [
            {"pairRectXYXY": [0, 0, X0, HEIGHT], "baselineRGBBytesSha256": raw_pixel_sha(baseline[:, :X0]),
             "candidateRGBBytesSha256": raw_pixel_sha(candidate[:, :X0]), "exactArrayEquality": left_same},
            {"pairRectXYXY": [X1, 0, PAIR_WIDTH, HEIGHT], "baselineRGBBytesSha256": raw_pixel_sha(baseline[:, X1:]),
             "candidateRGBBytesSha256": raw_pixel_sha(candidate[:, X1:]), "exactArrayEquality": right_same}],
        "spatialResampling": False, "noUpscaling": True,
    }


def write_qa(pair):
    image, items = Image.fromarray(pair), []

    def crop(name, box, kind, **extra):
        piece = image.crop(box)
        require(max(piece.size) <= 1536, f"QA crop too large for native review: {name}")
        items.append({**save_image(QA / f"{name}.png", piece), "kind": kind,
                      "pairSourceRectXYXY": list(box), "pixelScale": 1, "resized": False,
                      "visualInspection": "pending", **extra})

    def full_vertical(name, center, width, overlap_rect=None):
        box = (center - width // 2, 0, center + width // 2, HEIGHT)
        band = image.crop(box)
        sheet, pieces = Image.new("RGB", (width * 4, 1024)), []
        for part in range(4):
            rect = (0, part * 1024, width, (part + 1) * 1024)
            origin = (part * width, 0)
            sheet.paste(band.crop(rect), origin)
            pieces.append({"bandRectXYXY": list(rect), "sheetOriginXY": list(origin)})
        require(max(sheet.size) <= 1536, "Native full-edge QA sheet too large")
        items.append({**save_image(QA / f"{name}.png", sheet), "kind": "complete-native-vertical-band",
                      "pairSourceRectXYXY": list(box), "logicalBandPixels": list(band.size),
                      "coveredLengthPixels": HEIGHT, "pieces": pieces, "pixelScale": 1, "resized": False,
                      "actualBlendOverlapRectXYXY": overlap_rect, "visualInspection": "pending"})

    full_vertical("common-edge-c10-c11-full", 4096, 256)
    full_vertical("insertion-left-full", X0 + EDGE_OVERLAP // 2, 384, [X0, 0, X0 + EDGE_OVERLAP, HEIGHT])
    full_vertical("insertion-right-full", X1 - EDGE_OVERLAP // 2, 384, [X1 - EDGE_OVERLAP, 0, X1, HEIGHT])
    for index in range(2, 5):
        start, overlap = STARTS[index - 1], (230 if index < 4 else 460)
        crop(f"strip-horizontal-s{index - 1}-s{index}-full",
             (X0 - 128, start - 32, X1 + 128, start + overlap + 32), "complete-native-horizontal-overlap",
             actualBlendOverlapRectXYXY=[X0, start, X1, start + overlap])
    for side, x in (("left", X0), ("right", X1)):
        crop(f"insertion-corner-{side}-top", (x - 256, 0, x + 256, 512), "insertion-corner")
        crop(f"insertion-corner-{side}-bottom", (x - 256, HEIGHT - 512, x + 256, HEIGHT), "insertion-corner")
    require(len(items) == 10, "Expected three vertical bands, three horizontal overlap bands, and four corners")
    return items


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true", help="Verify available native sources and input provenance; write nothing")
    args = parser.parse_args(argv)
    baseline, baselines = load_baseline()
    patches, entries, missing = load_patches(baseline, baselines)
    if args.validate_only:
        print(json.dumps({"validatedPatches": len(entries), "missing": missing,
                          "complete": not missing, "baselines": baselines, "writes": 0}, indent=2))
        return 0
    require(not missing, "Integration refused: missing " + ", ".join(missing) + "; only --validate-only is available until all four exist")
    seam_fn = native.load_seam_function()
    repaired, seams = integrate(baseline, patches, seam_fn)
    pixels = pixel_verification(baseline, repaired)
    qa = write_qa(repaired)
    outputs = []
    for index, tile_id in enumerate(("r08_c10", "r08_c11")):
        destination = OUTPUT / f"{tile_id}.png"
        require(all(not same_path(destination, item["file"]) for item in baselines), "Cannot overwrite either baseline source")
        array = repaired[:, index * 4096:(index + 1) * 4096]
        saved = save_image(destination, Image.fromarray(array))
        require(np.array_equal(rgb(destination, (4096, 4096)), array), f"Saved pixels differ from integrated pixels: {tile_id}")
        outputs.append({**saved, "tile": tile_id, "pairRectXYXY": [index * 4096, 0, (index + 1) * 4096, HEIGHT],
                        "globalRectXYXY": [PAIR_GLOBAL_ORIGIN[0] + index * 4096, PAIR_GLOBAL_ORIGIN[1],
                                           PAIR_GLOBAL_ORIGIN[0] + (index + 1) * 4096, PAIR_GLOBAL_ORIGIN[1] + HEIGHT],
                        "savedPNGPixelsExactlyEqualComputedCandidate": True})
    # Verify the actual saved PNG pair, not only the in-memory candidate.
    saved_pair = np.concatenate([rgb(item["file"], (4096, 4096)) for item in outputs], axis=1)
    saved_pixels = pixel_verification(baseline, saved_pair)
    require(saved_pixels == pixels, "Saved pair verification differs from in-memory verification")
    for baseline_source in baselines:
        check_hash(baseline_source["file"], baseline_source["sha256"], "immutable baseline after write")
    manifest = {
        "createdAtUtc": native.utc_now(), "appearance": "donghai_day",
        "status": "west-common-edge-repaired-candidates-pending-visual-review", "formalAccepted": False,
        "wholeCityComplete": False, "clientAcceptance": False, "visualInspectionPerformedByScript": False,
        "script": {"file": str(Path(__file__).resolve()), "sha256": sha(Path(__file__))},
        "reusedAssemblyFunctions": {"file": str(Path(native.__file__).resolve()), "sha256": sha(Path(native.__file__))},
        "seamHelper": {"file": str(native.HELPER), "sha256": sha(native.HELPER), "function": "_minimum_vertical_seam"},
        "baselines": baselines, "nativeRepairSources": entries,
        "parameters": {"pairPixels": [PAIR_WIDTH, HEIGHT], "stripPixels": [PATCH, HEIGHT],
                       "stripPairRectXYXY": [X0, 0, X1, HEIGHT], "patchYStarts": list(STARTS),
                       "longitudinalOverlaps": [230, 230, 460], "insertionOverlapEachSidePixels": EDGE_OVERLAP,
                       "transitionWidthPixels": 2, "order": "top-to-bottom strip, then left and right insertion seams",
                       "registration": False, "colorCorrection": False, "imageBlur": False,
                       "maskBlur": False, "spatialResampling": False, "noUpscaling": True},
        "seams": seams, "pixelVerification": saved_pixels, "baselinesByteHashesUnchangedAfterOutput": True,
        "outputs": outputs, "qa": qa,
        "qaCoverage": {"fullCommonEdge": True, "fullLeftInsertionOverlapAndOuterEdge": True,
                       "fullRightInsertionOverlapAndOuterEdge": True, "horizontalOverlapBands": 3,
                       "insertionCorners": 4, "nativePixelScale": 1, "maxQADimension": 1536,
                       "inspectionStatus": "pending"},
    }
    save_json(OUTPUT / "west-integration-manifest.json", manifest)
    save_json(QA / "manifest.json", {"outputs": outputs, "qa": qa, "coverage": manifest["qaCoverage"],
                                    "visualInspection": "pending"})
    print(json.dumps({"outputs": outputs, "manifest": str(OUTPUT / "west-integration-manifest.json"),
                      "qaDirectory": str(QA), "outsideRepairExactlyIdentical": True, "formalAccepted": False}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, FileNotFoundError) as error:
        raise SystemExit(f"ERROR: {error}") from error
