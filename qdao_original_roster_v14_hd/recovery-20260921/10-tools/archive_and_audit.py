"""Character 10 only: preserve real built-in results and audit their bytes.

No image generation, pixel editing, visual approval or shared-index writes.
Commands: preflight; archive --archive DIR --original PNG --result JSON;
          check --archive DIR.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
from PIL import Image

HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
ROOT = HERE.parents[2]
GENERATION = RECOVERY / "10-generation"
AUDIT = RECOVERY / "10-work/audit"
CHARACTER = "10_crimson_spear_girl"
PORTRAIT = ROOT / "q_daoist_character_pack_4096/10_crimson_spear_girl_transparent_4096.png"
IDENTITY = RECOVERY / "10-work/references/identity-inspection-1024.png"
CONFIG = ROOT / "config/image-generation.json"
DIRS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write_new(path, value):
    path = Path(path)
    require(not path.exists(), f"Refusing to replace evidence: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def relative(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def inspect(path):
    with Image.open(path) as image:
        image.load()
        alpha = image.getchannel("A") if "A" in image.getbands() else None
        extrema = list(alpha.getextrema()) if alpha is not None else None
        return {
            "file": relative(path), "sha256": sha(path),
            "width": image.width, "height": image.height,
            "format": image.format, "mode": image.mode,
            "alphaRange": extrema,
            "hasTransparentPixels": extrema is not None and extrema[0] < 255,
            "alphaBBox": list(alpha.getbbox()) if alpha is not None and alpha.getbbox() else None,
        }


def archive_dir(path):
    path = Path(path).resolve()
    require(path.is_relative_to(GENERATION.resolve()) and path != GENERATION.resolve(),
            "Archive must be inside recovery-20260921/10-generation")
    require(path.is_dir(), "Prepare the request archive before archiving")
    return path


def preflight():
    require(PORTRAIT.is_file() and IDENTITY.is_file(), "Missing authoritative or derived identity reference")
    candidates = [ROOT / "qdao_original_roster_v13/candidate" / CHARACTER,
                  ROOT / "qdao_original_roster_v14_hd/candidate" / CHARACTER,
                  RECOVERY / "10-work"]
    rows = []
    for base in candidates:
        if base.exists():
            for path in base.rglob("*.png"):
                rel = path.relative_to(base).as_posix()
                if re.search(r"(?:^|/)walk/(?:N|NE|E|SE|S|SW|W|NW)/\d{2}\.png$", rel):
                    rows.append({"kind": "walk", "path": relative(path), "sha256": sha(path)})
                elif re.search(r"(?:^|/)idle/(?:N|NE|E|SE|S|SW|W|NW)\.png$", rel):
                    rows.append({"kind": "idle", "path": relative(path), "sha256": sha(path)})
    value = {
        "checkedAt": utc(), "character": CHARACTER, "readOnlyInventory": True,
        "walk": sum(row["kind"] == "walk" for row in rows),
        "idle": sum(row["kind"] == "idle" for row in rows),
        "expectedWalk": 128, "expectedIdle": 8,
        "searchedRoots": [relative(p) for p in candidates], "foundActions": rows,
        "missingWalk": {direction: list(range(1, 17)) for direction in DIRS} if not rows else None,
        "missingIdle": list(DIRS) if not rows else None,
        "portrait": inspect(PORTRAIT),
        "historicalPortraitRecord": relative(PORTRAIT.parent / "records" / (PORTRAIT.stem + ".json")),
        "note": "4096 portrait is a historical export, not a newly generated native HD action.",
        "visualReview": "not_performed", "clientValidation": "not_performed",
    }
    write_new(AUDIT / "preflight-inventory.json", value)
    write_new(AUDIT / "config-snapshot.json", {
        "capturedAt": utc(), "source": relative(CONFIG), "sourceSHA256": sha(CONFIG),
        "configSnapshot": read(CONFIG),
        "evidenceScope": "Captured during this character task; request.json does not itself include a configuration snapshot.",
    })
    write_new(AUDIT / "identity-inspection-1024.generation.json", {
        **inspect(IDENTITY), "recordedAt": utc(), "tool": None, "route": "local-derived-reference",
        "generatedAt": None, "actualModel": None, "actualQuality": None,
        "unverifiedReason": "Historical original model and quality are not disclosed by the available portrait record.",
        "derivedFrom": [{"file": relative(PORTRAIT), "sha256": sha(PORTRAIT),
                         "generationRecord": relative(PORTRAIT.parent / "records" / (PORTRAIT.stem + ".json"))}],
        "operation": {"type": "whole-image-downsample", "sourceDimensions": [4096, 4096],
                      "outputDimensions": [1024, 1024], "purpose": "identity reference input and inspection only",
                      "newAIImage": False, "countsAsAction": False},
    })
    return {"preflight": relative(AUDIT / "preflight-inventory.json"), "walk": value["walk"], "idle": value["idle"]}


def prompt_bytes(archive, request):
    expected = request["actual_request"]["prompt"].encode("utf-8")
    path = archive / "prompt.txt"
    actual = path.read_bytes()
    if actual != expected:
        require(actual.rstrip(b"\r\n") == expected,
                "Prompt differs beyond patch-added terminal CR/LF; do not alter request meaning")
        require(not (archive / "prompt.before-terminal-newline-normalization.txt").exists(),
                "Existing normalization evidence; investigate instead of overwriting")
    return expected, actual


def reference_rows(request):
    paths = request["actual_request"].get("referenced_image_paths", [])
    require(paths and isinstance(paths, list), "No actual local reference list")
    rows = []
    roles = request.get("referenceRoles", [])
    bindings = request.get("reference_bindings_at_start", [])
    for number, value in enumerate(paths, 1):
        path = Path(value).resolve()
        require(path.is_file() and path.is_relative_to(ROOT), "Reference must exist within this workspace")
        role = roles.get(value) if isinstance(roles, dict) else roles[number - 1] if number <= len(roles) else None
        role = role or ("identity" if number == 1 else "confirmed-style" if number == 2 else "pose-proportion-continuity")
        bound = next((b for b in bindings if str(b.get("path", b.get("file", ""))).replace("\\", "/") == value.replace("\\", "/")), None)
        if bound:
            require(bound.get("sha256") == sha(path), "Reference changed since request start: " + value)
        rows.append({"submittedPath": value, "file": relative(path), "sha256": sha(path),
                     "purpose": role,
                     "hashObservation": "verified-against-request-start-binding" if bound else "archive-time; no matching start-time SHA binding"})
    return rows


def archive_result(args):
    archive = archive_dir(args.archive)
    original = Path(args.original).resolve()
    result_path = Path(args.result).resolve()
    require(original.is_file() and result_path.is_file(), "Actual PNG and result JSON must exist")
    request_path = archive / "request.json"
    request = read(request_path)
    expected_prompt, old_prompt = prompt_bytes(archive, request)
    result = read(result_path)
    hint = result.get("output_hint")
    require(isinstance(hint, str) and hint, "Exact actual tool output_hint is required")
    require(str(original).replace("\\", "/") in hint.replace("\\", "/"),
            "Original PNG path is not in actual output_hint; do not invent a mapping")
    start = request.get("startedAt") or request["actual_request"].get("started_at")
    require(start, "No actual request start timestamp")
    parsed_start = datetime.fromisoformat(start.replace("Z", "+00:00"))
    require(parsed_start.tzinfo is not None, "Request timestamp must include timezone")
    require(request.get("submittedParameters", {"model": None, "quality": None}) == {"model": None, "quality": None},
            "This helper only supports host-managed calls with no model/quality selectors")
    references = reference_rows(request)
    config_record = read(AUDIT / "config-snapshot.json")
    if request.get("configSnapshot"):
        config_record = {"configSnapshot": request["configSnapshot"], "capturedAt": start,
                         "evidenceScope": "Configuration snapshot saved in actual request before submission"}
    config_evidence_path = request_path if request.get("configSnapshot") else AUDIT / "config-snapshot.json"
    outputs = [archive / n for n in ("raw.png", "raw.png.generation.json", "generation-receipt.json", "static-check.json")]
    require(all(not path.exists() for path in outputs), "Use a fresh attempt; immutable evidence already exists")
    result_target = archive / "tool-result.json"
    require(not result_target.exists() or sha(result_target) == sha(result_path), "Conflicting tool-result.json")
    original_info = inspect(original)
    require(original_info["format"] == "PNG", "Actual generated result must be PNG")
    # A small native result is still archived faithfully; it simply fails the HD action gate.
    if old_prompt != expected_prompt:
        (archive / "prompt.before-terminal-newline-normalization.txt").write_bytes(old_prompt)
        (archive / "prompt.txt").write_bytes(expected_prompt)
    if result_target != result_path and not result_target.exists():
        shutil.copy2(result_path, result_target)
    shutil.copy2(original, archive / "raw.png")
    observed_at = utc()
    native_pass = min(original_info["width"], original_info["height"]) >= 1024
    receipt = {
        "character": CHARACTER, "tool": "built-in image_gen", "route": "builtin",
        "requestFile": relative(request_path), "requestSHA256": sha(request_path),
        "actual_request": request["actual_request"], "started_at": start,
        "resultObservedAt": observed_at,
        "completed_at": result.get("completed_at") or result.get("completedAt"),
        "completionTimeEvidence": "Only filled if present in actual result; archive observation is separate.",
        "output_hint": hint, "original_generated_file": str(original),
        "originalPreserved": original.is_file(), "rawSHA256": sha(archive / "raw.png"),
        "toolResultFile": relative(result_target), "toolResultSHA256": sha(result_target),
        "generation_calls": 1, "paid_api_calls": 0, "model_actual": "host-managed-unverified",
        "status": "generated_pending_review" if native_pass else "generated_rejected_native_resolution",
        "promptTerminalNewlineNormalized": old_prompt != expected_prompt,
        "references": references,
    }
    write_new(archive / "generation-receipt.json", receipt)
    generation = {
        **inspect(archive / "raw.png"), "generatedAt": start,
        "generatedAtEvidence": "actual request startedAt; precise model completion timestamp not disclosed",
        "resultObservedAt": observed_at, "tool": "image_gen__imagegen", "route": "builtin",
        "configSnapshot": config_record["configSnapshot"],
        "configSnapshotEvidence": {"file": relative(config_evidence_path),
                                   "sha256": sha(config_evidence_path),
                                   "capturedAt": config_record["capturedAt"],
                                   "scope": config_record["evidenceScope"]},
        "submittedParameters": {"model": None, "quality": None},
        "actualModel": None, "actualQuality": None,
        "unverifiedReason": "宿主管理；本次工具未开放 model/quality 参数，也未披露可核实的实际型号或质量。",
        "evidence": {"request": relative(request_path), "requestSHA256": sha(request_path),
                     "toolResult": relative(result_target), "toolResultSHA256": sha(result_target),
                     "receipt": relative(archive / "generation-receipt.json"),
                     "receiptSHA256": sha(archive / "generation-receipt.json"),
                     "outputHintField": "output_hint", "originalFile": str(original)},
        "prompt": {"file": relative(archive / "prompt.txt"), "sha256": sha(archive / "prompt.txt")},
        "references": references, "nativeHDGate": native_pass,
        "visualReview": "pending", "clientValidation": "not_performed",
    }
    write_new(archive / "raw.png.generation.json", generation)
    check = check_archive(archive)
    write_new(archive / "static-check.json", check)
    return check


def check_archive(archive):
    archive = archive_dir(archive)
    record = read(archive / "raw.png.generation.json")
    receipt = read(archive / "generation-receipt.json")
    request = read(archive / "request.json")
    raw = archive / "raw.png"
    original = Path(receipt["original_generated_file"])
    info = inspect(raw)
    checks = {
        "rawSHA": info["sha256"] == record["sha256"] == receipt["rawSHA256"],
        "originalPreservedByteIdentical": original.is_file() and sha(original) == sha(raw),
        "exactPrompt": (archive / "prompt.txt").read_bytes() == request["actual_request"]["prompt"].encode("utf-8"),
        "requestSHA": sha(archive / "request.json") == record["evidence"]["requestSHA256"],
        "toolResultSHA": sha(ROOT / record["evidence"]["toolResult"]) == record["evidence"]["toolResultSHA256"],
        "receiptSHA": sha(archive / "generation-receipt.json") == record["evidence"]["receiptSHA256"],
        "referenceSHA": all(sha(ROOT / row["file"]) == row["sha256"] for row in record["references"]),
        "dimensions": [info["width"], info["height"]] == [record["width"], record["height"]],
        "nativeAtLeast1024": min(info["width"], info["height"]) >= 1024,
        "transparentAlpha": info["hasTransparentPixels"],
        "modelQualityUnverified": record["actualModel"] is None and record["actualQuality"] is None,
    }
    evidence_keys = set(checks) - {"nativeAtLeast1024", "transparentAlpha"}
    return {"checkedAt": utc(), "character": CHARACTER, "archive": relative(archive),
            "checks": checks, "sourceEvidencePassed": all(checks[k] for k in evidence_keys),
            "nativeAndAlphaGatePassed": checks["nativeAtLeast1024"] and checks["transparentAlpha"],
            "dimensions": [info["width"], info["height"]], "alphaRange": info["alphaRange"],
            "rawSHA256": info["sha256"], "visualReview": "not_performed_by_script",
            "clientValidation": "not_performed", "approved": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    arc = sub.add_parser("archive")
    arc.add_argument("--archive", type=Path, required=True)
    arc.add_argument("--original", type=Path, required=True)
    arc.add_argument("--result", type=Path, required=True)
    check = sub.add_parser("check")
    check.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    value = preflight() if args.command == "preflight" else archive_result(args) if args.command == "archive" else check_archive(args.archive)
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
