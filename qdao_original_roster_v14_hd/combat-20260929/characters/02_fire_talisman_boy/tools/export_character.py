"""Strict, additive export for 02_fire_talisman_boy only.

Requires six complete explicit selections and one fixed whole-canvas transform.
Without --publish or --preview-dir, only reads and validates inputs.
Technical success never sets visual approval or client acceptance.
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

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT.parents[1]
COUNTS = {"hit": 6, "attack": 12, "cast": 16}
TIMING = {"hit": 40, "attack": 30, "cast": 45}
EXPECTED = {(a, d, n) for a, count in COUNTS.items() for d in ("E", "W") for n in range(1, count + 1)}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    return digest(path.read_bytes())


def relative(path):
    return path.relative_to(ROOT).as_posix()


def own_path(value, must_exist=True):
    path = Path(value)
    if not path.is_absolute():
        path = BATCH / path if path.parts[0] == "characters" else ROOT / path
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Path leaves this character: {value}")
    if must_exist and not path.is_file():
        raise ValueError(f"Input file missing: {path}")
    return path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def geometry(image):
    alpha = np.asarray(image)[:, :, 3]
    ys, xs = np.where(alpha > 8)
    if not len(xs):
        raise ValueError("No visible image pixels")
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    if not np.any(alpha == 0):
        raise ValueError("No fully transparent pixels")
    return {"visibleBBox": bbox, "transparentPixels": int(np.count_nonzero(alpha == 0)),
            "visibleTouchesEdge": bbox[0] == 0 or bbox[1] == 0 or bbox[2] == image.width or bbox[3] == image.height}


def visible_hashes(image):
    # Ignore all hidden RGB and very faint alpha noise so neither can conceal
    # copied poses. Tight crops also detect exact copies shifted on the canvas.
    array = np.array(image)
    array[array[:, :, 3] <= 8] = 0
    ys, xs = np.where(array[:, :, 3] > 8)
    crop = array[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    header = str(crop.shape).encode("ascii")
    return {"visiblePixelSha256": digest(array.tobytes()),
            "visibleCropSha256": digest(header + crop.tobytes()),
            "mirroredVisibleCropSha256": digest(header + crop[:, ::-1].tobytes())}


def read_native(path):
    with Image.open(path) as source:
        if source.format != "PNG" or source.mode != "RGBA":
            raise ValueError(f"Native file must be PNG RGBA: {path}")
        source.load()
        image = source.copy()
    if min(image.size) < 1024:
        raise ValueError(f"Native canvas below 1024: {path} {image.size}")
    geom = geometry(image)
    if geom["visibleTouchesEdge"]:
        raise ValueError(f"Subject touches native canvas edge: {path}")
    return image, geom


def validate_receipt(receipt, path, source, sha, image):
    required = ("file", "sha256", "generatedAt", "tool", "route", "configSnapshot",
                "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references")
    absent = [key for key in required if key not in receipt]
    if absent:
        raise ValueError(f"Receipt lacks fields {absent}: {path}")
    if str(receipt["sha256"]).lower() != sha or own_path(receipt["file"]) != source:
        raise ValueError(f"Source/receipt file or hash mismatch: {path}")
    if not receipt["generatedAt"] or not (receipt.get("generatedAtEvidence") or receipt["evidence"].get("timestamp")):
        raise ValueError(f"Receipt must state generation time and its evidence: {path}")
    if not receipt["prompt"] or not receipt["references"] or not receipt["configSnapshot"]:
        raise ValueError(f"Receipt has empty prompt/references/config: {path}")
    if any(receipt[key] is None for key in ("actualModel", "actualQuality")) and not receipt.get("unverifiedReason"):
        raise ValueError(f"Unknown model/quality needs explicit reason: {path}")
    if (receipt.get("width"), receipt.get("height")) != image.size:
        raise ValueError(f"Native dimensions in receipt disagree: {path}")
    for ref in receipt["references"]:
        if not isinstance(ref, dict) or not ref.get("path") or not (ref.get("role") or ref.get("purpose")):
            raise ValueError(f"Every reference must have path and role/purpose: {path}")


def load_selection(paths):
    entries, keys, sources, groups = [], set(), set(), set()
    for value in paths:
        path = own_path(value)
        data = read_json(path)
        if not isinstance(data, dict) or data.get("status") == "partial":
            raise ValueError(f"Incomplete selection document: {path}")
        sets = data.get("sets", [data])
        for selected in sets:
            action, direction = selected.get("action"), selected.get("direction")
            if action not in COUNTS or direction not in ("E", "W"):
                raise ValueError(f"Invalid selection action/direction: {path}")
            if selected.get("status") == "partial" or (action, direction) in groups:
                raise ValueError(f"Partial or duplicate selected sequence: {action}/{direction}")
            groups.add((action, direction))
            frames = selected.get("frames", [])
            if [row.get("frame") for row in frames] != list(range(1, COUNTS[action] + 1)):
                raise ValueError(f"Expected ordered complete frames for {action}/{direction}: {path}")
            for row in frames:
                key = action, direction, row["frame"]
                source, record_path = own_path(row["file"]), own_path(row["generationRecord"])
                if key in keys or source in sources:
                    raise ValueError(f"Duplicate slot or reused source: {key}")
                keys.add(key)
                sources.add(source)
                sha = file_sha(source)
                if row.get("sha256", "").lower() != sha:
                    raise ValueError(f"Explicit selection SHA missing/mismatch: {key}")
                record = read_json(record_path)
                image, geom = read_native(source)
                validate_receipt(record, record_path, source, sha, image)
                entries.append({"key": key, "source": source, "sourceSha": sha,
                                "recordPath": record_path, "recordSha": file_sha(record_path), "record": record,
                                "selection": path, "selectionSha": file_sha(path), "image": image,
                                "nativeGeometry": geom})
    if keys != EXPECTED:
        missing = sorted(EXPECTED - keys)
        raise ValueError(f"Require all 68 slots; selected {len(keys)}, missing {missing}")
    return entries


def load_transform(path, entries):
    path = own_path(path)
    config = read_json(path)
    canvas = config.get("nativeCanvas")
    factor = config.get("scale")
    offset = config.get("offset")
    if not isinstance(canvas, list) or len(canvas) != 2 or any(type(v) is not int for v in canvas):
        raise ValueError("Transform nativeCanvas must be [width,height]")
    if not isinstance(factor, (int, float)) or not 0 < factor <= 1:
        raise ValueError("Transform scale must be >0 and <=1; no upscaling")
    if not isinstance(offset, list) or len(offset) != 2 or any(type(v) is not int for v in offset):
        raise ValueError("Transform offset must be explicit integer [x,y]")
    if not config.get("reason"):
        raise ValueError("Transform must explain its fixed anchor and scale in reason")
    if any(list(entry["image"].size) != canvas for entry in entries):
        raise ValueError("All native canvases must match one global transform")
    scaled = [round(canvas[0] * factor), round(canvas[1] * factor)]
    if min(scaled) < 1:
        raise ValueError("Empty transformed canvas")
    return {"file": relative(path), "sha256": file_sha(path), "nativeCanvas": canvas,
            "scale": factor, "offset": offset, "scaledCanvas": scaled,
            "reason": config["reason"], "scope": "One transform for all 68 frames and both directions",
            "noFramewiseBoundingBoxScale": True, "noFramewiseRecentering": True}


def render(entries, transform):
    rows, originals, mirror_originals, outputs, mirror_outputs = [], {}, {}, {}, {}
    for entry in entries:
        key, image = entry["key"], entry["image"]
        hashes = visible_hashes(image)
        for keyname, collection in (("visibleCropSha256", originals), ("mirroredVisibleCropSha256", mirror_originals)):
            value = hashes[keyname]
            if value in originals or value in mirror_originals:
                raise ValueError(f"Native duplicate/mirrored pose: {key} and {originals.get(value, mirror_originals.get(value))}")
        originals[hashes["visibleCropSha256"]] = key
        mirror_originals[hashes["mirroredVisibleCropSha256"]] = key
        scaled = image if list(image.size) == transform["scaledCanvas"] else image.resize(tuple(transform["scaledCanvas"]), Image.Resampling.LANCZOS)
        bbox = geometry(scaled)["visibleBBox"]
        x, y = transform["offset"]
        if bbox[0] + x <= 0 or bbox[1] + y <= 0 or bbox[2] + x >= 1024 or bbox[3] + y >= 1024:
            raise ValueError(f"Global transform clips or touches boundary: {key}")
        final = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        final.paste(scaled, (x, y))
        out_hashes = visible_hashes(final)
        for value in (out_hashes["visibleCropSha256"], out_hashes["mirroredVisibleCropSha256"]):
            if value in outputs or value in mirror_outputs:
                raise ValueError(f"Export duplicate/mirrored pose: {key}")
        outputs[out_hashes["visibleCropSha256"]] = key
        mirror_outputs[out_hashes["mirroredVisibleCropSha256"]] = key
        buffer = io.BytesIO()
        final.save(buffer, format="PNG")
        raw = buffer.getvalue()
        action, direction, number = key
        out = ROOT / "runtime" / action / direction / f"{number:02d}.png"
        record_path = ROOT / "provenance/receipts/derived" / f"{action}-{direction}-{number:02d}.json"
        source_record = entry["record"]
        record = {"file": relative(out), "sha256": digest(raw), "width": 1024, "height": 1024,
                  "format": "PNG RGBA", "tool": "Pillow whole-canvas fixed-transform export", "route": "derived",
                  "generatedAt": source_record["generatedAt"], "generatedAtEvidence": source_record.get("generatedAtEvidence"),
                  "derivedAt": datetime.now(timezone.utc).isoformat(), "configSnapshot": source_record["configSnapshot"],
                  "submittedParameters": {"model": None, "quality": None},
                  "actualModel": source_record["actualModel"], "actualQuality": source_record["actualQuality"],
                  "unverifiedReason": source_record.get("unverifiedReason"), "prompt": source_record["prompt"],
                  "references": source_record["references"],
                  "derivedFrom": {"file": relative(entry["source"]), "sha256": entry["sourceSha"],
                                  "generationRecord": relative(entry["recordPath"]), "generationRecordSha256": entry["recordSha"]},
                  "operation": {"kind": "whole_canvas_uniform_scale_and_fixed_offset", "transform": transform,
                                "filter": "Pillow LANCZOS when scaling only", "noPoseSynthesisOrMirror": True,
                                "pixelsAtFullyTransparentLocations": "unchanged apart from optional whole-canvas downsampling"},
                  "evidence": {"selection": relative(entry["selection"]), "selectionSha256": entry["selectionSha"],
                               "nativeGeometry": entry["nativeGeometry"], "nativePixelHashes": hashes,
                               "outputGeometry": geometry(final), "outputPixelHashes": out_hashes},
                  "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}
        rows.append({"key": key, "raw": raw, "out": out, "receipt": record_path, "record": record})
    return rows


def make_preview(rows, destination, published):
    sets = []
    for action, count in COUNTS.items():
        for direction in ("E", "W"):
            images = []
            for row in sorted((r for r in rows if r["key"][:2] == (action, direction)), key=lambda r: r["key"][2]):
                path = row["out"]
                if not published:
                    path = destination / "frames" / action / direction / f"{row['key'][2]:02d}.png"
                    write_new(path, row["raw"])
                images.append(Path(os.path.relpath(path, destination)).as_posix())
            sets.append({"action": action, "direction": direction, "label": f"{action}/{direction}",
                         "frameMs": TIMING[action], "durationMs": count * TIMING[action], "images": images})
    template = (Path(__file__).with_name("preview_template.html")).read_text(encoding="utf-8")
    data = json.dumps(sets, ensure_ascii=False).replace("<", "\\u003c")
    write_new(destination / "index.html", template.replace("__SEQUENCES_JSON__", data).encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", nargs="+", required=True, help="Character-relative JSON files, or one JSON containing sets")
    parser.add_argument("--transform", required=True, help="Character-relative global transform JSON")
    parser.add_argument("--preview-dir", help="New character-relative preview directory")
    parser.add_argument("--publish", action="store_true", help="Write 68 new runtime images and derived receipts, never overwrite")
    args = parser.parse_args()
    entries = load_selection(args.selection)
    transform = load_transform(args.transform, entries)
    rows = render(entries, transform)
    preview = own_path(args.preview_dir, False) if args.preview_dir else None
    if preview and preview.exists():
        raise ValueError(f"Preview output already exists: {preview}")
    if args.publish:
        for row in rows:
            if row["out"].exists() or row["receipt"].exists():
                raise ValueError(f"Refuse to overwrite runtime/receipt: {row['out']}")
        # Every input and all 68 rendered outputs passed before any publish write.
        for row in rows:
            write_new(row["receipt"], json_bytes(row["record"]))
            write_new(row["out"], row["raw"])
    report = {"character": ROOT.name, "selectedSlots": len(rows), "expectedSlots": 68,
              "technicalPreflightPassed": True, "nativeDuplicateOrMirrorPairs": 0,
              "outputDuplicateOrMirrorPairs": 0, "counts": {f"{a}/{d}": count for a, count in COUNTS.items() for d in ("E", "W")},
              "globalTransform": transform, "published": bool(args.publish),
              "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
              "limitations": ["Exact visible duplicate/mirror hashes cannot prove distinct poses or consistent identity.",
                              "Native canvas dimensions do not prove generation detail; inspect source and model evidence.",
                              "Playback preview creation does not constitute visual approval."],
              "frames": [row["record"] for row in rows]}
    if preview:
        make_preview(rows, preview, args.publish)
        write_new(preview / "technical-report.json", json_bytes(report))
    print(json.dumps({key: value for key, value in report.items() if key != "frames"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"export_character: {error}", file=sys.stderr)
        raise SystemExit(2)
