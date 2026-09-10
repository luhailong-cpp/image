#!/usr/bin/env python3
"""Deterministically process ImageGen art; never synthesize animation poses.

Requires Pillow and numpy and the installed generate2dsprite skill processor.
Only processes the specified character directory. Raw files stay in their cache.
"""
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

VERSION = 1
CELL = 512
FOOT = (256, 471)
ROWS = {"cardinal": ["S", "W", "E", "N"], "diagonal": ["SW", "NW", "NE", "SE"]}
DIRECTIONS = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]
DEFAULT_PROCESSOR = Path.home() / ".agents/skills/generate2dsprite/scripts/generate2dsprite.py"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bounds(image: Image.Image, threshold: int = 8):
    yy, xx = np.nonzero(np.asarray(image.getchannel("A")) > threshold)
    if not len(xx):
        return None
    return [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]


def foot_anchor(image: Image.Image) -> tuple[float, int]:
    """Grounded contact = lowest visible row; X uses the lower body median.

    This is an automatic feet estimate, not a semantic skeleton detector.
    The source is required to contain no detached ground effects or shadow.
    """
    yy, xx = np.nonzero(np.asarray(image.getchannel("A")) > 8)
    if not len(xx):
        raise ValueError("empty frame")
    cutoff = np.percentile(yy, 90)
    return float(np.median(xx[yy >= cutoff])), int(yy.max())


def prompt_path(args, kind: str) -> Path | None:
    explicit = getattr(args, f"{kind}_prompt")
    candidates = [explicit] if explicit else []
    candidates += [args.character_dir / "prompts" / f"{kind}.txt",
                   args.character_dir / f"{kind}-prompt.txt",
                   args.character_dir / f"prompt-{kind}.txt"]
    return next((p for p in candidates if p and p.is_file()), None)


