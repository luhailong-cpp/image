"""Archive real image_gen outputs for character 15; never create or fake poses.

The default action archives one native full-frame source. --select authorizes an
otherwise eligible source for delivery. --scan reads the archive and delivery
without changing them. Structural eligibility is not an art review.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
import numpy as np

# Loading shared vendor modules must not create shared __pycache__ files.
sys.dont_write_bytecode = True


CHARACTER = "15_water_dragon_scholar_boy"
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
RECOVERY = Path(__file__).resolve().parent.parent
WORKSPACE = RECOVERY.parent.parent
GENERATION = RECOVERY / "15-generation"
DELIVERY = RECOVERY / "15-delivery-preview" / "runtime"
CONFIG = WORKSPACE / "config" / "image-generation.json"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def under(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path must remain within {root}: {path}")
    return path


def write_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def copy_once(source, target):
    source, target = Path(source).resolve(), Path(target).resolve()
    if source == target:
        return
    if target.exists():
        if digest(source) != digest(target):
            raise ValueError(f"Refusing to overwrite different archived bytes: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also protects against concurrent processes using a slot.
    with source.open("rb") as src, target.open("xb") as dst:
        shutil.copyfileobj(src, dst)


def inspect_image(path):
    with Image.open(path) as image:
        image.load()
        alpha = image.getchannel("A") if "A" in image.getbands() else None
        extrema = alpha.getextrema() if alpha else None
        transparent = bool(extrema and extrema[0] == 0 and extrema[1] > 0)
        edge_clear = bool(alpha and all(
            edge.getextrema()[1] == 0 for edge in (
                alpha.crop((0, 0, image.width, 1)),
                alpha.crop((0, image.height - 1, image.width, image.height)),
                alpha.crop((0, 0, 1, image.height)),
                alpha.crop((image.width - 1, 0, image.width, image.height)),
            )
        ))
        problems = []
        if image.format != "PNG":
            problems.append("source_is_not_png")
        if min(image.size) < 1024:
            problems.append("native_frame_below_1024")
        if not transparent:
            problems.append("no_real_transparent_background_alpha")
        if not edge_clear:
            problems.append("nontransparent_canvas_edge")
        if image.width != image.height:
            problems.append("nonsquare_canvas_needs_processing")
        return {
            "path": str(Path(path).resolve()), "sha256": digest(path),
            "width": image.width, "height": image.height,
            "format": image.format, "mode": image.mode,
            "alphaRange": list(extrema) if extrema else None,
            "alphaBounds": list(alpha.getbbox()) if alpha and alpha.getbbox() else None,
            "hasRealTransparency": transparent, "canvasEdgesTransparent": edge_clear,
            "structuralProblems": problems,
            "structurallyEligible": not problems,
            "requiresDownscale": image.size != (1024, 1024),
            "artReview": "pending_manual_review",
            "singleFullFrame": "caller_asserted_by_slot_mapping_not_machine_verified",
        }


def tool_arguments(request):
    for key in ("arguments", "tool_arguments", "toolArguments", "parameters", "request"):
        value = request.get(key)
        if isinstance(value, dict) and ("prompt" in value or "referenced_image_paths" in value):
            return value
    return request


def resolve_input_path(value, request_path):
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    candidates = [request_path.parent / path, WORKSPACE / path]
    return next((p.resolve() for p in candidates if p.is_file()), candidates[0].resolve())


def prompt_bytes(request, request_path):
    args = tool_arguments(request)
    exact = args.get("prompt")
    explicit = request.get("prompt_path") or request.get("promptPath")
    if isinstance(exact, dict):
        explicit = exact.get("path") or explicit
        exact = exact.get("text")
    # The actually submitted request wins over a convenience prompt file.
    if isinstance(exact, str) and exact:
        return exact.encode("utf-8")
    if explicit:
        path = resolve_input_path(explicit, request_path)
        payload = path.read_bytes()
        return payload
    sibling = request_path.parent / "prompt.txt"
    if sibling.is_file():
        return sibling.read_bytes()
    raise ValueError("Request must contain exact prompt text or an existing prompt_path")


def references(request, request_path):
    args = tool_arguments(request)
    values = args.get("referenced_image_paths") or request.get("references") or []
    result = []
    for item in values:
        value = item.get("path") if isinstance(item, dict) else item
        if not value:
            continue
        path = resolve_input_path(value, request_path)
        result.append({
            "path": str(path), "exists": path.is_file(),
            "sha256": digest(path) if path.is_file() else None,
            "purpose": item.get("purpose", "unspecified_in_request")
            if isinstance(item, dict) else "unspecified_in_request",
        })
    return result


def slot_name(kind, direction, frame):
    if kind == "walk":
        if frame is None or not 1 <= frame <= 16:
            raise ValueError("Walk requires --frame in 1..16")
        return f"walk/{direction}/{frame:02d}.png"
    if frame is not None:
        raise ValueError("Independent idle must omit --frame")
    return f"idle/{direction}.png"


def save_image_once(image, path):
    payload = io.BytesIO()
    image.save(payload, format="PNG")
    data = payload.getvalue()
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Refusing to replace different processing pixels: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(data)


def process_native(raw, folder):
    """Use the existing pipeline's deterministic cleanup and whole-cell geometry."""
    vendor = RECOVERY.parent / "tools" / "vendor"
    modules = {}
    for name in ("generate2dsprite", "edge_despill"):
        spec = importlib.util.spec_from_file_location(name, vendor / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[name] = module
    with Image.open(raw) as source:
        cell = source.convert("RGBA")
    data = np.array(cell)
    low_alpha = (data[:, :, 3] > 0) & (data[:, :, 3] <= 8)
    removed_low_alpha = int(low_alpha.sum())
    if data[:, :, 3].min() < 255:
        data[:, :, 3][data[:, :, 3] <= 8] = 0
    prepared = Image.fromarray(data)
    keyed = modules["generate2dsprite"].remove_bg_magenta(prepared, 100, 150)
    alpha = np.asarray(keyed)[:, :, 3]
    if any(np.any(edge) for edge in (alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1])):
        raise ValueError("Original full-frame source touches canvas after cleanup; regenerate")
    scale = 1024 / max(cell.size) * .88
    if scale > 1:
        raise ValueError("No whole-cell upscaling permitted")
    size = (round(cell.width * scale), round(cell.height * scale))
    normalized = keyed.resize(size, Image.Resampling.LANCZOS)
    cleaned, despill = modules["edge_despill"].despill(normalized, radius=4, reference_radius=12)
    y, x = np.where(np.asarray(cleaned)[:, :, 3] > 8)
    if not len(x):
        raise ValueError("Cleanup produced an empty image")
    top, height = int(y.min()), int(y.max()) - int(y.min())
    anchor_x, anchor_y = float(np.median(x[y < top + max(1, int(height * .42))])), int(y.max())
    delta = [round(512 - anchor_x), 942 - anchor_y]
    bbox = cleaned.getchannel("A").getbbox()
    moved = [bbox[0] + delta[0], bbox[1] + delta[1], bbox[2] + delta[0], bbox[3] + delta[1]]
    if min(moved[:2]) < 1 or max(moved[2:]) > 1023:
        raise ValueError(f"Fixed .88 scale and anchor would clip: {moved}; regenerate")
    final = Image.new("RGBA", (1024, 1024))
    final.paste(cleaned, tuple(delta))
    output_dir = folder / "processing-fixed088-v1"
    stages = {}
    for name, image in (("keyed", keyed), ("normalized", normalized), ("cleaned", cleaned), ("final", final)):
        path = output_dir / f"{name}.png"
        save_image_once(image, path)
        stages[name] = {"path": str(path), "sha256": digest(path), "size": list(image.size)}
    final_array = np.asarray(final)
    fy, fx = np.where(final_array[:, :, 3] > 8)
    ftop, fheight = int(fy.min()), int(fy.max()) - int(fy.min())
    after = [float(np.median(fx[fy < ftop + max(1, int(fheight * .42))])), int(fy.max())]
    rgb = final_array[:, :, :3].astype(np.int16)
    stats = {
        "rawLowAlphaPixelsRemoved": removed_low_alpha,
        "keyerVisiblePixelsRemoved": int(np.count_nonzero(data[:, :, 3] > 0) - np.count_nonzero(alpha > 0)),
        "despill": despill,
        "finalStrongMagentaPixels": int(np.count_nonzero((rgb[:, :, 0] > 200) & (rgb[:, :, 1] < 100) & (rgb[:, :, 2] > 200) & (final_array[:, :, 3] > 0))),
        "finalBorderVisiblePixels": int(np.count_nonzero(final_array[0, :, 3]) + np.count_nonzero(final_array[-1, :, 3]) + np.count_nonzero(final_array[:, 0, 3]) + np.count_nonzero(final_array[:, -1, 3])),
    }
    previews = {}
    for name, color in (("light", (245, 241, 231, 255)), ("dark", (27, 35, 49, 255))):
        composited = Image.new("RGBA", final.size, color)
        composited.alpha_composite(final)
        path = output_dir / f"check-{name}.png"
        save_image_once(composited.convert("RGB"), path)
        previews[name] = str(path)
    operation = {
        "name": "existing_pipeline_deterministic_cleanup_uniform_scale_anchor",
        "chromaThresholds": [100, 150], "alphaCleanupThreshold": 8,
        "commonScale": .88, "wholeCellScale": scale, "normalizedSize": list(size),
        "rootPx": [512, 942], "anchorAfterPx": after, "translationPx": delta,
        "anchorAlgorithm": "upper_body_alpha_gt8_median_42_percent_x_lowest_alpha_gt8_y",
        "upscaled": False, "perSubjectFit": False, "poseModification": False,
        "stages": stages, "edgeStatistics": stats, "backgroundChecks": previews,
        "vendorSources": {name: {"path": str(vendor / f"{name}.py"), "sha256": digest(vendor / f"{name}.py")} for name in modules},
    }
    report = output_dir / "processing.json"
    if report.exists():
        if load_json(report) != operation:
            raise ValueError("Existing processing report differs; refusing overwrite")
    else:
        write_new(report, operation)
    return output_dir / "final.png", operation


