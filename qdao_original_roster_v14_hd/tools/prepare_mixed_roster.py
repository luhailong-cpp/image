"""Freeze preserved Original 04-06 evidence and exact remaining action slots.

This is a metadata-only preparation tool. It cannot generate, approve, assemble,
stage or publish artwork. Existing V13 and all-HD V14 tools remain unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image
from mixed_workspace import active_ids

ROOT = Path(__file__).resolve().parents[1]
V13 = ROOT.parent / "qdao_original_roster_v13"
PREPARATION_ROOT = ROOT / "mixed-preparation"
SOURCE_COMMIT = "9adcf9291e4a867601868889a5965f3cd48630ba"
MODE = "mixed-preserved-v1"
SCHEMA = "qdao-original-v14/mixed-preparation-v1"
DIRS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
MIXED_IDS = ("04_mountain_guardian_boy", "05_celestial_musician_girl", "06_thunder_caster_boy")
ACTION_PATHS = tuple(f"walk/{d}/{n:02d}.png" for d in DIRS for n in range(1, 17)) + tuple(f"idle/{d}.png" for d in DIRS)
PNG_PATHS = ACTION_PATHS + ("portrait.png",)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def value_sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def safe_child(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    require(not relative.is_absolute() and ".." not in relative.parts, f"Unsafe relative path: {relative}")
    child = root / relative
    require(child.resolve().is_relative_to(root), f"Path escapes root: {child}")
    current = child
    while current != root:
        require(not current.is_symlink() and not (hasattr(current, "is_junction") and current.is_junction()),
                f"Linked evidence path is unsupported: {current}")
        current = current.parent
    return child


def runtime_file(relative, digest, source_digest, source_kind, native_cell_size=None):
    """The client contract; this only describes an existing preserved output."""
    require(relative in PNG_PATHS, "Unknown runtime slot")
    require(re.fullmatch("[0-9a-f]{64}", digest or "") and re.fullmatch("[0-9a-f]{64}", source_digest or ""),
            "Runtime/source SHA must be lower-case SHA256")
    portrait = relative == "portrait.png"
    require(source_kind == ("original-portrait" if portrait else "preserved-v13"),
            "Preparation cannot relabel preserved files as native-HD")
    result = {"path": relative, "sha256": digest, "width": 1024 if portrait else 512,
              "height": 1024 if portrait else 512, "source_kind": source_kind, "source_sha256": source_digest}
    if not portrait:
        require(isinstance(native_cell_size, list) and len(native_cell_size) == 2 and
                all(isinstance(v, int) and v > 0 for v in native_cell_size), "Invalid recorded native cell")
        result.update(pixels_per_unit=52, pivot=[0.5, 0.08], root_px=[256, 471],
                      native_cell_size=native_cell_size, preserved_sha256=digest)
    return result


def png_info(path):
    with Image.open(path) as image:
        return {"format": image.format, "mode": image.mode, "size": list(image.size)}


def build_preparation():
    inventory_path = V13 / "inventory.json"
    inventory = read(inventory_path)
    require(inventory.get("source_commit") == SOURCE_COMMIT and inventory.get("unique_character_count") == 23,
            "Unexpected original identity inventory")
    identities = inventory["characters"]
    require(len(identities) == 23 and len({r["character_id"] for r in identities}) == 23,
            "Original identity inventory must contain 23 unique entries")
    require(tuple(r["character_id"] for r in identities[4:7]) == MIXED_IDS, "Mixed IDs differ from restored inventory")
    tracked = {}
    issues = {}

    def issue(character, role, path, expected=None, actual=None, output=None, reason="recorded_sha_mismatch"):
        key = (character, role, str(path), expected, actual, reason)
        item = issues.setdefault(key, {"character_id": character, "role": role, "path": str(path),
                                      "recorded_sha256": expected, "actual_sha256": actual,
                                      "reason": reason, "affected_outputs": []})
        if output and output not in item["affected_outputs"]:
            item["affected_outputs"].append(output)

    def track(path):
        path = Path(path).resolve()
        key = str(path)
        if key not in tracked:
            require(path.is_file(), f"Evidence file missing: {path}")
            tracked[key] = {"path": key, "sha256": sha(path), "bytes": path.stat().st_size}
        return tracked[key]

    def reference(character, out, item, role, output):
        if not isinstance(item, dict) or not item.get("path"):
            issue(character, role, out, output=output, reason="recorded_reference_missing")
            return None
        path = safe_child(out, item["path"])
        if not path.is_file():
            issue(character, role, path, item.get("sha256"), None, output, "evidence_file_missing")
            return None
        actual = track(path)
        if item.get("sha256") != actual["sha256"]:
            issue(character, role, path, item.get("sha256"), actual["sha256"], output)
        return actual

    track(inventory_path)
    state_path = ROOT / "CONTINUATION_STATE_20260918.json"
    track(state_path)
    state = {r["character_id"]: r for r in read(state_path)["characters"]}
    characters = []
    missing_characters = []
    trees = []
    preserved_rows = []
    for entry in identities[4:]:
        character = entry["character_id"]
        if character not in active_ids():
            continue
        require(entry["source_commit"] == SOURCE_COMMIT, "Identity source commit changed")
        out = V13 / "candidate" / character
        present = {p for p in ACTION_PATHS if (out / p).is_file()}
        missing = [p for p in ACTION_PATHS if p not in present]
        walked = sum(p.startswith("walk/") for p in present)
        idled = len(present) - walked
        old = state.get(character, {})
        if old.get("candidate_walk") != walked or old.get("candidate_idle") != idled:
            issue(character, "continuation_state", state_path, output=None, reason="live_action_counts_differ_from_handoff")
        if character not in MIXED_IDS and present:
            issue(character, "new_character", out, reason="unexpected_existing_actions_require_manual_classification")
        missing_characters.append({"character_id": character, "name": entry["name"],
                                   "target_resolution_mode": MODE if character in MIXED_IDS else "all-native-hd-v14",
                                   "existing_walk": walked, "existing_idle": idled,
                                   "missing_walk": sum(p.startswith("walk/") for p in missing),
                                   "missing_idle": sum(p.startswith("idle/") for p in missing),
                                   "missing_action_paths": missing})
        if character not in MIXED_IDS:
            continue
        fs_path = safe_child(out, "processing/frame-sources.json")
        records = read(fs_path)
        profile = read(safe_child(out, "processing/scale-profile.json"))
        expected_scale = 0.88 if character.startswith("06_") else 0.84
        require(profile.get("common_scale") == expected_scale and profile.get("root_px") == [256, 471]
                and profile.get("alignment_version") == 2 and profile.get("per_subject_bbox_scaling") is False,
                f"Unexpected preserved character geometry: {character}")
        require(set(records) == present, f"Saved source records and live action slots differ: {character}")
        tree_paths = []
        for file in sorted(out.rglob("*")):
            if file.is_file():
                relative = file.relative_to(out).as_posix()
                track(safe_child(out, relative))
                tree_paths.append(relative)
        trees.append({"character_id": character, "root": str(out.resolve()), "files": tree_paths})
        slots = []
        source_cells = set()
        for relative in ACTION_PATHS:
            if relative not in present:
                slots.append({"path": relative, "state": "missing_awaiting_confirmed_2_5",
                              "required_width": 1024, "required_height": 1024,
                              "required_pixels_per_unit": 104, "required_root_px": [512, 942],
                              "required_pivot": [0.5, 0.08], "required_source_kind": "native-hd",
                              "required_native_cell_min_px": 1024, "actual_model_evidence": None})
                continue
            rec = records[relative]
            output = track(out / relative)
            require(png_info(out / relative) == {"format": "PNG", "mode": "RGBA", "size": [512, 512]},
                    f"Preserved action is no longer 512 RGBA: {character}/{relative}")
            if rec.get("output_sha256") != output["sha256"]:
                issue(character, "output", out / relative, rec.get("output_sha256"), output["sha256"], relative)
            source = reference(character, out, rec.get("source"), "raw", relative)
            reference(character, out, rec.get("prompt"), "prompt", relative)
            reference(character, out, rec.get("generation", {}).get("receipt"), "receipt", relative)
            for name, stage in rec.get("stages", {}).items():
                reference(character, out, stage, "stage_" + name, relative)
            src = rec["source"]
            box = src["cell_xyxy"]
            native = [box[2] - box[0], box[3] - box[1]]
            cell = (src["sha256"], tuple(box))
            if cell in source_cells:
                issue(character, "source_cell", out / src["path"], output=relative, reason="source_cell_reused")
            source_cells.add(cell)
            if source:
                info = png_info(Path(source["path"]))
                if src.get("native_size") != info["size"]:
                    issue(character, "raw_dimensions", source["path"], output=relative, reason="recorded_native_size_mismatch")
            description = runtime_file(relative, output["sha256"], src["sha256"], "preserved-v13", native)
            preserved_rows.append({"character_id": character, **description})
            slots.append({"path": relative, "state": "preserved_unapproved_legacy",
                          "runtime_file": description, "original_source_record": rec})
        portrait = read(safe_child(out, "processing/portrait-source.json"))
        portrait_output = track(out / "portrait.png")
        require(png_info(out / "portrait.png") == {"format": "PNG", "mode": "RGBA", "size": [1024, 1024]},
                "Preserved portrait is not 1024 RGBA")
        original = track(safe_child(out, portrait["preserved_source"]))
        baseline = track(Path(entry["baseline_path"]))
        require(png_info(original["path"])["size"] == [4096, 4096], "Original portrait must remain 4096")
        for actual in (original, baseline):
            if actual["sha256"] != entry["sha256"] or entry["sha256"] != entry["git_manifest_sha256"]:
                issue(character, "original_portrait", actual["path"], entry["sha256"], actual["sha256"], "portrait.png")
        if portrait.get("source_sha256") != original["sha256"]:
            issue(character, "portrait_source_record", original["path"], portrait.get("source_sha256"), original["sha256"], "portrait.png")
        if portrait.get("output_sha256") != portrait_output["sha256"]:
            issue(character, "portrait_output", out / "portrait.png", portrait.get("output_sha256"), portrait_output["sha256"], "portrait.png")
        description = runtime_file("portrait.png", portrait_output["sha256"], original["sha256"], "original-portrait")
        preserved_rows.append({"character_id": character, **description})
        slots.append({"path": "portrait.png", "state": "preserved_original_portrait", "runtime_file": description,
                      "original_source_record": portrait})
        require(len(slots) == 137 and {s["path"] for s in slots} == set(PNG_PATHS), "Must explicitly plan all 137 runtime slots")
        characters.append({"character_id": character, "version": 14, "resolution_mode": MODE,
                           "frame_size": [1024, 1024], "portrait_size": [1024, 1024],
                           "runtime_geometry": {"reference_frame_size": 512, "pixels_per_unit": 104, "pivot": [0.5, 0.08]},
                           "common_scale": expected_scale, "frame_count": 16, "frame_duration_ms": 30,
                           "cycle_duration_ms": 480, "move_speed": 9, "dedicated_idle": True,
                           "existing_walk": walked, "existing_idle": idled,
                           "planned_runtime_slots": slots})
    preserved = {"schema": "qdao-original-v14/preserved-output-snapshot-v1", "resolution_mode": MODE,
                 "files": preserved_rows, "status": "snapshot_only_not_visual_approval"}
    snapshot = {"schema": "qdao-original-v14/legacy-evidence-snapshot-v1", "files": sorted(tracked.values(), key=lambda r: r["path"]),
                "candidate_trees": trees, "status": "snapshot_only_not_source_approval"}
    missing = {"schema": "qdao-original-v14/missing-actions-v1", "characters": missing_characters,
               "totals": {"walk": sum(r["missing_walk"] for r in missing_characters),
                          "idle": sum(r["missing_idle"] for r in missing_characters)},
               "generation_status": "paused_until_actual_gpt_image_2_5_evidence", "confirmed_new_2_5_actions": 0}
    document = {"schema": SCHEMA, "created_utc": datetime.now(timezone.utc).isoformat(), "source_commit": SOURCE_COMMIT,
                "status": "incomplete_generation_paused", "visual_review": "pending", "runtime_review": "pending",
                "preserved_snapshot_sha256": value_sha(preserved), "evidence_snapshot_sha256": value_sha(snapshot),
                "missing_actions_sha256": value_sha(missing), "legacy_evidence_issues": list(issues.values()),
                "characters": characters, "can_assemble_candidate": False, "can_stage": False, "can_publish": False,
                "required_gates": ["all_137_real_runtime_pngs", "preserved_snapshot_bytes_unchanged",
                                   "resolve_historical_evidence_conflicts_without_rewriting_history",
                                   "new_cells_native_at_least_1024_no_upscale", "actual_builtin_2_5_evidence_bound_to_raw_and_receipt",
                                   "independent_source_reconstruction", "fresh_exact_sha_visual_review_all_eight_directions",
                                   "native_and_1080p_closeup_inspection", "new_real_unity_edit_and_play_run",
                                   "normal_and_nearest_capture_review_with_clipping", "full_test_input_post_comparison",
                                   "explicit_mixed_publication_gate_and_old_resource_audit"]}
    return {"preparation.json": document, "preserved-output-snapshot.json": preserved,
            "legacy-evidence-snapshot.json": snapshot, "missing-actions.json": missing}


def write_preparation(bundle, output):
    output = Path(output).resolve()
    root = PREPARATION_ROOT.resolve()
    require(output != root and output.is_relative_to(root), "Output must be a new child of mixed-preparation")
    safe_child(root, output.relative_to(root))
    require(not output.exists(), "Preparation runs are immutable; choose a new output directory")
    output.mkdir(parents=True, exist_ok=False)
    for name, value in bundle.items():
        with (output / name).open("xb") as stream:
            stream.write(encoded(value))


def check_preparation(directory, require_complete=False):
    directory = Path(directory).resolve()
    doc = read(directory / "preparation.json")
    require(doc.get("schema") == SCHEMA and doc.get("source_commit") == SOURCE_COMMIT, "Unknown preparation contract")
    for name, field in (("preserved-output-snapshot.json", "preserved_snapshot_sha256"),
                        ("legacy-evidence-snapshot.json", "evidence_snapshot_sha256"),
                        ("missing-actions.json", "missing_actions_sha256")):
        require(sha(directory / name) == doc[field], f"Preparation snapshot changed: {name}")
    snapshot = read(directory / "legacy-evidence-snapshot.json")
    failures = []
    for row in snapshot["files"]:
        path = Path(row["path"])
        if not path.is_file():
            failures.append({"path": str(path), "reason": "missing"})
        elif path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            failures.append({"path": str(path), "reason": "changed"})
    for tree in snapshot["candidate_trees"]:
        root = Path(tree["root"])
        live = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        if live != set(tree["files"]):
            failures.append({"path": str(root), "reason": "candidate_tree_inventory_changed",
                             "added": sorted(live - set(tree["files"])), "removed": sorted(set(tree["files"]) - live)})
    require(not failures, "Preservation snapshot mismatch: " + json.dumps(failures, ensure_ascii=False))
    missing = read(directory / "missing-actions.json")
    require([r["character_id"] for r in doc["characters"]] == list(MIXED_IDS), "Wrong mixed identities")
    preserved = read(directory / "preserved-output-snapshot.json")
    by_key = {(r["character_id"], r["path"]): r for r in preserved["files"]}
    require(len(by_key) == len(preserved["files"]), "Duplicate preserved outputs")
    for character in doc["characters"]:
        slots = character["planned_runtime_slots"]
        require(len(slots) == 137 and {s["path"] for s in slots} == set(PNG_PATHS), "Incomplete/duplicate planned runtime inventory")
        for slot in slots:
            if "runtime_file" in slot:
                row = slot["runtime_file"]
                require(by_key[(character["character_id"], row["path"])] == {"character_id": character["character_id"], **row},
                        "Preserved slot differs from immutable output snapshot")
                require(row == runtime_file(row["path"], row["sha256"], row["source_sha256"], row["source_kind"], row.get("native_cell_size")),
                        "Preserved slot violates mixed resolution geometry")
    require(doc.get("can_assemble_candidate") is False and doc.get("can_stage") is False and doc.get("can_publish") is False,
            "A preparation record cannot grant artwork approval or publication")
    result = {"status": "passed_snapshot_integrity", "artwork_status": "incomplete_generation_paused",
              "preserved_snapshot_sha256": doc["preserved_snapshot_sha256"],
              "tracked_evidence_files": len(snapshot["files"]), "preserved_runtime_pngs": len(preserved["files"]),
              "legacy_evidence_conflicts": len(doc["legacy_evidence_issues"]), "remaining_actions": missing["totals"],
              "can_assemble_candidate": False, "can_stage": False, "can_publish": False, "writesPerformed": False}
    require(not require_complete,
            "Preparation cannot be approved/published: missing real actions, unresolved historical evidence, confirmed 2.5 provenance, "
            "source reconstruction, fresh visual approval and real Unity mixed-asset publication evidence are required")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Read-only audit by default; --execute freezes only new JSON metadata")
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--execute", action="store_true")
    check = commands.add_parser("check", help="Read-only verification; never repairs or approves source evidence")
    check.add_argument("--directory", type=Path, required=True)
    check.add_argument("--require-complete", action="store_true", help="Deliberately rejects preparation as an unapproved artwork package")
    args = parser.parse_args(argv)
    if args.command == "prepare":
        bundle = build_preparation()
        if args.execute:
            write_preparation(bundle, args.output)
        result = {"status": "preparation_saved" if args.execute else "preparation_dry_run",
                  "output": str(args.output.resolve()), "writesPerformed": args.execute,
                  "preserved_runtime_pngs": len(bundle["preserved-output-snapshot.json"]["files"]),
                  "remaining_actions": bundle["missing-actions.json"]["totals"],
                  "legacy_evidence_conflicts": len(bundle["preparation.json"]["legacy_evidence_issues"]),
                  "can_assemble_candidate": False, "can_stage": False, "can_publish": False}
    else:
        result = check_preparation(args.directory, args.require_complete)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Do not claim zero writes after a possible I/O error during --execute.
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
