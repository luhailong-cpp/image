"""Assemble unreviewed r08_c13 cores and native-pixel QA; never update state.

Usage: python assemble_native.py assemble
       python assemble_native.py partial-preview

Only native patches with matching .png.generation.json SHA-256 are consumed.
No generation, registration, color correction, feathering or artwork scaling
is performed. The partial preview alone is downscaled and is not final art.
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
import tempfile

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
TILE = ROOT / "r08_c13"
NATIVE = TILE / "native"
OUTPUT = TILE / "output"
QA = TILE / "qa" / "core-assembly"
CORE_BOX = (115, 115, 1139, 1139)
EXPECTED = [f"r{row:02}_c{col:02}" for row in range(1, 5) for col in range(1, 5)]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decode(data: bytes, name: str, expected_size: tuple[int, int]) -> Image.Image:
    with Image.open(io.BytesIO(data)) as source:
        source.load()
        if source.size != expected_size:
            raise ValueError(f"{name}: expected {expected_size}, got {source.size}")
        if source.mode not in ("RGB", "RGBA"):
            raise ValueError(f"{name}: expected RGB/RGBA, got {source.mode}")
        if source.mode == "RGBA" and source.getchannel("A").getextrema() != (255, 255):
            raise ValueError(f"{name}: transparent pixels are not complete opaque artwork")
        return source.convert("RGB")


def load_patches(require_complete: bool) -> tuple[dict, list]:
    files = sorted(NATIVE.glob("r??_c??.png"))
    extras = [path.name for path in files if path.stem not in EXPECTED]
    if extras:
        raise ValueError(f"Unexpected patch coordinates: {extras}")
    patches, evidence, missing = {}, [], []
    for patch_id in EXPECTED:
        path = NATIVE / f"{patch_id}.png"
        if not path.exists():
            missing.append(patch_id)
            continue
        record_path = Path(str(path) + ".generation.json")
        if not record_path.is_file():
            raise ValueError(f"Missing generation record: {record_path}")
        # Bind both pixels and record to the bytes actually read in this run.
        data, record_data = path.read_bytes(), record_path.read_bytes()
        record = json.loads(record_data.decode("utf-8-sig"))
        expected_hash = record.get("sha256")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
            raise ValueError(f"Invalid generation SHA-256: {record_path}")
        actual_hash = digest(data)
        if expected_hash.lower() != actual_hash:
            raise ValueError(f"Generation SHA-256 mismatch: {path}")
        if record.get("resizedAfterGeneration") is not False:
            raise ValueError(f"Native unscaled provenance is not explicit: {record_path}")
        if record.get("finalArtUpscaled") is True:
            raise ValueError(f"Upscaled source is forbidden: {record_path}")
        image = decode(data, str(path), (1254, 1254))
        if record.get("width") != 1254 or record.get("height") != 1254:
            raise ValueError(f"Generation dimensions do not match native pixels: {record_path}")
        row, col = int(patch_id[1:3]), int(patch_id[5:7])
        patches[patch_id] = image.crop(CORE_BOX)
        evidence.append({
            "id": patch_id, "file": str(path), "sha256": actual_hash,
            "pixels": [1254, 1254], "generationRecord": str(record_path),
            "generationRecordSha256": digest(record_data),
            "generationHashVerified": True, "sourceCoreCropXYXY": list(CORE_BOX),
            "destinationXY": [(col - 1) * 1024, (row - 1) * 1024],
            "resized": False,
        })
    if require_complete and missing:
        raise ValueError(f"Complete 4K assembly requires all 16 patches; missing: {missing}")
    return patches, evidence


def atomic_write(path: Path, data: bytes) -> None:
    resolved = path.resolve()
    if not any(resolved.is_relative_to(folder.resolve()) for folder in (OUTPUT, QA)):
        raise ValueError(f"Output outside allowed task folders: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".assembly-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_image(path: Path, image: Image.Image, metadata: dict) -> dict:
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    data = stream.getvalue()
    record = {
        "schemaVersion": 1, "createdAtUtc": now(), "file": str(path),
        "sha256": digest(data), "pixels": list(image.size),
        "formalAccepted": False, "clientAccepted": False,
        "visualReview": "pending; this script performs no visual acceptance",
        **metadata,
    }
    atomic_write(path, data)
    sidecar = Path(str(path) + ".generation.json")
    atomic_write(sidecar, (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return {"file": str(path), "sha256": record["sha256"], "pixels": list(image.size),
            "sidecar": str(sidecar), "sidecarSha256": digest(sidecar.read_bytes())}


def load_west() -> tuple[Image.Image, dict]:
    contract_path = TILE / "source-contract.json"
    contract = read_json(contract_path)
    source = contract["west"]
    path = Path(source["file"])
    data = path.read_bytes()
    if digest(data) != source["sha256"] or source["sha256"] != contract["westSourceSha256"]:
        raise ValueError("Pinned c12 source-contract hash mismatch")
    image = decode(data, str(path), (4096, 4096))
    proof = {"file": str(path), "sha256": digest(data), "pixels": [4096, 4096],
             "role": "read-only pinned west neighbor r08_c12 from c13 source contract",
             "sourceContract": {"file": str(contract_path), "sha256": digest(contract_path.read_bytes())}}
    selection_path = ROOT / "current-selection.json"
    if selection_path.is_file():
        selection = read_json(selection_path)
        if selection.get("tile") == "r08_c12":
            selected = selection["core"]
            active_data = Path(selected["file"]).read_bytes()
            if digest(active_data) != selected["sha256"]:
                raise ValueError("Current c12 selected source hash mismatch")
            active = decode(active_data, selected["file"], (4096, 4096))
            same = image.crop((3584, 0, 4096, 4096)).tobytes() == active.crop((3584, 0, 4096, 4096)).tobytes()
            if not same:
                raise ValueError("Current c12 east512 differs from pinned c13 generation context; coordinate shared-edge QA before assembly")
            proof["currentC12East512PixelIdentical"] = True
            proof["currentC12AtRun"] = selected
    return image, proof


def source_crop(source: dict, box: tuple, position: tuple) -> dict:
    return {"sourceFile": source["file"], "sourceSha256": source["sha256"],
            "sourceCropXYXY": list(box), "destinationXY": list(position),
            "resized": False, "rotated": False}


def export_qa(core: Image.Image, candidate: dict, west: Image.Image, west_source: dict) -> list:
    exports = []

    def save(name: str, image: Image.Image, crops: list, scope: str) -> None:
        sources = [candidate]
        if any(crop["sourceFile"] == west_source["file"] for crop in crops):
            sources.append(west_source)
        exports.append(save_image(QA / name, image, {
            "operation": "unscaled exact source crops rearranged for native-pixel inspection",
            "role": "QA only; not final artwork", "finalArt": False,
            "derivedFrom": sources, "crops": crops, "inspectionScope": scope,
            "artResampled": False, "colorCorrection": False,
        }))

    for axis in ("x", "y"):
        for boundary in (1024, 2048, 3072):
            sheet, crops = Image.new("RGB", (1024, 1024)), []
            for part in range(4):
                if axis == "x":
                    box = (boundary - 128, part * 1024, boundary + 128, (part + 1) * 1024)
                    position = (part * 256, 0)
                else:
                    box = (part * 1024, boundary - 128, (part + 1) * 1024, boundary + 128)
                    position = (0, part * 256)
                sheet.paste(core.crop(box), position)
                crops.append(source_crop(candidate, box, position))
            order = "top-to-bottom source segments arranged left-to-right" if axis == "x" else "left-to-right source segments arranged top-to-bottom"
            save(f"{axis}{boundary}-full4096.png", sheet, crops,
                 f"Full 4096-pixel internal {axis}={boundary} seam, 256-wide band; {order}; no rotation or resize")

    sheet, crops = Image.new("RGB", (1536, 1536)), []
    for row, y in enumerate((1024, 2048, 3072)):
        for col, x in enumerate((1024, 2048, 3072)):
            box, position = (x - 256, y - 256, x + 256, y + 256), (col * 512, row * 512)
            sheet.paste(core.crop(box), position)
            crops.append(source_crop(candidate, box, position))
    save("nine-internal-junctions.png", sheet, crops, "All nine internal intersections; 512-square each, arranged spatially in a 3x3 grid")

    sheet, crops = Image.new("RGB", (1024, 1024)), []
    for box, position in (((0, 0, 512, 512), (0, 0)), ((3584, 0, 4096, 512), (512, 0)),
                          ((0, 3584, 512, 4096), (0, 512)), ((3584, 3584, 4096, 4096), (512, 512))):
        sheet.paste(core.crop(box), position)
        crops.append(source_crop(candidate, box, position))
    save("four-tile-corners.png", sheet, crops, "Four 512-square corners of this candidate only; adjacent north/south/east tiles are unavailable, so this is not four-tile junction acceptance")

    sheet, crops = Image.new("RGB", (1024, 1024)), []
    for part in range(4):
        y0, y1 = part * 1024, (part + 1) * 1024
        for image, source, box, position in (
            (west, west_source, (3968, y0, 4096, y1), (part * 256, 0)),
            (core, candidate, (0, y0, 128, y1), (part * 256 + 128, 0)),
        ):
            sheet.paste(image.crop(box), position)
            crops.append(source_crop(source, box, position))
    save("west-c12-c13-full4096.png", sheet, crops,
         "Entire west common edge: 128 pixels from c12 plus 128 pixels from c13; four 1024-high source segments arranged left-to-right without resizing")
    return exports


def assemble() -> dict:
    patches, evidence = load_patches(require_complete=True)
    # Validate every dependency before writing any assembled candidate or QA.
    west, west_source = load_west()
    core = Image.new("RGB", (4096, 4096))
    for source in evidence:
        core.paste(patches[source["id"]], tuple(source["destinationXY"]))
    candidate = save_image(OUTPUT / "r08_c13-unreviewed.png", core, {
        "operation": "16 native 1024-square cores assembled at exact integer coordinates",
        "role": "unreviewed complete-pixel candidate; not formally accepted",
        "finalArt": False, "completePixelCandidate": True,
        "globalPixelRectXYWH": [49152, 28672, 4096, 4096],
        "derivedFrom": evidence, "artResampled": False, "artUpscaled": False,
        "feathering": False, "registration": False, "colorCorrection": False,
        "stateFilesModified": False,
    })
    qa_exports = export_qa(core, candidate, west, west_source)
    return {"mode": "assemble", "candidate": candidate, "qa": qa_exports,
            "formalAccepted": False, "stateFilesModified": False}


def partial_preview() -> dict:
    patches, evidence = load_patches(require_complete=False)
    preview = Image.new("RGB", (1024, 1024), (38, 49, 58))
    for source in evidence:
        position = tuple(value // 4 for value in source["destinationXY"])
        preview.paste(patches[source["id"]].resize((256, 256), Image.Resampling.LANCZOS), position)
    result = save_image(OUTPUT / "r08_c13-partial-preview.png", preview, {
        "operation": "quarter-size native-core placement preview; missing cells remain dark gray",
        "role": "partial overview only; never a 4K candidate or final artwork",
        "finalArt": False, "completePixelCandidate": False,
        "fragmentsCountAsTiles": False, "nativePatchesShown": len(patches),
        "requiredNativePatches": 16, "missing": [key for key in EXPECTED if key not in patches],
        "derivedFrom": evidence, "previewResampling": "LANCZOS 1024 to 256 per core",
        "previewScale": 0.25, "missingPixelRGB": [38, 49, 58],
        "stateFilesModified": False,
    })
    return {"mode": "partial-preview", "preview": result, "nativePatchesShown": len(patches),
            "countAsProducedTile": False, "stateFilesModified": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("assemble", "partial-preview"))
    args = parser.parse_args()
    try:
        result = assemble() if args.mode == "assemble" else partial_preview()
    except (OSError, ValueError, KeyError) as error:
        print(f"Assembly refused: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
