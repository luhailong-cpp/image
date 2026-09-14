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


def body_ground_anchor(image):
    """Horizontal upper-body axis plus ground height, independent of support foot.

    The eight approved chibi identities have a large stable head. Its upper
    42% silhouette provides a translation-covariant axis; using the lowest
    foot pixels instead moves the whole sprite when the support leg changes.
    This never changes pose pixels or applies individual-frame scaling.
    """
    yy, xx = np.nonzero(np.asarray(image.getchannel("A")) > 8)
    if not len(xx):
        raise ValueError("empty frame")
    head_end = int(yy.min() + (yy.max() - yy.min()) * 0.42)
    head_x = xx[yy < head_end]
    if not len(head_x):
        raise ValueError("missing upper-body axis")
    return float(np.median(head_x)), int(yy.max())


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


def run_sheet(raw, kind, work, processor_path=DEFAULT_PROCESSOR, padding=2, prompt=None, force=False, rows=None, cols=None, alignment_version=2):
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
        for gate in (("is_empty", "source_edge_touch") if alignment_version == 3 else
                     ("is_empty", "source_edge_touch", "output_edge_touch", "paste_clamped")):
            if info.get(gate):
                errors.append(f"{info['grid']}: {gate}")
        if not info.get("crop_bbox"):
            frames.append(Image.new("RGBA", (CELL, CELL)))
            continue
        # Preserve existing antialias alpha; masked paste would square it.
        crop = clean.crop(info["source_box"]).crop(info["crop_bbox"])
        scaled = crop.resize(tuple(info["output_size"]), Image.Resampling.LANCZOS)
        if alignment_version == 3:
            # The old processor's feet placement is discarded, including any
            # clamping it needed. Recover every cleaned source pixel instead.
            frames.append(scaled)
        else:
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
            for gate, limit in ((("body_scale_cv", 0.08),) if alignment_version == 3 else
                                (("body_scale_cv", 0.08), ("anchor_y_std", 0.05))):
                if qc[gate] > limit:
                    errors.append(f"{direction}: {gate}={qc[gate]:.5f} > {limit}")
    if alignment_version == 3:
        meta["alignment_v3_note"] = "legacy feet placement discarded; source foot variance recorded, not gated"
    meta["alpha_composition_override"] = "unmasked RGBA paste, no alpha squaring"
    meta["direction_qc"] = metrics
    meta["strict_qc_errors"] = errors
    write_json(work / "v12-sheet-qc.json", {"status": "failed" if errors else "passed_numeric_pending_visual", "errors": errors, "metrics": metrics})
    return frames, meta, source, errors


def normalize(image, scale, despill_edges=False, despill_radius=2):
    box = image.getbbox()
    if box is None:
        raise ValueError("empty preprocessed frame")
    crop = image.crop(box)
    scaled = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.Resampling.LANCZOS)
    ax, ay = body_ground_anchor(scaled)
    px, py = round(FOOT[0] - ax), FOOT[1] - ay
    if px < 1 or py < 1 or px + scaled.width >= CELL or py + scaled.height >= CELL:
        raise ValueError(f"shared scale would clip/touch output edge: {px, py, *scaled.size}")
    result = Image.new("RGBA", (CELL, CELL))
    result.paste(scaled, (px, py))
    cleanup = None
    if despill_edges:
        from edge_despill import despill
        result, cleanup = despill(result, radius=despill_radius, reference_radius=despill_radius * 3)
    return result, {"source_crop_bbox": list(box), "shared_scale": scale, "paste_xy": [px, py],
                    "resized_crop_size": list(scaled.size), "bbox_alpha_gt_8": bounds(result),
                    "body_ground_anchor_px": list(body_ground_anchor(result)), "alignment_version": 2, "output_edge_touch": False, "paste_clamped": False,
                    "rgba_sha256": hashlib.sha256(result.tobytes()).hexdigest(), "edge_despill": cleanup}


