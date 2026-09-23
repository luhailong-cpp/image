"""Assemble the selected native patches and prepare unreviewed 1:1 evidence.

No generation, scaling, blending, registration, acceptance, shared-state update,
or source deletion is performed. Run only after all 16 plan entries are ready.
The hard core boundaries intentionally expose geometric/material disagreements.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).resolve()
WORK = SCRIPT.parent
TILE_DIR = WORK.parent
PROJECT = TILE_DIR.parents[3]
PLAN = TILE_DIR / "plan.json"
LAYOUT = TILE_DIR / "layout-record.json"
TILE = "r08_c09"
NATIVE = 1254
CORE = 1024
HALO = 115
EXTENT = 4326
SIZE = 4096
HALF_STRIP = 128
SEGMENT = 1024
BOTTOM_SHA = "5ce3e9099c4292a3c2d2b854bcc6d2cfd3b8858bb6960bc8e7966699ade4742c"
STYLE_SHA = "85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def mapped_path(value: str) -> Path:
    """Resolve old E:/work/image pointers without modifying historical text."""
    normalized = str(value).replace("\\", "/")
    prefix = "E:/work/image"
    if normalized.lower() == prefix.lower():
        return PROJECT
    if normalized.lower().startswith(prefix.lower() + "/"):
        return PROJECT / normalized[len(prefix) + 1 :]
    result = Path(normalized)
    return result if result.is_absolute() else TILE_DIR / result


class Inputs:
    """Hash bytes as read, and reject concurrent changes before completion."""

    def __init__(self) -> None:
        self.observed: dict[Path, str] = {}
        self.texts: dict[Path, bytes] = {}
        self.line_ending_equivalence: list[dict] = []

    def read(self, path: Path, expected: str | None = None, text: bool = False) -> bytes:
        path = path.resolve(strict=True)
        data = path.read_bytes()
        digest = sha(data)
        if expected is not None:
            if digest != expected.lower() and text:
                # Windows checkout changed line endings in old text evidence.
                # Prove the complete historical byte stream, never ignore a SHA.
                historical = data.replace(b"\r\n", b"\n")
                require(sha(historical) == expected.lower(), f"SHA mismatch beyond CRLF/LF: {path}")
                self.line_ending_equivalence.append({"path": str(path), "currentByteSha256": digest,
                    "recordedHistoricalSha256": expected.lower(), "reconstructedHistoricalSha256": sha(historical),
                    "operation": "replace CRLF bytes with LF bytes only", "pngBytesAffected": False,
                    "claim": "Exact historical SHA reconstructed; current file bytes have different line endings"})
            else:
                require(digest == expected.lower(), f"SHA mismatch: {path}")
        old = self.observed.get(path)
        require(old is None or old == digest, f"STALE_FAIL: {path}")
        self.observed[path] = digest
        if text:
            self.texts[path] = data
        return data

    def json(self, path: Path, expected: str | None = None) -> dict:
        return json.loads(self.read(path, expected, text=True).decode("utf-8-sig"))

    def unchanged(self) -> None:
        for path, digest in self.observed.items():
            require(path.is_file() and sha(path.read_bytes()) == digest, f"STALE_FAIL: {path}")

    def identity(self, path: Path) -> dict:
        path = path.resolve()
        return {"path": str(path), "sha256": self.observed[path]}


def decode(data: bytes, size: tuple[int, int], label: str) -> Image.Image:
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        require(image.format == "PNG", f"Not PNG: {label}")
        require(image.size == size, f"Unexpected size {image.size}: {label}")
        require(image.mode in ("RGB", "RGBA"), f"Unsupported mode {image.mode}: {label}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), f"Nonopaque pixels: {label}")
        # Fully opaque RGBA -> RGB drops alpha only, preserving RGB values.
        return image.convert("RGB")


def write_json(path: Path, value: dict) -> dict:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as handle:
        handle.write(data)
    return {"path": str(path), "sha256": sha(data)}


def save_png(path: Path, image: Image.Image) -> dict:
    require(not path.exists(), f"Refusing overwrite: {path}")
    image.save(path, format="PNG")
    data = path.read_bytes()
    return {"path": str(path), "sha256": sha(data), "width": image.width, "height": image.height}


def main() -> None:
    require(len(sys.argv) == 1, "No arguments supported; inputs are this tile's plan and layout record")
    inputs = Inputs()
    inputs.read(SCRIPT, text=True)
    plan = inputs.json(PLAN)
    layout = inputs.json(LAYOUT)
    require(plan.get("tile", {}).get("row") == 8 and plan["tile"].get("column") == 9 and layout.get("tile") == TILE, "Wrong tile")
    require(plan.get("deliveryTilePixels") == [SIZE, SIZE], "Wrong delivery dimensions")
    require(plan.get("assembledBeforeOuterCrop") == [EXTENT, EXTENT], "Wrong extended dimensions")
    require((plan.get("core"), plan.get("halo"), plan.get("adjacentOverlap")) == (CORE, HALO, 230), "Wrong overlap geometry")
    require(layout.get("globalPixelRectXYWH") == [32768, 28672, SIZE, SIZE], "Wrong global coordinates")
    inputs.read(LAYOUT, plan["layoutRecord"]["sha256"], text=True)
    patches = plan.get("patches", [])
    expected_ids = {f"r{r + 1:02}_c{c + 1:02}" for r in range(4) for c in range(4)}
    require(len(patches) == 16 and {p.get("id") for p in patches} == expected_ids, "Need exactly 16 unique patches")

    # Validate everything before creating an output version. Missing patches or
    # mismatched records fail here and can never produce a completed candidate.
    source_images = {}
    sources = []
    for patch in sorted(patches, key=lambda p: (p["row"], p["column"])):
        ident = patch["id"]
        r, c = patch["row"], patch["column"]
        require(type(r) is int and type(c) is int and 0 <= r < 4 and 0 <= c < 4, f"Invalid coordinates: {ident}")
        require(ident == f"r{r + 1:02}_c{c + 1:02}", f"ID/coordinate mismatch: {ident}")
        require(patch.get("outputFile"), f"Missing selected output path: {ident}")
        native_path = mapped_path(patch["outputFile"])
        record_path = native_path.with_suffix(".record.json")
        record = inputs.json(record_path)
        require(record.get("schemaVersion") == 4, f"Unsupported record schema: {ident}")
        native_bytes = inputs.read(native_path, record["nativeSha256"])
        require(mapped_path(record.get("file", "")).resolve() == native_path.resolve(), f"Record points elsewhere: {ident}")
        require(mapped_path(record.get("nativeFile", "")).resolve() == native_path.resolve(), f"Native record points elsewhere: {ident}")
        require(record.get("sha256") == record["nativeSha256"] == record.get("toolOutputSha256"), f"Native/output SHA mismatch: {ident}")
        require(record.get("nativePixels") == [NATIVE, NATIVE] and (record.get("width"), record.get("height")) == (NATIVE, NATIVE), f"Wrong recorded dimensions: {ident}")
        require(record.get("resampled") is False and record.get("finalArtUpscaled") is False, f"Not documented native detail: {ident}")
        require(patch["fullCanvasBox"] == [c * CORE, r * CORE, c * CORE + NATIVE, r * CORE + NATIVE], f"Guide box mismatch: {ident}")
        image = decode(native_bytes, (NATIVE, NATIVE), ident)
        source_images[(r, c)] = image

        evidence = record.get("evidence", {})
        bound_text = []
        receipt_path = mapped_path(evidence["file"])
        receipt = inputs.json(receipt_path, evidence["sha256"])
        bound_text.append(inputs.identity(receipt_path))
        original_request_path = mapped_path(patch["request"])
        original_request = inputs.json(original_request_path)
        bound_text.append(inputs.identity(original_request_path))
        effective_request = original_request
        preflight = None
        if record.get("preflightEvidence"):
            preflight_ref = record["preflightEvidence"]
            preflight_path = mapped_path(preflight_ref["file"])
            preflight = inputs.json(preflight_path, preflight_ref["sha256"])
            bound_text.append(inputs.identity(preflight_path))
            inputs.read(original_request_path, preflight.get("originalRequestSha256", preflight["requestSha256"]), text=True)
            request_path = mapped_path(preflight["requestSnapshot"])
            effective_request = inputs.json(request_path, preflight["requestSha256"])
            bound_text.append(inputs.identity(request_path))
            require(mapped_path(preflight.get("originalRequestPath", preflight.get("requestPath"))).resolve() == original_request_path.resolve(), f"Original request path mismatch: {ident}")
        require(receipt.get("request") == effective_request, f"Receipt/effective request mismatch: {ident}")
        require(original_request["prompt"] == effective_request["prompt"], f"Effective prompt differs: {ident}")
        require([ref["path"] for ref in record["submittedImages"]] == effective_request["referenced_image_paths"], f"Actual reference paths mismatch: {ident}")
        require(record["toolCall"]["referenced_image_paths"] == effective_request["referenced_image_paths"], f"Tool call path mismatch: {ident}")
        require(record["references"] == record["submittedImages"], f"Reference lists inconsistent: {ident}")
        require(record.get("promptFile") and record.get("promptSha256"), f"Missing prompt identity: {ident}")
        prompt_path = mapped_path(record["promptFile"])
        prompt_bytes = inputs.read(prompt_path, record["promptSha256"], text=True)
        require(prompt_bytes.decode("utf-8-sig") == effective_request["prompt"], f"Prompt text mismatch: {ident}")
        bound_text.append(inputs.identity(prompt_path))

        derived_ref = record["editBefore"]["record"]
        derived_path = mapped_path(derived_ref["file"])
        inputs.json(derived_path, derived_ref["sha256"])
        bound_text.append(inputs.identity(derived_path))

        # Only the explicit style alias is allowed. All current references must
        # match their historical SHA; no missing source or mismatched SHA is skipped.
        reference_status = []
        for ref in record.get("references", []):
            path = mapped_path(ref["path"])
            status = "current_bytes_match"
            if not path.is_file() and path == PROJECT / "designs/guild-ui-v2/source/guild-overview.png":
                require(ref["sha256"] == STYLE_SHA, f"Unknown style identity: {ident}")
                path = PROJECT / "designs/gameplay-ui/04-guild.png"
                status = "identical_sha_verified_at_retained_style_alias"
            observed = sha(inputs.read(path, ref["sha256"]))
            reference_status.append({"recorded": ref, "resolvedPath": str(path), "currentSha256": observed, "status": status})
        require(record["references"][0]["sha256"] == patch["guideSha256"], f"Plan guide hash mismatch: {ident}")
        require(mapped_path(record["references"][0]["path"]).resolve() == mapped_path(patch["guide"]).resolve(), f"Plan guide path mismatch: {ident}")
        if preflight:
            require([(x["path"], x["sha256"]) for x in preflight["references"]] ==
                    [(x["path"], x["sha256"]) for x in record["references"]], f"Preflight actual reference hashes mismatch: {ident}")
        for original_path, actual_ref in zip(original_request["referenced_image_paths"], record["references"], strict=True):
            if original_path != actual_ref["path"]:
                require(mapped_path(original_path) == PROJECT / "designs/guild-ui-v2/source/guild-overview.png" and
                        mapped_path(actual_ref["path"]) == PROJECT / "designs/gameplay-ui/04-guild.png" and
                        actual_ref["sha256"] == STYLE_SHA, f"Unexplained request reference change: {ident}")
        sources.append({
            "id": ident, "row": r, "col": c,
            "native": inputs.identity(native_path), "record": inputs.identity(record_path),
            "generationRecord": record, "requestResponsePrompt": bound_text,
            "referenceVerification": reference_status,
            "nativeCoreLTRB": [HALO, HALO, HALO + CORE, HALO + CORE],
            "corePasteXY": [c * CORE, r * CORE],
        })

    bottom_ref = layout["bottomConstraint"]["core"]
    bottom_path = mapped_path(bottom_ref["file"])
    require(bottom_path.name == "r09_c09.png" and bottom_path.parent.name == "r09_c09_repair_v6", "Bottom must be selected r09_c09 repair_v6")
    require(bottom_ref.get("sha256") == BOTTOM_SHA, "Bottom layout binding changed; review before assembling")
    bottom = decode(inputs.read(bottom_path, BOTTOM_SHA), (SIZE, SIZE), "bottom r09_c09 repair_v6")
    inputs.unchanged()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    version = WORK / "versions" / f"hard-core-{stamp}"
    version.mkdir(parents=True, exist_ok=False)
    qa_dir, provenance_dir = version / "qa", version / "provenance"
    qa_dir.mkdir()
    provenance_dir.mkdir()

    # Partition overlaps at the exact core boundary. Outermost patches retain
    # their outside halo; no resize, color shift, registration, or feathering.
    extended = Image.new("RGB", (EXTENT, EXTENT))
    for source in sources:
        r, c = source["row"], source["col"]
        box = (0 if c == 0 else HALO, 0 if r == 0 else HALO,
               NATIVE if c == 3 else HALO + CORE, NATIVE if r == 3 else HALO + CORE)
        xy = (c * CORE + box[0], r * CORE + box[1])
        extended.paste(source_images[(r, c)].crop(box), xy)
        source["extendedOwnership"] = {"sourceCropLTRB": list(box), "pasteXY": list(xy)}
    candidate = extended.crop((HALO, HALO, HALO + SIZE, HALO + SIZE))
    for (r, c), image in source_images.items():
        require(candidate.crop((c * CORE, r * CORE, (c + 1) * CORE, (r + 1) * CORE)).tobytes()
                == image.crop((HALO, HALO, HALO + CORE, HALO + CORE)).tobytes(), "Core pixel identity failed")

    candidate_info = save_png(version / f"{TILE}.png", candidate)
    extended_info = save_png(version / "extended-context.png", extended)
    evidence_items = []

    def evidence(name: str, image: Image.Image, metadata: dict) -> dict:
        item = {"id": name, "status": "pending_visual_review", "passed": None,
                "pixelScale": "1:1", "resized": False, "artifact": save_png(qa_dir / f"{name}.png", image), **metadata}
        evidence_items.append(item)
        return item

    # Six entire internal seams; each has four contiguous, unresized segments.
    # No lines or labels are drawn into evidence pixels. Coordinates live in JSON.
    seam_groups = []
    for axis in ("vertical", "horizontal"):
        for k in range(1, 4):
            coordinate = k * CORE
            segment_ids = []
            for segment in range(4):
                start, end = segment * SEGMENT, (segment + 1) * SEGMENT
                box = ((coordinate - HALF_STRIP, start, coordinate + HALF_STRIP, end)
                       if axis == "vertical" else (start, coordinate - HALF_STRIP, end, coordinate + HALF_STRIP))
                ident = f"internal-{axis}-{coordinate}-segment-{segment + 1:02}"
                evidence(ident, candidate.crop(box), {"kind": "internal_seam_segment", "axis": axis,
                         "seamCoordinate": coordinate, "candidateCropLTRB": list(box), "fullSeamRange": [start, end],
                         "source": candidate_info})
                segment_ids.append(ident)
            seam_groups.append({"id": f"{axis}-{coordinate}", "segments": segment_ids,
                                "coverage": [0, SIZE], "status": "pending_visual_review", "passed": None})
    for r in range(1, 4):
        for c in range(1, 4):
            x, y = c * CORE, r * CORE
            box = (x - HALF_STRIP, y - HALF_STRIP, x + HALF_STRIP, y + HALF_STRIP)
            evidence(f"internal-junction-r{r:02}-c{c:02}", candidate.crop(box), {
                "kind": "internal_four_patch_junction", "candidateXY": [x, y],
                "candidateCropLTRB": list(box), "source": candidate_info})

    # The bottom edge uses the real selected neighbor core, never its old halo.
    bottom_identity = inputs.identity(bottom_path)
    for segment in range(4):
        start, end = segment * SEGMENT, (segment + 1) * SEGMENT
        image = Image.new("RGB", (SEGMENT, 2 * HALF_STRIP))
        image.paste(candidate.crop((start, SIZE - HALF_STRIP, end, SIZE)), (0, 0))
        image.paste(bottom.crop((start, 0, end, HALF_STRIP)), (0, HALF_STRIP))
        evidence(f"external-bottom-r09_c09-segment-{segment + 1:02}", image, {
            "kind": "external_neighbor_edge_segment", "tiles": [TILE, "r09_c09"],
            "boundaryYInEvidence": HALF_STRIP, "fullEdgeRange": [start, end],
            "sources": [{"identity": candidate_info, "cropLTRB": [start, SIZE - HALF_STRIP, end, SIZE]},
                        {"identity": bottom_identity, "cropLTRB": [start, 0, end, HALF_STRIP]}]})

    qa = write_json(qa_dir / "index.json", {
        "tile": TILE, "createdAtUtc": now(), "formalAccepted": False,
        "status": "evidence_generated_not_visually_reviewed", "artAcceptance": "pending",
        "candidate": candidate_info, "internalSeams": seam_groups, "internalJunctionCount": 9,
        "externalEdges": {"bottom": {"neighbor": bottom_identity, "coverage": [0, SIZE], "passed": None,
                                     "status": "pending_visual_review"},
                          "top": {"status": "pending_neighbor_and_review", "passed": None},
                          "left": {"status": "pending_neighbor_and_review", "passed": None},
                          "right": {"status": "pending_neighbor_and_review", "passed": None}},
        "externalFourTileJunctions": {"status": "pending_neighbors_and_review", "passed": None},
        "evidence": evidence_items,
        "limitations": ["Prepared evidence is not an inspection result.", "Inspect all listed PNGs at original pixels.",
                        "Hard core cuts may contain geometry and material discontinuities requiring redraw.",
                        "Layout, navigation, recent camera clarity, and client runtime are not validated."],
    })

    # Save exact text bytes, not image backups. These preserve historical model,
    # request, response and source records even after authorized future cleanup.
    snapshots = []
    for path, data in sorted(inputs.texts.items(), key=lambda item: str(item[0]).lower()):
        snapshot = provenance_dir / f"{sha(data)}-{path.name}"
        if not snapshot.exists():
            with snapshot.open("xb") as handle:
                handle.write(data)
        snapshots.append({"source": str(path), "sha256": sha(data), "snapshot": str(snapshot)})
    inputs.unchanged()
    assembly = write_json(version / "assembly.json", {
        "schemaVersion": 1, "tile": TILE, "appearance": "tianyong_festival", "version": version.name,
        "createdAtUtc": now(), "purpose": "candidate_assembly_pending_review", "formalAccepted": False,
        "status": "complete_candidate_pending_visual_review", "plan": inputs.identity(PLAN),
        "layoutRecord": inputs.identity(LAYOUT), "script": inputs.identity(SCRIPT),
        "nativeSourceCount": 16, "nativeDimensions": [NATIVE, NATIVE], "grid": [4, 4],
        "step": CORE, "overlap": 230, "halo": HALO, "extendedDimensions": [EXTENT, EXTENT],
        "coreCropLTRB": [HALO, HALO, HALO + SIZE, HALO + SIZE], "globalCoreLTRB": [32768, 28672, 36864, 32768],
        "worldRect": plan["tile"]["worldRect"],
        "method": {"name": "hard_core_pixel_ownership", "resized": False, "upscaled": False,
                   "resampling": "none", "blending": "none", "blendWidthPixels": 0,
                   "registration": "none", "colorCorrection": "none", "geometryRepair": "none",
                   "corePixelsEqualSelectedNativeCores": True,
                   "extendedHaloRole": "work_in_progress_context_not_authoritative_neighbor_core",
                   "seamlessClaim": False, "singleNative4KClaim": False},
        "sources": sources, "textSnapshots": snapshots, "textLineEndingEquivalence": inputs.line_ending_equivalence,
        "outputs": {"candidate": candidate_info, "extended": extended_info},
        "qa": qa, "bottomNeighborUsedOnlyForEvidence": bottom_identity,
        "sharedFilesModified": False, "sourcesDeleted": False,
        "actualModel": None, "actualQuality": None,
        "modelEvidenceScope": "Consult each preserved generation record; assembly does not infer a backend version.",
    })
    try:
        inputs.unchanged()
    except Exception as error:
        write_json(version / "ABORTED.json", {"status": "STALE_FAIL", "formalAccepted": False, "reason": str(error)})
        raise
    result = write_json(version / "result.json", {
        "tile": TILE, "formalAccepted": False, "status": "candidate_pending_visual_review",
        "candidate": candidate_info, "assembly": assembly, "qa": qa,
        "technicalScope": "16 source records and native bytes verified; copied core pixels exact; no visual acceptance",
        "completedAtUtc": now(), "doNotPromoteWithoutReview": True,
    })
    print(json.dumps({"versionDirectory": str(version), "candidate": candidate_info, "assembly": assembly,
                      "qa": qa, "result": result, "formalAccepted": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
