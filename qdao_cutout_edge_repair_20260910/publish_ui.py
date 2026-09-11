"""Plan, then explicitly publish the 158 accepted v10 UI PNG contracts.

The immutable source staging tree and its generation-status file are never
modified. Only enumerated formal PNG/SVG/manifest paths can be published; QA
reports and preview images are excluded. This is an image-repository delivery,
not a Unity import. Backups have short names for Windows path compatibility.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V10 = ROOT / "qdao_ui_style_recut_v10"
STAGE = V10 / "staged"
PLAN = HERE / "ui-plan.json"
PUBLISHED = HERE / "published-ui.json"
PREFLIGHT = ROOT / "docs/style-repair-20260911/publish-preflight.json"
FINAL = ROOT / "docs/style-repair-20260911/ui-final-delivery.json"
VISUAL = ROOT / "docs/style-repair-20260911/ui-review.json"
PORTRAITS = ROOT / "docs/style-repair-20260911/ui-portraits-final-review.json"
ATOMIC = "q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def current_sha(path):
    return sha(path) if Path(path).is_file() else None


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def safe(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Unsafe path: " + str(relative))
    return path


def save(path, data):
    path = safe(HERE, Path(path).resolve().relative_to(HERE))
    temp = path.with_name(".json-" + uuid.uuid4().hex[:8] + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def load_validator():
    # Import only; check_manifests is read-only and main() is never called.
    tool_dir = str(V10 / "tools")
    if tool_dir not in sys.path:
        sys.path.insert(0, tool_dir)
    spec = importlib.util.spec_from_file_location("v10_publish_readonly_validator", V10 / "tools/validate_staged.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metadata_checks(contract_rows):
    validation = load_validator().check_manifests(STAGE)
    errors = list(validation["errors"])
    by_path = {r["path"]: r for r in contract_rows}
    layer_dir = "q_daoist_login_ui_uncropped_highres_final_layers"
    layers = read(STAGE / layer_dir / "manifest_native_q5.json")
    old_layers = read(V10 / "contracts/layers.json")
    for field in ("hero_placement_2560", "control_placements_2560", "text_placements_2560", "layer_contract"):
        if layers.get(field) != old_layers.get(field):
            errors.append("Layer contract changed: " + field)
    outputs = layers["outputs"] + read(STAGE / "qdao_ui_redesign_v5/hud/placement.json")["validation"]["layers"]
    if len(outputs) != 15:
        errors.append("Expected 15 layer/HUD metadata outputs")
    for row in outputs:
        p = row["path"]
        if p not in by_path or row["sha256"] != sha(safe(STAGE, p)):
            errors.append("Composite output metadata SHA mismatch: " + p)
        if p in by_path and (row["size"] != by_path[p]["size"] or row["mode"] != by_path[p]["mode"]):
            errors.append("Composite canvas/mode mismatch: " + p)
    all_legacy = {a["png"]: a for a in read(STAGE / "exact_qdao_slices/manifest_native_q5.json")["assets"]}
    atom = read(STAGE / ATOMIC / "manifest_native_q5.json")
    if len(atom["assets"]) != 23:
        errors.append("Expected 23 atomic manifest assets")
    for row in atom["assets"]:
        if row != all_legacy.get(row["png"]):
            errors.append("Atomic/full manifest disagree: " + row["png"])
    badges = read(STAGE / ATOMIC / "manifest_ai_qstyle_badges.json")
    if ATOMIC + "/" + badges["source_sheet"] not in by_path:
        errors.append("Badge atlas missing from formal PNG contract")
    for row in badges["outputs"]:
        if ATOMIC + "/" + row["file"] not in by_path:
            errors.append("Badge output missing from formal PNG contract")
    validation.update({"composite_records_checked": 15, "atomic_duplicate_records_checked": 23,
                       "badge_outputs_checked": len(badges["outputs"]), "atlas_xml_files_required": 0,
                       "atlas_note": "The UI badge atlas is in the 158 PNG contracts. Its formal metadata references PNG/JSON, not XML. The unrelated 124-item atlas is excluded.",
                       "errors": errors})
    return validation


def plan():
    dependencies = [PREFLIGHT, FINAL, VISUAL, PORTRAITS,
                    V10 / "contracts/current_files.json", V10 / "contracts/components.json",
                    V10 / "contracts/legacy.json", V10 / "contracts/attributes.json",
                    V10 / "contracts/layers.json", V10 / "tools/validate_staged.py",
                    V10 / "tools/inventory_contracts.py"]
    bindings = [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in dependencies]
    baseline = read(V10 / "contracts/current_files.json")
    final = read(FINAL)
    visual = read(VISUAL)
    portraits = read(PORTRAITS)
    if baseline["asset_count"] != 158 or len(baseline["files"]) != 158:
        raise ValueError("Expected frozen 158 PNG contracts")
    approved = {r["path"]: r for r in final["files"]}
    reviewed = {r["path"]: r for r in visual["records"]}
    portrait_approved = {"designs/attribute-panels/v2-painted/unity-slices/png/" + r["name"]: r
                         for r in portraits["records"]}
    if len(approved) != 158 or len(reviewed) != 158 or portraits["status"] != "passed":
        raise ValueError("Incomplete visual/final evidence")
    companions = [r["path"] for r in read(PREFLIGHT)["ui"]["companion_files"]]
    if len(companions) != 126 or len(set(companions)) != 126:
        raise ValueError("Expected exact 126 reviewed companion paths")
    if Counter(Path(p).suffix for p in companions) != {".svg": 118, ".json": 8}:
        raise ValueError("Unexpected companion file types/counts")
    for p in companions:
        if any(t in p for t in ("review", "validation", "contact", "overview")):
            raise ValueError("QA file is not a publication target: " + p)
    pngs = [r["path"] for r in baseline["files"]]
    if set(pngs) & set(companions):
        raise ValueError("Duplicate publication path")
    rows, errors = [], []
    for old in baseline["files"]:
        relative = old["path"]
        staged = safe(STAGE, relative)
        digest = sha(staged)
        if digest != approved[relative]["staged_sha256"]:
            errors.append("Changed since final accepted snapshot: " + relative)
        if relative in portrait_approved:
            review = portrait_approved[relative]
            if review["sha256"] != digest or review["status"] != "passed":
                errors.append("Portrait review does not match: " + relative)
        else:
            review = reviewed[relative]
            if review["staged_sha"] != digest or review.get("visual_review") != "passed":
                errors.append("Visual review does not match: " + relative)
        with Image.open(staged) as im:
            im.load()
            if list(im.size) != old["size"] or im.mode != old["mode"]:
                errors.append("PNG contract differs: " + relative)
            if "A" in im.getbands():
                extrema = im.getchannel("A").getextrema()
                if extrema[1] == 0 or (old["alpha_range"][0] == 0 and extrema[0] != 0):
                    errors.append("Required alpha is missing: " + relative)
        rows.append({"path": relative, "kind": "png", "family": old["family"],
                     "size": old["size"], "mode": old["mode"],
                     "before_sha256": current_sha(safe(ROOT, relative)), "staged_sha256": digest})
    for relative in companions:
        rows.append({"path": relative, "kind": Path(relative).suffix[1:],
                     "before_sha256": current_sha(safe(ROOT, relative)),
                     "staged_sha256": sha(safe(STAGE, relative))})
    checks = metadata_checks(baseline["files"])
    errors += checks["errors"]
    for row in rows:
        row["changed"] = row["before_sha256"] != row["staged_sha256"]
        row["bytes"] = safe(STAGE, row["path"]).stat().st_size
        if current_sha(safe(ROOT, row["path"])) != row["before_sha256"] or sha(safe(STAGE, row["path"])) != row["staged_sha256"]:
            errors.append("Concurrent file update during plan: " + row["path"])
    for item in bindings:
        if sha(safe(ROOT, item["path"])) != item["sha256"]:
            errors.append("Concurrent evidence/contract update: " + item["path"])
    report = {"schema": "qdao.ui-delivery-plan.v1", "created_utc": now(),
              "status": "ready" if not errors else "blocked", "files": rows, "bindings": bindings,
              "checks": checks, "errors": errors,
              "summary": {"total_files": len(rows), "contract_pngs": 158, "companion_files": 126,
                          "files_to_replace": sum(r["changed"] for r in rows),
                          "unchanged_files": sum(not r["changed"] for r in rows),
                          "replace_counts": dict(Counter(r["kind"] for r in rows if r["changed"]))},
              "scope": "Only enumerated formal files. No QA, screenshots, engine integration, v10 source edits or generation-status change. Staged manifests retain their historical build metadata; published-ui.json records actual repository delivery."}
    save(PLAN, report)
    print(json.dumps({"plan": str(PLAN), "status": report["status"], **report["summary"], "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


def verify_plan(report, written=()):
    written = set(written)
    for item in report["bindings"]:
        if sha(safe(ROOT, item["path"])) != item["sha256"]:
            raise RuntimeError("Evidence/contract changed: " + item["path"])
    for row in report["files"]:
        if sha(safe(STAGE, row["path"])) != row["staged_sha256"]:
            raise RuntimeError("Staged source changed: " + row["path"])
        expected = row["staged_sha256"] if row["path"] in written else row["before_sha256"]
        if current_sha(safe(ROOT, row["path"])) != expected:
            raise RuntimeError("Production changed concurrently: " + row["path"])


def atomic_copy(source, target, expected_current, expected_new):
    # The temporary sibling is deliberately shorter than every formal filename.
    temp = target.parent / (".ui-" + uuid.uuid4().hex[:8] + ".tmp")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, temp)
        if sha(temp) != expected_new:
            raise RuntimeError("Copy verification failed: " + str(source))
        if current_sha(target) != expected_current:
            raise RuntimeError("Concurrent destination update: " + str(target))
        os.replace(temp, target)
    finally:
        if temp.exists():
            temp.unlink()


def publish():
    report = read(PLAN)
    if report["status"] != "ready" or report["errors"]:
        raise RuntimeError("Plan is not ready")
    if len(report["files"]) != 284 or len({r["path"] for r in report["files"]}) != 284:
        raise RuntimeError("Publication plan scope changed")
    verify_plan(report)
    run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    backup = HERE / ("uib-" + run)
    backup.mkdir(exist_ok=False)
    manifest = {"run_id": run, "started_utc": now(), "plan_sha256": sha(PLAN),
                "status": "preparing", "backup_directory": backup.relative_to(ROOT).as_posix(),
                "backup_files": [], "written": [], "scope": report["scope"]}
    changed = [r for r in report["files"] if r["changed"]]
    written = []
    try:
        # All backups are verified before the first production mutation.
        for index, row in enumerate(changed):
            name = f"{index:04}.bin"
            if row["before_sha256"] is not None:
                shutil.copyfile(safe(ROOT, row["path"]), backup / name)
                if sha(backup / name) != row["before_sha256"]:
                    raise RuntimeError("Destination changed during backup: " + row["path"])
            manifest["backup_files"].append({"path": row["path"], "backup": name,
                                              "before_sha256": row["before_sha256"], "after_sha256": row["staged_sha256"]})
        save(backup / "manifest.json", manifest)
        verify_plan(report)
        manifest["status"] = "publishing"
        save(backup / "manifest.json", manifest)
        for row in changed:
            source, destination = safe(STAGE, row["path"]), safe(ROOT, row["path"])
            if sha(source) != row["staged_sha256"]:
                raise RuntimeError("Staged source changed during publish: " + row["path"])
            atomic_copy(source, destination, row["before_sha256"], row["staged_sha256"])
            written.append(row["path"])
            manifest["written"] = list(written)
            save(backup / "manifest.json", manifest)
            if sha(destination) != row["staged_sha256"]:
                raise RuntimeError("Concurrent update after replacement: " + row["path"])
        verify_plan(report, written)
        manifest.update({"status": "published", "completed_utc": now(),
                         "summary": report["summary"], "all_284_formal_files_match_staging": True,
                         "files": report["files"], "validation": report["checks"]})
        save(backup / "manifest.json", manifest)
        save(PUBLISHED, manifest)
        print(json.dumps({"status": "published", "report": str(PUBLISHED), **report["summary"]}))
        return 0
    except BaseException as exc:
        rollback, conflicts = [], []
        by_path = {r["path"]: r for r in manifest["backup_files"]}
        for relative in reversed(written):
            row = by_path[relative]
            destination = safe(ROOT, relative)
            if current_sha(destination) != row["after_sha256"]:
                conflicts.append(relative)
                continue
            try:
                if row["before_sha256"] is None:
                    # This exact newly created file is owned by this attempt.
                    destination.unlink()
                else:
                    atomic_copy(backup / row["backup"], destination, row["after_sha256"], row["before_sha256"])
                rollback.append(relative)
            except Exception as rollback_error:
                conflicts.append(relative + ": " + str(rollback_error))
        manifest.update({"status": "failed_rolled_back" if not conflicts else "failed_concurrent_changes_preserved",
                         "failed_utc": now(), "error": str(exc), "rolled_back": rollback,
                         "rollback_conflicts_preserved": conflicts})
        save(backup / "manifest.json", manifest)
        save(PUBLISHED, manifest)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "publish"))
    args = parser.parse_args()
    raise SystemExit(plan() if args.command == "plan" else publish())
