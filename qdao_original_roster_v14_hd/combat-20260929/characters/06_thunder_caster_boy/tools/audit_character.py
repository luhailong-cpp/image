#!/usr/bin/env python3
"""Read-only runtime PNG/provenance audit, with character-local reports.

No visual or client acceptance is inferred. Missing cleaned-up source images
are explicitly reported; their retained generation records remain verifiable.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import sys
from export_character import ROOT, CHARACTER, ACTIONS, DIRECTIONS, EXPECTED, local, rel, sha, read_json, open_rgba, receipt_check, write_new, json_bytes
from preview_character import write_preview


def audit():
    frames, hashes, mirrors, duplicates, mirrored = [], {}, {}, [], []
    for action, (count, ms) in ACTIONS.items():
        for direction in DIRECTIONS:
            for number in range(1, count + 1):
                path = ROOT / "runtime" / action / direction / f"{number:02d}.png"
                receipt = ROOT / "provenance/receipts/derived" / f"{action}-{direction}-{number:02d}.json"
                row = {"action": action, "direction": direction, "frame": number, "file": rel(path),
                       "exists": path.is_file(), "frameDurationMs": ms, "issues": [], "warnings": []}
                if not path.is_file():
                    row["issues"].append("missing_runtime_frame")
                    frames.append(row)
                    continue
                try:
                    image, info = open_rgba(path)
                    row.update(info)
                    row["sha256"] = sha(path)
                    if image.size != (1024, 1024):
                        row["issues"].append("wrong_dimensions")
                    if info["visibleTouchesEdge"]:
                        row["issues"].append("visible_subject_touches_edge")
                    h = info["visiblePixelSha256"]
                    if h in hashes:
                        duplicates.append([hashes[h], row["file"]])
                        row["issues"].append("duplicate_visible_pixels")
                    if h in mirrors:
                        mirrored.append([mirrors[h], row["file"]])
                        row["issues"].append("exact_horizontal_mirror_visible_pixels")
                    hashes[h] = row["file"]
                    mirrors[info["horizontalMirrorVisiblePixelSha256"]] = row["file"]
                    record = read_json(receipt)
                    row["generationRecord"] = rel(receipt)
                    row["generationRecordSha256"] = sha(receipt)
                    if local(record.get("file")) != path:
                        row["issues"].append("runtime_record_file_mismatch")
                    if record.get("sha256") != row["sha256"]:
                        row["issues"].append("runtime_record_sha256_mismatch")
                    if not record.get("operation"):
                        row["issues"].append("missing_export_operation")
                    source = record.get("derivedFrom", {})
                    original = local(source.get("file"))
                    original_record = local(source.get("generationRecord"))
                    if sha(original_record) != source.get("generationRecordSha256"):
                        row["issues"].append("source_receipt_sha256_mismatch")
                    source_record = read_json(original_record)
                    receipt_check(source_record, source.get("sha256"))
                    if local(source_record["file"]) != original:
                        row["issues"].append("source_record_file_mismatch")
                    if original.exists():
                        if sha(original) != source.get("sha256"):
                            row["issues"].append("source_image_sha256_mismatch")
                        row["sourceImageStatus"] = "present_and_hashed"
                    else:
                        row["sourceImageStatus"] = "not_present_generation_record_retained"
                        row["warnings"].append("source_pixels_unavailable_for_live_rehash")
                    evidence = record.get("evidence", {})
                    selection = local(evidence.get("selection"))
                    if sha(selection) != evidence.get("selectionSha256"):
                        row["issues"].append("selection_sha256_mismatch")
                    selection_data = read_json(selection)
                    matching = [entry for entry in selection_data.get("frames", []) if entry.get("frame") == number]
                    if selection_data.get("action") != action or selection_data.get("direction") != direction or len(matching) != 1:
                        row["issues"].append("selection_slot_mismatch")
                    else:
                        item = matching[0]
                        if local(item["file"]) != original or item.get("sha256") != source.get("sha256") or local(item["generationRecord"]) != original_record or item.get("generationRecordSha256") != source.get("generationRecordSha256"):
                            row["issues"].append("selection_source_chain_mismatch")
                    row["nativeDimensions"] = [source_record["width"], source_record["height"]]
                    row["actualModel"] = source_record["actualModel"]
                    row["actualQuality"] = source_record["actualQuality"]
                except Exception as exc:
                    row["issues"].append("audit_error")
                    row["error"] = str(exc)
                frames.append(row)
    expected_paths = {ROOT / "runtime" / a / d / f"{n:02d}.png" for a, d, n in EXPECTED}
    unexpected = [rel(p) for p in (ROOT / "runtime").rglob("*.png") if p not in expected_paths]
    present = sum(row["exists"] for row in frames)
    invalid = sum(bool(row["issues"]) for row in frames)
    return {"character": CHARACTER, "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
            "summary": {"expected": 68, "present": present, "missing": 68 - present, "framesWithIssues": invalid,
                        "duplicateGroups": len(duplicates), "mirroredPairs": len(mirrored),
                        "technicalAuditPassed": invalid == 0 and not unexpected},
            "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
            "note": "Exact pixel/mirror checks cannot establish distinct poses, identity, hand correctness, stable roots or good animation. Those require actual review.",
            "unexpectedRuntimePngs": unexpected, "duplicatePairs": duplicates, "horizontalMirrorPairs": mirrored, "frames": frames}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="New character-local report directory")
    parser.add_argument("--allow-incomplete", action="store_true", help="Only changes exit code; report still records every issue")
    args = parser.parse_args()
    destination = local(args.out)
    if destination.exists():
        raise ValueError(f"Refuse existing audit output: {destination}")
    report = audit()
    write_new(destination / "manifest.json", json_bytes(report))
    write_preview(destination, ROOT / "runtime", "passed" if report["summary"]["technicalAuditPassed"] else "failed_or_incomplete")
    print(json.dumps({"out": str(destination), **report["summary"], "visualApproval": "pending", "clientIntegration": "not_integrated"}, ensure_ascii=False, indent=2))
    return 0 if report["summary"]["technicalAuditPassed"] or args.allow_incomplete else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"audit_character: {exc}", file=sys.stderr)
        raise SystemExit(2)
