#!/usr/bin/env python3
"""Role-05-only explicit-selection export. Read-only unless --publish/--preview-dir.

No image generation, pose synthesis, alpha removal, overwrite, or client change.
All source validation and rendering finish before any output is written.
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

ROLE = Path(__file__).resolve().parents[1]
BATCH = ROLE.parents[1]
IDENTIFIER = "05_celestial_musician_girl"
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
REQUIRED = {(a, d, f) for a, (n, _) in ACTIONS.items() for d in DIRECTIONS for f in range(1, n + 1)}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json_snapshot(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value, digest(raw)


def local_path(value: str | Path, *, exists: bool = True) -> Path:
    value = Path(value)
    if not value.is_absolute():
        value = BATCH / value if value.parts[0] == "characters" else ROLE / value
    result = value.resolve()
    if not result.is_relative_to(ROLE):
        raise ValueError(f"Path escapes role 05: {result}")
    if exists and not result.is_file():
        raise ValueError(f"Missing file: {result}")
    return result


def relative(path: Path) -> str:
    return path.relative_to(BATCH).as_posix()


def geometry(image: Image.Image) -> dict:
    alpha = np.asarray(image.getchannel("A"))
    ys, xs = np.where(alpha > 8)
    if not len(xs):
        raise ValueError("No visible subject at alpha > 8")
    return {
        "canvas": list(image.size),
        "visibleBBoxAlphaAbove8": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "transparentPixels": int(np.count_nonzero(alpha == 0)),
        "partialAlphaPixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
        "visibleTouchesCanvasEdge": bool(np.any(alpha[0] > 8) or np.any(alpha[-1] > 8)
                                         or np.any(alpha[:, 0] > 8) or np.any(alpha[:, -1] > 8)),
    }


def pixel_fingerprints(image: Image.Image) -> dict:
    pixels = np.array(image)
    pixels[pixels[:, :, 3] == 0] = 0
    ys, xs = np.where(pixels[:, :, 3] > 0)
    if not len(xs):
        raise ValueError("Fully transparent source")
    crop = pixels[int(ys.min()):int(ys.max()) + 1, int(xs.min()):int(xs.max()) + 1]
    def array_hash(array):
        return digest(str(array.shape).encode("ascii") + array.tobytes())
    return {"visiblePixelsSha256": array_hash(pixels),
            "visibleMirrorSha256": array_hash(pixels[:, ::-1]),
            "visibleCropSha256": array_hash(crop),
            "visibleCropMirrorSha256": array_hash(crop[:, ::-1])}


def load_selected(paths: list[Path]) -> list[dict]:
    rows, seen_keys, seen_sources = [], set(), set()
    for selection_path in paths:
        selection_path = local_path(selection_path)
        data, selection_sha = read_json_snapshot(selection_path)
        action, direction = data.get("action"), data.get("direction")
        if action not in ACTIONS or direction not in DIRECTIONS or data.get("partial") is True:
            raise ValueError(f"Invalid or partial selection: {selection_path}")
        frames = data.get("frames", [])
        expected = list(range(1, ACTIONS[action][0] + 1))
        if [x.get("frame") for x in frames] != expected:
            raise ValueError(f"Selection must contain ordered frames {expected}: {selection_path}")
        for entry in frames:
            key = (action, direction, entry["frame"])
            source_path = local_path(entry["file"])
            record_path = local_path(entry["generationRecord"])
            if key in seen_keys or source_path in seen_sources:
                raise ValueError(f"Duplicate slot or source: {key}, {source_path}")
            seen_keys.add(key)
            seen_sources.add(source_path)
            raw = source_path.read_bytes()
            source_sha = digest(raw)
            record, record_sha = read_json_snapshot(record_path)
            if entry.get("sha256", "").lower() != source_sha or record.get("sha256", "").lower() != source_sha:
                raise ValueError(f"Mandatory source/selection/receipt SHA mismatch: {source_path}")
            if local_path(record["file"]) != source_path:
                raise ValueError(f"Receipt names a different source: {record_path}")
            required_fields = ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot",
                               "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references")
            if any(k not in record for k in required_fields):
                raise ValueError(f"Generation record missing fields: {record_path}")
            if not record["prompt"] or not record["references"] or not record["evidence"]:
                raise ValueError(f"Empty prompt/references/evidence: {record_path}")
            if (record["actualModel"] is None or record["actualQuality"] is None) and not record.get("unverifiedReason"):
                raise ValueError(f"Undisclosed actual model/quality needs reason: {record_path}")
            with Image.open(io.BytesIO(raw)) as decoded:
                if decoded.format != "PNG" or decoded.mode != "RGBA" or min(decoded.size) < 1024:
                    raise ValueError(f"Native single-frame source must be RGBA PNG >=1024 each axis: {source_path}")
                decoded.load()
                image = decoded.copy()
            if (record.get("width"), record.get("height")) != image.size:
                raise ValueError(f"Recorded native dimensions do not match source: {record_path}")
            geom = geometry(image)
            if geom["visibleTouchesCanvasEdge"] or not geom["transparentPixels"]:
                raise ValueError(f"Source lacks transparency or clips visible subject: {source_path}")
            rows.append({"key": key, "source": source_path, "sourceSha256": source_sha,
                         "image": image, "sourceGeometry": geom, "fingerprints": pixel_fingerprints(image),
                         "record": record, "recordPath": record_path, "recordSha256": record_sha,
                         "selection": selection_path, "selectionSha256": selection_sha})
    if seen_keys != REQUIRED:
        raise ValueError(f"Require all 68 explicit slots; missing={sorted(REQUIRED - seen_keys)}, extra={sorted(seen_keys - REQUIRED)}")
    return sorted(rows, key=lambda r: (list(ACTIONS).index(r["key"][0]), r["key"][1], r["key"][2]))


def reject_duplicates(rows: list[dict], field: str) -> None:
    exact, crop = {}, {}
    for row in rows:
        info, key = row[field], row["key"]
        for lookup, direct, mirrored in ((exact, "visiblePixelsSha256", "visibleMirrorSha256"),
                                        (crop, "visibleCropSha256", "visibleCropMirrorSha256")):
            if info[direct] in lookup:
                raise ValueError(f"Copied visible content: {lookup[info[direct]]} and {key}")
            if info[mirrored] in lookup:
                raise ValueError(f"Mirrored visible content: {lookup[info[mirrored]]} and {key}")
            lookup[info[direct]] = key


def load_transforms(path: Path, rows: list[dict]) -> dict:
    source_path = local_path(path)
    data, source_sha = read_json_snapshot(source_path)
    if data.get("character") != IDENTIFIER or data.get("approvedForExport") is not True:
        raise ValueError("Transform must name role 05 and explicitly set approvedForExport=true after visual anchor review")
    transforms = data.get("directions")
    if not isinstance(transforms, dict) or set(transforms) != set(DIRECTIONS):
        raise ValueError("Transform needs E and W direction entries")
    scales = set()
    for direction, transform in transforms.items():
        native = transform.get("nativeCanvas")
        scale, offset = transform.get("scale"), transform.get("offset")
        if not isinstance(scale, (int, float)) or not 0 < scale <= 1:
            raise ValueError("Scale must be positive uniform downsample or 1, never upscale")
        if not isinstance(offset, list) or len(offset) != 2 or any(type(x) is not int for x in offset):
            raise ValueError("Offset must be two fixed integer pixels")
        sizes = {tuple(r["image"].size) for r in rows if r["key"][1] == direction}
        if sizes != {tuple(native or [])}:
            raise ValueError(f"Every {direction} source must match explicit native canvas: {sizes}")
        scales.add(scale)
    if len(scales) != 1:
        raise ValueError("Same character must use one uniform scale across E and W")
    data["transformFileEvidence"] = {"file": relative(source_path), "sha256": source_sha}
    return data


def render(rows: list[dict], transform_data: dict) -> list[dict]:
    timestamp = datetime.now(timezone.utc).isoformat()
    for row in rows:
        action, direction, frame = row["key"]
        transform = transform_data["directions"][direction]
        image = row["image"]
        scale, offset = transform["scale"], tuple(transform["offset"])
        size = (round(image.width * scale), round(image.height * scale))
        scaled = image if size == image.size else image.resize(size, Image.Resampling.LANCZOS)
        bbox = scaled.getchannel("A").getbbox()
        if bbox is None or bbox[0] + offset[0] < 0 or bbox[1] + offset[1] < 0 or bbox[2] + offset[0] > 1024 or bbox[3] + offset[1] > 1024:
            raise ValueError(f"Global transform would crop nonzero alpha: {row['key']}")
        final = Image.new("RGBA", (1024, 1024))
        final.paste(scaled, offset)
        geom = geometry(final)
        if geom["visibleTouchesCanvasEdge"]:
            raise ValueError(f"Final visible subject touches edge: {row['key']}")
        out = io.BytesIO()
        final.save(out, format="PNG")
        row["png"] = out.getvalue()
        row["outputFingerprints"] = pixel_fingerprints(final)
        row["destination"] = ROLE / "runtime" / action / direction / f"{frame:02d}.png"
        row["receiptDestination"] = ROLE / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{frame:02d}.json"
        source = row["record"]
        row["outputRecord"] = {
            "file": relative(row["destination"]), "sha256": digest(row["png"]),
            "generatedAt": source["generatedAt"], "generatedAtEvidence": source["generatedAtEvidence"],
            "derivedAt": timestamp, "width": 1024, "height": 1024, "format": "PNG RGBA",
            "tool": "Pillow fixed whole-canvas export", "route": "derived",
            "configSnapshot": source["configSnapshot"], "submittedParameters": {"model": None, "quality": None},
            "actualModel": source["actualModel"], "actualQuality": source["actualQuality"],
            "unverifiedReason": source.get("unverifiedReason"), "prompt": source["prompt"], "references": source["references"],
            "evidence": {"selection": relative(row["selection"]), "selectionSha256": row["selectionSha256"],
                         "sourceGenerationRecord": relative(row["recordPath"]), "sourceGenerationRecordSha256": row["recordSha256"]},
            "derivedFrom": {"file": relative(row["source"]), "sha256": row["sourceSha256"],
                            "generationRecord": relative(row["recordPath"]), "generationRecordSha256": row["recordSha256"]},
            "operation": {"kind": "fixed_whole_canvas_uniform_export", "transform": transform,
                          "transformFileEvidence": transform_data["transformFileEvidence"],
                          "filter": "none" if scale == 1 else "Pillow LANCZOS", "alphaThresholdRemoval": None,
                          "preservesSemitransparency": True, "noFramewiseBBoxFit": True, "noPoseSynthesis": True},
            "sourceGeometry": row["sourceGeometry"], "outputGeometry": geom,
            "pixelFingerprints": row["outputFingerprints"], "visualApproval": "pending",
            "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
        }
    reject_duplicates(rows, "outputFingerprints")
    return rows


def preview_html(rows: list[dict]) -> str:
    sets = [{"label": f"{a}/{d}", "ms": ms,
             "images": [f"frames/{a}/{d}/{f:02d}.png" for f in range(1, count + 1)]}
            for a, (count, ms) in ACTIONS.items() for d in DIRECTIONS]
    template = Path(__file__).with_name("preview_template.html").read_text(encoding="utf-8")
    return template.replace("__SEQUENCES__", json.dumps(sets, ensure_ascii=False))


def write_new(path: Path, raw: bytes) -> None:
    local_path(path, exists=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, nargs=6, required=True)
    parser.add_argument("--transform", type=Path, required=True)
    parser.add_argument("--preview-dir", type=Path)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if ROLE.name != IDENTIFIER:
        raise ValueError("This export entry point is scoped to role 05 only")
    rows = load_selected(args.selection)
    reject_duplicates(rows, "fingerprints")
    transform_data = load_transforms(args.transform, rows)
    rows = render(rows, transform_data)
    report = {"character": IDENTIFIER, "technicalPreflight": "passed", "selectedSlots": len(rows),
              "sequenceTimings": {a: {"framesPerDirection": n, "frameMs": ms, "segmentMs": n * ms} for a, (n, ms) in ACTIONS.items()},
              "transform": transform_data, "visualApproval": "pending", "clientIntegration": "not_integrated",
              "runtimeAcceptance": "not_tested", "note": "Unique pixels do not prove independent poses; six-segment visual playback review required.",
              "frames": [r["outputRecord"] for r in rows]}
    planned = []
    if args.publish:
        for row in rows:
            planned.extend([(row["destination"], row["png"]),
                            (row["receiptDestination"], (json.dumps(row["outputRecord"], ensure_ascii=False, indent=2) + "\n").encode("utf-8"))])
    if args.preview_dir:
        preview = local_path(args.preview_dir, exists=False)
        if preview.exists():
            raise ValueError(f"Refuse to reuse preview directory: {preview}")
        for row in rows:
            a, d, f = row["key"]
            planned.append((preview / "frames" / a / d / f"{f:02d}.png", row["png"]))
        planned.extend([(preview / "index.html", preview_html(rows).encode("utf-8")),
                        (preview / "technical-report.json", (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))])
    for path, _ in planned:
        if local_path(path, exists=False).exists():
            raise ValueError(f"Refuse overwrite: {path}")
    # A concurrent producer must not invalidate a chain after preflight.
    for row in rows:
        for path, expected in ((row["source"], row["sourceSha256"]),
                               (row["recordPath"], row["recordSha256"]),
                               (row["selection"], row["selectionSha256"])):
            if digest(path.read_bytes()) != expected:
                raise ValueError(f"Input changed during export preflight; restart after producer finishes: {path}")
    transform_evidence = transform_data["transformFileEvidence"]
    if digest(local_path(transform_evidence["file"]).read_bytes()) != transform_evidence["sha256"]:
        raise ValueError("Transform changed during export preflight; restart after anchor review finishes")
    for path, raw in planned:
        write_new(path, raw)
    print(json.dumps({k: v for k, v in report.items() if k != "frames"}, ensure_ascii=False, indent=2))
    print(json.dumps({"filesWritten": len(planned), "exportedRuntime": 68 if args.publish else 0}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"role05 export: {error}", file=sys.stderr)
        raise SystemExit(2)
