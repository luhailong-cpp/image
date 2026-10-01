#!/usr/bin/env python3
"""07-only truthful registration, fixed-canvas export, preview and technical audit.

Never synthesizes poses, chooses versions, overwrites files or grants visual approval.
Requires Pillow and NumPy. Every write is confined to this character directory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image

CHARACTER = "07_moon_shadow_assassin_girl"
ROOT = Path(__file__).resolve().parents[1]
COUNTS = {"hit": 6, "attack": 12, "cast": 16}
MS = {"hit": 40, "attack": 30, "cast": 45}
KEYS = [(a, d, f) for a, count in COUNTS.items() for d in ("E", "W") for f in range(1, count + 1)]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def local(path):
    path = Path(path)
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f"Write/input path outside this character: {resolved}")
    return resolved


def relative(path):
    return local(path).relative_to(ROOT).as_posix()


def write_new(path, value):
    path = local(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(value, bytes):
        value = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(value)


def png_info(path):
    with Image.open(path) as check:
        if check.format != "PNG":
            raise ValueError(f"Not PNG: {path}")
        check.verify()
    with Image.open(path) as opened:
        opened.load()
        if opened.mode != "RGBA":
            raise ValueError(f"Expected RGBA PNG, found {opened.mode}: {path}")
        image = opened.copy()
    pixels = np.asarray(image)
    alpha = pixels[:, :, 3]
    visible = alpha > 8
    ys, xs = np.where(visible)
    canonical = pixels.copy()
    canonical[alpha <= 8] = 0
    crop = canonical[int(ys.min()):int(ys.max()) + 1, int(xs.min()):int(xs.max()) + 1] if len(xs) else canonical[:0, :0]
    crop_header = str(crop.shape).encode("ascii")
    info = {
        "sha256": sha(path), "width": image.width, "height": image.height,
        "mode": image.mode, "format": "PNG", "alphaMin": int(alpha.min()),
        "alphaMax": int(alpha.max()), "transparentPixels": int(np.count_nonzero(alpha == 0)),
        "visiblePixels": int(visible.sum()),
        "visibleBBox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None,
        "visibleTouchesEdge": bool(visible[0].any() or visible[-1].any() or visible[:, 0].any() or visible[:, -1].any()),
        "visiblePixelSha256": hashlib.sha256(canonical.tobytes()).hexdigest(),
        "mirrorVisiblePixelSha256": hashlib.sha256(canonical[:, ::-1].tobytes()).hexdigest(),
        "positionInvariantVisibleSha256": hashlib.sha256(crop_header + crop.tobytes()).hexdigest(),
        "positionInvariantMirrorSha256": hashlib.sha256(crop_header + crop[:, ::-1].tobytes()).hexdigest(),
        "pixelComparisonNote": "For audit hashes only, alpha <= 8 is normalized to zero; source pixels are unchanged.",
    }
    return image, info


def snapshot(args):
    files = []
    for folder in ("staging", "runtime", "selection", "provenance", "prompts"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file():
                files.append({"file": relative(path), "sha256": sha(path), "bytes": path.stat().st_size,
                              "mtimeUtc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()})
    for path in sorted(ROOT.glob("*selection*.json")):
        files.append({"file": relative(path), "sha256": sha(path), "bytes": path.stat().st_size})
    slots = set()
    for item in files:
        match = re.fullmatch(r"staging/(hit|attack|cast)-([EW])-(\d{2})-v\d+\.png", item["file"])
        if match:
            slots.add((match[1], match[2], int(match[3])))
    result = {"character": CHARACTER, "observedAt": now(), "files": files,
              "candidateSlots": len(set(KEYS) & slots), "expectedSlots": 68,
              "missingCandidateSlots": [list(key) for key in KEYS if key not in slots],
              "runtimeSlots": sum((ROOT / f"runtime/{a}/{d}/{f:02d}.png").is_file() for a, d, f in KEYS)}
    write_new(args.out, result)
    return {"snapshot": relative(args.out), "candidateSlots": result["candidateSlots"], "runtimeSlots": result["runtimeSlots"]}


def validate_submission(submission):
    for field in ("configSnapshot", "submittedParameters", "prompt", "references", "submittedAt", "submittedAtEvidence"):
        if not submission.get(field):
            raise ValueError(f"Submission missing {field}")
    params = submission["submittedParameters"]
    if params.get("prompt") != submission["prompt"]:
        raise ValueError("Submission prompt must exactly match actual submittedParameters.prompt")
    if params.get("transparent_background") is not True:
        raise ValueError("This contract requires transparent_background=true")
    refs = submission["references"]
    if not isinstance(refs, list) or any(not ref.get("path") or not ref.get("role") for ref in refs):
        raise ValueError("references must list actual path and purpose for each input")
    if params.get("referenced_image_paths") != [ref["path"] for ref in refs]:
        raise ValueError("references must exactly match actual submitted referenced_image_paths order")


def register(args):
    if not re.fullmatch(r"(hit|attack|cast)-[EW]-\d{2}-v[1-9]\d*", args.label):
        raise ValueError("Label must be action-direction-frame-vN")
    action, direction, frame, _ = args.label.split("-")
    if (action, direction, int(frame)) not in KEYS:
        raise ValueError("Label is outside one of the 68 authorized slots")
    submission_path, returned_path = local(args.submission), local(args.returned)
    submission, returned = read(submission_path), read(returned_path)
    validate_submission(submission)
    if returned.get("status") != "success" or not returned.get("returnedAt") or not returned.get("evidence"):
        raise ValueError("Returned evidence must record status=success, returnedAt, evidence")
    source = Path(args.source).resolve()
    declared_source = returned.get("toolReturnedPath")
    if not declared_source or Path(declared_source).resolve() != source:
        raise ValueError("Source must match actual toolReturnedPath in returned evidence")
    image, info = png_info(source)
    image.close()
    if info["width"] < 1024 or info["height"] < 1024:
        raise ValueError("Native single-frame output smaller than 1024 in either dimension")
    destination = ROOT / "staging" / (args.label + ".png")
    receipt = ROOT / "provenance/receipts" / (args.label + ".json")
    if destination.exists() or receipt.exists():
        raise ValueError("Existing source/receipt will not be overwritten")
    record = {
        "file": relative(destination), **info, "nativeSize": [info["width"], info["height"]],
        "generatedAt": returned.get("generatedAt", returned["returnedAt"]),
        "generatedAtEvidence": returned.get("generatedAtEvidence", "Tool completion observed at returnedAt; generation start/end was not disclosed."),
        "recordedAt": now(), "tool": "image_gen.imagegen", "route": "builtin",
        "configSnapshot": submission["configSnapshot"], "submittedParameters": submission["submittedParameters"],
        "actualModel": returned.get("actualModel"), "actualQuality": returned.get("actualQuality"),
        "unverifiedReason": returned.get("unverifiedReason", "Host-managed tool did not disclose actual model or quality; both remain unconfirmed."),
        "prompt": submission["prompt"], "references": submission["references"],
        "evidence": {"submissionRecord": relative(submission_path), "submissionSha256": sha(submission_path),
                     "returnRecord": relative(returned_path), "returnRecordSha256": sha(returned_path),
                     "toolReturnedPath": str(source), "returnedEvidence": returned["evidence"]},
        "review": {"status": "pending"}, "clientIntegration": "not_integrated",
    }
    write_new(destination, source.read_bytes())
    write_new(receipt, record)
    return {"file": relative(destination), "generationRecord": relative(receipt), "sha256": info["sha256"], "nativeSize": record["nativeSize"]}


def read_selection(path):
    selection = read(local(path))
    if selection.get("status") != "complete":
        raise ValueError("Export requires status=complete explicit selection")
    rows = selection.get("frames", [])
    keys = [(row.get("action"), row.get("direction"), row.get("frame")) for row in rows]
    if len(rows) != 68 or set(keys) != set(KEYS):
        raise ValueError("Selection must contain each of the 68 authorized slots exactly once")
    seen, visible_sources, mirrored_sources = set(), {}, {}
    for row in rows:
        source, receipt = local(row["file"]), local(row["generationRecord"])
        if source in seen:
            raise ValueError(f"Source selected into multiple slots: {source}")
        seen.add(source)
        record = read(receipt)
        digest = sha(source)
        if row.get("sha256") != digest or record.get("sha256") != digest:
            raise ValueError(f"Selection/source/record SHA mismatch: {source}")
        if local(record["file"]) != source:
            raise ValueError(f"Generation record points to another image: {source}")
        for field in ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot", "submittedParameters", "evidence", "prompt", "references", "actualModel", "actualQuality"):
            if field not in record:
                raise ValueError(f"Source record missing {field}: {receipt}")
        if (record["actualModel"] is None or record["actualQuality"] is None) and not record.get("unverifiedReason"):
            raise ValueError(f"Undisclosed actual values need explicit unverifiedReason: {receipt}")
        image, info = png_info(source)
        if info["width"] < 1024 or info["height"] < 1024:
            raise ValueError(f"Native single-frame source smaller than 1024: {source}")
        if not info["transparentPixels"] or not info["visiblePixels"] or info["visibleTouchesEdge"]:
            raise ValueError(f"Source transparency/visibility/edge check failed: {source}")
        visible_digest = info["positionInvariantVisibleSha256"]
        if visible_digest in visible_sources or visible_digest in mirrored_sources:
            raise ValueError(f"Source is an exact visible duplicate/mirror even after translation: {source}")
        visible_sources[visible_digest] = source
        mirrored_sources[info["positionInvariantMirrorSha256"]] = source
        row.update(source=source, receipt=receipt, record=record, image=image, info=info)
    return rows


def prepare_export(args):
    rows = read_selection(args.selection)
    sizes = {row["image"].size for row in rows}
    if len(sizes) != 1:
        raise ValueError(f"One fixed global canvas requires identical native dimensions: {sizes}")
    size = next(iter(sizes))
    transform = read(local(args.transform)) if args.transform else {"nativeCanvas": [1024, 1024], "scaledWholeCanvas": [1024, 1024], "offset": [0, 0], "reason": "Identity export; generated frames already use agreed canvas and anchor."}
    if transform.get("nativeCanvas") != list(size):
        raise ValueError("Explicit transform nativeCanvas does not match; only 1024 identity is the default")
    target = transform["scaledWholeCanvas"]
    if len(target) != 2 or any(type(n) is not int or n <= 0 for n in target):
        raise ValueError("scaledWholeCanvas must be positive integers")
    if target[0] > size[0] or target[1] > size[1] or abs(target[0] / size[0] - target[1] / size[1]) > 0.001:
        raise ValueError("Only uniform whole-canvas downsample or identity is allowed")
    if not transform.get("reason"):
        raise ValueError("Explicit transform requires a reason")
    hashes, mirrors = {}, {}
    for row in rows:
        action, direction, frame = row["action"], row["direction"], row["frame"]
        offset = transform.get("directionOffsets", {}).get(direction, transform.get("offset"))
        if not isinstance(offset, list) or len(offset) != 2 or any(type(n) is not int for n in offset):
            raise ValueError("Fixed offset or directionOffsets E/W integer pair required")
        image = row["image"]
        scaled = image if image.size == tuple(target) else image.resize(tuple(target), Image.Resampling.LANCZOS)
        bbox = scaled.getchannel("A").getbbox()
        if not bbox or bbox[0] + offset[0] < 0 or bbox[1] + offset[1] < 0 or bbox[2] + offset[0] > 1024 or bbox[3] + offset[1] > 1024:
            raise ValueError(f"Fixed transform would clip nontransparent pixels: {row['file']}")
        output = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        output.paste(scaled, tuple(offset))
        array = np.array(output)
        array[array[:, :, 3] <= 8] = 0
        digest = hashlib.sha256(array.tobytes()).hexdigest()
        mirror = hashlib.sha256(array[:, ::-1].tobytes()).hexdigest()
        if digest in hashes or digest in mirrors:
            raise ValueError(f"Visible duplicate or exact mirror: {row['file']} / {hashes.get(digest, mirrors.get(digest))}")
        hashes[digest], mirrors[mirror] = row["file"], row["file"]
        buffer = io.BytesIO()
        output.save(buffer, format="PNG")
        row["png"] = buffer.getvalue()
        destination = ROOT / f"runtime/{action}/{direction}/{frame:02d}.png"
        receipt = ROOT / f"provenance/receipts/derived/{action}-{direction}-{frame:02d}.json"
        row["destination"], row["derivedReceipt"] = destination, receipt
        row["derived"] = {
            "file": relative(destination), "sha256": hashlib.sha256(row["png"]).hexdigest(),
            "generatedAt": row["record"]["generatedAt"], "derivedAt": now(),
            "width": 1024, "height": 1024, "format": "PNG", "mode": "RGBA",
            "tool": "Pillow fixed whole-canvas export", "route": "derived",
            "derivedFrom": {"file": row["file"], "sha256": row["sha256"], "generationRecord": row["generationRecord"], "generationRecordSha256": sha(row["receipt"])},
            "operation": {"kind": "fixed_whole_canvas_export", "transform": transform, "appliedOffset": offset,
                          "resampling": "identity" if image.size == tuple(target) else "Pillow LANCZOS",
                          "noPerFrameBBoxAdjustment": True, "noPoseSynthesis": True, "noAlphaEditing": True},
            "selection": relative(args.selection), "selectionSha256": sha(local(args.selection)),
            "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
        }
    return rows, transform


def export(args):
    rows, transform = prepare_export(args)
    if args.publish:
        for row in rows:
            if row["destination"].exists() or row["derivedReceipt"].exists():
                raise ValueError(f"Refuse to overwrite runtime/receipt: {row['destination']}")
        for row in rows:
            write_new(row["derivedReceipt"], row["derived"])
            write_new(row["destination"], row["png"])
    return {"selectedSlots": len(rows), "technicalPreflight": "passed", "published": bool(args.publish), "transform": transform,
            "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}


def preview(args):
    destination = local(args.out)
    sets = []
    for action, count in COUNTS.items():
        for direction in ("E", "W"):
            paths = [ROOT / f"runtime/{action}/{direction}/{number:02d}.png" for number in range(1, count + 1)]
            if not all(path.is_file() for path in paths):
                raise ValueError(f"Complete runtime required for six-segment preview; missing {action}/{direction}")
            sets.append({"action": action, "direction": direction, "ms": MS[action],
                         "images": [Path(os.path.relpath(path, destination.parent)).as_posix() for path in paths]})
    template = Path(__file__).with_name("preview.html").read_text(encoding="utf-8")
    write_new(destination, template.replace("__SETS__", json.dumps(sets)).encode("utf-8"))
    return {"preview": relative(destination), "visualApproval": "pending", "normalFrameMs": MS, "slowMultiplier": 0.25}


def audit(args):
    frames, issues, hashes, mirrors, cropped, cropped_mirrors = [], [], {}, {}, {}, {}
    retention_path = ROOT / "provenance/retention.json"
    retention = read(retention_path).get("removed", []) if retention_path.exists() else []
    for action, direction, frame in KEYS:
        path = ROOT / f"runtime/{action}/{direction}/{frame:02d}.png"
        receipt = ROOT / f"provenance/receipts/derived/{action}-{direction}-{frame:02d}.json"
        row = {"action": action, "direction": direction, "frame": frame, "file": relative(path), "issues": []}
        try:
            image, info = png_info(path)
            image.close()
            row.update(info)
            if (info["width"], info["height"]) != (1024, 1024):
                row["issues"].append("wrong_dimensions")
            if not info["transparentPixels"] or not info["visiblePixels"]:
                row["issues"].append("missing_transparency_or_visible_subject")
            if info["visibleTouchesEdge"]:
                row["issues"].append("visible_subject_touches_edge")
            digest = info["visiblePixelSha256"]
            if digest in hashes:
                row["issues"].append("duplicate_visible_pixels:" + hashes[digest])
            if digest in mirrors:
                row["issues"].append("exact_mirror_visible_pixels:" + mirrors[digest])
            hashes[digest], mirrors[info["mirrorVisiblePixelSha256"]] = row["file"], row["file"]
            cropped_digest = info["positionInvariantVisibleSha256"]
            if cropped_digest in cropped:
                row["issues"].append("translated_visible_duplicate:" + cropped[cropped_digest])
            if cropped_digest in cropped_mirrors:
                row["issues"].append("translated_visible_mirror:" + cropped_mirrors[cropped_digest])
            cropped[cropped_digest], cropped_mirrors[info["positionInvariantMirrorSha256"]] = row["file"], row["file"]
            record = read(receipt)
            if record["sha256"] != info["sha256"] or local(record["file"]) != path:
                row["issues"].append("derived_receipt_mismatch")
            source = record["derivedFrom"]
            source_record_path = local(source["generationRecord"])
            source_record = read(source_record_path)
            if sha(source_record_path) != source["generationRecordSha256"] or source_record["sha256"] != source["sha256"]:
                row["issues"].append("source_receipt_chain_mismatch")
            source_path = local(source["file"])
            if source_path.exists():
                if sha(source_path) != source["sha256"]:
                    row["issues"].append("source_image_hash_mismatch")
            elif not any(item.get("file") == source["file"] and item.get("sha256") == source["sha256"]
                         and item.get("removedAt") and item.get("reason") and item.get("verifiedFinalSha256") == info["sha256"]
                         for item in retention):
                row["issues"].append("source_missing_without_retention_record")
            if not record.get("operation") or not record.get("selection"):
                row["issues"].append("missing_operation_or_selection")
            elif sha(local(record["selection"])) != record["selectionSha256"]:
                row["issues"].append("selection_changed_since_export")
            for field in ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot", "submittedParameters", "evidence", "prompt", "references", "actualModel", "actualQuality"):
                if field not in source_record:
                    row["issues"].append("source_receipt_missing_" + field)
            evidence = source_record["evidence"]
            for name, hash_name in (("submissionRecord", "submissionSha256"), ("returnRecord", "returnRecordSha256")):
                if name not in evidence or sha(local(evidence[name])) != evidence.get(hash_name):
                    row["issues"].append("generation_evidence_chain_mismatch_" + name)
            if evidence.get("submissionRecord"):
                submission = read(local(evidence["submissionRecord"]))
                validate_submission(submission)
                if submission["submittedParameters"] != source_record["submittedParameters"] or submission["configSnapshot"] != source_record["configSnapshot"]:
                    row["issues"].append("submission_record_content_mismatch")
            if (source_record.get("actualModel") is None or source_record.get("actualQuality") is None) and not source_record.get("unverifiedReason"):
                row["issues"].append("undisclosed_model_quality_without_reason")
            row["sourceGenerationRecord"] = source["generationRecord"]
        except (OSError, ValueError, KeyError) as exc:
            row["issues"].append(str(exc))
        frames.append(row)
    expected = {row["file"] for row in frames}
    unexpected = [relative(path) for path in (ROOT / "runtime").rglob("*.png") if relative(path) not in expected]
    if unexpected:
        issues.append({"unexpectedRuntimePng": unexpected})
    result = {"character": CHARACTER, "auditedAt": now(), "expectedSlots": 68,
              "presentSlots": sum((ROOT / row["file"]).is_file() for row in frames),
              "framesWithIssues": sum(bool(row["issues"]) for row in frames), "issues": issues,
              "technicalAuditPassed": not issues and all(not row["issues"] for row in frames),
              "frames": frames, "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
              "limitation": "Unique pixels and absence of exact mirrors do not prove unique poses, identity, anatomical correctness or animation quality; actual six-segment visual playback review is required."}
    write_new(args.out, result)
    print(json.dumps({k: v for k, v in result.items() if k != "frames"}, ensure_ascii=False, indent=2))
    return 0 if result["technicalAuditPassed"] else 2


def main():
    if ROOT.name != CHARACTER:
        raise ValueError("This private tool must remain under 07 character")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("snapshot")
    cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("register")
    for name in ("source", "label", "submission", "returned"):
        cmd.add_argument("--" + name, required=True)
    cmd = sub.add_parser("export")
    cmd.add_argument("--selection", required=True)
    cmd.add_argument("--transform")
    cmd.add_argument("--publish", action="store_true")
    cmd = sub.add_parser("preview")
    cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("audit")
    cmd.add_argument("--out", required=True)
    args = parser.parse_args()
    result = globals()[args.command](args)
    if isinstance(result, int):
        return result
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"combat07: {exc}", file=sys.stderr)
        raise SystemExit(2)
