"""Import one locally archived 06 frame without changing historical receipts.

Destination is an isolated staging tree restricted to 06-work or 06-tools; canonical is never written.
This helper creates file-binding evidence, never artwork approval.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE_ROOT = ROOT.parent
CHARACTER = "06_thunder_caster_boy"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def migration_binding(archive):
    raw, prompt, receipt_path, provenance_path = [archive / p for p in (
        "raw.png", "prompt.txt", "generation-receipt.json", "provenance.json")]
    require(all(p.is_file() for p in (raw, prompt, receipt_path)),
            "Need archived raw, exact prompt and actual receipt")
    receipt = read(receipt_path)
    provenance = read(provenance_path) if provenance_path.is_file() else {}
    if provenance:
        require(sha(raw) == provenance.get("sha256"), "Archived raw differs from saved provenance SHA")
    envelope = read(archive / "request.json") if (archive / "request.json").is_file() else {}
    request = receipt.get("actual_request") or envelope.get("request") or envelope
    require(prompt.read_bytes().decode("utf-8-sig") == request.get("prompt"),
            "Prompt bytes differ from actual request")
    require(receipt.get("generation_calls", receipt.get("successfulBuiltinCalls")) == 1 and receipt.get("paid_api_calls", receipt.get("paidApiCalls")) == 0,
            "Receipt must record one built-in and zero paid API calls")
    require(receipt.get("tool") in ("built-in image_gen", "image_gen", "image_gen.imagegen", "image_gen__imagegen"),
            "Not an authorized built-in receipt")
    references = request.get("referenced_image_paths")
    require(isinstance(references, list) and references, "Missing actual reference-image paths")
    mappings = []
    for original in references:
        normalized = str(original).replace("\\", "/")
        if normalized.lower().startswith("e:/work/image/"):
            relative = normalized[len("E:/work/image/"):]
            local = (IMAGE_ROOT / relative).resolve()
            require(local.is_relative_to(IMAGE_ROOT.resolve()), "Reference mapping escapes image workspace")
            mapping_kind = "exact_historical_workspace_prefix"
        else:
            local = Path(original).resolve()
            mapping_kind = "original_path"
        require(local.is_file(), "Local reference not found: " + str(local))
        mappings.append({"historical_request_path": original, "local_path": str(local),
                         "local_sha256": sha(local), "mapping_kind": mapping_kind,
                         "historical_reference_sha_available": False})
    with Image.open(raw) as image:
        size = list(image.size)
    require(min(size) >= 1024 and (not provenance or size == provenance.get("native_size")),
            "Native source must match provenance and be at least 1024 in both dimensions")
    original_name = receipt.get("original_generated_file") or receipt.get("originalOutputPath")
    original = Path(original_name or "")
    original_exists = original.is_file()
    if original_exists:
        require(sha(original) == sha(raw), "Present original generated file differs from saved raw")
    require(bool(provenance) or original_exists, "No saved raw SHA or currently matching original tool output")
    return {"schema": "qdao-local-archived-source-binding-v1", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "archive": str(archive), "raw_sha256": sha(raw), "native_size": size,
            "prompt_sha256": sha(prompt), "receipt_sha256": sha(receipt_path),
            "provenance_sha256": sha(provenance_path) if provenance_path.is_file() else None, "prompt_matches_actual_request": True,
            "raw_matches_historical_provenance_sha": True if provenance else None, "reference_mappings": mappings,
            "historical_original_generated_file": original_name,
            "historical_original_currently_exists": original_exists,
            "original_generated_file_verified_this_run": original_exists,
            "strict_mixed_assembly_receipt_validation": "not_performed_by_this_helper",
            "model_identity_verified": False, "c2pa_signature_verified": False,
            "source_evidence_scope": "unchanged_archive_prompt_receipt_provenance_and_local_file_bindings",
            "visual_review": "pending"}


def preserve_before_import(out, key, batch_id):
    """Keep prior pixels and exact input metadata before any candidate mutation."""
    paths = [key, "processing/frame-sources.json", "manifest.json", "qc.json"]
    direction, frame = key.split("/")[1:]
    paths += [f"review/validation-{direction}-{Path(frame).stem}.json"]
    existing = [p for p in paths if (out / p).is_file()]
    if not existing:
        return None
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = HERE / "history" / f"{timestamp}-{batch_id}"
    require(not backup.exists(), "Backup path unexpectedly exists")
    backup.mkdir(parents=True)
    copied = {}
    for relative in existing:
        target = backup / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out / relative, target)
        copied[relative] = sha(target)
    records = read(out / "processing/frame-sources.json") if (out / "processing/frame-sources.json").is_file() else {}
    write(backup / "previous-frame-source-record.json", records.get(key))
    write(backup / "backup.json", {"candidate": str(out), "target_slot": key,
          "replacement_of_existing_png": (out / key).is_file(), "files": copied,
          "old_source_batches_retained_in_place": True})
    return str(backup)


def previews(out, direction, frame, review_root):
    image = Image.open(out / f"walk/{direction}/{frame:02d}.png").convert("RGBA")
    review_root.mkdir(parents=True, exist_ok=True)
    outputs = []
    for name, color in (("dark", (30, 38, 46)), ("light", (240, 238, 228))):
        canvas = Image.new("RGB", (1024, 1088), color)
        canvas.paste(image, (0, 48), image)
        draw = ImageDraw.Draw(canvas)
        draw.text((20, 16), f"06 / {direction}{frame:02d} / 1024 native export / visual pending", fill=(255,255,255) if name == "dark" else (20,30,30))
        path = review_root / f"{direction}{frame:02d}-{name}.png"
        canvas.save(path)
        outputs.append({"path": str(path), "sha256": sha(path), "composition_only": True})
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--direction", choices=("N", "NE", "E", "SE", "S", "SW", "W", "NW"), required=True)
    parser.add_argument("--frame", type=int, choices=range(1,17), required=True)
    parser.add_argument("--staging-root", type=Path, default=HERE.parent / "06-work")
    parser.add_argument("--chroma-profile", choices=("standard", "purple-preserve", "native-alpha"), default="native-alpha")
    args = parser.parse_args()
    args.canonical = False
    require(re.fullmatch(r"[A-Za-z0-9_-]+", args.batch_id), "Invalid batch ID")
    archive = args.archive.resolve()
    binding = migration_binding(archive)
    stage_root = args.staging_root.resolve()
    require((stage_root.is_relative_to(HERE.resolve()) or stage_root == (HERE.parent / "06-work").resolve()), "Staging must remain inside current recovery directory")
    destination_root = ROOT if args.canonical else stage_root
    out = destination_root / "candidate" / CHARACTER
    require(not (out / "source" / args.batch_id).exists() and not (out / "processing/batches" / args.batch_id).exists(),
            "Use a fresh batch ID to preserve all historical source and processing evidence")
    key = f"walk/{args.direction}/{args.frame:02d}.png"
    backup = preserve_before_import(out, key, args.batch_id)
    pipe = module("thunder_local_pipeline", HERE / "alpha_pipeline.py")
    pipe.output = lambda character: out if character == CHARACTER else (_ for _ in ()).throw(ValueError("06 only"))
    pipe.preview = lambda: None
    pipe.import_sheet(SimpleNamespace(command="import-walk", character=CHARACTER, direction=args.direction,
         source=archive/"raw.png", prompt=archive/"prompt.txt", receipt=archive/"generation-receipt.json",
         batch_id=args.batch_id, common_scale=.88, chroma_profile=args.chroma_profile, rows=1, cols=1,
         source_cell_indices=None, idle_order=None, output_frames=str(args.frame), start_frame=1))
    verifier = module("thunder_local_verify", HERE / "alpha_verify.py")
    verifier.ROOT = destination_root
    verifier.mod = lambda name: module("thunder_local_independent_" + name, ROOT / "tools/vendor" / f"{name}.py")
    verified = verifier.verify(CHARACTER, args.direction, False, args.frame)
    write(out / "review" / f"validation-{args.direction}-{args.frame:02d}.json", verified)
    write(out / (key + ".generation.json"), {
        "file": key, "sha256": sha(out / key), "derivedFrom": {
            "path": str(archive / "raw.png"), "sha256": sha(archive / "raw.png"),
            "generationRecord": str(archive / "raw.png.generation.json") if (archive / "raw.png.generation.json").exists() else None,
            "receipt": str(archive / "generation-receipt.json")},
        "operation": "whole-cell-downsample-0.88-and-integer-anchor-alignment",
        "profile": args.chroma_profile,
        "native_alpha_and_rgb_not_keyed_or_despilled": args.chroma_profile == "native-alpha",
        "alpha_resampled_only_by_whole_cell_LANCZOS": args.chroma_profile == "native-alpha",
        "actualModel": None, "actualQuality": None,
        "unverifiedReason": "宿主管理，实际型号与质量见原图证据；后处理未调用生成模型。",
        "source_record": "processing/frame-sources.json",
        "visual_review": "pending"})
    evidence = out / "recovery-bindings" / args.batch_id
    write(evidence / "migration-binding.json", binding)
    if (archive / "provenance.json").is_file():
        shutil.copy2(archive / "provenance.json", evidence / "historical-provenance.json")
    views = previews(out, args.direction, args.frame, out / "review/backgrounds")
    result = {"character": CHARACTER, "slot": key, "destination": str(out),
              "canonical_candidate_written": bool(args.canonical), "source_batch": args.batch_id,
              "prior_state_backup": backup, "output_sha256": sha(out / key),
              "single_frame_reconstruction": verified, "migration_binding": str(evidence / "migration-binding.json"),
              "previews": views, "visual_review": "pending", "can_publish": False}
    write(evidence / "import-result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
