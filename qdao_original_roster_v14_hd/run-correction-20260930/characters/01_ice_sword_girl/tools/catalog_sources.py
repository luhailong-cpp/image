#!/usr/bin/env python3
"""Catalog existing source PNGs and research candidates for this character only.

Uses only the Python standard library. Default is read-only; --write writes
source .png.generation.json sidecars and the character-local manifest.json.
Never edits PNGs, receipts, prompts, export scripts, client files or shared data.
No number of files or technical checks can grant artistic acceptance here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import sys
import uuid
import zlib

sys.dont_write_bytecode = True
ROLE = "01_ice_sword_girl"
ROOT = Path(__file__).resolve().parents[1]
AUTHORIZED_ROOT = Path(
    "D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/"
    "run-correction-20260930/characters/01_ice_sword_girl"
).resolve()
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
PNG_MODES = {0: "L", 2: "RGB", 3: "P", 4: "LA", 6: "RGBA"}


def utc_time(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def guarded(path: Path) -> Path:
    resolved = path.resolve()
    if ROOT != AUTHORIZED_ROOT or not resolved.is_relative_to(ROOT):
        raise ValueError(f"Path escapes the sole authorized write directory: {resolved}")
    return resolved


def local(path: Path) -> str:
    return guarded(path).relative_to(ROOT).as_posix()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def file_record(path: Path, inside: bool = True) -> dict:
    resolved = guarded(path) if inside else path.resolve()
    result = {"path": local(resolved) if inside else str(resolved),
              "absolutePath": str(resolved), "present": resolved.is_file()}
    if resolved.is_file():
        data = resolved.read_bytes()
        result.update(sha256=digest(data), bytes=len(data))
    else:
        result.update(sha256=None, bytes=None)
    return result


def png_info(data: bytes) -> dict:
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("File is not a PNG")
    offset, ihdr, chunks = 8, None, []
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("Truncated PNG chunk")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        end = offset + length + 12
        if end > len(data):
            raise ValueError("Truncated PNG chunk payload")
        payload = data[offset + 8:offset + 8 + length]
        expected_crc = struct.unpack(">I", data[end - 4:end])[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != expected_crc:
            raise ValueError(f"PNG CRC mismatch in {kind!r}")
        chunks.append(kind)
        if kind == b"IHDR":
            if ihdr is not None or length != 13 or len(chunks) != 1:
                raise ValueError("Invalid PNG IHDR")
            ihdr = struct.unpack(">IIBBBBB", payload)
        offset = end
        if kind == b"IEND":
            if length != 0 or offset != len(data):
                raise ValueError("Invalid PNG IEND or trailing data")
            break
    if ihdr is None or not chunks or chunks[-1] != b"IEND" or b"IDAT" not in chunks:
        raise ValueError("Missing required PNG chunks")
    width, height, depth, color, compression, filtering, interlace = ihdr
    if not width or not height or color not in PNG_MODES:
        raise ValueError("Invalid dimensions or unsupported PNG color type")
    return {"width": width, "height": height, "mode": PNG_MODES[color],
            "bitDepth": depth, "pngColorType": color,
            "explicitAlphaChannel": color in (4, 6),
            "transparencyChunk": b"tRNS" in chunks,
            "inspection": "PNG IHDR and all chunk CRCs checked; pixels not decoded; transparent pixels and visual quality not inferred."}


def purpose(reference: str) -> str:
    path = reference.replace("\\", "/").lower()
    if "/designs/" in path:
        return "Approved hand-painted style/material/finish only, not UI composition or character identity."
    if path.endswith("/portrait.png"):
        return "This character's identity and anatomical handedness: right hand ice sword, left hand blue talisman."
    if "/generation/e/09-v1.png" in path:
        return "Direct AI edit input for frame 09: retain identity/camera/design while correcting arm and leg pose."
    if "/generation/e/01-v1.png" in path:
        return "New frame 01 identity, face/head size, canvas scale and camera reference; not evidence of correct target-frame pose."
    if "/walk/" in path:
        return "Existing directional character baseline for identity, scale and camera; old walking pose is not run acceptance."
    return "Submitted visual reference; consult the exact prompt for its role."


def reference_records(receipt: dict, observed_at: str) -> list[dict]:
    submitted = receipt.get("submittedParameters") or {}
    references = submitted.get("referenced_image_paths") or []
    records = []
    for value in references:
        record = file_record(Path(value), inside=False)
        record.update(submittedPath=value, purpose=purpose(value),
                      purposeEvidence="Role interpreted from this image's saved exact prompt and reference path.",
                      hashObservedAtUtc=observed_at,
                      historicalHashLimitation="Current read-only reference SHA; receipt records submitted path but does not establish the file hash at tool submission.")
        records.append(record)
    return records


def source_record(path: Path, now: str, fallback: dict, fallback_file: dict) -> dict:
    path = guarded(path)
    source = file_record(path)
    info = png_info(path.read_bytes())
    receipt_path = guarded(path.with_suffix(".receipt.json"))
    prompt_path = guarded(path.with_suffix(".prompt.txt"))
    if not receipt_path.is_file() or not prompt_path.is_file():
        raise ValueError(f"Source lacks its exact receipt/prompt: {path.name}; no outputs written.")
    receipt = load_json(receipt_path)
    reported = receipt.get("submittedParameters") or {}
    if any(reported.get(key) is not None for key in ("model", "quality")) or any(
        receipt.get(key) is not None for key in ("actualModel", "actualQuality")
    ):
        raise ValueError(f"{path.name}: newly disclosed model/quality needs an explicit catalog schema review; refusing to erase evidence.")
    is_study = path.stem.lower().startswith("study16")
    configuration = receipt.get("configSnapshot")
    from_receipt = configuration is not None
    if configuration is None:
        configuration = fallback.get("configSnapshot")
    if configuration is None:
        raise ValueError(f"No generation-target configuration snapshot for {path.name}")
    source_times = {key: receipt[key] for key in ("generatedAt", "completedAtUtc") if key in receipt}
    result = {
        "schemaVersion": 1, "characterId": ROLE, "catalogedAtUtc": now,
        "file": source["path"], "absolutePath": source["absolutePath"],
        "sha256": source["sha256"], "bytes": source["bytes"],
        "actualNativeWidth": info["width"], "actualNativeHeight": info["height"],
        "actualNativeMode": info["mode"], "pngInspection": info,
        "nativeDimensionsEvidence": "Measured directly from this stored tool-returned PNG, not from requested prompt dimensions; no upscale performed by this catalog.",
        "sourceFileMtime": {"valueUtc": utc_time(path.stat().st_mtime),
                            "kind": "host_file_modification_time",
                            "limitation": "Host filesystem time, potentially affected by copy/save; not proof of generation time."},
        "generationTimeAsReportedByReceipt": source_times or None,
        "receipt": file_record(receipt_path), "prompt": file_record(prompt_path),
        "tool": receipt.get("tool"), "route": receipt.get("route"),
        "toolOutputHintAsReported": receipt.get("output_hint"),
        "configurationTarget": {
            "contents": configuration, "canonicalJsonSha256": digest(encode(configuration)),
            "source": "receipt.configSnapshot" if from_receipt else "generation/config-at-task-start.json:configSnapshot",
            "evidenceFile": file_record(receipt_path) if from_receipt else fallback_file,
            "limitation": "Target configuration only; neither explicit submitted selectors nor confirmed returned model/quality. Fallback is task-start context, not independently proven per-call settings."
        },
        "submittedModel": None, "submittedQuality": None,
        "actualModel": None, "actualQuality": None,
        "submittedParametersAsRecorded": reported,
        "modelQualityUnconfirmedReason": "The builtin image_gen invocation did not expose model or quality selectors, and the tool response did not disclose actual model/version or quality. Prompt text and configuration targets are not submitted API selectors or returned-value evidence.",
        "references": reference_records(receipt, now),
        "assetType": "research-only-4x4-study-sheet" if is_study else "single-frame",
        "researchCandidate": True, "visualPassed": False, "formalExported": False,
        "clientIntegrated": False,
        "acceptance": "Not an accepted running frame; source presence and native dimensions do not prove pose, gait, continuity or artistic quality."
    }
    if is_study:
        result["studySheet"] = {
            "intendedColumns": 4, "intendedRows": 4, "intendedCells": 16,
            "intendedOrder": "row-major 01-16",
            "nativeCellWidth": info["width"] / 4,
            "nativeCellHeight": info["height"] / 4,
            "integerCellGridPossible": info["width"] % 4 == 0 and info["height"] % 4 == 0,
            "cellDimensionsMeaning": "Nominal equal-grid dimensions computed from actual stored sheet size; does not establish observed sprite count, layout correctness or independent poses.",
            "nativeHdFrames": False, "contributesTo128FrameCount": False,
            "limitation": "Research study only. Each cell is smaller than native 1024; cropping or upscaling cannot turn it into a native HD frame. No cells are exported by this script."
        }
    return result


def export_claims() -> dict[str, tuple[dict, dict]]:
    claims = {}
    export_dir = guarded(ROOT / "export")
    if not export_dir.exists():
        return claims
    for path in sorted(export_dir.glob("*.manifest.json")):
        path = guarded(path)
        for record in load_json(path).get("files", []):
            if isinstance(record, dict) and isinstance(record.get("path"), str):
                key = local(ROOT / record["path"])
                claims[key] = (record, file_record(path))
    return claims


def candidate_records() -> list[dict]:
    result = []
    claims = export_claims()
    candidate_dir = guarded(ROOT / "candidate/walk")
    for path in sorted(candidate_dir.rglob("*.png")) if candidate_dir.exists() else []:
        record = file_record(guarded(path))
        record["pngInspection"] = png_info(path.read_bytes())
        record.update(researchCandidate=True, visualPassed=False, formalExported=False,
                      clientIntegrated=False,
                      status="Technical derivative research candidate; presence is not accepted animation delivery.")
        claim, evidence = claims.get(record["path"], ({}, None))
        derivative = claim.get("derivedFrom") or {}
        output_matches = bool(claim) and claim.get("sha256") == record["sha256"]
        source_path = derivative.get("sourcePath")
        source = file_record(guarded(ROOT / source_path)) if source_path else None
        source_matches = bool(source and source["present"] and source["sha256"] == derivative.get("sourceSha256"))
        record["derivationEvidence"] = {
            "exportManifest": evidence,
            "candidateShaMatchesRecordedExport": output_matches,
            "sourceShaMatchesRecordedExport": source_matches,
            "recordedDerivation": derivative or None,
            "sourceObserved": source,
            "status": "Recorded source and output hashes match current files; operation copied from export manifest, not recomputed." if output_matches and source_matches else "Unverified or missing derivation claim; no operation inferred."
        }
        record["technicalDerivativeNote"] = (
            "Export manifest records whole-canvas downsampling to 1024; this only creates a technical research candidate, not a formally accepted export."
            if output_matches and source_matches and derivative.get("operation") == "whole_canvas_LANCZOS_downsample"
            else "Research candidate only; check derivationEvidence for the recorded transformation."
        )
        result.append(record)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write local source sidecars and manifest; otherwise dry run.")
    args = parser.parse_args()
    guarded(ROOT)
    now = datetime.now(timezone.utc).isoformat()
    config_path = guarded(ROOT / "generation/config-at-task-start.json")
    fallback = load_json(config_path)
    fallback_file = file_record(config_path)
    source_dir = guarded(ROOT / "generation/E")
    sources, output_plan = [], {}
    for path in sorted(source_dir.glob("*.png")):
        record = source_record(path, now, fallback, fallback_file)
        sidecar = guarded(path.with_name(path.name + ".generation.json"))
        output_plan[sidecar] = encode(record)
        sources.append({"file": record["file"], "sha256": record["sha256"],
                        "actualNativeWidth": record["actualNativeWidth"],
                        "actualNativeHeight": record["actualNativeHeight"],
                        "actualNativeMode": record["actualNativeMode"],
                        "assetType": record["assetType"],
                        "generationRecord": local(sidecar),
                        "generationRecordSha256": digest(output_plan[sidecar]),
                        "visualPassed": False, "formalExported": False})
    candidates = candidate_records()
    by_path = {record["path"]: record for record in candidates}
    slots = []
    for direction in DIRECTIONS:
        for number in range(1, 17):
            path = f"candidate/walk/{direction}/{number:02d}.png"
            record = by_path.get(path)
            slots.append({"direction": direction, "frame": number, "path": path,
                          "status": "present" if record else "missing",
                          "sha256": record["sha256"] if record else None,
                          "visualPassed": False, "formalExported": False})
    expected_paths = {slot["path"] for slot in slots}
    present = sum(slot["status"] == "present" for slot in slots)
    manifest = {
        "schemaVersion": 1, "characterId": ROLE, "catalogedAtUtc": now,
        "scope": "Read-only catalog of generation/E source PNGs and this character's candidate/walk files; writes only this character's source sidecars and root manifest.",
        "sourceImages": sources, "sourceImageCount": len(sources),
        "singleFrameSourceCount": sum(source["assetType"] == "single-frame" for source in sources),
        "researchStudySheetCount": sum(source["assetType"] != "single-frame" for source in sources),
        "candidateFiles": candidates, "candidateFileCount": len(candidates),
        "expectedSlotCount": 128, "presentSlotCount": present, "missingSlotCount": 128 - present,
        "expectedSlots": slots,
        "unexpectedCandidateFiles": [record["path"] for record in candidates if record["path"] not in expected_paths],
        "visualPassed": 0, "formalExported": 0,
        "clientIntegrated": False, "clientRuntimeVerified": False,
        "dynamicAcceptance": "Not established by this inventory script; see independently authored visual review and playback evidence.",
        "candidateMeaning": "Existing candidate PNGs may be whole-canvas downsampled technical derivatives. They remain research candidates; no artistic pass, complete cycle or formal export is granted by file count, unique hashes or this script.",
        "studyMeaning": "The 4x4 study sheet and its cells never fill any expected native-HD frame slot.",
        "configurationEvidence": fallback_file,
        "catalogTool": file_record(Path(__file__)),
    }
    output_plan[guarded(ROOT / "manifest.json")] = encode(manifest)
    # Complete inspection and path preflight before the first write.
    for path in output_plan:
        guarded(path)
        if path.exists() and not path.is_file():
            raise ValueError(f"Output is not a regular file: {path}")
    written = []
    if args.write:
        for path, data in output_plan.items():
            path = guarded(path)
            if path.is_file() and path.read_bytes() == data:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = guarded(path.with_name(path.name + ".tmp-" + uuid.uuid4().hex))
            try:
                temporary.write_bytes(data)
                os.replace(temporary, path)
            finally:
                if temporary.is_file():
                    temporary.unlink()
            written.append(local(path))
    print(json.dumps({"mode": "write" if args.write else "dry-run",
                      "sourceImages": len(sources), "candidateFiles": len(candidates),
                      "presentSlots": present, "missingSlots": 128 - present,
                      "visualPassed": 0, "formalExported": 0,
                      "clientIntegrated": False, "written": written}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
