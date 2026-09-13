#!/usr/bin/env python3
"""Independent export audit; visual judgment must already be recorded in qc.json."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from process_roster import APPROVED, DIRECTIONS, V11, sha, write_json


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
            ax = float(np.median(xx[yy >= np.percentile(yy, 90)]))
            ay = int(yy.max())
            if ay != 471 or abs(ax - 256) > 0.5:
                raise ValueError(f"Wrong feet anchor {ax, ay}: {relative}")
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
            "foot_anchors": anchors, "artifacts": artifacts}


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
