"""Non-destructive mixed V14 assembly and independent source reconstruction.

Only Original 04-06; no generation, visual approval, activation or publication.
The current user permits the built-in image tool without a confirmed version.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import sys

import numpy as np
from PIL import Image

import prepare_mixed_roster as base

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "mixed-candidates"
DIRS = base.DIRS
SCHEMA = "qdao-original-v14/mixed-assembly-v1"
MODEL_POLICY = "builtin-authorized-version-unconfirmed-allowed"
RECONCILIATION_TOOL = ROOT / "mixed-preparation/legacy-text-reconciliation-20260918/legacy_text_reconciliation.py"
RECONCILIATION_SHA = "f47f284bc9c4e36ac6f57d7ecca757f5c7f82e4458c9df16f17aa0eb6e218fc3"


def require(ok, message):
    base.require(ok, message)


read, sha, encoded, safe_child = base.read, base.sha, base.encoded, base.safe_child


def imread(path):
    with Image.open(path) as image:
        return image.convert("RGBA")


def vendor(name):
    spec = importlib.util.spec_from_file_location("mixed_rebuild_" + name, ROOT / "tools/vendor" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reconciliation_module(path):
    require(sha(Path(path)) == RECONCILIATION_SHA, "Legacy text reconciliation tool differs from reviewed whitelist")
    spec = importlib.util.spec_from_file_location("mixed_legacy_text_reconciliation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reconcile_checks(result, module, original_root, original_record, observed_root, observed_record, source_records_bytes):
    """Resolve only exact reviewed newline exceptions; leave every old byte/claim unchanged."""
    evidence = []
    for issue in result["evidence_issues"]:
        require(issue["role"] in ("prompt", "receipt"), "Only old text conflicts may be reconciled")
        original = original_record["prompt"] if issue["role"] == "prompt" else original_record["generation"]["receipt"]
        observed = observed_record["prompt"] if issue["role"] == "prompt" else observed_record["generation"]["receipt"]
        proof = module.reconcile_bytes(str(Path(original_root) / original["path"]), original["sha256"],
                    str(Path(original_root) / "processing/frame-sources.json"), hashlib.sha256(source_records_bytes).hexdigest(),
                    safe_child(observed_root, observed["path"]).read_bytes(), source_records_bytes)
        require(result["path"] in proof["matching_frame_source_keys"], "Reconciliation does not bind this action")
        evidence.append(proof)
    if evidence:
        result["reconciled_text_evidence"] = evidence
        result["evidence_issues"] = []
        result["source_evidence"] = "verified_with_exact_historical_text_reconciliation"
    return result


def file_inventory(directory):
    directory = Path(directory).resolve()
    return {p.relative_to(directory).as_posix(): sha(safe_child(directory, p.relative_to(directory)))
            for p in sorted(directory.rglob("*")) if p.is_file()}


def action_identity(path):
    require(path in base.ACTION_PATHS, "Unknown action output: " + path)
    parts = path.split("/")
    return ("walk", parts[1], int(parts[2][:-4])) if parts[0] == "walk" else ("idle", parts[1][:-4], 0)


def reference(root, item, role, issues, tolerate_text_conflict=False):
    require(isinstance(item, dict) and item.get("path"), "Missing " + role + " reference")
    path = safe_child(root, item["path"])
    require(path.is_file(), "Missing " + role + ": " + str(path))
    actual = sha(path)
    if actual != item.get("sha256"):
        require(tolerate_text_conflict and role in ("prompt", "receipt"), "Changed " + role + ": " + str(path))
        issues.append({"role": role, "path": item["path"], "recorded_sha256": item.get("sha256"),
                       "actual_sha256": actual, "status": "unresolved_historical_text_conflict"})
    return path


def validate_native_receipt(receipt, receipt_path, raw_path, prompt_path):
    """Validate saved request/output file bindings, not signed API/model identity."""
    require(isinstance(receipt, dict) and receipt.get("tool") in
            ("built-in image_gen", "image_gen", "image_gen.imagegen", "image_gen__imagegen"),
            "New HD receipt needs an explicit authorized built-in tool name")
    request = receipt.get("actual_request")
    require(isinstance(request, dict) and isinstance(request.get("prompt"), str) and request["prompt"].strip(),
            "New HD receipt needs the actual request prompt")
    require(request["prompt"] == Path(prompt_path).read_bytes().decode("utf-8-sig"),
            "Actual request prompt differs from saved exact prompt bytes")
    references = request.get("referenced_image_paths")
    require(isinstance(references, list) and references and all(isinstance(p, str) and p for p in references),
            "New HD request needs actual saved reference-image paths")
    reference_files = []
    for value in references:
        path = Path(value)
        require(path.is_absolute() and path.is_file(), "Actual request reference image is missing")
        reference_files.append({"path": str(path.resolve()), "sha256": sha(path)})
    require(len({row["path"] for row in reference_files}) == len(reference_files), "Duplicate actual reference path")
    hint = receipt.get("output_hint")
    match = re.match(r"^Generated images are saved to (.+?) as (.+?\.png) by default\.(?:\r?\n|$)", hint or "")
    require(match is not None, "New HD output_hint must retain the actual original PNG path")
    original = Path(receipt.get("original_generated_file", ""))
    require(original.is_absolute() and original.is_file() and Path(match.group(2)).resolve() == original.resolve()
            and Path(match.group(1)).resolve() == original.parent.resolve(), "Original generated PNG path differs or is missing")
    raw_sha = sha(Path(raw_path))
    require(sha(original) == raw_sha, "Original generated PNG bytes differ from saved raw")
    require(type(receipt.get("generation_calls")) is int and receipt["generation_calls"] == 1
            and type(receipt.get("paid_api_calls")) is int and receipt["paid_api_calls"] == 0,
            "New HD receipt must identify one built-in call and no paid API call")
    started = request.get("started_at")
    require(isinstance(started, str), "Actual request start time missing")
    require(datetime.fromisoformat(started.replace("Z", "+00:00")).tzinfo is not None, "Request time needs UTC offset")
    return {"schema": "builtin-saved-request-output-bindings-v1", "tool": receipt["tool"],
            "receipt_sha256": sha(Path(receipt_path)), "actual_request_sha256": base.value_sha(request),
            "prompt_sha256": sha(Path(prompt_path)), "original_generated_file": str(original.resolve()),
            "original_generated_sha256": raw_sha, "saved_raw_sha256": raw_sha, "reference_files": reference_files,
            "verification_scope": "saved_metadata_and_file_bindings_only_not_cryptographic_generation_attestation",
            "model_identity_verification": "not_claimed", "c2pa_signature_verification": "not_performed"}


def reconstruct(root, relative, record, size, common_scale, keyer=None, edge=None, character=None):
    """Rebuild an existing PNG in memory; never writes/repaints a frame."""
    require(size in (512, 1024), "Unsupported output size")
    kind, direction, number = action_identity(relative)
    require((record.get("kind"), record.get("direction"), record.get("frame")) == (kind, direction, number)
            and record.get("output") == relative, "Recorded action identity differs: " + relative)
    require(record.get("alignment_version") == 2 and record.get("common_scale") == common_scale,
            "Per-frame scale or alignment changed: " + relative)
    exported_path = safe_child(root, relative)
    require(base.png_info(exported_path) == {"format": "PNG", "mode": "RGBA", "size": [size, size]},
            "Output must be an exact RGBA PNG at its declared resolution: " + relative)
    require(sha(exported_path) == record.get("output_sha256"), "Output SHA differs: " + relative)
    exported = imread(exported_path)
    alpha = np.asarray(exported)[:, :, 3]
    require(alpha.min() == 0 and alpha.max() == 255, "Output lacks transparent background or opaque subject")
    issues = []
    source = record["source"]
    raw_path = reference(root, source, "raw", issues)
    prompt = reference(root, record.get("prompt"), "prompt", issues, size == 512)
    generation = record.get("generation", {})
    require(generation.get("tool") == "built-in image_gen", "Action source is not the authorized built-in tool")
    receipt_path = reference(root, generation.get("receipt"), "receipt", issues, size == 512)
    receipt = read(receipt_path)
    require(isinstance(receipt, dict) and isinstance(receipt.get("output_hint"), str) and receipt["output_hint"].strip(),
            "Saved real tool output_hint receipt is required: " + relative)
    require(receipt.get("tool", "built-in image_gen") in ("built-in image_gen", "image_gen", "image_gen.imagegen", "image_gen__imagegen"),
            "Receipt belongs to another tool")
    require(prompt.stat().st_size > 0, "Exact prompt is empty")
    receipt_binding = validate_native_receipt(receipt, receipt_path, raw_path, prompt) if size == 1024 else None
    raw = imread(raw_path)
    require(source.get("native_size") == list(raw.size), "Recorded raw dimensions differ")
    rows, cols = source["grid"]
    allowed = ((4, 4), (2, 4), (2, 2), (2, 1), (1, 2), (1, 1)) if kind == "walk" else ((2, 4), (1, 1))
    require((rows, cols) in allowed, "Unsupported original grid")
    index = source["cell_index"]
    require(type(index) is int and 0 <= index < rows * cols, "Invalid source cell index")
    r, c = divmod(index, cols)
    if kind == "walk":
        start = source.get("sequence_start_frame", 1)
        mapping = source.get("output_frame_map") or list(range(start, start + rows * cols))
        selected = source.get("selected_source_cell_indices", list(range(rows * cols)))
        assigned = [v for v in mapping if v is not None]
        require(len(mapping) == rows * cols and selected and len(set(selected)) == len(selected)
                and set(selected) == {i for i, value in enumerate(mapping) if value is not None}
                and index in selected and len(set(assigned)) == len(assigned)
                and all(type(v) is int and 1 <= v <= 16 for v in assigned) and mapping[index] == number,
                "Incorrect complete-cell to action mapping")
        require((rows, cols) not in ((1, 1), (1, 2), (2, 1), (2, 2)) or source.get("output_frame_map") is not None,
                "Small source grids need an explicit final-frame mapping")
    else:
        mapping = source.get("output_direction_map") or list(DIRS)
        require(len(mapping) == rows * cols and mapping[index] == direction and
                ((rows, cols) == (2, 4) and set(mapping) == set(DIRS) or
                 (rows, cols) == (1, 1) and mapping == [direction] and source.get("selected_source_cell_indices") == [0]),
                "Incorrect independent-idle mapping")
    box = [round(c * raw.width / cols), round(r * raw.height / rows),
           round((c + 1) * raw.width / cols), round((r + 1) * raw.height / rows)]
    require(source.get("cell_xyxy") == box, "Source crop is not the original complete cell")
    factor = size / max(raw.width / cols, raw.height / rows) * common_scale
    require(math.isfinite(factor) and factor > 0 and record.get("whole_cell_scale") == factor, "Wrong whole-cell normalization")
    native_size = [box[2] - box[0], box[3] - box[1]]
    if size == 1024:
        require(min(raw.width / cols, raw.height / rows, *native_size) >= 1024, "New HD native cell is below 1024")
        require(factor <= 1, "New HD upscaling is forbidden")
    keyer, edge = keyer or vendor("generate2dsprite"), edge or vendor("edge_despill")
    cell = raw.crop(box)
    prepared = cell.copy()
    threshold = record.get("alpha_cleanup_threshold", 0)
    require(threshold in (0, 8) and (threshold == 0 or np.asarray(raw)[:, :, 3].min() < 255), "Invalid alpha cleanup")
    if threshold:
        array = np.array(prepared)
        array[:, :, 3][array[:, :, 3] <= threshold] = 0
        prepared = Image.fromarray(array, "RGBA").copy()
    chroma = record.get("chroma_thresholds", [100, 150])
    require(chroma in ([100, 150], [50, 75]), "Unsupported chroma thresholds")
    if character and character.startswith("05_"):
        require(chroma == [50, 75], "05 must preserve its purple costume with 50/75 chroma")
    keyed = keyer.remove_bg_magenta(prepared, *chroma)
    a = np.asarray(keyed)[:, :, 3]
    require(not any(np.any(side) for side in (a[0], a[-1], a[:, 0], a[:, -1])), "Original cell foreground touches an edge")
    normalized_size = (round(cell.width * factor), round(cell.height * factor))
    require(record.get("normalized_size") == list(normalized_size), "Recorded normalized dimensions differ")
    normalized = keyed.resize(normalized_size, Image.Resampling.LANCZOS) if keyed.size != normalized_size else keyed.copy()
    clean, stats = edge.despill(normalized, radius=4, reference_radius=12)
    require(np.array_equal(np.asarray(normalized)[:, :, 3], np.asarray(clean)[:, :, 3])
            and np.array_equal(np.asarray(normalized)[:, :, 1], np.asarray(clean)[:, :, 1])
            and stats["protected_red_changes"] == 0 and stats["outside_band_changes"] == 0, "Despill changed protected pixels")
    y, x = np.where(np.asarray(clean)[:, :, 3] > 8)
    require(len(x) > 0, "Empty original subject")
    top = int(y.min())
    axis = float(np.median(x[y < top + max(1, int((int(y.max()) - top) * .42))]))
    anchor = [size // 2, 471 * (size // 512)]
    delta = [round(anchor[0] - axis), anchor[1] - int(y.max())]
    require(record.get("translation_px") == delta, "Integer alignment differs")
    visible_y, visible_x = np.where(np.asarray(clean)[:, :, 3] > 0)
    require(visible_x.min() + delta[0] >= 1 and visible_x.max() + delta[0] <= size - 2
            and visible_y.min() + delta[1] >= 1 and visible_y.max() + delta[1] <= size - 2,
            "Aligned source would clip")
    final = Image.new("RGBA", (size, size))
    final.paste(clean, tuple(delta))
    require(final.tobytes() == exported.tobytes(), "Independent reconstruction differs: " + relative)
    for stage, expected in (("cell", cell), ("keyed", keyed), ("normalized", normalized), ("cleaned", clean), ("final", final)):
        path = reference(root, record["stages"][stage], "stage_" + stage, issues)
        require(imread(path).tobytes() == expected.tobytes(), "Reconstructed stage differs: " + stage)
    # No generation version is inferred from either requested-model text or this receipt.
    pixels = np.asarray(final)
    ys, xs = np.where(pixels[:, :, 3] > 8)
    height = int(ys.max() - ys.min() + 1)
    half = size // 4
    return {"path": relative, "pixel_reconstruction": "passed", "source_evidence": "blocked" if issues else "verified_saved_files",
            "evidence_issues": issues, "source_cell": [source["sha256"], box], "native_cell_size": native_size,
            "whole_cell_scale": factor, "subject_height_fraction": height / size,
            "body_area_scale": float(np.sqrt(np.count_nonzero(pixels[:, size // 2 - half:size // 2 + half, 3]) / (size * size))),
            "pixel_sha256": hashlib.sha256(final.tobytes()).hexdigest(), "receipt_sha256_actual": sha(receipt_path),
            "generation_receipt_binding": receipt_binding,
            "model_identity_verification": "not_claimed", "c2pa_signature_verification": "not_performed"}


def numeric_review(results):
    by = {r["path"]: r for r in results}
    directions, errors, means = {}, [], []
    for direction in DIRS:
        frames = [by[p] for p in (f"walk/{direction}/{n:02d}.png" for n in range(1, 17)) if p in by]
        idle = by.get(f"idle/{direction}.png")
        item = {"available_walk": len(frames), "dedicated_idle_present": idle is not None, "status": "partial"}
        if len(frames) == 16 and idle:
            heights = [r["subject_height_fraction"] for r in frames]
            scales = [r["body_area_scale"] for r in frames]
            cv = float(np.std(scales) / np.mean(scales))
            mean = float(np.mean(heights))
            drift = abs(idle["subject_height_fraction"] / mean - 1)
            hashes = [r["pixel_sha256"] for r in frames]
            if len(set(hashes)) != 16:
                errors.append(direction + ": duplicate_walk_pixels")
            if idle["pixel_sha256"] in hashes:
                errors.append(direction + ": idle_copied_from_walk")
            if cv > .08:
                errors.append(direction + ": body_scale_cv")
            if drift > .08:
                errors.append(direction + ": idle_walk_height_drift")
            item.update(status="numeric_only_pending_visual", body_scale_cv=cv, idle_walk_height_drift=drift)
            means.append(mean)
        directions[direction] = item
    if len(means) == 8 and max(means) / min(means) > 1.10:
        errors.append("cross_direction_mean_height_ratio")
    return {"directions": directions, "errors": errors, "visual_review": "pending"}


def collect_references(record):
    return [record["source"], record["prompt"], record["generation"]["receipt"], *record["stages"].values()]


def remap_record(record, prefix):
    remapped = copy.deepcopy(record)
    for item in collect_references(remapped):
        item["path"] = prefix + "/" + item["path"]
    return remapped


def runtime_row(relative, record, size, preserved):
    source = record["source"]
    box = source["cell_xyxy"]
    row = {"path": relative, "sha256": record["output_sha256"], "width": size, "height": size,
           "pixels_per_unit": 52 * (size // 512), "pivot": [.5, .08], "root_px": [size // 2, 471 * (size // 512)],
           "source_kind": "preserved-v13" if preserved else "native-hd", "source_sha256": source["sha256"],
           "native_cell_size": [box[2] - box[0], box[3] - box[1]], "availability": "present"}
    if preserved:
        row["preserved_sha256"] = row["sha256"]
    return row


def legacy_frozen_rows(character, legacy):
    """Derive preserved slots from the real fixed legacy tree, never its copy."""
    records = read(legacy / "processing/frame-sources.json")
    require(set(records) <= set(base.ACTION_PATHS), "Legacy source map has unknown action slots")
    live_actions = {p for p in base.ACTION_PATHS if (legacy / p).is_file()}
    require(set(records) == live_actions, "Real legacy actions differ from its source map")
    frozen = {}
    for relative, record in records.items():
        digest = sha(legacy / relative)
        require(digest == record["output_sha256"], "Real preserved output differs from its historical source record")
        box = record["source"]["cell_xyxy"]
        frozen[relative] = {"character_id": character, **base.runtime_file(relative, digest, record["source"]["sha256"],
            "preserved-v13", [box[2] - box[0], box[3] - box[1]])}
    portrait = read(legacy / "processing/portrait-source.json")
    digest = sha(legacy / "portrait.png")
    require(digest == portrait["output_sha256"], "Real preserved portrait differs from its source record")
    frozen["portrait.png"] = {"character_id": character, **base.runtime_file("portrait.png", digest,
        portrait["source_sha256"], "original-portrait")}
    return frozen, records, portrait


def assemble_plan(character, preparation, hd_candidate, reconcile_legacy_text=False):
    require(character in base.MIXED_IDS, "Only unsealed Original 04-06 may use mixed assembly")
    preparation, hd_candidate = Path(preparation).resolve(), Path(hd_candidate).resolve()
    document = read(preparation / "preparation.json")
    require(document.get("schema") == base.SCHEMA and document.get("source_commit") == base.SOURCE_COMMIT, "Wrong preparation")
    snapshot_path = preparation / "preserved-output-snapshot.json"
    require(sha(snapshot_path) == document["preserved_snapshot_sha256"], "Preservation snapshot changed")
    evidence_path = preparation / "legacy-evidence-snapshot.json"
    require(sha(evidence_path) == document["evidence_snapshot_sha256"], "Legacy evidence snapshot changed")
    snapshot = read(snapshot_path)
    frozen = {r["path"]: r for r in snapshot["files"] if r["character_id"] == character}
    require(len(frozen) == sum(r["character_id"] == character for r in snapshot["files"]) and "portrait.png" in frozen,
            "Duplicate or missing frozen output rows")
    legacy = base.V13 / "candidate" / character
    before = file_inventory(legacy)
    evidence = read(evidence_path)
    trees = [t for t in evidence["candidate_trees"] if t["character_id"] == character]
    require(len(trees) == 1 and Path(trees[0]["root"]).resolve() == legacy.resolve(), "Wrong preserved candidate tree")
    require(set(before) == set(trees[0]["files"]), "Preserved candidate inventory changed since snapshot")
    tracked = {Path(r["path"]).resolve(): r["sha256"] for r in evidence["files"]}
    for relative, digest in before.items():
        require(tracked.get((legacy / relative).resolve()) == digest, "Preserved evidence bytes changed: " + relative)
    actual_frozen, _, _ = legacy_frozen_rows(character, legacy)
    require(frozen == actual_frozen, "Frozen snapshot differs from the real preserved source tree")
    records = read(legacy / "processing/frame-sources.json")
    require(set(records) == set(frozen) - {"portrait.png"}, "Preserved action mappings differ from frozen slots")
    hd_records_path = hd_candidate / "processing/frame-sources.json"
    hd_records = read(hd_records_path) if hd_records_path.is_file() else {}
    require(isinstance(hd_records, dict) and set(hd_records) <= set(base.ACTION_PATHS), "Unknown HD action record")
    require(all((hd_candidate / p).is_file() for p in hd_records), "HD source record has no output")
    hd_available = {p for p in base.ACTION_PATHS if (hd_candidate / p).is_file()}
    require(hd_available == set(hd_records), "HD outputs and source records differ")
    if hd_records:
        hd_manifest = read(hd_candidate / "manifest.json")
        require(hd_manifest.get("character_id") == character and hd_manifest.get("version") == 14
                and hd_manifest.get("frame_size") == [1024, 1024]
                and hd_manifest.get("sources_sha256") == sha(hd_records_path), "HD candidate identity/manifest source binding differs")
        hd_files = {row["path"]: row["sha256"] for row in hd_manifest["files"]}
        require(len(hd_files) == len(hd_manifest["files"]), "Duplicate HD manifest file rows")
        require(all(hd_files.get(path) == rec["output_sha256"] for path, rec in hd_records.items()), "HD manifest output binding differs")
        hd_cells = [(rec["source"]["sha256"], tuple(rec["source"]["cell_xyxy"])) for rec in hd_records.values()]
        require(len(hd_cells) == len(set(hd_cells)), "HD source cell was reused, including an excluded pilot")
    excluded = sorted(set(hd_records) & set(frozen))
    chosen = {p: r for p, r in hd_records.items() if p not in frozen}
    scale = .88 if character.startswith("06_") else .84
    keyer, edge = vendor("generate2dsprite"), vendor("edge_despill")
    reconciler = reconciliation_module(RECONCILIATION_TOOL) if reconcile_legacy_text else None
    copies, mappings, checks, files = {}, {}, [], []

    def copy_from(source, dest):
        source = Path(source)
        digest = sha(source)
        existing = copies.get(dest)
        require(existing is None or existing["sha256"] == digest, "Conflicting copied evidence path")
        copies[dest] = {"source": str(source.resolve()), "sha256": digest}

    for relative in base.ACTION_PATHS:
        preserved = relative in records
        rec = records.get(relative) if preserved else chosen.get(relative)
        if rec is None:
            files.append({"path": relative, "sha256": None, "width": 1024, "height": 1024,
                          "pixels_per_unit": 104, "pivot": [.5, .08], "root_px": [512, 942],
                          "source_kind": "native-hd", "source_sha256": None, "native_cell_size": None,
                          "availability": "missing"})
            continue
        origin, size = (legacy, 512) if preserved else (hd_candidate, 1024)
        if preserved:
            require(sha(origin / relative) == frozen[relative]["sha256"] == frozen[relative]["preserved_sha256"],
                    "Preserved output would change: " + relative)
        if character.startswith("05_"):
            require(rec.get("chroma_thresholds") == [50, 75], "05 must preserve its purple costume with 50/75 chroma")
        result = reconstruct(origin, relative, rec, size, scale, keyer, edge, character)
        if preserved and reconciler and result["evidence_issues"]:
            reconcile_checks(result, reconciler, legacy, rec, origin, rec, (legacy / "processing/frame-sources.json").read_bytes())
        checks.append(result)
        files.append(runtime_row(relative, rec, size, preserved))
        prefix = "evidence/preserved-v13" if preserved else "evidence/native-hd"
        for item in collect_references(rec):
            copy_from(safe_child(origin, item["path"]), prefix + "/" + item["path"])
        copy_from(origin / relative, relative)
        copy_from(origin / "processing/frame-sources.json", prefix + "/processing/frame-sources.json")
        if not preserved:
            copy_from(origin / "manifest.json", prefix + "/manifest.json")
        mappings[relative] = {"source_kind": "preserved-v13" if preserved else "native-hd",
                              "original_record": rec, "record": remap_record(rec, prefix),
                              "original_records_path": prefix + "/processing/frame-sources.json",
                              "original_records_sha256": sha(origin / "processing/frame-sources.json")}
    cells = [(r["source_cell"][0], tuple(r["source_cell"][1])) for r in checks]
    require(len(cells) == len(set(cells)), "One original source cell cannot fill multiple actions")
    portrait = read(legacy / "processing/portrait-source.json")
    source = safe_child(legacy, portrait["preserved_source"])
    entry = next(r for r in read(base.V13 / "inventory.json")["characters"] if r["character_id"] == character)
    require(entry["source_commit"] == base.SOURCE_COMMIT and sha(source) == portrait["source_sha256"] == entry["sha256"]
            == entry["git_manifest_sha256"], "Portrait identity provenance differs")
    require(imread(source).size == (4096, 4096) and base.png_info(legacy / "portrait.png") ==
            {"format": "PNG", "mode": "RGBA", "size": [1024, 1024]}, "Wrong portrait sizes")
    require(sha(legacy / "portrait.png") == frozen["portrait.png"]["sha256"] == portrait["output_sha256"]
            and imread(source).resize((1024, 1024), Image.Resampling.LANCZOS).tobytes() == imread(legacy / "portrait.png").tobytes(),
            "Portrait is not the preserved whole-image downsample")
    portrait_row = {k: v for k, v in frozen["portrait.png"].items() if k != "character_id"}
    files.append({**portrait_row, "availability": "present"})
    copy_from(legacy / "portrait.png", "portrait.png")
    copy_from(source, "evidence/original-portrait-4096.png")
    copy_from(snapshot_path, "processing/preserved-output-snapshot.json")
    copy_from(base.V13 / "inventory.json", "processing/original-inventory.json")
    if reconciler:
        copy_from(RECONCILIATION_TOOL, "evidence/legacy-text-reconciliation.py")
    source_document = {"schema": SCHEMA + "/sources", "actions": mappings, "portrait": portrait}
    qc = numeric_review(checks)
    conflicts = [{"output": r["path"], **issue} for r in checks for issue in r["evidence_issues"]]
    missing = [r["path"] for r in files if r["availability"] == "missing"]
    status = "partial" if missing else "blocked_source_evidence" if conflicts else "blocked_numeric" if qc["errors"] else "ready_for_visual_review"
    manifest = {"version": 14, "character_id": character, "resolution_mode": base.MODE, "status": status,
                "visual_review": "pending", "frame_size": [1024, 1024], "portrait_size": [1024, 1024],
                "frame_size_px": 1024, "pixels_per_unit": 104, "native_cell_min_px": 1024, "native_cell_min_scope": "native-hd-only",
                "runtime_geometry": {"reference_frame_size": 512, "pixels_per_unit": 104, "pivot": [.5, .08]},
                "alignment": {"alignment_version": 2, "root_px": [512, 942], "common_scale": scale,
                              "per_subject_bbox_scaling": False, "resolution_mode": base.MODE},
                "directions": list(DIRS), "frame_count": 16, "frame_duration_ms": 30, "cycle_duration_ms": 480,
                "dedicated_idle": True, "contact_frame": 0, "move_speed": 9, "files": files,
                "preserved_snapshot_sha256": sha(snapshot_path), "sources_path": "processing/mixed-sources.json",
                "sources_sha256": base.value_sha(source_document), "model_policy": MODEL_POLICY}
    report = {"schema": SCHEMA, "character_id": character, "status": status, "created_utc": datetime.now(timezone.utc).isoformat(),
              "runtime_png_slots": 137, "present_runtime_pngs": len(files) - len(missing), "missing_action_paths": missing,
              "preserved_actions": len(records), "new_native_actions": len(chosen), "excluded_hd_preserved_slots": excluded,
              "pixel_reconstruction_count": len(checks), "source_evidence_status": "blocked" if conflicts else "verified_saved_files",
              "unresolved_historical_text_conflicts": conflicts, "action_checks": checks,
              "visual_review": "pending", "runtime_review": "pending", "can_publish": False,
              "model_policy": MODEL_POLICY, "model_identity_verification": "not_claimed", "c2pa_signature_verification": "not_performed",
              "legacy_root": str(legacy.resolve()), "legacy_before": before, "input_files": list(copies.values()),
              "copied_files": {path: row["sha256"] for path, row in copies.items()},
              "manifest_sha256": base.value_sha(manifest), "qc_sha256": base.value_sha(qc),
              "source_commit": base.SOURCE_COMMIT}
    report["legacy_text_reconciliation_tool_sha256"] = RECONCILIATION_SHA if reconciler else None
    report["reconciled_historical_text_items"] = len({(p["original_path"], p["expected_sha256"])
        for result in checks for p in result.get("reconciled_text_evidence", [])})
    require(len(files) == 137 and {f["path"] for f in files} == set(base.PNG_PATHS), "Mixed runtime inventory must contain exactly 137 slots")
    require(file_inventory(legacy) == before, "Preserved source changed during read-only assembly")
    return {"manifest.json": manifest, "qc.json": qc, "processing/mixed-sources.json": source_document,
            "assembly-report.json": report}, copies


def execute_plan(documents, copies, output):
    output = Path(output).resolve()
    root = OUTPUT_ROOT.resolve()
    require(output.is_relative_to(root) and output != root, "Assembly output must be a new child of mixed-candidates")
    safe_child(root, output.relative_to(root))
    require(not output.exists(), "Assembly runs are immutable; choose a new output path")
    for row in copies.values():
        require(sha(Path(row["source"])) == row["sha256"], "Input changed before copy")
    output.mkdir(parents=True)
    for relative, row in copies.items():
        target = safe_child(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(row["source"], target)
        require(sha(target) == row["sha256"], "Copied evidence differs")
    for relative, document in documents.items():
        target = safe_child(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(encoded(document))
    report = documents["assembly-report.json"]
    require(file_inventory(Path(report["legacy_root"])) == report["legacy_before"], "Preserved originals changed during copy")


def check_assembly(directory, require_complete=False):
    directory = Path(directory).resolve()
    manifest, report = read(directory / "manifest.json"), read(directory / "assembly-report.json")
    require(report.get("schema") == SCHEMA and manifest.get("character_id") in base.MIXED_IDS
            and manifest["character_id"] == report["character_id"], "Wrong mixed assembly identity")
    require(manifest.get("resolution_mode") == base.MODE and manifest.get("visual_review") == "pending"
            and report.get("can_publish") is False and not (directory / "appearance.json").exists(), "Assembly cannot grant activation/approval")
    require(manifest.get("version") == 14 and manifest.get("frame_count") == 16 and manifest.get("frame_duration_ms") == 30
            and manifest.get("cycle_duration_ms") == 480 and manifest.get("dedicated_idle") is True
            and manifest.get("move_speed") == 9 and manifest.get("frame_size") == [1024, 1024]
            and manifest.get("portrait_size") == [1024, 1024]
            and manifest.get("runtime_geometry") == {"reference_frame_size": 512, "pixels_per_unit": 104, "pivot": [.5, .08]},
            "Mixed timing or maximum geometry changed")
    expected_scale = .88 if manifest["character_id"].startswith("06_") else .84
    require(manifest["alignment"] == {"alignment_version": 2, "root_px": [512, 942], "common_scale": expected_scale,
                                      "per_subject_bbox_scaling": False, "resolution_mode": base.MODE}, "Mixed alignment changed")
    require(sha(directory / "manifest.json") == report["manifest_sha256"] and sha(directory / "qc.json") == report["qc_sha256"],
            "Assembly metadata changed")
    require(sha(directory / "processing/mixed-sources.json") == manifest["sources_sha256"]
            and sha(directory / "processing/preserved-output-snapshot.json") == manifest["preserved_snapshot_sha256"],
            "Source or preserved snapshot changed")
    legacy = (base.V13 / "candidate" / manifest["character_id"]).resolve()
    require(Path(report["legacy_root"]).resolve() == legacy, "Assembly points to another legacy source root")
    require(file_inventory(legacy) == report["legacy_before"], "Original legacy source changed since assembly")
    for relative, digest in report["copied_files"].items():
        require(sha(safe_child(directory, relative)) == digest, "Copied source/output bytes changed: " + relative)
    rows = manifest["files"]
    require(len(rows) == 137 and {r["path"] for r in rows} == set(base.PNG_PATHS), "Incomplete/duplicate 137-slot inventory")
    source_document = read(directory / "processing/mixed-sources.json")
    snapshot = read(directory / "processing/preserved-output-snapshot.json")
    frozen = {r["path"]: r for r in snapshot["files"] if r["character_id"] == manifest["character_id"]}
    require(len(frozen) == sum(r["character_id"] == manifest["character_id"] for r in snapshot["files"]), "Duplicate frozen rows")
    actual_frozen, actual_records, actual_portrait = legacy_frozen_rows(manifest["character_id"], legacy)
    require(frozen == actual_frozen, "Copied frozen snapshot differs from real legacy source tree")
    require(set(frozen) <= {r["path"] for r in rows if r["availability"] == "present"}, "A preserved slot was dropped or marked missing")
    copied_legacy_records = directory / "evidence/preserved-v13/processing/frame-sources.json"
    require(sha(copied_legacy_records) == sha(legacy / "processing/frame-sources.json")
            and read(copied_legacy_records) == actual_records
            and set(actual_records) == set(frozen) - {"portrait.png"}, "Copied legacy source map differs from the real tree")
    require(source_document["portrait"] == actual_portrait, "Copied portrait source record differs from the real tree")
    require(sha(directory / "processing/original-inventory.json") == sha(base.V13 / "inventory.json"), "Copied identity inventory differs")
    live_runtime = {p.relative_to(directory).as_posix() for folder in (directory / "walk", directory / "idle")
                    for p in folder.rglob("*.png") if p.is_file()}
    if (directory / "portrait.png").is_file():
        live_runtime.add("portrait.png")
    require(live_runtime == {r["path"] for r in rows if r["availability"] == "present"}, "Extra or missing runtime PNG")
    keyer, edge = vendor("generate2dsprite"), vendor("edge_despill")
    reconciler = None
    if report.get("legacy_text_reconciliation_tool_sha256"):
        require(report["legacy_text_reconciliation_tool_sha256"] == RECONCILIATION_SHA, "Unknown reconciliation whitelist")
        reconciler = reconciliation_module(directory / "evidence/legacy-text-reconciliation.py")
    checks, missing = [], []
    for row in rows:
        relative = row["path"]
        path = safe_child(directory, relative)
        if row["availability"] == "missing":
            require(not path.exists() and row["sha256"] is None, "Missing slot acquired unbound artwork")
            missing.append(relative)
            continue
        require(path.is_file() and sha(path) == row["sha256"], "Assembled output changed: " + relative)
        if relative in frozen:
            require(row["sha256"] == frozen[relative]["sha256"] and row["width"] == frozen[relative]["width"]
                    and row["source_kind"] == frozen[relative]["source_kind"], "Preserved runtime slot was replaced")
        else:
            require(row["source_kind"] == "native-hd" and row["width"] == 1024, "New slot cannot masquerade as legacy")
            hd_manifest = read(directory / "evidence/native-hd/manifest.json")
            require(hd_manifest.get("character_id") == manifest["character_id"] and hd_manifest.get("version") == 14
                    and hd_manifest.get("frame_size") == [1024, 1024]
                    and hd_manifest.get("sources_sha256") == sha(directory / "evidence/native-hd/processing/frame-sources.json")
                    and {r["path"]: r["sha256"] for r in hd_manifest["files"]}.get(relative) == row["sha256"],
                    "Copied HD manifest/source identity differs")
        if relative == "portrait.png":
            portrait = source_document["portrait"]
            source = directory / "evidence/original-portrait-4096.png"
            inventory = read(directory / "processing/original-inventory.json")
            identity = next(r for r in inventory["characters"] if r["character_id"] == manifest["character_id"])
            require(sha(source) == portrait["source_sha256"] == identity["sha256"] == row["source_sha256"]
                    and portrait["output_sha256"] == row["sha256"], "Portrait identity changed")
            require(imread(source).size == (4096, 4096) and imread(path).size == (1024, 1024)
                    and imread(source).resize((1024, 1024), Image.Resampling.LANCZOS).tobytes() == imread(path).tobytes(),
                    "Portrait whole-image reconstruction differs")
            continue
        wrapped = source_document["actions"][relative]
        if relative in actual_records:
            require(wrapped["original_record"] == actual_records[relative], "Copied action source record differs from the real tree")
            for item in collect_references(wrapped["original_record"]):
                require(sha(safe_child(directory, "evidence/preserved-v13/" + item["path"])) == sha(safe_child(legacy, item["path"])),
                        "Copied preserved source bytes differ from original")
        originals = read(safe_child(directory, wrapped["original_records_path"]))
        require(sha(safe_child(directory, wrapped["original_records_path"])) == wrapped["original_records_sha256"]
                and originals[relative] == wrapped["original_record"], "Historical record changed")
        prefix = "evidence/preserved-v13" if row["source_kind"] == "preserved-v13" else "evidence/native-hd"
        require(wrapped["record"] == remap_record(wrapped["original_record"], prefix), "Assembly rewrote source claims")
        expected = runtime_row(relative, wrapped["record"], row["width"], row["source_kind"] == "preserved-v13")
        require(row == expected, "Per-frame runtime geometry/source differs")
        result = reconstruct(directory, relative, wrapped["record"], row["width"], manifest["alignment"]["common_scale"], keyer, edge,
                             manifest["character_id"])
        if row["source_kind"] == "preserved-v13" and reconciler and result["evidence_issues"]:
            reconcile_checks(result, reconciler, report["legacy_root"], wrapped["original_record"], directory,
                             wrapped["record"], safe_child(directory, wrapped["original_records_path"]).read_bytes())
        checks.append(result)
    require(numeric_review(checks) == read(directory / "qc.json"), "Mixed numeric review changed")
    cells = [(r["source_cell"][0], tuple(r["source_cell"][1])) for r in checks]
    require(len(cells) == len(set(cells)), "Assembled original source cell reused")
    require(missing == report["missing_action_paths"], "Missing-slot report differs")
    conflicts = [{"output": r["path"], **issue} for r in checks for issue in r["evidence_issues"]]
    saved_reconciliations = {r["path"]: r.get("reconciled_text_evidence", []) for r in report["action_checks"]}
    require({r["path"]: r.get("reconciled_text_evidence", []) for r in checks} == saved_reconciliations,
            "Historical text reconciliation proof differs")
    require({r["path"]: r.get("generation_receipt_binding") for r in checks} ==
            {r["path"]: r.get("generation_receipt_binding") for r in report["action_checks"]},
            "Saved request/output generation bindings differ")
    if require_complete:
        require(not missing and not conflicts and not read(directory / "qc.json")["errors"],
                "Complete source-ready assembly requires every real action, resolved legacy text evidence and valid numeric QC")
    numeric_errors = read(directory / "qc.json")["errors"]
    return {"status": "partial" if missing else "blocked_source_evidence" if conflicts else "blocked_numeric" if numeric_errors else "source_recheck_complete_pending_visual",
            "character_id": manifest["character_id"], "present_runtime_pngs": 137 - len(missing),
            "missing_actions": len(missing), "reconstructed_actions": len(checks), "historical_text_conflicts": len(conflicts),
            "visual_review": "pending", "can_publish": False, "writesPerformed": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    assemble = commands.add_parser("assemble")
    assemble.add_argument("--character", required=True, choices=base.MIXED_IDS)
    assemble.add_argument("--preparation", type=Path, required=True)
    assemble.add_argument("--hd-candidate", type=Path, required=True)
    assemble.add_argument("--output", type=Path, required=True)
    assemble.add_argument("--execute", action="store_true")
    assemble.add_argument("--require-complete", action="store_true")
    assemble.add_argument("--reconcile-legacy-text", action="store_true", help="Verify only the eleven reviewed exact newline/SHA exceptions in memory")
    check = commands.add_parser("check")
    check.add_argument("--directory", type=Path, required=True)
    check.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "check":
        result = check_assembly(args.directory, args.require_complete)
    else:
        documents, copies = assemble_plan(args.character, args.preparation, args.hd_candidate, args.reconcile_legacy_text)
        report = documents["assembly-report.json"]
        require(not args.require_complete or report["status"] == "ready_for_visual_review", "Incomplete or blocked assembly cannot reach visual review")
        if args.execute:
            execute_plan(documents, copies, args.output)
        result = {key: report[key] for key in ("status", "character_id", "present_runtime_pngs", "preserved_actions", "new_native_actions", "excluded_hd_preserved_slots", "source_evidence_status")}
        result.update(missing_actions=len(report["missing_action_paths"]),
                      reconciled_historical_text_items=report["reconciled_historical_text_items"],
                      writesPerformed=args.execute, visual_review="pending", can_publish=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
