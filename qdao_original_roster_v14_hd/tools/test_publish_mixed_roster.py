"""Synthetic gate tests, confined to temporary tools directories.

The heavy source/visual-approved verifier is mocked ONLY in the whole-workflow
fixture. Real approval/reconstruction is covered by the existing independent
assemble/approve suites. No fixture is real artwork, a Unity run, or approval.
"""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from PIL import Image
import publish_mixed_roster as pub


class MixedPublicationTests(unittest.TestCase):
    def setUp(self):
        self.owner = Path(__file__).resolve().parent
        self.temp = tempfile.TemporaryDirectory(prefix="mixed-publish-unit-", dir=self.owner)
        self.root = Path(self.temp.name).resolve()
        self.work = self.root / "work"
        self.v14 = self.work / "image/qdao_original_roster_v14_hd"
        self.formal = self.work / "mmorpg-client"
        self.isolated = self.work / "tmp/qdao-original-live-candidate-20260917"
        self.runs = self.work / "image/qdao_original_roster_v13/runtime-validation"
        self.run = self.runs / "unit-real-run-shape-not-real-evidence"
        self.character = "04_mountain_guardian_boy"
        self.approved = self.v14 / "mixed-approved/unit-fixture" / self.character
        self.stage_path = self.v14 / "mixed-stage-audits/unit-fixture.json"
        self.audit = self.v14 / "mixed-publication-audits/unit-fixture.json"
        self.review = self.run / "runtime-visual-review.json"
        self.patches = [patch.object(pub, "WORK", self.work), patch.object(pub, "ROOT", self.v14),
            patch.object(pub, "FORMAL", self.formal), patch.object(pub, "ISOLATED", self.isolated),
            patch.object(pub, "RUNS", self.runs), patch.object(pub, "AUDITS", self.audit.parent),
            patch.object(pub.approve, "APPROVED_ROOT", self.v14 / "mixed-approved"),
            patch.object(pub.stage, "AUDIT_ROOT", self.stage_path.parent)]
        for item in self.patches:
            item.start()
        self.addCleanup(self.cleanup)
        for project in (self.formal, self.isolated):
            for name in pub.INPUT_ROOTS:
                (project / name).mkdir(parents=True, exist_ok=True)
            self.write(project / "ProjectSettings/ProjectVersion.txt", b"UNIT FIXTURE ONLY\n")
            for name in pub.BINDINGS:
                content = ("cameraZoomMin: 5\ncameraZoomMax: 30\ncameraZoomDefault: 27\n" if name == pub.gate.CAMERA_CONFIG
                           else "Synthetic bound input " + name + "\n")
                self.write(project / name, content.encode())
        self.old_ids = ["00_unit_preserved", "01_unit_preserved", "02_unit_preserved", "03_unit_preserved"]
        for character in self.old_ids:
            for project in (self.formal, self.isolated):
                self.write(project / pub.CHARACTERS / "QdaoOriginalRosterV13" / character / "fixture.txt",
                           ("UNIT OLD RESOURCE ONLY " + character).encode())
        protected = pub.file_inventory(self.isolated / pub.CHARACTERS)
        formal_baseline_rows = [{"path": p, "sha256": "a" * 64, "bytes": 1}
                                for p in pub.gate.INPUT_BINDING_PATHS]
        formal_baseline_rows += [{"path": pub.CHARACTERS + "/" + p, "sha256": digest,
                                 "bytes": (self.formal / pub.CHARACTERS / p).stat().st_size}
                                for p, digest in protected.items()]
        formal_baseline = self.runs / pub.FORMAL_BASELINE_RELATIVE
        self.save(formal_baseline, {"schema": 1, "created_utc": "2025-12-31T00:00:00Z",
            "project": str(self.formal), "scope": pub.FORMAL_BASELINE_SCOPE,
            "prior_review_sha256": pub.FORMAL_BASELINE_PRIOR_REVIEW_SHA256,
            "source_paths": list(pub.gate.INPUT_BINDING_PATHS), "character_resource_count": len(protected),
            "files": formal_baseline_rows, "test_fixture": "Synthetic old formal baseline, never real protection evidence"})
        for item in (patch.object(pub, "FORMAL_BASELINE_SHA256", pub.sha(formal_baseline)),
                     patch.object(pub, "FORMAL_BASELINE_CHARACTER_COUNT", len(protected))):
            item.start()
            self.patches.append(item)
        declarations = []
        for relative in sorted(pub.gate.EXPECTED_PNGS):
            width = 1024 if relative == "portrait.png" or relative.startswith(("walk/SW/", "walk/NW/")) and int(Path(relative).stem) % 4 != 1 else 512
            self.write(self.approved / relative, ("UNIT NONIMAGE RUNTIME HASH FIXTURE " + relative).encode())
            declarations.append({"path": relative, "width": width, "height": width, "pixels_per_unit": 104 if width == 1024 else 52,
                "source_kind": "native-hd" if width == 1024 else "preserved-v13", "sha256": pub.sha(self.approved / relative)})
        self.manifest = {"files": declarations}
        self.save(self.approved / "manifest.json", self.manifest)
        for name in ("validation.json", "qc.json", "approval.json", "appearance.json"):
            self.save(self.approved / name, {"scope": "SYNTHETIC MOCKED LOWER LEVEL; NOT ARTWORK OR APPROVAL", "file": name})
        self.outputs = {p: pub.sha(self.approved / p) for p in pub.gate.EXPECTED_OUTPUTS}
        self.checked = {"character_id": self.character, "runtime_outputs": self.outputs}
        self.verify = patch.object(pub.approve, "verify_approved", return_value=self.checked).start()
        self.addCleanup(patch.stopall)
        target = self.isolated / pub.gate.FAMILY / self.character
        for relative, digest in self.outputs.items():
            self.write(target / relative, (self.approved / relative).read_bytes())
            self.write(target / (relative + ".meta"), ("UNIT META " + relative).encode())
        for relative in ("runtime-index.asset", "runtime-index.asset.meta", "walk.meta", "idle.meta"):
            self.write(target / relative, ("UNIT DERIVED DATA " + relative).encode())
        for direction in pub.gate.DIRECTIONS:
            self.write(target / ("walk/" + direction + ".meta"), b"UNIT DIRECTORY META")
        self.write(target.with_suffix(".meta"), b"UNIT TARGET META")
        self.write(target.parent.with_suffix(".meta"), b"UNIT FAMILY META")
        self.stage_record = {"schema": pub.stage.SCHEMA, "status": "staged_pending_real_unity_validation",
            "writesPerformed": True, "protected_changed_files": 0, "formal_publication_authorized": False,
            "stage_tool_sha256": pub.sha(Path(pub.stage.__file__)), "character_id": self.character,
            "approved": str(self.approved), "project": str(self.isolated), "target": str(target), "audit": str(self.stage_path),
            "runtime_outputs": self.outputs, "approved_inventory": pub.file_inventory(self.approved),
            "protected_before": protected, "staged_at_utc": "2026-01-01T00:00:00Z"}
        self.save(self.stage_path, self.stage_record)
        runner = self.v14.parent / "qdao_original_roster_v13/tools/run_unity_tests.ps1"
        self.write(runner, b"UNIT RUNNER FILE BINDING, NOT EXECUTABLE")
        self.write(runner.with_name("capture_unity_inputs.py"), b"UNIT CAPTURE FILE BINDING, NOT EXECUTABLE")
        self.snapshot()
        self.actor = self.actor_fixture()
        old_actors = [{"actualCharacterId": character, "actualIsOriginalRoster": True, "actualArtworkVersion": 13,
            "v13SixteenFrameContractObserved": True, "actualFramesMatchResources": True, "actualIdleMatchResources": True,
            "movementObserved": True, "stoppedIdle": True, "actualFrameWorldHeight": 512 / 52,
            "actualFrameHeight": 512} for character in self.old_ids]
        # One reusable noise image makes honest format/SHA tests without real art.
        self.noise = self.root / "unit-noise.png"
        Image.effect_noise((1920, 1080), 30).convert("RGB").save(self.noise)
        for actor in old_actors + [self.actor]:
            self.view(actor, "normalView")
        self.view(self.actor, "nearestView")
        self.actor["walkFrameCaptures"] = []
        for n, direction in enumerate(("SW", "NW")):
            resource = pub.gate.RESOURCE_FAMILY + "/" + self.character + f"/walk/{direction}/02"
            moving = {"actualCharacterId": self.character + f"-walk-{direction}-02", "actualFrameHeight": 1024}
            for name in ("normalView", "nearestView"):
                self.view(moving, name)
            self.actor["walkFrameCaptures"].append({"characterId": self.character, "direction": direction, "frameNumber": 2,
                "resourcePath": resource, "resourcePngSha256": self.rows["Assets/Resources/" + resource + ".png"]["sha256"],
                "inputSnapshotSha256": pub.sha(self.run / "input-playmode.json"), "textureWidth": 1024, "textureHeight": 1024,
                "pixelsPerUnit": 104, "frameWorldHeight": 512 / 52, "normalizedPivot": {"x": .5, "y": .08},
                "billboardScale": {"x": 1, "y": 1, "z": 1}, "locomotionState": "Run", "realMotorEnabled": True,
                "matchesExpectedResource": True, "pathDistance": .45, "movementSeconds": .05,
                "routeStart": {"x": 0, "y": 0, "z": 0}, "captureFeet": {"x": .45, "y": 0, "z": 0},
                "simulationFrame": 100 + n * 35, "generatedUtc": "2026-01-01T00:00:08Z",
                "normalView": moving["normalView"], "nearestView": moving["nearestView"]})
        self.report = {"schemaVersion": 2, "behaviorAssertionsCompleted": True,
            "projectPath": str(self.isolated), "inputSnapshotPath": str(self.run / "input-playmode.json"),
            "inputSnapshotSha256": pub.sha(self.run / "input-playmode.json"), "generatedUtc": "2026-01-01T00:00:08Z",
            "selectedAppearanceCount": 5, "testedOriginalCount": 5, "testedMixedOriginalCount": 1,
            "testedHdOriginalCount": 0, "appearances": old_actors + [self.actor]}
        self.report_path = self.run / "city-captures/runtime-observed-appearances.json"
        self.save(self.report_path, self.report)
        self.baseline = {"actualCharacterId": "24_lu_dongbin", "actualArtworkVersion": 12, "actualFrameCount": 8,
            "movementObserved": True, "stoppedIdle": True, "realMotorEnabled": True, "controllerMoveSpeed": 9,
            "actualCycleDurationMs": 480, "actualCycleWorldDistance": 4.32, "actualFramesPerUnit": 8 / 4.32}
        baseline_input = self.runs / "input-snapshot-run1-playmode.json"
        self.save(baseline_input, {"files": [self.rows[pub.gate.CONTROLLER]]})
        self.save(self.runs / "contract-run1/city-captures/runtime-observed-appearances.json",
            {"behaviorAssertionsCompleted": True, "inputSnapshotSha256": pub.sha(baseline_input), "appearances": [self.baseline]})
        for platform in ("EditMode", "PlayMode"):
            self.xml_and_launch(platform)
        self.review_fixture()
        self.arguments = SimpleNamespace(project=self.formal, approved=self.approved, run=self.run,
            audit=self.audit, stage_audit=self.stage_path, runtime_visual_review=self.review)

    def cleanup(self):
        patch.stopall()
        assert self.root.parent == self.owner and self.root.name.startswith("mixed-publish-unit-")
        self.temp.cleanup()

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def save(self, path, data):
        self.write(path, pub.encoded(data))

    def snapshot(self):
        self.rows = pub.tree_inventory(self.isolated, pub.INPUT_ROOTS)
        runner = self.v14.parent / "qdao_original_roster_v13/tools/run_unity_tests.ps1"
        for name, second in (("input-editmode.json", 1), ("input-playmode.json", 6), ("post-playmode.json", 11)):
            self.save(self.run / name, {"project": str(self.isolated), "shared_writable_links": False,
                "included_roots": list(pub.INPUT_ROOTS), "files": list(self.rows.values()), "count": len(self.rows),
                "bytes": sum(r["bytes"] for r in self.rows.values()), "created_utc": f"2026-01-01T00:00:{second:02d}Z",
                "capture_tool_sha256": pub.sha(runner.with_name("capture_unity_inputs.py")), "unity_runner_sha256": pub.sha(runner)})

    def actor_fixture(self):
        prefix = pub.gate.RESOURCE_FAMILY + "/" + self.character
        actor = {"requestedCharacterId": self.character, "actualCharacterId": self.character,
            "actualIsOriginalRoster": True, "actualIsMixedResolution": True, "v14MixedContractObserved": True,
            "actualIsHd": False, "v14HdContractObserved": False, "actualArtworkVersion": 14, "catalogVersion": 14,
            "actualFrameCount": 16, "catalogFrameDurationMs": 30, "activationAlignmentVersion": 2,
            "activationContactFrame": 0, "resourceFolder": prefix, "actualFrameWidth": 512, "actualFrameHeight": 512,
            "textureWidth": 512, "textureHeight": 512, "actualPixelsPerUnit": 52, "actualFrameWorldHeight": 512 / 52,
            "actualNormalizedPivot": {"x": .5, "y": .08}, "actualBillboardScale": {"x": 1, "y": 1, "z": 1},
            "expectedIdleResourcePath": prefix + "/idle/N", "maxResidentHdDirectionsObserved": 2,
            "actualTravelDistance": 4.8, "actualPathDistance": 4.8, "movementSeconds": 4.8 / 9,
            "observedWalkPoseCount": 16, "sampledPosesPerDirection": {d: 16 if d == "N" else 0 for d in pub.gate.DIRECTIONS},
            "observedWalkSpriteNames": ["UNIT POSE " + str(i) for i in range(16)], "controllerMoveSpeed": 9,
            "actualCycleDurationMs": 480, "actualCycleWorldDistance": 4.32, "actualFramesPerUnit": 16 / 4.32,
            "activationSha256": self.outputs["appearance.json"], "manifestSha256": self.outputs["manifest.json"],
            "activationManifestSha256": self.outputs["manifest.json"], "activationQcSha256": pub.sha(self.approved / "qc.json"),
            "activationValidationSha256": self.outputs["validation.json"]}
        actor["actualFrameGeometry"] = [{"resourcePath": prefix + "/" + row["path"][:-4], "width": row["width"],
            "height": row["height"], "pixelsPerUnit": row["pixels_per_unit"], "worldHeight": 512 / 52,
            "pivot": {"x": .5, "y": .08}} for row in self.manifest["files"] if row["path"] != "portrait.png"]
        for field in ("actualFramesPerDirection", "actualUniqueFrameSpritesPerDirection", "actualUniqueFrameTexturesPerDirection"):
            actor[field] = {d: 16 for d in pub.gate.DIRECTIONS}
        for field in ("actualTextureWidthsPerDirection", "actualTextureHeightsPerDirection"):
            actor[field] = {d: 0 if d in ("SW", "NW") else 512 for d in pub.gate.DIRECTIONS}
        actor["actualDedicatedIdleDirections"] = {d: 1 for d in pub.gate.DIRECTIONS}
        for field in ("activationPresent", "manifestPresent", "actualFramesMatchResources", "actualIdleMatchResources",
                      "actualHasDedicatedIdle", "spriteMatchesDedicatedIdle", "movementObserved", "stoppedIdle", "realMotorEnabled"):
            actor[field] = True
        return actor

    def view(self, actor, name):
        suffix = "-nearest-zoom" if name == "nearestView" else ""
        path = self.run / "city-captures" / ("tianyong-" + actor["actualCharacterId"] + suffix + ".png")
        self.write(path, self.noise.read_bytes())
        zoom = 5 if name == "nearestView" else 27
        height = 512 / 52 * 1080 / (2 * zoom)
        bottom = 540 - height * .08
        actor[name] = {"imagePath": str(path), "imageSha256": pub.sha(path), "renderWidth": 1920, "renderHeight": 1080,
            "configuredZoomMin": 5, "configuredZoomDefault": 27, "requestedZoom": zoom, "actualOrthographicSize": zoom,
            "frameLeftPixels": 960 - height / 2, "frameRightPixels": 960 + height / 2,
            "frameBottomPixels": bottom, "frameTopPixels": bottom + height, "projectedFrameHeightPixels": height,
            "screenPixelsPerTexturePixel": height / actor["actualFrameHeight"], "actorFeetScreenPixels": {"x": 960, "y": 540, "z": 110},
            "fullFrameInsideCapture": bottom + height <= 1080}

    def xml_and_launch(self, platform):
        second = 2 if platform == "EditMode" else 7
        methods = [pub.gate.HD_REQUIRED_METHODS[platform], pub.MIXED_METHODS[platform]]
        extra = [("MmorpgClient.Tests.EditMode.Tianyong.QdaoOriginalAppearanceTests",
                  "OriginalRegistryKeepsTwentyThreeIndependentIdsAndDoesNotRewriteExistingRosterOrLegacy")] if platform == "EditMode" else [
            ("MmorpgClient.Tests.PlayMode.QdaoRosterSandboxPlayModeTests", "RealCitySandbox_SwitchesAllAvailableAppearancesWithoutReplacingThePlayer_AndWalksWithTheRealMotor"),
            ("MmorpgClient.Tests.PlayMode.QdaoRosterAnimatorPlayModeTests", "EveryCharacter_WalksItsDeclaredFramesInAllEightDirections_AndSettlesOnItsIdlePose")]
        cases = [(cls, method, f"{cls}.{method}({i})") for cls, rows in methods for method, count in rows.items() for i in range(count)]
        cases += [(cls, method, cls + "." + method) for cls, method in extra]
        result = ET.Element("test-run", result="Passed", total=str(len(cases)), passed=str(len(cases)), failed="0", skipped="0",
            inconclusive="0", **{"start-time": f"2026-01-01T00:00:{second + 1:02d}Z", "end-time": f"2026-01-01T00:00:{second + 2:02d}Z"})
        for cls, method, name in cases:
            ET.SubElement(result, "test-case", classname=cls, methodname=method, fullname=name, result="Passed")
        stem = platform.lower()
        xml, log = self.run / (stem + ".xml"), self.run / (stem + ".log")
        ET.ElementTree(result).write(xml, encoding="utf-8")
        self.write(log, b"SYNTHETIC TEST FIXTURE. THIS IS NOT A UNITY LOG.")
        snapshot = self.run / ("input-" + stem + ".json")
        arguments = ["-projectPath", str(self.isolated), "-testPlatform", platform, "-testFilter", pub.gate.EXPECTED_FILTERS[platform],
                     "-testResults", str(xml), "-logFile", str(log)]
        self.save(self.run / (stem + "-launch.json"), {"platform": platform, "filter": pub.gate.EXPECTED_FILTERS[platform],
            "project": str(self.isolated), "input_snapshot": str(snapshot), "input_snapshot_sha256": pub.sha(snapshot),
            "capture_directory": str(self.run / "city-captures"), "arguments": arguments,
            "started_utc": f"2026-01-01T00:00:{second:02d}Z"})
        self.save(self.run / (stem + "-completion.json"), {"exit_code": 0, "xml_exists": True, "log": str(log),
            "finished_utc": f"2026-01-01T00:00:{second + 3:02d}Z"})

    def review_fixture(self):
        self.save(self.review, {"schema": pub.REVIEW_SCHEMA, "status": "passed", "reviewer": "UNIT FIXTURE, NOT A REVIEW",
            "reviewed_utc": "2026-01-01T00:00:12Z", "runtime_report_sha256": pub.sha(self.report_path),
            "input_snapshot_sha256": pub.sha(self.run / "input-playmode.json"),
            "approval_receipt_sha256": pub.sha(self.approved / "approval.json"), "stage_audit_sha256": pub.sha(self.stage_path),
            "mixed_geometry_reviewed": True, "preserved_idle_capture_acknowledged": True,
            "mixed_geometry_notes": "Synthetic geometry for code tests only; no artwork approval.",
            "views": [{"character_id": self.character, "view": name, "status": "passed",
                "image_sha256": self.actor[name]["imageSha256"], "clipping_reviewed": True,
                "full_frame_inside_capture": self.actor[name]["fullFrameInsideCapture"],
                "notes": "Synthetic noise PNG; not a gameplay or artwork acceptance."} for name in ("normalView", "nearestView")],
            "walk_views": [{"character_id": self.character, "direction": capture["direction"], "frame_number": 2,
                "simulation_frame": capture["simulationFrame"], "resource_sha256": capture["resourcePngSha256"],
                "view": name, "status": "passed", "image_sha256": capture[name]["imageSha256"], "clipping_reviewed": True,
                "full_frame_inside_capture": capture[name]["fullFrameInsideCapture"],
                "notes": "Synthetic moving capture fixture, not actual Unity evidence."}
                for capture in self.actor["walkFrameCaptures"] for name in ("normalView", "nearestView")]})

    def change(self, path, mutate):
        value = pub.read(path)
        mutate(value)
        self.save(path, value)

    def test_complete_fixture_dry_run_writes_nothing_then_publishes_only140_new_files(self):
        before = pub.file_inventory(self.root)
        plan = pub.prepare(self.arguments)
        self.assertEqual(before, pub.file_inventory(self.root))
        receipt = pub.execute(plan, self.arguments)
        target = self.formal / pub.gate.FAMILY / self.character
        self.assertEqual(receipt["status"], "published_pending_formal_editor_import")
        self.assertEqual(pub.file_inventory(target), self.outputs)
        self.assertEqual(pub.tree_inventory(self.formal, pub.FORMAL_ROOTS, target), plan["protectedFormal"])
        self.assertFalse((target / "runtime-index.asset").exists())
        self.assertFalse(target.with_suffix(".meta").exists())
        with self.assertRaisesRegex(ValueError, "Existing character"):
            pub.prepare(self.arguments)

    def test_source_visual_verification_failure_cannot_be_bypassed(self):
        self.verify.side_effect = ValueError("Actual source reconstruction or visual approval rejected")
        with self.assertRaisesRegex(ValueError, "reconstruction"):
            pub.prepare(self.arguments)
        self.assertFalse(self.audit.exists())

    def test_missing_swapped_wrong_ppu_pivot_duplicate_geometry_rejected(self):
        plan = {"characterId": self.character, "manifest": self.manifest}
        for mode in ("missing", "duplicate", "dimensions", "ppu", "pivot", "identity", "summary", "idle"):
            actor = copy.deepcopy(self.actor)
            with self.subTest(mode=mode):
                if mode == "missing": actor["actualFrameGeometry"].pop()
                elif mode == "duplicate": actor["actualFrameGeometry"][-1] = actor["actualFrameGeometry"][0]
                elif mode == "dimensions": actor["actualFrameGeometry"][0]["width"] = 1024
                elif mode == "ppu": actor["actualFrameGeometry"][0]["pixelsPerUnit"] = 104
                elif mode == "pivot": actor["actualFrameGeometry"][0]["pivot"]["y"] = .5
                elif mode == "identity": actor["actualFrameGeometry"][0]["resourcePath"] = "another/identity"
                elif mode == "summary": actor["actualTextureWidthsPerDirection"]["SW"] = 1024
                else: actor["actualFrameHeight"] = 1024
                with self.assertRaises(ValueError):
                    pub.geometry_check(actor, plan)

    def test_missing_mixed_parameter_case_even_with_passed_xml_rejected(self):
        for platform in ("EditMode", "PlayMode"):
            path = self.run / (platform.lower() + ".xml")
            result = ET.parse(path).getroot()
            classname, methods = pub.MIXED_METHODS[platform]
            victim = next(c for c in result if c.get("classname") == classname and methods.get(c.get("methodname"), 0) > 1)
            result.remove(victim)
            result.set("passed", str(len(result))); result.set("total", str(len(result)))
            ET.ElementTree(result).write(path, encoding="utf-8")
            with self.subTest(platform=platform), self.assertRaisesRegex(ValueError, "mixed method"):
                pub.check_unity_results(path, platform)

    def test_edit_play_post_changed_or_current_input_drift_rejected(self):
        post = self.run / "post-playmode.json"
        original = post.read_bytes()
        self.change(post, lambda d: d["files"][0].update(sha256="f" * 64))
        with self.assertRaisesRegex(ValueError, "full inputs differ"):
            pub.prepare(self.arguments)
        self.write(post, original)
        self.write(self.isolated / "Assets/unexpected.txt", b"UNIT CONCURRENT INPUT")
        with self.assertRaisesRegex(ValueError, "Current isolated"):
            pub.prepare(self.arguments)

    def test_formal_source_and_old_resource_changes_rejected(self):
        path = self.formal / pub.BINDINGS[0]
        old = path.read_bytes(); self.write(path, b"UNIT concurrent code")
        with self.assertRaisesRegex(ValueError, "Formal source"):
            pub.prepare(self.arguments)
        self.write(path, old)
        self.write(self.formal / pub.CHARACTERS / "QdaoOriginalRosterV13" / self.old_ids[0] / "fixture.txt", b"UNIT CHANGED OLD")
        with self.assertRaisesRegex(ValueError, "Formal old character"):
            pub.prepare(self.arguments)

    def test_stage_and_review_binding_changes_rejected(self):
        original = self.stage_path.read_bytes()
        self.change(self.stage_path, lambda d: d.update(character_id="05_other"))
        with self.assertRaisesRegex(ValueError, "Stage belongs"):
            pub.prepare(self.arguments)
        self.write(self.stage_path, original)
        self.change(self.review, lambda d: d.update(approval_receipt_sha256="a" * 64))
        with self.assertRaisesRegex(ValueError, "review bindings"):
            pub.prepare(self.arguments)

    def test_fake_counts_old_fallback_and_zero_residency_rejected(self):
        original = self.report_path.read_bytes()
        for field, value in (("actualIsMixedResolution", False), ("actualArtworkVersion", 13),
                             ("maxResidentHdDirectionsObserved", 0), ("actualFramesMatchResources", False)):
            with self.subTest(field=field):
                self.write(self.report_path, original)
                self.change(self.report_path, lambda d: d["appearances"][-1].update({field: value}))
                with self.assertRaises(ValueError):
                    pub.prepare(self.arguments)

    def test_missing_nearest_image_or_changed_png_rejected(self):
        path = Path(self.actor["nearestView"]["imagePath"])
        original = path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            pub.prepare(self.arguments)
        self.write(path, original + b"changed")
        with self.assertRaisesRegex(ValueError, "bytes changed"):
            pub.prepare(self.arguments)

    def test_future_review_unreviewed_clipping_and_unacknowledged_idle_rejected(self):
        original = self.review.read_bytes()
        mutations = [lambda d: d.update(reviewed_utc="2100-01-01T00:00:00Z"),
                     lambda d: d["views"][1].update(full_frame_inside_capture=True),
                     lambda d: d.update(preserved_idle_capture_acknowledged=False)]
        for mutate in mutations:
            self.write(self.review, original); self.change(self.review, mutate)
            with self.assertRaises(ValueError):
                pub.prepare(self.arguments)

    def test_nonzero_exit_or_narrow_filter_rejected(self):
        completion = self.run / "playmode-completion.json"
        original = completion.read_bytes()
        self.change(completion, lambda d: d.update(exit_code=1))
        with self.assertRaisesRegex(ValueError, "exit0"):
            pub.prepare(self.arguments)
        self.write(completion, original)
        self.change(self.run / "playmode-launch.json", lambda d: d.update(filter="OnlyOneTest"))
        with self.assertRaisesRegex(ValueError, "complete expected"):
            pub.prepare(self.arguments)

    def test_existing_target_guid_and_reused_audit_rejected(self):
        target_meta = (self.formal / pub.gate.FAMILY / self.character).with_suffix(".meta")
        self.write(target_meta, b"UNIT existing GUID")
        with self.assertRaisesRegex(ValueError, "Existing character"):
            pub.prepare(self.arguments)
        target_meta.unlink()
        self.save(self.audit, {"scope": "prior unit audit"})
        with self.assertRaisesRegex(ValueError, "new publication"):
            pub.prepare(self.arguments)

    def test_wrong_project_and_formal_artwork_identifier_rejected(self):
        self.arguments.project = self.isolated
        with self.assertRaisesRegex(ValueError, "Unsupported Unity"):
            pub.prepare(self.arguments)
        self.arguments.project = self.formal
        self.checked["character_id"] = "05_unit"
        with self.assertRaisesRegex(ValueError, "Original04-06 only"):
            pub.prepare(self.arguments)

    def test_idle_only_evidence_cannot_publish_even_with_passed_unity_results(self):
        self.change(self.report_path, lambda d: d["appearances"][-1].pop("walkFrameCaptures"))
        with self.assertRaisesRegex(ValueError, "native direction captures"):
            pub.prepare(self.arguments)

    def test_native_captures_require_separate_exact_visual_review(self):
        self.change(self.review, lambda d: d.pop("walk_views"))
        with self.assertRaisesRegex(ValueError, "walking visual review coverage"):
            pub.prepare(self.arguments)

    def test_copy_failure_cleans_only_temp_and_retains_failed_audit(self):
        plan = pub.prepare(self.arguments)
        with patch.object(pub.shutil, "copyfile", side_effect=OSError("unit copy failure")):
            with self.assertRaisesRegex(OSError, "unit copy"):
                pub.execute(plan, self.arguments)
        self.assertEqual(pub.read(self.audit)["status"], "failed_before_activation")
        self.assertFalse(Path(plan["target"]).exists())
        self.assertEqual(pub.tree_inventory(self.formal, pub.FORMAL_ROOTS), plan["protectedFormal"])

    def test_protected_file_race_before_activation_blocks(self):
        plan = pub.prepare(self.arguments)
        real_copy = pub.shutil.copyfile
        def raced_copy(source, destination):
            result = real_copy(source, destination)
            self.write(self.formal / "Assets/unit-concurrent.txt", b"UNIT UNRELATED CONCURRENT FILE")
            return result
        with patch.object(pub.shutil, "copyfile", side_effect=raced_copy):
            with self.assertRaisesRegex(ValueError, "Protected formal"):
                pub.execute(plan, self.arguments)
        self.assertFalse(Path(plan["target"]).exists())
        self.assertTrue((self.formal / "Assets/unit-concurrent.txt").exists())

    def test_post_activation_failure_retains_target_and_records_audit(self):
        plan = pub.prepare(self.arguments)
        real_inventory = pub.tree_inventory
        def fail_after(root, roots, excluded=None):
            if excluded == Path(plan["target"]) and excluded.exists():
                raise ValueError("unit failure after activation")
            return real_inventory(root, roots, excluded)
        with patch.object(pub, "tree_inventory", side_effect=fail_after):
            with self.assertRaisesRegex(RuntimeError, "target retained"):
                pub.execute(plan, self.arguments)
        self.assertTrue(Path(plan["target"]).is_dir())
        self.assertEqual(pub.read(self.audit)["status"], "failed_after_target_activation")


if __name__ == "__main__":
    unittest.main()