def run_processor(args, kind: str, raw: Path, work: Path) -> tuple[dict, dict]:
    work.mkdir(parents=True, exist_ok=True)
    native = Image.open(raw)
    source = {"path": str(raw.resolve()), "sha256": sha(raw), "native_size": list(native.size),
              "native_mode": native.mode, "source": "built-in image_gen"}
    if kind != "portrait" and (native.width % 4 or native.height % 4 or native.width != native.height):
        raise ValueError(f"{kind}: expected square 4x4 raw sheet divisible by 4; got {native.size}")
    prompt = prompt_path(args, kind)
    if prompt:
        source["prompt_file"] = str(prompt.resolve())
        source["prompt_sha256"] = sha(prompt)
    else:
        source["prompt_file"] = None
        source["prompt_status"] = "not supplied; preserve the original generation prompt separately"
    command = [sys.executable, str(args.processor), "process", "--input", str(raw),
               "--target", "player", "--mode", "single" if kind == "portrait" else "walk",
               "--output-dir", str(work), "--duration", str(args.duration)]
    if prompt:
        command += ["--prompt-file", str(prompt)]
    if kind == "portrait":
        command += ["--single-size", "1024"]
    else:
        command += ["--rows", "4", "--cols", "4", "--cell-size", str(CELL),
                    "--fit-scale", "0.84", "--align", "feet", "--scale-strategy", "preserve",
                    "--shared-scale", "--component-mode", "largest", "--component-padding", "2",
                    "--trim-border", "0", "--edge-clean-depth", "0", "--strict-qc"]
    cache = {"version": VERSION, "source_sha256": source["sha256"],
             "processor_sha256": sha(args.processor), "command": command,
             "prompt_sha256": source.get("prompt_sha256")}
    cache_path = work / "processor-cache.json"
    cache_match = cache_path.exists() and json.loads(cache_path.read_text(encoding="utf-8")) == cache
    if not cache_match:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (work / "processor.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise ValueError(f"{kind}: skill processor strict QC failed; inspect {work / 'processor.log'}")
        write_json(cache_path, cache)
    metadata = json.loads((work / "pipeline-meta.json").read_text(encoding="utf-8"))
    metadata["invocation"] = command
    metadata["processor_sha256"] = cache["processor_sha256"]
    return metadata, source


def normalized_frame(image: Image.Image, common_scale: float) -> tuple[Image.Image, dict]:
    bbox = image.getbbox()
    if bbox is None:
        raise ValueError("empty processed frame")
    cropped = image.crop(bbox)
    resized_size = (max(1, round(cropped.width * common_scale)), max(1, round(cropped.height * common_scale)))
    scaled = cropped.resize(resized_size, Image.Resampling.LANCZOS)
    ax, ay = foot_anchor(scaled)
    px, py = round(FOOT[0] - ax), FOOT[1] - ay
    # Check full nonzero-alpha image, including antialiased edge pixels.
    if px < 1 or py < 1 or px + scaled.width >= CELL or py + scaled.height >= CELL:
        raise ValueError(f"shared scale would crop/edge-touch a frame: {px, py, *scaled.size}")
    output = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    output.paste(scaled, (px, py))
    output_bbox = bounds(output)
    final_anchor = foot_anchor(output)
    rgba = np.asarray(output)
    magenta = ((rgba[:, :, 0] > 180) & (rgba[:, :, 1] < 90) &
               (rgba[:, :, 2] > 180) & (rgba[:, :, 3] > 32))
    info = {"bbox_alpha_gt_8": output_bbox, "foot_anchor_px": list(final_anchor),
            "foot_from_bottom": CELL - 1 - final_anchor[1], "shared_scale": common_scale,
            "resized_crop_size": list(resized_size), "paste_xy": [px, py],
            "source_crop_bbox": list(bbox), "output_edge_touch": False, "paste_clamped": False,
            "magenta_like_pixels": int(magenta.sum()),
            "rgba_sha256": hashlib.sha256(output.tobytes()).hexdigest()}
    return output, info


def compose(frames: list[Image.Image], cols: int) -> Image.Image:
    result = Image.new("RGBA", (cols * CELL, math.ceil(len(frames) / cols) * CELL), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        result.paste(frame, ((i % cols) * CELL, (i // cols) * CELL))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character-dir", required=True, type=Path)
    for kind in ["portrait", "cardinal", "diagonal"]:
        parser.add_argument(f"--{kind}", required=True, type=Path)
        parser.add_argument(f"--{kind}-prompt", type=Path)
    parser.add_argument("--processor", type=Path, default=DEFAULT_PROCESSOR)
    parser.add_argument("--tmp-root", type=Path, default=Path("E:/work/tmp/qdao-roster-v11"))
    parser.add_argument("--duration", type=int, default=125, help="GIF frame milliseconds (default 8 fps)")
    parser.add_argument("--target-height", type=int, default=420, help="shared maximum silhouette height, not per-frame fit")
    parser.add_argument("--force", action="store_true", help="re-run processor even if raw and settings are unchanged")
    args = parser.parse_args()
    if not args.processor.is_file():
        parser.error(f"skill processor not found: {args.processor}")
    if not 100 <= args.target_height <= 450:
        parser.error("--target-height must be between 100 and 450")
    args.character_dir = args.character_dir.resolve()
    args.character_dir.mkdir(parents=True, exist_ok=True)
    work = args.tmp_root / args.character_dir.name
    record_dir = args.character_dir / "processing"
    record_dir.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("sprite_processor", args.processor)
    processor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(processor)
    qc = {"version": VERSION, "status": "processing", "errors": [], "directions": {},
          "gates": {"body_scale_cv_max": 0.08, "source_anchor_y_std_max": 0.05,
                    "cross_direction_mean_height_ratio_max": 1.10,
                    "exact_duplicate_frames_allowed": 0, "foot_target_px": list(FOOT)},
          "visual_review": "required: verify character identity, direction, gait, complete limbs, and key edges"}
    sources, metadata, pre_frames = {}, {}, {}
    try:
        for kind in ["portrait", "cardinal", "diagonal"]:
            print(f"Processing {args.character_dir.name}/{kind}...", flush=True)
            cache = work / kind / "processor-cache.json"
            if args.force and cache.exists():
                cache.unlink()
            meta, source = run_processor(args, kind, getattr(args, kind), work / kind)
            sources[kind], metadata[kind] = source, meta
            write_json(record_dir / f"{kind}-pipeline-meta.json", meta)
            prompt = prompt_path(args, kind)
            if prompt:
                shutil.copyfile(prompt, record_dir / f"{kind}-prompt-used.txt")
            if kind != "portrait":
                for row, direction in enumerate(ROWS[kind]):
                    pre_frames[direction] = [Image.open(work / kind / f"walk-{row * 4 + col + 1}.png").convert("RGBA")
                                             for col in range(4)]
                    direction_qc = processor.summarize_frame_qc(meta["frames"][row * 4:row * 4 + 4])
                    qc["directions"][direction] = direction_qc
                    for metric, limit in [("body_scale_cv", 0.08), ("anchor_y_std", 0.05)]:
                        if direction_qc[metric] > limit:
                            qc["errors"].append(f"{direction}: {metric}={direction_qc[metric]:.5f} > {limit}")
        all_pre = [frame for d in DIRECTIONS for frame in pre_frames[d]]
        max_height = max(bounds(frame)[3] - bounds(frame)[1] for frame in all_pre)
        common_scale = args.target_height / max_height
        # One safety scale chosen for the whole bundle, never an individual frame.
        for frame in all_pre:
            box = frame.getbbox()
            cropped = frame.crop(box)
            ax, ay = foot_anchor(cropped)
            common_scale = min(common_scale, (FOOT[0] - 4) / max(ax, 1),
                               (CELL - FOOT[0] - 4) / max(cropped.width - ax, 1),
                               (FOOT[1] - 4) / max(ay, 1),
                               (CELL - FOOT[1] - 4) / max(cropped.height - ay, 1))
        qc["shared_final_scale"] = common_scale
        qc["pre_max_subject_height"] = max_height
        qc["requested_max_subject_height"] = args.target_height
        output_frames, frame_records = {}, {}
        for direction in DIRECTIONS:
            pairs = [normalized_frame(frame, common_scale) for frame in pre_frames[direction]]
            output_frames[direction] = [p[0] for p in pairs]
            frame_records[direction] = [p[1] for p in pairs]
            heights = [r["bbox_alpha_gt_8"][3] - r["bbox_alpha_gt_8"][1] for r in frame_records[direction]]
            unique = len({r["rgba_sha256"] for r in frame_records[direction]})
            qc["directions"][direction].update({"output_subject_heights": heights,
                "output_subject_height_mean": float(np.mean(heights)), "unique_frames": unique,
                "output_foot_y_std": float(np.std([r["foot_anchor_px"][1] for r in frame_records[direction]]))})
            if unique != 4:
                qc["errors"].append(f"{direction}: only {unique}/4 unique RGBA frames")
        means = [qc["directions"][d]["output_subject_height_mean"] for d in DIRECTIONS]
        ratio = max(means) / min(means)
        qc["cross_direction_mean_height_ratio"] = ratio
        if ratio > 1.10:
            qc["errors"].append(f"cross-direction mean-height ratio {ratio:.5f} > 1.10; regenerate scale-mismatched source")
        write_json(record_dir / "frame-transforms.json", frame_records)
        profile = {"version": VERSION, "strategy": "preserve then one global scale, per-frame translation only",
                   "cell_size": [CELL, CELL], "output_foot_px": list(FOOT),
                   "processor_preserve_fit_scale": 0.84, "final_common_scale": common_scale,
                   "native_sheet_sizes": {k: sources[k]["native_size"] for k in ROWS},
                   "source_normalization": "same 512-square raw-cell normalization; isotropic, no independent frame fitting",
                   "mirrored_frames": False, "synthetic_or_repeated_frames": False,
                   "expected_frames_per_direction": 4}
        write_json(record_dir / "scale-profile.json", profile)
        qc["status"] = "failed" if qc["errors"] else "passed_numeric_qc_pending_visual_review"
        write_json(args.character_dir / "qc.json", qc)
        write_json(record_dir / "sources.json", sources)
        if qc["errors"]:
            diagnostic_dir = work / "qc-review"
            diagnostic_dir.mkdir(parents=True, exist_ok=True)
            compose([f for d in DIRECTIONS for f in output_frames[d]], 4).save(diagnostic_dir / "rejected-contact-sheet.png")
            raise ValueError("; ".join(qc["errors"]) + f"; diagnostic: {diagnostic_dir}")
        shutil.copyfile(work / "portrait" / "clean.png", args.character_dir / "portrait.png")
        for direction in DIRECTIONS:
            frame_dir = args.character_dir / "walk" / direction
            frame_dir.mkdir(parents=True, exist_ok=True)
            for i, frame in enumerate(output_frames[direction], 1):
                frame.save(frame_dir / f"{i:02d}.png")
            compose(output_frames[direction], 4).save(frame_dir / "strip.png")
            processor.save_transparent_gif(output_frames[direction], frame_dir / "walk.gif", args.duration)
        for kind, directions in ROWS.items():
            compose([f for d in directions for f in output_frames[d]], 4).save(args.character_dir / f"walk-{kind}.png")
        artifacts = [args.character_dir / "portrait.png"]
        artifacts += [args.character_dir / f"walk-{kind}.png" for kind in ROWS]
        artifacts += [p for d in DIRECTIONS for p in sorted((args.character_dir / "walk" / d).iterdir()) if p.suffix in {".png", ".gif"}]
        manifest = {"version": VERSION, "character_id": args.character_dir.name,
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "art_source": "built-in image_gen", "portrait": "portrait.png", "portrait_size": [1024, 1024],
                    "walk": {"directions": DIRECTIONS, "frames_per_direction": 4, "cell": [CELL, CELL],
                             "strip_size": [2048, 512], "frame_duration_ms": args.duration,
                             "fps": 1000 / args.duration, "feet_px_from_top_left": list(FOOT),
                             "row_order_cardinal": ROWS["cardinal"], "row_order_diagonal": ROWS["diagonal"],
                             "frame_pattern": "walk/{direction}/{01,02,03,04}.png",
                             "strip_pattern": "walk/{direction}/strip.png", "gif_pattern": "walk/{direction}/walk.gif"},
                    "qc": "qc.json", "client_integration": "not performed; these are authentic 4-frame image assets",
                    "sources": sources, "processing": "processing/scale-profile.json",
                    "files": [{"path": p.relative_to(args.character_dir).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in artifacts]}
        write_json(args.character_dir / "manifest.json", manifest)
        print(json.dumps({"character": args.character_dir.name, "status": qc["status"], "frames": 32,
                          "cross_direction_height_ratio": ratio, "manifest": str(args.character_dir / "manifest.json")}, ensure_ascii=False))
        return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        qc["status"] = "failed"
        if str(exc) not in qc["errors"]:
            qc["errors"].append(str(exc))
        write_json(args.character_dir / "qc.json", qc)
        write_json(record_dir / "sources.json", sources)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
