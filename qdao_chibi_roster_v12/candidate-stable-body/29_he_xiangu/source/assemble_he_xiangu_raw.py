#!/usr/bin/env python3
"""Assemble He Xiangu raw candidates by exact whole-cell rearrangement only."""
from __future__ import annotations
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(r"E:\work\image\qdao_chibi_roster_v12")
OUT = BASE / "candidate-stable-body" / "29_he_xiangu" / "source"
FORMAL = BASE / "29_he_xiangu"
FIXES = BASE / "review" / "he_xiangu_idle_fixes"
EXPECTED_MANIFEST = "91fa33a20c7223de4a40b1cf601c1e886ce4284aa62a5c694f5f6f4c0d71fd86"
CELL = 443
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
PAIRS = {"s_e": ("S", "E"), "n_w": ("N", "W"), "ne_sw": ("NE", "SW"), "nw_se": ("NW", "SE")}
ROTATE = {"N", "NE", "S", "SW"}
FIX_CELL_SHA = {
    "E": "2e0603a1af1704e9321fd13c24cb95252112156f9de9bb40c462f4d92d3d1ab2",
    "W": "da8b6c8d53790aaf852345022c814071f26decd54935cd0078ddf68129181116",
}
CONTACT_REVIEW = {
    "N": "Original 01: anatomical left front foot is on image-left; image-right right foot trails with its sole visible. Original 05 reverses these legs.",
    "NE": "Original 01: near anatomical RIGHT leg trails toward image-bottom-left with visible sole; far LEFT boot is ahead toward image-right/up. Original 05 has near RIGHT thigh/boot forward and the LEFT leg trailing.",
    "S": "Original 01: anatomical LEFT foot is forward on image-right, RIGHT arm forward on image-left. Original 05 reverses both.",
    "SW": "Original 01: near anatomical LEFT thigh crosses in front toward image-left/down; near LEFT hand trails and far RIGHT arm advances. Original 05 has the far RIGHT leg ahead and near LEFT leg behind.",
    "E": "Retained original 01: near anatomical RIGHT leg is forward and near RIGHT arm trails.",
    "SE": "Retained original 01: near anatomical RIGHT thigh crosses ahead; near RIGHT arm trails, opposite arm advances.",
    "W": "Retained original 01: far anatomical RIGHT leg is forward; near LEFT arm advances.",
    "NW": "Retained original 01: far anatomical RIGHT foot is forward toward image-left/up; near LEFT leg trails.",
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rgba_sha(image):
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()

def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def checked(path, expected):
    path = Path(path)
    if not path.is_file() or sha(path) != expected:
        raise ValueError(f"Missing or changed source: {path}")
    return path

def box(index, cols=4):
    x, y = index % cols * CELL, index // cols * CELL
    return (x, y, x + CELL, y + CELL)

def preserve(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if sha(src) != sha(dst):
        raise ValueError(f"Copy changed bytes: {src}")

def provenance_refs(value, found):
    if isinstance(value, dict):
        for pathkey, hashkey in [
            ("path", "sha256"), ("source_path", "source_sha256"),
            ("basis_source", "basis_sha256"), ("output_path", "output_sha256"),
            ("prompt_file", "prompt_sha256")
        ]:
            p, h = value.get(pathkey), value.get(hashkey)
            if isinstance(p, str) and isinstance(h, str) and len(h) == 64:
                found[(str(Path(p)), h)] = None
        for child in value.values():
            provenance_refs(child, found)
    elif isinstance(value, list):
        for child in value:
            provenance_refs(child, found)

def main():
    assert OUT.resolve().is_relative_to((BASE / "candidate-stable-body" / "29_he_xiangu").resolve())
    OUT.mkdir(parents=True, exist_ok=True)
    prov = OUT / "provenance"
    prov.mkdir(exist_ok=True)
    snapshot = prov / "original-manifest.json"
    if snapshot.exists():
        checked(snapshot, EXPECTED_MANIFEST)
    else:
        preserve(checked(FORMAL / "manifest.json", EXPECTED_MANIFEST), snapshot)
    manifest = json.loads(snapshot.read_text(encoding="utf-8"))
    refs = {}
    provenance_refs(manifest["sources"], refs)
    upstream = []
    for p, h in sorted(refs):
        checked(p, h)
        upstream.append({"path": p, "sha256": h, "verified": True})
    write_json(prov / "upstream-files-sha256.json", upstream)

    # Preserve the exact five manifest-selected inputs, including old E/W idle.
    inputs = {}
    for kind, info in manifest["sources"].items():
        src = checked(info["path"], info["sha256"])
        copy = prov / "manifest-inputs" / f"{kind}.png"
        preserve(src, copy)
        im = Image.open(copy).convert("RGBA")
        expected_size = (1772, 886) if kind == "idle" else (1772, 1772)
        if im.size != expected_size or info["native_cell_size"] != [443, 443]:
            raise ValueError(f"Unexpected native geometry for {kind}: {im.size}")
        inputs[kind] = (im, src, copy, info)

    fix_inputs = {}
    for direction in ("E", "W"):
        src = checked(FIXES / direction / "idle-cell-443.png", FIX_CELL_SHA[direction])
        gp = FIXES / direction / "generated-source.json"
        generated = json.loads(gp.read_text(encoding="utf-8"))
        checked(generated["original_path"], generated["original_sha256"])
        checked(FIXES / direction / "idle-native.png", generated["original_sha256"])
        for name in ("idle-native.png", "idle-cell-443.png", "prompt.txt", "generated-source.json",
                     "reference-source.json", "qc.json"):
            preserve(FIXES / direction / name, prov / "idle-fixes" / direction / name)
        image = Image.open(src).convert("RGBA")
        if image.size != (443, 443):
            raise ValueError("Replacement idle must already be a whole 443-square cell")
        fix_inputs[direction] = (image, src, generated)

    all_frames = []
    output_sources = {}
    contact_cells = {}
    for kind, dirs in PAIRS.items():
        raw, original, preserved, original_info = inputs[kind]
        sheet = Image.new("RGBA", raw.size)
        frame_map = []
        for direction_index, direction in enumerate(dirs):
            shift = 4 if direction in ROTATE else 0
            for new_index in range(8):
                old_index = (new_index + shift) % 8
                source_box = box(direction_index * 8 + old_index)
                output_box = box(direction_index * 8 + new_index)
                cell = raw.crop(source_box)
                sheet.paste(cell, output_box[:2])  # no mask: preserve RGBA bytes
                record = {
                    "direction": direction, "output_phase": new_index + 1,
                    "source_phase": old_index + 1, "cycle_rotation_frames": shift,
                    "source_path": str(original), "source_sha256": original_info["sha256"],
                    "preserved_source_path": str(preserved),
                    "source_crop_box": list(source_box), "output_cell_box": list(output_box),
                    "whole_cell_size": [443, 443], "whole_cell_scale": 1.0,
                    "source_crop_rgba_sha256": rgba_sha(cell),
                    "output_cell_rgba_sha256": rgba_sha(sheet.crop(output_box)),
                    "pixel_identical": sheet.crop(output_box).tobytes() == cell.tobytes(),
                }
                if not record["pixel_identical"]:
                    raise ValueError("Whole-cell rearrangement changed a pixel")
                frame_map.append(record)
                all_frames.append({"sheet": kind, **record})
                if new_index in (0, 4):
                    contact_cells[(direction, new_index + 1)] = cell
        path = OUT / f"{kind}.png"
        # A direction pair unaffected by the plan remains byte-for-byte identical.
        if all(direction not in ROTATE for direction in dirs):
            preserve(preserved, path)
        else:
            sheet.save(path)
        reopened = Image.open(path).convert("RGBA")
        if reopened.tobytes() != sheet.tobytes():
            raise ValueError("Saved sheet differs from assembled RGBA pixels")
        assembly = {
            "version": 12,
            "operation": "exact whole 443x443 source cells; selected COMPLETE eight-frame cycles rotated by four; no rendering or resizing",
            "output_path": str(path), "output_sha256": sha(path),
            "output_size": list(sheet.size), "output_grid": [4, 4],
            "direction_order": list(dirs), "original_manifest_snapshot": str(snapshot),
            "original_manifest_sha256": EXPECTED_MANIFEST,
            "sources": [{"path": str(original), "sha256": original_info["sha256"],
                         "preserved_path": str(preserved), "native_size": list(raw.size),
                         "upstream_manifest_source_key": kind}],
            "frames": frame_map,
            "new_poses_generated_by_script": False, "per_frame_body_fit": False,
            "mirrored_frames": False, "repeated_or_interpolated_poses": False,
        }
        write_json(path.with_suffix(".assembly.json"), assembly)
        output_sources[kind] = {"path": str(path), "sha256": sha(path), "grid": [4, 4],
                                "native_cell_size": [443, 443], "direction_order": list(dirs)}

    raw, original, preserved, original_info = inputs["idle"]
    idle = raw.copy()
    idle_frames = []
    for i, direction in enumerate(DIRECTIONS):
        dest = box(i)
        if direction in fix_inputs:
            cell, src, generation = fix_inputs[direction]
            cell_box = (0, 0, 443, 443)
            source_hash = FIX_CELL_SHA[direction]
            source_preserved = prov / "idle-fixes" / direction / "idle-cell-443.png"
        else:
            cell, src = raw.crop(dest), original
            cell_box, source_hash = dest, original_info["sha256"]
            source_preserved, generation = preserved, None
        idle.paste(cell, dest[:2])
        record = {
            "direction": direction, "source_path": str(src), "source_sha256": source_hash,
            "preserved_source_path": str(source_preserved),
            "source_crop_box": list(cell_box), "output_cell_box": list(dest),
            "whole_cell_size": [443, 443], "whole_cell_scale": 1.0,
            "source_crop_rgba_sha256": rgba_sha(cell),
            "output_cell_rgba_sha256": rgba_sha(idle.crop(dest)),
            "pixel_identical": idle.crop(dest).tobytes() == cell.tobytes(),
            "replacement": direction in fix_inputs,
        }
        if generation:
            record["imagegen_source"] = generation
        if not record["pixel_identical"]:
            raise ValueError("Idle insertion changed pixels")
        idle_frames.append(record)
        all_frames.append({"sheet": "idle", **record})
    path = OUT / "idle.png"
    idle.save(path)
    if Image.open(path).convert("RGBA").tobytes() != idle.tobytes():
        raise ValueError("Saved idle differs from assembled RGBA pixels")
    write_json(path.with_suffix(".assembly.json"), {
        "version": 12, "operation": "replace E/W only with whole authored 443x443 idle cells; keep other six cells exact",
        "output_path": str(path), "output_sha256": sha(path), "output_size": list(idle.size),
        "output_grid": [4, 2], "direction_order": list(DIRECTIONS),
        "original_manifest_snapshot": str(snapshot), "original_manifest_sha256": EXPECTED_MANIFEST,
        "basis_source": str(original), "basis_sha256": original_info["sha256"],
        "frames": idle_frames, "new_poses_generated_by_script": False,
        "per_frame_body_fit": False, "mirrored_frames": False, "interpolation": False
    })
    output_sources["idle"] = {"path": str(path), "sha256": sha(path), "grid": [4, 2],
                              "native_cell_size": [443, 443], "direction_order": list(DIRECTIONS)}
    phase_plan = {
        "target_first_contact": "anatomical RIGHT",
        "rotation_mapping": {d: [((i + (4 if d in ROTATE else 0)) % 8) + 1 for i in range(8)] for d in DIRECTIONS},
        "independent_original_contact_review": CONTACT_REVIEW,
        "review_basis": "Formal manifest paired-sheet native cells 01 and 05 viewed again; no reliance on filename-only left/right labels",
        "retained_motion_limit": "Existing high-knee/back-kick intermediate art is unchanged; phase normalization does not claim a new natural walk.",
    }
    write_json(OUT / "phase-plan.json", phase_plan)
    write_json(OUT / "cell-source-map.json", all_frames)
    write_json(OUT / "candidate-sources.json", {
        "character_id": "29_he_xiangu", "stage": "raw_assembly_only_not_processed_or_published",
        "original_manifest_sha256": EXPECTED_MANIFEST,
        "sources": output_sources, "frame_map": "cell-source-map.json", "phase_plan": "phase-plan.json",
        "upstream_inventory": str(prov / "upstream-files-sha256.json"),
        "original_manifest_snapshot": str(snapshot),
        "checks": {"walk_cells_identical": 64, "idle_cells_identical_to_selected_source": 8,
                   "upstream_files_verified": len(upstream), "native_idle_replacements": ["E", "W"],
                   "whole_cell_resize_operations_in_this_script": 0,
                   "mirror_operations": 0, "interpolation_operations": 0, "new_art_operations": 0,
                   "formal_resources_written": False},
    })
    # Diagnostic contact board; raw cells are displayed without any art edits.
    board = Image.new("RGB", (1772, 1852), "#e8e3d9")
    draw = ImageDraw.Draw(board)
    for row in range(4):
        for half in range(2):
            direction = DIRECTIONS[row * 2 + half]
            for side, phase in enumerate((1, 5)):
                x, y = (half * 2 + side) * 443, row * 463
                cell = contact_cells[(direction, phase)].convert("RGB")
                board.paste(cell, (x, y + 20))
                old_phase = phase_plan["rotation_mapping"][direction][phase - 1]
                draw.text((x + 8, y + 5), f"{direction} new{phase:02} <- old{old_phase:02}", fill="black")
    board.save(OUT / "contact-01-05-review.jpg", quality=88)
    write_json(OUT / "assembly-script-sha256.json", {"path": str(Path(__file__).resolve()), "sha256": sha(__file__)})
    print(json.dumps({"status": "assembled", "output": str(OUT), "walk_cells_checked": 64,
                      "idle_cells_checked": 8, "upstream_files_verified": len(upstream),
                      "rotated_directions": sorted(ROTATE), "sources": output_sources}, ensure_ascii=False))

if __name__ == "__main__":
    main()