def archive(args):
    for flag in ("generation_dir", "source", "request_json", "receipt_json", "direction", "kind"):
        if getattr(args, flag) is None:
            raise ValueError(f"Archive requires --{flag.replace('_', '-')}")
    folder = under(args.generation_dir, GENERATION)
    if folder == GENERATION.resolve():
        raise ValueError("--generation-dir must be a per-output directory under 15-generation")
    source, request_path, receipt_path = [Path(p).resolve() for p in
                                        (args.source, args.request_json, args.receipt_json)]
    for path in (source, request_path, receipt_path):
        if not path.is_file():
            raise ValueError(f"Missing actual source/request/receipt: {path}")
    request, receipt = load_json(request_path), load_json(receipt_path)
    if not isinstance(request, dict) or not isinstance(receipt, dict):
        raise ValueError("Request and receipt must be JSON objects")
    slot = slot_name(args.kind, args.direction, args.frame)
    inspection = inspect_image(source)
    # Below-minimum sources are rejected before any archive or delivery write.
    if min(inspection["width"], inspection["height"]) < 1024:
        raise ValueError("Native full-frame dimensions must both be at least 1024; no upscaling")
    if inspection["format"] != "PNG":
        raise ValueError("Archive expects the actual PNG returned by image_gen")
    exact_prompt = prompt_bytes(request, request_path)
    reference_rows = references(request, request_path)
    raw, prompt = folder / "raw.png", folder / "submitted-prompt.txt"
    request_copy, receipt_copy = folder / "request.json", folder / "receipt.json"
    generation_record = folder / "raw.png.generation.json"
    existing = load_json(generation_record) if generation_record.exists() else None
    identity = {"slot": slot, "sourceSha256": inspection["sha256"],
                "requestSha256": digest(request_path), "receiptSha256": digest(receipt_path),
                "promptSha256": hashlib.sha256(exact_prompt).hexdigest()}
    if existing and existing.get("archiveIdentity") != identity:
        raise ValueError("This archive already belongs to a different source, slot or evidence")
    if prompt.exists() and prompt.read_bytes() != exact_prompt:
        raise ValueError("Refusing to overwrite differing submitted-prompt.txt")
    copy_once(source, raw)
    copy_once(request_path, request_copy)
    copy_once(receipt_path, receipt_copy)
    if not prompt.exists():
        with prompt.open("xb") as handle:
            handle.write(exact_prompt)
    if existing is None:
        snapshot = request.get("configSnapshot") or request.get("config_snapshot")
        snapshot_origin = "request_configSnapshot"
        if not isinstance(snapshot, dict):
            snapshot = load_json(CONFIG)
            snapshot_origin = "archive_time_config_not_proof_of_generation_time_settings"
        generated_at = (receipt.get("generatedAt") or receipt.get("generated_at")
                        or receipt.get("completed_at_utc") or receipt.get("completedAtUtc") or receipt.get("completedAt"))
        existing = {
            "schemaVersion": 1, "character": CHARACTER, "file": "raw.png",
            "archiveIdentity": identity, "archivedAt": utc_now(),
            "generatedAt": generated_at, "generationTimeStatus": "reported" if generated_at else "unverified",
            "originalSourcePath": str(source), "sha256": inspection["sha256"],
            "nativeImage": {key: inspection[key] for key in ("width", "height", "format", "mode")},
            "tool": "image_gen", "route": "builtin", "configSnapshot": snapshot,
            "configSnapshotEvidence": snapshot_origin,
            "submittedParameters": {"model": None, "quality": None},
            "actualModel": None, "actualQuality": None,
            "unverifiedReason": "host-managed; tool does not expose model/quality selectors or disclose actual model/quality",
            "prompt": {"path": "submitted-prompt.txt", "sha256": identity["promptSha256"]},
            "references": reference_rows,
            "evidence": {
                "request": {"path": "request.json", "sha256": identity["requestSha256"]},
                "receipt": {"path": "receipt.json", "sha256": identity["receiptSha256"]},
                "toolOutputHint": receipt.get("output_hint") or receipt.get("outputHint"),
            },
            "structuralInspection": inspection,
            "status": "structurally_eligible_pending_selection_and_art_review"
            if inspection["structurallyEligible"] else "needs-processing",
            "artReview": "pending_manual_review", "clientValidation": "not_performed",
        }
        write_new(generation_record, existing)
    result = {"archive": str(folder), "slot": slot, "status": existing["status"],
              "structuralInspection": inspection, "selected": False}
    processed, processing = (process_native(raw, folder) if args.process else (None, None))
    selected_inspection = inspect_image(processed) if processed else inspection
    if processed:
        result.update(processed=str(processed), processing=processing, processedInspection=selected_inspection)
    if args.select:
        if not selected_inspection["structurallyEligible"]:
            raise ValueError("Archived needs-processing source; delivery refused: " +
                             ", ".join(selected_inspection["structuralProblems"]))
        if selected_inspection["requiresDownscale"] and not args.allow_downscale:
            raise ValueError("Archived native square source; selecting it requires --allow-downscale")
        target = under(DELIVERY / slot, DELIVERY)
        sidecar = target.with_name(target.name + ".generation.json")
        if target.exists() or sidecar.exists():
            raise ValueError(f"Delivery slot already exists; refusing to overwrite: {target}")
        # Do not select the same native source into two distinct animation slots.
        for prior in DELIVERY.rglob("*.png.generation.json") if DELIVERY.exists() else ():
            if load_json(prior).get("derivedFrom", {}).get("sha256") == inspection["sha256"]:
                raise ValueError(f"Same source is already assigned to a delivery slot: {prior}")
        if processed:
            payload = processed.read_bytes()
            operation = processing
        elif inspection["requiresDownscale"]:
            with Image.open(raw) as image:
                output = io.BytesIO()
                image.resize((1024, 1024), Image.Resampling.LANCZOS).save(output, format="PNG")
                payload = output.getvalue()
            operation = {"name": "uniform_downscale", "resampler": "Pillow LANCZOS",
                         "scale": 1024 / inspection["width"], "outputSize": [1024, 1024],
                         "upscaled": False, "perSubjectFit": False, "poseModification": False}
        else:
            payload = raw.read_bytes()
            operation = {"name": "byte_identical_copy", "outputSize": [1024, 1024],
                         "upscaled": False, "poseModification": False}
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(payload)
        write_new(sidecar, {
            "schemaVersion": 1, "character": CHARACTER, "slot": slot,
            "file": target.name, "sha256": digest(target), "selectedAt": utc_now(),
            "selectionAuthorization": "explicit_cli_--select", "selectionNote": args.selection_note,
            "derivedFrom": {"path": str(raw), "sha256": inspection["sha256"],
                            "generationRecord": str(generation_record)},
            "operation": operation, "actualModel": None, "actualQuality": None,
            "artReview": "pending_manual_review", "clientValidation": "not_performed",
        })
        result.update(selected=True, delivery=str(target), deliverySha256=digest(target), operation=operation)
    return result


