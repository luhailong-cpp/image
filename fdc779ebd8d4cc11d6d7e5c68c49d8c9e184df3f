#!/usr/bin/env python3
"""Independently verify v8 exposure outputs against immutable source backups.

Requires Pillow and NumPy. This module never writes images or metadata manifests.
Only main() writes validation.json. Importing it is safe before processing exists.

Required processing.json record fields:
    path, original_sha256, output_sha256, backup, changed, kind, preset
path is relative to workspace_root; backup is relative to the v8 directory.
Optional top-level fields: workspace_root, validation_policy, tile_manifests,
atlas_specs. A record's validation_policy overrides the top-level policy.

tile_manifests accepts paths or objects with manifest and master paths relative
to workspace_root. atlas_specs accepts objects with json and optional xml paths.
The known Tianyong map and FairyGUI atlas are discovered when those lists are
omitted. Existing atlas discrepancies are measured against backups; only newly
introduced mismatching pixels fail. Map crops must match their master exactly.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
from collections import defaultdict
from contextlib import nullcontext
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image


V8 = Path(__file__).resolve().parents[1]
WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
SRGB = np.arange(256, dtype=np.float32) / 255.0
LINEAR = np.where(SRGB <= 0.04045, SRGB / 12.92,
                  ((SRGB + 0.055) / 1.055) ** 2.4)
DEFAULT_POLICY = {
    "luminance_increase_tolerance": 1.0 / 255.0,
    "highlight_threshold": 0.75,
    "highlight_min_drop": 0.0,
    "shadow_threshold": 0.20,
    "shadow_max_mean_drop": 0.04,
    "shadow_retention_min": 0.60,
    "crush_source_threshold": 8.0 / 255.0,
    "crush_output_threshold": 1.0 / 255.0,
}
REQUIRED = {"path", "original_sha256", "output_sha256", "backup", "changed",
            "kind", "preset"}
PNG_URI = re.compile(r"^data:image/png(?:;[^,]*)?;base64,(.*)$", re.I | re.S)
ATLAS_JSON = (
    "q_daoist_login_ui_10240_redraw_clear_final_layers/"
    "q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/"
    "fairygui_atlas/qstyle_fairygui_atlas_600.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def within(base: Path, relative: str) -> Path:
    result = (base / str(relative).replace("\\", "/")).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError(f"Path escapes its declared root: {relative}")
    return result


def key_for(path: Path, workspace: Path) -> str:
    return path.resolve().relative_to(workspace.resolve()).as_posix()


def image_metrics(original, output, policy: dict) -> dict:
    """Compare decoded pixels in strips, keeping memory bounded for large art."""
    before_context = nullcontext(original) if isinstance(original, Image.Image) else Image.open(original)
    after_context = nullcontext(output) if isinstance(output, Image.Image) else Image.open(output)
    with before_context as before, after_context as after:
        result = {
            "original_size": list(before.size), "output_size": list(after.size),
            "original_mode": before.mode, "output_mode": after.mode,
            "original_frames": getattr(before, "n_frames", 1),
            "output_frames": getattr(after, "n_frames", 1),
            "size_equal": before.size == after.size,
            "mode_equal": before.mode == after.mode,
        }
        # load() verifies decoding even when a structural mismatch stops metrics.
        before.load()
        after.load()
        if not result["size_equal"] or not result["mode_equal"]:
            return result
        if result["original_frames"] != 1 or result["output_frames"] != 1:
            raise ValueError("Animated raster requires frame-wise validation")
        if before.mode not in {"RGB", "RGBA", "L", "LA", "P", "1"}:
            raise ValueError(f"Unsupported pixel mode: {before.mode}")
        counts = defaultdict(int)
        sums = defaultdict(float)
        digest = hashlib.sha256()
        digest.update(f"RGBA:{after.width}x{after.height}:".encode("ascii"))
        maximum_increase = -math.inf
        histogram_before = np.zeros(256, dtype=np.float64)
        histogram_after = np.zeros(256, dtype=np.float64)
        for y in range(0, before.height, 128):
            box = (0, y, before.width, min(y + 128, before.height))
            a = np.asarray(before.crop(box).convert("RGBA"))
            b = np.asarray(after.crop(box).convert("RGBA"))
            digest.update(b.tobytes())
            alpha = a[..., 3]
            visible = alpha > 0
            hidden = ~visible
            counts["pixels"] += int(alpha.size)
            counts["visible_pixels"] += int(np.count_nonzero(visible))
            counts["hidden_pixels"] += int(np.count_nonzero(hidden))
            counts["alpha_changed_pixels"] += int(np.count_nonzero(alpha != b[..., 3]))
            rgb_changed = np.any(a[..., :3] != b[..., :3], axis=-1)
            counts["hidden_rgb_changed_pixels"] += int(np.count_nonzero(hidden & rgb_changed))
            counts["visible_rgb_changed_pixels"] += int(np.count_nonzero(visible & rgb_changed))
            if not np.any(visible):
                continue
            old_y = SRGB[a[..., :3]] @ WEIGHTS
            new_y = SRGB[b[..., :3]] @ WEIGHTS
            old_linear = LINEAR[a[..., :3]] @ WEIGHTS
            new_linear = LINEAR[b[..., :3]] @ WEIGHTS
            weight = alpha.astype(np.float32) / 255.0
            delta = new_y - old_y
            maximum_increase = max(maximum_increase, float(np.max(delta[visible])))
            counts["luminance_increased_pixels"] += int(np.count_nonzero(
                visible & (delta > policy["luminance_increase_tolerance"] + 1e-7)))
            counts["newly_crushed_pixels"] += int(np.count_nonzero(
                visible & (old_y >= policy["crush_source_threshold"])
                & (new_y <= policy["crush_output_threshold"])))
            masks = {
                "visible": visible,
                "highlight": visible & (old_y >= policy["highlight_threshold"]),
                "shadow": visible & (old_y <= policy["shadow_threshold"]),
            }
            for name, mask in masks.items():
                counts[f"{name}_sample_pixels"] += int(np.count_nonzero(mask))
                w = weight[mask]
                sums[f"{name}_weight"] += float(w.sum(dtype=np.float64))
                sums[f"{name}_original"] += float((old_y[mask] * w).sum(dtype=np.float64))
                sums[f"{name}_output"] += float((new_y[mask] * w).sum(dtype=np.float64))
            sums["original_linear"] += float((old_linear * weight).sum(dtype=np.float64))
            sums["output_linear"] += float((new_linear * weight).sum(dtype=np.float64))
            histogram_before += np.bincount(
                np.rint(old_y[visible] * 255).astype(np.int32),
                weights=weight[visible], minlength=256)
            histogram_after += np.bincount(
                np.rint(new_y[visible] * 255).astype(np.int32),
                weights=weight[visible], minlength=256)
        result.update(counts)
        # Explicit zero keys are useful for assertions and downstream summaries.
        for field in ("alpha_changed_pixels", "hidden_rgb_changed_pixels",
                      "luminance_increased_pixels", "newly_crushed_pixels"):
            result.setdefault(field, 0)
        result["decoded_pixel_sha256"] = digest.hexdigest()
        result["max_luminance_increase"] = (
            maximum_increase if math.isfinite(maximum_increase) else None)
        result["luminance_space"] = "sRGB Rec.709-weighted luma, range 0..1"
        for name in ("visible", "highlight", "shadow"):
            weight = sums[f"{name}_weight"]
            old = sums[f"{name}_original"] / weight if weight else None
            new = sums[f"{name}_output"] / weight if weight else None
            result[f"{name}_original_mean"] = old
            result[f"{name}_output_mean"] = new
            result[f"{name}_mean_drop"] = old - new if old is not None else None
            result[f"{name}_retention"] = new / old if old else None
        total_weight = sums["visible_weight"]
        result["original_linear_mean"] = sums["original_linear"] / total_weight if total_weight else None
        result["output_linear_mean"] = sums["output_linear"] / total_weight if total_weight else None
        for label, histogram in (("original", histogram_before), ("output", histogram_after)):
            cumulative = np.cumsum(histogram)
            total = cumulative[-1]
            result[f"{label}_luma_percentiles"] = {
                str(p): float(np.searchsorted(cumulative, total * p / 100.0)) / 255.0
                if total else None for p in (10, 50, 90, 99)
            }
        return result


def gif_metrics(original: Path, output: Path, policy: dict) -> dict:
    """Compare every displayed GIF frame, timing, and all non-palette bytes.

    Pillow may expose first frames as P and later frames as RGB/RGBA. Initial
    modes are checked separately; matching frames are compared as RGBA.
    """
    from gif_grade import gif_structure_bytes

    old_data = original.read_bytes()
    new_data = output.read_bytes()
    result = {
        "non_palette_bytes_equal": gif_structure_bytes(old_data) == gif_structure_bytes(new_data),
        "frames": [],
    }
    with Image.open(io.BytesIO(old_data)) as before, Image.open(io.BytesIO(new_data)) as after:
        result.update({
            "original_size": list(before.size), "output_size": list(after.size),
            "size_equal": before.size == after.size,
            "original_mode": before.mode, "output_mode": after.mode,
            "mode_equal": before.mode == after.mode,
            "original_frames": getattr(before, "n_frames", 1),
            "output_frames": getattr(after, "n_frames", 1),
            "original_loop": before.info.get("loop"),
            "output_loop": after.info.get("loop"),
            "original_background_index": before.info.get("background"),
            "output_background_index": after.info.get("background"),
        })
        result["frame_count_equal"] = result["original_frames"] == result["output_frames"]
        result["loop_equal"] = result["original_loop"] == result["output_loop"]
        result["background_index_equal"] = result["original_background_index"] == result["output_background_index"]
        for index in range(min(result["original_frames"], result["output_frames"])):
            before.seek(index)
            after.seek(index)
            old_extent = getattr(before, "dispose_extent", (0, 0, *before.size))
            new_extent = getattr(after, "dispose_extent", (0, 0, *after.size))
            frame = {
                "index": index,
                "original_duration_ms": before.info.get("duration"),
                "output_duration_ms": after.info.get("duration"),
                "original_disposal": getattr(before, "disposal_method", None),
                "output_disposal": getattr(after, "disposal_method", None),
                "original_extent": list(old_extent) if old_extent is not None else None,
                "output_extent": list(new_extent) if new_extent is not None else None,
            }
            frame["duration_equal"] = frame["original_duration_ms"] == frame["output_duration_ms"]
            frame["disposal_equal"] = frame["original_disposal"] == frame["output_disposal"]
            frame["extent_equal"] = frame["original_extent"] == frame["output_extent"]
            with before.convert("RGBA") as old_frame, after.convert("RGBA") as new_frame:
                frame["original_decoder_mode"] = before.mode
                frame["output_decoder_mode"] = after.mode
                frame["image"] = image_metrics(old_frame, new_frame, policy)
            result["frames"].append(frame)
        semantic = {
            "size": result["output_size"], "loop": result["output_loop"],
            "frames": [{"pixels": frame["image"].get("decoded_pixel_sha256"),
                        "duration": frame["output_duration_ms"],
                        "disposal": frame["output_disposal"],
                        "extent": frame["output_extent"]} for frame in result["frames"]],
        }
        result["decoded_pixel_sha256"] = hashlib.sha256(
            json.dumps(semantic, sort_keys=True).encode("utf-8")).hexdigest()
    return result


def svg_structure(path: Path):
    """Return a structure signature and PNG payloads; ignore layout whitespace."""
    root = ET.fromstring(path.read_bytes())
    payloads = []

    def signature(node):
        attrs = {}
        for name, value in node.attrib.items():
            match = PNG_URI.match(value.strip())
            if match:
                payloads.append(base64.b64decode(re.sub(r"\s+", "", match.group(1)), validate=True))
                attrs[name] = "<embedded-png>"
            else:
                attrs[name] = value
        return [node.tag, sorted(attrs.items()),
                node.text if node.text and node.text.strip() else "",
                node.tail if node.tail and node.tail.strip() else "",
                [signature(child) for child in node]]

    structure = signature(root)
    texts = [ET.tostring(node, encoding="unicode") for node in root.iter()
             if node.tag.rsplit("}", 1)[-1] == "text"]
    return structure, payloads, texts


class Validator:
    def __init__(self, processing: Path, workspace: Path | None = None):
        self.processing = processing.resolve()
        self.v8 = self.processing.parent
        self.data = json.loads(self.processing.read_text(encoding="utf-8-sig"))
        self.workspace = (workspace or Path(self.data.get("workspace_root", self.v8.parent))).resolve()
        self.errors = []
        self.warnings = []
        self.results = []
        self.record_map = {}
        self.metric_cache = {}

    def issue(self, severity, check, path, detail):
        target = self.errors if severity == "error" else self.warnings
        target.append({"check": check, "path": str(path), "detail": detail})

    def check(self, condition, check, path, detail):
        if not condition:
            self.issue("error", check, path, detail)
        return bool(condition)

    def policy_for(self, record):
        policy = dict(DEFAULT_POLICY)
        if "expect_highlight_reduction" in self.data:
            policy["expect_highlight_reduction"] = self.data["expect_highlight_reduction"]
        policy.update(self.data.get("validation_policy", {}))
        if "expect_highlight_reduction" in record:
            policy["expect_highlight_reduction"] = record["expect_highlight_reduction"]
        policy.update(record.get("validation_policy", {}))
        policy.setdefault("expect_highlight_reduction", bool(record["changed"]))
        return policy

    def assert_metrics(self, metrics, path, policy):
        self.check(metrics["size_equal"], "dimensions", path, metrics["output_size"])
        self.check(metrics["mode_equal"], "mode", path, metrics["output_mode"])
        if not metrics["size_equal"] or not metrics["mode_equal"]:
            return
        for field in ("alpha_changed_pixels", "hidden_rgb_changed_pixels",
                      "luminance_increased_pixels", "newly_crushed_pixels"):
            self.check(metrics[field] == 0, field, path, metrics[field])
        drop = metrics["highlight_mean_drop"]
        if drop is not None and policy["expect_highlight_reduction"]:
            minimum = float(policy["highlight_min_drop"])
            self.check(drop > 1e-8 if minimum == 0 else drop >= minimum - 1e-7,
                       "highlight_reduction", path, {"mean_drop": drop, "minimum": minimum})
        shadow_drop = metrics["shadow_mean_drop"]
        if shadow_drop is not None:
            self.check(shadow_drop <= policy["shadow_max_mean_drop"] + 1e-7,
                       "shadow_mean_drop", path, shadow_drop)
        retention = metrics["shadow_retention"]
        if retention is not None:
            self.check(retention >= policy["shadow_retention_min"] - 1e-7,
                       "shadow_retention", path, retention)

    def assert_gif_metrics(self, metrics, path, policy):
        for field in ("size_equal", "mode_equal", "frame_count_equal", "loop_equal",
                      "background_index_equal", "non_palette_bytes_equal"):
            self.check(metrics[field], f"gif_{field}", path, metrics[field])
        for frame in metrics["frames"]:
            frame_path = f"{path}#frame-{frame['index']}"
            for field in ("duration_equal", "disposal_equal", "extent_equal"):
                self.check(frame[field], f"gif_{field}", frame_path, frame[field])
            self.assert_metrics(frame["image"], frame_path, policy)

    def verify_record(self, record):
        name = str(record.get("path", "<missing path>"))
        start_errors = len(self.errors)
        result = {"path": name, "kind": record.get("kind"), "preset": record.get("preset")}
        try:
            missing = sorted(REQUIRED - set(record))
            if missing:
                raise ValueError(f"Missing record fields: {missing}")
            output = within(self.workspace, name)
            original = within(self.v8, record["backup"])
            canonical = key_for(output, self.workspace)
            if canonical in self.record_map:
                raise ValueError("Duplicate output path in processing records")
            self.record_map[canonical] = record
            source_sha = sha256_file(original)
            output_sha = sha256_file(output)
            result.update(original_sha256=source_sha, output_sha256=output_sha,
                          changed=source_sha != output_sha)
            self.check(source_sha == record["original_sha256"], "backup_sha256", name, source_sha)
            self.check(output_sha == record["output_sha256"], "output_sha256", name, output_sha)
            self.check(bool(record["changed"]) == (source_sha != output_sha),
                       "changed_flag", name, result["changed"])
            policy = self.policy_for(record)
            result["validation_policy"] = policy
            cache_key = (source_sha, output_sha)
            if output.suffix.lower() == ".svg":
                old_structure, old_pngs, old_texts = svg_structure(original)
                new_structure, new_pngs, new_texts = svg_structure(output)
                self.check(old_structure == new_structure, "svg_structure", name,
                           "All XML geometry, non-image attributes and text must remain unchanged")
                self.check(old_texts == new_texts, "svg_text", name,
                           "Text element subtrees must remain unchanged")
                self.check(len(old_pngs) == len(new_pngs), "svg_embedded_png_count", name,
                           {"original": len(old_pngs), "output": len(new_pngs)})
                result["embedded_png_count"] = len(new_pngs)
                result["text_element_count"] = len(new_texts)
                embedded_results = []
                for index, (old, new) in enumerate(zip(old_pngs, new_pngs)):
                    embedded_policy = dict(policy)
                    # An SVG can contain unchanged text/icon PNGs next to changed art.
                    embedded_policy["expect_highlight_reduction"] = (
                        policy["expect_highlight_reduction"] and old != new)
                    metrics = image_metrics(io.BytesIO(old), io.BytesIO(new), embedded_policy)
                    self.assert_metrics(metrics, f"{name}#png-{index}", embedded_policy)
                    embedded_results.append(metrics)
                result["embedded_pngs"] = embedded_results
                semantic = [new_structure, [m.get("decoded_pixel_sha256") for m in embedded_results]]
                result["decoded_pixel_sha256"] = hashlib.sha256(
                    json.dumps(semantic, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
            elif output.suffix.lower() == ".gif":
                policy_key = json.dumps(policy, sort_keys=True)
                cache_key += (policy_key,)
                if cache_key not in self.metric_cache:
                    self.metric_cache[cache_key] = gif_metrics(original, output, policy)
                metrics = copy.deepcopy(self.metric_cache[cache_key])
                self.assert_gif_metrics(metrics, name, policy)
                result["gif"] = metrics
                result["decoded_pixel_sha256"] = metrics["decoded_pixel_sha256"]
            else:
                policy_key = json.dumps(policy, sort_keys=True)
                cache_key += (policy_key,)
                if cache_key not in self.metric_cache:
                    self.metric_cache[cache_key] = image_metrics(original, output, policy)
                metrics = copy.deepcopy(self.metric_cache[cache_key])
                self.assert_metrics(metrics, name, policy)
                result["image"] = metrics
                result["decoded_pixel_sha256"] = metrics.get("decoded_pixel_sha256")
            result["readable"] = True
        except Exception as exc:
            self.issue("error", "file_validation", name, f"{type(exc).__name__}: {exc}")
            result["readable"] = False
        result["status"] = "passed" if len(self.errors) == start_errors else "failed"
        self.results.append(result)

    def original_for(self, output: Path) -> Path:
        key = key_for(output, self.workspace)
        if key not in self.record_map:
            raise ValueError(f"No immutable original backup recorded for {key}")
        return within(self.v8, self.record_map[key]["backup"])

    def verify_duplicates(self):
        groups = defaultdict(list)
        for result in self.results:
            if result.get("original_sha256"):
                groups[result["original_sha256"]].append(result)
        reports = []
        for source_sha, members in groups.items():
            if len(members) < 2:
                continue
            pixel_hashes = {item.get("decoded_pixel_sha256") for item in members}
            passed = None not in pixel_hashes and len(pixel_hashes) == 1
            self.check(passed, "duplicate_pixel_consistency", source_sha,
                       [item["path"] for item in members])
            byte_equal = len({item.get("output_sha256") for item in members}) == 1
            if passed and not byte_equal:
                self.issue("warning", "duplicate_encoding_difference", source_sha,
                           "Decoded content matches; output file encodings differ")
            reports.append({"original_sha256": source_sha, "count": len(members),
                            "paths": [item["path"] for item in members],
                            "pixels_equal": passed, "bytes_equal": byte_equal})
        return reports

    def verify_tiles(self):
        specs = self.data.get("tile_manifests")
        if specs is None:
            candidate = self.workspace / "tianyong_city_6x6/tile_manifest.json"
            specs = [{"manifest": key_for(candidate, self.workspace),
                      "master": "tianyong_city_6x6/Previews/tianyong_city_master_6144.png"}] if candidate.exists() else []
        reports = []
        for spec in specs:
            spec = {"manifest": spec} if isinstance(spec, str) else spec
            name = spec["manifest"]
            start_errors = len(self.errors)
            report = {"manifest": name, "tiles": []}
            try:
                manifest_path = within(self.workspace, name)
                meta = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
                master_path = within(self.workspace, spec["master"]) if spec.get("master") else (
                    manifest_path.parent / "Previews/tianyong_city_master_6144.png")
                expected_size = (meta["assembledSize"]["width"], meta["assembledSize"]["height"])
                expected_count = meta["grid"]["columns"] * meta["grid"]["rows"]
                self.check(len(meta["tiles"]) == expected_count, "tile_count", name,
                           {"actual": len(meta["tiles"]), "expected": expected_count})
                report["master"] = key_for(master_path, self.workspace)
                report["expected_count"] = expected_count
                with Image.open(master_path) as master:
                    self.check(master.size == expected_size, "master_dimensions", name, list(master.size))
                    for tile in meta["tiles"]:
                        tile_path = within(manifest_path.parent, tile["file"])
                        b = tile["pixelBounds"]
                        box = (b["x"], b["y"], b["x"] + b["width"], b["y"] + b["height"])
                        if not (0 <= box[0] < box[2] <= master.width and 0 <= box[1] < box[3] <= master.height):
                            raise ValueError(f"Out-of-bounds tile: {tile['id']}")
                        with Image.open(tile_path) as image:
                            crop = master.crop(box)
                            equal = (image.size == crop.size and image.mode == crop.mode
                                     and image.tobytes() == crop.tobytes())
                        self.check(equal, "tile_exact_master_crop", key_for(tile_path, self.workspace), list(box))
                        report["tiles"].append({"id": tile["id"], "bounds": list(box), "exact": equal})
            except Exception as exc:
                self.issue("error", "tile_validation", name, f"{type(exc).__name__}: {exc}")
            report["status"] = "passed" if len(self.errors) == start_errors else "failed"
            reports.append(report)
        return reports

    def verify_atlases(self):
        specs = self.data.get("atlas_specs")
        if specs is None:
            candidate = self.workspace / ATLAS_JSON
            specs = [{"json": ATLAS_JSON, "xml": str(Path(ATLAS_JSON).with_suffix(".xml")).replace("\\", "/")}] if candidate.exists() else []
        reports = []
        for spec in specs:
            start_errors = len(self.errors)
            name = spec["json"]
            report = {"json": name, "frames": []}
            try:
                json_path = within(self.workspace, name)
                meta = json.loads(json_path.read_text(encoding="utf-8-sig"))
                atlas_path = within(json_path.parent, meta["image"])
                original_atlas = self.original_for(atlas_path)
                xml_frames = {}
                if spec.get("xml"):
                    xml_path = within(self.workspace, spec["xml"])
                    xml_root = ET.parse(xml_path).getroot()
                    xml_frames = {node.attrib["name"]: node.attrib for node in xml_root}
                    self.check(len(xml_frames) == len(meta["frames"]), "atlas_xml_frame_count", name, len(xml_frames))
                self.check(len(meta["frames"]) == meta["count"], "atlas_frame_count", name, len(meta["frames"]))
                with Image.open(original_atlas) as old_atlas, Image.open(atlas_path) as new_atlas:
                    self.check(new_atlas.size == (meta["width"], meta["height"]), "atlas_dimensions", name, list(new_atlas.size))
                    for frame in meta["frames"]:
                        # This is the same source resolution used by build_atlas.py.
                        source = json_path.parent.parent / frame["group"] / frame["source_file"].replace("\\", "/").split("/")[-1]
                        source = within(self.workspace, key_for(source, self.workspace))
                        old_source = self.original_for(source)
                        if xml_frames:
                            attrs = xml_frames.get(frame["name"], {})
                            for field in ("x", "y", "width", "height", "frameX", "frameY", "frameWidth", "frameHeight"):
                                self.check(field in attrs and int(attrs[field]) == int(frame[field]),
                                           "atlas_xml_geometry", f"{name}#{frame['name']}", field)
                        box = (frame["x"], frame["y"], frame["x"] + frame["width"], frame["y"] + frame["height"])
                        with Image.open(old_source) as old_image, Image.open(source) as new_image:
                            expected = (frame["width"], frame["height"])
                            if old_image.size != expected or new_image.size != expected:
                                raise ValueError(f"Source size does not fit frame: {frame['name']}")
                            a = np.asarray(old_atlas.crop(box).convert("RGBA"))
                            b = np.asarray(old_image.convert("RGBA"))
                            c = np.asarray(new_atlas.crop(box).convert("RGBA"))
                            d = np.asarray(new_image.convert("RGBA"))
                            old_diff = np.any(a != b, axis=-1)
                            new_diff = np.any(c != d, axis=-1)
                            introduced = int(np.count_nonzero(new_diff & ~old_diff))
                            baseline_count = int(np.count_nonzero(old_diff))
                            current_count = int(np.count_nonzero(new_diff))
                        self.check(introduced == 0, "atlas_new_mismatching_pixels",
                                   frame["name"], introduced)
                        if baseline_count:
                            self.issue("warning", "atlas_baseline_difference", frame["name"],
                                       {"original_pixels": baseline_count, "output_pixels": current_count,
                                        "new_mismatching_pixels": introduced})
                        report["frames"].append({"name": frame["name"],
                            "source": key_for(source, self.workspace),
                            "baseline_mismatching_pixels": baseline_count,
                            "output_mismatching_pixels": current_count,
                            "introduced_mismatching_pixels": introduced,
                            "exact": current_count == 0})
            except Exception as exc:
                self.issue("error", "atlas_validation", name, f"{type(exc).__name__}: {exc}")
            report["status"] = "passed" if len(self.errors) == start_errors else "failed"
            reports.append(report)
        return reports

    def run(self):
        records = self.data.get("records")
        if not isinstance(records, list) or not records:
            raise ValueError("processing.json must contain a nonempty records array")
        for index, record in enumerate(records, 1):
            self.verify_record(record)
            if index % 25 == 0 or index == len(records):
                print(f"Verified {index}/{len(records)} files; errors={len(self.errors)}", flush=True)
        duplicates = self.verify_duplicates()
        tiles = self.verify_tiles()
        atlases = self.verify_atlases()
        image_results = []
        for result in self.results:
            if "image" in result:
                image_results.append(result["image"])
            image_results.extend(result.get("embedded_pngs", []))
            image_results.extend(frame["image"] for frame in result.get("gif", {}).get("frames", []))
        summary = {
            "files": len(records),
            "files_passed": sum(item["status"] == "passed" for item in self.results),
            "changed_files": sum(bool(item.get("changed")) for item in self.results),
            "raster_payloads_checked": len(image_results),
            "gif_files_checked": sum("gif" in item for item in self.results),
            "gif_frames_checked": sum(len(item.get("gif", {}).get("frames", [])) for item in self.results),
            "alpha_changed_pixels": sum(item.get("alpha_changed_pixels", 0) for item in image_results),
            "hidden_rgb_changed_pixels": sum(item.get("hidden_rgb_changed_pixels", 0) for item in image_results),
            "luminance_increased_pixels": sum(item.get("luminance_increased_pixels", 0) for item in image_results),
            "newly_crushed_pixels": sum(item.get("newly_crushed_pixels", 0) for item in image_results),
            "duplicate_groups": len(duplicates),
            "tiles_checked": sum(len(item["tiles"]) for item in tiles),
            "atlas_frames_checked": sum(len(item["frames"]) for item in atlases),
            "errors": len(self.errors), "warnings": len(self.warnings),
        }
        return {
            "schema_version": 1,
            "status": "passed" if not self.errors else "failed",
            "verified_at_utc": datetime.now(timezone.utc).isoformat(),
            "processing": str(self.processing), "workspace_root": str(self.workspace),
            "summary": summary, "errors": self.errors, "warnings": self.warnings,
            "records": self.results, "duplicates": duplicates,
            "tile_manifests": tiles, "atlases": atlases,
            "limits": [
                "Numerical verification does not replace visual review of composition, colour and text readability.",
                "SVG structure and embedded PNG pixels are checked; SVG raster rendering is not performed.",
                "Brightness statistics are alpha-weighted; fully transparent RGB is compared exactly and excluded from luminance.",
            ],
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processing", type=Path, default=V8 / "processing.json")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--output", type=Path, help="Defaults to validation.json beside processing.json")
    args = parser.parse_args(argv)
    destination = args.output or args.processing.resolve().parent / "validation.json"
    try:
        validator = Validator(args.processing, args.workspace)
        report = validator.run()
    except Exception as exc:
        report = {"schema_version": 1, "status": "failed",
                  "verified_at_utc": datetime.now(timezone.utc).isoformat(),
                  "summary": {"errors": 1},
                  "errors": [{"check": "validation_setup", "path": str(args.processing),
                              "detail": f"{type(exc).__name__}: {exc}"}]}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(destination),
                      "summary": report["summary"]}, ensure_ascii=False), flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
