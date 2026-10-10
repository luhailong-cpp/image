#!/usr/bin/env python3
"""Independent export audit; visual judgment must already be recorded in qc.json."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from process_roster import APPROVED, DIRECTIONS, V11, sha, write_json


def verify_v3_frame(image, before, record, reference, common_scale):
    """Independent pixel reconstruction; intentionally does not call alignment helpers."""
    if before.mode != "RGBA" or image.mode != "RGBA" or image.size != (512, 512):
        raise ValueError("Invalid v3 RGBA geometry")
    alpha = np.asarray(before.getchannel("A"))
    yy0, xx0 = np.nonzero(alpha > 0)
    yy, xx = np.nonzero(alpha > 8)
    if not len(xx0) or not len(xx):
        raise ValueError("Empty v3 input")
    box = [int(xx0.min()), int(yy0.min()), int(xx0.max()) + 1, int(yy0.max()) + 1]
    digest = lambda im: hashlib.sha256(im.tobytes()).hexdigest()
    if (record.get("alignment_version") != 3 or record.get("shared_scale") != common_scale or
            record.get("pretranslation_bbox") != box or
            record.get("resized_crop_size") != list(before.size) or
            record.get("pretranslation_rgba_sha256") != digest(before) or
            record.get("pretranslation_crop_rgba_sha256") != digest(before.crop(box))):
        raise ValueError("V3 pretranslation evidence differs")
    original_box = record.get("source_crop_bbox", [])
    if len(original_box) != 4 or any(type(v) is not int for v in original_box):
        raise ValueError("Invalid v3 source crop metadata")
    expected_size = [max(1, round((original_box[2] - original_box[0]) * common_scale)),
                     max(1, round((original_box[3] - original_box[1]) * common_scale))]
    if expected_size != list(before.size):
        raise ValueError("V3 shared scale differs between poses")
    top = int(yy.min())
    roi_height = reference["roi_height_px"]
    ax = float(np.median(xx[yy < top + roi_height]))
    target_x, target_y = reference["target_head_px"]
    shift = [round(target_x - ax), target_y - top]
    if record.get("translation_px") != shift or any(type(v) is not int for v in record["translation_px"]):
        raise ValueError("V3 translation does not align the independently measured head")
    moved = [box[0] + shift[0], box[1] + shift[1], box[2] + shift[0], box[3] + shift[1]]
    if min(moved[:2]) < 1 or max(moved[2:]) > 511:
        raise ValueError("V3 translation clips or touches nonzero alpha")
    expected = Image.new("RGBA", (512, 512))
    expected.paste(before, tuple(shift))
    if expected.tobytes() != image.tobytes() or digest(image.crop(moved)) != digest(before.crop(box)):
        raise ValueError("V3 output changes/crops source RGBA or has an incorrect shift")
    out_alpha = np.asarray(image.getchannel("A"))
    oy, ox = np.nonzero(out_alpha > 8)
    out_top = int(oy.min())
    out_ax = float(np.median(ox[oy < out_top + roi_height]))
    out_box = [int(ox.min()), out_top, int(ox.max()) + 1, int(oy.max()) + 1]
    if abs(out_ax - 256) > .5 or out_top != target_y:
        raise ValueError("V3 output does not match the idle head anchor")
    if (record.get("head_anchor_before_px") != [ax, top] or
            record.get("head_anchor_after_px") != [out_ax, out_top] or
            record.get("bbox_alpha_gt_0") != moved or record.get("bbox_alpha_gt_8") != out_box or
            record.get("rgba_sha256") != digest(image) or record.get("output_edge_touch") is not False or
            record.get("paste_clamped") is not False):
        raise ValueError("V3 transform metadata differs from independently reconstructed pixels")
    return {"head_anchor": [out_ax, out_top], "lowest_alpha_y": int(oy.max()), "translation_px": shift}


def verify_alignment_v3(root, alignment):
    root = Path(root).resolve()
    if (root.name not in APPROVED or alignment.get("horizontal") != "fixed_idle_head_roi_alpha_median" or
            alignment.get("vertical") != "direction_idle_head_top" or alignment.get("root_px") != [256, 471]):
        raise ValueError("Unknown v3 alignment contract")
    scale = alignment.get("common_scale")
    if not isinstance(scale, (int, float)) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("Invalid v3 common scale")
    if alignment.get("transforms_path") != "processing/frame-transforms.json":
        raise ValueError("Unexpected v3 transform evidence path")
    transforms_path = root / alignment["transforms_path"]
    if sha(transforms_path) != alignment.get("transforms_sha256"):
        raise ValueError("Changed v3 transform evidence")
    records = json.loads(transforms_path.read_text(encoding="utf-8"))
    references = alignment.get("direction_references", {})
    if (set(references) != set(DIRECTIONS) or set(records) != {"walk", "idle"} or
            set(records["walk"]) != set(DIRECTIONS) or set(records["idle"]) != set(DIRECTIONS)):
        raise ValueError("V3 evidence must cover all 72 poses")
    checked = []
    for direction in DIRECTIONS:
        if len(records["walk"][direction]) != 8:
            raise ValueError("V3 direction must contain eight transforms")
        reference = references[direction]
        inputs = []
        for index, record in enumerate([records["idle"][direction], *records["walk"][direction]]):
            filename = "idle.png" if index == 0 else f"{index:02d}.png"
            relative = f"processing/alignment-v3/{direction}/{filename}"
            path = (root / relative).resolve()
            if not path.is_relative_to(root) or record.get("input_path") != relative or sha(path) != record.get("input_sha256"):
                raise ValueError("Missing or changed v3 pretranslation input")
            with Image.open(path) as im:
                if im.mode != "RGBA":
                    raise ValueError("V3 input is not RGBA")
                inputs.append(im.copy())
        idle_alpha = np.asarray(inputs[0].getchannel("A"))
        iy, ix = np.nonzero(idle_alpha > 8)
        if not len(ix):
            raise ValueError("Empty v3 idle reference")
        expected_reference = {"roi_height_px": max(1, int((int(iy.max()) - int(iy.min())) * .42)),
                              "alpha_threshold": 8, "target_head_px": [256, int(iy.min()) + 471 - int(iy.max())],
                              "idle_input_path": records["idle"][direction]["input_path"],
                              "idle_input_sha256": records["idle"][direction]["input_sha256"],
                              "idle_rgba_sha256": records["idle"][direction]["rgba_sha256"]}
        if reference != expected_reference:
            raise ValueError("V3 reference differs from independently measured idle")
        for index, (before, record) in enumerate(zip(inputs, [records["idle"][direction], *records["walk"][direction]])):
            relative = f"idle/{direction}.png" if index == 0 else f"walk/{direction}/{index:02d}.png"
            with Image.open(root / relative) as image:
                measured = verify_v3_frame(image, before, record, reference, scale)
            checked.append({"path": relative, **measured})
    return checked


def verify_character(root, require_visual=True):
    root = Path(root)
    if root.name not in APPROVED:
        raise ValueError(f"Unapproved identity: {root.name}")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    qc = json.loads((root / "qc.json").read_text(encoding="utf-8"))
    if manifest.get("version") != 12 or manifest.get("character_id") != root.name:
        raise ValueError("Wrong V12 manifest identity")
    if qc.get("errors") or qc.get("status") not in ("passed", "passed_numeric_qc_pending_visual_review"):
        raise ValueError("Numeric processing QC has not passed")
    if require_visual and (qc.get("status") != "passed" or qc.get("visual_review") != "passed"):
        raise ValueError("Character identity, eight real gait poses, direction and edges still need visual review")
    if manifest["walk"]["frames_per_direction"] != 8 or manifest["walk"]["frame_duration_ms"] != 60:
        raise ValueError("Expected eight genuine frames at 60 ms each")
    if set(manifest["walk"]["directions"]) != set(DIRECTIONS) or not manifest["idle"]["dedicated_neutral_pose"]:
        raise ValueError("Expected all eight directions and independent neutral idle poses")
    alignment = manifest.get("alignment", {})
    alignment_version = alignment.get("version")
    v3_anchors = None
    if alignment_version == 3:
        v3_anchors = verify_alignment_v3(root, alignment)
    elif alignment != {"version": 2, "horizontal": "upper_body_alpha_median_42_percent",
                       "vertical": "lowest_alpha_gt_8", "root_px": [256, 471]}:
        raise ValueError("Expected supported body alignment v2 or v3")
    expected = {"portrait.png"}
    expected.update(f"idle/{d}.png" for d in DIRECTIONS)
    expected.update(f"walk/{d}/{i:02d}.png" for d in DIRECTIONS for i in range(1, 9))
    expected.update(f"walk/{d}/{name}" for d in DIRECTIONS for name in ("strip.png", "walk.gif"))
    files = {item["path"]: item for item in manifest["files"]}
    if len(files) != len(manifest["files"]) or set(files) != expected:
        raise ValueError("Expected exact 89-file final media set")
    actual = {p.relative_to(root).as_posix() for folder in (root / "walk", root / "idle")
              for p in folder.rglob("*") if p.suffix.lower() in (".png", ".gif")}
    if actual != expected - {"portrait.png"}:
        raise ValueError(f"Unexpected final frame/strip/idle file set: {sorted(actual ^ (expected - {'portrait.png'}))}")
    artifacts = []
    anchors, unique_count = [], {}
    for relative in sorted(expected):
        path = root / relative
        digest = sha(path)
        if digest != files[relative]["sha256"]:
            raise ValueError(f"Changed exported media after manifest: {relative}")
        artifacts.append({"path": relative, "sha256": digest, "bytes": path.stat().st_size})
        if path.suffix != ".png":
            continue
        with Image.open(path) as image:
            image.load()
            size = (1024, 1024) if relative == "portrait.png" else (4096, 512) if relative.endswith("strip.png") else (512, 512)
            if image.mode != "RGBA" or image.size != size or image.format != "PNG":
                raise ValueError(f"Invalid image contract: {relative}: {image.mode}/{image.size}")
            rgba = np.asarray(image)
            if rgba[:, :, 3].min() != 0 or rgba[:, :, 3].max() != 255:
                raise ValueError(f"Missing transparent background or opaque body: {relative}")
            if size != (512, 512):
                continue
            yy, xx = np.nonzero(rgba[:, :, 3] > 8)
            # Independently recompute horizontal body axis; do not reuse the processor helper.
            upper_limit = int(yy.min() + (yy.max() - yy.min()) * 0.42)
            axis_pixels = xx[yy < upper_limit]
            if not len(axis_pixels):
                raise ValueError(f"Missing upper-body axis: {relative}")
            ax = float(np.median(axis_pixels))
            ay = int(yy.max())
            if alignment_version == 2 and (ay != 471 or abs(ax - 256) > 0.5):
                raise ValueError(f"Wrong body-axis/ground anchor {ax, ay}: {relative}")
            alpha = rgba[:, :, 3]
            if any(np.any(edge) for edge in (alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1])):
                raise ValueError(f"Output touches cell edge: {relative}")
            anchors.append({"path": relative, "anchor": [ax, ay]})
    portrait_source = manifest.get("portrait_source", {})
    portrait_mode = manifest.get("portrait_mode", "v11_unchanged")
    if portrait_mode == "v11_unchanged":
        if sha(root / "portrait.png") != sha(V11 / root.name / "portrait.png"):
            raise ValueError("Unchanged V11 portrait differs from its accepted source")
    elif portrait_mode == "replacement":
        if portrait_source.get("export_sha256") != sha(root / "portrait.png"):
            raise ValueError("Replacement portrait differs from its recorded export")
        original = Path(portrait_source.get("path", ""))
        if not original.is_file() or sha(original) != portrait_source.get("sha256"):
            raise ValueError("Replacement portrait source/provenance missing or changed")
    else:
        raise ValueError("Unknown portrait source mode")
    for direction in DIRECTIONS:
        frame_bytes = []
        with Image.open(root / "walk" / direction / "strip.png") as strip:
            for index in range(8):
                with Image.open(root / "walk" / direction / f"{index + 1:02d}.png") as frame:
                    pixels = frame.tobytes()
                if strip.crop((index * 512, 0, (index + 1) * 512, 512)).tobytes() != pixels:
                    raise ValueError(f"Strip/frame mismatch: {direction}/{index + 1}")
                frame_bytes.append(pixels)
        unique_count[direction] = len({hashlib.sha256(p).hexdigest() for p in frame_bytes})
        if unique_count[direction] != 8:
            raise ValueError(f"Duplicate gait frame: {direction}")
        with Image.open(root / "idle" / f"{direction}.png") as idle:
            if idle.tobytes() in frame_bytes:
                raise ValueError(f"Idle copied from walk: {direction}")
        with Image.open(root / "walk" / direction / "walk.gif") as gif:
            if gif.n_frames != 8 or gif.info.get("loop") != 0:
                raise ValueError(f"GIF must contain exactly eight looping frames: {direction}")
            for index in range(8):
                gif.seek(index)
                if gif.info.get("duration") != 60:
                    raise ValueError(f"GIF timing incorrect: {direction}/{index + 1}")
    return {"version": 12, "character_id": root.name, "status": "passed" if require_visual else "passed_exports_pending_visual",
            "verified_at_utc": datetime.now(timezone.utc).isoformat(), "movement_frames": 64,
            "neutral_idle_frames": 8, "portraits": 1, "media_files": 89, "unique_frames": unique_count,
            "manifest_sha256": sha(root / "manifest.json"), "qc_sha256": sha(root / "qc.json"),
            "alignment_version": alignment_version,
            ("body_ground_anchors" if alignment_version == 2 else "head_anchors"): anchors if alignment_version == 2 else v3_anchors,
            "artifacts": artifacts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character-dir", type=Path, required=True)
    parser.add_argument("--allow-pending-visual", action="store_true", help="Numeric audit only; output cannot be imported to the game.")
    args = parser.parse_args()
    result = verify_character(args.character_dir.resolve(), not args.allow_pending_visual)
    write_json(args.character_dir / "validation.json", result)
    print(json.dumps({key: result[key] for key in ("character_id", "status", "movement_frames", "neutral_idle_frames", "media_files")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
