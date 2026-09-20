"""Metadata/preservation rejection tests; no generated or candidate artwork."""
from pathlib import Path
import tempfile
import unittest

import prepare_mixed_roster as p


class PreparationTests(unittest.TestCase):
    def setUp(self):
        p.PREPARATION_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="metadata-gate-tests-", dir=p.PREPARATION_ROOT)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.evidence = self.source / "evidence.txt"
        self.evidence.write_text("fixture is metadata only\n", encoding="utf-8")
        self.bundle = self.make_bundle()
        self.output = self.root / "snapshot"
        p.write_preparation(self.bundle, self.output)

    def tearDown(self):
        self.temp.cleanup()

    def make_bundle(self):
        digest = p.sha(self.evidence)
        row = p.runtime_file("walk/N/01.png", digest, "b" * 64, "preserved-v13", [627, 627])
        preserved = {"files": [{"character_id": p.MIXED_IDS[0], **row}]}
        snapshot = {"files": [{"path": str(self.evidence), "sha256": digest, "bytes": self.evidence.stat().st_size}],
                    "candidate_trees": [{"root": str(self.source), "files": ["evidence.txt"]}]}
        missing = {"totals": {"walk": 2260, "idle": 128}}
        characters = []
        for index, character in enumerate(p.MIXED_IDS):
            slots = [{"path": path, "state": "missing_awaiting_confirmed_2_5"} for path in p.PNG_PATHS]
            if index == 0:
                slots[0] = {"path": "walk/N/01.png", "runtime_file": row}
            characters.append({"character_id": character, "planned_runtime_slots": slots})
        doc = {"schema": p.SCHEMA, "source_commit": p.SOURCE_COMMIT,
               "preserved_snapshot_sha256": p.value_sha(preserved), "evidence_snapshot_sha256": p.value_sha(snapshot),
               "missing_actions_sha256": p.value_sha(missing), "legacy_evidence_issues": [], "characters": characters,
               "can_assemble_candidate": False, "can_stage": False, "can_publish": False}
        return {"preparation.json": doc, "preserved-output-snapshot.json": preserved,
                "legacy-evidence-snapshot.json": snapshot, "missing-actions.json": missing}

    def mutate_document(self, action):
        path = self.output / "preparation.json"
        doc = p.read(path)
        action(doc)
        path.write_bytes(p.encoded(doc))

    def test_preserved_world_geometry(self):
        row = p.runtime_file("idle/N.png", "a" * 64, "b" * 64, "preserved-v13", [444, 444])
        self.assertEqual(row["pixels_per_unit"], 52)
        self.assertEqual(row["root_px"], [256, 471])
        self.assertEqual(row["width"] / row["pixels_per_unit"], 1024 / 104)
        self.assertEqual(row["sha256"], row["preserved_sha256"])

    def test_legacy_cannot_be_relabelled_as_native_hd(self):
        with self.assertRaisesRegex(ValueError, "relabel"):
            p.runtime_file("walk/N/01.png", "a" * 64, "b" * 64, "native-hd", [1254, 1254])

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            p.safe_child(self.root, "../candidate/frame.png")

    def test_output_run_cannot_be_overwritten(self):
        with self.assertRaisesRegex(ValueError, "immutable"):
            p.write_preparation(self.bundle, self.output)

    def test_snapshot_pass_is_not_approval(self):
        result = p.check_preparation(self.output)
        self.assertEqual(result["status"], "passed_snapshot_integrity")
        self.assertFalse(result["can_publish"])
        with self.assertRaisesRegex(ValueError, "cannot be approved"):
            p.check_preparation(self.output, require_complete=True)

    def test_old_file_mutation_rejected(self):
        self.evidence.write_text("changed historical bytes\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "snapshot mismatch"):
            p.check_preparation(self.output)

    def test_old_file_removal_rejected(self):
        self.evidence.unlink()
        with self.assertRaisesRegex(ValueError, "snapshot mismatch"):
            p.check_preparation(self.output)

    def test_old_tree_addition_rejected(self):
        (self.source / "added.txt").write_text("new", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "inventory_changed"):
            p.check_preparation(self.output)

    def test_snapshot_change_rejected(self):
        (self.output / "preserved-output-snapshot.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "snapshot changed"):
            p.check_preparation(self.output)

    def test_missing_runtime_slot_rejected(self):
        self.mutate_document(lambda doc: doc["characters"][0]["planned_runtime_slots"].pop())
        with self.assertRaisesRegex(ValueError, "planned runtime inventory"):
            p.check_preparation(self.output)

    def test_geometry_substitution_rejected(self):
        self.mutate_document(lambda doc: doc["characters"][0]["planned_runtime_slots"][0]["runtime_file"].update(pixels_per_unit=104))
        with self.assertRaisesRegex(ValueError, "differs from immutable"):
            p.check_preparation(self.output)

    def test_preparation_cannot_self_grant_publication(self):
        self.mutate_document(lambda doc: doc.update(can_publish=True))
        with self.assertRaisesRegex(ValueError, "cannot grant"):
            p.check_preparation(self.output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
