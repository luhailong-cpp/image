"""Negative checks use in-memory mutations; original evidence is never written."""
import unittest
from pathlib import Path

import legacy_text_reconciliation as subject


class ExactLegacyExceptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        character, relative, current, expected, rule = subject.WHITELIST[0]
        cls.path = f"{subject.ROOT}/{character}/source/{relative}"
        cls.source_path = f"{subject.ROOT}/{character}/processing/frame-sources.json"
        cls.args = [cls.path, expected, cls.source_path, subject.SOURCE_HASHES[character],
                    Path(cls.path).read_bytes(), Path(cls.source_path).read_bytes()]

    def test_all_eleven_recover_original_record_hashes_without_exporting_text(self):
        report = subject.build_report()
        self.assertEqual(report["exception_count"], 11)
        self.assertEqual(len({r["original_path"] for r in report["items"]}), 11)
        self.assertEqual(sum(r["transformation_rule"] == "crlf_to_lf" for r in report["items"]), 4)
        for row in report["items"]:
            self.assertEqual(row["expected_sha256"], row["reconstructed_sha256"])
            self.assertFalse(row["reconstructed_bytes_exported"])
            self.assertTrue(row["matching_frame_source_keys"])

    def rejected(self, index, value):
        args = list(self.args)
        args[index] = value
        with self.assertRaises(subject.ReconciliationError):
            subject.reconcile_bytes(*args)

    def test_other_path_and_traversal_rejected(self):
        self.rejected(0, self.path.replace("idle-eightdir-v3", "unapproved-batch"))
        self.rejected(0, self.path.replace("/source/", "/source/../source/"))

    def test_wrong_expected_record_hash_rejected(self):
        self.rejected(1, "0" * 64)

    def test_wrong_source_path_and_claimed_hash_rejected(self):
        self.rejected(2, self.source_path.replace("04_mountain_guardian_boy", "06_thunder_caster_boy"))
        self.rejected(3, "0" * 64)

    def test_modified_source_record_bytes_rejected(self):
        self.rejected(5, self.args[5] + b" ")

    def test_modified_text_content_rejected(self):
        self.rejected(4, self.args[4].replace(b"built-in", b"changed", 1))

    def test_unapproved_equivalent_line_endings_rejected(self):
        self.rejected(4, self.args[4].replace(b"\r\n", b"\n"))

    def test_copied_evidence_can_be_checked_without_reading_original_location(self):
        row = subject.reconcile_bytes(*self.args)
        self.assertEqual(row["current_sha256"], subject.sha256(self.args[4]))
        self.assertEqual(row["frame_sources_sha256"], subject.sha256(self.args[5]))


if __name__ == "__main__":
    unittest.main()
