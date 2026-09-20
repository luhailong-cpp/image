"""Small dictionary/JSON checks for separate formal/isolated old-resource gates.

No real resources, PNG fixtures, approved bundles or Unity execution. Only two
tiny synthetic JSON records are written per test in a private temporary folder.
"""
from __future__ import annotations
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import publish_mixed_roster as pub


class SeparateProjectBaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mixed-baseline-unit-", dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.formal = self.root / "formal"
        self.isolated = self.root / "isolated"
        self.runs = self.root / "runs"
        self.audit_root = self.root / "stage-audits"
        self.audit = self.audit_root / "fixture.json"
        self.baseline = self.runs / pub.FORMAL_BASELINE_RELATIVE
        self.prefix = pub.CHARACTERS + "/"
        self.relative = "QdaoOriginalRosterV13/00_unit/walk/S/01.png"
        self.author = self.prefix + self.relative
        self.meta = self.author + ".meta"
        self.folder_meta = self.prefix + "QdaoOriginalRosterV13.meta"
        self.plan = {"characterId": "04_mountain_guardian_boy", "approved": str(self.root / "approved"),
                     "outputs": {"appearance.json": "9" * 64}, "approvedInventory": {"appearance.json": "9" * 64}}
        self.formal_rows = {self.author: self.row(self.author, "a"), self.meta: self.row(self.meta, "b"),
                            self.folder_meta: self.row(self.folder_meta, "c")}
        self.isolated_rows = copy.deepcopy(self.formal_rows)
        self.isolated_rows[self.meta] = self.row(self.meta, "d", 6000)
        self.isolated_rows[self.folder_meta] = self.row(self.folder_meta, "e")
        target = pub.gate.FAMILY + "/" + self.plan["characterId"]
        for p in (target + "/appearance.json", target + ".meta", pub.gate.FAMILY + ".meta"):
            self.isolated_rows[p] = self.row(p, "f")
        self.stage_record = {"schema": pub.stage.SCHEMA, "status": "staged_pending_real_unity_validation",
            "writesPerformed": True, "protected_changed_files": 0, "formal_publication_authorized": False,
            "stage_tool_sha256": pub.sha(Path(pub.stage.__file__)), "character_id": self.plan["characterId"],
            "approved": self.plan["approved"], "project": str(self.isolated), "target": str(self.isolated / target),
            "audit": str(self.audit), "runtime_outputs": self.plan["outputs"],
            "approved_inventory": self.plan["approvedInventory"], "staged_at_utc": "2026-01-02T00:00:00Z",
            "protected_before": {p[len(self.prefix):]: row["sha256"] for p, row in self.isolated_rows.items()
                if p in (self.author, self.meta, self.folder_meta)}}
        self.baseline_record = {"schema": 1, "created_utc": "2026-01-01T00:00:00Z",
            "project": str(self.formal), "scope": pub.FORMAL_BASELINE_SCOPE,
            "prior_review_sha256": pub.FORMAL_BASELINE_PRIOR_REVIEW_SHA256,
            "source_paths": list(pub.gate.INPUT_BINDING_PATHS), "character_resource_count": len(self.formal_rows),
            "files": list(copy.deepcopy(self.formal_rows).values()) + [self.row(p, "1") for p in pub.gate.INPUT_BINDING_PATHS],
            "test_fixture": "Small synthetic dictionary only"}
        for name, value in (("FORMAL", self.formal), ("ISOLATED", self.isolated), ("RUNS", self.runs),
                            ("FORMAL_BASELINE_CHARACTER_COUNT", len(self.formal_rows))):
            context = patch.object(pub, name, value)
            context.start(); self.addCleanup(context.stop)
        context = patch.object(pub.stage, "AUDIT_ROOT", self.audit_root)
        context.start(); self.addCleanup(context.stop)
        self.write(self.audit, self.stage_record)
        self.write(self.baseline, self.baseline_record)
        self.sha_patch = patch.object(pub, "FORMAL_BASELINE_SHA256", pub.sha(self.baseline))
        self.sha_patch.start(); self.addCleanup(self.sha_patch.stop)

    @staticmethod
    def row(path, digit, size=62):
        return {"path": path, "sha256": digit * 64, "bytes": size}

    @staticmethod
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pub.encoded(value))

    def check(self):
        return pub.stage_binding(self.audit, self.plan, self.isolated_rows, self.formal_rows)

    def rewrite_baseline_with_test_pin(self):
        self.write(self.baseline, self.baseline_record)
        # Only in this synthetic test: update the mocked constant to exercise
        # inner identity/scope validation independently of the outer SHA gate.
        pub.FORMAL_BASELINE_SHA256 = pub.sha(self.baseline)

    def test_independent_guid_and_importer_bytes_are_preserved_and_accepted(self):
        before = copy.deepcopy((self.formal_rows, self.isolated_rows, self.stage_record))
        result = self.check()["verified_legacy_protection"]
        self.assertEqual(result["crossProjectDifferentMetaCount"], 2)
        self.assertEqual(result["crossProjectAuthoredFileCount"], 1)
        self.assertEqual(result["formalOldFileCount"], 3)
        self.assertEqual(result["isolatedOldFileCount"], 3)
        self.assertEqual(before, (self.formal_rows, self.isolated_rows, self.stage_record))

    def test_formal_author_sha_change_rejected(self):
        self.formal_rows[self.author]["sha256"] = "2" * 64
        with self.assertRaisesRegex(ValueError, "own safety baseline"): self.check()

    def test_formal_meta_sha_change_rejected(self):
        self.formal_rows[self.meta]["sha256"] = "2" * 64
        with self.assertRaisesRegex(ValueError, "own safety baseline"): self.check()

    def test_formal_byte_size_change_rejected(self):
        self.formal_rows[self.meta]["bytes"] += 1
        with self.assertRaisesRegex(ValueError, "own safety baseline"): self.check()

    def test_formal_missing_or_extra_old_file_rejected(self):
        before = copy.deepcopy(self.formal_rows)
        for relative in (self.author, self.meta):
            self.formal_rows = copy.deepcopy(before); del self.formal_rows[relative]
            with self.subTest(path=relative), self.assertRaisesRegex(ValueError, "own safety baseline"): self.check()
        self.formal_rows = copy.deepcopy(before)
        extra = self.prefix + "unexpected.meta"; self.formal_rows[extra] = self.row(extra, "3")
        with self.assertRaisesRegex(ValueError, "own safety baseline"): self.check()

    def test_isolated_author_or_meta_change_rejected(self):
        before = copy.deepcopy(self.isolated_rows)
        for relative in (self.author, self.meta, self.folder_meta):
            self.isolated_rows = copy.deepcopy(before); self.isolated_rows[relative]["sha256"] = "4" * 64
            with self.subTest(path=relative), self.assertRaisesRegex(ValueError, "since staging"): self.check()

    def test_isolated_missing_or_extra_old_file_rejected(self):
        before = copy.deepcopy(self.isolated_rows)
        for relative in (self.author, self.meta):
            self.isolated_rows = copy.deepcopy(before); del self.isolated_rows[relative]
            with self.subTest(path=relative), self.assertRaisesRegex(ValueError, "since staging"): self.check()
        self.isolated_rows = copy.deepcopy(before)
        extra = self.prefix + "unexpected.meta"; self.isolated_rows[extra] = self.row(extra, "3")
        with self.assertRaisesRegex(ValueError, "since staging"): self.check()

    def test_cross_project_authored_change_even_with_consistent_isolated_baseline_rejected(self):
        self.isolated_rows[self.author]["sha256"] = "5" * 64
        self.stage_record["protected_before"][self.relative] = "5" * 64
        self.write(self.audit, self.stage_record)
        with self.assertRaisesRegex(ValueError, "authored character resources differ"): self.check()

    def test_replaced_formal_baseline_bytes_rejected(self):
        self.baseline.write_bytes(self.baseline.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "baseline bytes changed"): self.check()

    def test_wrong_formal_baseline_project_scope_or_prior_review_rejected(self):
        original = copy.deepcopy(self.baseline_record)
        for field, value in (("project", str(self.isolated)), ("scope", "arbitrary new baseline"),
                             ("prior_review_sha256", "6" * 64), ("schema", 2)):
            self.baseline_record = copy.deepcopy(original); self.baseline_record[field] = value
            self.rewrite_baseline_with_test_pin()
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "identity/scope"): self.check()

    def test_formal_baseline_missing_source_or_resource_row_rejected(self):
        original = copy.deepcopy(self.baseline_record)
        for relative in (self.author, pub.gate.INPUT_BINDING_PATHS[0]):
            self.baseline_record = copy.deepcopy(original)
            self.baseline_record["files"] = [r for r in self.baseline_record["files"] if r["path"] != relative]
            self.rewrite_baseline_with_test_pin()
            with self.subTest(path=relative), self.assertRaisesRegex(ValueError, "resource scope"): self.check()

    def test_formal_baseline_duplicate_source_or_file_rejected(self):
        self.baseline_record["source_paths"].append(self.baseline_record["source_paths"][0])
        self.rewrite_baseline_with_test_pin()
        with self.assertRaisesRegex(ValueError, "source scope"): self.check()
        self.baseline_record["source_paths"].pop()
        self.baseline_record["files"].append(copy.deepcopy(self.baseline_record["files"][0]))
        self.rewrite_baseline_with_test_pin()
        with self.assertRaisesRegex(ValueError, "duplicate paths"): self.check()

    def test_baseline_created_after_stage_rejected(self):
        self.baseline_record["created_utc"] = "2026-01-03T00:00:00Z"
        self.rewrite_baseline_with_test_pin()
        with self.assertRaisesRegex(ValueError, "must precede"): self.check()

    def test_preexisting_v14_family_meta_is_still_protected(self):
        path = pub.gate.FAMILY + ".meta"
        self.stage_record["protected_before"][path[len(self.prefix):]] = "7" * 64
        self.write(self.audit, self.stage_record)
        with self.assertRaisesRegex(ValueError, "since staging"): self.check()

    def test_new_target_cannot_be_hidden_inside_old_stage_inventory(self):
        path = "QdaoOriginalRosterV14/04_mountain_guardian_boy/appearance.json"
        self.stage_record["protected_before"][path] = "f" * 64
        self.write(self.audit, self.stage_record)
        with self.assertRaisesRegex(ValueError, "already contains"): self.check()

    def test_traversal_in_stage_inventory_rejected(self):
        self.stage_record["protected_before"]["../not-a-character.meta"] = "8" * 64
        self.write(self.audit, self.stage_record)
        with self.assertRaisesRegex(ValueError, "Invalid isolated"): self.check()


if __name__ == "__main__": unittest.main()
