"""Register builtin image results and assemble a 4x4 native-pixel tile.

All runtime output is confined to this task directory. No generation, resizing,
blending, registration, acceptance, or source deletion is performed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
CORE, HALO, NATIVE, GRID = 1024, 115, 1254, 4
SIZE = CORE * GRID
PADDED = SIZE + HALO * 2
PATCH_IDS = [f"r{r:02d}_c{c:02d}" for r in range(1, 5) for c in range(1, 5)]


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tile_path(tile):
    if not re.fullmatch(r"r(?:0[1-9]|1[0-6])_c(?:0[1-9]|1[0-6])", tile):
        raise ValueError("tile must be r01_c01 through r16_c16")
    result = (ROOT / tile).resolve()
    if not result.is_relative_to(ROOT):
        raise ValueError("output must remain inside this task directory")
    return result


def config_path(supplied):
    if supplied:
        return Path(supplied).resolve(strict=True)
    for parent in (ROOT, *ROOT.parents):
        candidate = parent / "config" / "image-generation.json"
        if candidate.is_file():
            return candidate
    raise ValueError("cannot find config/image-generation.json; pass --config")


def resolved_input(value, base=None):
    path = Path(value)
    if not path.is_absolute() and base:
        path = base / path
    return path.resolve(strict=True)


def copy_evidence(source, target):
    if source.resolve() != target.resolve():
        shutil.copyfile(source, target)
    return {"path": str(target), "sha256": sha256(target), "originalPath": str(source)}


def record(args):
    tile = tile_path(args.tile)
    source = resolved_input(args.source)
    prompt_source = resolved_input(args.prompt_file)
    result_source = resolved_input(args.tool_result_json)
    refs_source = resolved_input(args.references_json)
    submitted_source = resolved_input(args.submitted_parameters_json) if args.submitted_parameters_json else None
    # Validate everything before creating output; timestamps must include a timezone.
    timestamp = datetime.fromisoformat(args.generated_at.replace("Z", "+00:00"))
    if timestamp.utcoffset() is None:
        raise ValueError("--generated-at must include its UTC offset or Z")
    config_file = config_path(args.config)
    config = read_json(config_file)
    if not config.get("model") or not config.get("quality"):
        raise ValueError("configuration is missing model or quality")
    result = read_json(result_source)
    prompt = prompt_source.read_text(encoding="utf-8-sig")
    if not prompt.strip():
        raise ValueError("prompt cannot be empty")
    raw_refs = read_json(refs_source)
    if not isinstance(raw_refs, list) or not raw_refs:
        raise ValueError("references JSON must be a nonempty list of {path, role}")
    refs = []
    for ref in raw_refs:
        if not isinstance(ref, dict) or not ref.get("role") or not ref.get("path"):
            raise ValueError("each reference requires path and role")
        path = resolved_input(ref["path"], refs_source.parent)
        refs.append({**ref, "path": str(path), "sha256": sha256(path)})
    submitted = read_json(submitted_source) if submitted_source else {}
    if not isinstance(submitted, dict):
        raise ValueError("submitted parameters must be a JSON object")
    if submitted.get("model") is not None or submitted.get("quality") is not None:
        raise ValueError("this helper is for builtin calls without model/quality selectors")
    if "prompt" in submitted and submitted["prompt"] != prompt:
        raise ValueError("submitted prompt differs from the prompt file")
    submitted.update({"model": None, "quality": None, "prompt": prompt})
    with Image.open(source) as img:
        img.load()
        if img.format != "PNG" or img.size != (NATIVE, NATIVE):
            raise ValueError(f"expected a native {NATIVE}x{NATIVE} PNG; received {img.format} {img.size}")
        mode = img.mode
    native = tile / "native"
    target = native / f"{args.patch_id}.png"
    sidecar = target.with_name(target.name + ".generation.json")
    evidence_dir = native / "records" / args.patch_id
    if target.exists() or sidecar.exists() or evidence_dir.exists():
        raise ValueError(f"refusing to overwrite an existing patch or its evidence: {args.patch_id}")
    evidence_dir.mkdir(parents=True)
    evidence = {
        "toolResult": copy_evidence(result_source, evidence_dir / "tool-result.json"),
        "prompt": copy_evidence(prompt_source, evidence_dir / "prompt.txt"),
        "referenceInput": copy_evidence(refs_source, evidence_dir / "reference-input.json"),
    }
    if submitted_source:
        evidence["submittedParameters"] = copy_evidence(submitted_source, evidence_dir / "submitted-parameters.json")
    shutil.copyfile(source, target)
    source_hash = sha256(source)
    if sha256(target) != source_hash:
        raise ValueError("copied pixels failed SHA256 verification")
    data = {
        "schemaVersion": 1, "assetId": "lanxian_spring", "tile": args.tile,
        "patchId": args.patch_id, "file": str(target), "sha256": source_hash,
        "generatedAt": args.generated_at, "recordedAt": now(),
        "width": NATIVE, "height": NATIVE, "format": "PNG", "mode": mode,
        "tool": "image_gen.imagegen", "route": "builtin",
        "configSnapshot": config, "configSource": str(config_file),
        "submittedParameters": submitted, "actualModel": None, "actualQuality": None,
        "unverifiedReason": "宿主管理，工具未开放 model/quality 选择器，未披露可核实的实际型号和质量。",
        "originalToolResultImagePath": str(source), "originalToolResultImageSha256": source_hash,
        "toolResultMetadata": result, "evidence": evidence,
        "prompt": evidence["prompt"]["path"], "references": refs,
        "geometry": {"nativeSize": NATIVE, "coreSize": CORE, "halo": HALO,
                     "coreBox": [HALO, HALO, HALO + CORE, HALO + CORE]},
        "qa": {"status": "pending", "accepted": False},
    }
    write_json(sidecar, data)
    print(json.dumps({"file": str(target), "record": str(sidecar), "sha256": source_hash}, ensure_ascii=False))


def ownership(index):
    """Keep each 1024 core, plus the first/last patch's outward 115 halo."""
    start = 0 if index == 0 else HALO
    end = NATIVE if index == GRID - 1 else HALO + CORE
    destination = index * CORE + start
    return start, end, destination


