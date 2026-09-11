"""Rebuild SVG-derived composites after refine_library.py stage, before publish.

Reads processing.json and svg_raster_pairs.json. All candidates are rendered and
validated before any staged payload changes. Originals/backups are never written.
Every alias sharing an original SHA receives the same rebuilt staged bytes and
updated metadata. A small transaction journal permits recovery if interrupted
between staged-file replacements and the atomic processing.json update.

Run: python qdao_exposure_refinement_v8/tools/rebuild_staged_composites.py
     [--node installed-node] [--sharp installed-sharp-directory] [--force]
     [--repair-quantized-edges validation.json]
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from grade_core import VERSION as GRADE_VERSION, PRESETS as GRADE_PRESETS, grade_png_bytes

VERSION = "staged-svg-composites-1.2"
ROOT = Path(__file__).resolve().parents[2]
V8 = ROOT / "qdao_exposure_refinement_v8"
PROCESSING = V8 / "processing.json"
MAPPING = V8 / "svg_raster_pairs.json"
REBUILT = V8 / "review" / "rebuilt"
REPORT = REBUILT / "composite_rebuild_report.json"
JOURNAL = REBUILT / "composite_rebuild_transaction.json"
LINEAR = np.where(np.arange(256) / 255 <= .04045, np.arange(256) / 255 / 12.92,
                  ((np.arange(256) / 255 + .055) / 1.055) ** 2.4)
WEIGHTS = np.array([.2126, .7152, .0722])
INTEGER_WEIGHTS = np.array([2126, 7152, 722], dtype=np.int32)
EDGE_POLICY = {"original_alpha_min": 1, "original_alpha_max": 4,
               "original_max_rgb_times_alpha_max": 255,
               "action": "preserve_exact_original_rgb",
               "reason": "At most one code value per premultiplied channel; prevent edge quantization color loss"}

# Exact historical build_layers.mjs composition; source paths arrive as JSON via
# stdin. No shell interpolation, downloads, image generation API, or input writes.
SCREEN_NODE = r"""
const fs=require('node:fs/promises'),path=require('node:path'),os=require('node:os');
(async()=>{
 let text='';for await(const chunk of process.stdin)text+=chunk;
 const request=JSON.parse(text);let sharp;
 for(const candidate of [request.sharp,'sharp',path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp')].filter(Boolean)){
  try{sharp=require(candidate);break;}catch{}
 }
 if(!sharp)throw new Error('Existing sharp package is unavailable');sharp.cache(false);
 const render=async(svg)=>sharp(Buffer.from(await fs.readFile(svg,'utf8'))).png({compressionLevel:9}).toBuffer();
 for(const job of request.jobs){
  const vector=await render(job.base_svg);
  let heroImage=sharp(job.hero_png);
  if(!job.hero_prepared)heroImage=heroImage.resize(310,310);
  const hero=await heroImage.png().toBuffer();
  const base=await sharp(vector).composite([{input:hero,left:2042,top:30}]).png({compressionLevel:9}).toBuffer();
  const controls=await render(job.controls_svg);
  const combined=await sharp(base).composite([{input:controls}]).png({compressionLevel:9}).toBuffer();
  const labels=await render(job.labels_svg);
  const fog=Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1080" viewBox="0 0 2560 1080" role="img"><rect width="2560" height="1080" fill="#EFF5DA" opacity=".25"/></svg>');
  const screen=await sharp(job.city_png).composite([{input:fog},{input:combined},{input:labels}]).removeAlpha().png({compressionLevel:9}).toBuffer();
  await fs.mkdir(path.dirname(job.output),{recursive:true});await fs.writeFile(job.output,screen);
  console.log(JSON.stringify({id:job.id,output:job.output,bytes:screen.length}));
 }
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
"""


RESIZE_NODE = r"""
const fs=require('node:fs/promises'),path=require('node:path'),os=require('node:os');
(async()=>{
 let text='';for await(const chunk of process.stdin)text+=chunk;
 const request=JSON.parse(text);let sharp;
 for(const candidate of [request.sharp,'sharp',path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp')].filter(Boolean)){
  try{sharp=require(candidate);break;}catch{}
 }
 if(!sharp)throw new Error('Existing sharp package is unavailable');sharp.cache(false);
 for(const job of request.jobs){
  const output=await sharp(job.input).resize(job.width,job.height).png().toBuffer();
  await fs.mkdir(path.dirname(job.output),{recursive:true});await fs.writeFile(job.output,output);
 }
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
"""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(json_bytes(value))
    os.replace(temporary, path)


def safe(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f"Path outside {base}: {relative}")
    return path


def staged_target(relative):
    target = safe(V8, relative)
    if not target.is_relative_to((V8 / "staged").resolve()):
        raise ValueError(f"Stage target must stay in v8/staged, never backups or originals: {relative}")
    return target


def validate_png(original_path, output_path):
    """Exact shape/alpha/hidden-RGB contracts plus strict per-pixel luminance.

    Both sRGB-weighted and linear-light brightness must never increase at any
    visible pixel. Newly crushed pixels use the general verifier's 8-to-1 sRGB
    code-value thresholds. We reject even quantization-only increases; there
    is no post-render min/clamp that could conceal a wrong composition recipe.
    """
    result = {"original": str(original_path), "output": str(output_path),
              "alpha_different_pixels": 0, "hidden_rgb_different_pixels": 0,
              "brighter_srgb_pixels": 0, "brighter_linear_pixels": 0, "newly_crushed_pixels": 0,
              "channel_increase_pixels": 0, "max_channel_increase": 0,
              "max_srgb_increase_codevalues": 0.0, "max_linear_increase": 0.0,
              "changed_rgb_pixels": 0, "first_brightness_increases": []}
    with Image.open(original_path) as original, Image.open(output_path) as output:
        result.update(original_size=list(original.size), output_size=list(output.size),
                      original_mode=original.mode, output_mode=output.mode)
        if original.size != output.size or original.mode != output.mode or original.mode not in ("RGB", "RGBA"):
            result.update(status="failed", error="Canvas or RGB/RGBA mode changed")
            return result
        for top in range(0, original.height, 128):
            box = (0, top, original.width, min(top + 128, original.height))
            left = np.asarray(original.crop(box)); right = np.asarray(output.crop(box))
            if original.mode == "RGBA":
                result["alpha_different_pixels"] += int(np.count_nonzero(left[..., 3] != right[..., 3]))
                visible = left[..., 3] != 0
                result["hidden_rgb_different_pixels"] += int(np.count_nonzero(np.any(left[..., :3] != right[..., :3], axis=2) & ~visible))
            else:
                visible = np.ones(left.shape[:2], dtype=bool)
            left_rgb = left[..., :3]; right_rgb = right[..., :3]
            difference = right_rgb.astype(np.int32) - left_rgb.astype(np.int32)
            srgb_difference = difference @ INTEGER_WEIGHTS
            old_srgb = left_rgb.astype(np.int32) @ INTEGER_WEIGHTS
            new_srgb = right_rgb.astype(np.int32) @ INTEGER_WEIGHTS
            result["newly_crushed_pixels"] += int(np.count_nonzero(visible & (old_srgb >= 80000) & (new_srgb <= 10000)))
            linear_difference = (LINEAR[right_rgb] - LINEAR[left_rgb]) @ WEIGHTS
            brighter_srgb = (srgb_difference > 0) & visible
            brighter_linear = (linear_difference > 1e-12) & visible
            brighter = brighter_srgb | brighter_linear
            result["brighter_srgb_pixels"] += int(np.count_nonzero(brighter_srgb))
            result["brighter_linear_pixels"] += int(np.count_nonzero(brighter_linear))
            result["channel_increase_pixels"] += int(np.count_nonzero(np.any(difference > 0, axis=2) & visible))
            result["changed_rgb_pixels"] += int(np.count_nonzero(np.any(difference != 0, axis=2)))
            result["max_channel_increase"] = max(result["max_channel_increase"], int(np.max(difference)))
            result["max_srgb_increase_codevalues"] = max(result["max_srgb_increase_codevalues"], float(np.max(srgb_difference)) / 10000)
            result["max_linear_increase"] = max(result["max_linear_increase"], float(np.max(linear_difference)))
            if len(result["first_brightness_increases"]) < 8 and brighter.any():
                ys, xs = np.nonzero(brighter)
                for y, x in zip(ys[:8], xs[:8]):
                    result["first_brightness_increases"].append({"x": int(x), "y": int(y + top), "before_rgb": left_rgb[y, x].tolist(), "after_rgb": right_rgb[y, x].tolist()})
                    if len(result["first_brightness_increases"]) == 8:
                        break
    keys = ("alpha_different_pixels", "hidden_rgb_different_pixels", "brighter_srgb_pixels", "brighter_linear_pixels", "newly_crushed_pixels")
    result["status"] = "passed" if all(result[key] == 0 for key in keys) else "failed"
    if result["status"] == "failed":
        result["error"] = "Rebuild changed transparency, brightened pixels, or newly crushed visible pixels; no clamping applied"
    return result



def preserve_quantized_edges(original_path, input_path, output_path):
    """Keep exact original colors only in diagnosed sub-one-code-value edges.

    RGB is unassociated in PNG. At alpha 1, one premultiplied code value becomes
    255 after unpremultiplication; at alpha 2/4 it becomes 127/63. Filtering the
    graded source can round that last contribution to zero. This narrow original
    color protection keeps edge hue without changing geometry, alpha, hidden RGB,
    or ordinary highlights. It does not relax any luminance acceptance threshold.
    """
    stats = {"policy": EDGE_POLICY, "protected_changed_pixels": 0,
             "alpha_histogram": {}, "max_premultiplied_channel_delta_codevalues": 0.0}
    with Image.open(original_path) as original, Image.open(input_path) as rendered:
        if original.size != rendered.size or original.mode != rendered.mode:
            raise RuntimeError("Quantized-edge protection cannot repair a canvas/mode mismatch")
        if original.mode != "RGBA":
            if input_path != output_path:
                shutil.copyfile(input_path, output_path)
            return stats
        result = rendered.copy()
        for top in range(0, original.height, 128):
            box = (0, top, original.width, min(top + 128, original.height))
            old = np.asarray(original.crop(box)); new = np.asarray(rendered.crop(box)).copy()
            if np.any(old[..., 3] != new[..., 3]):
                raise RuntimeError("Quantized-edge protection requires unchanged original alpha")
            alpha = old[..., 3].astype(np.int32)
            mask = ((alpha >= EDGE_POLICY["original_alpha_min"])
                    & (alpha <= EDGE_POLICY["original_alpha_max"])
                    & (old[..., :3].max(axis=-1).astype(np.int32) * alpha <= EDGE_POLICY["original_max_rgb_times_alpha_max"])
                    & np.any(old[..., :3] != new[..., :3], axis=-1))
            count = int(np.count_nonzero(mask))
            if not count:
                continue
            stats["protected_changed_pixels"] += count
            delta = np.abs(old[..., :3].astype(np.int32) - new[..., :3].astype(np.int32)) * alpha[..., None]
            stats["max_premultiplied_channel_delta_codevalues"] = max(stats["max_premultiplied_channel_delta_codevalues"], float(delta[mask].max()) / 255)
            for a, n in zip(*np.unique(alpha[mask], return_counts=True)):
                key = str(int(a)); stats["alpha_histogram"][key] = stats["alpha_histogram"].get(key, 0) + int(n)
            new[..., :3][mask] = old[..., :3][mask]
            result.paste(Image.fromarray(new), box)
        if not stats["protected_changed_pixels"]:
            if input_path != output_path:
                shutil.copyfile(input_path, output_path)
            return stats
        if stats["max_premultiplied_channel_delta_codevalues"] > 1:
            raise RuntimeError("Edge change exceeds the diagnosed one-code-value premultiplication bound")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_path.with_name(output_path.name + ".edge-protection.tmp")
        metadata = {key: rendered.info[key] for key in ("icc_profile", "dpi", "exif") if key in rendered.info}
        result.save(temporary, format="PNG", compress_level=6, **metadata)
        os.replace(temporary, output_path)
    return stats


def recover_transaction():
    """Finish only this script's prepared transaction, after checking every hash."""
    if not JOURNAL.exists():
        return False
    journal = read_json(JOURNAL)
    if journal.get("status") != "prepared":
        return False
    processing_sha = digest(PROCESSING)
    if processing_sha not in (journal["processing_before_sha256"], journal["processing_after_sha256"]):
        raise RuntimeError("processing.json changed independently of the pending rebuild transaction")
    for operation in journal["operations"]:
        candidate = safe(V8, operation["candidate"])
        target = staged_target(operation["target"])
        if not candidate.is_relative_to(REBUILT.resolve()):
            raise ValueError("Transaction candidate is outside the rebuild output directory")
        if digest(candidate) != operation["after_sha256"]:
            raise RuntimeError(f"Pending rebuild candidate changed: {candidate}")
        if digest(target) not in (operation["before_sha256"], operation["after_sha256"]):
            raise RuntimeError(f"Staged file changed outside the pending rebuild: {target}")
    for operation in journal["operations"]:
        candidate = safe(V8, operation["candidate"])
        target = staged_target(operation["target"])
        if digest(target) == operation["after_sha256"]:
            continue
        temporary = target.with_name(target.name + ".composite-rebuild.tmp")
        shutil.copyfile(candidate, temporary)
        os.replace(temporary, target)
    write_json(PROCESSING, journal["updated_processing"])
    if digest(PROCESSING) != journal["processing_after_sha256"]:
        raise RuntimeError("Rebuild processing manifest write did not match prepared bytes")
    report = journal["report"]
    report.update(status="completed", completed_utc=utc_now(), staged_payloads_written=True)
    write_json(REPORT, report)
    journal.update(status="committed", committed_utc=utc_now())
    write_json(JOURNAL, journal)
    return True


def rebuild_staged_composites(*, node="node", sharp=None, force=False):
    if recover_transaction():
        return read_json(REPORT)
    processing_before_sha = digest(PROCESSING)
    plan = read_json(PROCESSING)
    if plan.get("status") != "staged" or any(record.get("status") != "staged" for record in plan["records"]):
        raise RuntimeError("Run only after every refine_library.py stage record is staged, before publish")
    if Path(plan.get("workspace_root", ROOT)).resolve() != ROOT.resolve():
        raise RuntimeError("processing.json workspace_root differs from this module's repository")
    by_path = {record["path"]: record for record in plan["records"]}
    by_sha = defaultdict(list)
    for record in plan["records"]:
        by_sha[record["original_sha256"]].append(record)
    mapping = read_json(MAPPING)
    target_paths = [pair["png"] for pair in mapping["pairs"]]
    screen_recipe = next(item for item in mapping["downstream_not_simple_svg_pairs"] if "pngs" in item)
    screen_paths = screen_recipe["pngs"]
    target_paths.extend(screen_paths)
    if len(target_paths) != 25 or len(screen_paths) != 4:
        raise RuntimeError("Expected the reviewed 21 SVG-derived PNG candidates and 4 legacy RGB screen paths")
    requested_hashes = {by_path[path]["original_sha256"] for path in target_paths}
    if not force and plan.get("composites_rebuild", {}).get("version") == VERSION:
        for original_sha in requested_hashes:
            for record in by_sha[original_sha]:
                if not record.get("composite_rebuilt") or digest(staged_target(record["staged"])) != record["output_sha256"]:
                    raise RuntimeError("A previously rebuilt staged payload or alias record changed")
        return read_json(REPORT)
    verified = set()

    def source(path, *, original=False):
        if path not in by_path:
            raise RuntimeError(f"Rebuild dependency is absent from processing.json: {path}")
        record = by_path[path]
        field = "backup" if original else "staged"
        expected = record["original_sha256"] if original else record["output_sha256"]
        actual_path = safe(V8, record[field]) if original else staged_target(record[field])
        key = (actual_path, expected)
        if key not in verified:
            if not actual_path.is_file() or digest(actual_path) != expected:
                raise RuntimeError(f"Rebuild input hash mismatch: {actual_path}")
            verified.add(key)
        return actual_path

    # Preflight every target alias and every original contract before rendering.
    for original_sha in requested_hashes:
        aliases = by_sha[original_sha]
        if len({r["output_sha256"] for r in aliases}) != 1:
            raise RuntimeError(f"Existing alias outputs disagree for original SHA {original_sha}")
        for record in aliases:
            source(record["path"])
            source(record["path"], original=True)
    jobs = []
    for pair in mapping["pairs"]:
        job = copy.deepcopy(pair)
        job["svg"] = source(pair["svg"]).as_posix()
        job["png"] = source(pair["png"], original=True).as_posix()
        job["output"] = (REBUILT / "svg_pairs" / pair["png"]).as_posix()
        for layer in job.get("overlays", []):
            field = "svg" if "svg" in layer else "png"
            layer[field] = source(layer[field]).as_posix()
        jobs.append(job)
    REBUILT.mkdir(parents=True, exist_ok=True)
    staged_mapping = REBUILT / "staged_svg_mapping.json"
    write_json(staged_mapping, {"schema": "qdao.svg.raster_pairs.v1", "root": ROOT.as_posix(), "pairs": jobs})
    report = {"schema": "qdao.composite_rebuild.v1", "version": VERSION, "started_utc": utc_now(),
              "status": "rendering", "formal_assets_written": False, "originals_and_backups_written": False,
              "requested_target_paths": target_paths, "requested_target_count": len(target_paths),
              "requested_original_hash_groups": len(requested_hashes), "checks": [], "rebuilt_groups": []}
    write_json(REPORT, report)
    try:
        if plan.get("algorithm") != GRADE_VERSION or plan.get("presets") != GRADE_PRESETS:
            raise RuntimeError("Frozen plan grading policy differs from the current grader; refusing to approximate raster overlays")
        # Lanczos includes negative lobes: grading first can raise neighbouring
        # dark samples during resize and amplify edge RGB on unpremultiplication.
        # Preserve the exact existing resampling/geometry, then apply the same
        # frozen preset once at the final overlay resolution. Never clamp a
        # rebuilt composite or change its resampling kernel to hide the issue.
        resize_requests = {}
        def request_overlay(path, width, height):
            record = by_path[path]
            key = (record["original_sha256"], width, height, record["preset"], bool(record["protect_chroma"]))
            if key not in resize_requests:
                stem = f'{record["original_sha256"]}_{width}x{height}_{record["preset"]}'
                resize_requests[key] = {"input": source(path, original=True).as_posix(), "width": width, "height": height,
                    "output": (REBUILT / "resized_raster_overlays" / (stem + "_original.png")).as_posix(),
                    "graded_output": (REBUILT / "resized_raster_overlays" / (stem + "_graded.png")).as_posix(),
                    "path": path, "preset": record["preset"], "protect_chroma": record["protect_chroma"]}
            return resize_requests[key]
        for pair, job in zip(mapping["pairs"], jobs):
            for original_layer, staged_layer in zip(pair.get("overlays", []), job.get("overlays", [])):
                if "png" not in original_layer:
                    continue
                if "width" not in original_layer or "height" not in original_layer:
                    raise RuntimeError("Raster overlay requires reviewed final width and height")
                prepared = request_overlay(original_layer["png"], original_layer["width"], original_layer["height"])
                staged_layer["png"] = prepared["graded_output"]
                # It is already at the exact final size; do not resize twice.
                staged_layer.pop("width", None); staged_layer.pop("height", None)
        screen_hero = request_overlay("qdao_chibi_game_pack_v4/hero-transparent_1024.png", 310, 310)
        subprocess.run([node, "-e", RESIZE_NODE], input=json.dumps({"sharp": sharp, "jobs": list(resize_requests.values())}), text=True, cwd=ROOT, check=True)
        report["raster_overlay_preparation"] = []
        for prepared in resize_requests.values():
            original_resized = Path(prepared["output"]); graded_resized = Path(prepared["graded_output"])
            graded_resized.write_bytes(grade_png_bytes(original_resized.read_bytes(), prepared["preset"], prepared["protect_chroma"]))
            overlay_check = validate_png(original_resized, graded_resized)
            if overlay_check["status"] != "passed":
                raise RuntimeError("Final-resolution raster overlay failed its exact original contract")
            report["raster_overlay_preparation"].append({**prepared, "method": "original_existing_kernel_resize_then_same_frozen_preset", "check": overlay_check})
        write_json(staged_mapping, {"schema": "qdao.svg.raster_pairs.v1", "root": ROOT.as_posix(), "pairs": jobs})
        command = [node, str(V8 / "tools" / "render_svg_pairs.mjs"), "--mapping", str(staged_mapping), "--report", str(REBUILT / "svg_render_report.json")]
        if sharp:
            command.extend(["--sharp", sharp])
        subprocess.run(command, cwd=ROOT, check=True)

        # The four legacy RGB paths are exact aliases. Check that before choosing
        # their one shared render, and verify the original historical recipe.
        if len({by_path[path]["original_sha256"] for path in screen_paths}) != 1:
            raise RuntimeError("The four legacy RGB screen originals are no longer identical aliases")
        dependencies = {
            "base_svg": "q_daoist_login_ui_uncropped_highres_final_layers/native_q5/base.svg",
            "controls_svg": "q_daoist_login_ui_uncropped_highres_final_layers/native_q5/controls.svg",
            "labels_svg": "q_daoist_login_ui_uncropped_highres_final_layers/native_q5/labels.svg",
            "hero_png": "qdao_chibi_game_pack_v4/hero-transparent_1024.png",
            "city_png": "qdao_chibi_game_pack_v4/main-city_2560x1080.png",
        }
        screen_jobs = []
        for original in (True, False):
            job = {name: source(path, original=original).as_posix() for name, path in dependencies.items()}
            job.update(id="original_recipe_check" if original else "graded_screen", output=(REBUILT / ("legacy_screen_original_check.png" if original else "legacy_screen_rebuilt.png")).as_posix())
            if not original:
                job.update(hero_png=screen_hero["graded_output"], hero_prepared=True)
            screen_jobs.append(job)
        subprocess.run([node, "-e", SCREEN_NODE], input=json.dumps({"sharp": sharp, "jobs": screen_jobs}), text=True, cwd=ROOT, check=True)
        original_screen = source(screen_paths[0], original=True)
        baseline = validate_png(original_screen, Path(screen_jobs[0]["output"]))
        baseline["purpose"] = "Original 2560 RGB historical recipe must reproduce original pixels exactly"
        baseline["exact_pixels"] = baseline["status"] == "passed" and baseline["changed_rgb_pixels"] == 0
        report["legacy_screen_original_recipe_check"] = baseline
        if not baseline["exact_pixels"]:
            raise RuntimeError("Historical legacy RGB recipe did not reproduce the original; refusing to substitute a different composition")

        candidates = []
        for pair, job in zip(mapping["pairs"], jobs):
            recipe = {"type": "svg_render", "id": pair["id"], "svg": pair["svg"],
                      "overlays": pair.get("overlays", []), "dimensions_from_original_png": True,
                      "source_presets_reused": True, "alpha_and_hidden_rgb_from_original": True,
                      "raster_overlay_order": "original_existing_kernel_resize_then_same_frozen_preset"}
            candidates.append((pair["png"], Path(job["output"]), recipe))
        for path in screen_paths:
            recipe = {"type": "legacy_rgb_server_screen", "dependencies": dependencies,
                      "size": [2560, 1080], "hero_rect": [2042, 30, 310, 310],
                      "veil": {"color": "#EFF5DA", "opacity": .25},
                      "order": ["city", "veil", "base_with_hero_and_controls", "unchanged_labels"],
                      "source_presets_reused": True, "original_recipe_pixel_exact_verified": True,
                      "raster_overlay_order": "original_existing_kernel_resize_then_same_frozen_preset"}
            candidates.append((path, Path(screen_jobs[1]["output"]), recipe))
        selected_by_sha = {}
        validation_cache = {}
        protected_candidates = {}
        report["quantized_edge_protection"] = []
        for path, candidate, recipe in candidates:
            original_sha = by_path[path]["original_sha256"]
            if candidate not in protected_candidates:
                edge_stats = preserve_quantized_edges(source(path, original=True), candidate, candidate)
                protected_candidates[candidate] = edge_stats
                report["quantized_edge_protection"].append({"target": path, **edge_stats})
            recipe["quantized_edge_protection"] = protected_candidates[candidate]
            output_sha = digest(candidate)
            key = (original_sha, output_sha)
            if key not in validation_cache:
                validation_cache[key] = validate_png(source(path, original=True), candidate)
            check = {"target": path, "original_sha256": original_sha, "output_sha256": output_sha, **validation_cache[key]}
            report["checks"].append(check)
            if check["status"] != "passed":
                continue
            if original_sha in selected_by_sha and selected_by_sha[original_sha]["output_sha256"] != output_sha:
                raise RuntimeError(f"Different recipes produced different bytes for aliases of {path}")
            entry = selected_by_sha.setdefault(original_sha, {"candidate": candidate, "output_sha256": output_sha, "recipes": []})
            if recipe not in entry["recipes"]:
                entry["recipes"].append(recipe)
        failures = [check for check in report["checks"] if check["status"] != "passed"]
        if failures:
            report.update(status="failed_validation", failure_count=len(failures), staged_payloads_written=False,
                          error="Candidate brightness or transparency checks failed; all original staged payloads remain intact; no clamping applied")
            write_json(REPORT, report)
            raise RuntimeError(f"{len(failures)} composite candidates failed; inspect {REPORT}")
        if set(selected_by_sha) != requested_hashes:
            raise RuntimeError("Not every requested original hash has a validated candidate")
        updated_plan = copy.deepcopy(plan)
        operations = []
        seen_targets = set()
        for record in updated_plan["records"]:
            entry = selected_by_sha.get(record["original_sha256"])
            if entry is None:
                continue
            staged_path = staged_target(record["staged"])
            if staged_path not in seen_targets:
                operations.append({"target": staged_path.relative_to(V8).as_posix(),
                                   "candidate": entry["candidate"].relative_to(V8).as_posix(),
                                   "before_sha256": record["output_sha256"], "after_sha256": entry["output_sha256"]})
                seen_targets.add(staged_path)
            record.update(output_sha256=entry["output_sha256"], changed=entry["output_sha256"] != record["original_sha256"],
                          composite_rebuilt=True, recipe={"version": VERSION, "sources": entry["recipes"]})
        for original_sha, entry in selected_by_sha.items():
            report["rebuilt_groups"].append({"original_sha256": original_sha, "output_sha256": entry["output_sha256"],
                                              "aliases": [r["path"] for r in by_sha[original_sha]],
                                              "candidate": entry["candidate"].relative_to(V8).as_posix(), "recipes": entry["recipes"]})
        updated_plan["summary"] = {**updated_plan.get("summary", {}), "total_records": len(updated_plan["records"]),
                                   "changed": sum(r["changed"] for r in updated_plan["records"]),
                                   "by_preset": dict(Counter(r["preset"] for r in updated_plan["records"]))}
        updated_plan["composites_rebuild"] = {"version": VERSION, "prepared_utc": utc_now(), "requested_paths": len(target_paths),
                                               "original_hash_groups": len(selected_by_sha), "stage_files": len(operations),
                                               "records_including_aliases": sum(len(by_sha[s]) for s in selected_by_sha),
                                               "report": REPORT.relative_to(V8).as_posix()}
        report.update(status="prepared", staged_payloads_written=False, stage_files_to_replace=len(operations),
                      updated_records_including_aliases=updated_plan["composites_rebuild"]["records_including_aliases"])
        if digest(PROCESSING) != processing_before_sha:
            raise RuntimeError("processing.json changed while composites were rendering; refusing to overwrite concurrent work")
        journal = {"version": VERSION, "status": "prepared", "processing_before_sha256": processing_before_sha,
                   "processing_after_sha256": hashlib.sha256(json_bytes(updated_plan)).hexdigest(),
                   "operations": operations, "updated_processing": updated_plan, "report": report}
        write_json(JOURNAL, journal)
        recover_transaction()
        final_report = read_json(REPORT)
        final_report["staged_payloads_written"] = True
        write_json(REPORT, final_report)
        return final_report
    except Exception as error:
        # A prepared journal is deliberately retained for safe hash-checked
        # recovery. Validation/render failures before it do not change stages.
        if not (JOURNAL.exists() and read_json(JOURNAL).get("status") == "prepared"):
            report.setdefault("error", str(error))
            if report["status"] not in ("failed_validation",):
                report["status"] = "failed"
            write_json(REPORT, report)
        raise



def repair_staged_quantized_edges(validation_path):
    """Repair only validated, diagnosed composite stages; leave all others exact."""
    if recover_transaction():
        return read_json(REPORT)
    before_sha = digest(PROCESSING)
    plan = read_json(PROCESSING)
    if plan.get("status") != "staged" or any(r.get("status") != "staged" for r in plan["records"]):
        raise RuntimeError("Edge repair requires a fully staged, unpublished plan")
    if Path(plan.get("workspace_root", ROOT)).resolve() != ROOT.resolve():
        raise RuntimeError("Edge repair workspace differs from this repository")
    validation = read_json(validation_path)
    by_stage = {staged_target(r["staged"]): r for r in plan["records"]}
    by_sha = defaultdict(list)
    for record in plan["records"]:
        by_sha[record["original_sha256"]].append(record)
    selected = {}
    for error in validation.get("errors", []):
        if error.get("check") != "newly_crushed_pixels":
            continue
        stage = safe(ROOT, error["path"])
        if stage not in by_stage:
            raise RuntimeError(f"Reported stage is not present in processing.json: {stage}")
        record = by_stage[stage]
        if not record.get("composite_rebuilt"):
            raise RuntimeError("Edge repair is restricted to this module's reconstructed composites")
        selected[record["original_sha256"]] = record
    if not selected:
        raise RuntimeError("No composite newly-crushed failures in the supplied validation report")
    previous_report = read_json(REPORT)
    for current in (REPORT, JOURNAL):
        if current.exists():
            previous_version = read_json(current).get("version", "unknown")
            archived = current.with_name(current.stem + "_" + previous_version + current.suffix)
            if not archived.exists():
                shutil.copyfile(current, archived)
    report = {"schema": "qdao.composite_rebuild.v1", "version": VERSION,
              "operation": "incremental_quantized_edge_protection", "started_utc": utc_now(),
              "status": "preparing", "formal_assets_written": False, "originals_and_backups_written": False,
              "validation_input": str(validation_path), "prior_rebuild_version": previous_report.get("version"),
              "policy": EDGE_POLICY, "checks": [], "rebuilt_groups": [],
              "requested_target_count": len(selected), "requested_original_hash_groups": len(selected),
              "staged_payloads_written": False}
    selected_outputs = {}
    from verify_exposure import image_metrics, DEFAULT_POLICY
    for original_sha, representative in selected.items():
        aliases = by_sha[original_sha]
        if len({r["output_sha256"] for r in aliases}) != 1:
            raise RuntimeError(f"Alias stages disagree before edge repair: {original_sha}")
        for record in aliases:
            if digest(staged_target(record["staged"])) != record["output_sha256"]:
                raise RuntimeError("Stage changed before incremental repair")
            if digest(safe(V8, record["backup"])) != original_sha:
                raise RuntimeError("Original backup hash mismatch")
        original = safe(V8, representative["backup"])
        stage = staged_target(representative["staged"])
        before_check = validate_png(original, stage)
        for field in ("alpha_different_pixels", "hidden_rgb_different_pixels", "brighter_srgb_pixels", "brighter_linear_pixels"):
            if before_check[field]:
                raise RuntimeError(f"Edge repair cannot mask unrelated failed contract: {field}")
        if not before_check["newly_crushed_pixels"]:
            raise RuntimeError("Validation input is stale: this stage has no newly-crushed pixels")
        directory = REBUILT / "edge_repair_v1.2"
        before_copy = directory / "before" / (original_sha + ".png")
        before_copy.parent.mkdir(parents=True, exist_ok=True)
        if not before_copy.exists():
            shutil.copyfile(stage, before_copy)
        if digest(before_copy) != representative["output_sha256"]:
            raise RuntimeError("Preserved pre-repair evidence hash differs from current stage")
        candidate = directory / "after" / (original_sha + ".png")
        edge_stats = preserve_quantized_edges(original, stage, candidate)
        after_check = validate_png(original, candidate)
        metrics = image_metrics(original, candidate, DEFAULT_POLICY)
        verification_ok = (all(metrics[k] == 0 for k in ("alpha_changed_pixels", "hidden_rgb_changed_pixels", "luminance_increased_pixels", "newly_crushed_pixels"))
                           and (metrics["shadow_mean_drop"] is None or metrics["shadow_mean_drop"] <= DEFAULT_POLICY["shadow_max_mean_drop"] + 1e-7)
                           and (metrics["shadow_retention"] is None or metrics["shadow_retention"] >= DEFAULT_POLICY["shadow_retention_min"] - 1e-7))
        check = {"target": representative["path"], "original_sha256": original_sha,
                 "before_output_sha256": representative["output_sha256"], "output_sha256": digest(candidate),
                 "before_check": before_check, "edge_protection": edge_stats,
                 "after_check": after_check, "generic_metrics": metrics,
                 "status": "passed" if after_check["status"] == "passed" and verification_ok else "failed"}
        report["checks"].append(check)
        if check["status"] != "passed":
            report.update(status="failed_validation", error="Edge repair failed unchanged strict and general checks")
            write_json(REPORT, report)
            raise RuntimeError("Candidate failed; no stage files changed")
        selected_outputs[original_sha] = {"candidate": candidate, "output_sha256": check["output_sha256"], "edge_protection": edge_stats}
    updated = copy.deepcopy(plan)
    operations = []; seen = set(); updated_count = 0
    for record in updated["records"]:
        entry = selected_outputs.get(record["original_sha256"])
        if entry is None:
            continue
        if record["staged"] not in seen:
            operations.append({"target": record["staged"], "candidate": entry["candidate"].relative_to(V8).as_posix(),
                               "before_sha256": record["output_sha256"], "after_sha256": entry["output_sha256"]})
            seen.add(record["staged"])
        record.update(output_sha256=entry["output_sha256"], changed=entry["output_sha256"] != record["original_sha256"])
        record["recipe"] = {**record["recipe"], "version": VERSION, "quantized_edge_protection": entry["edge_protection"]}
        updated_count += 1
    for original_sha, entry in selected_outputs.items():
        report["rebuilt_groups"].append({"original_sha256": original_sha, "output_sha256": entry["output_sha256"],
                                       "aliases": [r["path"] for r in by_sha[original_sha]],
                                       "candidate": entry["candidate"].relative_to(V8).as_posix(), "edge_protection": entry["edge_protection"]})
    updated["composites_rebuild"] = {**updated.get("composites_rebuild", {}), "version": VERSION,
                                      "incremental_edge_repair": {"prepared_utc": utc_now(), "stage_files": len(operations),
                                                                  "records_including_aliases": updated_count, "report": REPORT.relative_to(V8).as_posix()}}
    report.update(status="prepared", stage_files_to_replace=len(operations), updated_records_including_aliases=updated_count,
                  newly_crushed_before=sum(c["before_check"]["newly_crushed_pixels"] for c in report["checks"]),
                  newly_crushed_after=sum(c["after_check"]["newly_crushed_pixels"] for c in report["checks"]),
                  total_protected_edge_pixels=sum(c["edge_protection"]["protected_changed_pixels"] for c in report["checks"]))
    if digest(PROCESSING) != before_sha:
        raise RuntimeError("processing.json changed concurrently; refusing to overwrite it")
    journal = {"version": VERSION, "status": "prepared", "processing_before_sha256": before_sha,
               "processing_after_sha256": hashlib.sha256(json_bytes(updated)).hexdigest(),
               "operations": operations, "updated_processing": updated, "report": report}
    write_json(JOURNAL, journal)
    recover_transaction()
    return read_json(REPORT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", default=shutil.which("node") or "node")
    parser.add_argument("--sharp")
    parser.add_argument("--force", action="store_true", help="Rebuild again using current staged source dependencies")
    parser.add_argument("--repair-quantized-edges", type=Path, metavar="VALIDATION_JSON", help="Update only composite stages with diagnosed newly-crushed failures")
    args = parser.parse_args()
    report = (repair_staged_quantized_edges(args.repair_quantized_edges) if args.repair_quantized_edges
              else rebuild_staged_composites(node=args.node, sharp=args.sharp, force=args.force))
    print(json.dumps({key: report.get(key) for key in ("status", "requested_target_count", "requested_original_hash_groups", "stage_files_to_replace", "updated_records_including_aliases")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
