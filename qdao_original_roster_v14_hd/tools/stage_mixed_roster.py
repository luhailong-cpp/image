"""Stage one approved mixed 04-06 into the sole isolated Unity project.

No formal publication, source-code writes, Unity launch or approval creation.
Default is read-only; execute creates an entirely new same-ID V14 directory.
"""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

import approve_mixed_roster as approve
import mixed_workspace

ROOT = approve.ROOT
ISOLATED_PROJECT = mixed_workspace.ISOLATED
CHARACTERS = "Assets/Resources/World/Characters"
FAMILY = CHARACTERS + "/QdaoOriginalRosterV14"
AUDIT_ROOT = ROOT / "mixed-stage-audits"
SCHEMA = "qdao-original-v14-mixed/isolated-stage-v1"
require, sha, read, encoded, safe_child = approve.require, approve.sha, approve.read, approve.encoded, approve.safe_child


def project_path(path):
    path = Path(path).absolute()
    path = approve.child_directory(path, path.parent)
    expected = approve.child_directory(ISOLATED_PROJECT, ISOLATED_PROJECT.absolute().parent)
    require(path == expected, "Only the exact isolated project is allowed; formal publication is unsupported")
    require(path.is_dir() and all(safe_child(path, p).is_dir() for p in ("Assets", "Packages", "ProjectSettings")),
            "Isolated Unity project is unavailable")
    return path.resolve()


def editor_closed(project):
    # An unlocked stale file is harmless; never delete it or force-close Unity.
    lock = safe_child(project, "Temp/UnityLockfile")
    if not lock.exists():
        return
    require(os.name == "nt", "Cannot establish an exclusive Unity lock on this platform")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    create.restype = ctypes.c_void_p
    handle = create(str(lock), 0x80000000, 0, None, 3, 0, None)
    require(handle not in (None, ctypes.c_void_p(-1).value), "Unity project lock is held; close the isolated editor before staging")
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle(handle)


def audit_path(path):
    path = approve.child_directory(path, AUDIT_ROOT)
    require(path.suffix == ".json" and not path.exists(), "Audit must be a new JSON under mixed-stage-audits")
    return path


def inventory_without(directory, excluded=None):
    result = approve.assembly.file_inventory(directory)
    if excluded:
        prefix = excluded.relative_to(directory).as_posix() + "/"
        result = {p: h for p, h in result.items() if not p.startswith(prefix)}
    return result


def prepare_stage(approved, project, audit):
    project = project_path(project)
    editor_closed(project)
    audit = audit_path(audit)
    approved = approve.child_directory(approved, approve.APPROVED_ROOT)
    checked = approve.verify_approved(approved)
    character = checked["character_id"]
    require(character in approve.assembly.base.MIXED_IDS and checked["formal_publication_authorized"] is False,
            "Only visual-approved mixed 04-06 may be staged")
    outputs = checked["runtime_outputs"]
    require(set(outputs) == set(approve.assembly.base.PNG_PATHS) | approve.RUNTIME_EXTRAS and len(outputs) == 140,
            "Exact 137 PNG plus manifest/validation/appearance staging whitelist required")
    target = safe_child(project, FAMILY + "/" + character)
    require(not target.exists() and not target.with_suffix(".meta").exists(),
            "Existing V14 character or GUID must never be replaced by mixed stage")
    protected = safe_child(project, CHARACTERS)
    require(protected.is_dir(), "Existing character resources must be present")
    return {"schema": SCHEMA, "character_id": character, "approved": str(approved), "project": str(project),
            "target": str(target), "audit": str(audit), "runtime_outputs": outputs,
            "approved_inventory": approve.assembly.file_inventory(approved),
            "protected_before": inventory_without(protected), "formal_publication_authorized": False,
            "actual_mixed_asset_unity_validation": "not_yet_run"}


