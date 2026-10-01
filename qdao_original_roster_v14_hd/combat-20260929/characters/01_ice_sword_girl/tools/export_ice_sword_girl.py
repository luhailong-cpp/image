#!/usr/bin/env python3
"""Explicit, character-local selection audit, uniform export and timed browser QA.

Default is read-only. Preview and publish destinations never overwrite files.
Pixel checks establish exact nonduplication only; actual pose and animation
approval must be recorded by a reviewer after playback.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import sys

from PIL import Image

CHARACTER = "01_ice_sword_girl"
CHAR_DIR = Path(__file__).resolve().parents[1]
BATCH = CHAR_DIR.parents[1]
REPO = BATCH.parents[1]
COUNTS = {"hit": 6, "attack": 12, "cast": 16}
TIMING = {"hit": 40, "attack": 30, "cast": 45}
DIRECTIONS = ("E", "W")
EXPECTED = [(a, d, f) for a, n in COUNTS.items() for d in DIRECTIONS for f in range(1, n + 1)]


def fail(message):
    raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(path.read_bytes())


def json_read(path):
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        fail(f"JSON object required: {path}")
    return value


def inside(path, root=CHAR_DIR):
    path = path.resolve()
    if not path.is_relative_to(root.resolve()):
        fail(f"Path outside authorized directory: {path}")
    return path


def local_path(value, must_exist=True):
    if not isinstance(value, str) or not value:
        fail("Nonempty local path required")
    path = Path(value.replace("\\", "/"))
    if not path.is_absolute():
        path = (BATCH if path.parts[0] == "characters" else CHAR_DIR) / path
    path = inside(path)
    if must_exist and not path.is_file():
        fail(f"Missing selected source or record: {path}")
    return path


def repo_reference(value):
    if not isinstance(value, str) or not value:
        fail("Missing prompt/reference path")
    path = Path(value.replace("\\", "/"))
    if not path.is_absolute():
        candidates = [REPO / path, BATCH / path, CHAR_DIR / path]
        path = next((candidate for candidate in candidates if candidate.is_file()), candidates[0])
    path = inside(path, REPO)
    if not path.is_file():
        fail(f"Missing prompt/reference: {path}")
    return path


def rel(path):
    return path.relative_to(CHAR_DIR).as_posix()


def geometry(image):
    alpha = image.getchannel("A")
    hist = alpha.histogram()
    mask = alpha.point(lambda value: 255 if value > 8 else 0)
    box = mask.getbbox()
    if box is None or hist[0] == 0:
        fail("Image must contain a visible subject and fully transparent pixels")
    return {"visibleBBoxAlphaOver8": list(box), "transparentPixels": hist[0],
            "visiblePixelsAlphaOver8": sum(hist[9:]), "alphaExtrema": list(alpha.getextrema()),
            "visibleTouchesEdge": box[0] == 0 or box[1] == 0 or box[2] == image.width or box[3] == image.height}


def signature(image, crop=False, mirror=False):
    # Pixels at alpha <= 8 and hidden RGB cannot disguise an exact copied pose.
    mask = image.getchannel("A").point(lambda value: 255 if value > 8 else 0)
    clean = Image.new("RGBA", image.size)
    clean.paste(image, (0, 0), mask)
    if crop:
        clean = clean.crop(mask.getbbox())
    if mirror:
        clean = clean.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return sha(str(clean.size).encode() + clean.tobytes())


def inspect_source(path):
    with Image.open(path) as probe:
        if probe.format != "PNG" or probe.mode != "RGBA":
            fail(f"Original must be RGBA PNG: {path}")
        probe.verify()
    with Image.open(path) as opened:
        image = opened.copy()
    if image.width != image.height or image.width < 1024:
        fail(f"Expected native square canvas >= 1024; contact-sheet cells cannot qualify: {path} {image.size}")
    geom = geometry(image)
    if geom["visibleTouchesEdge"]:
        fail(f"Visible source touches edge; visually inspect or redraw before selection: {path}")
    return image, geom


def validate_receipt(record_path, source_path, source_sha, source_size, seen=None):
    seen = set() if seen is None else seen
    if record_path in seen:
        fail(f"Circular provenance chain: {record_path}")
    seen.add(record_path)
    data = json_read(record_path)
    if local_path(data.get("file")) != source_path or data.get("sha256", "").lower() != source_sha:
        fail(f"Source/receipt file or SHA mismatch: {record_path}")
    if (data.get("width"), data.get("height")) != source_size:
        fail(f"Source/receipt native dimensions mismatch: {record_path}")
    if data.get("derivedFrom"):
        derivation = data["derivedFrom"]
        if not data.get("operation"):
            fail(f"Derived record requires operation: {record_path}")
        parent = local_path(derivation["file"])
        parent_record = local_path(derivation["generationRecord"])
        parent_sha = file_sha(parent)
        if derivation.get("sha256") != parent_sha:
            fail(f"Derived source SHA mismatch: {record_path}")
        if derivation.get("generationRecordSha256") and derivation["generationRecordSha256"] != file_sha(parent_record):
            fail(f"Derived source receipt SHA mismatch: {record_path}")
        with Image.open(parent) as original:
            parent_size = original.size
        validate_receipt(parent_record, parent, parent_sha, parent_size, seen)
    else:
        required = ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot",
                    "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references")
        missing = [name for name in required if name not in data]
        if missing:
            fail(f"Missing provenance fields {missing}: {record_path}")
        if not data["generatedAt"] or not data["generatedAtEvidence"] or not data["evidence"]:
            fail(f"Generation/time evidence cannot be empty: {record_path}")
        if (data["actualModel"] is None or data["actualQuality"] is None) and not data.get("unverifiedReason"):
            fail(f"Unknown returned model/quality needs unverifiedReason: {record_path}")
        repo_reference(data["prompt"])
        if not isinstance(data["references"], list) or not data["references"]:
            fail(f"References required: {record_path}")
        for reference in data["references"]:
            if not isinstance(reference, dict) or not reference.get("role"):
                fail(f"Reference path and role required: {record_path}")
            repo_reference(reference.get("path"))
    return data


def load_selection(path):
    selection = json_read(path)
    if selection.get("schemaVersion") != 1 or selection.get("character") != CHARACTER:
        fail("Selection requires schemaVersion 1 and character 01_ice_sword_girl")
    if selection.get("status") not in ("partial", "complete"):
        fail("Selection status must be partial or complete")
    transform = selection.get("exportTransform", {})
    if transform.get("mode") != "normalized_whole_canvas":
        fail("Explicit normalized_whole_canvas transform required")
    scale = transform.get("contentScale")
    if isinstance(scale, bool) or not isinstance(scale, (float, int)) or not math.isfinite(scale) or not 0 < scale <= 1:
        fail("contentScale must be a finite number in (0,1]")
    for direction in DIRECTIONS:
        offset = transform.get("offsetByDirection", {}).get(direction)
        if not isinstance(offset, list) or len(offset) != 2 or any(type(v) is not int for v in offset):
            fail(f"Fixed integer offsetByDirection.{direction} required")
    sequences = selection.get("sequences")
    if not isinstance(sequences, list) or len(sequences) != 6:
        fail("Exactly six explicit sequences required, including empty partial sequences")
    entries, groups, sources = [], set(), set()
    for sequence in sequences:
        action, direction = sequence.get("action"), sequence.get("direction")
        group = (action, direction)
        if action not in COUNTS or direction not in DIRECTIONS or group in groups:
            fail(f"Unknown or duplicate sequence: {group}")
        groups.add(group)
        status = sequence.get("status")
        if status not in ("partial", "complete"):
            fail(f"Sequence status must be explicit: {group}")
        frames = sequence.get("frames")
        if not isinstance(frames, list):
            fail(f"Sequence frames must be an array: {group}")
        indices = [entry.get("frame") for entry in frames]
        if any(type(i) is not int or i < 1 or i > COUNTS[action] for i in indices) or indices != sorted(set(indices)):
            fail(f"Frames must be unique increasing integers 1..{COUNTS[action]}: {group}")
        if status == "complete" and indices != list(range(1, COUNTS[action] + 1)):
            fail(f"Complete sequence has missing slots: {group}")
        for frame in frames:
            source, receipt = local_path(frame.get("file")), local_path(frame.get("generationRecord"))
            if source in sources:
                fail(f"One source selected into multiple slots: {source}")
            sources.add(source)
            digest = file_sha(source)
            if frame.get("sha256", "").lower() != digest:
                fail(f"Mandatory selection SHA mismatch: {source}")
            image, geom = inspect_source(source)
            record = validate_receipt(receipt, source, digest, image.size)
            entries.append({"key": (action, direction, frame["frame"]), "source": source,
                            "sourceSha256": digest, "receipt": receipt, "receiptSha256": file_sha(receipt),
                            "sourceRecord": record, "image": image, "nativeGeometry": geom})
    complete = len(entries) == 68 and selection["status"] == "complete" and all(s["status"] == "complete" for s in sequences)
    if selection["status"] == "complete" and not complete:
        fail("Top-level complete requires all six complete sequences and all 68 slots")
    return selection, sorted(entries, key=lambda row: EXPECTED.index(row["key"])), complete


def duplicate_check(entries, image_key):
    visible, cropped, mirrored = {}, {}, {}
    for entry in entries:
        image, key = entry[image_key], entry["key"]
        digest, crop_digest = signature(image), signature(image, crop=True)
        mirror_digest = signature(image, crop=True, mirror=True)
        if digest in visible or crop_digest in cropped:
            fail(f"Exact visible/cropped duplicate in {image_key}: {key} and {visible.get(digest, cropped.get(crop_digest))}")
        if crop_digest in mirrored or mirror_digest in cropped:
            fail(f"Exact horizontally mirrored pose in {image_key}: {key} and {mirrored.get(crop_digest, cropped.get(mirror_digest))}")
        visible[digest], cropped[crop_digest], mirrored[mirror_digest] = key, key, key
        entry[image_key + "Signatures"] = {"visibleAlphaOver8": digest, "croppedVisibleAlphaOver8": crop_digest,
                                          "mirroredCroppedVisibleAlphaOver8": mirror_digest}


def render(entries, selection, selection_path):
    transform = selection["exportTransform"]
    side = round(1024 * transform["contentScale"])
    if side < 1:
        fail("Transform yields an empty canvas")
    derived_at = datetime.now(timezone.utc).isoformat()
    for entry in entries:
        action, direction, frame = entry["key"]
        original = entry["image"]
        scaled = original.resize((side, side), Image.Resampling.LANCZOS)
        x, y = transform["offsetByDirection"][direction]
        box = scaled.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if box is None or box[0] + x < 0 or box[1] + y < 0 or box[2] + x > 1024 or box[3] + y > 1024:
            fail(f"Fixed transform would crop visible subject: {entry['key']}")
        output = Image.new("RGBA", (1024, 1024))
        output.paste(scaled, (x, y))
        geom = geometry(output)
        if geom["visibleTouchesEdge"]:
            fail(f"Output subject touches edge: {entry['key']}")
        entry["output"] = output
        buffer = io.BytesIO()
        output.save(buffer, format="PNG")
        entry["png"] = buffer.getvalue()
        entry["destination"] = CHAR_DIR / "runtime" / action / direction / f"{frame:02d}.png"
        entry["derivedReceipt"] = CHAR_DIR / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{frame:02d}.json"
        source = entry["sourceRecord"]
        entry["record"] = {
            "file": rel(entry["destination"]), "sha256": sha(entry["png"]), "width": 1024, "height": 1024,
            "format": "PNG RGBA", "derivedAt": derived_at, "generatedAt": source.get("generatedAt"),
            "generatedAtEvidence": source.get("generatedAtEvidence"), "tool": "Pillow", "route": "derived",
            "configSnapshot": source.get("configSnapshot"), "submittedParameters": {"model": None, "quality": None},
            "actualModel": source.get("actualModel"), "actualQuality": source.get("actualQuality"),
            "unverifiedReason": source.get("unverifiedReason"), "prompt": source.get("prompt"),
            "references": source.get("references"),
            "evidence": {"selection": rel(selection_path), "selectionSha256": file_sha(selection_path)},
            "derivedFrom": {"file": rel(entry["source"]), "sha256": entry["sourceSha256"],
                            "generationRecord": rel(entry["receipt"]), "generationRecordSha256": entry["receiptSha256"]},
            "operation": {"kind": "normalized_whole_canvas_uniform_downsample_fixed_direction_offset",
                          "filter": "Pillow LANCZOS", "transform": transform, "nativeCanvas": list(original.size),
                          "scaledWholeCanvas": [side, side], "wholeCanvasFactor": side / original.width,
                          "offset": [x, y], "noFramewiseBoundingBoxScale": True, "noFramewiseRecentering": True,
                          "noMirrorOrPoseSynthesis": True, "noFaintAlphaRemoval": True},
            "nativeGeometry": entry["nativeGeometry"], "outputGeometry": geom,
            "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}
    duplicate_check(entries, "output")
    for entry in entries:
        entry["record"]["pixelAudit"] = {"source": entry["imageSignatures"], "output": entry["outputSignatures"],
                                          "comparisonAlphaThreshold": 8,
                                          "limitation": "Exact pixel and mirror checks cannot certify unique poses or visual animation quality."}


def write_new(path, data):
    inside(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def preview_html(entries, complete):
    sets = []
    for action, count in COUNTS.items():
        for direction in DIRECTIONS:
            by_frame = {row["key"][2]: row for row in entries if row["key"][:2] == (action, direction)}
            sets.append({"label": f"{action}/{direction}", "ms": TIMING[action], "count": count,
                         "frames": [{"number": f, "url": f"frames/{action}/{direction}/{f:02d}.png" if f in by_frame else None}
                                    for f in range(1, count + 1)]})
    data = json.dumps(sets).replace("<", "\\u003c")
    template = (Path(__file__).with_name("preview_ice_sword_girl.html")).read_text(encoding="utf-8")
    return template.replace("__SETS__", data).replace("__SELECTION_STATUS__", "complete / 68 selected" if complete else "partial / incomplete; missing slots remain visible")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True, help="Character-local explicit six-sequence JSON")
    parser.add_argument("--preview-dir", type=Path, help="New character-local directory; writes rendered technical preview")
    parser.add_argument("--report", type=Path, help="New character-local JSON report file")
    parser.add_argument("--publish", action="store_true", help="Requires complete 68-slot selection; no overwrite")
    args = parser.parse_args()
    selection_path = inside(args.selection)
    selection_sha = file_sha(selection_path)
    selection, entries, complete = load_selection(selection_path)
    duplicate_check(entries, "image")
    render(entries, selection, selection_path)
    present = {row["key"] for row in entries}
    missing = [f"{a}/{d}/{f:02d}" for a, d, f in EXPECTED if (a, d, f) not in present]
    report = {"schemaVersion": 1, "character": CHARACTER, "generatedAt": datetime.now(timezone.utc).isoformat(),
              "selection": rel(selection_path), "selectionSha256": selection_sha,
              "selectionStatus": selection["status"], "selectedSlots": len(entries), "expectedSlots": 68,
              "missingSlots": missing, "complete": complete, "technicalSelectedFramesPassed": True,
              "technicalFullContractPassed": complete, "visualApproval": "pending",
              "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
              "normalFrameDurationMs": TIMING, "exportTransform": selection["exportTransform"],
              "frames": [row["record"] for row in entries],
              "limitations": ["Exact duplicate and mirror checks do not prove independent drawing or distinct poses.",
                              "No visual playback approval is implied by preview creation.",
                              "No client integration or runtime validation was performed."]}
    preview = inside(args.preview_dir) if args.preview_dir else None
    report_path = inside(args.report) if args.report else None
    if preview and preview.exists():
        fail(f"Preview directory already exists; choose a fresh path: {preview}")
    if report_path and report_path.exists():
        fail(f"Report exists: {report_path}")
    if args.publish:
        if not complete:
            fail(f"Publication refused: complete six-group selection with 68 slots required; have {len(entries)}")
        for entry in entries:
            for path in (entry["destination"], entry["derivedReceipt"]):
                if path.exists():
                    fail(f"Refuse to overwrite existing runtime/receipt: {path}")
    # Recheck mutable inputs immediately before any writes.
    if file_sha(selection_path) != report["selectionSha256"]:
        fail("Selection changed during audit; retry")
    for entry in entries:
        if file_sha(entry["source"]) != entry["sourceSha256"] or file_sha(entry["receipt"]) != entry["receiptSha256"]:
            fail(f"Source/receipt changed during audit: {entry['key']}")
    if preview:
        for row in entries:
            action, direction, frame = row["key"]
            write_new(preview / "frames" / action / direction / f"{frame:02d}.png", row["png"])
        write_new(preview / "index.html", preview_html(entries, complete).encode("utf-8"))
        write_new(preview / "technical-report.json", encoded(report))
    if report_path:
        write_new(report_path, encoded(report))
    if args.publish:
        for row in entries:
            write_new(row["derivedReceipt"], encoded(row["record"]))
            write_new(row["destination"], row["png"])
    print(json.dumps({"character": CHARACTER, "selectedSlots": len(entries), "missingSlots": len(missing),
                      "complete": complete, "technicalSelectedFramesPassed": True, "technicalFullContractPassed": complete,
                      "published": len(entries) if args.publish else 0,
                      "preview": str(preview / "index.html") if preview else None,
                      "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"ice_sword_girl export failed: {error}", file=sys.stderr)
        sys.exit(2)