def prepare_alignment_v3(image, scale, despill_edges=False, despill_radius=2):
    """One character-wide scale, before any per-pose integer translation."""
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("Invalid shared alignment scale")
    box = bounds(image, 0)
    if box is None:
        raise ValueError("empty preprocessed frame")
    crop = image.crop(box)
    size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    crop = crop.resize(size, Image.Resampling.LANCZOS)
    cleanup = None
    if despill_edges:
        from edge_despill import despill
        padded = Image.new("RGBA", (crop.width + 8, crop.height + 8))
        padded.paste(crop, (4, 4))
        padded, cleanup = despill(padded, radius=despill_radius, reference_radius=despill_radius * 3)
        crop = padded.crop((4, 4, crop.width + 4, crop.height + 4))
    return crop, {"source_crop_bbox": box, "shared_scale": scale,
                  "resized_crop_size": list(size), "edge_despill": cleanup}


def head_anchor_v3(image, roi_height):
    yy, xx = np.nonzero(np.asarray(image.getchannel("A")) > 8)
    if not len(xx) or roi_height < 1:
        raise ValueError("Missing fixed head ROI")
    top = int(yy.min())
    return float(np.median(xx[yy < top + roi_height])), top


def alignment_v3_reference(idle_crop):
    box = bounds(idle_crop)
    if box is None:
        raise ValueError("Missing idle reference")
    # Calibrate once from idle. Walk foot depth never changes this ROI height.
    roi_height = max(1, int((box[3] - 1 - box[1]) * .42))
    return {"roi_height_px": roi_height, "alpha_threshold": 8,
            "target_head_px": [FOOT[0], box[1] + FOOT[1] - (box[3] - 1)]}


def translate_alignment_v3(crop, reference):
    ax, ay = head_anchor_v3(crop, reference["roi_height_px"])
    tx, ty = reference["target_head_px"]
    dx, dy = round(tx - ax), int(ty - ay)
    box = bounds(crop, 0)
    moved = [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]
    if min(moved[:2]) < 1 or max(moved[2:]) > CELL - 1:
        raise ValueError(f"alignment v3 would clip/touch nonzero alpha: {moved}")
    result = Image.new("RGBA", (CELL, CELL))
    result.paste(crop, (dx, dy))  # Unmasked: preserve the source RGBA exactly.
    return result, {"alignment_version": 3, "pretranslation_bbox": box,
                    "pretranslation_rgba_sha256": hashlib.sha256(crop.tobytes()).hexdigest(),
                    "pretranslation_crop_rgba_sha256": hashlib.sha256(crop.crop(box).tobytes()).hexdigest(),
                    "translation_px": [dx, dy], "head_anchor_before_px": [ax, ay],
                    "head_anchor_after_px": list(head_anchor_v3(result, reference["roi_height_px"])),
                    "bbox_alpha_gt_8": bounds(result), "bbox_alpha_gt_0": bounds(result, 0),
                    "rgba_sha256": hashlib.sha256(result.tobytes()).hexdigest(),
                    "output_edge_touch": False, "paste_clamped": False}


