"""Read-only repository artwork exposure inventory and review contact sheets.

Source assets are never written. Only JSON and review JPEGs under this package
are outputs. Contact thumbnails must never be inputs to production grading.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO / "qdao_exposure_refinement_v8"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tga", ".svg"}
INFRA = {".git", "node_modules", ".agents", ".codex", ".venv", "venv", "__pycache__", ".pytest_cache", "unity-download-resume"}
REFERENCE_DIRS = {".work", "backups", "backup", "references", "reference", "qa", "qc", "docs", "diagnostics"}
SAMPLE_MAX = 512


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def classify(path):
    rel = path.relative_to(REPO)
    parts = [p.lower() for p in rel.parts]
    stem = path.stem.lower()
    if parts[0] == PACKAGE.name:
        return "v8_review_sample", "Current refinement package excluded from treatment"
    keep = next((p for p in parts[:-1] if p in REFERENCE_DIRS), None)
    if keep:
        return "reference_or_diagnostic", f"Preserve {keep} directory"
    if re.match(r"^(reference|ref)[-_]", stem) or stem.endswith(("-reference", "_reference")):
        return "reference_or_diagnostic", "Reference-named input retained as evidence"
    if "walkmask" in stem or "walk_mask" in stem or "dim_overlay" in stem or "dim_mask" in stem:
        return "technical_preserve", "Navigation overlay or black alpha dim mask"
    if stem in {"labels", "hud_labels"}:
        return "technical_preserve", "Independent text layer"
    if any(p in {"source", "sources"} for p in parts[:-1]) or stem.endswith(".raw") or "matte" in stem or "chroma" in stem:
        return "source_or_matte", "Production source or chroma/matte artwork"
    if "prepared" in parts:
        return "prepared_copy", "Prepared client asset retained in coverage"
    if "derived" in parts:
        return "derived", "Production derived artwork retained in coverage"
    return "formal", "Formal asset or presentation output"


def scan():
    paths = []
    for current, directories, files in os.walk(REPO):
        directories[:] = sorted(d for d in directories if d.lower() not in INFRA and not (Path(current) / d).is_symlink())
        # Review contacts are outputs of this script, not new samples to audit.
        if Path(current).resolve() == (PACKAGE / "review").resolve():
            directories[:] = []
            continue
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix.lower() in EXTENSIONS and not path.is_symlink():
                paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(REPO).as_posix())


NODE_RENDERER = r"""
const readline=require('node:readline');
const sharp=require(process.argv[1]);
const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
(async()=>{for await(const line of rl){try{
  const req=JSON.parse(line);
  const s=sharp(req.path,{density:72,limitInputPixels:false});
  const m=await s.metadata();
  const buf=await s.resize({width:req.max,height:req.max,fit:'inside',withoutEnlargement:true}).png().toBuffer();
  process.stdout.write(JSON.stringify({size:[m.width,m.height],png:buf.toString('base64')})+'\n');
}catch(e){process.stdout.write(JSON.stringify({error:String(e)})+'\n');}}})();
"""


class SvgRenderer:
    def __init__(self):
        node = shutil.which("node")
        sharp = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp"
        if not node or not sharp.exists():
            raise RuntimeError("Existing Node/Sharp renderer unavailable; no dependency downloads attempted")
        self.process = subprocess.Popen([node, "-e", NODE_RENDERER, str(sharp)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

    def render(self, path):
        self.process.stdin.write(json.dumps({"path": str(path), "max": SAMPLE_MAX}) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError("SVG renderer exited: " + self.process.stderr.read()[-1000:])
        result = json.loads(line)
        if "error" in result:
            raise RuntimeError(result["error"])
        image = Image.open(io.BytesIO(base64.b64decode(result["png"]))).convert("RGBA")
        return image, result["size"]

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            self.process.wait(timeout=30)


def read_sample(path, svg):
    if path.suffix.lower() == ".svg":
        im, size = svg.render(path)
        alpha = im.getchannel("A").getextrema()
        return im, {"size": size, "mode": "SVG", "alpha_range": list(alpha), "alpha_measurement": "512px maximum rasterized SVG preview", "frames": 1, "sample_method": "Sharp SVG rendering, max 512px"}
    with Image.open(path) as opened:
        size, mode = list(opened.size), opened.mode
        frames = getattr(opened, "n_frames", 1)
        opened.seek(0)
        rgba = opened.convert("RGBA")
        alpha = rgba.getchannel("A").getextrema()
        scale = min(1, SAMPLE_MAX / max(size))
        sample_size = tuple(max(1, round(n * scale)) for n in size)
        sample = rgba.resize(sample_size, Image.Resampling.NEAREST)
        rgba.close()
    return sample, {"size": size, "mode": mode, "alpha_range": list(alpha), "alpha_measurement": "Full original first-frame alpha extrema", "frames": frames, "sample_method": "Deterministic nearest-neighbor spatial sample, max 512px; frame 0"}


def metrics(image):
    a = np.asarray(image, dtype=np.uint8)
    visible = a[:, :, 3] > 16
    result = {"sample_size": list(image.size), "visible_fraction": float(visible.mean()), "visible_sample_pixels": int(visible.sum())}
    if not visible.any():
        result.update({k: 0.0 for k in ["linear_luminance_mean", "linear_luminance_p90", "linear_luminance_p99", "srgb_luminance_mean", "bright_fraction", "nearwhite_fraction", "colorful_fraction", "magenta_chroma_fraction"]})
        return result
    rgb = a[:, :, :3][visible].astype(np.float32) / 255.0
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    weights = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    luminance = linear @ weights
    srgb_lum = rgb @ weights
    mn, mx = rgb.min(axis=1), rgb.max(axis=1)
    chroma = mx - mn
    result.update({
        "linear_luminance_mean": float(luminance.mean()),
        "linear_luminance_p90": float(np.percentile(luminance, 90)),
        "linear_luminance_p99": float(np.percentile(luminance, 99)),
        "srgb_luminance_mean": float(srgb_lum.mean()),
        "bright_fraction": float((srgb_lum > 0.85).mean()),
        "nearwhite_fraction": float(((mn > 0.93) & (chroma < 0.08)).mean()),
        "colorful_fraction": float(((chroma > 0.15) & (mx > 0.20)).mean()),
        "magenta_chroma_fraction": float(((rgb[:, 0] > 150/255) & (rgb[:, 2] > 130/255) & (rgb[:, 1] < 100/255)).mean()),
    })
    return {k: round(v, 7) if isinstance(v, float) else v for k, v in result.items()}


def font(size):
    for name in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def fit_label(draw, text, used_font, max_width=220):
    if draw.textlength(text, font=used_font) <= max_width:
        return text
    while text and draw.textlength(text + "…", font=used_font) > max_width:
        text = text[:-1]
    return text + "…"


def build_contacts(groups, asset_map, svg, output):
    eligible = {"formal", "prepared_copy", "derived", "source_or_matte"}
    priority = {"formal": 0, "source_or_matte": 1, "derived": 2, "prepared_copy": 3}
    buckets = {"formal": [], "sources_mattes": []}
    for group in groups:
        candidates = [asset_map[p] for p in group["paths"] if asset_map[p]["classification"] in eligible]
        if not candidates:
            continue
        representative = min(candidates, key=lambda a: (priority[a["classification"]], len(a["path"]), a["path"]))
        group["review_representative"] = representative["path"]
        bucket = "sources_mattes" if all(a["classification"] == "source_or_matte" for a in candidates) else "formal"
        group["contact_bucket"] = bucket
        buckets[bucket].append((group, representative))
    contacts = []
    title_font, label_font = font(20), font(12)
    cw, ch, header = 236, 214, 42
    for bucket, items in buckets.items():
        items.sort(key=lambda pair: pair[1]["path"])
        for page in range(math.ceil(len(items) / 60)):
            section = items[page*60:(page+1)*60]
            sheet = Image.new("RGB", (cw*6, header+ch*10), "#25282b")
            draw = ImageDraw.Draw(sheet)
            draw.text((10, 8), f"{bucket}  {page+1:02d}  |  Original exposure review / unique byte groups", fill="#ececec", font=title_font)
            mapping = []
            for cell, (group, entry) in enumerate(section):
                x, y = (cell%6)*cw+8, (cell//6)*ch+header
                tile = Image.new("RGB", (220, 160), "#808080")
                try:
                    sample, _ = read_sample(REPO / entry["path"], svg)
                    sample.thumbnail((220, 160), Image.Resampling.LANCZOS)
                    px, py = (220-sample.width)//2, (160-sample.height)//2
                    tile.paste(sample, (px, py), sample.getchannel("A"))
                    sample.close()
                except Exception as exc:
                    ImageDraw.Draw(tile).text((5, 60), "Preview unavailable", fill="white", font=label_font)
                    entry["contact_error"] = str(exc)
                sheet.paste(tile, (x, y))
                number = page*60+cell+1
                display_name = Path(entry["path"]).name
                display_name = display_name[:32] + "…" if len(display_name)>33 else display_name
                draw.text((x, y+164), fit_label(draw, f"{number:04d}  {group['id']}  {display_name}", label_font), fill="#ededed", font=label_font)
                m = entry.get("metrics", {})
                draw.text((x, y+181), f"W {m.get('nearwhite_fraction',0):.1%}  B {m.get('bright_fraction',0):.1%}  copies {len(group['paths'])}", fill="#b8c3cd", font=label_font)
                draw.text((x, y+197), fit_label(draw, entry["path"].split("/")[0], label_font), fill="#98a7b1", font=label_font)
                mapping.append({"number": number, "cell": cell, "row": cell//6, "column": cell%6, "group_id": group["id"], "path": entry["path"], "all_paths": group["paths"]})
            target = output / f"{bucket}-{page+1:02d}.jpg"
            sheet.save(target, quality=91, subsampling=0)
            sheet.close()
            contacts.append({"file": target.relative_to(REPO).as_posix(), "bucket": bucket, "page": page+1, "size": [cw*6, header+ch*10], "cells": mapping})
            print(f"contact {bucket} {page+1}: {len(section)} groups", flush=True)
    return {"schema": "qdao.exposure.contacts.v1", "purpose": "Audit-only thumbnails; never production grading inputs", "columns": 6, "rows": 10, "max_image_size": [220, 160], "transparent_background": "#808080", "unique_groups_covered": sum(len(s["cells"]) for s in contacts), "sheets": contacts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-contacts", action="store_true")
    args = parser.parse_args()
    output = PACKAGE / "review"
    output.mkdir(parents=True, exist_ok=True)
    paths = scan()
    svg = SvgRenderer()
    assets, digest_groups, metric_cache = [], defaultdict(list), {}
    try:
        for index, path in enumerate(paths):
            rel = path.relative_to(REPO).as_posix()
            classification, reason = classify(path)
            with path.open("rb") as source_file:
                digest = hashlib.file_digest(source_file, "sha256").hexdigest()
            record = {"path": rel, "sha256": digest, "bytes": path.stat().st_size, "extension": path.suffix.lower(), "classification": classification, "classification_reason": reason, "treatment_included": classification in {"formal", "source_or_matte", "derived", "prepared_copy"}}
            try:
                if digest in metric_cache:
                    record.update(metric_cache[digest])
                else:
                    sample, metadata = read_sample(path, svg)
                    record.update(metadata)
                    record["metrics"] = metrics(sample)
                    sample.close()
                    metric_cache[digest] = {k: v for k, v in record.items() if k in {"size", "mode", "alpha_range", "alpha_measurement", "frames", "sample_method", "metrics"}}
            except Exception as exc:
                record["read_error"] = str(exc)
            assets.append(record)
            digest_groups[digest].append(rel)
            if index % 50 == 0:
                print(f"audited {index+1}/{len(paths)}", flush=True)
        groups = [{"id": f"G{number:04d}", "sha256": digest, "paths": members, "count": len(members)} for number, (digest, members) in enumerate(digest_groups.items(), 1)]
        included = [a for a in assets if a["treatment_included"]]
        summary = {
            "total_visual_files": len(assets), "by_classification": dict(Counter(a["classification"] for a in assets)),
            "by_extension": dict(Counter(a["extension"] for a in assets)),
            "included_files": len(included), "included_unique_byte_groups": len({a["sha256"] for a in included}),
            "included_duplicate_redundant_files": len(included)-len({a["sha256"] for a in included}),
            "all_unique_byte_groups": len(groups), "all_duplicate_groups": sum(len(g["paths"])>1 for g in groups),
            "read_errors": [{"path": a["path"], "error": a["read_error"]} for a in assets if "read_error" in a],
            "included_with_nearwhite_over_10pct": sum(a.get("metrics", {}).get("nearwhite_fraction", 0)>0.10 for a in included),
            "included_with_bright_over_25pct": sum(a.get("metrics", {}).get("bright_fraction", 0)>0.25 for a in included),
        }
        inventory = {"schema": "qdao.exposure.inventory.v1", "created_utc": datetime.now(timezone.utc).isoformat(), "repo": str(REPO), "read_only_assets": True, "statistics_policy": {"visibility": "alpha >16; color statistics use only visible sampled pixels", "linear_luminance": "sRGB IEC inverse transfer, Rec.709 weights .2126 .7152 .0722", "bright_fraction": "display-encoded RGB weighted luminance >0.85", "nearwhite_fraction": "min(R,G,B)>0.93 and max-min<0.08, encoded RGB", "colorful_fraction": "encoded RGB max-min>0.15 and max>0.20", "magenta_chroma_fraction": "R>150/255 B>130/255 G<100/255", "warning": "Metrics indicate candidates for visual review, not proof of lost detail or overexposure"}, "infrastructure_excluded": sorted(INFRA), "generated_review_outputs_excluded": "qdao_exposure_refinement_v8/review", "summary": summary, "assets": assets, "groups": groups}
        if not args.no_contacts:
            contacts = build_contacts(groups, {a["path"]: a for a in assets}, svg, output)
            write_json(output / "contacts.json", contacts)
            summary["contact_sheets"] = len(contacts["sheets"])
            summary["contact_unique_groups_covered"] = contacts["unique_groups_covered"]
        write_json(PACKAGE / "inventory.json", inventory)
        print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    finally:
        svg.close()


if __name__ == "__main__":
    main()
