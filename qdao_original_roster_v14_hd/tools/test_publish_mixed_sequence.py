"""Small sequential publication/import protection tests, never Unity evidence."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import publish_mixed_roster as pub
import test_publish_mixed_baselines as baseline_tests
import verify_mixed_walk_captures as walking


class SequentialProtectionTests(unittest.TestCase):
    setUp = baseline_tests.SeparateProjectBaselineTests.setUp
    row = staticmethod(baseline_tests.SeparateProjectBaselineTests.row)
    write = staticmethod(baseline_tests.SeparateProjectBaselineTests.write)

    def extension(self, before, character, prior):
        outputs = {p: "9" * 64 for p in pub.gate.EXPECTED_OUTPUTS}
        prefix = pub.gate.FAMILY + "/" + character
        after = copy.deepcopy(before)
        for relative in outputs:
            for suffix in ("", ".meta"):
                path = prefix + "/" + relative + suffix
                after[path] = self.row(path, "9")
        for path in (prefix + "/runtime-index.asset", prefix + "/runtime-index.asset.meta",
                     prefix + ".meta", pub.gate.FAMILY + ".meta"):
            if path not in after:
                after[path] = self.row(path, "8")
        publication = self.root / "publication-audits" / (character + "-publication.json")
        imported = publication.with_name(character + "-import.json")
        receipt = {"schema": pub.SCHEMA, "status": "published_pending_formal_editor_import",
                   "writesPerformed": True, "protectedChangedFiles": 0, "derivedIndexCopied": False,
                   "characterId": character, "project": str(self.formal), "outputs": outputs,
                   "previousImportAudits": [str(p) for p in prior], "previousImportAuditSha256": [pub.sha(p) for p in prior],
                   "protectedFormal": before, "publishedUtc": f"2026-01-02T00:{len(prior)*2:02}:00Z"}
        self.write(publication, receipt)
        self.write(imported, {"schema": pub.IMPORT_SCHEMA, "status": "recorded_local_index_inventory",
                            "project": str(self.formal), "publicationAudit": str(publication),
                            "publicationAuditSha256": pub.sha(publication), "characterResources": after,
                            "recordedUtc": f"2026-01-02T00:{len(prior)*2+1:02}:00Z"})
        return after, imported, receipt

    def chain(self, count=2):
        context = patch.object(pub, "AUDITS", self.root / "publication-audits")
        context.start(); self.addCleanup(context.stop)
        rows, imports = self.formal_rows, []
        for character in pub.approve.assembly.base.MIXED_IDS[:count]:
            rows, imported, receipt = self.extension(rows, character, imports)
            imports.append(imported)
        return rows, imports

    def verify(self, rows, imports):
        return pub.formal_character_baseline(rows, "2026-01-03T00:00:00Z", imports)

    def test_first04_then05_imports_extend_original_baseline_without_reset(self):
        rows, imports = self.chain()
        checked, binding = self.verify(rows, imports)
        self.assertEqual(len(checked), len(rows))
        self.assertEqual([r["characterId"] for r in binding["priorImports"]], list(pub.approve.assembly.base.MIXED_IDS[:2]))
        self.assertEqual(binding["historicalCharacterFileCount"], 3)

    def test_three_mixed_imports_are_protected_in_order(self):
        rows, imports = self.chain(3)
        self.assertEqual(len(self.verify(rows, imports)[1]["priorImports"]), 3)
        with self.assertRaisesRegex(ValueError, "chain differs"):
            self.verify(rows, list(reversed(imports)))

    def test_prior_v14_index_or_meta_changes_and_missing_import_audit_rejected(self):
        rows, imports = self.chain()
        for suffix in ("runtime-index.asset", "runtime-index.asset.meta", "walk/N/01.png.meta"):
            changed = copy.deepcopy(rows)
            changed[pub.gate.FAMILY + "/04_mountain_guardian_boy/" + suffix]["sha256"] = "6" * 64
            with self.subTest(suffix=suffix), self.assertRaisesRegex(ValueError, "own safety baseline"):
                self.verify(changed, imports)
        with self.assertRaisesRegex(ValueError, "own safety baseline"):
            self.verify(rows, imports[:1])

    def test_import_cannot_bless_a_changed_historical_resource(self):
        rows, imports = self.chain(1)
        imported = pub.read(imports[0])
        imported["characterResources"][self.meta]["sha256"] = "6" * 64
        self.write(imports[0], imported)
        with self.assertRaisesRegex(ValueError, "changed protected"):
            self.verify(rows, imports)

    def test_import_requires_140_authored_files_and_index(self):
        rows, imports = self.chain(1)
        imported = pub.read(imports[0])
        del imported["characterResources"][pub.gate.FAMILY + "/04_mountain_guardian_boy/runtime-index.asset"]
        self.write(imports[0], imported)
        with self.assertRaisesRegex(ValueError, "generated index"):
            self.verify(rows, imports)

    def test_prior_publication_receipt_sha_is_pinned(self):
        rows, imports = self.chain(1)
        publication = Path(pub.read(imports[0])["publicationAudit"])
        publication.write_bytes(publication.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "publication audit changed"):
            self.verify(rows, imports)

    def test_independent_indices_are_excluded_only_from_cross_project_author_compare(self):
        rows, imports = self.chain(1)
        self.plan["previousImportAudits"] = [str(p) for p in imports]
        self.plan["characterId"] = "05_celestial_musician_girl"
        target = pub.gate.FAMILY + "/" + self.plan["characterId"]
        isolated = copy.deepcopy(rows)
        index = pub.gate.FAMILY + "/04_mountain_guardian_boy/runtime-index.asset"
        isolated[index]["sha256"] = "4" * 64
        self.stage_record.update(character_id=self.plan["characterId"], target=str(self.isolated / target),
                                 staged_at_utc="2026-01-03T00:00:00Z",
                                 protected_before={p[len(self.prefix):]: r["sha256"] for p, r in isolated.items()})
        self.write(self.audit, self.stage_record)
        isolated[target + "/appearance.json"] = self.row(target + "/appearance.json", "9")
        isolated[target + ".meta"] = self.row(target + ".meta", "9")
        pub.stage_binding(self.audit, self.plan, isolated, rows)
        isolated[index]["sha256"] = "5" * 64
        with self.assertRaisesRegex(ValueError, "since staging"):
            pub.stage_binding(self.audit, self.plan, isolated, rows)


class NativeTargetsTests(unittest.TestCase):
    def test_all_native_directions_pick_first_frame_in_canonical_order(self):
        manifest = {"files": [{"path": f"walk/{d}/{n:02}.png", "source_kind": "native-hd"}
                              for d, n in (("NW", 3), ("NE", 2), ("E", 9), ("NW", 2), ("E", 1))]}
        self.assertEqual(walking.native_targets(manifest), [("NE", 2), ("E", 1), ("NW", 2)])

    def test_one_native_direction_cannot_complete_runtime_capture_gate(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            walking.native_targets({"files": [{"path": "walk/E/01.png", "source_kind": "native-hd"}]})


class FormalIndexBindingTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="mixed-index-unit-", dir=Path(__file__).parent)
        self.addCleanup(temp.cleanup)
        self.project = Path(temp.name)
        self.character = "05_celestial_musician_girl"
        self.target = self.project / pub.gate.FAMILY / self.character
        self.target.mkdir(parents=True)
        self.receipt = {"characterId": self.character, "outputs": {p: "a" * 64 for p in pub.gate.EXPECTED_OUTPUTS},
                        "manifest": {"files": []}}
        lines = ["%YAML 1.1", "--- !u!114 &11400000", "MonoBehaviour:",
                 "  resourceFolder: " + pub.gate.RESOURCE_FAMILY + "/" + self.character,
                 "  manifestSha256: " + "a" * 64, "  activationSha256: " + "a" * 64,
                 "  validationSha256: " + "a" * 64, "  resolutionMode: mixed-preserved-v1", "  entries:"]
        for index, relative in enumerate(sorted(pub.gate.EXPECTED_PNGS)):
            path = self.target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"PRIVATE SYNTHETIC FILE FOR INDEX SERIALIZATION TEST")
            guid = f"{index+1:032x}"
            path.with_suffix(".png.meta").write_text("guid: " + guid + "\n", encoding="utf-8")
            self.receipt["outputs"][relative] = pub.sha(path)
            self.receipt["manifest"]["files"].append({"path": relative, "width": 1024, "height": 1024, "pixels_per_unit": 104})
            lines += ["  - path: " + relative, "    assetGuid: " + guid, "    sha256: " + pub.sha(path),
                      "    width: 1024", "    height: 1024", "    pixelsPerUnit: 104",
                      "    sourceBytes: " + str(path.stat().st_size),
                      "    sourceWriteUtcTicks: " + str(path.stat().st_mtime_ns // 100 + 621355968000000000)]
        self.index = self.target / "runtime-index.asset"
        self.index.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_137_index_rows_bind_actual_local_guids_hashes_and_times(self):
        pub.check_local_index(self.project, self.receipt)

    def test_copied_isolated_guid_or_stale_timestamp_is_rejected(self):
        original = self.index.read_text(encoding="utf-8")
        self.index.write_text(original.replace("assetGuid: " + f"{1:032x}", "assetGuid: " + "f" * 32), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "local PNG GUIDs"):
            pub.check_local_index(self.project, self.receipt)
        self.index.write_text(original.replace("sourceWriteUtcTicks: ", "sourceWriteUtcTicks: 9", 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "timestamp differs"):
            pub.check_local_index(self.project, self.receipt)

    def test_wrong_source_dimensions_are_rejected(self):
        original = self.index.read_text(encoding="utf-8")
        self.index.write_text(original.replace("width: 1024", "width: 512", 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "geometry differs"):
            pub.check_local_index(self.project, self.receipt)


if __name__ == "__main__":
    unittest.main()
