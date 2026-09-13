#!/usr/bin/env python3
"""Split authored ImageGen poses and align them; never invent motion or redraw art."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

VERSION = 12
CELL = 512
FOOT = (256, 471)
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
SHEETS = {"s_e": ("S", "E"), "n_w": ("N", "W"),
          "ne_sw": ("NE", "SW"), "nw_se": ("NW", "SE")}
APPROVED = ("23_lantern_courier", "24_lu_dongbin", "25_lion_drum_guard",
            "26_osmanthus_healer", "27_ink_kite_ranger", "28_moon_rabbit_artificer",
            "29_he_xiangu", "30_han_xiangzi")
DEFAULT_PROCESSOR = Path.home() / ".agents/skills/generate2dsprite/scripts/generate2dsprite.py"
V11 = Path(__file__).resolve().parent.parent / "qdao_chibi_roster_v11"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bounds(image, threshold=8):
    yy, xx = np.nonzero(np.asarray(image.getchannel("A")) > threshold)
    if not len(xx):
        return None
    return [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]


def foot_anchor(image):
    yy, xx = np.nonzero(np.asarray(image.getchannel("A")) > 8)
    if not len(xx):
        raise ValueError("empty frame")
    return float(np.median(xx[yy >= np.percentile(yy, 90)])), int(yy.max())


def load_processor(path):
    spec = importlib.util.spec_from_file_location("sprite_processor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compose(frames, cols):
    out = Image.new("RGBA", (cols * CELL, math.ceil(len(frames) / cols) * CELL))
    for i, frame in enumerate(frames):
        out.paste(frame, (i % cols * CELL, i // cols * CELL))
    return out


def run_sheet(raw, kind, work, processor_path=DEFAULT_PROCESSOR, padding=2, prompt=None, force=False, rows=None, cols=None):
    """Use the skill primitive, then apply strict gates per coherent direction.

    Different facings have different silhouettes, so body-area CV is measured
    within each eight-pose gait, not between a front view and a side view.
    Every frame still has unconditional structural/containment gates.
    """
    raw, work = Path(raw).resolve(), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    single_direction = kind.upper() in DIRECTIONS
    default_cols, default_rows = (2, 4) if single_direction else (4, 2 if kind == "idle" else 4)
    cols, rows = cols or default_cols, rows or default_rows
    if rows * cols != (8 if single_direction or kind == "idle" else 16):
        raise ValueError(f"{kind}: wrong cell count for the authored action contract")
    with Image.open(raw) as native:
        size, mode = native.size, native.mode
    cw, ch = size[0] // cols, size[1] // rows
    if cw < 64 or ch < 64 or max(cw, ch) / min(cw, ch) > 1.03:
        raise ValueError(f"{kind}: needs {cols} columns x {rows} rows of nearly square cells; got {size}")
    source = {"path": str(raw), "sha256": sha(raw), "native_size": list(size), "native_mode": mode,
              "source": "built-in image_gen", "grid": [cols, rows], "native_cell_size": [cw, ch],
              "unused_outer_remainder_px": [size[0] % cols, size[1] % rows]}
    assembly_path = raw.with_suffix(".assembly.json")
    if assembly_path.is_file():
        provenance = json.loads(assembly_path.read_text(encoding="utf-8"))
        if provenance.get("output_sha256") != source["sha256"]:
            raise ValueError(f"{kind}: assembly provenance does not match input pixels")
        source.update(source="built-in image_gen, followed by deterministic grid rearrangement",
                      assembly_provenance=provenance, assembly_metadata_sha256=sha(assembly_path))
    command = [sys.executable, "-X", "utf8", "-B", str(processor_path), "process", "--input", str(raw),
               "--target", "player", "--mode", "idle" if kind == "idle" else "walk", "--output-dir", str(work),
               "--rows", str(rows), "--cols", str(cols), "--cell-size", str(CELL), "--fit-scale", "0.84",
               "--align", "feet", "--scale-strategy", "preserve", "--shared-scale", "--component-mode", "largest",
               "--component-padding", str(padding), "--trim-border", "0", "--edge-clean-depth", "0", "--duration", "60"]
    if prompt and Path(prompt).is_file():
        command += ["--prompt-file", str(prompt)]
        source.update(prompt_file=str(Path(prompt).resolve()), prompt_sha256=sha(prompt))
    cache = {"pipeline_version": VERSION, "source_sha256": source["sha256"],
             "processor_sha256": sha(processor_path), "command": command}
    cache_path = work / "processor-cache.json"
    if force or not cache_path.exists() or json.loads(cache_path.read_text(encoding="utf-8")) != cache:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (work / "processor.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise ValueError(f"{kind}: skill processor failed; inspect {work / 'processor.log'}")
        write_json(cache_path, cache)
    meta = json.loads((work / "pipeline-meta.json").read_text(encoding="utf-8"))
    meta.update(invocation=command, processor_sha256=cache["processor_sha256"],
                strict_gate_scope="structural per frame; body CV and source anchor variance per direction")
    errors = []
    if len(meta["frames"]) != cols * rows:
        raise ValueError(f"{kind}: processor did not return exact grid frame count")
    clean = Image.open(work / "raw-sheet-clean.png").convert("RGBA")
    used_w, used_h = cw * cols, ch * rows
    if used_w < clean.width and bounds(clean.crop((used_w, 0, clean.width, clean.height))):
        errors.append("visible subject pixels in unused outer column remainder")
    if used_h < clean.height and bounds(clean.crop((0, used_h, clean.width, clean.height))):
        errors.append("visible subject pixels in unused outer row remainder")
    frames = []
    for info in meta["frames"]:
        for gate in ("is_empty", "source_edge_touch", "output_edge_touch", "paste_clamped"):
            if info.get(gate):
                errors.append(f"{info['grid']}: {gate}")
        if not info.get("crop_bbox"):
            frames.append(Image.new("RGBA", (CELL, CELL)))
            continue
        # Preserve existing antialias alpha; masked paste would square it.
        crop = clean.crop(info["source_box"]).crop(info["crop_bbox"])
        scaled = crop.resize(tuple(info["output_size"]), Image.Resampling.LANCZOS)
        frame = Image.new("RGBA", (CELL, CELL))
        frame.paste(scaled, tuple(info["paste_position"]))
        frames.append(frame)
    processor = load_processor(processor_path)
    metrics = {}
    if kind != "idle":
        direction_order = (kind.upper(),) if single_direction else SHEETS[kind]
        for index, direction in enumerate(direction_order):
            qc = processor.summarize_frame_qc(meta["frames"][index * 8:index * 8 + 8])
            metrics[direction] = qc
            for gate, limit in (("body_scale_cv", 0.08), ("anchor_y_std", 0.05)):
                if qc[gate] > limit:
                    errors.append(f"{direction}: {gate}={qc[gate]:.5f} > {limit}")
    meta["alpha_composition_override"] = "unmasked RGBA paste, no alpha squaring"
    meta["direction_qc"] = metrics
    meta["strict_qc_errors"] = errors
    write_json(work / "v12-sheet-qc.json", {"status": "failed" if errors else "passed_numeric_pending_visual", "errors": errors, "metrics": metrics})
    return frames, meta, source, errors


def normalize(image, scale):
    box = image.getbbox()
    if box is None:
        raise ValueError("empty preprocessed frame")
    crop = image.crop(box)
    scaled = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.Resampling.LANCZOS)
    ax, ay = foot_anchor(scaled)
    px, py = round(FOOT[0] - ax), FOOT[1] - ay
    if px < 1 or py < 1 or px + scaled.width >= CELL or py + scaled.height >= CELL:
        raise ValueError(f"shared scale would clip/touch output edge: {px, py, *scaled.size}")
    result = Image.new("RGBA", (CELL, CELL))
    result.paste(scaled, (px, py))
    return result, {"source_crop_bbox": list(box), "shared_scale": scale, "paste_xy": [px, py],
                    "resized_crop_size": list(scaled.size), "bbox_alpha_gt_8": bounds(result),
                    "foot_anchor_px": list(foot_anchor(result)), "output_edge_touch": False, "paste_clamped": False,
                    "rgba_sha256": hashlib.sha256(result.tobytes()).hexdigest()}


def prepare_portrait(args, root):
    """Preserve the V11 portrait, or deterministically clean an explicit replacement."""
    raw = getattr(args, "portrait_raw", None)
    if raw:
        raw = raw.resolve()
        folder = root / "processing" / "portrait"
        folder.mkdir(parents=True, exist_ok=True)
        with Image.open(raw) as image:
            native_size, native_mode = list(image.size), image.mode
        command = [sys.executable, "-X", "utf8", "-B", str(args.processor), "process", "--input", str(raw),
                   "--target", "player", "--mode", "single", "--single-size", "1024", "--output-dir", str(folder)]
        prompt = root / "prompts" / "portrait.txt"
        if prompt.is_file():
            command += ["--prompt-file", str(prompt)]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (folder / "processor.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise ValueError(f"Replacement portrait cleanup failed: {folder / 'processor.log'}")
        portrait = folder / "clean.png"
        source = {"mode": "replacement", "path": str(raw), "source": "built-in image_gen",
                  "sha256": sha(raw), "native_size": native_size, "native_mode": native_mode,
                  "processing_invocation": command, "processor_sha256": sha(args.processor)}
    else:
        portrait = (args.portrait or V11 / root.name / "portrait.png").resolve()
        source = {"mode": "replacement" if args.portrait else "v11_unchanged", "path": str(portrait),
                  "sha256": sha(portrait), "source": "explicit processed replacement" if args.portrait else "accepted V11 portrait"}
        with Image.open(portrait) as image:
            source.update(native_size=list(image.size), native_mode=image.mode)
    with Image.open(portrait) as image:
        if image.mode != "RGBA" or image.size != (1024, 1024):
            raise ValueError("Portrait export must be a 1024 square RGBA image")
        if image.getchannel("A").getextrema() != (0, 255):
            raise ValueError("Portrait requires transparent background and visible opaque artwork")
    source["export_sha256"] = sha(portrait)
    source["baseline_v11_sha256"] = sha(V11 / root.name / "portrait.png")
    write_json(root / "processing" / "portrait-source.json", source)
    return portrait, source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character-dir", required=True, type=Path)
    for kind in (*SHEETS, "idle"):
        parser.add_argument("--" + kind.replace("_", "-"), required=True, type=Path)
    portrait_options = parser.add_mutually_exclusive_group()
    portrait_options.add_argument("--portrait", type=Path, help="Explicit processed 1024x1024 RGBA replacement; otherwise preserve V11.")
    portrait_options.add_argument("--portrait-raw", type=Path, help="Newly generated solid-magenta portrait to clean with the image skill.")
    parser.add_argument("--processor", type=Path, default=DEFAULT_PROCESSOR)
    parser.add_argument("--target-height", type=int, default=420)
    parser.add_argument("--component-padding", type=int, choices=range(9), default=2)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.character_dir.resolve()
    if root.name not in APPROVED:
        parser.error("Only the eight accepted character IDs are allowed; the rejected elder is excluded.")
    if not 100 <= args.target_height <= 450:
        parser.error("Target silhouette height must be 100..450.")
    root.mkdir(parents=True, exist_ok=True)
    work = root / "processing"
    qc = {"version": VERSION, "status": "processing", "errors": [], "visual_review": "required",
          "gates": {"body_scale_cv_max": 0.08, "source_anchor_y_std_max": 0.05,
                    "cross_direction_mean_height_ratio_max": 1.10, "idle_walk_height_drift_max": 0.08,
                    "foot_target_px": list(FOOT), "unique_frames_per_direction": 8}}
    sources, pre_walk, pre_idle, directions_qc = {}, {}, {}, {}
    try:
        for kind in (*SHEETS, "idle"):
            print(f"Processing {root.name}/{kind}...", flush=True)
            frames, meta, source, errors = run_sheet(getattr(args, kind), kind, work / kind, args.processor,
                                                    args.component_padding, root / "prompts" / f"{kind}.txt", args.force)
            sources[kind] = source
            qc["errors"].extend(f"{kind}: {error}" for error in errors)
            write_json(work / f"{kind}-pipeline-meta.json", meta)
            if kind == "idle":
                pre_idle = dict(zip(DIRECTIONS, frames))
            else:
                for i, direction in enumerate(SHEETS[kind]):
                    pre_walk[direction] = frames[i * 8:i * 8 + 8]
                directions_qc.update(meta["direction_qc"])
        all_pre = [f for d in DIRECTIONS for f in pre_walk[d]] + [pre_idle[d] for d in DIRECTIONS]
        max_height = max(bounds(f)[3] - bounds(f)[1] for f in all_pre)
        scale = args.target_height / max_height
        for frame in all_pre:
            crop = frame.crop(frame.getbbox())
            ax, ay = foot_anchor(crop)
            scale = min(scale, (FOOT[0] - 4) / max(ax, 1), (CELL - FOOT[0] - 4) / max(crop.width - ax, 1),
                        (FOOT[1] - 4) / max(ay, 1), (CELL - FOOT[1] - 4) / max(crop.height - ay, 1))
        output_walk, output_idle, records = {}, {}, {"walk": {}, "idle": {}}
        means = []
        for direction in DIRECTIONS:
            pairs = [normalize(f, scale) for f in pre_walk[direction]]
            output_walk[direction] = [p[0] for p in pairs]
            records["walk"][direction] = [p[1] for p in pairs]
            output_idle[direction], records["idle"][direction] = normalize(pre_idle[direction], scale)
            heights = [r["bbox_alpha_gt_8"][3] - r["bbox_alpha_gt_8"][1] for r in records["walk"][direction]]
            mean = float(np.mean(heights))
            means.append(mean)
            unique = len({r["rgba_sha256"] for r in records["walk"][direction]})
            ib = records["idle"][direction]["bbox_alpha_gt_8"]
            idle_drift = abs((ib[3] - ib[1]) / mean - 1)
            directions_qc[direction].update(unique_frames=unique, output_subject_heights=heights,
                                            output_subject_height_mean=mean, idle_walk_height_drift=idle_drift)
            if unique != 8:
                qc["errors"].append(f"{direction}: only {unique}/8 distinct RGBA frames; cannot invent intermediates")
            if idle_drift > 0.08:
                qc["errors"].append(f"{direction}: idle/walk height drift {idle_drift:.5f} > .08")
            if records["idle"][direction]["rgba_sha256"] in {r["rgba_sha256"] for r in records["walk"][direction]}:
                qc["errors"].append(f"{direction}: idle is a copied walk frame, needs separately authored neutral pose")
        ratio = max(means) / min(means)
        if ratio > 1.10:
            qc["errors"].append(f"cross-direction mean-height ratio {ratio:.5f} > 1.10")
        qc.update(directions=directions_qc, shared_final_scale=scale, pre_max_subject_height=max_height,
                  cross_direction_mean_height_ratio=ratio,
                  status="failed" if qc["errors"] else "passed_numeric_qc_pending_visual_review")
        write_json(root / "qc.json", qc)
        write_json(work / "sources.json", sources)
        write_json(work / "frame-transforms.json", records)
        write_json(work / "scale-profile.json", {"version": VERSION, "cell_size": [CELL, CELL],
                   "output_foot_px": list(FOOT), "processor_preserve_fit_scale": 0.84, "final_common_scale": scale,
                   "strategy": "same normalized raw-cell scale for all 72 poses, then one common final scale; translation only per pose",
                   "source_to_output_scale_by_sheet": {kind: CELL / max(source["native_cell_size"]) * .84 * scale for kind, source in sources.items()},
                   "native_sheet_sizes": {k: s["native_size"] for k, s in sources.items()},
                   "per_frame_scale_normalization": False, "mirrored_frames": False, "synthetic_or_repeated_frames": False})
        compose([f for d in DIRECTIONS for f in output_walk[d]], 8).save(work / "walk-review.png")
        compose([output_idle[d] for d in DIRECTIONS], 4).save(work / "idle-review.png")
        if qc["errors"]:
            raise ValueError("; ".join(qc["errors"]))
        portrait, portrait_source = prepare_portrait(args, root)
        if portrait.resolve() != (root / "portrait.png").resolve():
            shutil.copyfile(portrait, root / "portrait.png")
        processor = load_processor(args.processor)
        (root / "idle").mkdir(exist_ok=True)
        for direction in DIRECTIONS:
            folder = root / "walk" / direction
            folder.mkdir(parents=True, exist_ok=True)
            for i, frame in enumerate(output_walk[direction], 1):
                frame.save(folder / f"{i:02d}.png")
            compose(output_walk[direction], 8).save(folder / "strip.png")
            processor.save_transparent_gif(output_walk[direction], folder / "walk.gif", 60)
            output_idle[direction].save(root / "idle" / f"{direction}.png")
        paths = [root / "portrait.png"] + [root / "idle" / f"{d}.png" for d in DIRECTIONS]
        paths += [root / "walk" / d / name for d in DIRECTIONS for name in [*(f"{i:02d}.png" for i in range(1, 9)), "strip.png", "walk.gif"]]
        write_json(root / "manifest.json", {"version": VERSION, "character_id": root.name,
                   "generated_at_utc": datetime.now(timezone.utc).isoformat(), "art_source": "built-in image_gen",
                   "portrait": "portrait.png", "portrait_size": [1024, 1024],
                   "portrait_mode": portrait_source["mode"], "portrait_source": portrait_source,
                   "portrait_v11_sha256": portrait_source["baseline_v11_sha256"],
                   "walk": {"directions": DIRECTIONS, "frames_per_direction": 8, "cell": [CELL, CELL],
                            "strip_size": [4096, 512], "frame_duration_ms": 60, "fps": 1000 / 60,
                            "feet_px_from_top_left": list(FOOT), "frame_pattern": "walk/{direction}/{01..08}.png",
                            "raw_sheet_direction_order": SHEETS},
                   "idle": {"directions": DIRECTIONS, "frames_per_direction": 1, "cell": [CELL, CELL],
                            "pattern": "idle/{direction}.png", "dedicated_neutral_pose": True},
                   "qc": "qc.json", "client_integration": "not yet performed", "sources": sources,
                   "files": [{"path": p.relative_to(root).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in paths]})
        print(json.dumps({"character": root.name, "status": qc["status"], "movement_frames": 64, "neutral_idle_frames": 8,
                          "media_count": len(paths), "scale": scale}, ensure_ascii=False))
        return 0
    except (ValueError, OSError) as error:
        qc["status"] = "failed"
        if str(error) not in qc["errors"]:
            qc["errors"].append(str(error))
        write_json(root / "qc.json", qc)
        write_json(work / "sources.json", sources)
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
