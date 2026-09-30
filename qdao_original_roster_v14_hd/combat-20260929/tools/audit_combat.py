#!/usr/bin/env python3
"""Read-only PNG/receipt audit and offline preview; Python standard library only.

Does not create or change any image. Reports technical readiness only; the
manifest always leaves visual approval and client integration pending.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
from datetime import datetime, timezone
import zlib

ACTIONS = {"hit": (6, 240), "attack": (12, 360), "cast": (16, 720)}
DIRECTIONS = ("E", "W")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    distances = (abs(p - a), abs(p - b), abs(p - c))
    return (a, b, c)[distances.index(min(distances))]


def inspect_png(path: Path) -> dict:
    """Decode existing noninterlaced 8-bit PNGs for exact RGBA comparison.

    Pixel comparison ignores container metadata but preserves hidden RGB.
    Unsupported encodings are reported, never silently certified.
    """
    raw = path.read_bytes()
    if raw[:8] != PNG_SIGNATURE:
        raise ValueError("Not a PNG")
    cursor, chunks, saw_end = 8, {}, False
    while cursor + 12 <= len(raw):
        length = struct.unpack_from(">I", raw, cursor)[0]
        kind = raw[cursor + 4:cursor + 8]
        stop = cursor + 12 + length
        if stop > len(raw):
            raise ValueError("Truncated PNG chunk")
        data = raw[cursor + 8:cursor + 8 + length]
        stored_crc = struct.unpack_from(">I", raw, cursor + 8 + length)[0]
        if binascii.crc32(kind + data) & 0xFFFFFFFF != stored_crc:
            raise ValueError("PNG chunk CRC mismatch: " + kind.decode("ascii", "replace"))
        chunks.setdefault(kind, []).append(data)
        cursor = stop
        if kind == b"IEND":
            saw_end = True
            break
    if not saw_end or len(chunks.get(b"IHDR", [])) != 1:
        raise ValueError("Missing IEND or invalid IHDR")
    width, height, depth, color_type, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", chunks[b"IHDR"][0]
    )
    result = {
        "width": width, "height": height, "bit_depth": depth,
        "color_type": color_type, "interlace": interlace,
        "alpha_channel": color_type in (4, 6), "transparency_chunk": b"tRNS" in chunks,
        "sha256": hashlib.sha256(raw).hexdigest(), "file_bytes": len(raw),
    }
    if not 1 <= width <= 8192 or not 1 <= height <= 8192:
        raise ValueError("PNG dimensions outside audit safety bound (1..8192)")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    if depth != 8 or interlace != 0 or compression != 0 or filtering != 0 or not channels:
        raise ValueError("Pixel audit supports noninterlaced 8-bit PNG only")
    stride = width * channels
    expected = height * (stride + 1)
    decoder = zlib.decompressobj()
    scanlines = decoder.decompress(b"".join(chunks.get(b"IDAT", [])), expected + 1)
    if len(scanlines) != expected or not decoder.eof or decoder.unused_data:
        raise ValueError("Invalid or unexpected decompressed PNG size")
    palette = b"".join(chunks.get(b"PLTE", []))
    trns = b"".join(chunks.get(b"tRNS", []))
    if color_type == 3 and (not palette or len(palette) % 3):
        raise ValueError("Invalid indexed PNG palette")
    transparent_gray = struct.unpack(">H", trns)[0] if color_type == 0 and trns else None
    transparent_rgb = struct.unpack(">HHH", trns) if color_type == 2 and trns else None
    rgba_hash, visible_hash = hashlib.sha256(), hashlib.sha256()
    alpha_min, alpha_max, transparent, opaque = 255, 0, 0, 0
    left, top, right, bottom = width, height, -1, -1
    previous = bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        mode = scanlines[start]
        row = bytearray(scanlines[start + 1:start + 1 + stride])
        if mode > 4:
            raise ValueError("Invalid PNG filter")
        for i in range(stride):
            a = row[i - channels] if i >= channels else 0
            b = previous[i]
            c = previous[i - channels] if i >= channels else 0
            predictor = 0 if mode == 0 else a if mode == 1 else b if mode == 2 else (a + b) // 2 if mode == 3 else paeth(a, b, c)
            row[i] = (row[i] + predictor) & 255
        rgba = bytearray(width * 4)
        for x in range(width):
            i = x * channels
            if color_type == 6:
                r, g, b, alpha = row[i:i + 4]
            elif color_type == 4:
                r = g = b = row[i]
                alpha = row[i + 1]
            elif color_type == 2:
                r, g, b = row[i:i + 3]
                alpha = 0 if (r, g, b) == transparent_rgb else 255
            elif color_type == 0:
                r = g = b = row[i]
                alpha = 0 if r == transparent_gray else 255
            else:
                p = row[i]
                if p * 3 + 3 > len(palette):
                    raise ValueError("PNG palette index out of range")
                r, g, b = palette[p * 3:p * 3 + 3]
                alpha = trns[p] if p < len(trns) else 255
            rgba[x * 4:x * 4 + 4] = bytes((r, g, b, alpha))
            alpha_min, alpha_max = min(alpha_min, alpha), max(alpha_max, alpha)
            transparent += alpha == 0
            opaque += alpha == 255
            if alpha > 8:
                left, top, right, bottom = min(left, x), min(top, y), max(right, x), max(bottom, y)
        rgba_hash.update(rgba)
        # Hidden RGB in fully transparent pixels cannot hide a copied frame.
        for i in range(0, len(rgba), 4):
            if rgba[i + 3] == 0:
                rgba[i:i + 3] = b"\x00\x00\x00"
        visible_hash.update(rgba)
        previous = row
    result.update(
        pixel_sha256=rgba_hash.hexdigest(), visible_pixel_sha256=visible_hash.hexdigest(),
        alpha_min=alpha_min, alpha_max=alpha_max, transparent_pixels=transparent,
        opaque_pixels=opaque, visible_bbox=None if right < 0 else [left, top, right + 1, bottom + 1],
    )
    return result


def receipt_entries(data):
    if isinstance(data, list):
        for value in data:
            yield from receipt_entries(value)
    elif isinstance(data, dict):
        if any(isinstance(data.get(key), str) for key in ("file", "asset_path", "output_path")):
            yield data
        for key in ("assets", "outputs", "frames", "images", "records"):
            if key in data:
                yield from receipt_entries(data[key])


def normalize_asset(value: str, root: Path, receipt_path: Path) -> str:
    value = value.replace("\\", "/")
    path = Path(value)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return value
    value = value.removeprefix("./")
    if not value.startswith("characters/"):
        receipt_relative = receipt_path.relative_to(root)
        # A character-local receipt may name runtime/... relative to that
        # character. Preserve its full historical identifier in the manifest.
        if len(receipt_relative.parts) > 2 and receipt_relative.parts[0] == "characters":
            return (Path(*receipt_relative.parts[:2]) / value).as_posix()
    return value


def load_receipts(root: Path):
    receipts, problems = {}, []
    receipt_paths = set(root.glob("characters/*/provenance/receipts/**/*.json"))
    # Retain compatibility with a batch-level index without requiring it.
    receipt_paths.update((root / "provenance" / "receipts").rglob("*.json"))
    for path in sorted(receipt_paths):
        relative = path.relative_to(root).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            for entry in receipt_entries(data):
                asset = next(entry[key] for key in ("file", "asset_path", "output_path") if isinstance(entry.get(key), str))
                asset = normalize_asset(asset, root, path)
                receipts.setdefault(asset, []).append((relative, entry))
        except (ValueError, OSError) as error:
            problems.append({"code": "invalid_receipt_json", "path": relative, "detail": str(error)})
    return receipts, problems


def provenance_problems(entry: dict, actual_sha: str) -> list[str]:
    problems = []
    if str(entry.get("sha256", "")).lower() != actual_sha:
        problems.append("receipt_sha256_missing_or_mismatch")
    if entry.get("derivedFrom"):
        if not entry.get("operation"):
            problems.append("derived_receipt_missing_operation")
        return problems
    for key in ("generatedAt", "tool", "route", "configSnapshot", "submittedParameters", "evidence", "prompt", "references"):
        if key not in entry:
            problems.append("receipt_missing_" + key)
    for key in ("actualModel", "actualQuality"):
        if key not in entry:
            problems.append("receipt_missing_" + key)
        elif entry[key] is None and not entry.get("unverifiedReason"):
            problems.append("receipt_unknown_without_reason_" + key)
    return problems


def build_manifest(root: Path, characters: list[str]) -> dict:
    receipts, issues = load_receipts(root)
    records, duplicate_groups = [], {}
    for character in characters:
        for action, (count, duration) in ACTIONS.items():
            for direction in DIRECTIONS:
                for number in range(1, count + 1):
                    relative = f"characters/{character}/runtime/{action}/{direction}/{number:02d}.png"
                    path = root / relative
                    record = {"character": character, "action": action, "direction": direction,
                              "number": number, "path": relative, "exists": path.is_file(),
                              "duration_ms": duration / count, "receipt_paths": [], "issues": []}
                    if not path.is_file():
                        record["issues"].append("missing_frame")
                    else:
                        try:
                            record.update(inspect_png(path))
                            if (record["width"], record["height"]) != (1024, 1024):
                                record["issues"].append("wrong_dimensions")
                            if not record["alpha_channel"]:
                                record["issues"].append("missing_alpha_channel")
                            if not record["transparent_pixels"]:
                                record["issues"].append("no_fully_transparent_pixels")
                            if record["visible_bbox"] is None:
                                record["issues"].append("fully_invisible_frame")
                            duplicate_groups.setdefault((record["width"], record["height"], record["visible_pixel_sha256"]), []).append(record)
                            matches = receipts.get(relative, [])
                            record["receipt_paths"] = [name for name, _ in matches]
                            if not matches:
                                record["issues"].append("missing_receipt")
                            else:
                                matching = [(name, entry) for name, entry in matches if str(entry.get("sha256", "")).lower() == record["sha256"]]
                                if not matching:
                                    record["issues"].append("receipt_sha256_missing_or_mismatch")
                                else:
                                    name, entry = matching[-1]
                                    record["verified_receipt_path"] = name
                                    record["issues"].extend(provenance_problems(entry, record["sha256"]))
                                    record["actual_model"] = entry.get("actualModel")
                                    record["actual_quality"] = entry.get("actualQuality")
                                    record["derived_from"] = entry.get("derivedFrom")
                        except (ValueError, OSError, struct.error, zlib.error) as error:
                            record["issues"].append("png_audit_error")
                            record["error"] = str(error)
                    records.append(record)
    duplicates = []
    for group in duplicate_groups.values():
        if len(group) > 1:
            duplicates.append([record["path"] for record in group])
            for record in group:
                record["issues"].append("duplicate_visible_pixels")
    expected_paths = {record["path"] for record in records}
    for character in characters:
        for path in (root / "characters" / character / "runtime").rglob("*.png"):
            relative = path.relative_to(root).as_posix()
            if relative not in expected_paths:
                issues.append({"code": "unexpected_runtime_png", "path": relative})
    present = sum(record["exists"] for record in records)
    invalid = sum(bool(record["issues"]) for record in records)
    return {
        "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "offline_pending", "client_integration": "not_integrated",
        "visual_approval": "pending", "runtime_acceptance": "not_tested",
        "note": "Technical audit only. Unique pixels do not prove unique poses, consistent identity, or animation quality.",
        "root": str(root), "characters": characters, "directions": list(DIRECTIONS),
        "actions": {name: {"frames_per_direction": count, "duration_ms": ms, "frame_duration_ms": ms / count} for name, (count, ms) in ACTIONS.items()},
        "frame_size": [1024, 1024], "summary": {
            "expected": len(records), "present": present, "missing": len(records) - present,
            "frames_with_issues": invalid, "duplicate_groups": len(duplicates),
            "global_issues": len(issues), "technical_audit_passed": invalid == 0 and not issues,
        }, "issues": issues, "duplicate_groups": duplicates, "frames": records,
    }


def write_preview(manifest: dict, root: Path, destination: Path) -> None:
    preview_data = dict(manifest)
    preview_data["frames"] = [dict(frame, url=Path(os.path.relpath(root / frame["path"], destination.parent)).as_posix()) for frame in manifest["frames"]]
    data = json.dumps(preview_data, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    template = Path(__file__).with_name("preview_template.html").read_text(encoding="utf-8")
    destination.write_text(template.replace("__MANIFEST_JSON__", data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--characters", nargs="+", help="Full retained IDs or two-digit aliases; default 00 pilot")
    selection.add_argument("--all-retained", action="store_true", help="All active_character_ids in the authoritative scope file")
    parser.add_argument("--scope-state", type=Path, default=None, help="Default: roster root/CONTINUATION_STATE_20260920_SCOPE_UPDATED.json")
    parser.add_argument("--out", type=Path, default=None, help="Output directory; default tools/report")
    parser.add_argument("--allow-incomplete", action="store_true", help="Return 0 even when the report has issues; report status is unchanged")
    args = parser.parse_args()
    root = args.root.resolve()
    scope_path = (args.scope_state or root.parent / "CONTINUATION_STATE_20260920_SCOPE_UPDATED.json").resolve()
    try:
        active_ids = json.loads(scope_path.read_text(encoding="utf-8-sig"))["active_character_ids"]
        if not isinstance(active_ids, list) or not active_ids or any(
            not isinstance(value, str) or len(value) < 4 or not value[:2].isdigit()
            or value[2] != "_" or "/" in value or "\\" in value for value in active_ids
        ) or len(active_ids) != len(set(active_ids)):
            raise ValueError("Invalid active_character_ids")
    except (OSError, ValueError, KeyError) as error:
        parser.error(f"Cannot read authoritative retained-character scope: {scope_path}: {error}")
    aliases = {}
    for character in active_ids:
        if character[:2] in aliases:
            parser.error(f"Ambiguous character prefix in scope: {character[:2]}")
        aliases[character[:2]] = character
    if args.all_retained:
        characters = active_ids
    else:
        characters = []
        for value in args.characters or ["00"]:
            full_id = aliases.get(value, value)
            if full_id not in active_ids:
                parser.error(f"Character {value!r} is not in active_character_ids; excluded IDs cannot be restored by this tool")
            if full_id not in characters:
                characters.append(full_id)
    destination = (args.out or Path(__file__).resolve().parent / "report").resolve()
    manifest = build_manifest(root, characters)
    manifest["scope_source"] = str(scope_path)
    manifest["retained_character_count"] = len(active_ids)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_preview(manifest, root, destination / "index.html")
    print(json.dumps({"output": str(destination), "status": manifest["status"], **manifest["summary"]}, ensure_ascii=False))
    return 0 if manifest["summary"]["technical_audit_passed"] or args.allow_incomplete else 2


if __name__ == "__main__":
    sys.exit(main())