def scan():
    expected = [f"walk/{d}/{n:02d}.png" for d in DIRECTIONS for n in range(1, 17)]
    expected += [f"idle/{d}.png" for d in DIRECTIONS]
    rows, archive_rows, groups, source_groups = [], [], {}, {}
    for slot in expected:
        path = DELIVERY / slot
        if not path.is_file():
            continue
        info = inspect_image(path)
        record_path = path.with_name(path.name + ".generation.json")
        record = load_json(record_path) if record_path.is_file() else {}
        origin = record.get("derivedFrom", {})
        source_path = Path(origin["path"]) if origin.get("path") else None
        info.update(slot=slot, generationRecord=str(record_path) if record_path.exists() else None,
                    sourceSha256=origin.get("sha256"),
                    sourceHashVerified=bool(source_path and source_path.is_file() and digest(source_path) == origin.get("sha256")),
                    outputHashVerified=info["sha256"] == record.get("sha256"))
        rows.append(info)
        groups.setdefault(info["sha256"], []).append(slot)
        if origin.get("sha256"):
            source_groups.setdefault(origin["sha256"], []).append(slot)
    for record_path in sorted(GENERATION.rglob("raw.png.generation.json")) if GENERATION.exists() else ():
        record = load_json(record_path)
        raw = record_path.parent / record["file"]
        archive_rows.append({"record": str(record_path), "slot": record.get("archiveIdentity", {}).get("slot"),
                             "nativeImage": record.get("nativeImage"), "sha256": record.get("sha256"),
                             "rawExists": raw.is_file(), "rawHashVerified": raw.is_file() and digest(raw) == record.get("sha256"),
                             "status": record.get("status"), "artReview": record.get("artReview")})
    present = {row["slot"] for row in rows}
    return {"schemaVersion": 1, "character": CHARACTER, "scannedAt": utc_now(),
            "deliveryRoot": str(DELIVERY), "walkCount": sum(s.startswith("walk/") for s in present),
            "idleCount": sum(s.startswith("idle/") for s in present),
            "missingSlots": [s for s in expected if s not in present],
            "archiveCount": len(archive_rows), "archives": archive_rows, "deliveryFiles": rows,
            "duplicateOutputHashes": {h: v for h, v in groups.items() if len(v) > 1},
            "duplicateSourceHashes": {h: v for h, v in source_groups.items() if len(v) > 1},
            "artReview": "inventory_only_not_art_approval", "clientValidation": "not_performed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-dir", type=Path, help="Per-output directory under 15-generation")
    parser.add_argument("--source", type=Path, help="Actual full-frame PNG returned by image_gen")
    parser.add_argument("--request-json", type=Path)
    parser.add_argument("--receipt-json", type=Path)
    parser.add_argument("--direction", choices=DIRECTIONS)
    parser.add_argument("--kind", choices=("walk", "idle"))
    parser.add_argument("--frame", type=int)
    parser.add_argument("--select", action="store_true", help="Explicitly select structurally eligible source")
    parser.add_argument("--allow-downscale", action="store_true", help="Allow square native source to shrink to 1024")
    parser.add_argument("--process", action="store_true", help="Authorized deterministic cleanup, common scale .88, root (512,942); no pose generation")
    parser.add_argument("--selection-note", default="Manual selection; art acceptance remains separately recorded")
    parser.add_argument("--scan", action="store_true", help="Read-only inventory JSON to stdout")
    args = parser.parse_args()
    if args.scan and (args.select or args.source or args.generation_dir or args.process):
        parser.error("--scan cannot be combined with archive/select inputs")
    try:
        result = scan() if args.scan else archive(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
