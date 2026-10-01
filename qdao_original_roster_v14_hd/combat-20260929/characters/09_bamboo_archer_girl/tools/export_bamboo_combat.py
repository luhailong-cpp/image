#!/usr/bin/env python3
"""09-only explicit selection preflight, fixed-canvas export and timed preview.

Default is read-only. --publish creates all 68 runtime PNGs and derived receipts;
--preview-dir creates a new private preview. Existing outputs are never replaced.
Neither PNG uniqueness nor a generated preview constitutes visual approval.
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

CHARACTER = "09_bamboo_archer_girl"
ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT.parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def local(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f"Path escapes this character: {path}")
    return resolved


def resolve_input(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("Missing input path")
    relative = Path(value)
    result = local(BATCH / relative if relative.parts[0] == "characters" else ROOT / relative)
    if not result.is_file():
        raise ValueError(f"Input is missing: {result}")
    return result


def geometry(image: Image.Image) -> dict:
    pixels = np.array(image)
    alpha = pixels[:, :, 3]
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        raise ValueError("Fully invisible image")
    canonical = pixels.copy()
    canonical[alpha == 0, :3] = 0
    return {
        "visibleBBox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "transparentPixels": int(np.count_nonzero(alpha == 0)),
        "visiblePixels": int(len(xs)),
        "alphaMin": int(alpha.min()), "alphaMax": int(alpha.max()),
        "visibleTouchesEdge": bool(np.any(alpha[0] > 8) or np.any(alpha[-1] > 8)
                                   or np.any(alpha[:, 0] > 8) or np.any(alpha[:, -1] > 8)),
        "visiblePixelSha256": sha(canonical.tobytes()),
        "mirroredVisiblePixelSha256": sha(canonical[:, ::-1].tobytes()),
    }


def open_png(path: Path) -> tuple[Image.Image, dict]:
    with Image.open(path) as source:
        if source.format != "PNG" or source.mode != "RGBA":
            raise ValueError(f"Requires true RGBA PNG: {path}")
        source.load()
        image = source.copy()
    if min(image.size) < 1024:
        raise ValueError(f"Native image is smaller than 1024: {path}")
    geom = geometry(image)
    if not geom["transparentPixels"]:
        raise ValueError(f"No fully transparent pixels: {path}")
    if geom["visibleTouchesEdge"]:
        raise ValueError(f"Visible subject touches a canvas edge: {path}")
    return image, geom


def validate_receipt(path: Path, source: Path, digest: str) -> dict:
    record = read_json(path)
    required = ("file", "sha256", "generatedAt", "generatedAtEvidence", "tool", "route",
                "configSnapshot", "submittedParameters", "actualModel", "actualQuality",
                "evidence", "prompt", "references", "width", "height")
    missing = [field for field in required if field not in record]
    if missing:
        raise ValueError(f"Incomplete generation record {path}: {missing}")
    if resolve_input(record["file"]) != source or str(record["sha256"]).lower() != digest:
        raise ValueError(f"Source path/hash and generation record disagree: {path}")
    if not record["prompt"] or not record["references"] or not record["evidence"]:
        raise ValueError(f"Empty prompt, references or evidence: {path}")
    if (record["actualModel"] is None or record["actualQuality"] is None) and not record.get("unverifiedReason"):
        raise ValueError(f"Unknown model/quality must have unverifiedReason: {path}")
    if record.get("derivedFrom"):
        raise ValueError(f"Selection must name a genuinely generated native pose, not a derived frame: {path}")
    return record


def selections() -> list[dict]:
    paths = sorted(set(ROOT.glob("*selection.json")) | set((ROOT / "selection").glob("*.json")))
    expected_groups = {(a, d) for a in ACTIONS for d in DIRECTIONS}
    rows, groups, sources = [], set(), set()
    for path in paths:
        selection = read_json(path)
        group = (selection.get("action"), selection.get("direction"))
        if group not in expected_groups or group in groups:
            raise ValueError(f"Unknown or repeated selection group: {path}")
        if selection.get("status") != "complete":
            raise ValueError(f"Selection must explicitly have status complete: {path}")
        groups.add(group)
        count, _ = ACTIONS[group[0]]
        entries = selection.get("frames", [])
        if [e.get("frame") for e in entries] != list(range(1, count + 1)):
            raise ValueError(f"Requires exactly ordered frames 1..{count}: {path}")
        for entry in entries:
            source = resolve_input(entry.get("file"))
            receipt = resolve_input(entry.get("generationRecord"))
            if source in sources:
                raise ValueError(f"One source is assigned to multiple slots: {source}")
            if not source.is_relative_to(ROOT / "staging") or not receipt.is_relative_to(ROOT / "provenance" / "receipts"):
                raise ValueError("Selections must use this character's staging and provenance/receipts")
            sources.add(source)
            source_hash, receipt_hash = sha_file(source), sha_file(receipt)
            if entry.get("sha256", "").lower() != source_hash:
                raise ValueError(f"Source SHA is missing or disagrees with explicit selection: {source}")
            if entry.get("generationRecordSha256", "").lower() != receipt_hash:
                raise ValueError(f"Generation-record SHA is missing or disagrees: {receipt}")
            record = validate_receipt(receipt, source, source_hash)
            rows.append({"action": group[0], "direction": group[1], "frame": entry["frame"],
                         "source": source, "sourceSha256": source_hash, "receipt": receipt,
                         "receiptSha256": receipt_hash, "record": record, "selection": path,
                         "selectionSha256": sha_file(path)})
    if groups != expected_groups or len(rows) != 68:
        missing = sorted(expected_groups - groups)
        raise ValueError(f"Requires six complete groups / 68 slots; found {len(rows)} slots, missing groups={missing}")
    return sorted(rows, key=lambda r: (list(ACTIONS).index(r["action"]), r["direction"], r["frame"]))


def load_transforms(path: Path | None, native: tuple[int, int]) -> dict:
    if native[0] != native[1]:
        raise ValueError("Uniform square native canvases required; rectangular inputs need manual review")
    factor = 1024 / native[0]
    if path:
        transforms = read_json(local(path))
        if set(transforms) != set(DIRECTIONS):
            raise ValueError("Transform file must have exactly E and W")
    else:
        transforms = {d: {"nativeCanvas": list(native), "factor": factor, "offset": [0, 0]} for d in DIRECTIONS}
    for direction, transform in transforms.items():
        if transform.get("nativeCanvas") != list(native):
            raise ValueError(f"Wrong nativeCanvas for {direction}")
        scale, offset = transform.get("factor"), transform.get("offset")
        if not isinstance(scale, (int, float)) or not 0 < scale <= 1:
            raise ValueError("Whole-canvas factor must be >0 and <=1")
        if not isinstance(offset, list) or len(offset) != 2 or any(type(v) is not int for v in offset):
            raise ValueError("Offset must be two explicit integer coordinates")
        if max(round(side * scale) for side in native) > 1024:
            raise ValueError("Scaled whole canvas exceeds 1024")
    return transforms


def render(rows: list[dict], transform_path: Path | None) -> tuple[list[dict], dict]:
    first_image, _ = open_png(rows[0]["source"])
    native = first_image.size
    first_image.close()
    transforms = load_transforms(transform_path, native)
    visible, mirror, output = {}, {}, []
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        image, native_geom = open_png(row["source"])
        if image.size != native or [row["record"]["width"], row["record"]["height"]] != list(image.size):
            raise ValueError(f"Mixed native canvas or inaccurate receipt dimensions: {row['source']}")
        key = f"{row['action']}-{row['direction']}-{row['frame']:02d}"
        transform = transforms[row["direction"]]
        scale, offset = transform["factor"], transform["offset"]
        identity = native == (1024, 1024) and scale == 1 and offset == [0, 0]
        if identity:
            final, png = image, row["source"].read_bytes()
        else:
            scaled = image.resize(tuple(round(side * scale) for side in native), Image.Resampling.LANCZOS)
            # Detect loss before pasting; opaque parts may never disappear off canvas.
            scaled_bbox = geometry(scaled)["visibleBBox"]
            if scaled_bbox[0] + offset[0] < 0 or scaled_bbox[1] + offset[1] < 0 or scaled_bbox[2] + offset[0] > 1024 or scaled_bbox[3] + offset[1] > 1024:
                raise ValueError(f"Fixed transform would clip visible subject: {key}")
            final = Image.new("RGBA", (1024, 1024))
            final.paste(scaled, tuple(offset))
            buffer = io.BytesIO()
            final.save(buffer, format="PNG")
            png = buffer.getvalue()
        geom = geometry(final)
        if geom["visibleTouchesEdge"] or not geom["transparentPixels"]:
            raise ValueError(f"Export would touch edge or lose transparency: {key}")
        digest = geom["visiblePixelSha256"]
        if digest in visible:
            raise ValueError(f"Duplicate visible pixels: {visible[digest]} and {key}")
        if digest in mirror:
            raise ValueError(f"Mirrored duplicate pixels: {mirror[digest]} and {key}")
        visible[digest], mirror[geom["mirroredVisiblePixelSha256"]] = key, key
        destination = ROOT / "runtime" / row["action"] / row["direction"] / f"{row['frame']:02d}.png"
        receipt = ROOT / "provenance" / "receipts" / "derived" / f"{key}.json"
        record = {
            "file": destination.relative_to(BATCH).as_posix(), "sha256": sha(png),
            "generatedAt": row["record"]["generatedAt"], "derivedAt": now,
            "width": 1024, "height": 1024, "format": "PNG RGBA",
            "tool": "export_bamboo_combat.py", "route": "derived",
            "actualModel": row["record"]["actualModel"], "actualQuality": row["record"]["actualQuality"],
            "unverifiedReason": row["record"].get("unverifiedReason"),
            "configSnapshot": row["record"]["configSnapshot"],
            "submittedParameters": {"model": None, "quality": None},
            "prompt": row["record"]["prompt"], "references": row["record"]["references"],
            "derivedFrom": {"file": row["source"].relative_to(BATCH).as_posix(), "sha256": row["sourceSha256"],
                            "generationRecord": row["receipt"].relative_to(BATCH).as_posix(),
                            "generationRecordSha256": row["receiptSha256"]},
            "evidence": {"selection": row["selection"].relative_to(BATCH).as_posix(),
                         "selectionSha256": row["selectionSha256"]},
            "operation": {"kind": "byte_preserving_identity_export" if identity else "fixed_whole_canvas_uniform_downsample",
                          "transform": transform, "filter": "none" if identity else "Pillow LANCZOS",
                          "noPerFrameRecentering": True, "noPoseSynthesis": True, "noMirroring": True},
            "nativeGeometry": native_geom, "outputGeometry": geom,
            "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
        }
        output.append({**row, "png": png, "destination": destination, "derivedReceipt": receipt, "derivedRecord": record})
        image.close()
        if final is not image:
            final.close()
    return output, transforms


def write_new(path: Path, payload: bytes) -> None:
    local(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def verify_inputs_unchanged(rows: list[dict]) -> None:
    """Fail before any write if another producer changed a selected input."""
    checked = set()
    for row in rows:
        for path, expected in ((row["source"], row["sourceSha256"]),
                               (row["receipt"], row["receiptSha256"]),
                               (row["selection"], row["selectionSha256"])):
            if path not in checked:
                if sha_file(path) != expected:
                    raise ValueError(f"Input changed during preflight: {path}")
                checked.add(path)


def preview_html(rows: list[dict], directory: Path, use_runtime: bool) -> str:
    sets = []
    for action, (count, ms) in ACTIONS.items():
        for direction in DIRECTIONS:
            current = [r for r in rows if (r["action"], r["direction"]) == (action, direction)]
            paths = [r["destination"] if use_runtime else directory / "frames" / action / direction / f"{r['frame']:02d}.png" for r in current]
            sets.append({"label": f"{action}/{direction}", "ms": ms, "count": count,
                         "frames": [Path(os.path.relpath(p, directory)).as_posix() for p in paths]})
    template = Path(__file__).with_name("preview_bamboo.html").read_text(encoding="utf-8")
    return template.replace("__SEQUENCES__", json.dumps(sets, ensure_ascii=False).replace("<", "\\u003c"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transforms", type=Path, help="Optional fixed E/W whole-canvas transforms JSON inside this character")
    parser.add_argument("--preview-dir", type=Path, help="New private preview directory; normal and 0.25x slow playback")
    parser.add_argument("--publish", action="store_true", help="Write all 68 runtime images and provenance only after complete preflight")
    args = parser.parse_args()
    if ROOT.name != CHARACTER:
        raise ValueError("This tool is restricted to 09_bamboo_archer_girl")
    selected = selections()
    rows, transforms = render(selected, args.transforms)
    verify_inputs_unchanged(rows)
    preview = local(args.preview_dir) if args.preview_dir else None
    if preview and preview.exists():
        raise ValueError(f"Refuse to replace preview directory: {preview}")
    if args.publish:
        for row in rows:
            if row["destination"].exists() or row["derivedReceipt"].exists():
                raise ValueError(f"Refuse to replace runtime or receipt: {row['destination']}")
        for row in rows:
            write_new(row["derivedReceipt"], (json.dumps(row["derivedRecord"], ensure_ascii=False, indent=2) + "\n").encode())
            write_new(row["destination"], row["png"])
    report = {"character": CHARACTER, "checkedAt": datetime.now(timezone.utc).isoformat(),
              "selectedSlots": len(rows), "technicalPreflight": "passed", "published": args.publish,
              "normalFrameMs": {a: ms for a, (_, ms) in ACTIONS.items()}, "transforms": transforms,
              "counts": {f"{a}/{d}": n for a, (n, _) in ACTIONS.items() for d in DIRECTIONS},
              "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
              "limits": "Exact visible duplicates and exact mirrored duplicates are checked. Distinct poses and visual continuity require playback review.",
              "frames": [row["derivedRecord"] for row in rows]}
    if preview:
        if not args.publish:
            for row in rows:
                write_new(preview / "frames" / row["action"] / row["direction"] / f"{row['frame']:02d}.png", row["png"])
        write_new(preview / "index.html", preview_html(rows, preview, args.publish).encode("utf-8"))
        write_new(preview / "technical-report.json", (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k: v for k, v in report.items() if k != "frames"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"export_bamboo_combat: {error}", file=sys.stderr)
        raise SystemExit(2)
