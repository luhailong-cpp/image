"""Prepare layout references and assemble generated detail; never call an image API."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "tianyong_festival_hd_20260910/tianyong_city_master_6144.png"
CORE, HALO, NATIVE = 2048, 128, 2304
IDS = ("r01_c01", "r01_c02", "r02_c01", "r02_c02")


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare():
    """Crop only, leaving the low-resolution references at their actual pixel size."""
    for name in ("references", "prompts", "generated", "qa"):
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as original:
        original.load()
        if original.size != (6144, 6144):
            raise ValueError("The approved layout source has changed size.")
        source = original.convert("RGB")
    source.crop((2048, 2048, 4096, 4096)).save(ROOT / "references/tianyong-center-layout-only.png")
    patches = []
    for index, patch_id in enumerate(IDS):
        row, col = divmod(index, 2)
        # This sample doubles the source detail density through generation, never resampling.
        x, y = 1984 + col * 1024, 1984 + row * 1024
        relative = f"references/{patch_id}.layout-only.png"
        source.crop((x, y, x + 1152, y + 1152)).save(ROOT / relative)
        patches.append({"id": patch_id, "row": row, "column": col,
                        "layoutReference": relative, "referencePixels": [1152, 1152],
                        "sourceCrop": [x, y, x + 1152, y + 1152],
                        "referenceSha256": digest(ROOT / relative),
                        "targetNativePixels": [NATIVE, NATIVE],
                        "corePixels": [CORE, CORE], "contextPerSide": HALO,
                        "promptFile": f"prompts/{patch_id}.prompt.txt",
                        "generatedFile": f"generated/{patch_id}.png"})
    write_json("preparation.json", {
        "schemaVersion": 1, "status": "prepared_awaiting_authorized_generation",
        "sourceFile": str(SOURCE), "sourcePixels": [6144, 6144], "sourceSha256": digest(SOURCE),
        "referencePurpose": "layout only; existing artwork, not new HD output",
        "cityKey": "tianyong", "variant": "festival", "sampleSourceCrop": [2048, 2048, 4096, 4096],
        "sampleWorldRect": {"x": 150, "y": 100, "width": 100, "height": 100},
        "targetTilePixels": [4096, 4096], "completeMapRows": None, "completeMapColumns": None,
        "targetModel": "gpt-image-2.5-sunburst-2026-09-08", "targetQuality": "max",
        "actualModel": None, "nativeOverlapPixels": 256,
        "generatedArtworkCount": 0, "runtimePublished": False, "patches": patches})
    print("Prepared 4 unscaled layout references; generated artwork count remains 0.")


def assemble():
    metadata = json.loads((ROOT / "preparation.json").read_text(encoding="utf-8"))
    if digest(SOURCE) != metadata["sourceSha256"]:
        raise ValueError("Layout source changed; review before assembling.")
    records_path = ROOT / "generation-records.json"
    if not records_path.is_file():
        raise ValueError("Missing generation-records.json: real generator evidence is required, not placeholder artwork.")
    records = json.loads(records_path.read_text(encoding="utf-8"))
    if {item["id"] for item in records} != set(IDS) or len(records) != 4:
        raise ValueError("Exactly four distinct generator records are required.")
    records = {item["id"]: item for item in records}
    arrays, provenance = [], []
    for patch in metadata["patches"]:
        patch_id = patch["id"]
        record = records[patch_id]
        if record.get("model") != metadata["targetModel"] or record.get("quality") != "max":
            raise ValueError(f"{patch_id}: expected the explicitly requested 2.5 snapshot and max quality.")
        if not record.get("requestId") or record.get("nativePixels") != [NATIVE, NATIVE]:
            raise ValueError(f"{patch_id}: missing generator provenance/native dimensions.")
        ref = ROOT / patch["layoutReference"]
        if digest(ref) != patch["referenceSha256"]:
            raise ValueError(f"{patch_id}: reference changed.")
        prompt = ROOT / patch["promptFile"]
        if not prompt.is_file() or digest(prompt) != record.get("promptSha256"):
            raise ValueError(f"{patch_id}: prompt does not match the recorded request.")
        path = ROOT / patch["generatedFile"]
        if digest(path) != record.get("outputSha256"):
            raise ValueError(f"{patch_id}: output differs from the generator record.")
        with Image.open(path) as generated:
            generated.load()
            if generated.format != "PNG" or generated.size != (NATIVE, NATIVE):
                raise ValueError(f"{patch_id}: expected a native 2304x2304 PNG; resampling is not allowed.")
            if "A" in generated.getbands() and generated.getchannel("A").getextrema() != (255, 255):
                raise ValueError(f"{patch_id}: terrain output must be fully opaque.")
            rgb = generated.convert("RGB")
            with Image.open(ref) as reference:
                enlarged = reference.convert("RGB").resize(rgb.size, Image.Resampling.LANCZOS)
            if np.array_equal(np.asarray(rgb), np.asarray(enlarged)):
                raise ValueError(f"{patch_id}: supplied artwork is just the enlarged reference.")
            arrays.append(np.asarray(rgb))
        provenance.append({"id": patch_id, "sha256": digest(path), "requestId": record["requestId"]})
    sys.dont_write_bytecode = True
    helper_path = ROOT.parent / "tianyong_festival_hd_20260910/seam_helpers.py"
    spec = importlib.util.spec_from_file_location("city_seams", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    def append(base, patch):
        result = helper._append_with_minimum_seam(base, patch, 256)
        # Float blending can truncate an identical source value by one level.
        # Preserve exact pixels wherever both overlap inputs already agree.
        left, right = base[:, -256:], patch[:, :256]
        identical = np.all(left == right, axis=2)
        overlap = result[:, base.shape[1] - 256:base.shape[1]]
        overlap[identical] = left[identical]
        return result

    upper = append(arrays[0], arrays[1])
    lower = append(arrays[2], arrays[3])
    assembled = append(upper.transpose(1, 0, 2), lower.transpose(1, 0, 2)).transpose(1, 0, 2)
    full = Image.fromarray(assembled)
    if full.size != (4352, 4352):
        raise AssertionError("Unexpected stitched bounds.")
    full.save(ROOT / "qa/tianyong-center-with-context-4352.png")
    tile = full.crop((128, 128, 4224, 4224))
    tile.save(ROOT / "qa/tianyong-center-candidate-4096.png")
    preview = tile.copy()
    preview.thumbnail((1024, 1024))
    preview.save(ROOT / "qa/tianyong-center-candidate-preview.png")
    write_json("assembly.json", {
        "status": "candidate_requires_visual_and_navigation_review", "tilePixels": list(tile.size),
        "sourceType": "four native max-quality renders stitched without enlargement",
        "nativePatchCount": 4, "nativePatchPixels": [2304, 2304], "overlapPixels": 256,
        "seamMethod": "existing minimum-error seam with 2px feather", "patches": provenance,
        "candidateSha256": digest(ROOT / "qa/tianyong-center-candidate-4096.png"),
        "resamplingUsedOnFinalArt": False, "visualReviewed": False,
        "navigationReviewed": False, "runtimePublished": False})
    print("4096 candidate assembled; visual, neighboring-tile, navigation and runtime review still required.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "assemble"))
    args = parser.parse_args()
    try:
        prepare() if args.action == "prepare" else assemble()
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f"error: {error}\n")
