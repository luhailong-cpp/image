#!/usr/bin/env python3
"""Character-local selection validation, whole-canvas export and offline preview.

No mode synthesizes poses, mirrors images, fits bounding boxes, or changes source
files. --audit writes nothing. --export needs every one of the 68 selected slots.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import sys

from PIL import Image, ImageOps


CHARACTER = "17_ghost_script_calligrapher_boy"
ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT.parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
TOTAL = 68


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return digest(path.read_bytes())


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def local_path(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("Missing file path")
    path = Path(value)
    if not path.is_absolute():
        path = BATCH / path if path.parts[0] == "characters" else ROOT / path
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Path escapes character directory: {value}")
    return path


def image_info(path: Path) -> tuple[Image.Image, dict]:
    with Image.open(path) as source:
        source.verify()
    with Image.open(path) as source:
        if source.format != "PNG" or source.mode != "RGBA":
            raise ValueError("Expected PNG with RGBA mode")
        source.load()
        image = source.copy()
    alpha = image.getchannel("A")
    histogram = alpha.histogram()
    if histogram[0] == 0:
        raise ValueError("No fully transparent pixels")
    if sum(histogram[9:]) == 0:
        raise ValueError("No visible subject with alpha > 8")
    visible = alpha.point(lambda value: 255 if value > 8 else 0)
    bbox = visible.getbbox()
    if bbox[0] == 0 or bbox[1] == 0 or bbox[2] == image.width or bbox[3] == image.height:
        raise ValueError("Visible subject touches canvas edge; inspect clipping")
    # Zero only hidden RGB for comparison; this canonical image is never exported.
    mask = alpha.point(lambda value: 255 if value else 0)
    rgb = Image.composite(image.convert("RGB"), Image.new("RGB", image.size), mask)
    canonical = Image.merge("RGBA", (*rgb.split(), alpha))
    return image, {
        "size": list(image.size), "mode": image.mode, "sha256": sha(path),
        "visibleBBox": list(bbox), "transparentPixels": histogram[0],
        "visiblePixelSha256": digest(canonical.tobytes()),
        "horizontalMirrorPixelSha256": digest(ImageOps.mirror(canonical).tobytes()),
    }


def source_record_errors(record: dict, source: Path, info: dict) -> list[str]:
    problems = []
    if str(record.get("sha256", "")).lower() != info["sha256"]:
        problems.append("source_receipt_sha_mismatch")
    try:
        if local_path(record.get("file")) != source:
            problems.append("source_receipt_file_mismatch")
    except (ValueError, TypeError):
        problems.append("source_receipt_file_invalid")
    for key in ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot",
                "submittedParameters", "evidence", "prompt", "references"):
        if not record.get(key):
            problems.append("source_receipt_missing_" + key)
    try:
        # `prompt` is a saved character-local prompt path. A receipt that also
        # keeps inline prompt text may give its saved path as `promptFile`.
        prompt_path = local_path(record.get("promptFile", record.get("prompt")))
        if not prompt_path.is_file() or not prompt_path.read_text(encoding="utf-8-sig").strip():
            problems.append("source_receipt_prompt_file_missing_or_empty")
    except (OSError, ValueError, TypeError):
        problems.append("source_receipt_prompt_file_invalid")
    references = record.get("references")
    if not isinstance(references, list) or not references:
        problems.append("source_receipt_references_not_nonempty_list")
    else:
        for index, reference in enumerate(references):
            try:
                value = reference.get("path") if isinstance(reference, dict) else None
                if not isinstance(value, str) or not value:
                    raise ValueError("Missing reference path")
                reference_path = Path(value)
                if not reference_path.is_absolute():
                    # External portrait/idle/design references are read-only.
                    # Relative references try the character, then repository.
                    character_reference = ROOT / reference_path
                    reference_path = character_reference if character_reference.is_file() else BATCH.parents[1] / reference_path
                if not reference_path.is_file():
                    raise ValueError("Reference file does not exist")
            except (OSError, ValueError, TypeError):
                problems.append(f"source_receipt_reference_path_invalid:{index}")
    for field in ("submittedParameters", "configSnapshot"):
        values = record.get(field)
        if not isinstance(values, dict):
            problems.append("source_receipt_" + field + "_not_object")
        else:
            for key in ("model", "quality"):
                if key not in values:
                    problems.append("source_receipt_" + field + "_missing_" + key)
    if [record.get("width"), record.get("height")] != info["size"]:
        problems.append("source_receipt_native_dimensions_mismatch")
    for key in ("actualModel", "actualQuality"):
        if key not in record:
            problems.append("source_receipt_missing_" + key)
        elif record[key] is None and not record.get("unverifiedReason"):
            problems.append("source_receipt_unknown_without_reason_" + key)
    return problems


def inspect_selection() -> tuple[dict, list[dict]]:
    report = {
        "character": CHARACTER, "generatedAt": datetime.now(timezone.utc).isoformat(),
        "expected": TOTAL, "validSelectedSlots": 0, "selectionComplete": False,
        "technicalPreflightPassed": False, "issues": [], "slots": [],
        "visualApproval": "pending", "clientIntegration": "not_integrated",
        "runtimeAcceptance": "not_tested",
        "note": "Technical checks cannot establish distinct poses or animation quality.",
    }
    selected, source_slots, pixel_slots, mirror_slots = [], {}, {}, {}
    for action, (count, interval) in ACTIONS.items():
        for direction in DIRECTIONS:
            selection_path = ROOT / "selections" / f"{action}-{direction}.json"
            entries = {}
            selection_error = None
            selection_sha = None
            try:
                selection = read_json(selection_path)
                selection_sha = sha(selection_path)
                if selection.get("action") != action or selection.get("direction") != direction:
                    raise ValueError("Selection action/direction mismatch")
                raw_entries = selection.get("entries")
                if not isinstance(raw_entries, list):
                    raise ValueError("Selection entries must be a list")
                indices = [entry.get("frame") if isinstance(entry, dict) else None for entry in raw_entries]
                if any(type(index) is not int or index < 1 or index > count for index in indices):
                    raise ValueError("Invalid frame index")
                if len(indices) != len(set(indices)):
                    raise ValueError("Duplicate selected slot")
                if indices != sorted(indices):
                    raise ValueError("Entries must be in increasing frame order")
                entries = {entry["frame"]: entry for entry in raw_entries}
                if selection.get("status") != "selected":
                    # Retain valid candidates for a partial preview, while the
                    # global issue makes full export fail even with 68 files.
                    report["issues"].append({"selection": relative(selection_path),
                                             "error": "selection_status_must_be_selected_for_export",
                                             "actualStatus": selection.get("status")})
            except (OSError, ValueError, TypeError) as error:
                selection_error = str(error)
                report["issues"].append({"selection": relative(selection_path), "error": selection_error})
            for frame in range(1, count + 1):
                slot = {"action": action, "direction": direction, "frame": frame,
                        "frameDurationMs": interval, "issues": []}
                report["slots"].append(slot)
                if selection_error or frame not in entries:
                    slot["issues"].append("missing_or_invalid_selection" if selection_error else "missing_selected_slot")
                    continue
                entry = entries[frame]
                try:
                    source = local_path(entry.get("file"))
                    record_path = local_path(entry.get("generationRecord"))
                    image, info = image_info(source)
                    slot.update(source=relative(source), sourceInfo=info,
                                generationRecord=relative(record_path))
                    if min(image.size) < 1024:
                        slot["issues"].append("native_canvas_below_1024_no_upscale_allowed")
                    if str(entry.get("sha256", "")).lower() != info["sha256"]:
                        slot["issues"].append("selection_sha_missing_or_mismatch")
                    record = read_json(record_path)
                    slot["issues"].extend(source_record_errors(record, source, info))
                    key = f"{action}/{direction}/{frame:02d}"
                    for seen, value, code in ((source_slots, str(source), "source_reused"),
                                              (pixel_slots, (tuple(info["size"]), info["visiblePixelSha256"]), "duplicate_visible_pixels")):
                        if value in seen:
                            slot["issues"].append(code + ":" + seen[value])
                        else:
                            seen[value] = key
                    mirrored_key = (tuple(info["size"]), info["visiblePixelSha256"])
                    if mirrored_key in mirror_slots:
                        slot["issues"].append("exact_mirror_of:" + mirror_slots[mirrored_key])
                    mirror_slots[(tuple(info["size"]), info["horizontalMirrorPixelSha256"])] = key
                    if not slot["issues"]:
                        selected.append({"slot": slot, "image": image, "source": source,
                                         "sourceRecord": record, "sourceReceipt": record_path,
                                         "sourceReceiptSha256": sha(record_path),
                                         "selection": selection_path, "selectionSha256": selection_sha})
                except (OSError, ValueError, TypeError) as error:
                    slot["issues"].append(str(error))
    sizes = {tuple(entry["slot"]["sourceInfo"]["size"]) for entry in selected}
    if len(sizes) > 1:
        report["issues"].append({"error": "mixed_native_canvases_need_explicit_review", "sizes": sorted(sizes)})
    report["validSelectedSlots"] = len(selected)
    report["missingOrInvalidSlots"] = [f"{s['action']}/{s['direction']}/{s['frame']:02d}" for s in report["slots"] if s["issues"]]
    report["selectionComplete"] = len(selected) == TOTAL
    report["technicalPreflightPassed"] = len(selected) == TOTAL and not report["issues"]
    return report, selected


def audit_runtime(report: dict) -> None:
    records, hashes, mirrored_hashes = [], {}, {}
    expected_paths = set()
    for slot in report["slots"]:
        path = ROOT / "runtime" / slot["action"] / slot["direction"] / f"{slot['frame']:02d}.png"
        expected_paths.add(path)
        record_path = path.with_suffix(".generation.json")
        item = {"file": relative(path), "exists": path.is_file(), "issues": []}
        records.append(item)
        if not item["exists"]:
            item["issues"].append("missing_runtime_frame")
            continue
        try:
            _, info = image_info(path)
            item.update(info)
            if info["size"] != [1024, 1024]:
                item["issues"].append("runtime_dimensions_not_1024")
            record = read_json(record_path)
            if record.get("sha256") != info["sha256"] or local_path(record.get("file")) != path:
                item["issues"].append("runtime_receipt_file_or_sha_mismatch")
            origin = record.get("derivedFrom", {})
            source, source_receipt = local_path(origin.get("file")), local_path(origin.get("generationRecord"))
            if sha(source) != origin.get("sha256") or sha(source_receipt) != origin.get("generationRecordSha256"):
                item["issues"].append("runtime_source_chain_sha_mismatch")
            original = read_json(source_receipt)
            if original.get("sha256") != origin.get("sha256"):
                item["issues"].append("runtime_source_receipt_sha_mismatch")
            if origin.get("file") != slot.get("source") or origin.get("sha256") != slot.get("sourceInfo", {}).get("sha256"):
                item["issues"].append("runtime_not_current_selection")
            evidence = record.get("evidence", {})
            if sha(local_path(evidence.get("selection"))) != evidence.get("selectionSha256"):
                item["issues"].append("runtime_selection_sha_mismatch")
            operation = record.get("operation", {})
            if operation.get("kind") != "whole_canvas_uniform_resize_and_fixed_padding" or not operation.get("noPoseSynthesis"):
                item["issues"].append("runtime_operation_missing_or_unexpected")
            pixel_sha = info["visiblePixelSha256"]
            if pixel_sha in hashes:
                item["issues"].append("duplicate_runtime_pixels:" + hashes[pixel_sha])
            if pixel_sha in mirrored_hashes:
                item["issues"].append("exact_runtime_mirror_of:" + mirrored_hashes[pixel_sha])
            hashes[pixel_sha] = relative(path)
            mirrored_hashes[info["horizontalMirrorPixelSha256"]] = relative(path)
        except (OSError, ValueError, TypeError) as error:
            item["issues"].append(str(error))
    extras = sorted(relative(path) for path in (ROOT / "runtime").rglob("*.png") if path not in expected_paths)
    report["runtime"] = {"expected": TOTAL, "present": sum(item["exists"] for item in records),
                         "framesWithIssues": sum(bool(item["issues"]) for item in records),
                         "unexpectedPngs": extras, "frames": records,
                         "technicalAuditPassed": not extras and all(not item["issues"] for item in records)}


def render_export(entry: dict) -> tuple[bytes, dict]:
    image = entry["image"]
    width, height = image.size
    factor = 1024 / max(width, height)
    size = (round(width * factor), round(height * factor))
    offset = ((1024 - size[0]) // 2, (1024 - size[1]) // 2)
    resized = image if image.size == size else image.resize(size, Image.Resampling.LANCZOS)
    final = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    final.paste(resized, offset)  # Preserve the original alpha rather than multiply it.
    buffer = io.BytesIO()
    final.save(buffer, format="PNG")
    return buffer.getvalue(), {"kind": "whole_canvas_uniform_resize_and_fixed_padding",
                             "nativeCanvas": [width, height], "outputCanvas": [1024, 1024],
                             "factor": factor, "scaledWholeCanvas": list(size), "offset": list(offset),
                             "filter": "none" if image.size == size else "Pillow LANCZOS",
                             "noFramewiseBoundingBoxFit": True, "noFramewiseRecentering": True,
                             "noMirror": True, "noPoseSynthesis": True, "alphaThresholdApplied": None}


def export(report: dict, selected: list[dict]) -> None:
    if not report["technicalPreflightPassed"]:
        raise ValueError("Refuse export: all 68 slots and provenance must pass preflight")
    outputs = []
    now = datetime.now(timezone.utc).isoformat()
    for entry in selected:
        slot = entry["slot"]
        path = ROOT / "runtime" / slot["action"] / slot["direction"] / f"{slot['frame']:02d}.png"
        record_path = path.with_suffix(".generation.json")
        if path.exists() or record_path.exists():
            raise ValueError(f"Refuse overwrite: {path} or {record_path}")
        # Recheck the source immediately before rendering to detect concurrent writes.
        if sha(entry["source"]) != slot["sourceInfo"]["sha256"] or sha(entry["sourceReceipt"]) != entry["sourceReceiptSha256"]:
            raise ValueError("Source or generation record changed during preflight")
        png, operation = render_export(entry)
        source = entry["sourceRecord"]
        record = {"file": relative(path), "sha256": digest(png), "width": 1024, "height": 1024,
                  "format": "PNG RGBA", "derivedAt": now,
                  "generatedAt": source["generatedAt"], "generatedAtEvidence": source["generatedAtEvidence"],
                  "tool": "Pillow deterministic whole-canvas export", "route": "derived",
                  "configSnapshot": source["configSnapshot"], "submittedParameters": {"model": None, "quality": None},
                  "actualModel": source["actualModel"], "actualQuality": source["actualQuality"],
                  "unverifiedReason": source.get("unverifiedReason"),
                  "prompt": source["prompt"], "references": source["references"],
                  "derivedFrom": {"file": relative(entry["source"]), "sha256": slot["sourceInfo"]["sha256"],
                                  "nativeDimensions": slot["sourceInfo"]["size"],
                                  "generationRecord": relative(entry["sourceReceipt"]),
                                  "generationRecordSha256": entry["sourceReceiptSha256"]},
                  "evidence": {"selection": relative(entry["selection"]), "selectionSha256": entry["selectionSha256"]},
                  "operation": operation, "visualApproval": "pending", "clientIntegration": "not_integrated",
                  "runtimeAcceptance": "not_tested"}
        outputs.extend(((record_path, (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")), (path, png)))
    # Every pose has been rendered before any write; xb also protects concurrent WIP.
    for path, data in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)


def make_preview(report: dict) -> None:
    destination = ROOT / "preview"
    destination.mkdir(parents=True, exist_ok=True)
    sets = []
    for action, (count, interval) in ACTIONS.items():
        for direction in DIRECTIONS:
            frames = []
            for slot in report["slots"]:
                if (slot["action"], slot["direction"]) != (action, direction):
                    continue
                runtime = ROOT / "runtime" / action / direction / f"{slot['frame']:02d}.png"
                runtime_item = next((item for item in report["runtime"]["frames"] if item["file"] == relative(runtime)), None)
                path = runtime if runtime_item and not runtime_item["issues"] else (ROOT / slot["source"] if slot.get("source") and not slot["issues"] else None)
                frames.append({"frame": slot["frame"], "url": Path(os.path.relpath(path, destination)).as_posix() if path else None,
                               "source": "runtime" if path == runtime else "selected native candidate",
                               "issues": slot["issues"]})
            sets.append({"action": action, "direction": direction, "interval": interval, "count": count, "frames": frames})
    data = json.dumps({"sets": sets, "report": report}, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    template = Path(__file__).with_name("preview_template.html").read_text(encoding="utf-8")
    (destination / "index.html").write_text(template.replace("__DATA_JSON__", data), encoding="utf-8")
    (destination / "technical-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", action="store_true", help="Print read-only selection/runtime audit")
    parser.add_argument("--export", action="store_true", help="Export exactly 68 validated slots; refuse overwrites")
    parser.add_argument("--preview", action="store_true", help="Write offline preview, explicitly partial if incomplete")
    args = parser.parse_args()
    if ROOT.name != CHARACTER:
        raise ValueError("Character directory mismatch")
    report, selected = inspect_selection()
    if args.export:
        export(report, selected)
    audit_runtime(report)
    if args.preview:
        make_preview(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["technicalPreflightPassed"] and report["runtime"]["technicalAuditPassed"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
