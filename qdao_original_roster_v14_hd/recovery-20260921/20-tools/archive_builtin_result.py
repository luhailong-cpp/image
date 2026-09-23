"""Archive one actual built-in result for character 20; never generate or process art."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

from PIL import Image

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
PACKAGE = RECOVERY.parent
IMAGE_ROOT = PACKAGE.parent
GENERATION = RECOVERY / "20-generation"
BUILTIN_GENERATED = (Path.home() / ".codex/generated_images").resolve()
CHARACTER = "20_star_formation_master_girl"
CONFIG_KEYS = ("model", "quality", "builtin_product", "verified_on", "sources")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def timestamp(value, label):
    require(isinstance(value, str) and value, f"Missing {label}")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return value


def request_arguments(request):
    for name in ("actual_request", "submittedArguments", "arguments", "request"):
        candidate = request.get(name)
        if isinstance(candidate, dict) and "prompt" in candidate:
            return candidate
    require("prompt" in request, "request.json must preserve actual tool prompt and references")
    return request


def archive_result(args):
    attempt = args.attempt.resolve()
    require(attempt.is_relative_to(GENERATION.resolve()) and attempt != GENERATION.resolve(),
            "Attempt must be a child of recovery-20260921/20-generation")
    require(attempt.is_dir(), "Prepare a distinct attempt directory before the real tool call")
    request_path, prompt_path = attempt / "request.json", attempt / "prompt.txt"
    require(request_path.is_file() and prompt_path.is_file(), "Need request.json and exact prompt.txt")
    request = read_json(request_path)
    actual = request_arguments(request)
    require(prompt_path.read_bytes() == actual["prompt"].encode("utf-8"),
            "Prompt bytes differ from actual submitted prompt")
    start_value = actual.get("started_at") or request.get("started_at") or request.get("startedAt")
    started_at = timestamp(start_value, "actual request start") if start_value else None
    started_at_basis = actual.get("started_at_basis") or request.get("started_at_basis") or (
        "caller-recorded request preparation time; exact service start undisclosed" if started_at else
        "Not recorded by calling agent; unknown, no timestamp inferred from later file creation")
    config = request.get("configSnapshot") or request.get("config_snapshot")
    require(isinstance(config, dict) and all(key in config for key in CONFIG_KEYS),
            "Need configSnapshot from request preparation; do not backfill from current config")
    submitted = request.get("submittedParameters", {})
    submitted_model = actual.get("model", submitted.get("model"))
    submitted_quality = actual.get("quality", submitted.get("quality"))
    require(submitted_model is None and submitted_quality is None,
            "This built-in entry point exposes no model/quality selector; only real parameters are allowed")
    references = actual.get("referenced_image_paths") or []
    require(references, "Character 20 requires actual local identity/style references")
    current_bindings = []
    roles = request.get("reference_roles", {})
    for value in references:
        path = Path(value).resolve()
        require(path.is_file() and (path.is_relative_to(IMAGE_ROOT.resolve())
                                   or path.is_relative_to(BUILTIN_GENERATED)),
                f"Missing reference or reference outside workspace/local .codex/generated_images: {value}")
        current_bindings.append({"path": str(path), "sha256": sha(path),
                                 "purpose": roles.get(value, "Not recorded in request; inspect exact prompt")})
    at_start = request.get("reference_bindings_at_start", [])
    if at_start:
        expected = {str(Path(row["path"]).resolve()).casefold(): row["sha256"] for row in at_start}
        require(all(expected.get(row["path"].casefold()) == row["sha256"] for row in current_bindings),
                "A reference differs from its request-start SHA")

    tool_path, original = args.tool_result.resolve(), args.original.resolve()
    require(tool_path.is_file() and original.is_file(), "Need genuine tool-result JSON and returned original file")
    tool = read_json(tool_path)
    hint = tool.get("output_hint")
    require(isinstance(hint, str) and hint, "Tool result must contain the genuine output_hint")
    require(str(original).replace("\\", "/").casefold() in hint.replace("\\", "/").casefold(),
            "Original file path must occur in the exact tool output_hint")
    require(original != attempt / "raw.png", "Original must be the tool-returned file, not its archive copy")
    raw = attempt / "raw.png"
    outputs = [raw, attempt / "generation-receipt.json", attempt / "provenance.json",
               attempt / "raw.png.generation.json"]
    require(not any(path.exists() for path in outputs), "Immutable attempt already has a result; use a new attempt")
    destination_tool = attempt / "tool-result.json"
    if destination_tool.exists():
        require(sha(destination_tool) == sha(tool_path), "Existing tool-result.json differs")
    with Image.open(original) as image:
        native_size = list(image.size)
        mode, image_format = image.mode, image.format
        image.verify()
    require(image_format == "PNG", "Current archive contract expects a returned PNG")
    with Image.open(original) as image:
        has_alpha = "A" in image.getbands() or "transparency" in image.info
        alpha = image.convert("RGBA").getchannel("A")
        histogram = alpha.histogram()
        transparency = {"native_alpha_information_present": has_alpha,
                        "alpha_extrema": list(alpha.getextrema()),
                        "fully_transparent_pixels": histogram[0],
                        "partially_transparent_pixels": sum(histogram[1:255]),
                        "fully_opaque_pixels": histogram[255],
                        "has_transparent_pixels": histogram[0] > 0,
                        "edge_and_checkerboard_visual_review": "pending"}
    original_sha = sha(original)
    completed_at = timestamp(args.completed_at or tool.get("completed_at")
                             or datetime.now(timezone.utc).isoformat(), "completion/archive time")
    time_basis = "caller-supplied actual completion time" if args.completed_at else (
        "tool result completed_at" if tool.get("completed_at") else
        "archive time after successful tool return; exact generation timestamp undisclosed")
    spec = importlib.util.spec_from_file_location("character20_provenance", PACKAGE / "tools/inspect_image_provenance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        provenance = module.inspect_image(original)
    except Exception as error:
        provenance = {"path": str(original), "sha256": original_sha, "native_size": native_size,
                      "metadata_only": True, "signature_verified": False,
                      "inspection_error": str(error), "effective_backend_model": "not_exposed_by_builtin_tool"}
    shutil.copy2(original, raw)
    require(sha(raw) == original_sha, "Archived raw byte mismatch")
    if not destination_tool.exists():
        shutil.copy2(tool_path, destination_tool)
    provenance["inspected_original_file"] = str(original)
    provenance["path"] = str(raw)
    write_new(attempt / "provenance.json", provenance)
    actual_model = tool.get("actualModel") or tool.get("actual_model")
    actual_quality = tool.get("actualQuality") or tool.get("actual_quality")
    evidence = [{"path": "tool-result.json", "sha256": sha(destination_tool), "fields": ["output_hint"]},
                {"path": "provenance.json", "sha256": sha(attempt / "provenance.json"),
                 "fields": ["created_actions", "signature_verified"],
                 "note": "C2PA assertions are preserved as metadata, not a verified signature or API model lock"}]
    for key in ("actualModel", "actual_model", "actualQuality", "actual_quality"):
        if tool.get(key) is not None:
            evidence[0]["fields"].append(key)
    receipt = {**request, "schema": "qdao-character20-builtin-receipt-v1", "character_id": CHARACTER,
               "tool": "built-in image_gen", "route": "builtin", "status": "generated_pending_review",
               "actual_request": actual, "started_at": started_at, "completed_at": completed_at,
               "started_at_basis": started_at_basis,
               "completed_at_basis": time_basis, "configSnapshot": config,
               "submittedParameters": {"model": submitted_model, "quality": submitted_quality},
               "model_actual": actual_model or "host-managed-unverified",
               "quality_actual": actual_quality or "host-managed-unverified",
               "actualModel": actual_model, "actualQuality": actual_quality,
               "output_hint": hint, "original_generated_file": str(original),
               "original_sha256": original_sha, "raw_sha256": sha(raw), "native_size": native_size,
               "transparency": transparency,
               "generation_calls": 1, "paid_api_calls": 0, "original_retained": True,
               "reference_bindings_verified_after_return": current_bindings,
               "reference_start_sha_available": bool(at_start), "visual_review": "pending",
               "source_is_single_frame": request.get("source_is_single_frame"),
               "native_canvas_min_1024": min(native_size) >= 1024,
               "art_approval": False, "client_validation_performed": False}
    write_new(attempt / "generation-receipt.json", receipt)
    generation = {"schema": "qdao-per-image-generation-v1", "file": "raw.png", "sha256": sha(raw),
                  "generatedAt": completed_at, "generatedAtBasis": time_basis,
                  "width": native_size[0], "height": native_size[1], "format": image_format, "mode": mode,
                  "transparency": transparency,
                  "tool": "built-in image_gen", "route": "builtin", "configSnapshot": config,
                  "submittedParameters": {"model": submitted_model, "quality": submitted_quality},
                  "parameterAvailability": "model and quality are not exposed by this built-in entry point",
                  "actualModel": actual_model, "actualQuality": actual_quality,
                  "unverifiedReason": {"actualModel": None if actual_model else "Host-managed; tool returned no explicit actual model",
                                       "actualQuality": None if actual_quality else "Host-managed; tool returned no explicit actual quality"},
                  "evidence": evidence + [{"path": "generation-receipt.json", "sha256": sha(attempt / "generation-receipt.json")}],
                  "prompt": {"path": "prompt.txt", "sha256": sha(prompt_path)},
                  "references": current_bindings, "nativeSingleFrameConfirmed": request.get("source_is_single_frame") is True,
                  "visualReview": "pending", "canPublish": False, "paidApiCalls": 0}
    write_new(attempt / "raw.png.generation.json", generation)
    return {"attempt": str(attempt), "raw_sha256": sha(raw), "native_size": native_size,
            "transparency": transparency,
            "native_canvas_min_1024": min(native_size) >= 1024, "actualModel": actual_model,
            "actualQuality": actual_quality, "visual_review": "pending", "paid_api_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", "--archive", dest="attempt", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--tool-result", type=Path, required=True)
    parser.add_argument("--completed-at", help="Actual tool completion timestamp with timezone, if recorded by caller")
    args = parser.parse_args()
    print(json.dumps(archive_result(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
