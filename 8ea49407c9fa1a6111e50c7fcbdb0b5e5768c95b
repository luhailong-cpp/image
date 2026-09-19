"""Temporary geometric PNG fixtures exercise rejection; these are not character art."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest

from PIL import Image, ImageDraw

import assemble_mixed_roster as a


class ReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="mixed-assembly-tests-", dir=a.ROOT / "tools")
        cls.root = Path(cls.temp.name)
        raw = Image.new("RGBA", (1254, 1254))
        ImageDraw.Draw(raw).rectangle((450, 200, 750, 1000), fill=(25, 120, 80, 255))
        raw.save(cls.root / "raw.png")
        (cls.root / "prompt.txt").write_text("Procedural rectangle TEST FIXTURE, never a generated character", encoding="utf-8")
        def fixture_receipt(raw_path, receipt_path):
            receipt_path.write_text(json.dumps({"tool": "built-in image_gen", "actual_model": "unverified-test-fixture",
                "metadata_only_fixture": True, "generation_calls": 1, "paid_api_calls": 0,
                "actual_request": {"prompt": (cls.root / "prompt.txt").read_bytes().decode("utf-8"),
                                   "referenced_image_paths": [str(cls.root / "raw.png")], "started_at": "2026-09-18T00:00:00Z"},
                "original_generated_file": str(raw_path),
                "output_hint": f"Generated images are saved to {raw_path.parent} as {raw_path} by default.\nTEST FIXTURE ONLY"}), encoding="utf-8")
        fixture_receipt(cls.root / "raw.png", cls.root / "receipt.json")
        cls.fixtures = {}
        for size, tools_root in ((512, a.base.V13 / "tools"), (1024, a.ROOT / "tools")):
            spec = importlib.util.spec_from_file_location("fixture_pipeline_" + str(size), tools_root / "pipeline.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.ROOT = cls.root / ("pipeline-" + str(size))
            args = SimpleNamespace(command="import-walk", character="04_mountain_guardian_boy", direction="SW",
                                   rows=1, cols=1, source_cell_indices=None, output_frames="2", start_frame=1,
                                   idle_order=None, source=cls.root / "raw.png", prompt=cls.root / "prompt.txt",
                                   receipt=cls.root / "receipt.json", common_scale=.84, chroma_profile="standard",
                                   batch_id="fixture")
            with contextlib.redirect_stdout(io.StringIO()):
                module.import_sheet(args)
            cls.fixtures[size] = module.ROOT / "candidate" / args.character
            if size == 1024:
                native_new = Image.new("RGBA", (1254, 1254))
                ImageDraw.Draw(native_new).rectangle((470, 180, 770, 1000), fill=(30, 140, 95, 255))
                native_new.save(cls.root / "new-raw.png")
                args.source, args.output_frames, args.batch_id = cls.root / "new-raw.png", "3", "fixture-new"
                fixture_receipt(args.source, cls.root / "new-receipt.json")
                args.receipt = cls.root / "new-receipt.json"
                module.ROOT = cls.root / "pipeline-new-native"
                with contextlib.redirect_stdout(io.StringIO()):
                    module.import_sheet(args)
                cls.native_new_fixture = module.ROOT / "candidate" / args.character

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.workspace = self.root / "working"
        self.workspace.mkdir()
        self.candidate = self.workspace / "candidate"
        shutil.copytree(self.fixtures[1024], self.candidate)
        self.record = a.read(self.candidate / "processing/frame-sources.json")["walk/SW/02.png"]
        self.original_v13 = a.base.V13
        a.base.V13 = self.workspace / "v13"

    def tearDown(self):
        a.base.V13 = self.original_v13
        shutil.rmtree(self.workspace)

    def test_native_reconstruction_does_not_claim_model(self):
        result = a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)
        self.assertEqual(result["pixel_reconstruction"], "passed")
        self.assertEqual(result["source_evidence"], "verified_saved_files")
        self.assertEqual(result["model_identity_verification"], "not_claimed")
        self.assertIn("not_cryptographic_generation_attestation", result["generation_receipt_binding"]["verification_scope"])

    def test_legacy_reconstruction_preserves_size_and_receipt_conflict(self):
        legacy = self.workspace / "legacy"
        shutil.copytree(self.fixtures[512], legacy)
        record = a.read(legacy / "processing/frame-sources.json")["walk/SW/02.png"]
        receipt = legacy / record["generation"]["receipt"]["path"]
        receipt.write_bytes(receipt.read_bytes() + b"\n")
        result = a.reconstruct(legacy, "walk/SW/02.png", record, 512, .84)
        self.assertEqual(result["pixel_reconstruction"], "passed")
        self.assertEqual(result["source_evidence"], "blocked")
        self.assertEqual(result["evidence_issues"][0]["role"], "receipt")

    def test_new_receipt_must_exist(self):
        (self.candidate / self.record["generation"]["receipt"]["path"]).unlink()
        with self.assertRaisesRegex(ValueError, "Missing receipt"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_new_receipt_mutation_is_rejected(self):
        path = self.candidate / self.record["generation"]["receipt"]["path"]
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Changed receipt"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def replace_receipt(self, mutation):
        path = self.candidate / self.record["generation"]["receipt"]["path"]
        receipt = a.read(path)
        mutation(receipt)
        path.write_bytes(a.encoded(receipt))
        self.record["generation"]["receipt"]["sha256"] = a.sha(path)

    def test_fake_nonempty_hint_cannot_pass_with_updated_record_hash(self):
        self.replace_receipt(lambda r: r.update(output_hint="fake"))
        with self.assertRaisesRegex(ValueError, "actual original PNG path"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_receipt_must_explicitly_name_builtin_tool(self):
        self.replace_receipt(lambda r: r.pop("tool"))
        with self.assertRaisesRegex(ValueError, "explicit authorized"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_receipt_request_prompt_must_match_exact_saved_text(self):
        self.replace_receipt(lambda r: r["actual_request"].update(prompt="another prompt"))
        with self.assertRaisesRegex(ValueError, "request prompt differs"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_receipt_requires_actual_reference_paths(self):
        self.replace_receipt(lambda r: r["actual_request"].update(referenced_image_paths=[]))
        with self.assertRaisesRegex(ValueError, "actual saved reference"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_receipt_output_path_cannot_name_different_png(self):
        self.replace_receipt(lambda r: r.update(original_generated_file=str(self.root / "new-raw.png")))
        with self.assertRaisesRegex(ValueError, "PNG path differs"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_receipt_original_output_bytes_must_equal_saved_raw(self):
        different = self.root / "new-raw.png"
        self.replace_receipt(lambda r: r.update(original_generated_file=str(different),
            output_hint=f"Generated images are saved to {different.parent} as {different} by default.\n"))
        with self.assertRaisesRegex(ValueError, "PNG bytes differ"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_receipt_placeholder_is_rejected_even_with_matching_hash(self):
        path = self.candidate / self.record["generation"]["receipt"]["path"]
        path.write_text("{}", encoding="utf-8")
        self.record["generation"]["receipt"]["sha256"] = a.sha(path)
        with self.assertRaisesRegex(ValueError, "output_hint"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_changed_output_is_rejected(self):
        path = self.candidate / "walk/SW/02.png"
        with Image.open(path) as image:
            changed = image.copy()
        changed.putpixel((512, 600), (255, 0, 0, 255))
        changed.save(path)
        with self.assertRaisesRegex(ValueError, "Output SHA"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_changed_stage_is_rejected(self):
        path = self.candidate / self.record["stages"]["cell"]["path"]
        path.write_bytes(path.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "Changed stage_cell"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_wrong_grid_mapping_is_rejected(self):
        self.record["source"]["output_frame_map"] = [3]
        with self.assertRaisesRegex(ValueError, "mapping"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_low_native_cell_is_rejected(self):
        self.record["source"].update(grid=[2, 2], cell_index=0, cell_xyxy=[0, 0, 627, 627],
                                     selected_source_cell_indices=[0], output_frame_map=[2, None, None, None])
        self.record["whole_cell_scale"] = 1024 / 627 * .84
        with self.assertRaisesRegex(ValueError, "below 1024"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84)

    def test_per_frame_scale_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "scale"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .88)

    def test_05_chroma_guard_is_shared_by_independent_reconstruction(self):
        with self.assertRaisesRegex(ValueError, "05 must preserve"):
            a.reconstruct(self.candidate, "walk/SW/02.png", self.record, 1024, .84, character="05_celestial_musician_girl")

    def test_source_record_mapping_keeps_original_unmodified(self):
        original = copy.deepcopy(self.record)
        remapped = a.remap_record(self.record, "evidence/native-hd")
        self.assertEqual(self.record, original)
        self.assertEqual(remapped["source"]["sha256"], self.record["source"]["sha256"])
        self.assertTrue(remapped["source"]["path"].startswith("evidence/native-hd/"))

    def test_sealed_identity_is_rejected_before_input_access(self):
        with self.assertRaisesRegex(ValueError, "Only unsealed"):
            a.assemble_plan("00_reference_topright_boy", self.workspace, self.candidate)

    def test_output_outside_new_mixed_root_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "new child"):
            a.execute_plan({}, {}, a.base.V13 / "candidate/04_mountain_guardian_boy")

    def test_existing_output_cannot_be_overwritten(self):
        old_root = a.OUTPUT_ROOT
        try:
            a.OUTPUT_ROOT = self.workspace
            with self.assertRaisesRegex(ValueError, "immutable"):
                a.execute_plan({}, {}, self.candidate)
        finally:
            a.OUTPUT_ROOT = old_root

    def make_partial_assembly(self, include_new=False):
        """A two-image fixture exercises the exact production assembly/check API."""
        character = "04_mountain_guardian_boy"
        legacy_root = self.workspace / "v13"
        legacy = legacy_root / "candidate" / character
        shutil.copytree(self.fixtures[512], legacy)
        original = legacy / "source/original-portrait-4096.png"
        portrait = Image.new("RGBA", (4096, 4096), (20, 90, 40, 255))
        portrait.save(original)
        portrait.resize((1024, 1024), Image.Resampling.LANCZOS).save(legacy / "portrait.png")
        original_hash = a.sha(original)
        entry = {"character_id": character, "source_commit": a.base.SOURCE_COMMIT,
                 "sha256": original_hash, "git_manifest_sha256": original_hash}
        (legacy_root / "inventory.json").write_bytes(a.encoded({"characters": [entry]}))
        (legacy / "processing/portrait-source.json").write_bytes(a.encoded({"preserved_source": "source/original-portrait-4096.png",
            "source_sha256": original_hash, "output_sha256": a.sha(legacy / "portrait.png")}))
        preparation = self.workspace / "preparation"
        preparation.mkdir()
        record = a.read(legacy / "processing/frame-sources.json")["walk/SW/02.png"]
        row = a.base.runtime_file("walk/SW/02.png", record["output_sha256"], record["source"]["sha256"], "preserved-v13", [1254, 1254])
        portrait_row = a.base.runtime_file("portrait.png", a.sha(legacy / "portrait.png"), original_hash, "original-portrait")
        snapshot = {"files": [{"character_id": character, **row}, {"character_id": character, **portrait_row}]}
        inventory = a.file_inventory(legacy)
        evidence = {"files": [{"path": str(legacy / path), "sha256": digest} for path, digest in inventory.items()],
                    "candidate_trees": [{"character_id": character, "root": str(legacy), "files": list(inventory)}]}
        (preparation / "preserved-output-snapshot.json").write_bytes(a.encoded(snapshot))
        (preparation / "legacy-evidence-snapshot.json").write_bytes(a.encoded(evidence))
        (preparation / "preparation.json").write_bytes(a.encoded({"schema": a.base.SCHEMA, "source_commit": a.base.SOURCE_COMMIT,
            "preserved_snapshot_sha256": a.base.value_sha(snapshot), "evidence_snapshot_sha256": a.base.value_sha(evidence)}))
        old_v13, old_output = a.base.V13, a.OUTPUT_ROOT
        output = self.workspace / "outputs" / character
        try:
            a.base.V13, a.OUTPUT_ROOT = legacy_root, self.workspace / "outputs"
            docs, copies = a.assemble_plan(character, preparation, self.native_new_fixture if include_new else self.candidate)
            a.execute_plan(docs, copies, output)
        finally:
            a.base.V13, a.OUTPUT_ROOT = old_v13, old_output
        self.assertEqual(a.file_inventory(legacy), inventory)
        return output, docs

    def test_partial_copy_has_137_slots_and_remains_unapproved(self):
        output, docs = self.make_partial_assembly()
        self.assertEqual(len(docs["manifest.json"]["files"]), 137)
        self.assertEqual(docs["assembly-report.json"]["status"], "partial")
        self.assertEqual(docs["assembly-report.json"]["excluded_hd_preserved_slots"], ["walk/SW/02.png"])
        self.assertFalse((output / "appearance.json").exists())
        checked = a.check_assembly(output)
        self.assertEqual(checked["missing_actions"], 135)
        self.assertFalse(checked["can_publish"])
        with self.assertRaisesRegex(ValueError, "Complete source-ready"):
            a.check_assembly(output, require_complete=True)

    def test_mutated_copied_legacy_prompt_is_rejected(self):
        output, docs = self.make_partial_assembly()
        wrapped = docs["processing/mixed-sources.json"]["actions"]["walk/SW/02.png"]
        copied_prompt = output / wrapped["record"]["prompt"]["path"]
        copied_prompt.write_bytes(copied_prompt.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Copied source/output bytes changed"):
            a.check_assembly(output)

    def test_new_native_action_fills_only_missing_slot_with_104_ppu(self):
        output, docs = self.make_partial_assembly(include_new=True)
        rows = {row["path"]: row for row in docs["manifest.json"]["files"]}
        self.assertEqual(rows["walk/SW/02.png"]["width"], 512)
        self.assertEqual(rows["walk/SW/02.png"]["pixels_per_unit"], 52)
        self.assertEqual(rows["walk/SW/03.png"]["width"], 1024)
        self.assertEqual(rows["walk/SW/03.png"]["pixels_per_unit"], 104)
        self.assertEqual(rows["walk/SW/03.png"]["source_kind"], "native-hd")
        result = a.check_assembly(output)
        self.assertEqual(result["present_runtime_pngs"], 3)
        self.assertEqual(result["reconstructed_actions"], 2)
        self.assertEqual(result["missing_actions"], 134)

    def test_hd_candidate_cannot_borrow_another_identity(self):
        path = self.candidate / "manifest.json"
        manifest = a.read(path)
        manifest["character_id"] = "05_celestial_musician_girl"
        path.write_bytes(a.encoded(manifest))
        with self.assertRaisesRegex(ValueError, "HD candidate identity"):
            self.make_partial_assembly()

    def update_report_hashes(self, output, manifest, report):
        (output / "manifest.json").write_bytes(a.encoded(manifest))
        report["manifest_sha256"] = a.sha(output / "manifest.json")
        (output / "assembly-report.json").write_bytes(a.encoded(report))

    def test_check_rejects_preserved_action_marked_missing_after_rehash(self):
        output, docs = self.make_partial_assembly()
        relative = "walk/SW/02.png"
        manifest, report = docs["manifest.json"], docs["assembly-report.json"]
        (output / relative).unlink()
        next(r for r in manifest["files"] if r["path"] == relative).update(availability="missing", sha256=None)
        report["copied_files"].pop(relative)
        report["missing_action_paths"].append(relative)
        self.update_report_hashes(output, manifest, report)
        with self.assertRaisesRegex(ValueError, "preserved slot was dropped"):
            a.check_assembly(output)

    def test_check_rejects_preserved_portrait_marked_missing_after_rehash(self):
        output, docs = self.make_partial_assembly()
        manifest, report = docs["manifest.json"], docs["assembly-report.json"]
        (output / "portrait.png").unlink()
        next(r for r in manifest["files"] if r["path"] == "portrait.png").update(availability="missing", sha256=None)
        report["copied_files"].pop("portrait.png")
        self.update_report_hashes(output, manifest, report)
        with self.assertRaisesRegex(ValueError, "preserved slot was dropped"):
            a.check_assembly(output)

    def test_check_rejects_rehashed_snapshot_omitting_preserved_slot(self):
        output, docs = self.make_partial_assembly()
        manifest, report = docs["manifest.json"], docs["assembly-report.json"]
        relative = "processing/preserved-output-snapshot.json"
        snapshot = a.read(output / relative)
        snapshot["files"] = [r for r in snapshot["files"] if r["path"] != "walk/SW/02.png"]
        (output / relative).write_bytes(a.encoded(snapshot))
        manifest["preserved_snapshot_sha256"] = a.sha(output / relative)
        report["copied_files"][relative] = a.sha(output / relative)
        self.update_report_hashes(output, manifest, report)
        with self.assertRaisesRegex(ValueError, "snapshot differs from real legacy"):
            a.check_assembly(output)

    def test_check_rejects_rehashed_copy_of_legacy_source_map(self):
        output, docs = self.make_partial_assembly()
        manifest, report = docs["manifest.json"], docs["assembly-report.json"]
        relative = "evidence/preserved-v13/processing/frame-sources.json"
        (output / relative).write_bytes(a.encoded({}))
        report["copied_files"][relative] = a.sha(output / relative)
        self.update_report_hashes(output, manifest, report)
        with self.assertRaisesRegex(ValueError, "Copied legacy source map differs"):
            a.check_assembly(output)

    def test_check_cannot_redirect_trust_to_copied_legacy_tree(self):
        output, docs = self.make_partial_assembly()
        manifest, report = docs["manifest.json"], docs["assembly-report.json"]
        other = self.workspace / "other-legacy"
        shutil.copytree(report["legacy_root"], other)
        report["legacy_root"], report["legacy_before"] = str(other), a.file_inventory(other)
        self.update_report_hashes(output, manifest, report)
        with self.assertRaisesRegex(ValueError, "another legacy source root"):
            a.check_assembly(output)

    def test_unknown_reconciliation_code_cannot_be_executed(self):
        path = self.workspace / "fake_reconciliation.py"
        path.write_text("raise RuntimeError('must never execute')", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "reviewed whitelist"):
            a.reconciliation_module(path)

    def test_reconciliation_does_not_generalize_to_other_text(self):
        module = a.reconciliation_module(a.RECONCILIATION_TOOL)
        result = {"path": "walk/SW/02.png", "evidence_issues": [{"role": "prompt"}]}
        with self.assertRaisesRegex(ValueError, "eleven approved"):
            a.reconcile_checks(result, module, self.candidate, self.record, self.candidate, self.record,
                               (self.candidate / "processing/frame-sources.json").read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
