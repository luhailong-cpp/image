"""Native 1:1 candidate assembly and QA export for lanxian_day only.

CLI: ingest JOB.json | assemble TILE_DIR | qa TILE_DIR [--west FILE]
     external-west TILE_DIR WEST_CORE.png

Ingest job fields: tileDir, cell (r01_c01..r04_c04), sourceOutputPath,
generatedAt (ISO 8601 with offset), prompt or promptFile, references
([{path, role}]), and configSnapshot. Optional: expectedSha256,
toolResultPath, toolResultId, submittedParameters. Relative output tileDir
is rooted at OUTPUT_ROOT; relative input paths are rooted at the job file.
No commands generate AI images, approve candidates, or update progress.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime, timezone
from uuid import uuid4

import numpy as np
from PIL import Image


OUTPUT_ROOT = Path(
    "D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/"
    "parallel_20261005/lanxian_day"
).resolve()
NATIVE, CORE, HALO, GRID = 1254, 1024, 115, 4
TILE, EXTENDED = CORE * GRID, CORE * GRID + 2 * HALO
CELL_RE = re.compile(r"r0[1-4]_c0[1-4]\Z")
UNKNOWN = "宿主管理，工具未披露／无可核实元数据；配置和提示词不代表实际版本证据。"


def now():
    return datetime.now(timezone.utc).isoformat()


def safe_output(value):
    """Resolve existing symlinks/junctions before every filesystem write."""
    path = Path(value)
    if not path.is_absolute():
        path = OUTPUT_ROOT / path
    path = path.resolve()
    if path == OUTPUT_ROOT or not path.is_relative_to(OUTPUT_ROOT):
        raise ValueError(f"Output must be strictly inside {OUTPUT_ROOT}: {path}")
    return path


def input_path(value, base):
    path = Path(value)
    return (path if path.is_absolute() else base / path).resolve(strict=True)


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def atomic_write(path, writer):
    path = safe_output(path)
    safe_output(path.parent).mkdir(parents=True, exist_ok=True)
    temporary = safe_output(path.with_name(path.name + "." + uuid4().hex + ".tmp"))
    try:
        writer(temporary)
        os.replace(safe_output(temporary), safe_output(path))
    finally:
        if temporary.exists():
            safe_output(temporary).unlink()


def write_json(path, value):
    atomic_write(path, lambda temp: temp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"))


def save_image(path, image):
    atomic_write(path, lambda temp: image.save(temp, format="PNG"))
    return {"file": str(safe_output(path)), "sha256": sha256(path),
            "width": image.width, "height": image.height, "format": "PNG",
            "mode": image.mode}


def load_image(path, size):
    with Image.open(path) as image:
        if image.format != "PNG" or image.size != size:
            raise ValueError(f"Expected PNG {size}, got {image.format} {image.size}: {path}")
        if image.mode not in ("RGB", "RGBA"):
            raise ValueError(f"Only RGB/RGBA native images are supported: {path}: {image.mode}")
        image.load()
        return image.copy()


def ingest(job_json):
    job_file = Path(job_json).resolve(strict=True)
    job = read_json(job_file)
    tile = safe_output(job["tileDir"])
    cell = job["cell"]
    if not CELL_RE.fullmatch(cell):
        raise ValueError("cell must be r01_c01 through r04_c04")
    generated_at = datetime.fromisoformat(job["generatedAt"].replace("Z", "+00:00"))
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generatedAt requires a timezone")
    snapshot = job["configSnapshot"]
    if not isinstance(snapshot, dict):
        raise ValueError("configSnapshot must be an object")
    for key in ("model", "quality", "builtin_product", "verified_on", "sources"):
        if key not in snapshot:
            raise ValueError(f"Missing configSnapshot.{key}")
    source = input_path(job["sourceOutputPath"], job_file.parent)
    source_sha = sha256(source)
    if job.get("expectedSha256") and source_sha.lower() != job["expectedSha256"].lower():
        raise ValueError("Source SHA256 does not match expectedSha256")
    native = load_image(source, (NATIVE, NATIVE))
    prompt = job.get("prompt")
    if prompt is None and job.get("promptFile"):
        prompt = input_path(job["promptFile"], job_file.parent).read_text(encoding="utf-8-sig")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("The actual submitted prompt must be supplied")
    references = []
    if not isinstance(job["references"], list) or not job["references"]:
        raise ValueError("At least one attached style/context reference with role is required")
    for reference in job["references"]:
        if not reference.get("role"):
            raise ValueError("Each reference needs its actual role")
        ref = input_path(reference["path"], job_file.parent)
        entry = dict(reference, path=str(ref), sha256=sha256(ref))
        with Image.open(ref) as ref_image:
            entry.update(width=ref_image.width, height=ref_image.height)
        references.append(entry)
    submitted = dict(job.get("submittedParameters") or {})
    if submitted.get("model") is not None or submitted.get("quality") is not None:
        raise ValueError("This builtin workflow has no model/quality selectors; fields must be null")
    if submitted.get("prompt", prompt) != prompt:
        raise ValueError("prompt and submittedParameters.prompt disagree")
    submitted.update(model=None, quality=None, prompt=prompt)
    result_evidence = {"sourceOutputPath": str(source), "sourceOutputSha256": source_sha}
    if job.get("toolResultPath"):
        result_path = input_path(job["toolResultPath"], job_file.parent)
        result_evidence.update(toolResultPath=str(result_path), toolResultSha256=sha256(result_path))
    if job.get("toolResultId") is not None:
        result_evidence["toolResultId"] = job["toolResultId"]
    output = safe_output(tile / "native" / (cell + ".png"))
    record_path = safe_output(str(output) + ".generation.json")
    prompt_path = safe_output(tile / "native" / (cell + ".prompt.txt"))
    for path in (output, record_path, prompt_path):
        if path.exists():
            raise FileExistsError(f"Will not overwrite native pixels or their evidence: {path}")
    atomic_write(output, lambda temp: shutil.copyfile(source, temp))
    if sha256(output) != source_sha:
        raise ValueError("Copied native image checksum mismatch")
    atomic_write(prompt_path, lambda temp: temp.write_text(prompt, encoding="utf-8"))
    record = {
        "schemaVersion": 1, "file": str(output), "sha256": source_sha,
        "generatedAt": job["generatedAt"], "ingestedAt": now(),
        "width": native.width, "height": native.height, "format": "PNG", "mode": native.mode,
        "cell": cell, "tool": "image_gen.imagegen", "route": "builtin",
        "configSnapshot": snapshot, "submittedParameters": submitted,
        "actualModel": None, "actualQuality": None,
        "unverifiedReason": UNKNOWN, "evidence": result_evidence,
        "prompt": str(prompt_path), "promptSha256": sha256(prompt_path),
        "references": references, "sourceJob": str(job_file), "sourceJobSha256": sha256(job_file),
        "geometry": {"nativePixels": [NATIVE, NATIVE], "coreBox": [HALO, HALO, HALO + CORE, HALO + CORE],
                     "haloPixels": HALO, "neighborOverlapPixels": HALO * 2},
        "status": "unreviewed_native_candidate", "formalAccepted": False,
    }
    write_json(record_path, record)
    return {"image": str(output), "generationRecord": str(record_path), "sha256": source_sha}


def assemble(tile_dir):
    tile = safe_output(tile_dir)
    sources, mappings, mode = [], [], None
    native_images = []
    seen_sha = set()
    for row in range(GRID):
        for col in range(GRID):
            cell = f"r{row + 1:02d}_c{col + 1:02d}"
            file = safe_output(tile / "native" / (cell + ".png"))
            record_path = Path(str(file) + ".generation.json")
            record = read_json(record_path)
            digest = sha256(file)
            if digest != record["sha256"] or (record["width"], record["height"]) != (NATIVE, NATIVE):
                raise ValueError(f"Native evidence mismatch: {file}")
            if Path(record["file"]).resolve() != file or record.get("cell") != cell:
                raise ValueError(f"Native identity mismatch: {record_path}")
            if digest in seen_sha:
                raise ValueError(f"Duplicate native source bytes would repeat map content: {cell}")
            seen_sha.add(digest)
            image = load_image(file, (NATIVE, NATIVE))
            mode = mode or image.mode
            if image.mode != mode:
                raise ValueError("All native sources must have identical color mode; no silent conversion")
            native_images.append((row, col, image))
            sources.append({"cell": cell, "file": str(file), "sha256": digest,
                            "generationRecord": str(record_path), "generationRecordSha256": sha256(record_path),
                            "nativePixels": [NATIVE, NATIVE]})
            source_box = [0 if col == 0 else HALO, 0 if row == 0 else HALO,
                          NATIVE if col == GRID - 1 else HALO + CORE,
                          NATIVE if row == GRID - 1 else HALO + CORE]
            destination = [0 if col == 0 else HALO + col * CORE,
                           0 if row == 0 else HALO + row * CORE]
            mappings.append({"cell": cell, "sourceBox": source_box, "extendedDestinationXY": destination,
                             "coreSourceBox": [HALO, HALO, HALO + CORE, HALO + CORE],
                             "coreDestinationXY": [col * CORE, row * CORE]})
    extended = Image.new(mode, (EXTENDED, EXTENDED))
    for (_, _, image), mapping in zip(native_images, mappings):
        extended.paste(image.crop(tuple(mapping["sourceBox"])), tuple(mapping["extendedDestinationXY"]))
    core = extended.crop((HALO, HALO, HALO + TILE, HALO + TILE))
    candidate = safe_output(tile / "candidate")
    extended_info = save_image(candidate / "extended4326.png", extended)
    core_info = save_image(candidate / "core4096.png", core)
    preview_info = save_image(candidate / "preview1024.png", core.resize((1024, 1024), Image.Resampling.LANCZOS))
    for info in (extended_info, core_info):
        info.update(pixelScale="1 source pixel : 1 output pixel", resampling="none",
                    operation="integer crop and paste; hard core boundaries; no feather, registration or color correction")
    preview_info.update(operation="LANCZOS downsample of core4096 for overview only", productionPixels=False,
                        derivedFrom=[core_info], resampling="LANCZOS", pixelScale="4 core pixels per preview pixel")
    manifest = {
        "schemaVersion": 1, "createdAt": now(), "appearance": "lanxian_day",
        "tileDirectory": str(tile), "status": "candidate_pending_visual_review", "formalAccepted": False,
        "wholeCityComplete": False, "clientValidated": False,
        "geometry": {"grid": [GRID, GRID], "native": [NATIVE, NATIVE], "coreStep": CORE,
                     "halo": HALO, "overlap": HALO * 2, "tilePixels": [TILE, TILE],
                     "extendedPixels": [EXTENDED, EXTENDED], "coreInExtended": [HALO, HALO, HALO + TILE, HALO + TILE]},
        "derivedFrom": sources, "pixelMappings": mappings,
        "noResampling": True, "scopeOfNoResampling": "extended4326 and core4096 only; preview is downsampled",
        "outputs": {"extended": extended_info, "core": core_info, "preview": preview_info},
        "qa": {"visualInspectionPerformed": False, "seamApproval": False,
               "note": "Hard-cut assembly is a candidate, not evidence of geometric or tonal seam continuity."},
    }
    write_json(candidate / "assembly.manifest.json", manifest)
    return manifest


def candidate_core(tile_dir):
    tile = safe_output(tile_dir)
    manifest_path = safe_output(tile / "candidate" / "assembly.manifest.json")
    manifest = read_json(manifest_path)
    path = safe_output(tile / "candidate" / "core4096.png")
    digest = sha256(path)
    if digest != manifest["outputs"]["core"]["sha256"]:
        raise ValueError("Candidate pixels differ from assembly manifest; reassemble before QA")
    image = load_image(path, (TILE, TILE))
    source = {"file": str(path), "sha256": digest,
              "assemblyManifest": str(manifest_path), "assemblyManifestSha256": sha256(manifest_path)}
    return tile, image, source


def qa(tile_dir, westFile=None):
    tile, core, source = candidate_core(tile_dir)
    qa_dir = safe_output(tile / "qa")
    checks = []

    def crop(name, kind, box, **extra):
        entry = save_image(qa_dir / (name + ".png"), core.crop(box))
        entry.update(kind=kind, sourceBox=list(box), derivedFrom=[source],
                     operation="integer crop", resampling="none", visualInspectionPerformed=False,
                     reviewStatus="pending", **extra)
        checks.append(entry)

    for seam in range(1, GRID):
        coordinate = seam * CORE
        for part in range(GRID):
            start = part * CORE
            crop(f"internal_vertical_{seam}_part{part + 1}", "internal_vertical_seam",
                 (coordinate - 128, start, coordinate + 128, start + CORE), seamCoordinate=coordinate)
            crop(f"internal_horizontal_{seam}_part{part + 1}", "internal_horizontal_seam",
                 (start, coordinate - 128, start + CORE, coordinate + 128), seamCoordinate=coordinate)
    for row in range(1, GRID):
        for col in range(1, GRID):
            x, y = col * CORE, row * CORE
            crop(f"intersection_r{row}_c{col}", "four_cell_intersection", (x - 256, y - 256, x + 256, y + 256))
    for name, box in {"nw": (0, 0, 512, 512), "ne": (TILE - 512, 0, TILE, 512),
                      "sw": (0, TILE - 512, 512, TILE), "se": (TILE - 512, TILE - 512, TILE, TILE)}.items():
        crop("corner_" + name, "outer_corner", box)
    for part in range(GRID):
        start = part * CORE
        for edge, box in {
            "north": (start, 0, start + CORE, 256), "south": (start, TILE - 256, start + CORE, TILE),
            "west": (0, start, 256, start + CORE), "east": (TILE - 256, start, TILE, start + CORE),
        }.items():
            crop(f"edge_{edge}_part{part + 1}", "outer_edge", box, edge=edge)
    rgb = np.asarray(core)[..., :3].astype(np.int16)
    differences = []
    for seam in range(1, GRID):
        coordinate = seam * CORE
        for axis, delta in (("vertical", rgb[:, coordinate] - rgb[:, coordinate - 1]),
                            ("horizontal", rgb[coordinate] - rgb[coordinate - 1])):
            absolute = np.abs(delta)
            differences.append({"axis": axis, "coordinate": coordinate,
                                "meanAbsoluteRGBDifference": float(absolute.mean()),
                                "p95AbsoluteChannelDifference": float(np.percentile(absolute, 95)),
                                "interpretation": "Diagnostic only; no pass/fail threshold or visual approval."})
    report = {"schemaVersion": 1, "createdAt": now(), "source": source, "status": "awaiting_visual_inspection",
              "formalAccepted": False, "visualInspectionPerformed": False, "noResampling": True,
              "coverageExported": {"fullLengthInternalVerticalSeams": 3, "fullLengthInternalHorizontalSeams": 3,
                                   "seamLength": TILE, "segmentsPerSeam": 4, "internalSeamCrops": 24,
                                   "fourCellIntersections": 9, "outerCorners": 4, "outerEdgeCrops": 16,
                                   "totalNativeCrops": len(checks)},
              "checks": checks, "boundaryStatistics": differences,
              "limitations": "Exports are evidence for manual review only. Outer edge crops alone do not verify adjacent-tile continuity."}
    write_json(qa_dir / "qa.manifest.json", report)
    if westFile is not None:
        report["westExternalQa"] = external_west(tile, westFile)
    return report


def external_west(tile_dir, westFile):
    tile, core, own_source = candidate_core(tile_dir)
    west_path = Path(westFile).resolve(strict=True)
    west = load_image(west_path, (TILE, TILE))
    if west.mode != core.mode:
        raise ValueError("Neighbor and candidate color modes must match")
    west_source = {"file": str(west_path), "sha256": sha256(west_path), "role": "west adjacent core4096"}
    seam = Image.new(core.mode, (512, TILE))
    seam.paste(west.crop((TILE - 256, 0, TILE, TILE)), (0, 0))
    seam.paste(core.crop((0, 0, 256, TILE)), (256, 0))
    checks = []
    for part in range(GRID):
        y = part * CORE
        check = save_image(safe_output(tile / "qa" / f"external_west_part{part + 1}.png"),
                           seam.crop((0, y, 512, y + CORE)))
        check.update(derivedFrom=[west_source, own_source],
                     pixelMappings=[{"source": west_source["file"], "sourceBox": [TILE - 256, y, TILE, y + CORE],
                                     "destinationXY": [0, 0]},
                                    {"source": own_source["file"], "sourceBox": [0, y, 256, y + CORE],
                                     "destinationXY": [256, 0]}],
                     resampling="none", operation="integer crop and paste", reviewStatus="pending",
                     visualInspectionPerformed=False)
        checks.append(check)
    report = {"schemaVersion": 1, "createdAt": now(), "edge": "west", "source": own_source,
              "neighbor": west_source, "fullLength": TILE, "stripWidth": 512, "seamXInCrop": 256,
              "formalAccepted": False, "visualInspectionPerformed": False, "noResampling": True,
              "status": "awaiting_visual_inspection", "checks": checks}
    write_json(safe_output(tile / "qa" / "external-west.manifest.json"), report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ingest").add_argument("job_json")
    commands.add_parser("assemble").add_argument("tile_dir")
    qa_parser = commands.add_parser("qa")
    qa_parser.add_argument("tile_dir")
    qa_parser.add_argument("--west")
    west_parser = commands.add_parser("external-west")
    west_parser.add_argument("tile_dir")
    west_parser.add_argument("west_file")
    args = parser.parse_args()
    if args.command == "ingest":
        result = ingest(args.job_json)
    elif args.command == "assemble":
        result = assemble(args.tile_dir)
    elif args.command == "qa":
        result = qa(args.tile_dir, args.west)
    else:
        result = external_west(args.tile_dir, args.west_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"workflow error: {error}", file=sys.stderr)
        sys.exit(1)
