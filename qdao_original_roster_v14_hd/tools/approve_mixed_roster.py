"""Seal an actually reviewed complete mixed assembly into a new offline bundle.

No generation, source relabelling, Unity invocation or formal publication.
The review is a saved reviewer assertion plus file bindings, not a signature.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

from PIL import Image
import assemble_mixed_roster as assembly

ROOT = assembly.ROOT
INPUT_ROOT = ROOT / "mixed-candidates"
APPROVED_ROOT = ROOT / "mixed-approved"
SCHEMA = "qdao-original-v14-mixed/approval-v1"
REVIEW_SCHEMA = "qdao-original-v14-mixed/visual-review-input-v1"
DIRECTION_CHECKS = ("normal_size", "enlarged", "seam_15_16_01", "anatomical_contacts_01_09")
GLOBAL_CHECKS = ("native_resolution", "closeup_1080p", "mixed_resolution_transition", "preserved_identity")
CHECKS = DIRECTION_CHECKS + GLOBAL_CHECKS
INPUT_BINDINGS = {
    "reviewed_input_manifest_sha256": "manifest.json",
    "reviewed_input_qc_sha256": "qc.json",
    "reviewed_input_assembly_report_sha256": "assembly-report.json",
    "reviewed_input_sources_sha256": "processing/mixed-sources.json",
    "reviewed_preserved_snapshot_sha256": "processing/preserved-output-snapshot.json",
}
RUNTIME_EXTRAS = {"manifest.json", "validation.json", "appearance.json"}
read, sha, encoded, require, safe_child = assembly.read, assembly.sha, assembly.encoded, assembly.require, assembly.safe_child


def digest(document):
    return hashlib.sha256(encoded(document)).hexdigest()


def child_directory(path, root):
    # Check lexical ancestors before resolve, so a junction cannot disguise a target.
    path, root = Path(path).absolute(), Path(root).absolute()
    for current in (path, root):
        while current != current.parent:
            require(not current.is_symlink() and not (hasattr(current, "is_junction") and current.is_junction()),
                    "Linked input/output ancestor is unsupported: " + str(current))
            current = current.parent
    # Windows TEMP may use ADMINI~1 while saved receipts use Administrator.
    # Normalize only after rejecting linked ancestors on both spellings.
    path, root = path.resolve(), root.resolve()
    require(path.is_relative_to(root) and path != root, "Path must be a child of " + str(root))
    safe_child(root, path.relative_to(root))
    return path.resolve()


def timestamp(value):
    require(isinstance(value, str), "Explicit UTC timestamp required")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None and result.utcoffset().total_seconds() == 0, "Timestamp must be UTC")
    return result


def runtime_files(manifest):
    rows = manifest.get("files", [])
    require(len(rows) == 137 and {r.get("path") for r in rows} == set(assembly.base.PNG_PATHS),
            "Complete exact 137 PNG inventory required")
    require(manifest.get("version") == 14 and manifest.get("resolution_mode") == assembly.base.MODE
            and manifest.get("character_id") in assembly.base.MIXED_IDS, "Wrong mixed identity or mode")
    for row in rows:
        require(row.get("availability") == "present" and re.fullmatch("[0-9a-f]{64}", row.get("sha256") or ""),
                "Missing or invalid runtime slot")
    kinds = [r.get("source_kind") for r in rows if r["path"] != "portrait.png"]
    require(set(kinds) == {"preserved-v13", "native-hd"}, "Mixed approval needs both preserved and new actions")
    return {r["path"]: r["sha256"] for r in rows}


def check_complete_assembly(directory):
    result = assembly.check_assembly(directory, require_complete=True)
    require(result.get("status") == "source_recheck_complete_pending_visual"
            and result.get("present_runtime_pngs") == 137 and result.get("missing_actions") == 0
            and result.get("reconstructed_actions") == 136 and result.get("historical_text_conflicts") == 0
            and result.get("can_publish") is False, "Independent complete source/reconciliation check failed")
    return result


def validate_review(directory, review, review_parent, evidence_resolver=None):
    manifest = read(directory / "manifest.json")
    files = runtime_files(manifest)
    require(review.get("schema") == REVIEW_SCHEMA and review.get("status") == "passed"
            and review.get("character_id") == manifest["character_id"], "Wrong visual review schema, status or identity")
    require(isinstance(review.get("reviewer"), str) and review["reviewer"].strip(), "Actual reviewer must be identified")
    reviewed = timestamp(review.get("reviewed_at_utc"))
    require(timestamp(read(directory / "assembly-report.json")["created_utc"]) <= reviewed <= datetime.now(timezone.utc),
            "Review predates assembly or is in the future")
    for key, relative in INPUT_BINDINGS.items():
        require(review.get(key) == sha(safe_child(directory, relative)), "Stale visual input binding: " + key)
    require(review.get("reviewed_artifacts") == files, "Review must bind exact current 137 PNG hashes")
    directions = review.get("reviewed_directions", [])
    require(len(directions) == 8 and set(directions) == set(assembly.DIRS), "All eight distinct directions must be reviewed")
    notes = review.get("notes_by_direction", {})
    require(set(notes) == set(assembly.DIRS) and all(isinstance(n, str) and len(n.strip()) >= 12 for n in notes.values()),
            "Concrete review notes for each direction required")
    for name in CHECKS:
        require(review.get(name + "_review") is True, "Actual visual inspection required: " + name)
    for name in GLOBAL_CHECKS:
        require(isinstance(review.get(name + "_notes"), str) and len(review[name + "_notes"].strip()) >= 12,
                "Concrete inspection notes required: " + name)
    evidence = review.get("evidence")
    require(isinstance(evidence, list) and evidence, "Saved actual visual evidence required")
    coverage = {name: set() for name in CHECKS}
    seen, resolved = set(), []
    for index, item in enumerate(evidence):
        require(isinstance(item, dict) and isinstance(item.get("path"), str), "Invalid visual evidence item")
        path = Path(item["path"])
        if evidence_resolver:
            path = evidence_resolver(index, item)
        elif not path.is_absolute():
            path = safe_child(review_parent, path)
        path = path.resolve()
        require(path not in seen and path.is_file() and sha(path) == item.get("sha256"),
                "Evidence is duplicate, missing or changed")
        seen.add(path)
        checks, dirs = item.get("checks", []), item.get("directions", [])
        require(checks and len(checks) == len(set(checks)) and set(checks) <= set(CHECKS)
                and len(dirs) == len(set(dirs)) and set(dirs) <= set(assembly.DIRS), "Invalid evidence coverage")
        require(isinstance(item.get("notes"), str) and len(item["notes"].strip()) >= 12, "Evidence needs concrete notes")
        with Image.open(path) as image:
            require(image.format == "PNG" and min(image.size) >= 64, "Evidence must be a readable PNG")
            if "closeup_1080p" in checks:
                require(image.size == (1920, 1080), "Closeup evidence must be a real 1920x1080 capture")
            if "native_resolution" in checks:
                require(min(image.size) >= 1024, "Native inspection evidence is too small")
            image.verify()
        for name in checks:
            coverage[name].update(dirs if name in DIRECTION_CHECKS else {"reviewed"})
        resolved.append(path)
    for name in DIRECTION_CHECKS:
        require(coverage[name] == set(assembly.DIRS), "Evidence missing directions for " + name)
    for name in GLOBAL_CHECKS:
        require(coverage[name], "Evidence missing " + name)
    return files, resolved


def activation(character, manifest_sha, qc_sha, validation_sha):
    return {"version": 14, "characterId": character, "resolutionMode": assembly.base.MODE,
            "frameCount": 16, "frameDurationMs": 30, "cycleDurationMs": 480, "alignmentVersion": 2,
            "dedicatedIdle": True, "contactFrame": 0, "frameWidth": 1024, "frameHeight": 1024,
            "portraitWidth": 1024, "portraitHeight": 1024, "pixelsPerUnit": 104, "pivotX": .5, "pivotY": .08,
            "status": "passed", "visualReview": "passed", "manifest_sha256": manifest_sha, "qc_sha256": qc_sha,
            "validation_sha256": validation_sha, "sourceCommit": assembly.base.SOURCE_COMMIT, "sourceFamily": "original-00-22"}


def approval_documents(directory, review, review_sha, source_check, sealed_at):
    manifest, qc = copy.deepcopy(read(directory / "manifest.json")), copy.deepcopy(read(directory / "qc.json"))
    require(qc.get("errors") == [] and set(qc.get("directions", {})) == set(assembly.DIRS), "Numeric QC failed")
    manifest.update(status="passed", visual_review="passed")
    qc.update(status="passed", visual_review="passed")
    for direction in qc["directions"].values():
        direction.update(status="passed", visual_review="passed")
    visual = {**copy.deepcopy(review), "reviewed_manifest_sha256": digest(manifest), "reviewed_qc_sha256": digest(qc),
              "review_input_sha256": review_sha, "sealed_at_utc": sealed_at,
              "runtime_acceptance": "pending_real_mixed_asset_unity_run"}
    validation = {"version": 14, "character_id": manifest["character_id"], "resolution_mode": assembly.base.MODE,
                  "scope": "all8", "status": "passed", "visual_review": "passed", "manifest_sha256": digest(manifest),
                  "qc_sha256": digest(qc), "visual_review_sha256": digest(visual), "reconstructed_frames": 136,
                  "synthetic_frames_created": 0, "missing_generation_receipts": [], "independent_assembly_check": source_check,
                  "runtime_acceptance": "pending_real_mixed_asset_unity_run", "formal_publication_authorized": False,
                  "source_evidence_scope": "saved_metadata_and_file_bindings_not_cryptographic_model_attestation"}
    return {"manifest.json": manifest, "qc.json": qc, "review/visual-review.json": visual, "validation.json": validation,
            "appearance.json": activation(manifest["character_id"], digest(manifest), digest(qc), digest(validation))}


def build_approval(directory, review_path):
    directory = child_directory(directory, INPUT_ROOT)
    review_path = Path(review_path).resolve()
    before = assembly.file_inventory(directory)
    review = read(review_path)
    files, evidence = validate_review(directory, review, review_path.parent)
    source_check = check_complete_assembly(directory)
    review_sha = sha(review_path)
    sealed_at = datetime.now(timezone.utc).isoformat()
    documents = approval_documents(directory, review, review_sha, source_check, sealed_at)
    copies = {p: {"source": str(safe_child(directory, p)), "sha256": h} for p, h in files.items()}
    copies["review/fresh-review-input.json"] = {"source": str(review_path), "sha256": review_sha}
    evidence_paths = []
    for index, path in enumerate(evidence):
        relative = f"review/evidence/{index:03d}-{sha(path)}.png"
        copies[relative] = {"source": str(path), "sha256": sha(path)}
        evidence_paths.append(relative)
    # Source records retain their exact original claims; approval is a separate document.
    for relative in INPUT_BINDINGS.values():
        target = "review/input-assembly/" + relative
        copies[target] = {"source": str(safe_child(directory, relative)), "sha256": sha(safe_child(directory, relative))}
    sealed_files = {p: digest(v) for p, v in documents.items()}
    require(assembly.file_inventory(directory) == before, "Assembly changed during approval")
    documents["approval.json"] = {"schema": SCHEMA, "character_id": source_check["character_id"],
        "status": "passed_visual_pending_unity", "formal_publication_authorized": False, "sealed_at_utc": sealed_at,
        "input_assembly": str(directory), "input_inventory": before, "review_input_sha256": review_sha,
        "evidence_copies": evidence_paths, "copied_files": {p: v["sha256"] for p, v in copies.items()},
        "sealed_files": sealed_files, "runtime_outputs": {**files, **{p: sealed_files[p] for p in RUNTIME_EXTRAS}},
        "approval_tool_sha256": sha(Path(__file__)), "assembly_tool_sha256": sha(Path(assembly.__file__))}
    return documents, copies


def execute_approval(documents, copies, output):
    output = child_directory(output, APPROVED_ROOT)
    require(output.name == documents["approval.json"]["character_id"], "Output leaf must equal original character ID")
    require(not output.exists(), "Approval bundles are immutable; use a new run directory")
    source = Path(documents["approval.json"]["input_assembly"])
    require(assembly.file_inventory(source) == documents["approval.json"]["input_inventory"], "Assembly changed before sealing")
    for row in copies.values():
        require(sha(Path(row["source"])) == row["sha256"], "Review/source changed before sealing")
    output.mkdir(parents=True)
    for relative, row in copies.items():
        target = safe_child(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(row["source"], target)
        require(sha(target) == row["sha256"], "Sealed copied file differs")
    for relative, value in sorted(documents.items(), key=lambda item: item[0] == "appearance.json"):
        target = safe_child(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded(value))
    require(assembly.file_inventory(source) == documents["approval.json"]["input_inventory"], "Assembly changed during sealing")


def verify_approved(directory):
    directory = child_directory(directory, APPROVED_ROOT)
    receipt = read(directory / "approval.json")
    require(receipt.get("schema") == SCHEMA and receipt.get("status") == "passed_visual_pending_unity"
            and receipt.get("formal_publication_authorized") is False, "Invalid mixed approval receipt")
    require(receipt.get("approval_tool_sha256") == sha(Path(__file__))
            and receipt.get("assembly_tool_sha256") == sha(Path(assembly.__file__)), "Approval/check tool changed")
    source = child_directory(receipt["input_assembly"], INPUT_ROOT)
    require(assembly.file_inventory(source) == receipt["input_inventory"], "Original assembly changed or unavailable")
    expected_files = {**receipt["copied_files"], **receipt["sealed_files"], "approval.json": sha(directory / "approval.json")}
    require(assembly.file_inventory(directory) == expected_files, "Approved file inventory changed")
    review_path = directory / "review/fresh-review-input.json"
    require(sha(review_path) == receipt["review_input_sha256"], "Sealed fresh review changed")
    review = read(review_path)
    evidence_copies = receipt["evidence_copies"]
    require(len(evidence_copies) == len(review.get("evidence", [])), "Evidence copy count differs")
    files, _ = validate_review(source, review, review_path.parent,
        lambda index, item: safe_child(directory, evidence_copies[index]))
    source_check = check_complete_assembly(source)
    expected = approval_documents(source, review, sha(review_path), source_check, receipt["sealed_at_utc"])
    require(set(receipt["sealed_files"]) == set(expected), "Unexpected approved metadata file")
    for relative, value in expected.items():
        require(sha(safe_child(directory, relative)) == digest(value), "Approval metadata does not derive from checked inputs: " + relative)
    expected_copied = set(files) | {"review/fresh-review-input.json"} | set(evidence_copies) | {
        "review/input-assembly/" + relative for relative in INPUT_BINDINGS.values()}
    require(set(receipt["copied_files"]) == expected_copied, "Unexpected copied file set")
    require(all(receipt["copied_files"][p] == h for p, h in files.items()), "Approved runtime pixels differ from reviewed source")
    for relative in INPUT_BINDINGS.values():
        require(sha(safe_child(directory, "review/input-assembly/" + relative)) == sha(safe_child(source, relative)),
                "Preserved pre-approval metadata changed")
    outputs = {**files, **{p: digest(expected[p]) for p in RUNTIME_EXTRAS}}
    require(receipt["runtime_outputs"] == outputs and len(outputs) == 140
            and directory.name == receipt["character_id"] == source_check["character_id"], "Wrong runtime outputs or identity")
    require(timestamp(receipt["sealed_at_utc"]) >= timestamp(review["reviewed_at_utc"]), "Seal predates visual review")
    return {"status": "passed_visual_pending_unity", "character_id": receipt["character_id"], "approved": str(directory),
            "runtime_outputs": outputs, "formal_publication_authorized": False, "writesPerformed": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    approve = commands.add_parser("approve")
    approve.add_argument("--assembly", type=Path, required=True)
    approve.add_argument("--review-input", type=Path, required=True)
    approve.add_argument("--output", type=Path, required=True)
    approve.add_argument("--execute", action="store_true")
    check = commands.add_parser("check")
    check.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "check":
        result = verify_approved(args.directory)
    else:
        documents, copies = build_approval(args.assembly, args.review_input)
        target = child_directory(args.output, APPROVED_ROOT)
        require(not target.exists() and target.name == documents["approval.json"]["character_id"], "Use a new same-ID approval target")
        if args.execute:
            execute_approval(documents, copies, target)
        result = {"status": "sealed_pending_unity" if args.execute else "ready_dry_run", "runtime_pngs": 137,
                  "writesPerformed": args.execute, "formal_publication_authorized": False}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
