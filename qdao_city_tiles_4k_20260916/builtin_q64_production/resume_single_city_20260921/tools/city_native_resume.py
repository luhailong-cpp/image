"""Preserve native outputs and adapt the historical Q64 assembler without editing it.

All writes stay beneath this script's sessions directory. Historical E:/work/image
paths are resolved to the current repository in memory; source JSON is never changed.
No image generation, creative editing, acceptance promotion, or shared-ledger writes.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageFile

HERE = Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / "config/image-generation.json").is_file())
ImageFile.LOAD_TRUNCATED_IMAGES = False


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def resolve_history(value, base):
    text = str(value).replace("\\", "/")
    prefix = "e:/work/image"
    if text.lower() == prefix or text.lower().startswith(prefix + "/"):
        return (REPO / text[len(prefix):].lstrip("/")).resolve()
    path = Path(text)
    return path.resolve() if path.is_absolute() else (Path(base) / path).resolve()


def local_tile(value):
    tile = resolve_history(value, REPO)
    require(tile.is_relative_to(REPO), "Tile must be in this repository")
    require((tile / "plan.json").is_file(), "Tile plan is missing")
    return tile


def session_for(tile):
    return HERE / "sessions" / tile.parent.name / tile.name


def inspect_image(path, expected=None):
    with Image.open(path) as im:
        require(im.format == "PNG", f"Expected PNG: {path}")
        require(getattr(im, "n_frames", 1) == 1, "Animated native output is not supported")
        im.verify()
    with Image.open(path) as im:
        im.load()
        pixels = list(im.size)
        require(im.mode in ("RGB", "RGBA"), f"Unsupported PNG mode: {im.mode}")
        require(im.mode != "RGBA" or im.getextrema()[3] == (255, 255), "Ground output must be opaque")
        require(expected is None or pixels == list(expected), f"Native dimensions {pixels}, expected {expected}")
        return pixels


def png_metadata_observations(path):
    """Read PNG metadata bytes only; this is not C2PA signature verification."""
    blob = Path(path).read_bytes()
    observations = []
    offset = 8
    while offset + 12 <= len(blob):
        size = int.from_bytes(blob[offset:offset + 4], "big")
        kind = blob[offset + 4:offset + 8]
        end = offset + 12 + size
        require(end <= len(blob), "Truncated PNG chunk while observing metadata")
        if kind in (b"caBX", b"tEXt", b"iTXt", b"zTXt"):
            data = blob[offset + 8:offset + 8 + size]
            for match in re.finditer(rb"[\x20-\x7e]{6,}", data):
                value = match.group().decode("ascii")
                if any(term in value.lower() for term in ("openai", "gpt image", "gpt-image", "softwareagent", "software_agent", "claim_generator", "c2pa")):
                    observations.append({"chunk": kind.decode("ascii"), "byteOffset": offset + 8 + match.start(),
                                         "readableString": value[:512]})
        offset = end
        if kind == b"IEND":
            break
    return {"method": "readable ASCII strings from PNG metadata chunks",
            "observations": observations, "c2paSignatureVerified": False,
            "backendModelVerified": False,
            "meaning": "Unverified embedded software-agent/claim strings only; not proof of actual backend model or quality."}


def patches(tile):
    plan = read(tile / "plan.json")
    require(plan.get("nativeGrid") == {"rows": 4, "columns": 4}, "Only the established 4x4 native grid is supported")
    require(plan.get("core") == 1024 and plan.get("halo") == 115, "Unexpected native geometry")
    require(len(plan["patches"]) == 16, "Expected sixteen patch entries")
    return plan


def register(args):
    tile = local_tile(args.tile_dir)
    plan = patches(tile)
    require(re.fullmatch(r"r0[1-4]_c0[1-4](?:\.[A-Za-z0-9_-]+)?", args.id), "Invalid native patch id/version")
    identity = args.id.split(".")[0]
    patch = next(p for p in plan["patches"] if p["id"] == identity)
    session = session_for(tile)
    output = session / "native" / f"{args.id}.png"
    record_path = output.with_suffix(".record.json")
    prompt_output = session / "prompts" / f"{args.id}.prompt.txt"
    receipt_output = session / "receipts" / f"{args.id}.json"
    require(not any(p.exists() for p in (output, record_path, prompt_output, receipt_output)), "Refusing to replace an existing native version")
    source = Path(args.source).resolve()
    prompt = Path(args.prompt_file).resolve()
    receipt_file = Path(args.receipt_file).resolve()
    receipt = read(receipt_file)
    require(isinstance(receipt, dict) and receipt, "A nonempty actual tool receipt is required")
    dimensions = inspect_image(source)
    require(prompt.read_text(encoding="utf-8-sig").strip(), "Actual submitted prompt is empty")
    refs = [resolve_history(p, tile) for p in args.reference]
    require(refs, "At least one actual submitted reference is required")
    if "request" in receipt:
        require(receipt["request"]["prompt"] == prompt.read_text(encoding="utf-8-sig"), "Receipt prompt differs from prompt file")
        require([resolve_history(p, tile) for p in receipt["request"]["referenced_image_paths"]] == refs,
                "Receipt references differ from supplied references")
    guide = resolve_history(patch["guide"], tile)
    require(refs[0] == guide, "First reference must be this patch's exact guide")
    require(sha(guide) == patch["guideSha256"], "Original guide SHA mismatch")
    reference_records = []
    for ref in refs:
        with Image.open(ref) as im:
            im.load()
            size = list(im.size)
        reference_records.append({"path": str(ref), "sha256": sha(ref), "pixels": size})
    for src, dest in ((source, output), (prompt, prompt_output), (receipt_file, receipt_output)):
        dest.parent.mkdir(parents=True, exist_ok=True)
        with src.open("rb") as incoming, dest.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        require(sha(src) == sha(dest), f"Byte preservation failed: {dest}")
    config = read(REPO / "config/image-generation.json")
    record = {
        "schemaVersion": 3, "id": identity, "versionStem": args.id,
        "role": "native_detail_candidate_not_accepted", "route": "builtin_image_gen",
        "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "requestedModel": config["model"], "requestedQuality": config["quality"],
        "actualModel": None, "actualQuality": None, "backendModelVerified": False,
        "modelEvidenceNote": "Host tool has no explicit model or quality selector; raw receipt retained. Configured target is not actual model evidence.",
        "actualNativePixels": dimensions, "sourceOutputPath": str(source),
        "sourceOutputSha256": sha(source), "outputFile": str(output), "outputSha256": sha(output),
        "sourceBytesPreserved": True, "promptFile": str(prompt_output), "promptSha256": sha(prompt_output),
        "promptText": prompt_output.read_text(encoding="utf-8-sig"),
        "promptTransport": args.prompt_transport,
        "guidePath": str(guide), "guideSha256": sha(guide), "submittedImages": reference_records,
        "selectedTargetImageOneBased": 1, "finalArtUpscaled": False, "resizedAfterGeneration": False,
        "toolCall": {"name": "image_gen.imagegen", "referenced_image_paths": [str(p) for p in refs],
                     "modelSelectorAvailable": False, "qualitySelectorAvailable": False},
        "toolOutputReceipt": {"file": str(receipt_output), "sha256": sha(receipt_output)},
        "pngMetadataObservations": png_metadata_observations(output),
        "originalPlan": {"file": str(tile / "plan.json"), "sha256": sha(tile / "plan.json")},
        "visualQa": {"status": "pending", "passed": False},
    }
    write_new(record_path, record)
    return {"record": str(record_path), "native": str(output), "nativePixels": dimensions,
            "sha256": record["outputSha256"], "assemblyEligibleDimensions": dimensions == [1254, 1254],
            "accepted": False}


def import_request(args):
    receipt_path = Path(args.request_file).resolve()
    receipt = read(receipt_path)
    hint = receipt["response"]["output_hint"]
    match = re.search(r" as (.+?\.png) by default\.", hint, re.DOTALL)
    require(match is not None, "Cannot identify the output PNG path in the actual output_hint")
    prompt_path = HERE / "request-prompts" / f"{local_tile(args.tile_dir).name}_{args.id}.prompt.txt"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_text = receipt["request"]["prompt"]
    if prompt_path.exists():
        require(prompt_path.read_text(encoding="utf-8") == prompt_text, "Existing actual-prompt snapshot differs")
    else:
        with prompt_path.open("x", encoding="utf-8", newline="") as stream:
            stream.write(prompt_text)
    return register(argparse.Namespace(tile_dir=args.tile_dir, id=args.id, source=match.group(1),
                                       prompt_file=str(prompt_path), receipt_file=str(receipt_path),
                                       reference=receipt["request"]["referenced_image_paths"],
                                       prompt_transport="Exact request.prompt from retained image_gen call JSON"))


def chosen_sources(tile):
    plan = patches(tile)
    session = session_for(tile)
    chosen = []
    for patch in plan["patches"]:
        identity = patch["id"]
        overrides = sorted((session / "native").glob(f"{identity}*.record.json"))
        require(len(overrides) <= 1, f"Multiple resumed versions for {identity}; explicit selection is required")
        if overrides:
            record_path = overrides[0]
            native = record_path.with_name(record_path.name.removesuffix(".record.json") + ".png")
        else:
            stem = patch.get("selectedNativeStem", identity)
            native = tile / "native" / f"{stem}.png"
            record_path = tile / "native" / f"{stem}.record.json"
        chosen.append((patch, native, record_path))
    return plan, chosen


def verify_one(tile, patch, native, record_path):
    record = read(record_path)
    identity = patch["id"]
    require(record.get("id") == identity, f"Record identity mismatch: {record_path}")
    require(record.get("route") in ("builtin", "builtin_image_gen"), "Unsupported generation route")
    require(record.get("backendModelVerified") is False, "Unexpected model evidence claim")
    require(record.get("finalArtUpscaled") is not True and record.get("resizedAfterGeneration") is not True,
            "Resized/enlarged native output cannot enter this assembler")
    dimensions = inspect_image(native, [1254, 1254])
    require(record.get("actualNativePixels") == dimensions, "Recorded native dimensions mismatch")
    native_hash = sha(native)
    require(native_hash == record.get("outputSha256") == record.get("sourceOutputSha256"),
            f"Native/source-record SHA mismatch: {identity}")
    require(resolve_history(record["outputFile"], tile) == native.resolve(), "Recorded output path mismatch")
    prompt = resolve_history(record["promptFile"], tile)
    guide = resolve_history(record["guidePath"], tile)
    require(guide == resolve_history(patch["guide"], tile), "Guide identity mismatch")
    require(sha(prompt) == record["promptSha256"], "Actual prompt SHA mismatch")
    require(prompt.read_text(encoding="utf-8-sig").strip(), "Actual prompt is empty")
    require(sha(guide) == record["guideSha256"] == patch["guideSha256"], "Guide SHA mismatch")
    references = record.get("submittedImages", [])
    call_paths = record.get("toolCall", {}).get("referenced_image_paths", [])
    require(references and [resolve_history(r["path"], tile) for r in references] ==
            [resolve_history(p, tile) for p in call_paths], "Submitted-reference call/record mismatch")
    require(resolve_history(references[0]["path"], tile) == guide, "First submitted reference is not the guide")
    require(record.get("selectedTargetImageOneBased") == 1, "Unexpected edit target")
    for ref in references:
        require(sha(resolve_history(ref["path"], tile)) == ref["sha256"], "Submitted reference SHA mismatch")
    original = resolve_history(record["sourceOutputPath"], tile)
    original_present = original.is_file()
    if original_present:
        require(sha(original) == native_hash, "Original generator output differs from preserved native")
    receipt = record.get("toolOutputReceipt")
    if isinstance(receipt, dict) and "file" in receipt:
        require(sha(resolve_history(receipt["file"], tile)) == receipt["sha256"], "Tool receipt SHA mismatch")
    return {
        "id": identity, "row": int(identity[1:3]), "column": int(identity[5:7]),
        "nativeFile": str(native.resolve()), "nativeSize": dimensions, "nativeSha256": native_hash,
        "recordFile": str(record_path.resolve()), "recordSha256": sha(record_path),
        "promptFile": str(prompt), "promptSha256": sha(prompt), "guideFile": str(guide), "guideSha256": sha(guide),
        "sourceOutputPath": record["sourceOutputPath"], "sourceOutputSha256": native_hash,
        "originalGeneratorOutputAvailable": original_present,
        "provenanceVerification": "live original + preserved native match" if original_present else
                                  "preserved native matches both historical recorded SHA values; original machine output unavailable",
        "route": record["route"], "backendModelVerified": False, "sourceBytesPreserved": True,
        "submittedImages": [{"path": str(resolve_history(r["path"], tile)), "sha256": r["sha256"]} for r in references],
    }


def inventory(tile, strict=False):
    plan, chosen = chosen_sources(tile)
    entries, missing, errors = [], [], []
    for patch, native, record_path in chosen:
        if not native.is_file() or not record_path.is_file():
            missing.append(patch["id"])
            continue
        try:
            entries.append(verify_one(tile, patch, native, record_path))
        except (ValueError, OSError, KeyError) as error:
            errors.append({"id": patch["id"], "error": str(error)})
    result = {"tile": str(tile), "session": str(session_for(tile)), "verifiedNativeCount": len(entries),
              "missing": missing, "errors": errors, "readyToAssemble": len(entries) == 16 and not errors,
              "historicalOriginalOutputsUnavailable": sum(not e["originalGeneratorOutputAvailable"] for e in entries),
              "sources": entries, "accepted": False}
    if strict:
        require(result["readyToAssemble"], json.dumps({"missing": missing, "errors": errors}))
    return plan, result


def adapt(tile):
    original = tile / "assemble_builtin.py"
    require(original.is_file(), "Historical assembler is missing")
    spec = importlib.util.spec_from_file_location("preserved_city_assembler", original)
    module = importlib.util.module_from_spec(spec)
    # Disable bytecode writes beside historical source.
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    session = session_for(tile)
    original_art_name = module.ART.name
    module.ROOT = session
    module.HELPERS = REPO / "tianyong_festival_hd_20260910/seam_helpers.py"
    module.OUTPUT = session / "output_resume_20260921"
    module.QA = session / "qa_resume_20260921"
    module.ART = module.OUTPUT / original_art_name
    module.MANIFEST = module.OUTPUT / "assembly.json"
    module.relative = lambda p: Path(os.path.relpath(Path(p).resolve(), session)).as_posix()

    def load_sources():
        _, checked = inventory(tile, strict=True)
        rows = []
        for offset in range(0, 16, 4):
            row = []
            for entry in checked["sources"][offset:offset + 4]:
                with Image.open(entry["nativeFile"]) as im:
                    row.append(np.asarray(im.convert("RGB")).copy())
            rows.append(row)
        return rows, checked["sources"]
    module.load_sources = load_sources
    return module


def assemble(tile, check=False):
    plan, checked = inventory(tile, strict=True)
    module = adapt(tile)
    session = session_for(tile)
    original_plan_hash = sha(tile / "plan.json")
    original_script_hash = sha(tile / "assemble_builtin.py")
    if check:
        manifest = read(module.MANIFEST)
        result = module.validate_saved(manifest, checked["sources"])
        adapter = read(session / "adapter-record.json")
        require(adapter["adapterSha256"] == sha(__file__), "Resume adapter changed after assembly")
        require(adapter["originalPlanSha256"] == original_plan_hash, "Historical plan changed after assembly")
        require(adapter["originalAssemblerSha256"] == original_script_hash, "Historical assembler changed after assembly")
        require(adapter["assemblySha256"] == sha(module.MANIFEST), "Assembly record changed after adaptation")
        return {**result, "accepted": False, "originalGeneratorOutputsUnavailable": checked["historicalOriginalOutputsUnavailable"]}
    require(not any(p.exists() for p in (session / "plan.json", session / "adapter-record.json", module.MANIFEST)),
            "Preserve the existing resumed assembly; use check instead")
    resumed_plan = copy.deepcopy(plan)
    resumed_plan["resumeSourcePlan"] = {"file": str(tile / "plan.json"), "sha256": original_plan_hash}
    resumed_plan["status"] = "resumed_candidate_native_assembly_pending_visual_review"
    for patch, entry in zip(resumed_plan["patches"], checked["sources"]):
        patch.update(promptFile=entry["promptFile"], guide=entry["guideFile"],
                     nativeFile=entry["nativeFile"], sourceRecord=entry["recordFile"],
                     submittedImages=[r["path"] for r in entry["submittedImages"]])
    write_new(session / "plan.json", resumed_plan)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        result = module.assemble()
    finally:
        sys.dont_write_bytecode = previous
    require(sha(tile / "plan.json") == original_plan_hash and sha(tile / "assemble_builtin.py") == original_script_hash,
            "Historical inputs changed during assembly")
    write_new(session / "adapter-record.json", {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "adapter": str(Path(__file__).resolve()), "adapterSha256": sha(__file__),
        "originalPlan": str(tile / "plan.json"), "originalPlanSha256": original_plan_hash,
        "originalAssembler": str(tile / "assemble_builtin.py"), "originalAssemblerSha256": original_script_hash,
        "assembly": str(module.MANIFEST), "assemblySha256": sha(module.MANIFEST),
        "historicalPathMapping": {"E:/work/image": str(REPO)}, "historicalSourceJsonModified": False,
        "historicalOriginalOutputsUnavailable": checked["historicalOriginalOutputsUnavailable"],
        "visualAcceptancePassed": False, "productionAccepted": False, "runtimePublished": False,
    })
    return {**result, "accepted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("register", "import-request", "inventory", "metadata", "assemble", "check"):
        sub = commands.add_parser(name)
        sub.add_argument("--tile-dir", required=True)
        if name == "import-request":
            sub.add_argument("--id", required=True)
            sub.add_argument("--request-file", required=True)
        if name == "register":
            sub.add_argument("--id", required=True)
            sub.add_argument("--source", required=True)
            sub.add_argument("--prompt-file", required=True)
            sub.add_argument("--reference", action="append", required=True)
            sub.add_argument("--receipt-file", required=True)
            sub.add_argument("--prompt-transport", default="UTF-8 file text submitted verbatim")
    args = parser.parse_args()
    if args.command == "register":
        result = register(args)
    elif args.command == "import-request":
        result = import_request(args)
    elif args.command == "inventory":
        _, result = inventory(local_tile(args.tile_dir))
    elif args.command == "metadata":
        tile = local_tile(args.tile_dir)
        _, chosen = chosen_sources(tile)
        result = {"backendModelVerified": False, "c2paSignaturesVerified": False,
                  "files": [{"id": p["id"], "native": str(n), "sha256": sha(n),
                             "metadata": png_metadata_observations(n)} for p, n, _ in chosen if n.is_file()]}
    else:
        result = assemble(local_tile(args.tile_dir), check=args.command == "check")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({"error": str(error), "accepted": False}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
