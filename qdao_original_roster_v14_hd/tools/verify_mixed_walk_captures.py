"""Read-only binding checks for real mixed04-06 native gameplay captures.

This is a required publisher gate; it does not publish, approve artwork,
produce screenshots, or replace a full current-input publication preflight.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import publish_mixed_roster as publisher

gate = publisher.gate
require, read, sha = gate.require, gate.read, gate.sha
CHARACTER = "04_mountain_guardian_boy"
SCHEMA = "qdao-original-v14-mixed/native-walk-capture-check-v1"
TEST_SOURCES = (
    "Assets/Tests/PlayMode/QdaoRosterAnimatorPlayModeTests.cs",
    "Assets/Tests/PlayMode/QdaoRosterSandboxPlayModeTests.cs",
)


def native_targets(manifest):
    files = manifest.get("files", [])
    require(len({row["path"] for row in files}) == len(files), "Duplicate manifest paths")
    result = []
    for direction in gate.DIRECTIONS:
        candidates = [n for n in range(1, 17) if any(row.get("path") == f"walk/{direction}/{n:02d}.png"
                      and row.get("source_kind") == "native-hd" for row in files)]
        if candidates:
            result.append((direction, min(candidates)))
    require(len(result) >= 2, "Native walking evidence requires at least two native directions")
    return result


def check_frames(actor, rows, manifest, snapshot_sha, capture_root, camera, started_utc, generated_utc):
    character = actor.get("actualCharacterId")
    require(character in publisher.ALLOWED_IDS and actor.get("actualIsMixedResolution") is True,
            "Required real mixed04-06 actor missing")
    targets = native_targets(manifest)
    captures = actor.get("walkFrameCaptures")
    require(isinstance(captures, list) and len(captures) == len(targets), "Exactly all declared native direction captures are required")
    indexed = {(entry.get("direction"), entry.get("frameNumber")): entry for entry in captures}
    require(set(indexed) == set(targets), "Duplicate, missing or wrong native walk target")
    declarations = {row["path"]: row for row in manifest["files"]}
    require(len(declarations) == len(manifest["files"]), "Duplicate manifest paths")
    prefix = gate.RESOURCE_FAMILY + "/" + character + "/"
    result = []
    previous_frame = -1
    for direction, number in targets:
        entry = indexed[direction, number]
        relative = f"walk/{direction}/{number:02d}.png"
        resource = prefix + relative[:-4]
        input_path = "Assets/Resources/" + resource + ".png"
        declared = declarations.get(relative, {})
        require(entry.get("characterId") == character and entry.get("resourcePath") == resource and
                entry.get("inputSnapshotSha256") == snapshot_sha, "Walk identity/resource/input binding differs")
        require(declared.get("source_kind") == "native-hd" and declared.get("width") == declared.get("height") == 1024 and
                declared.get("pixels_per_unit") == 104 and input_path in rows and
                declared.get("sha256") == rows[input_path]["sha256"] == entry.get("resourcePngSha256"),
                "Walk source must match the actual input and native manifest SHA/geometry")
        require(entry.get("textureWidth") == entry.get("textureHeight") == 1024,
                "The rendered walking texture must actually be 1024")
        gate.near(entry.get("pixelsPerUnit"), 104, .0001, "Native walk PPU")
        gate.near(entry.get("frameWorldHeight"), 512 / 52, .0001, "Native walk world height")
        for axis, value in (("x", .5), ("y", .08)):
            gate.near(entry.get("normalizedPivot", {}).get(axis), value, .0001, "Walk normalized pivot")
        for axis in ("x", "y", "z"):
            gate.near(entry.get("billboardScale", {}).get(axis), 1, .0001, "Walk billboard scale")
        require(entry.get("locomotionState") == "Run" and entry.get("realMotorEnabled") is True and
                entry.get("matchesExpectedResource") is True, "Capture must show an actual running real-motor resource")
        distance, seconds = entry.get("pathDistance"), entry.get("movementSeconds")
        require(gate.finite_number(distance) and .05 < distance <= 10 and
                gate.finite_number(seconds) and 0 < seconds <= 1, "Unmeasured/invalid walking capture interval")
        gate.near(distance / seconds, actor.get("controllerMoveSpeed"), .15, "Actual capture interval movement speed")
        start, end = entry.get("routeStart", {}), entry.get("captureFeet", {})
        require(all(gate.finite_number(point.get(axis)) for point in (start, end) for axis in ("x", "y", "z")),
                "Walking route coordinates are not finite")
        travel = ((end["x"] - start["x"]) ** 2 + (end["z"] - start["z"]) ** 2) ** .5
        require(.05 < travel <= distance + .001, "Setup warp/stationary position cannot stand in for measured walking")
        require(type(entry.get("simulationFrame")) is int and entry["simulationFrame"] > previous_frame,
                "Walk captures must identify distinct ordered simulation frames")
        previous_frame = entry["simulationFrame"]
        require(gate.utc(started_utc) <= gate.utc(entry["generatedUtc"]) <= gate.utc(generated_utc),
                "Walking capture timestamp is outside the fresh run observation interval")
        # Reuse the existing checked PNG/projection implementation. This local
        # name only selects the explicit walking filename, not another actor.
        view_actor = {"actualCharacterId": f"{character}-walk-{direction}-{number:02d}",
                      "actualFrameHeight": 1024, "actualFrameWorldHeight": entry["frameWorldHeight"],
                      "normalView": entry.get("normalView"), "nearestView": entry.get("nearestView")}
        for name in ("normalView", "nearestView"):
            view = gate.check_runtime_view(view_actor, name, capture_root, camera)
            result.append({"character_id": character, "direction": direction, "frame_number": number,
                           "resource_path": resource, "resource_sha256": entry["resourcePngSha256"],
                           "simulation_frame": entry["simulationFrame"], "view": name, **view})
    return result


def verify(run, character=CHARACTER):
    require(character in publisher.ALLOWED_IDS, "Only retained mixed04-06 may be checked")
    run = publisher.approve.child_directory(Path(run), publisher.RUNS)
    require(run.parent == publisher.RUNS.resolve(), "Use the exact new runtime-validation run directory")
    report_path = run / "city-captures/runtime-observed-appearances.json"
    snapshot_path = run / "input-playmode.json"
    report, snapshot = read(report_path), read(snapshot_path)
    rows = publisher.snapshot_rows(snapshot)
    require(Path(snapshot["project"]).resolve() == publisher.ISOLATED.resolve() and
            Path(report["projectPath"]).resolve() == publisher.ISOLATED.resolve() and
            Path(report["inputSnapshotPath"]).resolve() == snapshot_path and
            report.get("schemaVersion") == 2 and report.get("behaviorAssertionsCompleted") is True and
            report.get("inputSnapshotSha256") == sha(snapshot_path), "Wrong or unfinished report/input binding")
    for relative in publisher.BINDINGS:
        require(relative in rows and rows[relative]["sha256"] == sha(publisher.ISOLATED / relative),
                "Actual tested source/config/meta differs from the current isolated source: " + relative)
    xml = run / "playmode.xml"
    publisher.check_unity_results(xml, "PlayMode")
    launch = gate.check_launch_binding(xml, report, rows, [], sha(snapshot_path), "PlayMode")
    require(Path(launch["input_snapshot"]).resolve() == snapshot_path and
            Path(launch["capture_directory"]).resolve() == report_path.parent,
            "Walk screenshots must belong to the exact fresh PlayMode launch")
    actors = [actor for actor in report["appearances"] if actor.get("actualCharacterId") == character]
    require(len(actors) == 1, "Missing or duplicate runtime mixed actor")
    actor = actors[0]
    manifest_relative = gate.FAMILY + "/" + character + "/manifest.json"
    manifest_path = gate.safe_child(publisher.ISOLATED, manifest_relative)
    require(manifest_relative in rows and rows[manifest_relative]["sha256"] == sha(manifest_path) == actor.get("manifestSha256"),
            "Current runtime manifest differs from the actual tested/loaded manifest")
    manifest = read(manifest_path)
    views = check_frames(actor, rows, manifest, sha(snapshot_path), report_path.parent,
                        gate.camera_contract(publisher.ISOLATED), launch["started_utc"], report["generatedUtc"])
    for view in views:
        resource = "Assets/Resources/" + view["resource_path"] + ".png"
        require(sha(gate.safe_child(publisher.ISOLATED, resource)) == view["resource_sha256"],
                "Native source PNG changed since the actual run")
    return {"schema": SCHEMA, "status": "bound_evidence_requires_visual_review",
            "checked_utc": datetime.now(timezone.utc).isoformat(), "run": str(run),
            "runtime_report_sha256": sha(report_path), "input_snapshot_sha256": sha(snapshot_path),
            "manifest_sha256": sha(manifest_path), "playmode_xml_sha256": sha(xml),
            "test_sources": {path: rows[path]["sha256"] for path in TEST_SOURCES}, "views": views,
            "scope": "File/input/geometry/movement assertion bindings only; requires actual normal/nearest visual review for every declared native walking direction and the full publication gate. No art or publication approval."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--character", choices=sorted(publisher.ALLOWED_IDS), default=CHARACTER)
    args = parser.parse_args()
    print(json.dumps(verify(args.run, args.character), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
