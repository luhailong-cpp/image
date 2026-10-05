#!/usr/bin/env python3
"""Read-only image/manifest checks; writes validation.json in this directory.

Run: python verify_assets.py
Dependency: Pillow. Does not modify images, generate frames, or certify art.

Expected manifest: {"frames": [{"file": "runtime/hit/E/01.png",
"action": "hit", "direction": "E", "frame": 1, "width": 1024,
"height": 1024, "durationMs": 40, "pivot": [0.5, 0.08],
"event": null, "sha256": "...", "sourceRecord": "records/hit-E-01.json",
"visualStatus": "pending"}]}. A sourceRecord may include #record-id; JSON
arrays or a top-level records[] can be selected by id. Plain files must hold a
single record, or one uniquely matching final file/sha256. Original image paths
inside a receipt are not required to survive the project's retention cleanup.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Pillow is required. Use the project's Python runtime with Pillow installed.")


ROOT = Path(__file__).resolve().parent
CONTRACT = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
EXPECTED = {
    f"runtime/{action}/{direction}/{number:02}.png": {
        "action": action, "direction": direction, "frame": number,
        "durationMs": duration,
    }
    for action, (count, duration) in CONTRACT.items()
    for direction in DIRECTIONS
    for number in range(1, count + 1)
}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def norm_file(value) -> str:
    return str(value).replace("\\", "/").removeprefix("./")


def local_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("reference resolves outside this character directory")
    return path


def records_from(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and isinstance(value.get("records"), list):
        return value["records"]
    return [value]


def source_record(ref: str, frame: dict) -> tuple[dict, str]:
    filename, separator, fragment = ref.partition("#")
    path = local_path(filename)
    if not path.is_file():
        raise ValueError(f"missing source record: {filename}")
    with path.open("r", encoding="utf-8-sig") as stream:
        value = json.load(stream)
    records = records_from(value)
    if separator:
        fragment = unquote(fragment)
        if isinstance(value, dict) and fragment in value:
            record = value[fragment]
        else:
            matches = [r for r in records if isinstance(r, dict) and str(r.get("id")) == fragment]
            if len(matches) != 1:
                raise ValueError(f"source fragment not unique or not found: {ref}")
            record = matches[0]
    elif len(records) == 1:
        record = records[0]
    else:
        matches = [r for r in records if isinstance(r, dict) and (
            norm_file(r.get("file", r.get("finalFile", ""))) == frame["file"]
            or r.get("sha256") == frame["sha256"])]
        if len(matches) != 1:
            raise ValueError(f"multi-record source needs #id or unique file/SHA match: {ref}")
        record = matches[0]
    if not isinstance(record, dict):
        raise ValueError(f"source record is not a JSON object: {ref}")
    return record, sha256(path)


def main() -> int:
    report = {
        "schemaVersion": 1,
        "checkedAtUtc": datetime.now(timezone.utc).isoformat(),
        "character": "04-stone-spirit",
        "expectedCount": 68,
        "technicalPassed": False,
        "artReview": "not assessed by this script",
        "clientAcceptance": "not assessed by this script",
        "limitations": [
            "Exact RGBA hashes catch identical pixels; they do not prove independent AI poses.",
            "Alpha bounds cannot judge anatomy, facing, anchor stability, continuity or cleanup quality.",
            "Source-reference checks verify links and declared evidence, not the model identity itself.",
            "Contact sheets, all six animations, adjacent poses and enlarged extremities require human visual review.",
        ],
        "errors": [], "warnings": [], "groups": {}, "frames": [],
    }
    errors, warnings = report["errors"], report["warnings"]
    manifest_path = ROOT / "manifest.json"
    frames = []
    if not manifest_path.is_file():
        errors.append("manifest.json is missing")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            frames = manifest.get("frames", []) if isinstance(manifest, dict) else []
            if not isinstance(frames, list):
                raise ValueError("manifest.frames must be an array")
            report["manifestSha256"] = sha256(manifest_path)
        except (OSError, ValueError) as exc:
            errors.append(f"manifest.json: {exc}")
            frames = []
    if len(frames) != 68:
        errors.append(f"manifest frame count {len(frames)} != 68")

    manifest_by_file = {}
    for row in frames:
        if not isinstance(row, dict) or not isinstance(row.get("file"), str):
            errors.append("manifest row is not an object with string file")
            continue
        filename = norm_file(row["file"])
        if filename in manifest_by_file:
            errors.append(f"duplicate manifest file: {filename}")
        manifest_by_file[filename] = row
        if filename not in EXPECTED:
            errors.append(f"unexpected manifest file: {filename}")

    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / "runtime").rglob("*")
              if p.is_file() and p.suffix.lower() == ".png"}
    report["actualCount"] = len(actual)
    for filename in sorted(actual - EXPECTED.keys()):
        errors.append(f"unexpected runtime PNG: {filename}")
    byte_hashes, pixel_hashes = defaultdict(list), defaultdict(list)
    for filename, expected in EXPECTED.items():
        info = {"file": filename, **expected, "errors": [], "warnings": []}
        report["frames"].append(info)
        frame_errors, frame_warnings = info["errors"], info["warnings"]
        path = ROOT / filename
        row = manifest_by_file.get(filename)
        if row is None:
            frame_errors.append("missing manifest entry")
        else:
            for key, value in expected.items():
                if row.get(key) != value:
                    frame_errors.append(f"manifest {key}: {row.get(key)!r} != {value!r}")
            for key in ("width", "height"):
                if row.get(key) != 1024:
                    frame_errors.append(f"manifest {key} != 1024")
            pivot = row.get("pivot")
            if isinstance(pivot, dict):
                pivot = [pivot.get("x"), pivot.get("y")]
            if pivot != [0.5, 0.08]:
                frame_errors.append("manifest pivot must be [0.5, 0.08] (bottom-left origin)")
            for key in ("event", "visualStatus"):
                if key not in row:
                    frame_errors.append(f"manifest missing {key}")
            if not isinstance(row.get("sha256"), str) or not re.fullmatch(r"[0-9a-fA-F]{64}", row["sha256"]):
                frame_errors.append("manifest sha256 is missing or invalid")
        if not path.is_file():
            frame_errors.append("missing PNG — pending production")
            continue
        info["sha256"] = sha256(path)
        byte_hashes[info["sha256"]].append(filename)
        if row and str(row.get("sha256", "")).lower() != info["sha256"]:
            frame_errors.append("manifest SHA256 does not match PNG")
        try:
            with Image.open(path) as image:
                image.load()
                info.update(width=image.width, height=image.height, mode=image.mode, format=image.format)
                if image.format != "PNG":
                    frame_errors.append("file format is not PNG")
                if image.size != (1024, 1024):
                    frame_errors.append(f"size {image.size} != (1024, 1024)")
                if image.mode != "RGBA":
                    frame_errors.append(f"mode {image.mode} != RGBA")
                rgba = image.convert("RGBA")
                # Ignore RGB values under alpha=0 so invisible padding cannot hide duplicates.
                canonical = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
                canonical.paste(rgba, (0, 0))
                pixels = bytearray(canonical.tobytes())
                for offset in range(0, len(pixels), 4):
                    if pixels[offset + 3] == 0:
                        pixels[offset:offset + 3] = b"\0\0\0"
                pixel_sha = hashlib.sha256(bytes(pixels)).hexdigest()
                info["rgbaPixelSha256"] = pixel_sha
                pixel_hashes[pixel_sha].append(filename)
                alpha = rgba.getchannel("A")
                histogram = alpha.histogram()
                bbox = alpha.getbbox()
                info["alpha"] = {
                    "min": alpha.getextrema()[0], "max": alpha.getextrema()[1],
                    "fullyTransparentPixels": histogram[0],
                    "partiallyTransparentPixels": sum(histogram[1:255]),
                    "opaquePixels": histogram[255],
                    "nonzeroBounds": list(bbox) if bbox else None,
                }
                solid = alpha.point(lambda a: 255 if a >= 16 else 0).getbbox()
                info["alpha"]["boundsAt16"] = list(solid) if solid else None
                if not histogram[0]:
                    frame_errors.append("no fully transparent pixels")
                if bbox is None:
                    frame_errors.append("empty transparent frame")
                else:
                    margins = [bbox[0], bbox[1], image.width - bbox[2], image.height - bbox[3]]
                    info["alpha"]["marginsLTRB"] = margins
                    if min(margins) == 0:
                        frame_warnings.append("nonzero alpha touches canvas edge; inspect clipping/glow")
                    if solid and (solid[0] == 0 or solid[1] == 0 or solid[2] == image.width or solid[3] == image.height):
                        frame_errors.append("alpha >=16 touches canvas edge; resolve or explicitly review clipping")
        except (OSError, ValueError) as exc:
            frame_errors.append(f"unreadable image: {exc}")
        if row:
            ref = row.get("sourceRecord")
            if not isinstance(ref, str) or not ref:
                frame_errors.append("manifest sourceRecord must reference a JSON record")
            else:
                try:
                    record, record_sha = source_record(ref, info)
                    info["sourceRecord"] = ref
                    info["sourceRecordFileSha256"] = record_sha
                    # Only compare fields explicitly declared as the final/runtime artifact.
                    for key in ("finalSha256", "outputSha256"):
                        if key in record and str(record[key]).lower() != info["sha256"]:
                            frame_errors.append(f"source {key} does not match runtime PNG")
                    if "finalFile" in record and norm_file(record["finalFile"]) != filename:
                        frame_errors.append("source finalFile does not match runtime file")
                    if not any(key in record for key in ("prompt", "promptFile", "generation", "source", "operation", "receipt", "toolResult")):
                        frame_warnings.append("source record has no recognized prompt/generation/derivation evidence field; inspect manually")
                except (OSError, ValueError, KeyError) as exc:
                    frame_errors.append(str(exc))

    report["duplicateFileGroups"] = [names for names in byte_hashes.values() if len(names) > 1]
    report["duplicatePixelGroups"] = [names for names in pixel_hashes.values() if len(names) > 1]
    for names in report["duplicatePixelGroups"]:
        errors.append("duplicate RGBA frame pixels: " + ", ".join(names))
    for action, (count, duration) in CONTRACT.items():
        for direction in DIRECTIONS:
            rows = [r for r in report["frames"] if r["action"] == action and r["direction"] == direction]
            report["groups"][f"{action}/{direction}"] = {
                "expectedCount": count, "presentCount": sum(r["file"] in actual for r in rows),
                "durationMs": duration, "totalDurationMs": count * duration,
                "frameErrorCount": sum(len(r["errors"]) for r in rows),
                "frameWarningCount": sum(len(r["warnings"]) for r in rows),
            }
    report["errorCount"] = len(errors) + sum(len(r["errors"]) for r in report["frames"])
    report["warningCount"] = len(warnings) + sum(len(r["warnings"]) for r in report["frames"])
    report["technicalPassed"] = report["errorCount"] == 0
    output = ROOT / "validation.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['actualCount']}/68 PNGs; {report['errorCount']} errors; {report['warningCount']} warnings")
    print(f"Technical checks: {'PASS' if report['technicalPassed'] else 'INCOMPLETE/FAIL'}")
    print(f"Report: {output}")
    print("Art review and client acceptance are separate; this script does not mark them passed.")
    return 0 if report["technicalPassed"] else 1


if __name__ == "__main__":
    sys.exit(main())
