#!/usr/bin/env python3
"""Validate this wolf's existing PNGs and build its offline delivery index.

No images are created, rewritten, resized, or deleted. Default execution writes
manifest.json, technical-validation.json and preview/index.html. --check is
strictly read-only; --preview-only writes only preview/index.html. Exit 1 means
incomplete/invalid technical delivery, not a crash. Pillow is required.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image


ROOT = Path(r"D:\work\image\designs\creature-combat-20261005\monsters\01-wild-wolf").resolve()
CONTRACT = (("hit", 6, 40), ("attack", 12, 30), ("cast", 16, 45))
SHA = re.compile(r"^[0-9a-fA-F]{64}$")


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def inside(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f"Image/output path escapes this character directory: {path}")
    return resolved


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def flatten_refs(value):
    if isinstance(value, str):
        yield {"path": value}
    elif isinstance(value, list):
        for item in value:
            yield from flatten_refs(item)
    elif isinstance(value, dict):
        if any(key in value for key in ("path", "file", "sourcePath", "source")):
            yield value
        else:
            for role, item in value.items():
                for ref in flatten_refs(item):
                    yield {"role": role, **ref}


def reference_path(value: str, record_path: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    # Existing historical records use either image-relative or character-root paths.
    candidates = [record_path.parent / path, ROOT / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()


def validate():
    issues = []
    file_hashes = defaultdict(list)
    pixel_hashes = defaultdict(list)
    groups = []
    expected_paths = set()
    checked_refs = {}

    def issue(level, code, frame, detail):
        issues.append({"severity": level, "code": code, "frame": frame, "detail": detail})

    def inspect_references(data, record_path, frame):
        resolved_refs = []
        values = list(flatten_refs(data.get("references", [])))
        if data.get("derivedFrom"):
            values += [{"role": "derivedFrom", **ref}
                       for ref in flatten_refs(data["derivedFrom"])]
            if not data.get("operation"):
                issue("error", "missing_derivation_operation", frame, "derivedFrom requires operation")
        if not values:
            issue("error", "missing_references", frame, "No identity/style/source references recorded")
        for ref in values:
            value = ref.get("path", ref.get("file", ref.get("sourcePath", ref.get("source"))))
            if not isinstance(value, str):
                issue("error", "invalid_reference_path", frame, str(ref))
                continue
            if "://" in value:
                resolved_refs.append({**ref, "exists": None, "check": "remote_not_fetched"})
                issue("warning", "remote_reference_unchecked", frame, value)
                continue
            path = reference_path(value, record_path)
            recorded_sha = ref.get("sha256", ref.get("sourceSha256"))
            retired = ref.get("deleted") is True or ref.get("retained") is False or ref.get("status") in {"deleted", "removed"}
            exists = path.is_file()
            result = {**ref, "resolvedPath": str(path), "exists": exists}
            if not exists:
                if retired and isinstance(recorded_sha, str) and SHA.fullmatch(recorded_sha):
                    result["check"] = "retired_source_documented_not_pixel_verified"
                    issue("warning", "retired_reference", frame, str(path))
                else:
                    result["check"] = "missing"
                    issue("error", "missing_reference", frame, str(path))
            else:
                cache_key = str(path)
                if cache_key not in checked_refs:
                    checked_refs[cache_key] = digest(path)
                result["actualSha256"] = checked_refs[cache_key]
                if recorded_sha and recorded_sha.lower() != result["actualSha256"]:
                    issue("error", "reference_sha_mismatch", frame, str(path))
                elif not recorded_sha:
                    issue("warning", "reference_sha_unrecorded", frame, str(path))
                if ref.get("role") == "derivedFrom" and not recorded_sha:
                    issue("error", "missing_source_sha", frame, str(path))
                result["check"] = "read_and_hashed"
            resolved_refs.append(result)
        return resolved_refs

    for action, count, duration in CONTRACT:
        for direction in ("E", "W"):
            group = {"id": f"{action}-{direction}", "action": action, "direction": direction,
                     "frameCount": count, "durationMs": duration, "totalDurationMs": count * duration,
                     "frames": []}
            for number in range(1, count + 1):
                relative = f"runtime/{action}/{direction}/{number:02d}.png"
                expected_paths.add(relative)
                frame = {"file": relative, "frame": number, "action": action, "direction": direction,
                         "width": None, "height": None, "durationMs": duration,
                         "pivot": [0.5, 0.08], "anchorTopLeft": [512, 942],
                         "event": None, "sha256": None, "pixelSha256": None,
                         "generationRecord": None, "sourceReferences": [],
                         "visualStatus": "not_reviewed", "technicalStatus": "missing"}
                group["frames"].append(frame)
                start = len(issues)
                try:
                    image_path = inside(ROOT / relative)
                    if not image_path.is_file():
                        issue("error", "missing_frame", relative, "Expected PNG does not exist")
                        continue
                    frame["sha256"] = digest(image_path)
                    file_hashes[frame["sha256"]].append(relative)
                    with Image.open(image_path) as image:
                        image.load()
                        frame.update(width=image.width, height=image.height, mode=image.mode, format=image.format)
                        if image.format != "PNG":
                            issue("error", "not_png", relative, str(image.format))
                        if image.size != (1024, 1024):
                            issue("error", "wrong_size", relative, list(image.size))
                        if image.mode != "RGBA":
                            issue("error", "not_rgba", relative, image.mode)
                        rgba = image.convert("RGBA")
                        # Normalize invisible RGB only for duplicate detection, without editing a file.
                        normalized = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
                        normalized.paste(rgba, mask=rgba.getchannel("A").point(lambda x: 255 if x else 0))
                        frame["pixelSha256"] = hashlib.sha256(
                            str(rgba.size).encode("ascii") + normalized.tobytes()).hexdigest()
                        pixel_hashes[frame["pixelSha256"]].append(relative)
                        alpha = rgba.getchannel("A")
                        minimum, maximum = alpha.getextrema()
                        bounds = alpha.getbbox()
                        borders = [alpha.crop((0, 0, image.width, 1)),
                                   alpha.crop((0, image.height - 1, image.width, image.height)),
                                   alpha.crop((0, 0, 1, image.height)),
                                   alpha.crop((image.width - 1, 0, image.width, image.height))]
                        border_max = max(border.getextrema()[1] for border in borders)
                        frame["alpha"] = {"minimum": minimum, "maximum": maximum,
                                          "contentBounds": list(bounds) if bounds else None,
                                          "boundaryMaximum": border_max,
                                          "fullyTransparentBoundary": border_max == 0}
                        if maximum == 0:
                            issue("error", "empty_image", relative, "All pixels are transparent")
                        if minimum != 0:
                            issue("error", "no_fully_transparent_pixel", relative, minimum)
                        if border_max != 0:
                            issue("error", "opaque_boundary", relative, "Nonzero alpha on canvas boundary; inspect clipping")
                    candidates = [image_path.with_suffix(".png.generation.json"), image_path.with_suffix(".generation.json")]
                    records = [inside(path) for path in candidates if path.is_file()]
                    if not records:
                        issue("error", "missing_generation_record", relative, "Expected image-adjacent .generation.json")
                    else:
                        if len(records) > 1:
                            issue("warning", "ambiguous_generation_record", relative, "Both names exist; uses .png.generation.json")
                        record_path = records[0]
                        data = load_json(record_path)
                        if not isinstance(data, dict):
                            raise ValueError("Generation record must be a JSON object")
                        frame["generationRecord"] = record_path.relative_to(ROOT).as_posix()
                        output = data.get("output") if isinstance(data.get("output"), dict) else {}
                        recorded_sha = data.get("sha256", output.get("sha256"))
                        if not isinstance(recorded_sha, str) or not SHA.fullmatch(recorded_sha):
                            issue("error", "missing_or_invalid_record_sha", relative, "Record needs this output's SHA256")
                        elif recorded_sha.lower() != frame["sha256"]:
                            issue("error", "output_sha_mismatch", relative, "Generation record SHA differs from current file")
                        for key in ("generatedAt", "tool", "route", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt"):
                            if key not in data:
                                issue("error", "missing_provenance_field", relative, key)
                        if any(data.get(key) is None for key in ("actualModel", "actualQuality")) and not data.get("unverifiedReason"):
                            issue("error", "missing_unverified_reason", relative, "Unknown actual model/quality needs an explicit reason")
                        submitted = data.get("submittedParameters")
                        if isinstance(submitted, dict):
                            for key in ("model", "quality"):
                                if key not in submitted:
                                    issue("error", "missing_submitted_parameter", relative, key)
                        elif submitted is not None:
                            issue("error", "invalid_submitted_parameters", relative, "Expected object with model/quality, null allowed per field")
                        frame["modelEvidence"] = {key: data.get(key) for key in
                                                  ("configSnapshot", "submittedParameters", "actualModel", "actualQuality", "unverifiedReason")}
                        frame["sourceReferences"] = inspect_references(data, record_path, relative)
                        prompt = data.get("prompt")
                        prompt_value = prompt.get("path") if isinstance(prompt, dict) else prompt
                        if isinstance(prompt_value, str) and (prompt_value.endswith((".txt", ".md")) or Path(prompt_value).is_absolute()):
                            if not reference_path(prompt_value, record_path).is_file():
                                issue("error", "missing_prompt_file", relative, prompt_value)
                        for key in ("action", "direction"):
                            if key in data and data[key] != frame[key]:
                                issue("error", "record_identity_mismatch", relative, key)
                        for key in ("pivot", "anchorTopLeft"):
                            if key in data and data[key] != frame[key]:
                                issue("error", "coordinate_contract_mismatch", relative, {key: data[key]})
                        frame["event"] = data.get("event")
                        frame["visualStatus"] = data.get("visualStatus", "not_reviewed")
                    frame["technicalStatus"] = "failed" if any(item["severity"] == "error" for item in issues[start:]) else "passed"
                except (OSError, ValueError, TypeError, AttributeError) as exc:
                    issue("error", "frame_inspection_failed", relative, str(exc))
                    frame["technicalStatus"] = "failed"
            groups.append(group)

    runtime = ROOT / "runtime"
    if runtime.exists():
        for path in runtime.rglob("*.png"):
            relative = path.relative_to(ROOT).as_posix()
            if relative not in expected_paths:
                issue("error", "unexpected_runtime_png", relative, "Outside the six authorized groups/numbering")
    duplicate_files = [paths for paths in file_hashes.values() if len(paths) > 1]
    duplicate_pixels = [paths for paths in pixel_hashes.values() if len(paths) > 1]
    for paths in duplicate_pixels:
        for path in paths:
            issue("error", "duplicate_pixels", path, paths)
    duplicates = {path for paths in duplicate_pixels for path in paths}
    for group in groups:
        for frame in group["frames"]:
            if frame["file"] in duplicates:
                frame["technicalStatus"] = "failed"
    frames = [frame for group in groups for frame in group["frames"]]
    errors = sum(item["severity"] == "error" for item in issues)
    summary = {"expectedFrames": 68, "existingFrames": sum(frame["sha256"] is not None for frame in frames),
               "passedFrames": sum(frame["technicalStatus"] == "passed" for frame in frames),
               "errors": errors, "warnings": sum(item["severity"] == "warning" for item in issues),
               "technicalPassed": errors == 0}
    timestamp = datetime.now(timezone.utc).isoformat()
    manifest = {"schemaVersion": 1, "character": "野狼", "slug": "01-wild-wolf", "builtAt": timestamp,
                "root": str(ROOT), "contract": "COMBAT_SPEC.md / 2026-10-05 / six combat groups",
                "coordinateConvention": {"origin": "top-left", "anchorTopLeft": [512, 942],
                                         "pivotOrigin": "bottom-left", "pivot": [0.5, 0.08],
                                         "note": "Contract coordinates; not measured or realigned by this script."},
                "directions": {"E": "敌方斜前朝右下", "W": "我方真斜后朝左上；独立绘制"},
                "clientAcceptance": "not_performed_by_this_tool",
                "visualAcceptance": "requires_human_all_frame_and_playback_review",
                "summary": summary, "groups": groups}
    report = {"schemaVersion": 1, "builtAt": timestamp, "summary": summary, "issues": issues,
              "duplicateFileGroups": duplicate_files, "duplicatePixelGroups": duplicate_pixels,
              "scope": "PNG decoding/dimensions/RGBA/alpha boundary, output/source SHA, frame inventory and provenance fields",
              "limitations": ["Does not establish anatomy, pose independence, perspective, identity, foot continuity or gameplay acceptance.",
                              "Metadata visualStatus is copied as recorded, not independently accepted.",
                              "Deleted sources are only traceable by recorded hashes; remote references are not fetched.",
                              "No image pixels are modified. No model/API/network calls are made."]}
    return manifest, report


def safe_write(path: Path, text: str):
    path = inside(path)
    inside(path.parent).mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_preview(manifest, report):
    template = inside(Path(__file__).with_name("preview.template.html")).read_text(encoding="utf-8")
    payload = json.dumps({"manifest": manifest, "report": report}, ensure_ascii=False).replace("<", "\\u003c")
    safe_write(ROOT / "preview" / "index.html", template.replace("__DELIVERY_DATA__", payload))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Only this wolf's fixed authorized root is accepted")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Read-only validation; print JSON report; write nothing")
    mode.add_argument("--preview-only", action="store_true", help="Write only preview/index.html")
    args = parser.parse_args()
    if args.root.resolve() != ROOT or Path(__file__).resolve().parent.parent != ROOT:
        parser.error(f"This script is restricted to {ROOT}")
    manifest, report = validate()
    if args.check:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        if not args.preview_only:
            safe_write(ROOT / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
            safe_write(ROOT / "technical-validation.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        build_preview(manifest, report)
        print(json.dumps(report["summary"], ensure_ascii=False))
        print(str(ROOT / "preview" / "index.html"))
    return 0 if report["summary"]["technicalPassed"] else 1


if __name__ == "__main__":
    sys.exit(main())
