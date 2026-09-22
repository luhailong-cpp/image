"""07-only source archives, alpha-preserving exports and offline review packages.

This script never generates artwork, invokes a paid API or approves animation.
Every imported raw is immutable. New export choices retain replaced files.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
RECOVERY = HERE.parent
PACKAGE = RECOVERY.parent
PROJECT = PACKAGE.parent
CHAR = "07_moon_shadow_assassin_girl"
DIRS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
OUT = HERE / "candidate" / CHAR
PREVIEWS = RECOVERY / "07-delivery-preview"
CONFIG = PROJECT / "config/image-generation.json"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def require(value, message):
    if not value:
        raise ValueError(message)


def write(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def copy_exact(source, target):
    source, target = Path(source), Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        require(sha(source) == sha(target), "Refusing to overwrite immutable evidence: " + str(target))
    else:
        shutil.copy2(source, target)
    require(sha(source) == sha(target), "Copy SHA mismatch")


def attempt_dir(attempt):
    require(re.fullmatch(r"[A-Za-z0-9_-]+", attempt), "Invalid attempt name")
    return HERE / "archives" / attempt


def slot(kind, direction, frame):
    require(direction in DIRS, "Expected one of eight directions")
    require(kind in ("walk", "idle"), "Expected walk or idle")
    if kind == "walk":
        require(frame is not None and 1 <= frame <= 16, "Walk requires --frame 1..16")
        return f"walk/{direction}/{frame:02d}.png"
    require(frame is None, "Idle is independent and has no --frame")
    return f"idle/{direction}.png"


def request_arguments(request):
    for key in ("arguments", "actual_request", "submittedArguments"):
        if isinstance(request.get(key), dict):
            value = request[key]
            return {k: value[k] for k in ("prompt", "referenced_image_paths", "num_last_images_to_include") if k in value}
    raise ValueError("No exact submitted tool arguments in request")


def bind_references(arguments):
    refs = arguments.get("referenced_image_paths", [])
    require(refs, "Local reference paths must be recorded")
    results = []
    for value in refs:
        path = Path(value).resolve()
        require(path.is_file(), "Missing reference: " + str(path))
        results.append({"path": str(path), "sha256": sha(path)})
    return results


def prepare(args):
    folder = attempt_dir(args.attempt)
    require(not folder.exists(), "Attempt already exists; choose a fresh attempt name")
    key = slot(args.kind, args.direction, args.frame)
    prompt = args.prompt.read_bytes().decode("utf-8-sig")
    arguments = {"prompt": prompt, "referenced_image_paths": [str(p.resolve()) for p in args.refs]}
    references = bind_references(arguments)
    prepared = now()
    request = {"schema": "qdao-07-builtin-request-v1", "character": CHAR, "attempt": args.attempt,
               "slot": key, "kind": args.kind, "direction": args.direction, "frame": args.frame,
               "tool": "image_gen.imagegen", "route": "builtin", "preparedAt": prepared,
               "status": "prepared_not_yet_submitted", "arguments": arguments,
               "configSnapshot": read(CONFIG), "configSnapshotCapturedAt": prepared,
               "submittedParameters": {"model": None, "quality": None},
               "referenceBindingsAtPreparation": references,
               "actualModel": None, "actualQuality": None,
               "unverifiedReason": "Host-managed; model/quality selectors are not exposed. Preparation is not proof of a call."}
    write(folder / "request.json", request, exclusive=True)
    (folder / "prompt.txt").write_bytes(prompt.encode("utf-8"))
    write(folder / "tool-arguments.json", arguments, exclusive=True)
    print(json.dumps({"request": str(folder / "request.json"), "tool_arguments": str(folder / "tool-arguments.json"),
                      "slot": key, "status": request["status"]}, ensure_ascii=False))


def archive(args):
    folder = attempt_dir(args.attempt)
    if args.request:
        require(args.kind and args.direction, "External request requires --kind and --direction (walk also --frame)")
        key = slot(args.kind, args.direction, args.frame)
        request = read(args.request)
        arguments = request_arguments(request)
        require(isinstance(arguments.get("prompt"), str) and arguments["prompt"], "Missing exact prompt")
        copy_exact(args.request, folder / "request-original.json")
        original_prompt = args.request.parent / "prompt.txt"
        if original_prompt.exists():
            copy_exact(original_prompt, folder / "prompt-original.txt")
            request["companionPromptMatchesRequestExactly"] = original_prompt.read_bytes().decode("utf-8-sig") == arguments["prompt"]
        if not (folder / "prompt.txt").exists():
            (folder / "prompt.txt").write_bytes(arguments["prompt"].encode("utf-8"))
        request = {**request, "character": CHAR, "attempt": args.attempt, "slot": key,
                   "kind": args.kind, "direction": args.direction, "frame": args.frame,
                   "arguments": arguments, "ingestedAt": now(),
                   "externalRequestPath": str(args.request.resolve()), "externalRequestSha256": sha(args.request)}
        if "configSnapshot" not in request:
            request["configSnapshot"] = read(CONFIG)
            request["configSnapshotCapturedAt"] = now()
            request["configSnapshotScope"] = "captured_at_archive_ingestion; original request did not contain a config snapshot"
        request["referenceBindingsAtIngestion"] = bind_references(arguments)
        if (folder / "request.json").exists():
            require(read(folder / "request.json").get("arguments") == arguments, "Attempt already contains different request arguments")
        else:
            write(folder / "request.json", request, exclusive=True)
    else:
        request = read(folder / "request.json")
        arguments = request_arguments(request)
        require((folder / "prompt.txt").read_bytes().decode("utf-8-sig") == arguments["prompt"], "Prompt differs from request")
    require(not (folder / "generation-receipt.json").exists(), "Result already archived; use another attempt")
    result_path = args.result or args.error
    require(result_path is not None and result_path.is_file(), "Pass --result or --error with actual tool JSON")
    result = read(result_path)
    evidence_name = "tool-result.json" if args.result else "tool-error.json"
    copy_exact(result_path, folder / evidence_name)
    completed = args.completed_at or now()
    receipt = {"schema": "qdao-07-builtin-receipt-v1", "character": CHAR, "attempt": args.attempt,
               "slot": request["slot"], "tool": request.get("tool", "image_gen.imagegen"), "route": "builtin",
               "requestPath": "request.json", "requestSha256": sha(folder / "request.json"),
               "actual_request": arguments, "preparedAt": request.get("preparedAt"),
               "startedAt": request.get("startedAt") or request.get("actual_request", {}).get("started_at"),
               "archivedAt": now(), "completedAt": args.completed_at,
               "completionTimeScope": "caller_supplied_tool_completion" if args.completed_at else "tool completion not disclosed; archivedAt is only archive time",
               "configSnapshot": request.get("configSnapshot"),
               "submittedParameters": request.get("submittedParameters", {"model": None, "quality": None}),
               "actualModel": None, "actualQuality": None,
               "unverifiedReason": "Host-managed; tool did not disclose a verified actual model or quality.",
               "generation_calls": 1, "paid_api_calls": 0,
               "toolEvidence": {"path": evidence_name, "sha256": sha(folder / evidence_name)},
               "status": "tool_error_no_image" if args.error else "generated_pending_visual_review"}
    # Only explicit fields in the actual result can populate actual version/quality.
    if isinstance(result, dict):
        for target, candidates in (("actualModel", ("actualModel", "actual_model", "model")),
                                   ("actualQuality", ("actualQuality", "actual_quality", "quality"))):
            for name in candidates:
                if isinstance(result.get(name), str) and result[name]:
                    receipt[target] = result[name]
                    receipt.setdefault("actualFieldEvidence", {})[target] = f"{evidence_name}.{name}"
                    break
    if args.error:
        require(args.original is None, "Error archive must not claim an original generated image")
        receipt["successfulGenerationCalls"] = 0
        write(folder / "generation-receipt.json", receipt, exclusive=True)
        print(json.dumps({"archive": str(folder), "status": receipt["status"], "image_created": False}))
        return
    require(args.original is not None and args.original.is_file(), "Successful result requires --original existing default generated PNG")
    original = args.original.resolve()
    text = json.dumps(result, ensure_ascii=False).replace("\\\\", "/").replace("\\", "/").lower()
    require(str(original).replace("\\", "/").lower() in text,
            "Original path must appear in actual tool result JSON; cannot invent a result binding")
    with Image.open(original) as im:
        require(im.format == "PNG", "Raw tool output must be PNG")
        width, height, mode = im.width, im.height, im.mode
    copy_exact(original, folder / "raw.png")
    receipt.update({"successfulGenerationCalls": 1, "original_generated_file": str(original),
                    "originalRetained": True, "rawSha256": sha(folder / "raw.png"),
                    "nativeSize": [width, height], "nativeMode": mode})
    write(folder / "generation-receipt.json", receipt, exclusive=True)
    record = {"file": "raw.png", "sha256": receipt["rawSha256"], "generatedAt": args.completed_at,
              "generatedAtScope": "caller_supplied_completion" if args.completed_at else "not_disclosed; see archive/started timestamps",
              "archivedAt": receipt["archivedAt"], "width": width, "height": height, "format": "PNG", "mode": mode,
              "tool": receipt["tool"], "route": "builtin", "configSnapshot": receipt["configSnapshot"],
              "submittedParameters": receipt["submittedParameters"], "actualModel": receipt["actualModel"],
              "actualQuality": receipt["actualQuality"], "unverifiedReason": receipt["unverifiedReason"],
              "prompt": {"path": "prompt.txt", "sha256": sha(folder / "prompt.txt")},
              "references": request.get("referenceBindingsAtPreparation") or request.get("referenceBindingsAtIngestion"),
              "referenceDerivation": request.get("referenceDerivation"),
              "evidence": [{"path": "generation-receipt.json", "sha256": sha(folder / "generation-receipt.json")}, receipt["toolEvidence"]]}
    write(folder / "raw.png.generation.json", record, exclusive=True)
    print(json.dumps({"archive": str(folder), "raw": str(folder / "raw.png"), "native_size": [width, height],
                      "sha256": receipt["rawSha256"], "actualModel": receipt["actualModel"], "actualQuality": receipt["actualQuality"]}, ensure_ascii=False))


def metrics(im):
    alpha = np.asarray(im.getchannel("A"))
    y, x = np.where(alpha > 8)
    require(len(x), "Empty alpha silhouette")
    top, bottom = int(y.min()), int(y.max())
    height = bottom - top + 1
    axis = float(np.median(x[y < top + max(1, int((height - 1) * .42))]))
    return {"size": list(im.size), "alpha_min": int(alpha.min()), "alpha_max": int(alpha.max()),
            "bbox_alpha_gt8": [int(x.min()), top, int(x.max()) + 1, bottom + 1],
            "subject_height": height, "axis": [axis, bottom],
            "alpha_boundary_touched": bool(any(np.any(edge) for edge in (alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]))),
            "body_scale": float(math.sqrt(np.count_nonzero(alpha[:, im.width // 4:3 * im.width // 4]) / (im.width * im.height)))}


def head_band_width(im):
    """Scale evidence only:95th row span in18..42% of significant subject height."""
    alpha = np.asarray(im.getchannel("A"))
    y, x = np.where(alpha > 8)
    top, height = int(y.min()), int(y.max() - y.min() + 1)
    widths = []
    for row in range(top + int(height * .18), top + int(height * .42)):
        xs = np.where(alpha[row] > 8)[0]
        if len(xs):
            widths.append(int(xs[-1] - xs[0] + 1))
    require(widths, "No measurable head band")
    return float(np.percentile(widths, 95))


def ingest(args):
    """Convenience wrapper for genuine result/request files already saved by generators."""
    folder = RECOVERY / "07-generation" / args.attempt
    require(folder.resolve().parent == (RECOVERY / "07-generation").resolve(), "Invalid attempt directory")
    request, result = read(folder / "request.json"), read(folder / "result.json")
    match = re.match(r"^(idle|walk)-(N|NE|E|SE|S|SW|W|NW)(?:-(\d{2}))?-", args.attempt)
    require(match, "Cannot infer action slot from attempt name")
    kind, direction, number = match.groups()
    frame = int(number) if kind == "walk" else None
    original = result.get("original_generated_file")
    error = result.get("status") not in ("success", "generated", "generated_pending_review") or not original
    if not error:
        original = Path(original)
        copy_exact(original, folder / "raw.png")
    archive_folder = attempt_dir(args.attempt)
    if not (archive_folder / "generation-receipt.json").exists():
        archive(argparse.Namespace(attempt=args.attempt, request=folder / "request.json", kind=kind,
            direction=direction, frame=frame, result=None if error else folder / "result.json",
            error=folder / "result.json" if error else None, original=None if error else original,
            completed_at=result.get("completedAt")))
    if args.select:
        require(not error, "Cannot select a failed generation")
        export(argparse.Namespace(attempt=args.attempt, replace=args.replace, revision=args.revision,
                                  head_reference=args.head_reference))


def export(args):
    folder = attempt_dir(args.attempt)
    request, receipt = read(folder / "request.json"), read(folder / "generation-receipt.json")
    require(receipt["status"] == "generated_pending_visual_review", "Cannot export failed generation")
    raw = folder / "raw.png"
    require(sha(raw) == receipt["rawSha256"], "Raw archive changed")
    with Image.open(raw) as source:
        require(source.mode == "RGBA" and source.format == "PNG", "Export requires native transparent RGBA PNG; regenerate opaque artwork")
        im = source.copy()
    require(min(im.size) >= 1024, "Each native single-person canvas axis must be >=1024; no upscaling")
    raw_metrics = metrics(im)
    require(raw_metrics["alpha_min"] == 0 and raw_metrics["alpha_max"] == 255, "Need transparent background and opaque body")
    pixels = np.array(im)
    significant = Image.fromarray(np.where(pixels[:, :, 3] > 8, 255, 0).astype(np.uint8))
    near_subject = np.asarray(significant.filter(ImageFilter.MaxFilter(7))) > 0
    remote_noise = (pixels[:, :, 3] > 0) & (pixels[:, :, 3] <= 8) & ~near_subject
    near_transparent = np.asarray(Image.fromarray(pixels[:, :, 3]).filter(ImageFilter.MinFilter(7))) == 0
    rgb_min, rgb_max = pixels[:, :, :3].min(2), pixels[:, :, :3].max(2)
    chromatic_noise = ((pixels[:, :, 3] > 0) & (pixels[:, :, 3] <= 8) & near_transparent &
                       (rgb_max > 220) & (rgb_min < 32) & (rgb_max.astype(int) - rgb_min.astype(int) > 180))
    pixels[:, :, 3][remote_noise | chromatic_noise] = 0
    im = Image.fromarray(pixels, "RGBA")
    cleaned_metrics = metrics(im)
    require(not cleaned_metrics["alpha_boundary_touched"], "Significant raw alpha touches boundary; regenerate clipped or residual-edge source")
    canvas_factor = 1024 / max(im.size)
    factor = canvas_factor
    calibration = None
    if getattr(args, "head_reference", None):
        reference_folder = attempt_dir(args.head_reference)
        reference_request = read(reference_folder / "request.json")
        require(reference_request["kind"] == "idle" and reference_request["direction"] == request["direction"],
                "Head calibration needs an independently generated idle from same direction")
        reference_raw = reference_folder / "raw.png"
        reference_receipt = read(reference_folder / "generation-receipt.json")
        require(sha(reference_raw) == reference_receipt["rawSha256"], "Reference raw changed")
        with Image.open(reference_raw) as reference_image:
            target_width = head_band_width(reference_image) * 1024 / max(reference_image.size)
        measured_width = head_band_width(im)
        factor = target_width / measured_width
        require(factor <= 1, "Calibration would enlarge native artwork; regenerate source instead")
        calibration = {"method": "uniform_complete_frame_scale_to_same_direction_idle_head_band",
                       "referenceAttempt": args.head_reference, "referenceRaw": str(reference_raw),
                       "referenceRawSha256": sha(reference_raw), "nativeMeasuredWidth": measured_width,
                       "targetWidth": target_width, "measurement": "alpha>8;18..42%subjectheight;95th_percentile_row_span",
                       "limitation": "Diagnostic scale alignment cannot repair anatomy, angle or pose errors."}
    size = tuple(round(v * factor) for v in im.size)
    normalized = im.resize(size, Image.Resampling.LANCZOS) if im.size != size else im.copy()
    scale_metrics = metrics(normalized)
    delta = [round(512 - scale_metrics["axis"][0]), 942 - scale_metrics["axis"][1]]
    alpha_box = normalized.getchannel("A").getbbox()
    bounds = [alpha_box[0] + delta[0], alpha_box[1] + delta[1], alpha_box[2] + delta[0], alpha_box[3] + delta[1]]
    require(min(bounds[:2]) >= 1 and max(bounds[2:]) <= 1023, f"Uniform aligned export would clip {bounds}; regenerate margins, do not crop")
    final = Image.new("RGBA", (1024, 1024))
    final.paste(normalized, tuple(delta))
    result_metrics = metrics(final)
    revision = getattr(args, "revision", None)
    require(revision is None or re.fullmatch(r"[A-Za-z0-9_-]+", revision), "Invalid export revision")
    exported = HERE / "exports" / (args.attempt + ("--" + revision if revision else ""))
    require(not exported.exists(), "Export attempt already exists; retained immutable output must not be replaced")
    destination = OUT / request["slot"]
    if destination.exists():
        require(args.replace, "Slot already selected; --replace retains old selection in history")
    exported.mkdir(parents=True)
    im.save(exported / "alpha-cleaned.png")
    normalized.save(exported / "normalized.png")
    final.save(exported / "output.png")
    record = {"character": CHAR, "attempt": args.attempt, "slot": request["slot"], "status": "candidate_pending_visual_review",
              "exportedAt": now(), "outputSha256": sha(exported / "output.png"),
              "derivedFrom": {"path": str(raw), "sha256": sha(raw), "generationRecord": str(folder / "raw.png.generation.json")},
              "operation": "remove_remote_alpha_noise_then_whole_canvas_uniform_downsample_then_integer_alignment; no_chroma_key; no_deformation; no_pose_synthesis",
              "commonScale": factor / canvas_factor, "wholeCanvasScale": factor, "normalizedSize": list(size), "translationPx": delta,
              "scaleCalibration": calibration,
              "anchorTarget": [512, 942], "alphaPolicy": "alpha<=8 remote speckles plus near-transparent extreme-saturation speckles removed; all source RGB and all alpha>8 unchanged before uniform resampling",
              "removedRemoteLowAlphaPixels": int(remote_noise.sum()), "alphaCleanedSha256": sha(exported / "alpha-cleaned.png"),
              "removedLowAlphaChromaticPixels": int(chromatic_noise.sum()), "removedUnionPixels": int((remote_noise | chromatic_noise).sum()),
              "nativeMetrics": raw_metrics, "outputMetrics": result_metrics,
              "actualModel": receipt.get("actualModel"), "actualQuality": receipt.get("actualQuality"),
              "configSnapshot": receipt.get("configSnapshot"), "submittedParameters": receipt.get("submittedParameters"),
              "normalizedSha256": sha(exported / "normalized.png"), "formalApproval": False, "clientIntegration": False}
    write(exported / "output.png.generation.json", record, exclusive=True)
    if destination.exists():
        backup = HERE / "selection-history" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") / request["slot"]
        copy_exact(destination, backup)
        if Path(str(destination) + ".generation.json").exists():
            copy_exact(Path(str(destination) + ".generation.json"), Path(str(backup) + ".generation.json"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(exported / "output.png", destination)
    shutil.copy2(exported / "output.png.generation.json", Path(str(destination) + ".generation.json"))
    print(json.dumps({"output": str(destination), "slot": request["slot"], "sha256": sha(destination),
                      "raw_height": raw_metrics["subject_height"], "height": result_metrics["subject_height"],
                      "anchor": result_metrics["axis"], "status": record["status"]}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--attempt", required=True)
    p.add_argument("--kind", choices=("walk", "idle"), required=True)
    p.add_argument("--direction", choices=DIRS, required=True)
    p.add_argument("--frame", type=int)
    p.add_argument("--prompt", type=Path, required=True)
    p.add_argument("--refs", type=Path, nargs="+", required=True)
    p.set_defaults(func=prepare)
    p = sub.add_parser("archive")
    p.add_argument("--attempt", required=True)
    p.add_argument("--request", type=Path, help="Ingest exact preexisting request without changing its original bytes")
    p.add_argument("--kind", choices=("walk", "idle"))
    p.add_argument("--direction", choices=DIRS)
    p.add_argument("--frame", type=int)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--result", type=Path)
    g.add_argument("--error", type=Path)
    p.add_argument("--original", type=Path)
    p.add_argument("--completed-at", help="Actual observed tool completion UTC; omit when unknown")
    p.set_defaults(func=archive)
    p = sub.add_parser("ingest", help="Read07-generation/ATTEMPT request/result, archive, optionally export/select")
    p.add_argument("--attempt", required=True)
    p.add_argument("--select", action="store_true")
    p.add_argument("--replace", action="store_true")
    p.add_argument("--revision")
    p.add_argument("--head-reference", help="Optional same-direction independent idle for complete-frame uniform downsample calibration")
    p.set_defaults(func=ingest)
    p = sub.add_parser("export")
    p.add_argument("--attempt", required=True)
    p.add_argument("--revision", help="New deterministic-processing version; never overwrites earlier exports")
    p.add_argument("--head-reference", help="Optional same-direction independent idle for complete-frame uniform downsample calibration")
    p.add_argument("--replace", action="store_true", help="Retain old selected slot and sidecar before selecting this new attempt")
    p.set_defaults(func=export)
    p = sub.add_parser("build-preview")
    p.add_argument("--revision", required=True)
    p.set_defaults(func=build_preview)
    args = parser.parse_args()
    args.func(args)


def build_preview(args):
    require(re.fullmatch(r"[A-Za-z0-9_-]+", args.revision), "Invalid revision")
    root = PREVIEWS / args.revision
    require(not root.exists(), "Use a new immutable preview revision")
    root.mkdir(parents=True)
    (root / "preview").mkdir()
    expected = [f"walk/{d}/{n:02d}.png" for d in DIRS for n in range(1, 17)] + [f"idle/{d}.png" for d in DIRS]
    rows, missing, cropped_hashes, mirrors, raw_hashes = [], [], [], [], []
    for key in expected:
        source = OUT / key
        if not source.is_file():
            missing.append(key)
            continue
        meta = read(Path(str(source) + ".generation.json"))
        require(sha(source) == meta["outputSha256"], "Selected PNG differs from sidecar: " + key)
        target = root / "runtime" / key
        copy_exact(source, target)
        copy_exact(Path(str(source) + ".generation.json"), Path(str(target) + ".generation.json"))
        with Image.open(target) as opened:
            require(opened.mode == "RGBA" and opened.size == (1024, 1024), "All new exports must be1024 RGBA")
            im = opened.copy()
        native = Path(meta["derivedFrom"]["path"])
        require(native.is_file() and sha(native) == meta["derivedFrom"]["sha256"], "Original raw changed")
        crop = im.crop(im.getchannel("A").getbbox())
        cropped_hashes.append((crop.size, hashlib.sha256(crop.tobytes()).hexdigest()))
        mirrors.append((crop.size, hashlib.sha256(crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes()).hexdigest()))
        raw_hashes.append(sha(native))
        rows.append({"path": key, "sha256": sha(target), "source": str(source), "attempt": meta["attempt"],
                     "nativeSource": meta["derivedFrom"], "nativeSize": meta["nativeMetrics"]["size"],
                     "metrics": metrics(im), "status": "candidate_pending_visual_review",
                     "actualModel": meta.get("actualModel"), "actualQuality": meta.get("actualQuality")})
    bykey = {r["path"]: r for r in rows}
    direction_report, gifs = {}, []
    for direction in DIRS:
        keys = [f"walk/{direction}/{n:02d}.png" for n in range(1, 17)]
        present = [k for k in keys if k in bykey]
        heights = [bykey[k]["metrics"]["subject_height"] for k in present]
        scales = [bykey[k]["metrics"]["body_scale"] for k in present]
        direction_report[direction] = {"walk": len(present), "idle": f"idle/{direction}.png" in bykey,
            "complete": len(present) == 16, "meanHeight": float(np.mean(heights)) if heights else None,
            "bodyScaleCV": float(np.std(scales) / np.mean(scales)) if scales else None,
            "semanticGaitReview": "pending", "dynamicReview": "pending"}
        for mode, color in (("dark", (30, 38, 46)), ("light", (240, 238, 228))):
            ink = "white" if mode == "dark" else "black"
            displays = []
            contact = Image.new("RGB", (1024, 1160), color)
            draw = ImageDraw.Draw(contact)
            for index, key in enumerate(keys):
                view = Image.new("RGB", (512, 512), color)
                if key in bykey:
                    with Image.open(root / "runtime" / key) as im:
                        small = im.resize((512, 512), Image.Resampling.LANCZOS)
                        view.paste(small, (0, 0), small)
                else:
                    ImageDraw.Draw(view).text((170, 245), "MISSING - NO SUBSTITUTE", fill=ink)
                displays.append(view)
                x, y = index % 4 * 256, index // 4 * 290
                contact.paste(view.resize((256, 256), Image.Resampling.LANCZOS), (x, y + 28))
                draw.text((x + 10, y + 8), f"{direction}{index+1:02d}" + (" / MISSING" if key not in bykey else ""), fill=ink)
            contact.save(root / f"preview/{direction}-contact-{mode}.png")
            seam = Image.new("RGB", (2048, 552), color)
            for column, n in enumerate((14, 15, 0, 1)):
                seam.paste(displays[n], (column * 512, 40))
                ImageDraw.Draw(seam).text((column * 512 + 14, 14), f"{direction}{n+1:02d}", fill=ink)
            seam.save(root / f"preview/{direction}-seam-{mode}.png")
            if len(present) == 16:
                gif = root / f"preview/{direction}-30ms-{mode}.gif"
                displays[0].save(gif, save_all=True, append_images=displays[1:], duration=[30] * 16,
                                 loop=0, optimize=False, disposal=2)
                with Image.open(gif) as check:
                    durations = []
                    for n in range(check.n_frames):
                        check.seek(n)
                        durations.append(check.info.get("duration"))
                    require(check.n_frames == 16 and durations == [30] * 16, "GIF timing/frame count mismatch")
                gifs.append({"path": str(gif.relative_to(root)), "sha256": sha(gif), "frames": 16,
                             "durationMs": durations, "cycleMs": 480, "interpolation": False})
    for mode, color in (("dark", (30, 38, 46)), ("light", (240, 238, 228))):
        contact = Image.new("RGB", (1024, 580), color)
        for n, direction in enumerate(DIRS):
            key = f"idle/{direction}.png"
            x, y = n % 4 * 256, n // 4 * 290
            ImageDraw.Draw(contact).text((x + 10, y + 8), direction + (" / MISSING" if key not in bykey else ""),
                                        fill="white" if mode == "dark" else "black")
            if key in bykey:
                with Image.open(root / "runtime" / key) as im:
                    small = im.resize((256, 256), Image.Resampling.LANCZOS)
                    contact.paste(small, (x, y + 28), small)
        contact.save(root / f"preview/idle-contact-{mode}.png")
    report = {"character": CHAR, "revision": args.revision, "builtAt": now(),
              "walkCount": sum(r["path"].startswith("walk/") for r in rows),
              "idleCount": sum(r["path"].startswith("idle/") for r in rows), "missing": missing,
              "frameDurationMs": 30, "cycleDurationMs": 480, "directions": direction_report,
              "files": rows, "gifs": gifs, "allOutput1024RGBA": True,
              "uniqueRawHashes": len(set(raw_hashes)), "uniqueCroppedPixelHashes": len(set(cropped_hashes)),
              "exactCroppedHorizontalMirrorMatches": len(set(cropped_hashes) & set(mirrors)),
              "alphaBoundaryTouchCount": sum(r["metrics"]["alpha_boundary_touched"] for r in rows),
              "offlineVisualReview": "pending", "formalApproval": False, "clientIntegration": False,
              "limitations": "Inventory, hashes and GIF timing do not establish anatomical or artistic acceptance. Missing frames have no substitute."}
    write(root / "manifest.json", report, exclusive=True)
    write(root / "structural-report.json", {**report, "manifestSha256": sha(root / "manifest.json")}, exclusive=True)
    template = (HERE / "preview-template.html").read_text(encoding="utf-8")
    (root / "index.html").write_text(template.replace("__MANIFEST__", json.dumps(report, ensure_ascii=False)), encoding="utf-8")
    PREVIEWS.mkdir(exist_ok=True)
    (PREVIEWS / "index.html").write_text(f'<!doctype html><meta charset="utf-8"><title>07 月影少女预览</title><a href="{args.revision}/index.html">07 月影少女 {args.revision}：{report["walkCount"]}/128行走 + {report["idleCount"]}/8独立站立，待美术复核</a>', encoding="utf-8")
    print(json.dumps({"preview": str(root / "index.html"), "manifest_sha256": sha(root / "manifest.json"),
                      "walk": report["walkCount"], "idle": report["idleCount"], "missing": len(missing), "gifs": len(gifs)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
