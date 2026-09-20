"""Eleven hash-bound legacy text exceptions; all reconstruction stays in memory.

This is not a general newline normalizer. No old file, record, prompt, receipt,
image, or audit is changed. A new JSON report is optional and never overwritten.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath

ROOT = "E:/work/image/qdao_original_roster_v13/candidate"
AUDIT_SHA256 = "51151bc3e3c8b2f696d5929112780ad351a114fbb5000d5c31567937f06caf98"
SCHEMA = "qdao-legacy-text-reconciliation-v1"
SOURCE_HASHES = {
    "04_mountain_guardian_boy": "e075732dd80f8d6bcec0ef817bd4e449a85ca7b44e547e60d16c56b686eccf48",
    "06_thunder_caster_boy": "e417760e438ff3db8ae7d2e203aa1d500788073bc5a830d9641345b294f95bf4",
}
# Character, source-relative path, current byte SHA, original recorded SHA, rule.
# These exact bindings are intentionally not loaded from mutable external config.
WHITELIST = (
    ("04_mountain_guardian_boy", "idle-eightdir-v3/generation-receipt.json", "ec85c71a4a02d5cd135c23281102178c7c4b78b575f95114a760d80371659c08", "29c18d5c82c5f149271627284c9045868f6c4746dbf6de429a1b7faf1075e7fc", "crlf_to_lf"),
    ("04_mountain_guardian_boy", "walk-S-rightboot-pair-v2/prompt.txt", "f8380ff5480d25f04f77844c7072eb0102e3507cd1763629b8d1770dad13eeb5", "0e74994c5bcdaa8cf1f41452065145ac147eaadc6cb0eb35fab2d8540b9db231", "crlf_to_lf"),
    ("04_mountain_guardian_boy", "walk-S-leftboot-pair-v4/prompt.txt", "175bebaa0752779618ad338094d2cb2e6c1475c08b31c0d344a2c36c9f91842e", "2073b77c3db4f6d2c7c36e4047a077ca07db231444a31b82ec18c74b288c4407", "crlf_to_lf_except_terminal_crlf"),
    ("04_mountain_guardian_boy", "NE-tween-02-06-10-14-resume-v1/generation-receipt.json", "5b7800cdafc813a414dd7457fd73f5bb52fa3ff9fb129f6c47ad54111d1fcb18", "5c94657cef4a84bc172cf2598e0f2ef350a5cad60a6d3cf25f082460cf10636a", "crlf_to_lf_except_terminal_crlf"),
    ("04_mountain_guardian_boy", "NE-end-14-15-16-resume-v1/generation-receipt.json", "f21ed195a46402fda66068ff3f11b2aa1e23b8eb471fc1219f106d1d6bcd12b5", "f0585d97cb3df760e5104c40cdd5ab83924dce8624cca9fa7644814d60eec6cd", "crlf_to_lf_except_terminal_crlf"),
    ("04_mountain_guardian_boy", "NE-tween-03-07-11-15-resume-v1/generation-receipt.json", "7e2a9c4ae488548f9356775e71169dcf6c505054aca21cf66c3652a40ba3b0a1", "b796a658fcaf77e6bc5a62b8302ed5ddd9186d2a795966117d8b81cfd64929c1", "crlf_to_lf_except_terminal_crlf"),
    ("04_mountain_guardian_boy", "NE-tween-04-08-12-16-resume-v1/generation-receipt.json", "a135093ab28a1dc37ecb9cc8ccb1244d0f93710b81d2d8e618af21ccded0fab1", "679597793decc2958e86a326bc244ced08dae6cffc87aa2d1f8b822bdafca48f", "crlf_to_lf_except_terminal_crlf"),
    ("04_mountain_guardian_boy", "SE-rightstep-2x4-resume-v1/generation-receipt.json", "d4491677a32cb1d684c9b5d68f62f602a2e17eefdedb5f025288242097235c79", "71448d5d47f421cc9fe9e807e529adf774168e81424f6ef0fd884c14c39850f0", "crlf_to_lf_except_terminal_crlf"),
    ("04_mountain_guardian_boy", "SE-leftstep-2x4-resume-v1/generation-receipt.json", "2b2dfda0e467ef82174b5bf81fafbe3f609d47622f7d1fd46943a5ed8c95196e", "5f14e760a4ee279ba5541e751daa765b1b98a033bbfa3c30b41c883c213c21dc", "crlf_to_lf_except_terminal_crlf"),
    ("06_thunder_caster_boy", "idle-eight-v1/prompt.txt", "a82232884835a7c5c5cb9e7f9bf71e2bf089e1a33563e071df294c48c844d2c6", "912e732d144adfb2240a2258632fc7cd6f431d24f1b796ba351454feea2e13ea", "crlf_to_lf"),
    ("06_thunder_caster_boy", "S-quarter-v1/prompt.txt", "e6f71462cd591aede7e2e25b4e77173378dcf439ed02fc1eb2555658afc72676", "06a010959f30fe04160506b14a2e8c572aa12a2594911f3aebd90ca9ecd5056b", "crlf_to_lf"),
)


class ReconciliationError(ValueError):
    pass


def require(value, message):
    if not value:
        raise ReconciliationError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def path_key(value):
    path = PureWindowsPath(str(value))
    require(path.is_absolute() and ".." not in path.parts, "Exact absolute source path required")
    return path.as_posix().casefold()


def binding_for(path):
    key = path_key(path)
    for row in WHITELIST:
        if key == path_key(f"{ROOT}/{row[0]}/source/{row[1]}"):
            return row
    raise ReconciliationError("Path is not one of the eleven approved text exceptions")


def reconcile_bytes(original_path, expected_sha256, frame_sources_path,
                    frame_sources_sha256, current_bytes, frame_sources_bytes):
    """Validate copied evidence with its ORIGINAL path binding; return JSON data only.

    This enables a self-contained assembly check: supply preserved current text
    bytes and the exact frozen frame-sources bytes. Never supplies recovered text.
    """
    character, relative, current_hash, recorded_hash, rule = binding_for(original_path)
    source_path = f"{ROOT}/{character}/processing/frame-sources.json"
    source_hash = SOURCE_HASHES[character]
    require(expected_sha256 == recorded_hash, "Expected text SHA is not whitelisted")
    require(path_key(frame_sources_path) == path_key(source_path), "Wrong frame-sources path")
    require(frame_sources_sha256 == source_hash, "Frame-sources SHA is not whitelisted")
    require(sha256(frame_sources_bytes) == source_hash, "Frame-sources bytes changed")
    require(sha256(current_bytes) == current_hash, "Current text bytes changed")
    records = json.loads(frame_sources_bytes.decode("utf-8-sig"))
    kind = "prompt" if relative.endswith("/prompt.txt") else "receipt"
    matching = []
    for key, record in records.items():
        evidence = record.get("prompt") if kind == "prompt" else record.get("generation", {}).get("receipt")
        if evidence and evidence.get("path") == "source/" + relative:
            require(evidence.get("sha256") == recorded_hash, "Source record text binding differs")
            matching.append(key)
    require(matching, "Text exception is absent from bound source records")
    normalized = current_bytes.replace(b"\r\n", b"\n")
    require(b"\r" not in normalized, "Unexpected carriage-return byte")
    if rule == "crlf_to_lf":
        reconstructed = normalized
    elif rule == "crlf_to_lf_except_terminal_crlf":
        require(normalized.endswith(b"\n") and not normalized.endswith(b"\n\n"),
                "Expected exactly one terminal newline")
        reconstructed = normalized[:-1] + b"\r\n"
    else:
        raise ReconciliationError("Unknown transformation rule")
    require(sha256(reconstructed) == recorded_hash, "Reconstruction does not match original recorded SHA")
    require(reconstructed.replace(b"\r\n", b"\n") == normalized, "Non-newline content changed")
    return {
        "schema": SCHEMA,
        "status": "reconciled_exact_historical_sha",
        "original_path": f"{ROOT}/{character}/source/{relative}",
        "character_id": character,
        "kind": kind,
        "current_sha256": current_hash,
        "expected_sha256": recorded_hash,
        "transformation_rule": rule,
        "reconstructed_sha256": sha256(reconstructed),
        "current_bytes": len(current_bytes),
        "reconstructed_bytes": len(reconstructed),
        "frame_sources_path": source_path,
        "frame_sources_sha256": source_hash,
        "matching_frame_source_keys": sorted(matching),
        "non_newline_content_unchanged": True,
        "reconstructed_bytes_exported": False,
        "tool_sha256": sha256(Path(__file__).read_bytes()),
    }


def read_stable(path):
    path = Path(path)
    for node in (path, *path.parents):
        require(not node.is_symlink() and not node.is_junction(), "Linked evidence path rejected")
    before = path.stat()
    require(before.st_nlink == 1 and path.is_file(), "Non-file or hard-linked evidence rejected")
    data = path.read_bytes()
    after = path.stat()
    require((before.st_size, before.st_mtime_ns, before.st_nlink) ==
            (after.st_size, after.st_mtime_ns, after.st_nlink), "Evidence changed during read")
    return data


def reconcile_text(path, expected_sha256, frame_sources_path, frame_sources_sha256):
    """Read-only original-file adapter; only exact whitelisted paths are read."""
    row = binding_for(path)
    require(expected_sha256 == row[3], "Expected text SHA is not whitelisted")
    require(path_key(frame_sources_path) == path_key(f"{ROOT}/{row[0]}/processing/frame-sources.json"),
            "Wrong frame-sources path")
    require(frame_sources_sha256 == SOURCE_HASHES[row[0]], "Frame-sources SHA is not whitelisted")
    return reconcile_bytes(path, expected_sha256, frame_sources_path, frame_sources_sha256,
                           read_stable(path), read_stable(frame_sources_path))


def build_report():
    items = [reconcile_text(f"{ROOT}/{character}/source/{relative}", expected,
                           f"{ROOT}/{character}/processing/frame-sources.json", SOURCE_HASHES[character])
             for character, relative, current, expected, rule in WHITELIST]
    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed",
        "exception_count": len(items),
        "original_inventory_audit_sha256": AUDIT_SHA256,
        "tool_sha256": sha256(Path(__file__).read_bytes()),
        "scope": "Only these eleven exact path/hash bindings; all other differences remain rejected.",
        "interpretation": "Historical text byte hashes are exactly reconstructed in memory; this does not approve artwork, alter model labels, or replace visual review.",
        "old_files_modified": False,
        "old_records_modified": False,
        "reconstructed_bytes_exported": False,
        "items": items,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Write only a new JSON beside this tool; refuse overwrite")
    args = parser.parse_args()
    report = build_report()
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        target = args.report.absolute()
        require(target.parent.resolve() == Path(__file__).parent.resolve() and target.suffix == ".json",
                "Report must be a new JSON beside this tool")
        require(not target.exists(), "Existing report cannot be overwritten")
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(output)
        print(json.dumps({"path": str(target), "sha256": sha256(target.read_bytes()),
                          "exception_count": len(report["items"]), "status": report["status"]}))
    else:
        print(output)


if __name__ == "__main__":
    main()
