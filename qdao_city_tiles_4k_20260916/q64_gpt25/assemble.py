#!/usr/bin/env python3
"""Strict mechanical 2x2 assembly; this file never generates art or calls an API.

Commands:
  python assemble.py --preflight       Validate plan + synthetic pixels, no art output.
  python assemble.py --record-contract Print the required per-native provenance schema.
  python assemble.py                   Validate real evidence, then assemble a candidate.
  python assemble.py --check           Revalidate an existing candidate.

A record/evidence schema is a documentary audit trail, not a server signature.
Only an explicit captured response model may populate returnedModel. A requested
model or an assertion in a prompt does not prove the returned backend version.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "plan.json"
HELPER = ROOT.parents[1] / "tianyong_festival_hd_20260910" / "seam_helpers.py"
MODEL = "gpt-image-2.5-sunburst-2026-09-08"
QUALITY = "max"
GRID, CORE, HALO = 2, 2048, 56
OVERLAP, PATCH, ASSEMBLED, FINAL = 112, 2160, 4208, 4096
OUTPUT, QA = ROOT / "output", ROOT / "qa"
ART = OUTPUT / "tianyong_r10_c07_q64_4k_candidate.png"
REPORT = OUTPUT / "assembly.json"
IDS = [f"r{r + 1:02d}_c{c + 1:02d}" for r in range(GRID) for c in range(GRID)]


class EvidenceError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    require(path.is_file(), f"Missing required evidence: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"Expected JSON object: {path}")
    return value


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def local_path(value: str, field: str) -> Path:
    require(isinstance(value, str) and bool(value), f"Missing path: {field}")
    path = Path(value)
    path = (path if path.is_absolute() else ROOT / path).resolve()
    require(path.is_relative_to(ROOT), f"{field} escapes this production package: {path}")
    return path


def assert_hash(value, actual: str, field: str) -> None:
    require(isinstance(value, str) and value.lower() == actual, f"SHA-256 mismatch or missing: {field}")


def read_pixels(path: Path, size: tuple[int, int]) -> np.ndarray:
    require(path.is_file(), f"Missing required native PNG: {path}")
    with Image.open(path) as image:
        image.load()
        require(image.format == "PNG" and image.size == size, f"Expected native PNG {size}, got {image.format} {image.size}: {path}")
        require(image.mode in ("RGB", "RGBA"), f"Unsupported colour mode {image.mode}: {path}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), f"Non-opaque map patch: {path}")
        return np.asarray(image.convert("RGB")).copy()


def load_plan() -> tuple[dict, list[dict]]:
    plan = read_json(PLAN)
    require(plan.get("schemaVersion") == 1, "Unsupported plan schema")
    require(plan.get("targetModel") == MODEL and plan.get("targetQuality") == QUALITY, "Plan target model/quality differs from the strict request")
    require(plan.get("nativeGrid") == {"rows": 2, "columns": 2}, "Expected native 2x2 grid")
    require(plan.get("deliveryTilePixels") == [FINAL, FINAL], "Expected 4096-square delivery")
    require(plan.get("sampleTile", {}).get("row") == 10 and plan.get("sampleTile", {}).get("column") == 7, "This assembler is for sample r10_c07")
    require(len(plan.get("patches", [])) == 4, "Plan must contain exactly four patches")
    by_id = {item.get("id"): item for item in plan["patches"]}
    require(set(by_id) == set(IDS), "Plan IDs are missing or duplicated")
    ordered = []
    for index, tile_id in enumerate(IDS):
        patch = by_id[tile_id]
        require((patch.get("row"), patch.get("column")) == divmod(index, GRID), f"Wrong coordinates: {tile_id}")
        require(patch.get("targetNativePixels") == [PATCH, PATCH] and patch.get("corePixels") == [CORE, CORE], f"Wrong native/core dimensions: {tile_id}")
        require(patch.get("contextPerSide") == HALO and patch.get("adjacentOverlap") == OVERLAP, f"Wrong overlap: {tile_id}")
        require(patch.get("referenceOnly") is True, f"Reference role must be layout-only: {tile_id}")
        prompt = local_path(patch.get("promptFile"), f"{tile_id}.promptFile")
        reference = local_path(patch.get("layoutReference"), f"{tile_id}.layoutReference")
        native = local_path(patch.get("outputFile"), f"{tile_id}.outputFile")
        require(native == ROOT / "native" / f"{tile_id}.png", f"Unexpected native location: {tile_id}")
        require(prompt.is_file() and prompt.read_text(encoding="utf-8-sig").strip(), f"Missing/empty prompt: {tile_id}")
        assert_hash(patch.get("promptSha256"), sha256(prompt), f"plan.{tile_id}.prompt")
        require(reference.is_file(), f"Missing layout reference: {reference}")
        assert_hash(patch.get("referenceSha256"), sha256(reference), f"plan.{tile_id}.reference")
        with Image.open(reference) as image:
            require(image.format == "PNG" and image.size == (PATCH, PATCH), f"Invalid layout reference: {reference}")
        ordered.append(patch)
    return plan, ordered


def record_contract() -> dict:
    """Strings in angle brackets are explanations, never sample generation evidence."""
    request = {
        "model": MODEL, "quality": QUALITY, "size": "2160x2160",
        "output_format": "png",
        "promptSha256": "<SHA-256 of exact saved UTF-8 prompt file>",
        "referenceSha256": "<SHA-256 of submitted reference PNG>",
    }
    return {
        "note": "Schema only. Do not create records before a real successful API call. Preserve a sanitized capture; never save credentials.",
        "recordFile": "native/{id}.record.json",
        "record": {
            "schemaVersion": 1, "id": "<r01_c01|r01_c02|r02_c01|r02_c02>",
            "route": "api", "provider": "openai", "request": request,
            "outputSha256": "<SHA-256 of unchanged returned PNG>",
            "promptSha256": "<same as request.promptSha256>",
            "referenceSha256": "<same as request.referenceSha256>",
            "actualNativePixels": [PATCH, PATCH],
            "resizedAfterGeneration": False, "finalArtUpscaled": False,
            "sourceOutputPath": "<path to retained original returned PNG; may equal native path>",
            "sourceOutputSha256": "<same as outputSha256>",
            "evidenceFile": "evidence/{id}.api-response.json",
            "evidenceSha256": "<SHA-256 of evidence JSON>",
        },
        "evidence": {
            "schemaVersion": 1, "eventType": "image_api_response",
            "route": "api", "provider": "openai", "endpoint": "/v1/images/edits",
            "request": request,
            "response": {
                "httpStatus": 200,
                "outputSha256": "<SHA-256 of actual decoded returned PNG>",
                "actualNativePixels": [PATCH, PATCH],
            },
        },
        "optionalResponseFields": {
            "model": "Only copy an actually returned model value. Omit when absent.",
            "requestId": "Only copy an actually returned request ID. Omit when absent.",
        },
        "modelEvidenceLimit": "Matching request parameters are verified locally. No response model means returned backend remains unverified; no model value is fabricated.",
    }


def validate_record(record: dict, evidence: dict, tile_id: str, hashes: dict) -> str | None:
    require(record.get("schemaVersion") == 1 and record.get("id") == tile_id, f"Record identity/schema mismatch: {tile_id}")
    for label, item in (("record", record), ("evidence", evidence)):
        require(item.get("route") == "api" and item.get("provider") == "openai", f"Explicit OpenAI API provenance required: {tile_id}.{label}")
        request = item.get("request", {})
        require(isinstance(request, dict), f"Missing captured request: {tile_id}.{label}")
        for field, expected in (("model", MODEL), ("quality", QUALITY), ("size", "2160x2160"), ("output_format", "png")):
            require(request.get(field) == expected, f"Wrong or missing request {field}: {tile_id}.{label}")
        for field, key in (("promptSha256", "prompt"), ("referenceSha256", "reference")):
            assert_hash(request.get(field), hashes[key], f"{tile_id}.{label}.request.{field}")
    require(evidence.get("schemaVersion") == 1 and evidence.get("eventType") == "image_api_response", f"Not a captured successful API response: {tile_id}")
    require(evidence.get("endpoint") == "/v1/images/edits", f"Expected image reference edit endpoint: {tile_id}")
    response = evidence.get("response", {})
    require(isinstance(response, dict), f"Missing API response: {tile_id}")
    require(type(response.get("httpStatus")) is int and 200 <= response["httpStatus"] < 300, f"Missing successful API status: {tile_id}")
    require(record.get("actualNativePixels") == [PATCH, PATCH] and response.get("actualNativePixels") == [PATCH, PATCH], f"Actual native size evidence mismatch: {tile_id}")
    require(record.get("resizedAfterGeneration") is False and record.get("finalArtUpscaled") is False, f"Native resize/upscale facts missing or disallowed: {tile_id}")
    for field, key in (("outputSha256", "native"), ("promptSha256", "prompt"), ("referenceSha256", "reference"), ("sourceOutputSha256", "native")):
        assert_hash(record.get(field), hashes[key], f"{tile_id}.{field}")
    assert_hash(response.get("outputSha256"), hashes["native"], f"{tile_id}.response.outputSha256")
    returned_model = response.get("model")
    require(returned_model is None or returned_model == MODEL, f"Returned model conflicts with requested snapshot: {tile_id}")
    require(record.get("backendModelVerified") is not True or returned_model == MODEL, f"Unsubstantiated verified backend assertion: {tile_id}")
    return returned_model


def missing_generation_evidence(patches: list[dict]) -> list[str]:
    missing = []
    for patch in patches:
        for path in (ROOT / patch["outputFile"], ROOT / "native" / f'{patch["id"]}.record.json'):
            if not path.is_file():
                missing.append(relative(path))
    return missing


def load_sources(patches: list[dict]) -> tuple[list[list[np.ndarray]], list[dict]]:
    missing = missing_generation_evidence(patches)
    require(not missing, "Generation evidence incomplete; refusing art output. Missing: " + ", ".join(missing))
    arrays, entries = [], []
    for patch in patches:
        tile_id = patch["id"]
        native = local_path(patch["outputFile"], "outputFile")
        prompt = local_path(patch["promptFile"], "promptFile")
        reference = local_path(patch["layoutReference"], "layoutReference")
        record_path = ROOT / "native" / f"{tile_id}.record.json"
        record = read_json(record_path)
        evidence_path = local_path(record.get("evidenceFile"), f"{tile_id}.evidenceFile")
        require(evidence_path != record_path, f"API capture must be a separate evidence file: {tile_id}")
        evidence = read_json(evidence_path)
        assert_hash(record.get("evidenceSha256"), sha256(evidence_path), f"{tile_id}.evidence")
        hashes = {"native": sha256(native), "prompt": sha256(prompt), "reference": sha256(reference)}
        require(hashes["native"] != hashes["reference"], f"Layout reference cannot be passed off as generated art: {tile_id}")
        returned_model = validate_record(record, evidence, tile_id, hashes)
        require(isinstance(record.get("sourceOutputPath"), str) and record["sourceOutputPath"], f"Original output path missing: {tile_id}")
        original = Path(record["sourceOutputPath"])
        original = (original if original.is_absolute() else ROOT / original).resolve()
        require(original.is_file() and sha256(original) == hashes["native"], f"Original returned PNG byte identity failed: {tile_id}")
        arrays.append(read_pixels(native, (PATCH, PATCH)))
        entries.append({
            "id": tile_id, "row": patch["row"], "column": patch["column"],
            "nativeFile": relative(native), "nativePixels": [PATCH, PATCH], "nativeSha256": hashes["native"],
            "recordFile": relative(record_path), "recordSha256": sha256(record_path),
            "evidenceFile": relative(evidence_path), "evidenceSha256": sha256(evidence_path),
            "promptFile": relative(prompt), "promptSha256": hashes["prompt"],
            "referenceFile": relative(reference), "referenceSha256": hashes["reference"],
            "sourceOutputPath": str(original), "sourceOutputSha256": hashes["native"],
            "route": "api", "requestedModel": MODEL, "requestedQuality": QUALITY,
            "explicitRequestParametersValidated": True, "returnedModel": returned_model,
            "backendModelVerified": returned_model == MODEL,
            "sourceBytesPreserved": True,
        })
    return [arrays[:GRID], arrays[GRID:]], entries


def load_seam_helper():
    spec = importlib.util.spec_from_file_location("city_minimum_seam", HELPER)
    require(spec is not None and spec.loader is not None, f"Cannot load seam helper: {HELPER}")
    module = importlib.util.module_from_spec(spec)
    # No cache/pyc writes to another directory.
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module._minimum_vertical_seam


def blend_exact(left: np.ndarray, right: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    weight = alpha.astype(np.uint32)[..., None]
    result = ((left.astype(np.uint32) * (255 - weight) + right.astype(np.uint32) * weight + 127) // 255).astype(np.uint8)
    identical = np.all(left == right, axis=2)
    require(np.array_equal(result[identical], left[identical]), "Integer blend changed identical input pixels")
    return result


def append_patch(base: np.ndarray, patch: np.ndarray, seam_fn, label: str) -> tuple[np.ndarray, dict]:
    require(base.shape[0] == patch.shape[0] and min(base.shape[1], patch.shape[1]) >= OVERLAP, f"Invalid overlap geometry: {label}")
    left, right = base[:, -OVERLAP:], patch[:, :OVERLAP]
    seam = seam_fn(left, right)
    require(seam.shape == (left.shape[0],) and np.all((seam >= 0) & (seam < OVERLAP)), f"Invalid minimum seam: {label}")
    columns = np.arange(OVERLAP)[None, :]
    mask = np.uint8(columns >= seam[:, None]) * 255
    alpha = np.asarray(Image.fromarray(mask).filter(ImageFilter.GaussianBlur(radius=2)), dtype=np.uint8)
    blended = blend_exact(left, right, alpha)
    pixels = np.concatenate((base[:, :-OVERLAP], blended, patch[:, OVERLAP:]), axis=1)
    difference = np.abs(left.astype(np.int16) - right.astype(np.int16))
    return pixels, {
        "label": label, "overlapPixels": OVERLAP, "seamLength": len(seam),
        "seamMin": int(seam.min()), "seamMax": int(seam.max()),
        "meanAbsoluteInputDifference": float(difference.mean()),
        "p95AbsoluteInputDifference": float(np.percentile(difference, 95)),
        "identicalInputPixelsPreserved": True,
    }


def compose(rows: list[list[np.ndarray]]) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    require(len(rows) == GRID and all(len(row) == GRID for row in rows), "Exactly 2x2 native patches required")
    require(all(image.dtype == np.uint8 and image.shape == (PATCH, PATCH, 3) for row in rows for image in row), "Native patch pixel contract failed")
    strips, metrics = [], []
    for index, row in enumerate(rows):
        strip, metric = append_patch(row[0], row[1], load_seam_helper(), f"row_{index + 1}_horizontal")
        require(strip.shape == (PATCH, ASSEMBLED, 3), "Row strip must be 4208x2160")
        strips.append(strip)
        metrics.append(metric)
    combined_t, metric = append_patch(strips[0].transpose(1, 0, 2), strips[1].transpose(1, 0, 2), load_seam_helper(), "vertical")
    metrics.append(metric)
    combined = combined_t.transpose(1, 0, 2)
    require(combined.shape == (ASSEMBLED, ASSEMBLED, 3), "Pre-crop assembly must be 4208 square")
    final = combined[HALO:HALO + FINAL, HALO:HALO + FINAL].copy()
    require(final.shape == (FINAL, FINAL, 3), "Delivery must be 4096 square")
    return combined, final, metrics


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".writing.json")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_png(path: Path, pixels: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".writing.png")
    Image.fromarray(pixels).save(temporary, format="PNG")
    temporary.replace(path)


def source_metadata() -> dict:
    return {
        "script": {"file": relative(Path(__file__)), "sha256": sha256(Path(__file__))},
        "plan": {"file": relative(PLAN), "sha256": sha256(PLAN)},
        "seamHelper": {"file": str(HELPER), "sha256": sha256(HELPER), "function": "_minimum_vertical_seam"},
    }


def preflight() -> dict:
    _, patches = load_plan()
    QA.mkdir(parents=True, exist_ok=True)
    # Coordinate-coded fixture at actual production dimensions. No art references
    # or fabricated API records enter this fixture.
    y, x = np.indices((ASSEMBLED, ASSEMBLED), dtype=np.uint16)
    canvas = np.stack((x % 256, y % 256, ((x // 256) * 17 + (y // 256) * 31) % 256), axis=2).astype(np.uint8)
    del x, y
    with tempfile.TemporaryDirectory(prefix="_mechanical_fixture_", dir=QA) as folder:
        fixture_dir = Path(folder).resolve()
        require(fixture_dir.is_relative_to(QA.resolve()), "Temporary fixture escaped QA directory")
        rows = []
        for r in range(GRID):
            row = []
            for c in range(GRID):
                path = fixture_dir / f"synthetic_r{r + 1}_c{c + 1}.png"
                crop = canvas[r * CORE:r * CORE + PATCH, c * CORE:c * CORE + PATCH]
                save_png(path, crop)
                row.append(read_pixels(path, (PATCH, PATCH)))
            rows.append(row)
        combined, final, metrics = compose(rows)
        require(np.array_equal(combined, canvas), "Synthetic full assembly orientation/pixel mismatch")
        expected = canvas[HALO:HALO + FINAL, HALO:HALO + FINAL]
        require(np.array_equal(final, expected), "Synthetic 56px outer crop mismatch")
        fixture_final = fixture_dir / "synthetic_result_NOT_ART.png"
        save_png(fixture_final, final)
        require(np.array_equal(read_pixels(fixture_final, (FINAL, FINAL)), expected), "Synthetic PNG roundtrip changed pixels")
        corners = {}
        for label, xx, yy in (("topLeft", 0, 0), ("topRight", FINAL - 1, 0), ("bottomLeft", 0, FINAL - 1), ("bottomRight", FINAL - 1, FINAL - 1), ("fourWayJoin", CORE, CORE)):
            corners[label] = {"deliveryXY": [xx, yy], "fullCanvasXY": [xx + HALO, yy + HALO], "RGB": final[yy, xx].tolist()}
        fixture_hash = sha256(fixture_final)
    require(not fixture_dir.exists(), "Temporary synthetic fixture was not removed")
    samples = np.broadcast_to(np.arange(256, dtype=np.uint8)[:, None, None], (256, 256, 3)).copy()
    weights = np.broadcast_to(np.arange(256, dtype=np.uint8)[None, :], (256, 256))
    require(np.array_equal(blend_exact(samples, samples, weights), samples), "Equal-pixel identity failed for a channel value/weight")
    zero = np.zeros((256, 256, 3), dtype=np.uint8)
    full = np.full_like(zero, 255)
    require(np.array_equal(blend_exact(zero, full, weights), np.repeat(weights[..., None], 3, axis=2)), "Integer blend endpoint/ramp validation failed")
    missing = missing_generation_evidence(patches)
    refusal = None
    if missing:
        try:
            load_sources(patches)
        except EvidenceError as exc:
            refusal = str(exc)
        require(refusal is not None, "Missing generation evidence did not fail closed")
    result = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "mechanical_preflight_passed_NOT_actual_art",
        "actualArtGeneratedByPreflight": False, "apiCalled": False,
        "nativeGenerated": False, "runtimePublished": False,
        **source_metadata(),
        "fixture": {
            "type": "synthetic_coordinate_pixels_only", "nativePatches": 4,
            "nativePixels": [PATCH, PATCH], "assembledPixels": [ASSEMBLED, ASSEMBLED],
            "cropBox": [HALO, HALO, HALO + FINAL, HALO + FINAL], "outputPixels": [FINAL, FINAL],
            "allAssembledPixelsMatchGlobalCoordinates": True, "allFinalPixelsMatchExactCrop": True,
            "pngRoundtripExact": True, "roundtripPngSha256": fixture_hash,
            "temporaryFilesRemoved": True, "savedSyntheticArtwork": False,
            "checkpoints": corners,
        },
        "integerBlend": {"all256EqualValuesAtAll256WeightsExact": True, "blackWhiteRampExact": True},
        "seamMetrics": metrics,
        "realGenerationEvidence": {"missingFiles": missing, "failClosedTest": "passed" if missing else "not_applicable_inputs_exist", "refusal": refusal},
        "productionArtPresent": ART.is_file(),
        "limitations": "Synthetic verification proves crop, orientation and arithmetic only. It does not verify real generated detail, backend identity, style or visual seam continuity.",
    }
    write_json(QA / "mechanical-preflight.json", result)
    return result


def write_qa(final: np.ndarray) -> list[dict]:
    image = Image.fromarray(final)
    entries = []
    for name, box in {
        "center_join_100pct": [CORE - 450, CORE - 450, CORE + 450, CORE + 450],
        "vertical_seam_top_100pct": [CORE - 450, 512, CORE + 450, 1412],
        "vertical_seam_bottom_100pct": [CORE - 450, 2684, CORE + 450, 3584],
        "horizontal_seam_left_100pct": [512, CORE - 450, 1412, CORE + 450],
        "horizontal_seam_right_100pct": [2684, CORE - 450, 3584, CORE + 450],
    }.items():
        path = QA / f"{name}.png"
        save_png(path, np.asarray(image.crop(box)))
        entries.append({"file": relative(path), "kind": "native-pixel-crop", "crop": box, "pixels": [900, 900], "sha256": sha256(path)})
    path = QA / "overview_1024.png"
    save_png(path, np.asarray(image.resize((1024, 1024), Image.Resampling.LANCZOS)))
    entries.append({"file": relative(path), "kind": "downsampled-preview-only", "pixels": [1024, 1024], "sha256": sha256(path)})
    return entries


def validate_saved(report: dict, entries: list[dict]) -> dict:
    require(report.get("nativeSources") == entries, "Source provenance changed since assembly")
    for key, value in source_metadata().items():
        require(report.get(key) == value, f"{key} changed since assembly")
    require(report.get("status") == "candidate_pending_visual_QA_not_published" and report.get("runtimePublished") is False, "Unexpected candidate publication status")
    assert_hash(report.get("output", {}).get("sha256"), sha256(ART), "output")
    pixels = read_pixels(ART, (FINAL, FINAL))
    candidate = Image.fromarray(pixels)
    for item in report.get("qa", []):
        path = local_path(item["file"], "QA artifact")
        assert_hash(item.get("sha256"), sha256(path), "QA artifact")
        expected = candidate.crop(item["crop"]) if item["kind"] == "native-pixel-crop" else candidate.resize((1024, 1024), Image.Resampling.LANCZOS)
        require(np.array_equal(read_pixels(path, tuple(item["pixels"])), np.asarray(expected)), f"QA pixels differ: {path}")
    require(len(report.get("qa", [])) == 6, "Expected six QA artifacts")
    return {"passed": True, "sources": 4, "outputPixels": [FINAL, FINAL], "qaArtifacts": 6}


def assemble() -> dict:
    _, patches = load_plan()
    rows, entries = load_sources(patches)  # All evidence checked before output creation.
    require(not ART.exists() and not REPORT.exists(), "Candidate already exists; retain history and use --check instead of overwriting")
    _, final, metrics = compose(rows)
    save_png(ART, final)
    qa = write_qa(final)
    report = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_pending_visual_QA_not_published", "runtimePublished": False,
        "scope": "One Q64 Tianyong r10_c07 tile; not a complete city",
        **source_metadata(), "nativeSources": entries,
        "requestedModel": MODEL, "requestedQuality": QUALITY,
        "allExplicitRequestParametersValidated": True,
        "backendModelVerified": all(entry["backendModelVerified"] for entry in entries),
        "modelEvidenceLimit": "Local captured API evidence is checked; no server signature or missing response model is invented.",
        "grid": {"rows": GRID, "columns": GRID, "origin": "top-left", "order": "row-major"},
        "nativePixels": [PATCH, PATCH], "corePixels": [CORE, CORE],
        "contextPerSide": HALO, "adjacentOverlap": OVERLAP,
        "assembledBeforeOuterCrop": [ASSEMBLED, ASSEMBLED],
        "cropBox": [HALO, HALO, HALO + FINAL, HALO + FINAL],
        "composition": {
            "method": "minimum-error seam: horizontal rows then vertical strip join",
            "maskGaussianRadiusPixels": 2, "integerBlend": "(left*(255-alpha)+right*alpha+127)//255",
            "identicalInputPixelsPreserved": True, "sourceResampling": False,
            "guidePixelsCompositedIntoFinal": False, "colorMatching": False,
            "globalBlur": False, "sharpening": False,
        },
        "finalArtUpscaled": False, "seamMetrics": metrics,
        "output": {"file": relative(ART), "pixels": [FINAL, FINAL], "format": "PNG", "mode": "RGB", "sha256": sha256(ART)},
        "qa": qa, "visualQa": {"status": "pending", "note": "Review Q style, true native detail and geometry across all seams at 100% and the game's closest camera."},
    }
    report["mechanicalValidation"] = validate_saved(report, entries)
    write_json(REPORT, report)
    return {"candidate": str(ART), "report": str(REPORT), **report["mechanicalValidation"], "status": report["status"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--preflight", action="store_true", help="Synthetic verification only; no API or actual art output.")
    group.add_argument("--record-contract", action="store_true", help="Print required evidence schema; create no record files.")
    group.add_argument("--check", action="store_true", help="Read-only validation of an existing candidate.")
    args = parser.parse_args()
    try:
        if args.record_contract:
            result = record_contract()
        elif args.preflight:
            result = preflight()
        elif args.check:
            _, patches = load_plan()
            _, entries = load_sources(patches)
            result = validate_saved(read_json(REPORT), entries)
        else:
            result = assemble()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (EvidenceError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "refused", "reason": str(exc), "apiCalled": False, "artOutputAuthorizedByThisRun": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
