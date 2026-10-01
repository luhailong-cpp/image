#!/usr/bin/env python3
"""Explicit single-character export; preflight by default, never overwrites.

All inputs and outputs are confined to this character. Source images must be
native single-frame RGBA PNGs at least 1024px in each dimension. This performs
only an explicitly declared uniform whole-canvas downsample/translation, never
pose synthesis, mirroring or per-frame fitting. Visual review stays pending.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

CHARACTER = "06_thunder_caster_boy"
ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT.parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
EXPECTED = {(a, d, n) for a, (count, _) in ACTIONS.items() for d in DIRECTIONS for n in range(1, count + 1)}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def inside(path):
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Path outside owned character: {path}")
    return path


def local(value):
    if not isinstance(value, str) or not value:
        raise ValueError("Expected a nonempty character-local path")
    path = Path(value)
    if not path.is_absolute():
        path = BATCH / path if path.parts[0] == "characters" else ROOT / path
    return inside(path)


def rel(path):
    return inside(path).relative_to(ROOT).as_posix()


def batch_rel(path):
    return inside(path).relative_to(BATCH).as_posix()


def write_new(path, data):
    path = inside(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def geometry(image):
    array = np.asarray(image)
    alpha = array[:, :, 3]
    ys, xs = np.where(alpha > 8)
    if not len(xs):
        raise ValueError("Image has no visible subject")
    normalized = array.copy()
    normalized[alpha == 0, :3] = 0
    return {
        "width": image.width, "height": image.height, "mode": image.mode,
        "transparentPixels": int(np.count_nonzero(alpha == 0)),
        "alphaMin": int(alpha.min()), "alphaMax": int(alpha.max()),
        "visibleBBox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "visibleTouchesEdge": bool(np.any(alpha[0] > 8) or np.any(alpha[-1] > 8) or np.any(alpha[:, 0] > 8) or np.any(alpha[:, -1] > 8)),
        "visiblePixelSha256": digest(normalized.tobytes()),
        "horizontalMirrorVisiblePixelSha256": digest(normalized[:, ::-1].tobytes()),
    }


def open_rgba(path):
    with Image.open(path) as probe:
        probe.verify()
    with Image.open(path) as probe:
        if probe.format != "PNG" or probe.mode != "RGBA":
            raise ValueError(f"Not an RGBA PNG: {path}")
        image = probe.copy()
    info = geometry(image)
    if info["transparentPixels"] == 0:
        raise ValueError(f"No actual fully transparent pixels: {path}")
    return image, info


def receipt_check(record, source_sha):
    if record.get("sha256", "").lower() != source_sha:
        raise ValueError("Source/receipt SHA256 mismatch")
    for key in ("file", "generatedAt", "generatedAtEvidence", "width", "height", "tool", "route", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references"):
        if key not in record:
            raise ValueError(f"Source record missing {key}")
    if not record["prompt"] or not record["references"]:
        raise ValueError("Source record has no prompt/references")
    if (record["actualModel"] is None or record["actualQuality"] is None) and not record.get("unverifiedReason"):
        raise ValueError("Undisclosed model/quality must have unverifiedReason")


def load_selected(directory, allow_partial):
    rows, slots, sources = [], set(), set()
    paths = sorted(inside(directory).glob("*.json"))
    for path in paths:
        data = read_json(path)
        action, direction = data.get("action"), data.get("direction")
        if action not in ACTIONS or direction not in DIRECTIONS:
            raise ValueError(f"Invalid action/direction in {path}")
        if data.get("status") == "partial" and not allow_partial:
            raise ValueError(f"Partial selection cannot be exported: {path}")
        frames = data.get("frames")
        if not isinstance(frames, list):
            raise ValueError(f"Missing frames list: {path}")
        numbers = [item.get("frame") for item in frames]
        if numbers != sorted(set(numbers)):
            raise ValueError(f"Frame numbers must be unique ascending integers: {path}")
        for item in frames:
            key = (action, direction, item["frame"])
            if key not in EXPECTED or key in slots:
                raise ValueError(f"Invalid or duplicate selection slot: {key}")
            slots.add(key)
            source, receipt = local(item["file"]), local(item["generationRecord"])
            if source in sources:
                raise ValueError(f"One source reused across slots: {source}")
            sources.add(source)
            source_sha, receipt_sha = sha(source), sha(receipt)
            if item.get("sha256", "").lower() != source_sha:
                raise ValueError(f"Selection source SHA256 missing or mismatch: {source}")
            if item.get("generationRecordSha256", "").lower() != receipt_sha:
                raise ValueError(f"Selection generationRecordSha256 missing or mismatch: {receipt}")
            record = read_json(receipt)
            receipt_check(record, source_sha)
            if local(record["file"]) != source:
                raise ValueError(f"Receipt names a different source: {receipt}")
            image, info = open_rgba(source)
            if min(image.size) < 1024:
                raise ValueError(f"Native single frame is smaller than 1024: {source}")
            if [record["width"], record["height"]] != list(image.size):
                raise ValueError(f"Recorded native dimensions mismatch: {source}")
            if info["visibleTouchesEdge"]:
                raise ValueError(f"Native visible subject reaches edge: {source}")
            rows.append({"key": key, "source": source, "sourceSha256": source_sha,
                         "receipt": receipt, "receiptSha256": receipt_sha, "sourceRecord": record,
                         "selection": path, "selectionSha256": sha(path), "image": image, "nativeGeometry": info})
    if not rows:
        raise ValueError("No explicit selected frames found")
    if slots != EXPECTED and not allow_partial:
        raise ValueError(f"Need exactly 68 explicit slots; missing {sorted(EXPECTED - slots)}")
    return sorted(rows, key=lambda x: (list(ACTIONS).index(x["key"][0]), x["key"][1], x["key"][2]))


def transforms_for(rows, transform_path):
    if transform_path:
        config = read_json(local(str(transform_path)))
        if config.get("targetCanvas") != [1024, 1024]:
            raise ValueError("Transform targetCanvas must be [1024,1024]")
        transforms = {d: config.get("directions", {}).get(d, config.get("common")) for d in DIRECTIONS}
    else:
        transforms = {d: {"nativeCanvas": [1024, 1024], "scale": 1, "offset": [0, 0]} for d in DIRECTIONS}
    for row in rows:
        transform = transforms[row["key"][1]]
        if not isinstance(transform, dict):
            raise ValueError("Transform must define common or both direction entries")
        if transform.get("nativeCanvas") != list(row["image"].size):
            raise ValueError(f"Native canvas differs from explicit transform: {row['source']}")
        scale, offset = transform.get("scale"), transform.get("offset")
        if not isinstance(scale, (int, float)) or not 0 < scale <= 1:
            raise ValueError("Uniform scale must be positive and cannot upscale")
        if not isinstance(offset, list) or len(offset) != 2 or any(type(x) is not int for x in offset):
            raise ValueError("Offset must be two integer pixel coordinates")
    return transforms


def render(rows, transforms):
    result, visible_hashes, mirror_hashes = [], {}, {}
    when = datetime.now(timezone.utc).isoformat()
    for row in rows:
        action, direction, frame = row["key"]
        transform = transforms[direction]
        source = row["image"]
        scale, offset = transform["scale"], transform["offset"]
        target_size = tuple(round(value * scale) for value in source.size)
        scaled = source.copy() if target_size == source.size else source.resize(target_size, Image.Resampling.LANCZOS)
        scaled_info = geometry(scaled)
        bbox = scaled_info["visibleBBox"]
        if bbox[0] + offset[0] < 0 or bbox[1] + offset[1] < 0 or bbox[2] + offset[0] > 1024 or bbox[3] + offset[1] > 1024:
            raise ValueError(f"Fixed transform clips subject: {row['key']}")
        image = Image.new("RGBA", (1024, 1024))
        image.paste(scaled, tuple(offset))
        info = geometry(image)
        if info["visibleTouchesEdge"]:
            raise ValueError(f"Exported subject reaches edge: {row['key']}")
        h = info["visiblePixelSha256"]
        if h in visible_hashes:
            raise ValueError(f"Duplicate visible frame: {row['key']} / {visible_hashes[h]}")
        if h in mirror_hashes:
            raise ValueError(f"Exact horizontally mirrored visible frame: {row['key']} / {mirror_hashes[h]}")
        visible_hashes[h] = row["key"]
        mirror_hashes[info["horizontalMirrorVisiblePixelSha256"]] = row["key"]
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        png = buffer.getvalue()
        destination = ROOT / "runtime" / action / direction / f"{frame:02d}.png"
        receipt = ROOT / "provenance/receipts/derived" / f"{action}-{direction}-{frame:02d}.json"
        source_record = row["sourceRecord"]
        record = {"file": batch_rel(destination), "sha256": digest(png), "width": 1024, "height": 1024,
                  "format": "PNG RGBA", "derivedAt": when,
                  "generatedAt": source_record["generatedAt"], "generatedAtEvidence": source_record["generatedAtEvidence"],
                  "tool": "Pillow deterministic explicit whole-canvas export", "route": "derived",
                  "configSnapshot": source_record["configSnapshot"], "submittedParameters": {"model": None, "quality": None},
                  "actualModel": source_record["actualModel"], "actualQuality": source_record["actualQuality"],
                  "unverifiedReason": source_record.get("unverifiedReason"), "prompt": source_record["prompt"],
                  "references": source_record["references"],
                  "derivedFrom": {"file": batch_rel(row["source"]), "sha256": row["sourceSha256"],
                                  "generationRecord": batch_rel(row["receipt"]), "generationRecordSha256": row["receiptSha256"]},
                  "evidence": {"selection": batch_rel(row["selection"]), "selectionSha256": row["selectionSha256"],
                               "exportTool": batch_rel(Path(__file__)), "exportToolSha256": sha(Path(__file__))},
                  "operation": {"kind": "explicit_uniform_whole_canvas_transform", "transform": transform,
                                "filter": "none" if target_size == source.size else "Pillow LANCZOS",
                                "alphaCleanup": "none", "noFramewiseFitting": True, "noMirroringOrPoseSynthesis": True},
                  "nativeGeometry": row["nativeGeometry"], "outputGeometry": info,
                  "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}
        result.append({"key": row["key"], "destination": destination, "receipt": receipt, "png": png, "record": record})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-dir", default="selection")
    parser.add_argument("--transform", help="Character-local explicit transform JSON; default identity for 1024 sources only")
    parser.add_argument("--allow-partial", action="store_true", help="Preflight/preview only, never permits partial publish")
    parser.add_argument("--preview-dir", help="New directory inside character; renders technical preview, no approval implied")
    parser.add_argument("--publish", action="store_true", help="Write all 68 runtime PNGs and derived receipts; refuses existing outputs")
    args = parser.parse_args()
    if args.publish and args.allow_partial:
        raise ValueError("Publish cannot accept --allow-partial")
    selected = load_selected(local(args.selection_dir), args.allow_partial)
    transforms = transforms_for(selected, args.transform)
    rows = render(selected, transforms)
    report = {"character": CHARACTER, "status": "technical_preflight_passed", "selectedSlots": len(rows),
              "missingSlots": [list(k) for k in sorted(EXPECTED - {row["key"] for row in rows})],
              "transforms": transforms, "visualApproval": "pending", "clientIntegration": "not_integrated",
              "runtimeAcceptance": "not_tested", "frames": [row["record"] for row in rows]}
    if args.publish:
        for row in rows:
            if row["destination"].exists() or row["receipt"].exists():
                raise ValueError(f"Refuse overwrite: {row['destination']} / {row['receipt']}")
    if args.preview_dir:
        preview = local(args.preview_dir)
        if preview.exists():
            raise ValueError(f"Refuse existing preview directory: {preview}")
        from preview_character import write_preview
        for row in rows:
            action, direction, number = row["key"]
            write_new(preview / "frames" / action / direction / f"{number:02d}.png", row["png"])
        write_new(preview / "technical-report.json", json_bytes(report))
        write_preview(preview, preview / "frames", report["status"])
    if args.publish:
        for row in rows:
            write_new(row["receipt"], json_bytes(row["record"]))
            write_new(row["destination"], row["png"])
    print(json.dumps({k: v for k, v in report.items() if k != "frames"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"export_character: {exc}", file=sys.stderr)
        raise SystemExit(2)