def assemble(args):
    tile = tile_path(args.tile)
    canvas = Image.new("RGB", (PADDED, PADDED), "#573b59")
    draw = ImageDraw.Draw(canvas)
    for y in range(0, PADDED, 128):
        for x in range(0, PADDED, 128):
            if (x // 128 + y // 128) % 2:
                draw.rectangle((x, y, x + 127, y + 127), fill="#302938")
    sources, missing = [], []
    for row in range(GRID):
        for col in range(GRID):
            patch = f"r{row + 1:02d}_c{col + 1:02d}"
            file = tile / "native" / f"{patch}.png"
            if not file.is_file():
                missing.append(patch)
                draw.text((col * CORE + HALO + 20, row * CORE + HALO + 20), f"MISSING {patch}", fill="white")
                continue
            generation = file.with_name(file.name + ".generation.json")
            if not generation.is_file():
                raise ValueError(f"generation record missing: {generation}")
            record_data = read_json(generation)
            digest = sha256(file)
            if record_data.get("sha256") != digest:
                raise ValueError(f"source hash differs from its generation record: {file}")
            with Image.open(file) as image:
                image.load()
                if image.format != "PNG" or image.size != (NATIVE, NATIVE):
                    raise ValueError(f"invalid native patch dimensions or format: {file}")
                if "A" in image.getbands() and image.getchannel("A").getextrema() != (255, 255):
                    raise ValueError(f"nonopaque source requires an explicit transparency policy: {file}")
                x0, x1, dx = ownership(col)
                y0, y1, dy = ownership(row)
                box = [x0, y0, x1, y1]
                canvas.paste(image.convert("RGB").crop(box), (dx, dy))
            sources.append({"patchId": patch, "file": str(file), "sha256": digest,
                            "generationRecord": str(generation), "generationRecordSha256": sha256(generation),
                            "sourceCrop": box, "destinationXY": [dx, dy],
                            "sourceNativeSize": [NATIVE, NATIVE], "resized": False})
    output = tile / "assembly"
    output.mkdir(parents=True, exist_ok=True)
    preview = output / "coverage.png"
    canvas.save(preview)
    outputs = [{"file": str(preview), "sha256": sha256(preview), "role": "coverage_preview", "width": PADDED, "height": PADDED}]
    if not missing:
        padded = output / "candidate_with_halo.png"
        core = output / "candidate_4096.png"
        canvas.save(padded)
        canvas.crop((HALO, HALO, HALO + SIZE, HALO + SIZE)).save(core)
        outputs.extend([
            {"file": str(padded), "sha256": sha256(padded), "role": "unreviewed_candidate_with_halo", "width": PADDED, "height": PADDED},
            {"file": str(core), "sha256": sha256(core), "role": "unreviewed_candidate", "width": SIZE, "height": SIZE},
        ])
    elif any((output / name).exists() for name in ("candidate_with_halo.png", "candidate_4096.png")):
        # Never silently treat a candidate from an older assembly as current.
        print("WARNING: historical candidate files exist but are excluded from this incomplete assembly manifest")
    manifest = {
        "schemaVersion": 1, "assetId": "lanxian_spring", "tile": args.tile, "assembledAt": now(),
        "operation": "native-pixel core crop and paste; retain outward halo; no resizing or blending",
        "geometry": {"grid": [GRID, GRID], "nativePatchSize": NATIVE, "coreSize": CORE, "halo": HALO,
                     "coreOutputSize": SIZE, "paddedOutputSize": PADDED, "paddedCoreBox": [HALO, HALO, HALO + SIZE, HALO + SIZE]},
        "presentPatchCount": len(sources), "requiredPatchCount": 16, "missingPatchIds": missing,
        "fullPixelCoverage": not missing, "completeTileCount": 0, "acceptedTileCount": 0,
        "derivedFrom": sources, "outputs": outputs,
        "qa": {"status": "pending", "accepted": False,
               "reason": "Pixel coverage is not seam review, geometry alignment, or client acceptance.",
               "requiredChecks": ["all 24 internal seam segments", "all 9 internal four-patch junctions", "all 4 outer shared edges against neighbours", "all 4 outer corners", "shared daytime geometry and navigation constraints"],
               "coreSeamCoordinates": [1024, 2048, 3072], "paddedSeamCoordinates": [1139, 2163, 3187],
               "checkedRanges": [], "clientAccepted": False},
    }
    write_json(output / "manifest.json", manifest)
    for item in outputs:
        write_json(Path(item["file"] + ".derivation.json"), {
            "file": item["file"], "sha256": item["sha256"], "operation": manifest["operation"],
            "derivedFrom": sources, "manifest": str(output / "manifest.json"),
            "role": item["role"], "fullPixelCoverage": not missing, "accepted": False,
        })
    print(json.dumps({"manifest": str(output / "manifest.json"), "present": len(sources), "missing": missing, "accepted": False}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record", help="copy and record one real builtin 1254x1254 result")
    rec.add_argument("--tile", default="r08_c09")
    rec.add_argument("--patch-id", required=True, choices=PATCH_IDS)
    rec.add_argument("--source", required=True)
    rec.add_argument("--generated-at", required=True, help="actual generation timestamp, including timezone")
    rec.add_argument("--prompt-file", required=True)
    rec.add_argument("--tool-result-json", required=True, help="saved actual tool response metadata")
    rec.add_argument("--references-json", required=True, help="JSON list of {path, role}; relative paths resolve beside this file")
    rec.add_argument("--submitted-parameters-json", help="optional exact tool request object")
    rec.add_argument("--config")
    rec.set_defaults(func=record)
    asm = sub.add_parser("assemble", help="make a native coverage preview and, only when full, unreviewed candidates")
    asm.add_argument("--tile", default="r08_c09")
    asm.set_defaults(func=assemble)
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
