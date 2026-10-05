#!/usr/bin/env python3
"""Read-only by default. Validate 山鬼 runtime frames; optionally write audit JSON/manifest.

Requires Pillow. Does not edit images or evidence sidecars and does not infer visual approval.
All optional output paths must resolve inside the pack. Existing outputs require --overwrite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

CONTRACT = (("hit", 6, 40), ("attack", 12, 30), ("cast", 16, 45))
PACK_ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(image: Image.Image) -> Image.Image:
    """Ignore invisible RGB when comparing image content."""
    rgba = image.convert("RGBA")
    zero_alpha = rgba.getchannel("A").point(lambda a: 255 if a == 0 else 0)
    rgba.paste((0, 0, 0, 0), mask=zero_alpha)
    return rgba


def image_hash(image: Image.Image) -> str:
    return hashlib.sha256(str(image.size).encode() + image.tobytes()).hexdigest()


def read_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def local_path(root: Path, text: str, sidecar: Path | None = None) -> Path | None:
    if not isinstance(text, str) or not text or "://" in text:
        return None
    candidate = Path(text)
    if candidate.is_absolute():
        return candidate
    options = [root / candidate]
    if sidecar:
        options.append(sidecar.parent / candidate)
    # Project-relative references such as designs/... are allowed as read-only evidence.
    options.extend(parent / candidate for parent in root.parents)
    return next((p for p in options if p.is_file()), options[0])


def evidence_record(root: Path, file: Path, action: str, direction: str, frame: int):
    candidates = [Path(str(file) + ".generation.json"), file.with_suffix(".generation.json"),
                  root / "generation" / action / direction / f"{frame:02d}.json",
                  root / "records" / f"{action}-{direction}-{frame:02d}.json"]
    return next((p for p in candidates if p.is_file()), None)


def audit_sidecar(root: Path, path: Path, frame: dict, add):
    try:
        record = read_json(path)
    except (ValueError, OSError) as exc:
        add("error", "invalid_generation_json", frame["file"], str(exc))
        return None
    if not isinstance(record, dict):
        add("error", "generation_record_not_object", frame["file"], str(path))
        return None
    rel = path.relative_to(root).as_posix()
    frame["source"] = {"generationRecord": rel, "generationRecordSha256": sha256(path),
                       "actualModel": record.get("actualModel"), "actualQuality": record.get("actualQuality")}
    if record.get("sha256") and record["sha256"].lower() != (frame.get("sha256") or "").lower():
        add("error", "generation_sha_mismatch", frame["file"], rel)
    if not record.get("sha256"):
        add("error", "generation_sha_missing", frame["file"], rel)
    derived = record.get("derivedFrom")
    if derived:
        if not record.get("operation"):
            add("error", "derived_operation_missing", frame["file"], rel)
        sources = derived if isinstance(derived, list) else [derived]
        for source in sources:
            if not isinstance(source, dict) or not source.get("sha256"):
                add("error", "derived_source_sha_missing", frame["file"], rel)
            if isinstance(source, dict):
                origin = source.get("generationRecord") or source.get("record")
                if not origin:
                    add("error", "derived_source_record_missing", frame["file"], rel)
                else:
                    original_record = local_path(root, origin, path)
                    if original_record is None or not original_record.is_file():
                        add("error", "derived_source_record_not_found", frame["file"], str(origin))
        # Raw source image may have been intentionally removed under retention policy.
        # Keep provenance in place without claiming it was pixel-verified.
    else:
        required = ("generatedAt", "width", "height", "format", "tool", "route", "configSnapshot",
                    "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references")
        for key in required:
            if key not in record:
                add("error", "generation_field_missing", frame["file"], key)
        if record.get("actualModel") is None or record.get("actualQuality") is None:
            if not record.get("unverifiedReason"):
                add("error", "unknown_model_reason_missing", frame["file"], rel)
        submitted = record.get("submittedParameters")
        if isinstance(submitted, dict):
            for key in ("model", "quality"):
                if key not in submitted:
                    add("error", "submitted_parameter_missing", frame["file"], key)
        stamp = record.get("generatedAt")
        if stamp:
            try:
                parsed = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError("timezone is required")
            except ValueError as exc:
                add("error", "generated_at_invalid", frame["file"], str(exc))
        for key in ("width", "height"):
            if record.get(key) and record[key] != frame.get(key):
                add("warning", "native_export_size_differs", frame["file"],
                    f"{key}: native={record[key]}, exported={frame.get(key)}; exported frame needs a derivation record")
        prompt = local_path(root, record.get("prompt"), path)
        if prompt is not None and not prompt.is_file():
            add("error", "prompt_file_not_found", frame["file"], str(record.get("prompt")))
        refs = record.get("references")
        if isinstance(refs, list):
            for ref in refs:
                name = ref.get("path") or ref.get("file") if isinstance(ref, dict) else ref
                reference = local_path(root, name, path)
                if reference is not None and not reference.is_file():
                    add("warning", "reference_file_not_found", frame["file"], str(name))
    frame["event"] = record.get("event")
    frame["visualStatus"] = record.get("visualStatus", "not_recorded")
    return record


def inspect(root: Path, require_sources: bool):
    findings = []

    def add(level, code, file, detail):
        findings.append({"level": level, "code": code, "file": file, "detail": detail})

    frames, image_hashes, crop_hashes, byte_hashes = [], defaultdict(list), defaultdict(list), defaultdict(list)
    mirror_hashes = {}
    expected_paths = set()
    for action, count, duration in CONTRACT:
        for direction in ("E", "W"):
            for index in range(1, count + 1):
                relative = f"runtime/{action}/{direction}/{index:02d}.png"
                expected_paths.add(relative)
                file = root / relative
                frame = {"file": relative, "action": action, "direction": direction, "frame": index,
                         "durationMs": duration, "pivot": [0.5, 0.08], "footPointTopOrigin": [512, 942],
                         "width": None, "height": None, "sha256": None, "event": None,
                         "source": None, "visualStatus": "not_recorded", "technicalStatus": "missing"}
                frames.append(frame)
                if not file.is_file():
                    add("error", "missing_frame", relative, "Expected formal PNG is absent")
                    continue
                frame["sha256"] = sha256(file)
                byte_hashes[frame["sha256"]].append(relative)
                try:
                    with Image.open(file) as source:
                        source.load()
                        frame.update(width=source.width, height=source.height, format=source.format, mode=source.mode)
                        if source.format != "PNG" or source.mode != "RGBA":
                            add("error", "image_format", relative, f"Expected PNG RGBA; got {source.format} {source.mode}")
                        if source.size != (1024, 1024):
                            add("error", "image_dimensions", relative, f"Expected 1024×1024; got {source.size}")
                        rgba = normalized(source)
                        alpha = rgba.getchannel("A")
                        hist = alpha.histogram()
                        bbox = alpha.getbbox()
                        frame["alpha"] = {"min": alpha.getextrema()[0], "max": alpha.getextrema()[1],
                                          "transparentPixels": hist[0], "opaquePixels": hist[255],
                                          "partialPixels": sum(hist[1:255]), "contentBounds": list(bbox) if bbox else None}
                        if not bbox:
                            add("error", "empty_frame", relative, "All pixels transparent")
                        if hist[0] == 0:
                            add("error", "no_transparent_background", relative, "No fully transparent pixel")
                        w, h = rgba.size
                        edge_alpha = sum(sum(alpha.crop(box).histogram()[1:]) for box in
                                         ((0, 0, w, 1), (0, h-1, w, h), (0, 1, 1, h-1), (w-1, 1, w, h-1)))
                        frame["alpha"]["nontransparentBorderPixels"] = edge_alpha
                        if edge_alpha:
                            add("warning", "content_touches_border", relative, f"{edge_alpha} border pixels have alpha; inspect clipping")
                        pixel_hash = image_hash(rgba)
                        frame["pixelSha256"] = pixel_hash
                        image_hashes[pixel_hash].append(relative)
                        if bbox:
                            crop_hashes[image_hash(rgba.crop(bbox))].append(relative)
                        mirror_hashes[relative] = image_hash(ImageOps.mirror(rgba))
                        frame["technicalStatus"] = "checked"
                except (OSError, ValueError) as exc:
                    add("error", "unreadable_image", relative, str(exc))
                    frame["technicalStatus"] = "invalid"
                sidecar = evidence_record(root, file, action, direction, index)
                if sidecar:
                    audit_sidecar(root, sidecar, frame, add)
                else:
                    add("error" if require_sources else "warning", "generation_record_missing", relative,
                        "No per-image generation sidecar found")
    actual_paths = {p.relative_to(root).as_posix() for p in (root / "runtime").rglob("*.png")} if (root / "runtime").exists() else set()
    for extra in sorted(actual_paths - expected_paths):
        add("error", "unexpected_runtime_frame", extra, "Outside the exact 68-frame contract")
    for kind, groups in (("duplicate_file_sha", byte_hashes), ("duplicate_pixels", image_hashes),
                         ("duplicate_visible_crop", crop_hashes)):
        for paths in groups.values():
            if len(paths) > 1:
                add("error", kind, paths[0], paths)
    for file, mirrored in mirror_hashes.items():
        if "/W/" not in file:
            continue
        matches = [p for p in image_hashes.get(mirrored, []) if "/E/" in p]
        if matches:
            add("error", "mirrored_e_frame", file, matches)
    errors = sum(f["level"] == "error" for f in findings)
    report = {"schemaVersion": 1, "checkedAt": datetime.now(timezone.utc).isoformat(),
              "root": str(root), "expectedFrames": 68, "presentFrames": sum(f["sha256"] is not None for f in frames),
              "errors": errors, "warnings": sum(f["level"] == "warning" for f in findings),
              "technicalStatus": "failed" if errors else "passed",
              "visualStatus": "not_asserted_by_script", "clientStatus": "not_tested",
              "limitations": ["Pixel and SHA checks cannot establish AI generation or anatomical correctness.",
                              "Visible crop checks detect exact translated copies, not all possible duplicate edits.",
                              "No sprite is transformed or written by this script.",
                              "Event timings stay null unless supplied in frame evidence; no gameplay events are invented."],
              "findings": findings}
    manifest = {"schemaVersion": 1, "character": "山鬼", "slug": "02-mountain-imp", "generatedAt": report["checkedAt"],
                "contract": {"frameCount": 68, "width": 1024, "height": 1024, "format": "PNG", "mode": "RGBA",
                             "directions": {"E": "enemy, front three-quarter, facing lower-right",
                                            "W": "ally, rear three-quarter, facing upper-left"},
                             "actions": {a: {"framesPerDirection": n, "durationMs": ms} for a, n, ms in CONTRACT},
                             "pivot": [0.5, 0.08], "footPointTopOrigin": [512, 942]},
                "validation": {k: report[k] for k in ("technicalStatus", "visualStatus", "clientStatus", "errors", "warnings")},
                "frames": frames}
    return report, manifest


def save_json(root: Path, name: str, data, overwrite: bool):
    target = Path(name)
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Output must remain inside pack: {target}")
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to replace {target}; use --overwrite explicitly")
    if not target.parent.is_dir():
        raise ValueError(f"Output parent directory does not exist: {target.parent}")
    with target.open("w" if overwrite else "x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=PACK_ROOT, help="Pack root (defaults to this script's parent pack)")
    parser.add_argument("--manifest", metavar="PATH", help="Optional manifest output; missing frames remain explicitly missing")
    parser.add_argument("--report", metavar="PATH", help="Optional validation JSON output")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly permit replacing requested output JSON")
    parser.add_argument("--allow-missing-sources", action="store_true", help="Downgrade absent sidecars to warnings during production")
    parser.add_argument("--json", action="store_true", help="Print full validation JSON to stdout")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"Pack root does not exist: {root}")
    report, manifest = inspect(root, not args.allow_missing_sources)
    try:
        if args.manifest:
            save_json(root, args.manifest, manifest, args.overwrite)
        if args.report:
            save_json(root, args.report, report, args.overwrite)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Output error: {exc}\n")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Frames: {report['presentFrames']}/68 | Errors: {report['errors']} | Warnings: {report['warnings']}")
        print(f"Technical: {report['technicalStatus']} | Visual: not asserted | Client: not tested")
        for item in report["findings"]:
            print(f"{item['level'].upper()} {item['code']}: {item['file']} — {item['detail']}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
