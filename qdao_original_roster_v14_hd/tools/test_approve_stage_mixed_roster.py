"""Fixture-only gate tests. No real artwork approval, Unity project or generation.

Source pixel reconstruction is independently tested by test_assemble_mixed_roster;
these metadata/stage tests mock only that expensive lower-level source check.
"""
import copy
from datetime import datetime, timedelta, timezone
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw
import approve_mixed_roster as a
import stage_mixed_roster as s

ID = a.assembly.base.MIXED_IDS[0]


def png(size):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rectangle((20, 20, size[0] - 20, size[1] - 20), fill=(90, 130, 180, 255))
    stream = io.BytesIO()
    im.save(stream, format="PNG")
    return stream.getvalue()


class GateFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="mixed-gate-test-")
        self.root = Path(self.temporary.name)
        self.input_root = self.root / "mixed-candidates"
        self.approved_root = self.root / "mixed-approved"
        self.input = self.input_root / "fixture-run" / ID
        self.output = self.approved_root / "fixture-run" / ID
        self.review_path = self.root / "fixture-review.json"
        self.project = self.root / "isolated-fixture"
        self.audit = self.root / "audit" / "fixture.json"
        self.patches = [
            patch.multiple(a, INPUT_ROOT=self.input_root, APPROVED_ROOT=self.approved_root),
            patch.multiple(s, ISOLATED_PROJECT=self.project, AUDIT_ROOT=self.audit.parent),
            patch.object(a, "check_complete_assembly", return_value={
                "status": "source_recheck_complete_pending_visual", "character_id": ID, "present_runtime_pngs": 137,
                "missing_actions": 0, "reconstructed_actions": 136, "historical_text_conflicts": 0,
                "visual_review": "pending", "can_publish": False, "writesPerformed": False}),
        ]
        for p in self.patches:
            p.start()
        self.source_mock = a.check_complete_assembly
        raw = {512: png((512, 512)), 1024: png((1024, 1024))}
        rows = []
        for index, path in enumerate(a.assembly.base.PNG_PATHS):
            size = 512 if index < 112 else 1024
            dst = self.input / path
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(raw[size])
            row = {"path": path, "sha256": a.sha(dst), "availability": "present", "width": size, "height": size,
                   "source_kind": "original-portrait" if path == "portrait.png" else "preserved-v13" if size == 512 else "native-hd",
                   "source_sha256": "a" * 64}
            if path != "portrait.png":
                row.update(pixels_per_unit=52 if size == 512 else 104, pivot=[.5, .08],
                           root_px=[size // 2, 471 if size == 512 else 942], native_cell_size=[size, size])
                if size == 512:
                    row["preserved_sha256"] = row["sha256"]
            rows.append(row)
        self.manifest = {"version": 14, "character_id": ID, "resolution_mode": a.assembly.base.MODE,
                         "status": "ready_for_visual_review", "visual_review": "pending", "files": rows}
        self.write(self.input / "manifest.json", self.manifest)
        self.write(self.input / "qc.json", {"errors": [], "status": "numeric_passed",
                   "visual_review": "pending", "directions": {d: {"visual_review": "pending"} for d in a.assembly.DIRS}})
        self.write(self.input / "assembly-report.json", {"created_utc": "2026-01-01T00:00:00+00:00"})
        self.write(self.input / "processing/mixed-sources.json", {"fixture": True, "original_claim": "unchanged"})
        self.write(self.input / "processing/preserved-output-snapshot.json", {"fixture": True})
        evidence = self.root / "fixture-evidence.png"
        evidence.write_bytes(png((1920, 1080)))
        self.review = {"schema": a.REVIEW_SCHEMA, "character_id": ID, "status": "passed", "reviewer": "TEST FIXTURE ONLY",
                       "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
                       "reviewed_artifacts": {r["path"]: r["sha256"] for r in rows},
                       "reviewed_directions": list(a.assembly.DIRS),
                       "notes_by_direction": {d: d + " TEST FIXTURE ONLY; no artwork inspected" for d in a.assembly.DIRS},
                       "evidence": [{"path": str(evidence), "sha256": a.sha(evidence), "checks": list(a.CHECKS),
                                     "directions": list(a.assembly.DIRS), "notes": "TEST FIXTURE ONLY; generated geometric rectangle"}]}
        self.review.update({k: a.sha(self.input / v) for k, v in a.INPUT_BINDINGS.items()})
        self.review.update({k + "_review": True for k in a.CHECKS})
        self.review.update({k + "_notes": "TEST FIXTURE ONLY; no real art approval" for k in a.GLOBAL_CHECKS})
        self.write(self.review_path, self.review)
        for directory in ("Assets", "Packages", "ProjectSettings", s.CHARACTERS):
            (self.project / directory).mkdir(parents=True, exist_ok=True)
        self.old = self.project / s.CHARACTERS / "QdaoOriginalRosterV13" / ID / "portrait.png"
        self.old.parent.mkdir(parents=True)
        self.old.write_bytes(raw[1024])
        for relative in ("Assets/Maps/keep.txt", "Assets/UI/keep.txt", "Assets/Scripts/keep.cs"):
            path = self.project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"unrelated original bytes")

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temporary.cleanup()

    @staticmethod
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(a.encoded(value))

    def save_review(self):
        self.write(self.review_path, self.review)

    def seal(self):
        self.save_review()
        docs, copies = a.build_approval(self.input, self.review_path)
        a.execute_approval(docs, copies, self.output)
        return docs

    def review_rejected(self):
        self.save_review()
        with self.assertRaises(ValueError):
            a.build_approval(self.input, self.review_path)

    def test_complete_offline_seal_and_check_preserve_source_bytes(self):
        before = a.assembly.file_inventory(self.input)
        self.seal()
        checked = a.verify_approved(self.output)
        self.assertEqual(140, len(checked["runtime_outputs"]))
        self.assertFalse(checked["formal_publication_authorized"])
        self.assertEqual(before, a.assembly.file_inventory(self.input))
        self.assertTrue(self.source_mock.called)
        activation = a.read(self.output / "appearance.json")
        self.assertEqual(a.assembly.base.MODE, activation["resolutionMode"])
        self.assertEqual(a.assembly.base.SOURCE_COMMIT, activation["sourceCommit"])
        self.assertEqual((1024, 104, .5, .08), tuple(activation[k] for k in ("frameWidth", "pixelsPerUnit", "pivotX", "pivotY")))

    def test_each_missing_visual_check_rejected(self):
        for check in a.CHECKS:
            with self.subTest(check=check):
                self.review[check + "_review"] = False
                self.review_rejected()
                self.review[check + "_review"] = True

    def test_each_stale_input_binding_rejected(self):
        for key in a.INPUT_BINDINGS:
            with self.subTest(key=key):
                saved = self.review[key]
                self.review[key] = "f" * 64
                self.review_rejected()
                self.review[key] = saved

    def test_artifact_sha_mismatch_rejected(self):
        self.review["reviewed_artifacts"]["portrait.png"] = "f" * 64
        self.review_rejected()

    def test_partial_inventory_rejected(self):
        self.manifest["files"][0]["availability"] = "missing"
        self.write(self.input / "manifest.json", self.manifest)
        self.review_rejected()

    def test_missing_direction_and_evidence_coverage_rejected(self):
        self.review["evidence"][0]["directions"].remove("NW")
        self.review_rejected()

    def test_native_inspection_evidence_cannot_be_thumbnail(self):
        path = Path(self.review["evidence"][0]["path"])
        path.write_bytes(png((64, 64)))
        self.review["evidence"][0]["sha256"] = a.sha(path)
        self.review_rejected()

    def test_closeup_must_be_actual_1080p_dimensions(self):
        path = Path(self.review["evidence"][0]["path"])
        path.write_bytes(png((1920, 1200)))
        self.review["evidence"][0]["sha256"] = a.sha(path)
        self.review_rejected()

    def test_evidence_file_changed_rejected(self):
        Path(self.review["evidence"][0]["path"]).write_bytes(b"changed")
        self.review_rejected()

    def test_review_before_assembly_rejected(self):
        self.review["reviewed_at_utc"] = "2025-01-01T00:00:00Z"
        self.review_rejected()

    def test_future_review_rejected(self):
        self.review["reviewed_at_utc"] = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        self.review_rejected()

    def test_all_hd_or_legacy_is_not_a_mixed_character(self):
        for row in self.manifest["files"]:
            if row["path"] != "portrait.png":
                row["source_kind"] = "native-hd"
        self.write(self.input / "manifest.json", self.manifest)
        self.review_rejected()

    def test_source_checker_failure_propagates(self):
        self.source_mock.side_effect = ValueError("unresolved historical text conflict")
        self.review_rejected()

    def test_offline_output_existing_rejected(self):
        self.seal()
        docs, copies = a.build_approval(self.input, self.review_path)
        with self.assertRaises(ValueError):
            a.execute_approval(docs, copies, self.output)

    def test_offline_output_escape_rejected(self):
        docs, copies = a.build_approval(self.input, self.review_path)
        with self.assertRaises(ValueError):
            a.execute_approval(docs, copies, self.root / ID)

    def test_original_assembly_change_invalidates_approval(self):
        self.seal()
        (self.input / "portrait.png").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            a.verify_approved(self.output)

    def test_rehashed_changed_approved_pixels_rejected(self):
        self.seal()
        path = self.output / "portrait.png"
        path.write_bytes(b"changed pixels")
        receipt = a.read(self.output / "approval.json")
        receipt["copied_files"]["portrait.png"] = a.sha(path)
        self.write(self.output / "approval.json", receipt)
        with self.assertRaises(ValueError):
            a.verify_approved(self.output)

    def test_rehashed_activation_change_rejected(self):
        self.seal()
        path = self.output / "appearance.json"
        document = a.read(path)
        document["resolutionMode"] = ""
        self.write(path, document)
        receipt = a.read(self.output / "approval.json")
        receipt["sealed_files"]["appearance.json"] = receipt["runtime_outputs"]["appearance.json"] = a.sha(path)
        self.write(self.output / "approval.json", receipt)
        with self.assertRaises(ValueError):
            a.verify_approved(self.output)

    def test_stage_exact_new_target_preserves_every_other_project_file(self):
        self.seal()
        before = a.assembly.file_inventory(self.project)
        plan = s.prepare_stage(self.output, self.project, self.audit)
        result = s.execute_stage(plan)
        after = a.assembly.file_inventory(self.project)
        prefix = s.FAMILY + "/" + ID + "/"
        self.assertEqual(before, {p: h for p, h in after.items() if not p.startswith(prefix)})
        self.assertEqual(140, len(after) - len(before))
        self.assertEqual(0, result["protected_changed_files"])
        self.assertFalse(result["formal_publication_authorized"])
        self.assertEqual("not_yet_run", result["actual_mixed_asset_unity_validation"])
        self.assertTrue(self.audit.is_file())

    def test_stage_default_plan_writes_nothing(self):
        self.seal()
        before = a.assembly.file_inventory(self.root)
        s.prepare_stage(self.output, self.project, self.audit)
        self.assertEqual(before, a.assembly.file_inventory(self.root))

    def test_stage_different_project_rejected(self):
        with self.assertRaises(ValueError):
            s.prepare_stage(self.output, Path("E:/work/mmorpg-client"), self.audit)

    def test_stage_existing_target_rejected(self):
        self.seal()
        (self.project / s.FAMILY / ID).mkdir(parents=True)
        with self.assertRaises(ValueError):
            s.prepare_stage(self.output, self.project, self.audit)

    def test_stage_existing_meta_rejected(self):
        self.seal()
        target = self.project / s.FAMILY / (ID + ".meta")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"existing GUID")
        with self.assertRaises(ValueError):
            s.prepare_stage(self.output, self.project, self.audit)

    def test_stage_changed_protected_input_rejected_before_write(self):
        self.seal()
        plan = s.prepare_stage(self.output, self.project, self.audit)
        self.old.write_bytes(b"concurrent legacy mutation")
        with self.assertRaises(ValueError):
            s.execute_stage(plan)
        self.assertFalse(Path(plan["target"]).exists())

    def test_stage_changed_approved_input_rejected_before_write(self):
        self.seal()
        plan = s.prepare_stage(self.output, self.project, self.audit)
        (self.output / "portrait.png").write_bytes(b"concurrent source mutation")
        with self.assertRaises(ValueError):
            s.execute_stage(plan)
        self.assertFalse(Path(plan["target"]).exists())

    def test_stage_audit_outside_whitelist_rejected(self):
        with self.assertRaises(ValueError):
            s.prepare_stage(self.output, self.project, self.project / "Assets/forbidden.json")

    def test_stage_failed_copy_removes_only_own_temporary_tree(self):
        self.seal()
        plan = s.prepare_stage(self.output, self.project, self.audit)
        before = a.assembly.file_inventory(self.project)
        with patch.object(s.shutil, "copyfile", side_effect=OSError("fixture copy failure")):
            with self.assertRaises(OSError):
                s.execute_stage(plan)
        self.assertEqual(before, a.assembly.file_inventory(self.project))
        self.assertEqual("failed_before_activation", a.read(self.audit)["status"])
        self.assertFalse(a.read(self.audit)["target_retained"])

    def test_audit_reservation_failure_cannot_activate(self):
        self.seal()
        plan = s.prepare_stage(self.output, self.project, self.audit)
        real_open = Path.open
        def reject_audit(path, *args, **kwargs):
            if path.resolve() == self.audit.resolve() and args and args[0] == "xb":
                raise PermissionError("fixture audit reservation denied")
            return real_open(path, *args, **kwargs)
        with patch.object(Path, "open", reject_audit):
            with self.assertRaises(PermissionError):
                s.execute_stage(plan)
        self.assertFalse(Path(plan["target"]).exists())

    def test_post_activation_failure_has_explicit_retained_target_audit(self):
        self.seal()
        plan = s.prepare_stage(self.output, self.project, self.audit)
        real_inventory = a.assembly.file_inventory
        def fail_final_inventory(directory):
            if Path(directory) == Path(plan["target"]):
                raise ValueError("fixture post-rename failure")
            return real_inventory(directory)
        with patch.object(a.assembly, "file_inventory", fail_final_inventory):
            with self.assertRaisesRegex(RuntimeError, "target retained"):
                s.execute_stage(plan)
        self.assertTrue(Path(plan["target"]).is_dir())
        saved = a.read(self.audit)
        self.assertEqual("failed_after_target_activation", saved["status"])
        self.assertTrue(saved["target_retained"])


class IndependentResultGate(unittest.TestCase):
    def test_partial_or_conflicted_independent_result_rejected(self):
        complete = {"status": "source_recheck_complete_pending_visual", "present_runtime_pngs": 137,
                    "missing_actions": 0, "reconstructed_actions": 136, "historical_text_conflicts": 0, "can_publish": False}
        for key, value in (("status", "partial"), ("present_runtime_pngs", 136), ("missing_actions", 1),
                           ("reconstructed_actions", 135), ("historical_text_conflicts", 1), ("can_publish", True)):
            with self.subTest(key=key), patch.object(a.assembly, "check_assembly", return_value={**complete, key: value}):
                with self.assertRaises(ValueError):
                    a.check_complete_assembly(Path("fixture"))


if __name__ == "__main__":
    unittest.main()
