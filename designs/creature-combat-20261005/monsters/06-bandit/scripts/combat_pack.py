"""Truthful local packaging for individually generated bandit combat frames.

Never generates, mirrors, interpolates or substitutes artwork. Files can only be
written below this character directory. The caller controls when these commands
run; building previews does not record a visual or game-client acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[3]
SPEC = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
PIVOT = {"topOriginPixels": [512, 942], "bottomLeftNormalized": [0.5, 0.08]}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def within_root(path):
    candidate = Path(path)
    resolved = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f"Write target outside character package: {resolved}")
    return resolved


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def read_path(value):
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def write_json(path, value, *, replace=True):
    path = within_root(path)
    if path.exists() and not replace:
        raise FileExistsError(f"Refusing to overwrite provenance: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inspect_image(path):
    path = read_path(path)
    with Image.open(path) as original:
        original.load()
        rgba = original.convert("RGBA")
        alpha = rgba.getchannel("A")
        hist = alpha.histogram()
        bounds = alpha.getbbox()
        w, h = rgba.size
        edges = [alpha.crop((0, 0, w, 1)), alpha.crop((0, h - 1, w, h)),
                 alpha.crop((0, 0, 1, h)), alpha.crop((w - 1, 0, w, h))]
        return {
            "file": rel(path), "sha256": sha256(path),
            "pixelSha256": hashlib.sha256(rgba.tobytes()).hexdigest(),
            "width": w, "height": h, "mode": original.mode,
            "format": original.format, "hasAlphaChannel": "A" in original.getbands(),
            "alphaExtrema": list(alpha.getextrema()),
            "transparentPixels": hist[0], "opaquePixels": hist[255],
            "partialAlphaPixels": sum(hist[1:255]),
            "alphaBoundingBox": list(bounds) if bounds else None,
            "edgeAlphaMax": [edge.getextrema()[1] for edge in edges],
        }


def cmd_inspect(args):
    print(json.dumps([inspect_image(p) for p in args.paths], ensure_ascii=False, indent=2))


def cmd_ingest(args):
    source, dest = read_path(args.source), within_root(args.dest)
    if source == dest:
        raise ValueError("Ingest requires a distinct original tool-output path")
    metadata = load_json(read_path(args.metadata))
    for key in ("generatedAt", "prompt", "references"):
        if key not in metadata:
            raise ValueError(f"Metadata is missing {key}")
    timestamp = datetime.fromisoformat(metadata["generatedAt"].replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("generatedAt must include a timezone")
    if not metadata["prompt"] or not isinstance(metadata["references"], list):
        raise ValueError("A nonempty actual prompt and reference array are required")
    for reference in metadata["references"]:
        if not reference.get("role") or not read_path(reference["path"]).is_file():
            raise ValueError(f"Reference role/path missing: {reference}")
    native = inspect_image(source)
    if native["format"] != "PNG":
        raise ValueError("Ingest requires the actual tool PNG, not a renamed format")
    sidecar = Path(str(dest) + ".generation.json")
    prompt_file = Path(str(dest) + ".prompt.txt")
    for target in (dest, sidecar, prompt_file):
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite generation: {target}")
    config = metadata.get("configSnapshot") or load_json(PROJECT / "config/image-generation.json")
    config = {key: config[key] for key in ("model", "quality", "builtin_product", "verified_on", "sources")}
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    prompt_file.write_text(metadata["prompt"], encoding="utf-8")
    record = {
        "schemaVersion": 1, "file": rel(dest), "sha256": native["sha256"],
        "generatedAt": metadata["generatedAt"], "ingestedAt": utc_now(),
        "width": native["width"], "height": native["height"], "format": "PNG",
        "nativeImage": native, "tool": "image_gen.imagegen", "route": "builtin",
        "configSnapshot": config,
        "submittedParameters": {"model": None, "quality": None},
        "actualModel": metadata.get("actualModel"), "actualQuality": metadata.get("actualQuality"),
        "unverifiedReason": metadata.get("unverifiedReason", "宿主管理；内置工具无 model/quality 参数，未披露实际版本与质量。"),
        "evidence": metadata.get("evidence", []), "toolResult": metadata.get("toolResult"),
        "toolOutputOriginalPath": source.as_posix(),
        "prompt": rel(prompt_file), "references": metadata["references"],
        "imageRole": metadata.get("imageRole", "combat-frame"),
        "pose": metadata.get("pose"), "event": metadata.get("event"),
        "visualStatus": metadata.get("visualStatus", "pending-human-or-agent-visual-review"),
        "clientValidation": "not-performed",
    }
    write_json(sidecar, record, replace=False)
    print(json.dumps({"file": rel(dest), "generation": rel(sidecar), "native": native}, ensure_ascii=False))


def transform_image(image, transform):
    mode = transform.get("mode", "identity")
    if mode == "identity":
        if image.size != (1024, 1024):
            raise ValueError(f"Identity export needs native 1024 square, got {image.size}")
        return image.copy(), {"mode": "identity", "canvas": [1024, 1024]}
    if mode != "fixed-affine":
        raise ValueError("Only identity or direction-wide fixed-affine transforms are allowed")
    scale, tx, ty = (float(transform.get(k, d)) for k, d in (("scale", 1), ("translateX", 0), ("translateY", 0)))
    if not all(math.isfinite(x) for x in (scale, tx, ty)) or scale <= 0:
        raise ValueError("Scale must be positive; transform parameters must be finite")
    matrix = (1 / scale, 0, -tx / scale, 0, 1 / scale, -ty / scale)
    result = image.transform((1024, 1024), Image.Transform.AFFINE, matrix,
                             resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
    return result, {"mode": mode, "scale": scale, "translateX": tx,
                    "translateY": ty, "canvas": [1024, 1024], "resampling": "BICUBIC",
                    "scope": "one fixed transform for every frame/action in this direction"}


def cmd_export(args):
    plan = load_json(read_path(args.plan))
    transforms = plan["directionTransforms"]
    items = plan["frames"]
    used = set()
    for item in items:
        direction, action, number = item["direction"], item["action"], int(item["frame"])
        if direction not in DIRECTIONS or action not in SPEC or not 1 <= number <= SPEC[action][0]:
            raise ValueError(f"Invalid frame identity {item}")
        if "transform" in item:
            raise ValueError("Per-frame transforms are prohibited")
        key = (action, direction, number)
        if key in used:
            raise ValueError(f"Duplicate frame in export plan {key}")
        used.add(key)
        source = read_path(item["source"])
        generation = read_path(item.get("generation", str(source) + ".generation.json"))
        source_record = load_json(generation)
        source_info = inspect_image(source)
        if source_record.get("sha256") != source_info["sha256"]:
            raise ValueError(f"Source provenance SHA mismatch: {source}")
        dest = within_root(f"runtime/{action}/{direction}/{number:02d}.png")
        if dest.exists() or Path(str(dest) + ".generation.json").exists():
            raise FileExistsError(f"Refusing to overwrite exported frame: {dest}")
        with Image.open(source) as original:
            output, operation = transform_image(original.convert("RGBA"), transforms[direction])
        dest.parent.mkdir(parents=True, exist_ok=True)
        output.save(dest, format="PNG")
        record = {
            "schemaVersion": 1, "file": rel(dest), "sha256": sha256(dest),
            "width": 1024, "height": 1024, "format": "PNG", "exportedAt": utc_now(),
            "derivedFrom": [{"file": rel(source), "sha256": source_info["sha256"], "generation": rel(generation)}],
            "operation": operation, "nativeDimensions": [source_info["width"], source_info["height"]],
            "actualModel": source_record.get("actualModel"), "actualQuality": source_record.get("actualQuality"),
            "configSnapshot": source_record.get("configSnapshot"),
            "unverifiedReason": source_record.get("unverifiedReason"),
            "event": item.get("event", source_record.get("event")),
            "pose": item.get("pose", source_record.get("pose")),
            "visualStatus": item.get("visualStatus", "pending-human-or-agent-visual-review"),
            "clientValidation": "not-performed",
        }
        write_json(str(dest) + ".generation.json", record, replace=False)
    print(json.dumps({"exported": len(items), "clientValidation": "not-performed"}))


def trace_record(path, expected_sha=None, seen=None):
    seen = set() if seen is None else seen
    path = read_path(path)
    if path in seen:
        return [f"Cyclic generation chain: {rel(path)}"]
    seen.add(path)
    if not path.is_file():
        return [f"Missing generation record: {rel(path)}"]
    record, errors = load_json(path), []
    if expected_sha and record.get("sha256") != expected_sha:
        errors.append(f"Generation SHA mismatch: {rel(path)}")
    if record.get("derivedFrom"):
        for source in record["derivedFrom"]:
            source_path = read_path(source["file"])
            if source_path.exists() and sha256(source_path) != source["sha256"]:
                errors.append(f"Derived source SHA mismatch: {rel(source_path)}")
            errors.extend(trace_record(source["generation"], source["sha256"], seen.copy()))
    else:
        for key in ("generatedAt", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "unverifiedReason", "prompt", "references"):
            if key not in record:
                errors.append(f"Missing provenance field {key}: {rel(path)}")
        if record.get("prompt") and not read_path(record["prompt"]).is_file():
            errors.append(f"Missing actual prompt: {record['prompt']}")
        for reference in record.get("references", []):
            if not read_path(reference["path"]).is_file():
                errors.append(f"Missing active reference: {reference['path']}")
    return errors


def cmd_build(args):
    frames, missing, errors, warnings = [], [], [], []
    seen_files, seen_pixels, direction_operations = {}, {}, {d: {} for d in DIRECTIONS}
    groups = []
    for action, (count, duration) in SPEC.items():
        for direction in DIRECTIONS:
            group_frames = []
            for number in range(1, count + 1):
                relative = f"runtime/{action}/{direction}/{number:02d}.png"
                path = ROOT / relative
                if not path.is_file():
                    missing.append(relative)
                    continue
                info = inspect_image(path)
                generation_path = Path(str(path) + ".generation.json")
                generation = load_json(generation_path) if generation_path.exists() else {}
                errors.extend(trace_record(generation_path, info["sha256"]))
                if [info["width"], info["height"], info["mode"], info["format"]] != [1024, 1024, "RGBA", "PNG"]:
                    errors.append(f"Runtime format must be 1024×1024 RGBA PNG: {relative}")
                if not info["transparentPixels"] or not info["alphaBoundingBox"]:
                    errors.append(f"Missing transparent background or empty image: {relative}")
                if any(info["edgeAlphaMax"]):
                    warnings.append(f"Nonzero alpha reaches canvas edge; visually inspect clipping: {relative}")
                for field, seen in (("sha256", seen_files), ("pixelSha256", seen_pixels)):
                    digest = info[field]
                    if digest in seen:
                        errors.append(f"Duplicate {field}: {relative} and {seen[digest]}")
                    seen[digest] = relative
                operation = generation.get("operation", {"mode": "identity", "canvas": [1024, 1024]})
                operation_key = json.dumps(operation, sort_keys=True)
                direction_operations[direction].setdefault(operation_key, []).append(relative)
                frame = {
                    **info, "action": action, "direction": direction, "frame": number,
                    "durationMs": duration, "pivot": PIVOT,
                    "event": generation.get("event"), "pose": generation.get("pose"),
                    "source": generation.get("derivedFrom", [{"file": relative, "sha256": info["sha256"]}]),
                    "generation": rel(generation_path),
                    "visualStatus": generation.get("visualStatus", "pending-human-or-agent-visual-review"),
                }
                frames.append(frame)
                group_frames.append(frame)
            groups.append({"action": action, "direction": direction, "expectedFrames": count,
                           "durationMs": duration, "totalDurationMs": count * duration, "frames": group_frames})
    for direction, operations in direction_operations.items():
        if len(operations) > 1:
            errors.append(f"Mixed export transforms in direction {direction}")
    allowed = {f"runtime/{a}/{d}/{i:02d}.png" for a, (n, _) in SPEC.items() for d in DIRECTIONS for i in range(1, n + 1)}
    for path in (ROOT / "runtime").rglob("*.png") if (ROOT / "runtime").exists() else []:
        if rel(path) not in allowed:
            errors.append(f"Unexpected runtime PNG: {rel(path)}")
    report = {
        "checkedAt": utc_now(), "expectedFrames": 68, "foundFrames": len(frames),
        "technicalStatus": "passed" if not errors and not missing else "incomplete-or-failed",
        "missing": missing, "errors": errors, "warnings": warnings,
        "directionTransformConsistency": {d: len(v) <= 1 for d, v in direction_operations.items()},
        "visualValidation": "not-established-by-this-script", "clientValidation": "not-performed",
        "limitations": ["SHA uniqueness does not prove independently generated poses.",
                        "Alpha and dimensions do not establish anatomy, direction or motion continuity.",
                        "Play every group at normal and 0.25× speed and inspect each frame before artistic sign-off."],
    }
    manifest = {
        "schemaVersion": 1, "characterId": "06-bandit", "characterName": "山贼",
        "builtAt": utc_now(), "scope": "hit, attack, cast only; no movement loops",
        "contract": {"frameCount": 68, "size": [1024, 1024], "format": "RGBA PNG", "pivot": PIVOT,
                     "directions": {"E": "enemy three-quarter front facing down-right", "W": "ally true three-quarter rear facing up-left; independently drawn"}},
        "technicalStatus": report["technicalStatus"], "clientValidation": "not-performed",
        "missing": missing, "groups": groups, "frames": frames,
    }
    write_json(args.manifest, manifest)
    write_json(args.report, report)
    write_json(args.index, {"builtAt": utc_now(), "images": [{"file": f["file"], "sha256": f["sha256"], "generation": f["generation"]} for f in frames]})
    create_preview(manifest, args.preview)
    print(json.dumps({"manifest": args.manifest, "report": args.report, "preview": args.preview,
                      "foundFrames": len(frames), "missing": len(missing), "errors": len(errors),
                      "technicalStatus": report["technicalStatus"]}, ensure_ascii=False))
    if args.strict and (errors or missing):
        raise SystemExit(2)


def create_preview(manifest, target):
    target = within_root(target)
    import os
    data = json.loads(json.dumps(manifest))
    for group in data["groups"]:
        for frame in group["frames"]:
            frame["previewSrc"] = os.path.relpath(ROOT / frame["file"], target.parent).replace("\\", "/")
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    template = Path(__file__).with_name("preview-template.html").read_text(encoding="utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template.replace("__PACK_DATA__", data_json), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("inspect", help="Read-only dimensions/alpha/hash inspection")
    p.add_argument("paths", nargs="+")
    p.set_defaults(func=cmd_inspect)
    p = commands.add_parser("ingest", help="Copy one actual tool output and write its immutable provenance")
    p.add_argument("--source", required=True)
    p.add_argument("--dest", required=True)
    p.add_argument("--metadata", required=True)
    p.set_defaults(func=cmd_ingest)
    p = commands.add_parser("export", help="Apply only one fixed transform per direction")
    p.add_argument("--plan", required=True)
    p.set_defaults(func=cmd_export)
    p = commands.add_parser("build", help="Build manifest, provenance index, technical report and offline player")
    p.add_argument("--manifest", default="manifest.json")
    p.add_argument("--report", default="qa/technical-report.json")
    p.add_argument("--index", default="generation-index.json")
    p.add_argument("--preview", default="preview/index.html")
    p.add_argument("--strict", action="store_true", help="Exit 2 if incomplete or technical errors exist")
    p.set_defaults(func=cmd_build)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