def normalize_direction_v3(walk, idle, scale, evidence_dir, root, despill_edges=False, despill_radius=2):
    prepared = [prepare_alignment_v3(f, scale, despill_edges, despill_radius) for f in [idle, *walk]]
    reference = alignment_v3_reference(prepared[0][0])
    evidence_dir.mkdir(parents=True, exist_ok=True)
    output, records = [], []
    for index, (crop, record) in enumerate(prepared):
        name = "idle.png" if index == 0 else f"{index:02d}.png"
        path = evidence_dir / name
        crop.save(path)
        result, transform = translate_alignment_v3(crop, reference)
        record.update(transform, input_path=path.relative_to(root).as_posix(), input_sha256=sha(path))
        output.append(result)
        records.append(record)
    reference.update(idle_input_path=records[0]["input_path"], idle_input_sha256=records[0]["input_sha256"],
                     idle_rgba_sha256=records[0]["rgba_sha256"])
    return output[1:], output[0], records[1:], records[0], reference


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
    parser.add_argument("--despill-magenta-edge", action="store_true", help="Remove verified magenta contamination within the selected alpha boundary band; preserve alpha, geometry, green and protected red.")
    parser.add_argument("--despill-radius", type=int, choices=(2, 4), default=2,
                        help="Opt-in edge radius for --despill-magenta-edge: 2px uses 6px clean references (default); 4px uses 12px references.")
    parser.add_argument("--alignment-version", type=int, choices=(2, 3), default=2,
                        help="2: legacy feet alignment; 3: explicit separate candidate head/idle alignment.")
    parser.add_argument("--common-scale", type=float,
                        help="V3 only: fixed common final scale for all 72 poses (e.g. 1.0 for pixel A/B).")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.character_dir.resolve()
    if root.name not in APPROVED:
        parser.error("Only the eight accepted character IDs are allowed; the rejected elder is excluded.")
    if not 100 <= args.target_height <= 450:
        parser.error("Target silhouette height must be 100..450.")
    if args.alignment_version == 3 and root == Path(__file__).resolve().parent / root.name:
        parser.error("Alignment v3 is opt-in for a separate approved-character candidate directory only.")
    if args.common_scale is not None and (args.alignment_version != 3 or
            not math.isfinite(args.common_scale) or args.common_scale <= 0):
        parser.error("--common-scale requires v3 and a positive finite number.")
    root.mkdir(parents=True, exist_ok=True)
    work = root / "processing"
    qc = {"version": VERSION, "status": "processing", "errors": [], "visual_review": "required",
          "gates": {"body_scale_cv_max": 0.08, "source_anchor_y_std_max": 0.05,
                    "cross_direction_mean_height_ratio_max": 1.10, "idle_walk_height_drift_max": 0.08,
                    "foot_target_px": list(FOOT), "unique_frames_per_direction": 8, "horizontal_body_axis_deviation_max_px": 0.5}}
    if args.alignment_version == 3:
        qc["gates"].pop("source_anchor_y_std_max")
        qc["gates"].pop("foot_target_px")
        qc["gates"].update(world_root_px=list(FOOT), head_top_deviation_max_px=0,
                           foot_depth_variance="record_only")
    sources, pre_walk, pre_idle, directions_qc = {}, {}, {}, {}
    references = {}
    try:
        for kind in (*SHEETS, "idle"):
            print(f"Processing {root.name}/{kind}...", flush=True)
            frames, meta, source, errors = run_sheet(getattr(args, kind), kind, work / kind, args.processor,
                                                    args.component_padding, root / "prompts" / f"{kind}.txt", args.force,
                                                    alignment_version=args.alignment_version)
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
        if args.common_scale is not None:
            scale = args.common_scale
        for frame in (all_pre if args.alignment_version == 2 else []):
            crop = frame.crop(frame.getbbox())
            ax, ay = body_ground_anchor(crop)
            scale = min(scale, (FOOT[0] - 4) / max(ax, 1), (CELL - FOOT[0] - 4) / max(crop.width - ax, 1),
                        (FOOT[1] - 4) / max(ay, 1), (CELL - FOOT[1] - 4) / max(crop.height - ay, 1))
        output_walk, output_idle, records = {}, {}, {"walk": {}, "idle": {}}
        means = []
        for direction in DIRECTIONS:
            if args.alignment_version == 3:
                (output_walk[direction], output_idle[direction], records["walk"][direction],
                 records["idle"][direction], references[direction]) = normalize_direction_v3(
                    pre_walk[direction], pre_idle[direction], scale, work / "alignment-v3" / direction,
                    root, args.despill_magenta_edge, args.despill_radius)
            else:
                pairs = [normalize(f, scale, args.despill_magenta_edge, args.despill_radius) for f in pre_walk[direction]]
                output_walk[direction] = [p[0] for p in pairs]
                records["walk"][direction] = [p[1] for p in pairs]
                output_idle[direction], records["idle"][direction] = normalize(pre_idle[direction], scale, args.despill_magenta_edge, args.despill_radius)
            heights = [r["bbox_alpha_gt_8"][3] - r["bbox_alpha_gt_8"][1] for r in records["walk"][direction]]
            mean = float(np.mean(heights))
            means.append(mean)
            unique = len({r["rgba_sha256"] for r in records["walk"][direction]})
            ib = records["idle"][direction]["bbox_alpha_gt_8"]
            idle_drift = abs((ib[3] - ib[1]) / mean - 1)
            directions_qc[direction].update(unique_frames=unique, output_subject_heights=heights,
                                            output_subject_height_mean=mean, idle_walk_height_drift=idle_drift)
            axis_x = [(head_anchor_v3(f, references[direction]["roi_height_px"])[0]
                       if args.alignment_version == 3 else body_ground_anchor(f)[0])
                      for f in [*output_walk[direction], output_idle[direction]]]
            axis_deviation = max(abs(x - FOOT[0]) for x in axis_x)
            directions_qc[direction].update(horizontal_body_axes_px=axis_x,
                                            horizontal_body_axis_max_deviation_px=axis_deviation)
            if axis_deviation > 0.5:
                qc["errors"].append(f"{direction}: horizontal body axis drift {axis_deviation:.3f} > .5px")
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
                    ("world_root_px" if args.alignment_version == 3 else "output_foot_px"): list(FOOT), "processor_preserve_fit_scale": 0.84, "final_common_scale": scale,
                   "strategy": "same normalized raw-cell scale for all 72 poses, then one common final scale; translation only per pose",
                   "source_to_output_scale_by_sheet": {kind: CELL / max(source["native_cell_size"]) * .84 * scale for kind, source in sources.items()},
                   "native_sheet_sizes": {k: s["native_size"] for k, s in sources.items()},
                   "per_frame_scale_normalization": False, "mirrored_frames": False, "synthetic_or_repeated_frames": False,
                   "edge_despill": f"boundary_{args.despill_radius}px_preserve_alpha_and_red" if args.despill_magenta_edge else None,
                   "edge_despill_parameters": {"radius_px": args.despill_radius, "reference_radius_px": args.despill_radius * 3} if args.despill_magenta_edge else None,
                   "alignment_version": args.alignment_version,
                   "horizontal_axis": "fixed idle head ROI alpha median" if args.alignment_version == 3 else "median alpha>8 in upper 42% of silhouette",
                   "vertical_axis": "direction idle head top" if args.alignment_version == 3 else "lowest alpha>8 ground pixel"})
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
        alignment = {"version": 2, "horizontal": "upper_body_alpha_median_42_percent",
                     "vertical": "lowest_alpha_gt_8", "root_px": list(FOOT)}
        if args.alignment_version == 3:
            alignment = {"version": 3, "horizontal": "fixed_idle_head_roi_alpha_median",
                         "vertical": "direction_idle_head_top", "root_px": list(FOOT),
                         "common_scale": scale, "direction_references": references,
                         "transforms_path": "processing/frame-transforms.json",
                         "transforms_sha256": sha(work / "frame-transforms.json")}
        write_json(root / "manifest.json", {"version": VERSION, "character_id": root.name,
                   "generated_at_utc": datetime.now(timezone.utc).isoformat(), "art_source": "built-in image_gen",
                   "alignment": alignment,
                   "edge_despill": {"enabled": bool(args.despill_magenta_edge), "radius_px": args.despill_radius, "reference_radius_px": args.despill_radius * 3, "green_unchanged": True, "alpha_unchanged": True, "geometry_unchanged": True, "red_protected": True, "implementation_sha256": sha(Path(__file__).with_name("edge_despill.py"))} if args.despill_magenta_edge else None,
                   "portrait": "portrait.png", "portrait_size": [1024, 1024],
                   "portrait_mode": portrait_source["mode"], "portrait_source": portrait_source,
                   "portrait_v11_sha256": portrait_source["baseline_v11_sha256"],
                   "walk": {"directions": DIRECTIONS, "frames_per_direction": 8, "cell": [CELL, CELL],
                            "strip_size": [4096, 512], "frame_duration_ms": 60, "fps": 1000 / 60,
                            ("world_root_px_from_top_left" if args.alignment_version == 3 else "feet_px_from_top_left"): list(FOOT), "frame_pattern": "walk/{direction}/{01..08}.png",
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
