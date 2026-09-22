"""Crop exact repair contexts and mechanically apply native repairs into new versions.

No image generation or visual approval. All outputs remain below tools/repairs.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
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
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def name(value):
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,100}", value), "Use a plain unique id/version name")
    return value


def png(path, expected):
    with Image.open(path) as image:
        require(image.format == "PNG" and getattr(image, "n_frames", 1) == 1, "Expected static PNG")
        image.verify()
    with Image.open(path) as image:
        image.load()
        require(image.size == tuple(expected), f"Expected {expected}, received {image.size}")
        require(image.mode in ("RGB", "RGBA"), "Expected RGB/RGBA")
        require(image.mode != "RGBA" or image.getextrema()[3] == (255, 255), "Expected opaque repair")
        return np.asarray(image.convert("RGB")).copy()


def mask_for(shape, width, feather=32, outer_fade=80):
    yy, xx = np.mgrid[:1254, :1254].astype(np.float32)
    center = 627.0
    distance = {"vertical": np.abs(xx - center), "horizontal": np.abs(yy - center),
                "cross": np.minimum(np.abs(xx - center), np.abs(yy - center))}[shape]
    alpha = np.clip((width / 2 + feather - distance) / (2 * feather), 0, 1)
    alpha = alpha * alpha * (3 - 2 * alpha)
    edge_distance = np.minimum.reduce([xx, yy, 1253 - xx, 1253 - yy])
    edge_weight = np.clip(edge_distance / outer_fade, 0, 1)
    edge_weight = edge_weight * edge_weight * (3 - 2 * edge_weight)
    return np.rint(alpha * edge_weight * 255).astype(np.uint8)


def prepare(args):
    source = Path(args.source).resolve()
    pixels = png(source, [4096, 4096])
    source_record = Path(args.source_record).resolve() if args.source_record else next(
        (p for p in (source.parent / "assembly.json", source.parent / "repair.json") if p.is_file()), None)
    require(source_record is not None and source_record.is_file(), "Source assembly/repair record is required")
    x, y = args.center_x - 627, args.center_y - 627
    box = [x, y, x + 1254, y + 1254]
    require(x >= 0 and y >= 0 and x + 1254 <= 4096 and y + 1254 <= 4096, "1254-square context must fit inside candidate")
    require(64 <= args.width <= 600, "Repair band width must be 64..600 pixels")
    directory = HERE / "repairs" / "prepared" / name(args.id)
    require(not directory.exists(), "Prepared repair already exists; use a new id")
    directory.mkdir(parents=True)
    context = directory / "context-native-1254.png"
    mask = directory / "mask.png"
    Image.fromarray(pixels[y:y + 1254, x:x + 1254]).save(context)
    alpha = mask_for(args.shape, args.width)
    Image.fromarray(alpha).save(mask)
    record = {"schemaVersion": 1, "id": args.id, "role": "repair_context_and_mask_not_final_art",
              "source": str(source), "sourceSha256": sha(source),
              "sourceRecord": str(source_record), "sourceRecordSha256": sha(source_record),
              "canvasBoxLTRB": box, "centerXY": [args.center_x, args.center_y],
              "context": str(context), "contextSha256": sha(context), "contextPixels": [1254, 1254],
              "resized": False, "mask": str(mask), "maskSha256": sha(mask),
              "maskShape": args.shape, "bandWidthPixels": args.width, "bandFeatherPixels": 32,
              "outerContextFadePixels": 80, "nonzeroMaskPixelCount": int(np.count_nonzero(alpha)),
              "maximumAllowedShiftPixels": 8.0, "visualAcceptancePassed": False}
    write_new(directory / "prepared.json", record)
    return {"prepared": str(directory / "prepared.json"), "reference": str(context), "mask": str(mask),
            "canvasBoxLTRB": box, "accepted": False}


def apply_repair(args):
    prepared_path = Path(args.prepared).resolve()
    prepared = read(prepared_path)
    source = Path(prepared["source"])
    for field in ("source", "sourceRecord", "context", "mask"):
        require(sha(prepared[field]) == prepared[field + "Sha256"], f"Prepared {field} changed")
    before = png(source, [4096, 4096])
    context = png(prepared["context"], [1254, 1254])
    x0, y0, x1, y1 = prepared["canvasBoxLTRB"]
    require(np.array_equal(before[y0:y1, x0:x1], context), "Prepared context no longer matches source candidate")
    request_path = Path(args.request_file).resolve()
    receipt = read(request_path)
    request = receipt["request"]
    require(request["prompt"].strip(), "Actual submitted prompt is required")
    refs = [Path(p).resolve() for p in request["referenced_image_paths"]]
    require(refs and refs[0] == Path(prepared["context"]).resolve(), "First actual reference must be the prepared context")
    match = re.search(r" as (.+?\.png) by default\.", receipt["response"]["output_hint"], re.DOTALL)
    require(match is not None, "Cannot identify original output path from actual receipt")
    native = Path(args.native).resolve() if args.native else Path(match.group(1)).resolve()
    require(native == Path(match.group(1)).resolve(), "Explicit native path must match actual tool receipt")
    repair = png(native, [1254, 1254])
    with Image.open(prepared["mask"]) as image:
        require(image.mode == "L" and image.size == (1254, 1254), "Invalid prepared mask")
        alpha = np.asarray(image).copy()
    sys.path.insert(0, str(HERE.parent / "tools" / "vendor"))
    helper_path = HERE.parents[1] / "tools/mechanical_join.py"
    spec = importlib.util.spec_from_file_location("city_mechanical_repair", helper_path)
    helper = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(helper)
        result, flow, correction, registration = helper.registered_join(
            context, repair, alpha, max_shift=8.0, match_tone=True)
    finally:
        sys.dont_write_bytecode = previous
    require(np.array_equal(result[alpha == 0], context[alpha == 0]), "Pixels outside repair mask changed")
    after = before.copy()
    after[y0:y1, x0:x1] = result
    changed = np.any(after != before, axis=2)
    allowed = np.zeros((4096, 4096), dtype=bool)
    allowed[y0:y1, x0:x1] = alpha > 0
    require(not np.any(changed & ~allowed), "Pixels outside full-canvas repair mask changed")
    directory = HERE / "repairs" / "versions" / name(args.version)
    require(not directory.exists(), "Repair version already exists; never replace an existing candidate")
    directory.mkdir(parents=True)
    for original, filename in ((native, "repair-native-1254.png"), (request_path, "request-receipt.json"),
                               (Path(prepared["mask"]), "mask.png"), (Path(prepared["context"]), "context-before.png")):
        with original.open("rb") as incoming, (directory / filename).open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        require(sha(original) == sha(directory / filename), "Source-byte preservation failed")
    (directory / "actual-prompt.txt").write_text(request["prompt"], encoding="utf-8", newline="")
    np.save(directory / "flow.npy", flow, allow_pickle=False)
    np.save(directory / "correction.npy", correction, allow_pickle=False)
    Image.fromarray(result).save(directory / "context-after.png")
    Image.fromarray(after).save(directory / "r09_c10.png")
    preview = Image.fromarray(after)
    preview.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    preview.save(directory / "overview-preview-only.png")
    files = {p.name: {"file": p.name, "sha256": sha(p)} for p in directory.iterdir() if p.is_file()}
    record = {"schemaVersion": 1, "version": args.version, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
              "status": "repaired_candidate_pending_visual_QA_not_published", "productionAccepted": False,
              "prepared": {"file": str(prepared_path), "sha256": sha(prepared_path)},
              "sourceCandidate": {"file": str(source), "sha256": sha(source)},
              "sourceRecord": {"file": prepared["sourceRecord"], "sha256": prepared["sourceRecordSha256"]},
              "originalNativeOutput": {"file": str(native), "sha256": sha(native), "actualNativePixels": [1254, 1254]},
              "actualPromptSha256": sha(directory / "actual-prompt.txt"),
              "actualReferences": [{"file": str(p), "sha256": sha(p)} for p in refs],
              "actualModel": None, "actualQuality": None, "backendModelVerified": False,
              "toolName": "image_gen.imagegen", "modelSelectorAvailable": False, "qualitySelectorAvailable": False,
              "helper": {"file": str(helper_path), "sha256": sha(helper_path)},
              "libraries": {"numpy": np.__version__, "opencv": helper.cv2.__version__},
              "script": {"file": str(Path(__file__).resolve()), "sha256": sha(__file__)},
              "canvasBoxLTRB": prepared["canvasBoxLTRB"], "registration": registration,
              "maskShape": prepared["maskShape"], "maskPixels": [1254, 1254],
              "changedCanvasPixelCount": int(changed.sum()), "outsideMaskPixelsUnchanged": True,
              "originalNativeBytesPreserved": True, "finalArtUpscaled": False,
              "resampling": "Recorded bounded subpixel alignment of repair boundary; no image enlargement",
              "files": files, "visualAcceptancePassed": False, "runtimePublished": False}
    write_new(directory / "repair.json", record)
    require(sha(source) == prepared["sourceSha256"], "Original candidate changed during repair")
    return {"candidate": str(directory / "r09_c10.png"), "record": str(directory / "repair.json"),
            "outsideMaskPixelsUnchanged": True, "actualMaxShiftXY": registration["actualMaxShiftXY"],
            "accepted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--source", required=True)
    prep.add_argument("--source-record")
    prep.add_argument("--center-x", type=int, required=True)
    prep.add_argument("--center-y", type=int, required=True)
    prep.add_argument("--id", required=True)
    prep.add_argument("--shape", choices=("cross", "vertical", "horizontal"), default="cross")
    prep.add_argument("--width", type=int, default=280)
    apply = commands.add_parser("apply-repair")
    apply.add_argument("--prepared", required=True)
    apply.add_argument("--request-file", required=True)
    apply.add_argument("--native", help="Optional original tool output PNG; must equal receipt output path")
    apply.add_argument("--version", required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args) if args.command == "prepare" else apply_repair(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, ModuleNotFoundError) as error:
        print(json.dumps({"error": str(error), "accepted": False}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
