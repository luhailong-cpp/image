#!/usr/bin/env python3
"""Hard minimum-error seams for a native 1254-square repair; no source-image resampling."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
QA = ROOT / "qa"
REPAIR = ROOT / "repairs" / "south_stairs"
BASE = OUT / "tianyong_plaza_4k_candidate.png"
DEST = OUT / "tianyong_plaza_4k_candidate_v2.png"
REPORT = OUT / "south_stairs_v2_assembly.json"
BAND = 96


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rgb(path):
    with Image.open(path) as image:
        image.load()
        return np.asarray(image.convert("RGB")).copy()


def save(array, path):
    Image.fromarray(array).save(path, format="PNG", optimize=True)


def main():
    original = load_json(OUT / "assembly.json")
    if sha(BASE) != original["output"]["sha256"]:
        raise ValueError("Base candidate differs from first assembly")
    plan = load_json(REPAIR / "plan.json")
    record = load_json(REPAIR / "repair.record.json")
    repair_path = REPAIR / "repair-native.png"
    before_path = REPAIR / "before.png"
    prompt_path = REPAIR / "repair.prompt.txt"
    for path, key in ((repair_path, "outputSha256"), (before_path, "referenceSha256"), (prompt_path, "promptSha256")):
        if sha(path) != record[key].lower():
            raise ValueError(f"Repair source hash mismatch: {path}")
    source_path = Path(record["sourceOutputPath"])
    if not source_path.is_file() or sha(source_path) != sha(repair_path):
        raise ValueError("Repair native file is not byte-identical to generator output")
    if record["actualNativePixels"] != [1254, 1254] or record["backendModelVerified"] is not False:
        raise ValueError("Unexpected repair provenance")
    rect = list(map(int, plan["crop"]))
    if rect != [1421, 2842, 2675, 4096]:
        raise ValueError("Unexpected repair crop")
    x0, y0, x1, y1 = rect
    base = rgb(BASE)
    old = base[y0:y1, x0:x1].copy()
    new = rgb(repair_path)
    before = rgb(before_path)
    if new.shape != (1254, 1254, 3) or not np.array_equal(old, before):
        raise ValueError("Repair dimension or exact before-crop verification failed")
    helper_path = ROOT.parents[1] / "tianyong_festival_hd_20260910" / "seam_helpers.py"
    spec = importlib.util.spec_from_file_location("existing_city_seams_v2", helper_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    seam_fn = module._minimum_vertical_seam
    height, width = old.shape[:2]
    left = seam_fn(old[:, :BAND], new[:, :BAND])
    right = seam_fn(old[:, -BAND:], new[:, -BAND:]) + width - BAND
    top = seam_fn(np.transpose(old[:BAND], (1, 0, 2)), np.transpose(new[:BAND], (1, 0, 2)))
    bottom = seam_fn(np.transpose(old[-BAND:], (1, 0, 2)), np.transpose(new[-BAND:], (1, 0, 2))) + height - BAND
    xx = np.arange(width)[None, :]
    yy = np.arange(height)[:, None]
    mask = (xx >= left[:, None]) & (xx < right[:, None]) & (yy >= top[None, :]) & (yy < bottom[None, :])
    composed_crop = np.where(mask[..., None], new, old)
    result = base.copy()
    result[y0:y1, x0:x1] = composed_crop
    if result.shape != (4096, 4096, 3):
        raise ValueError("Output must remain exactly 4096 square")
    outside = np.ones((4096, 4096), dtype=bool)
    outside[y0:y1, x0:x1] = False
    if not np.array_equal(result[outside], base[outside]):
        raise AssertionError("Pixels outside the repair crop changed")
    # Every output sample is selected unchanged from one source. No interpolation, blending or blur.
    if not np.all(np.all(composed_crop == old, axis=2) | np.all(composed_crop == new, axis=2)):
        raise AssertionError("A pixel was synthesized during hard-seam selection")
    save(result, DEST)
    previews = []
    overview = Image.fromarray(result).resize((1024, 1024), Image.Resampling.LANCZOS)
    overview_path = QA / "v2_overview_1024.png"
    overview.save(overview_path, format="PNG", optimize=True)
    previews.append({"file": str(overview_path.relative_to(ROOT)), "kind": "downsampled_preview_only", "size": [1024, 1024], "sha256": sha(overview_path)})
    crops = {
        "v2_south_stairs_left_seam_100pct": [971, 3196, 1871, 4096],
        "v2_south_stairs_right_seam_100pct": [2225, 3196, 3125, 4096],
        "v2_south_stairs_top_seam_100pct": [1598, 2392, 2498, 3292],
        "v2_south_stairs_center_100pct": [1598, 3196, 2498, 4096],
        "v2_south_stairs_fullwidth_100pct": [650, 2842, 3450, 4096],
    }
    for name, crop in crops.items():
        a,b,c,d = crop
        path = QA / (name + ".png")
        save(result[b:d,a:c], path)
        previews.append({"file": str(path.relative_to(ROOT)), "kind": "native_pixel_crop", "crop": crop,
                         "size": [c-a, d-b], "resized": False, "sha256": sha(path)})
    full_preview = Image.fromarray(result[2842:4096,650:3450]).resize((1400,627), Image.Resampling.LANCZOS)
    full_preview_path = QA / "v2_south_stairs_fullwidth_overview_1400.png"
    full_preview.save(full_preview_path, format="PNG", optimize=True)
    previews.append({"file": str(full_preview_path.relative_to(ROOT)), "kind": "downsampled_preview_only",
                     "sourceCrop": [650,2842,3450,4096], "size": [1400,627], "sha256": sha(full_preview_path)})
    mask_path = QA / "v2_south_stairs_source_selection_mask.png"
    Image.fromarray(mask.astype(np.uint8)*255).save(mask_path)
    seams = {name: {"min": int(line.min()), "max": int(line.max()), "mean": float(line.mean())}
             for name,line in (("left_x",left),("right_x",right),("top_y",top),("bottom_y",bottom))}
    report = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_pending_visual_QA_not_published", "published": False,
        "base": {"file": str(BASE), "sha256": sha(BASE), "assemblySha256": sha(OUT / "assembly.json")},
        "repair": {"file": str(repair_path), "sha256": sha(repair_path), "recordSha256": sha(REPAIR / "repair.record.json"),
                   "promptSha256": sha(prompt_path), "beforeSha256": sha(before_path), "nativeSize": [1254,1254], "crop": rect,
                   "route": record["route"], "backendModelVerified": False},
        "script": {"file": str(Path(__file__)), "sha256": sha(Path(__file__))},
        "seamHelper": {"file": str(helper_path), "sha256": sha(helper_path), "function": "_minimum_vertical_seam"},
        "composition": {"method": "four independent minimum-error border seams, interior masks intersected; hard source selection",
                        "borderSearchBandPixels": BAND, "featherPixels": 0, "colorMatching": False,
                        "sourceResampling": False, "sourceStretching": False, "blur": False, "sharpening": False,
                        "outsideCropPixelsPreserved": True, "outputPixelsAreUnmodifiedSourceSamples": True,
                        "selectedRepairPixelCount": int(mask.sum()), "seamPositions": seams},
        "output": {"file": str(DEST), "width": 4096, "height": 4096, "sha256": sha(DEST)},
        "finalArtUpscaled": False, "qa": previews,
        "selectionMask": {"file": str(mask_path), "sha256": sha(mask_path), "white": "repair", "black": "original"},
        "visualQa": {"status": "pending", "concern": "Repair fixes interior stair line continuity but may introduce tread-height mismatch at side edges; no visual pass claimed."}
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"output": str(DEST), "report": str(REPORT), "nativeSize": [4096,4096], "qaFiles": len(previews),
                      "mechanicalChecks": "passed; exact source selection, no resampling, all source hashes verified",
                      "status": report["status"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