def save_audit(stream, document):
    stream.seek(0)
    stream.write(encoded(document))
    stream.truncate()
    stream.flush()
    os.fsync(stream.fileno())


def execute_stage(plan):
    # Rebuild the entire gate immediately before the first write.
    fresh = prepare_stage(plan["approved"], plan["project"], plan["audit"])
    require(fresh == plan, "Staging input, protected resource or target changed since dry run")
    project = Path(plan["project"])
    target = safe_child(project, FAMILY + "/" + plan["character_id"])
    family = safe_child(project, FAMILY)
    temporary = safe_child(project, FAMILY + "/." + plan["character_id"] + ".mixed-stage-" + uuid.uuid4().hex)
    protected = safe_child(project, CHARACTERS)
    created = activated = False
    audit = audit_path(plan["audit"])
    audit.parent.mkdir(parents=True, exist_ok=True)
    stream = audit.open("xb")
    try:
        save_audit(stream, {**plan, "status": "staging_in_progress", "writesPerformed": False,
                            "stage_tool_sha256": sha(Path(__file__))})
        family.mkdir(parents=True, exist_ok=True)
        temporary.mkdir()
        created = True
        source = Path(plan["approved"])
        for relative, digest in sorted(plan["runtime_outputs"].items(), key=lambda item: item[0] == "appearance.json"):
            original = safe_child(source, relative)
            require(sha(original) == digest, "Approved input changed during copy")
            destination = safe_child(temporary, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, destination)
            require(sha(destination) == digest, "Staged copy differs")
        require(approve.assembly.file_inventory(temporary) == plan["runtime_outputs"], "Temporary runtime inventory differs")
        require(approve.assembly.file_inventory(source) == plan["approved_inventory"], "Approval changed during staging")
        editor_closed(project)
        require(inventory_without(protected, temporary) == plan["protected_before"], "Existing characters changed during stage")
        require(not target.exists() and not target.with_suffix(".meta").exists(), "Target or GUID appeared during staging")
        os.rename(temporary, target)
        created = False
        activated = True
        require(approve.assembly.file_inventory(target) == plan["runtime_outputs"], "Final runtime inventory differs")
        require(inventory_without(protected, target) == plan["protected_before"], "Old character resources were changed")
        receipt = {**plan, "status": "staged_pending_real_unity_validation", "staged_at_utc": datetime.now(timezone.utc).isoformat(),
                   "protected_changed_files": 0, "writesPerformed": True, "stage_tool_sha256": sha(Path(__file__))}
        save_audit(stream, receipt)
        return receipt
    except Exception as error:
        # The reserved audit exists before activation, including if a post-rename check fails.
        failure = {**plan, "status": "failed_after_target_activation" if activated else "failed_before_activation",
                   "target_retained": activated, "error": str(error), "writesPerformed": created or activated}
        try:
            save_audit(stream, failure)
        except OSError:
            pass  # Storage failure may leave an incomplete audit; activation state is explicit in the error below.
        if activated:
            raise RuntimeError("Stage failed after isolated target activation; target retained; inspect audit " + str(audit)) from error
        raise
    finally:
        stream.close()
        if created and temporary.exists():
            # Only our newly created temporary tree can be removed.
            safe_child(project, temporary.relative_to(project))
            require(temporary.parent == family and temporary.name.startswith("." + plan["character_id"] + ".mixed-stage-"),
                    "Unsafe temporary cleanup")
            shutil.rmtree(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    plan = prepare_stage(args.approved, args.project, args.audit)
    result = execute_stage(plan) if args.execute else {**plan, "status": "ready_dry_run", "writesPerformed": False}
    # Avoid dumping thousands of protected hashes into the console; the execute audit retains all of them.
    summary = {k: v for k, v in result.items() if k not in ("protected_before", "approved_inventory", "runtime_outputs")}
    summary.update(protected_file_count=len(plan["protected_before"]), runtime_output_count=len(plan["runtime_outputs"]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
