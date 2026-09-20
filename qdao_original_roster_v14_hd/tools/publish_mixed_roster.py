"""Publish the first approved mixed Original04 after a fresh real Unity run.

Read-only by default. Does not generate artwork, approvals, Unity evidence, metas
or indices. Saved reviews/receipts are assertions and file bindings, not signed
attestations. Existing clients, tools and historical evidence are never rewritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

sys.dont_write_bytecode = True
import approve_mixed_roster as approve
import publish_original_roster_v14 as gate
import stage_mixed_roster as stage
from review_mixed_client_run import MIXED_METHODS

ROOT = approve.ROOT
WORK = ROOT.parents[1]
FORMAL = WORK / "mmorpg-client"
ISOLATED = WORK / "tmp/qdao-original-live-candidate-20260917"
RUNS = ROOT.parent / "qdao_original_roster_v13/runtime-validation"
AUDITS = ROOT / "mixed-publication-audits"
ALLOWED_IDS = {"04_mountain_guardian_boy"}
CHARACTERS = "Assets/Resources/World/Characters"
INPUT_ROOTS = ("Assets", "Packages", "ProjectSettings", "Library/PackageCache")
FORMAL_ROOTS = INPUT_ROOTS[:3]
MIXED_SOURCE = ("Assets/Scripts/World/QdaoMixedResolutionContract.cs",
                "Assets/Tests/EditMode/Tianyong/QdaoMixedResolutionAppearanceTests.cs")
BINDINGS = gate.INPUT_BINDING_PATHS + MIXED_SOURCE + tuple(p + ".meta" for p in MIXED_SOURCE)
SCHEMA = "qdao-original-v14-mixed/publication-v1"
REVIEW_SCHEMA = "qdao-original-v14-mixed/runtime-visual-review-v1"
FORMAL_BASELINE_RELATIVE = "mixed-resolution-client-run1/formal-safety-baseline.json"
FORMAL_BASELINE_SHA256 = "8238ab4d32a2c4782f2b853339257cd3054b5e9b8c9c796351d78b42b823377f"
FORMAL_BASELINE_CHARACTER_COUNT = 3451
FORMAL_BASELINE_PRIOR_REVIEW_SHA256 = "fbb8230ef662edc5d060ca9862cf6b5e2f88ea81895da128650ec23cf4d1e03b"
FORMAL_BASELINE_SCOPE = "Read-only source/character safety audit; not a closed-Unity test-input snapshot"
read, sha, require, safe_child, encoded = gate.read, gate.sha, gate.require, gate.safe_child, gate.encoded


def exact_project(path, expected):
    path = approve.child_directory(Path(path), WORK)
    require(path == expected.resolve(), "Unsupported Unity project")
    require(all(safe_child(path, p).is_dir() for p in FORMAL_ROOTS)
            and safe_child(path, "ProjectSettings/ProjectVersion.txt").is_file(), "Unity project unavailable")
    stage.editor_closed(path)
    return path


def tree_inventory(root, roots, excluded=None):
    """Hash regular unlinked files, rejecting concurrent changes and linked dirs."""
    root = Path(root)
    rows, stats = {}, {}
    excluded = Path(excluded) if excluded else None
    def files():
        result = []
        for relative in roots:
            base = safe_child(root, relative)
            require(base.is_dir(), "Missing protected/input root: " + relative)
            for directory, dirs, names in os.walk(base, followlinks=False):
                for name in list(dirs):
                    # The walked directory was already checked; each child name
                    # comes from the filesystem, not a user-supplied path. Check
                    # links at each level without resolving every ancestor again
                    # for every one of tens of thousands of input files.
                    child = Path(directory) / name
                    require(not child.is_symlink() and not (hasattr(child, "is_junction") and child.is_junction()),
                            "Linked input directory: " + str(child))
                    if excluded and child == excluded:
                        dirs.remove(name)
                for name in names:
                    child = Path(directory) / name
                    require(not child.is_symlink() and child.is_file() and child.stat().st_nlink == 1,
                            "Linked/nonregular input file: " + str(child))
                    result.append(child)
        return sorted(result)
    paths = files()
    for path in paths:
        before = path.stat()
        digest = sha(path)
        after = path.stat()
        require((before.st_size, before.st_mtime_ns, before.st_nlink) ==
                (after.st_size, after.st_mtime_ns, after.st_nlink), "Input changed during hashing")
        key = path.relative_to(root).as_posix()
        rows[key] = {"path": key, "sha256": digest, "bytes": after.st_size}
        stats[path] = (after.st_size, after.st_mtime_ns, after.st_nlink)
    require(paths == files(), "Input file set changed during hashing")
    for path, value in stats.items():
        final = path.stat()
        require((final.st_size, final.st_mtime_ns, final.st_nlink) == value, "Hashed input changed")
    return rows


def file_inventory(directory):
    return {p: row["sha256"] for p, row in tree_inventory(Path(directory), (".",)).items()}


def snapshot_rows(document):
    require(document.get("shared_writable_links") is False and
            document.get("included_roots") == list(INPUT_ROOTS), "Incomplete/shared Unity snapshot")
    rows = gate.snapshot_records(document)
    require(document.get("count") == len(rows) and document.get("bytes") == sum(r["bytes"] for r in rows.values()),
            "Snapshot totals disagree")
    for path, row in rows.items():
        require(path == row["path"] and not Path(path).is_absolute() and ".." not in Path(path).parts
                and isinstance(row["bytes"], int) and row["bytes"] >= 0
                and re.fullmatch("[0-9a-f]{64}", row["sha256"]), "Invalid snapshot row")
    return rows


def check_unity_results(path, platform):
    required = ("QdaoOriginalAppearanceTests.OriginalRegistryKeepsTwentyThreeIndependentIdsAndDoesNotRewriteExistingRosterOrLegacy"
                if platform == "EditMode" else
                "QdaoRosterSandboxPlayModeTests.RealCitySandbox_SwitchesAllAvailableAppearancesWithoutReplacingThePlayer_AndWalksWithTheRealMotor")
    result = gate.check_results(path, required, hd_platform=platform)
    if platform == "PlayMode":
        gate.check_results(path, "QdaoRosterAnimatorPlayModeTests.EveryCharacter_WalksItsDeclaredFramesInAllEightDirections_AndSettlesOnItsIdlePose")
    class_name, methods = MIXED_METHODS[platform]
    cases = [c for c in result.iter("test-case") if c.get("classname") == class_name]
    counts = Counter(c.get("methodname") for c in cases)
    require(all(counts[method] == count for method, count in methods.items()),
            "Missing/extra mixed method or parameter cases: " + platform)
    return result


def geometry_check(actor, plan):
    declarations = {row["path"]: row for row in plan["manifest"]["files"] if row["path"] != "portrait.png"}
    prefix = gate.RESOURCE_FAMILY + "/" + plan["characterId"] + "/"
    records = actor.get("actualFrameGeometry", [])
    require(isinstance(records, list) and len(records) == 136, "Actual mixed geometry must contain 136 actions")
    by = {r["resourcePath"]: r for r in records}
    expected = {prefix + p[:-4]: r for p, r in declarations.items()}
    require(len(by) == 136 and set(by) == set(expected), "Duplicate/missing/wrong-identity mixed geometry")
    require({row["width"] for row in declarations.values()} == {512, 1024}, "A real preserved/native mixed set is required")
    for path, declared in expected.items():
        actual = by[path]
        require(actual.get("width") == declared["width"] and actual.get("height") == declared["height"],
                "Actual per-frame mixed dimensions differ: " + path)
        gate.near(actual.get("pixelsPerUnit"), declared["pixels_per_unit"], .0001, "Per-frame PPU")
        gate.near(actual.get("worldHeight"), 512 / 52, .0001, "Per-frame world height")
        for axis, value in (("x", .5), ("y", .08)):
            gate.near(actual.get("pivot", {}).get(axis), value, .0001, "Per-frame feet pivot")
    for field, dimension in (("actualTextureWidthsPerDirection", "width"), ("actualTextureHeightsPerDirection", "height")):
        summary = {}
        for direction in gate.DIRECTIONS:
            sizes = {declarations[f"walk/{direction}/{i:02d}.png"][dimension] for i in range(1, 17)}
            summary[direction] = next(iter(sizes)) if len(sizes) == 1 else 0
        require(actor.get(field) == summary, "Mixed direction summary differs")
    idle = actor.get("expectedIdleResourcePath")
    require(idle in by and "/idle/" in idle, "Actual stopped idle is not a declared independent idle")
    observed = by[idle]
    for field, source in (("actualFrameWidth", "width"), ("actualFrameHeight", "height"),
                          ("textureWidth", "width"), ("textureHeight", "height")):
        require(actor.get(field) == observed[source], "Displayed mixed idle dimensions differ")
    gate.near(actor.get("actualPixelsPerUnit"), observed["pixelsPerUnit"], .0001, "Displayed idle PPU")
    gate.near(actor.get("actualFrameWorldHeight"), 512 / 52, .0001, "Displayed world frame height")
    for axis, value in (("x", .5), ("y", .08)):
        gate.near(actor.get("actualNormalizedPivot", {}).get(axis), value, .0001, "Displayed normalized pivot")
    for axis in ("x", "y", "z"):
        gate.near(actor.get("actualBillboardScale", {}).get(axis), 1, .0001, "Billboard scale")


def actor_check(actor, plan, baseline):
    character = plan["characterId"]
    require(actor.get("requestedCharacterId") == actor.get("actualCharacterId") == character and
            actor.get("actualIsOriginalRoster") is True and actor.get("actualIsMixedResolution") is True and
            actor.get("v14MixedContractObserved") is True and actor.get("actualIsHd") is False and
            actor.get("v14HdContractObserved") is False, "Actual mixed identity/mode was not observed")
    require(actor.get("actualArtworkVersion") == actor.get("catalogVersion") == 14 and
            actor.get("actualFrameCount") == 16 and actor.get("catalogFrameDurationMs") == 30 and
            actor.get("activationAlignmentVersion") == 2 and actor.get("activationContactFrame") == 0 and
            actor.get("resourceFolder") == gate.RESOURCE_FAMILY + "/" + character,
            "Mixed runtime contract differs")
    geometry_check(actor, plan)
    require(1 <= actor.get("maxResidentHdDirectionsObserved", 0) <= 2, "Mixed direction residency is not bounded")
    for field in ("actualFramesPerDirection", "actualUniqueFrameSpritesPerDirection", "actualUniqueFrameTexturesPerDirection"):
        require(actor.get(field) == {d: 16 for d in gate.DIRECTIONS}, "Missing distinct loaded 8x16 frames: " + field)
    require(actor.get("actualDedicatedIdleDirections") == {d: 1 for d in gate.DIRECTIONS}, "Dedicated idle inventory differs")
    for field in ("activationPresent", "manifestPresent", "actualFramesMatchResources", "actualIdleMatchResources",
                  "actualHasDedicatedIdle", "spriteMatchesDedicatedIdle", "movementObserved", "stoppedIdle", "realMotorEnabled"):
        require(actor.get(field) is True, "Actual motor/resource/idle assertion missing: " + field)
    for field, expected in (("activationSha256", plan["outputs"]["appearance.json"]),
                            ("manifestSha256", plan["manifestSha256"]), ("activationManifestSha256", plan["manifestSha256"]),
                            ("activationQcSha256", plan["qcSha256"]), ("activationValidationSha256", plan["validationSha256"])):
        require(actor.get(field) == expected, "Runtime approval bytes differ: " + field)
    require(actor.get("actualTravelDistance", 0) > 3 and actor.get("actualPathDistance", 0) > 3 and
            actor.get("movementSeconds", 0) > .48 and actor.get("observedWalkPoseCount") == 16,
            "Actual mixed motor route must observe all 16 poses")
    sampled = actor.get("sampledPosesPerDirection", {})
    require(set(sampled) == set(gate.DIRECTIONS) and all(type(n) is int and n >= 0 for n in sampled.values())
            and sum(sampled.values()) == max(sampled.values()) == 16, "Actual sampled route differs")
    names = actor.get("observedWalkSpriteNames", [])
    require(len(names) == len(set(names)) == 16, "Actual moving sprite names are missing/duplicated")
    for field in ("controllerMoveSpeed", "actualCycleDurationMs", "actualCycleWorldDistance"):
        gate.near(actor.get(field), baseline[field], .01 if field == "actualCycleDurationMs" else .0001, field)
    gate.near(actor.get("actualFramesPerUnit"), baseline["actualFramesPerUnit"] * 2, .0001, "16-pose distance cadence")
    gate.near(actor["actualPathDistance"] / actor["movementSeconds"], actor["controllerMoveSpeed"], .15, "Actual speed")


def visual_review(path, report_path, snapshot_path, report, views, plan, stage_path):
    review = read(path)
    require(review.get("schema") == REVIEW_SCHEMA and review.get("status") == "passed"
            and isinstance(review.get("reviewer"), str) and review["reviewer"].strip(), "Mixed runtime visual review required")
    require(review.get("runtime_report_sha256") == sha(report_path) and
            review.get("input_snapshot_sha256") == sha(snapshot_path) and
            review.get("approval_receipt_sha256") == plan["approvalReceiptSha256"] and
            review.get("stage_audit_sha256") == sha(stage_path), "Runtime visual review bindings differ")
    require(gate.utc(report["generatedUtc"]) <= gate.utc(review["reviewed_utc"]) <= datetime.now(timezone.utc).timestamp(),
            "Runtime visual review predates capture or is in the future")
    require(review.get("mixed_geometry_reviewed") is True and review.get("preserved_idle_capture_acknowledged") is True
            and isinstance(review.get("mixed_geometry_notes"), str) and len(review["mixed_geometry_notes"].strip()) >= 12,
            "Review must describe the mixed geometry and acknowledge the actual preserved idle captures")
    records = review.get("views", [])
    keys = [(r.get("character_id"), r.get("view")) for r in records]
    require(len(keys) == len(set(keys)) and set(keys) == set(views), "Runtime visual review view coverage differs")
    for record in records:
        observed = views[(record["character_id"], record["view"])]
        require(record.get("status") == "passed" and record.get("image_sha256") == observed["imageSha256"]
                and record.get("clipping_reviewed") is True and
                type(record.get("full_frame_inside_capture")) is bool and
                record["full_frame_inside_capture"] == observed["fullFrameInsideCapture"] and
                isinstance(record.get("notes"), str) and len(record["notes"].strip()) >= 12,
                "Runtime screenshot lacks exact SHA/clipping/visual review")
    return sha(path)


def formal_character_baseline(formal_rows, staged_at_utc):
    """Pin old formal resources to their own retained baseline, including metas.

    The prior source rows describe the pre-sync code and are validated for scope,
    not compared to current code. Current code has its separate 50-file binding.
    No replacement baseline can silently bless changed old resources.
    """
    path = safe_child(RUNS, FORMAL_BASELINE_RELATIVE)
    require(sha(path) == FORMAL_BASELINE_SHA256, "Formal safety baseline bytes changed or unrecognized")
    document = read(path)
    require(document.get("schema") == 1 and Path(document.get("project", "")).resolve() == FORMAL.resolve()
            and document.get("scope") == FORMAL_BASELINE_SCOPE
            and document.get("prior_review_sha256") == FORMAL_BASELINE_PRIOR_REVIEW_SHA256,
            "Formal safety baseline identity/scope differs")
    require(gate.utc(document["created_utc"]) <= gate.utc(staged_at_utc)
            and gate.utc(document["created_utc"]) <= datetime.now(timezone.utc).timestamp(),
            "Formal safety baseline must precede this stage and cannot be future-dated")
    source_paths = document.get("source_paths", [])
    require(len(source_paths) == len(set(source_paths)) and set(source_paths) == set(gate.INPUT_BINDING_PATHS),
            "Formal safety baseline source scope differs")
    records = gate.snapshot_records(document)
    prefix = CHARACTERS + "/"
    resources = {p: row for p, row in records.items() if p.startswith(prefix)}
    require(len(resources) == document.get("character_resource_count") == FORMAL_BASELINE_CHARACTER_COUNT
            and set(records) == set(source_paths) | set(resources), "Formal safety baseline resource scope differs")
    for relative, row in records.items():
        require(relative == row.get("path") and "\\" not in relative and not Path(relative).is_absolute()
                and ".." not in Path(relative).parts and isinstance(row.get("sha256"), str)
                and re.fullmatch("[0-9a-f]{64}", row["sha256"])
                and type(row.get("bytes")) is int and row["bytes"] >= 0, "Invalid formal safety baseline row")
    current = {p: row for p, row in formal_rows.items() if p.startswith(prefix)}
    require(current == resources, "Formal old character inventory differs from its own safety baseline")
    # Read again so a concurrent baseline edit cannot survive the pinned-SHA check.
    require(sha(path) == FORMAL_BASELINE_SHA256, "Formal safety baseline changed during validation")
    return {p: row["sha256"] for p, row in resources.items()}, {
        "path": str(path), "sha256": FORMAL_BASELINE_SHA256, "createdUtc": document["created_utc"],
        "characterFileCount": len(resources), "scope": "Exact formal old character files, including every .meta"}


def stage_binding(stage_path, plan, rows, formal_rows):
    stage_path = approve.child_directory(stage_path, stage.AUDIT_ROOT)
    record = read(stage_path)
    target = ISOLATED / gate.FAMILY / plan["characterId"]
    require(record.get("schema") == stage.SCHEMA and record.get("status") == "staged_pending_real_unity_validation"
            and record.get("writesPerformed") is True and record.get("protected_changed_files") == 0 and
            record.get("formal_publication_authorized") is False and
            record.get("stage_tool_sha256") == sha(Path(stage.__file__)), "Unverified/stale isolated stage audit")
    require(record.get("character_id") == plan["characterId"] and Path(record["approved"]).resolve() == Path(plan["approved"])
            and Path(record["project"]).resolve() == ISOLATED.resolve() and Path(record["target"]).resolve() == target.resolve()
            and Path(record["audit"]).resolve() == stage_path and record.get("runtime_outputs") == plan["outputs"]
            and record.get("approved_inventory") == plan["approvedInventory"], "Stage belongs to different approval/target")
    prefix = CHARACTERS + "/"
    saved = record.get("protected_before")
    require(isinstance(saved, dict) and saved, "Missing isolated stage protection inventory")
    for relative, digest in saved.items():
        require(isinstance(relative, str) and relative and "\\" not in relative and not Path(relative).is_absolute()
                and ".." not in Path(relative).parts and isinstance(digest, str)
                and re.fullmatch("[0-9a-f]{64}", digest), "Invalid isolated stage protection row")
    protected = {prefix + p: digest for p, digest in saved.items()}
    formal, formal_binding = formal_character_baseline(formal_rows, record["staged_at_utc"])
    target_key = gate.FAMILY + "/" + plan["characterId"]
    require(not any(p.startswith(target_key + "/") or p == target_key + ".meta" for p in protected),
            "Stage protection inventory already contains the new target")
    created_metas = {target_key + ".meta"}
    if gate.FAMILY + ".meta" not in protected:
        created_metas.add(gate.FAMILY + ".meta")
    previous = {p: r["sha256"] for p, r in rows.items() if p.startswith(prefix)
                and not p.startswith(target_key + "/") and p not in created_metas}
    require(previous == protected, "Tested old characters changed since staging")
    # GUIDs and importer details are generated independently by each project.
    # They remain fully protected above, but are not author-supplied asset bytes.
    formal_authored = {p: h for p, h in formal.items() if not p.endswith(".meta")}
    isolated_authored = {p: h for p, h in protected.items() if not p.endswith(".meta")}
    require(formal_authored == isolated_authored, "Formal/isolated old authored character resources differ")
    protection = {
        "schema": "qdao-original-v14-mixed/separate-project-protection-v1",
        "formalSafetyBaseline": formal_binding, "formalOldFileCount": len(formal),
        "isolatedOldFileCount": len(protected), "crossProjectAuthoredFileCount": len(formal_authored),
        "formalMetaFileCount": sum(p.endswith(".meta") for p in formal),
        "isolatedMetaFileCount": sum(p.endswith(".meta") for p in protected),
        "crossProjectDifferentMetaCount": sum(formal.get(p) != protected.get(p)
            for p in set(formal) | set(protected) if p.endswith(".meta")),
        "formalOldInventorySha256": hashlib.sha256(encoded(dict(sorted(formal.items())))).hexdigest(),
        "isolatedStageInventorySha256": hashlib.sha256(encoded(dict(sorted(protected.items())))).hexdigest(),
        "metaPolicy": "Every old meta matches its own project baseline; no cross-project GUID/importer equivalence or copying"}
    return {**record, "verified_legacy_protection": protection}


def runtime_acceptance(plan, run, review_path, stage_path, formal_rows):
    documents = {name: read(run / name) for name in ("input-editmode.json", "input-playmode.json", "post-playmode.json")}
    by = {name: snapshot_rows(doc) for name, doc in documents.items()}
    rows = by["input-playmode.json"]
    require(all(data == rows for data in by.values()), "Edit/Play/post full inputs differ")
    runner = ROOT.parent / "qdao_original_roster_v13/tools/run_unity_tests.ps1"
    capture = runner.with_name("capture_unity_inputs.py")
    for document in documents.values():
        require(Path(document["project"]).resolve() == ISOLATED.resolve()
                and document.get("capture_tool_sha256") == sha(capture)
                and document.get("unity_runner_sha256") == sha(runner), "Snapshot project/capture/runner binding differs")
    require(tree_inventory(ISOLATED, INPUT_ROOTS) == rows, "Current isolated inputs differ from completed test run")
    for path in BINDINGS:
        require(path in rows and path in formal_rows and formal_rows[path]["sha256"] == rows[path]["sha256"],
                "Formal source/meta/camera differs from actual tested source: " + path)
    staged = stage_binding(stage_path, plan, rows, formal_rows)
    report_path = run / "city-captures/runtime-observed-appearances.json"
    report = read(report_path)
    snapshot_path = run / "input-playmode.json"
    require(report.get("schemaVersion") == 2 and report.get("behaviorAssertionsCompleted") is True and
            Path(report["projectPath"]).resolve() == ISOLATED.resolve() and
            Path(report["inputSnapshotPath"]).resolve() == snapshot_path and
            report.get("inputSnapshotSha256") == sha(snapshot_path), "Runtime observation is not bound to this fresh input")
    evidence = {}
    for platform, stem in (("EditMode", "editmode"), ("PlayMode", "playmode")):
        xml = run / (stem + ".xml")
        check_unity_results(xml, platform)
        launch = gate.check_launch_binding(xml, report, rows, [plan],
                    sha(snapshot_path) if platform == "PlayMode" else None, platform)
        input_path = run / ("input-" + stem + ".json")
        require(Path(launch["input_snapshot"]).resolve() == input_path and
                Path(launch["capture_directory"]).resolve() == report_path.parent,
                "Actual run launch paths differ")
        completion = read(run / (stem + "-completion.json"))
        require(gate.utc(staged["staged_at_utc"]) <= gate.utc(documents[input_path.name]["created_utc"]) <=
                gate.utc(launch["started_utc"]), "Run input predates approved asset staging or follows launch")
        require(gate.utc(completion["finished_utc"]) <= gate.utc(documents["post-playmode.json"]["created_utc"]) <=
                datetime.now(timezone.utc).timestamp(), "Post snapshot predates test completion or is in the future")
        evidence[platform] = {name: sha(run / (stem + suffix)) for name, suffix in
            (("xml", ".xml"), ("launch", "-launch.json"), ("completion", "-completion.json"), ("log", ".log"))}
    require(gate.utc(read(run / "editmode-completion.json")["finished_utc"]) <=
            gate.utc(documents["input-playmode.json"]["created_utc"]), "Play input must follow completed Edit run")
    gate.check_runtime_inventory(rows, plan, require_index=True)
    baseline_path = RUNS / "contract-run1/city-captures/runtime-observed-appearances.json"
    baseline_input = RUNS / "input-snapshot-run1-playmode.json"
    baseline = read(baseline_path)
    require(baseline.get("behaviorAssertionsCompleted") is True and baseline.get("inputSnapshotSha256") == sha(baseline_input),
            "Real V12 movement baseline is unbound")
    old = next((a for a in baseline["appearances"] if a.get("actualCharacterId") == "24_lu_dongbin"), None)
    require(old and old.get("actualArtworkVersion") == 12 and old.get("actualFrameCount") == 8 and
            all(old.get(k) is True for k in ("movementObserved", "stoppedIdle", "realMotorEnabled")), "Missing real V12 motor baseline")
    require(gate.snapshot_records(read(baseline_input))[gate.CONTROLLER]["sha256"] == rows[gate.CONTROLLER]["sha256"],
            "Movement controller changed since actual baseline")
    actors = report.get("appearances", [])
    ids = [a.get("actualCharacterId") for a in actors]
    require(len(ids) == len(set(ids)) == report.get("selectedAppearanceCount"), "Duplicated/unobserved selected appearances")
    originals = [a for a in actors if a.get("actualIsOriginalRoster") is True]
    mixed = [a for a in originals if a.get("actualIsMixedResolution") is True]
    full_hd = [a for a in originals if a.get("actualIsHd") is True]
    require(report.get("testedOriginalCount") == len(originals) == 5 and
            report.get("testedMixedOriginalCount") == len(mixed) == 1 and
            report.get("testedHdOriginalCount") == len(full_hd) == 0, "First mixed04 run must observe old00-03 plus real mixed04")
    old_ids = {p.name for p in (FORMAL / CHARACTERS / "QdaoOriginalRosterV13").iterdir() if p.is_dir()}
    require({a["actualCharacterId"] for a in originals if a not in mixed} == old_ids and len(old_ids) == 4 and
            all(a.get("actualArtworkVersion") == 13 and a.get("v13SixteenFrameContractObserved") is True and
                a.get("actualFramesMatchResources") is True and a.get("actualIdleMatchResources") is True and
                a.get("movementObserved") is True and a.get("stoppedIdle") is True
                for a in originals if a not in mixed), "Preserved original00-03 regression observations incomplete")
    actor_check(mixed[0], plan, old)
    camera = gate.camera_contract(FORMAL)
    require(camera["minimum"] < camera["default"], "Nearest camera view is not closer")
    # Check every normal capture for regressions; the reviewed pair belongs to 04.
    for actor in actors:
        gate.check_runtime_view(actor, "normalView", report_path.parent, camera)
    views = {(plan["characterId"], name): gate.check_runtime_view(mixed[0], name, report_path.parent, camera)
             for name in ("normalView", "nearestView")}
    review_sha = visual_review(review_path, report_path, snapshot_path, report, views, plan, stage_path)
    return {"unityEvidence": evidence, "snapshotSha256": {p: sha(run / p) for p in documents},
            "inputFileCount": len(rows), "runtimeReportSha256": sha(report_path), "runtimeVisualReviewSha256": review_sha,
            "legacyProtection": staged["verified_legacy_protection"],
            "stageAuditSha256": sha(stage_path), "baselineReportSha256": sha(baseline_path),
            "baselineInputSha256": sha(baseline_input), "sourceBindings": {p: rows[p]["sha256"] for p in BINDINGS},
            "testedOriginalCount": 5, "testedMixedOriginalCount": 1, "testedHdOriginalCount": 0,
            "runtimeViews": [{"characterId": key[0], "view": key[1], **value} for key, value in views.items()],
            "captureFrameSize": [mixed[0]["actualFrameWidth"], mixed[0]["actualFrameHeight"]],
            "captureScope": "Actual preserved stopped idle; new native walk detail reviewed in the sealed offline assembly"}


def prepare(arguments):
    project = exact_project(arguments.project, FORMAL)
    exact_project(ISOLATED, ISOLATED)
    approved = approve.child_directory(arguments.approved, approve.APPROVED_ROOT)
    checked = approve.verify_approved(approved)
    character = checked["character_id"]
    require(character in ALLOWED_IDS, "This first-publication workflow supports Original04 only")
    outputs = checked["runtime_outputs"]
    require(set(outputs) == gate.EXPECTED_OUTPUTS and len(outputs) == 140, "Exact 137 PNG plus three JSON required")
    target = safe_child(project, gate.FAMILY + "/" + character)
    require(not target.exists() and not target.with_suffix(".meta").exists(), "Existing character or GUID may never be replaced")
    audit = approve.child_directory(arguments.audit, AUDITS)
    require(audit.suffix == ".json" and not audit.exists(), "Choose a new publication JSON audit")
    run = approve.child_directory(arguments.run, RUNS)
    require(run.parent == RUNS.resolve(), "Use a direct new runtime-validation run")
    review = approve.child_directory(arguments.runtime_visual_review, run)
    plan = {"characterId": character, "approved": str(approved), "project": str(project), "target": str(target),
            "audit": str(audit), "run": str(run), "outputs": outputs, "manifest": read(approved / "manifest.json"),
            "manifestSha256": sha(approved / "manifest.json"), "qcSha256": sha(approved / "qc.json"),
            "validationSha256": sha(approved / "validation.json"), "approvalReceiptSha256": sha(approved / "approval.json"),
            "approvedInventory": file_inventory(approved)}
    plan["protectedFormal"] = tree_inventory(project, FORMAL_ROOTS)
    plan["runtimeAcceptance"] = runtime_acceptance(plan, run, review, arguments.stage_audit, plan["protectedFormal"])
    plan["toolSha256"] = {Path(module.__file__).name: sha(Path(module.__file__))
        for module in (approve, approve.assembly, gate, stage)}
    plan["toolSha256"][Path(__file__).name] = sha(Path(__file__))
    plan["toolSha256"]["review_mixed_client_run.py"] = sha(Path(__file__).with_name("review_mixed_client_run.py"))
    require(file_inventory(approved) == plan["approvedInventory"], "Approval changed during publication checks")
    require(tree_inventory(project, FORMAL_ROOTS) == plan["protectedFormal"], "Formal inputs changed during publication checks")
    return plan


def write_audit(stream, document):
    stream.seek(0)
    stream.write(encoded(document))
    stream.truncate()
    stream.flush()
    os.fsync(stream.fileno())


def execute(plan, arguments):
    require(prepare(arguments) == plan, "Publication inputs changed after preflight")
    project, target, audit = Path(plan["project"]), Path(plan["target"]), Path(plan["audit"])
    family = safe_child(project, gate.FAMILY)
    temporary = safe_child(project, gate.FAMILY + "/.mixed-publish-" + uuid.uuid4().hex)
    audit.parent.mkdir(parents=True, exist_ok=True)
    activated = created = False
    receipt = {**plan, "schema": SCHEMA, "status": "publishing", "writesPerformed": False}
    with audit.open("xb") as stream:
        try:
            write_audit(stream, receipt)
            family.mkdir(parents=True, exist_ok=True)
            temporary.mkdir()
            created = True
            for relative, digest in sorted(plan["outputs"].items(), key=lambda item: item[0] == "appearance.json"):
                source = safe_child(plan["approved"], relative)
                require(sha(source) == digest, "Approved bytes changed during publication")
                destination = safe_child(temporary, relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                require(sha(destination) == digest, "Copied runtime bytes differ")
            require(file_inventory(temporary) == plan["outputs"], "Temporary runtime set differs")
            require(file_inventory(plan["approved"]) == plan["approvedInventory"], "Approval changed during copy")
            stage.editor_closed(project)
            require(tree_inventory(project, FORMAL_ROOTS, temporary) == plan["protectedFormal"], "Protected formal inputs changed")
            require(not target.exists() and not target.with_suffix(".meta").exists(), "Target/GUID appeared concurrently")
            # Both absolute paths have been confined to the fixed family, and only
            # this new temporary directory is moved. No existing files are replaced.
            require(temporary.parent == target.parent == family and temporary.name.startswith(".mixed-publish-"), "Unsafe promotion")
            os.rename(temporary, target)
            created, activated = False, True
            require(file_inventory(target) == plan["outputs"], "Promoted runtime bytes differ")
            require(tree_inventory(project, FORMAL_ROOTS, target) == plan["protectedFormal"], "Unrelated formal inputs changed")
            receipt.update(status="published_pending_formal_editor_import", writesPerformed=True,
                publishedUtc=datetime.now(timezone.utc).isoformat(), protectedChangedFiles=0,
                formalEditorRun=False, derivedIndexCopied=False, authoredFileCount=140)
            write_audit(stream, receipt)
            return receipt
        except Exception as error:
            receipt.update(status="failed_after_target_activation" if activated else "failed_before_activation",
                           writesPerformed=created or activated, targetRetained=activated, error=str(error))
            try:
                write_audit(stream, receipt)
            except OSError:
                pass
            if activated:
                raise RuntimeError("Publication failed after activation; target retained; inspect " + str(audit)) from error
            raise
        finally:
            if created and temporary.exists():
                safe_child(project, temporary.relative_to(project))
                require(temporary.parent == family and temporary.name.startswith(".mixed-publish-"), "Unsafe temporary cleanup")
                shutil.rmtree(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved", required=True, type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--stage-audit", required=True, type=Path)
    parser.add_argument("--runtime-visual-review", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    arguments = parser.parse_args(argv)
    plan = prepare(arguments)
    result = execute(plan, arguments) if arguments.execute else {
        **plan, "schema": SCHEMA, "status": "ready_dry_run", "writesPerformed": False}
    omitted = {"outputs", "manifest", "approvedInventory", "protectedFormal"}
    summary = {k: v for k, v in result.items() if k not in omitted}
    summary.update(authoredFileCount=140, protectedFileCount=len(plan["protectedFormal"]))
    print(__import__("json").dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(__import__("json").dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
