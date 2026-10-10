#!/usr/bin/env python3
"""Transpose eight authored phase-by-view sheets into directional walking grids.

Inputs: phase 01 through 08, each a frozen pose seen from eight directions in
four columns and two rows: N NE E SE / S SW W NW. Outputs: walk-DIR.png, each
four columns and two rows of phases 01..08. This rearranges existing pixels;
it never draws, mirrors, repeats, or interpolates a walking pose.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

from process_roster import DEFAULT_PROCESSOR, DIRECTIONS, bounds, load_processor, sha, write_json


def load_phase(path, phase, processor):
    path = path.resolve()
    with Image.open(path) as opened:
        original_size, original_mode = list(opened.size), opened.mode
        raw = opened.convert("RGBA")
    cw, ch = raw.width // 4, raw.height // 2
    if min(cw, ch) < 64 or max(cw, ch) / min(cw, ch) > 1.03:
        raise ValueError(f"Phase {phase:02d}: expected 4 columns x 2 rows of nearly square cells; got {raw.size}")
    clean = processor.remove_bg_magenta(raw.copy(), 50, 80)
    if 4 * cw < raw.width and bounds(clean.crop((4 * cw, 0, raw.width, raw.height))):
        raise ValueError(f"Phase {phase:02d}: visible subject in excluded right grid remainder")
    if 2 * ch < raw.height and bounds(clean.crop((0, 2 * ch, raw.width, raw.height))):
        raise ValueError(f"Phase {phase:02d}: visible subject in excluded bottom grid remainder")
    record = {"phase": phase, "path": str(path), "sha256": sha(path),
              "native_size": original_size, "native_mode": original_mode,
              "source_grid": [4, 2], "native_cell_size": [cw, ch],
              "source_direction_order": list(DIRECTIONS),
              "unused_outer_remainder_px": [raw.width % 4, raw.height % 2]}
    upstream = path.with_suffix(".assembly.json")
    if upstream.is_file():
        provenance = json.loads(upstream.read_text(encoding="utf-8"))
        if provenance.get("output_sha256") != record["sha256"]:
            raise ValueError(f"Phase {phase:02d}: upstream provenance does not match source pixels")
        record.update(upstream_assembly=provenance, upstream_assembly_sha256=sha(upstream))
    cells = {}
    for view, direction in enumerate(DIRECTIONS):
        box = [view % 4 * cw, view // 4 * ch, (view % 4 + 1) * cw, (view // 4 + 1) * ch]
        visible = bounds(clean.crop(box))
        if visible is None:
            raise ValueError(f"Phase {phase:02d}/{direction}: empty view cell")
        if visible[0] <= 0 or visible[1] <= 0 or visible[2] >= cw or visible[3] >= ch:
            raise ValueError(f"Phase {phase:02d}/{direction}: visible subject touches its source cell boundary")
        crop = raw.crop(box)
        cells[direction] = (crop, {"phase": phase, "direction": direction,
                                  "source_view_index": view, "source_crop_box": box,
                                  "source_crop_size": [cw, ch],
                                  "source_crop_rgba_sha256": hashlib.sha256(crop.tobytes()).hexdigest()})
    return record, cells


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", action="append", type=Path, required=True,
                        help="Repeat exactly eight times, in chronological phase 01..08 order.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--directions", nargs="+", choices=DIRECTIONS, default=list(DIRECTIONS),
                        help="Output these standard directions only; the source cell order is always fixed.")
    parser.add_argument("--processor", type=Path, default=DEFAULT_PROCESSOR,
                        help="Installed sprite skill used only for read-only source containment checks.")
    args = parser.parse_args()
    if len(args.phase) != 8:
        parser.error("Exactly eight original phase sheets are required; missing phases cannot be duplicated.")
    if len(set(args.directions)) != len(args.directions):
        parser.error("--directions must not repeat a direction")
    source_paths = [path.resolve() for path in args.phase]
    if len(set(source_paths)) != 8:
        parser.error("Every phase must reference its own authored sheet; a path cannot be repeated.")
    output_dir = args.output_dir.resolve()
    processor = load_processor(args.processor)
    sources, groups = [], []
    for phase, path in enumerate(source_paths, 1):
        record, cells = load_phase(path, phase, processor)
        sources.append(record)
        groups.append(cells)
    if len({source["sha256"] for source in sources}) != 8:
        raise ValueError("At least two entire phase sheets have identical bytes; provide all eight authored phases")
    # Normalize raw-cell geometry, never subject bounding boxes. One isotropic
    # factor is used for every view of a given native sheet, yielding the same
    # normalized cell scale across all 64 views. Unequal aspect is padded, not stretched.
    cell = max(max(source["native_cell_size"]) for source in sources)
    for source in sources:
        cw, ch = source["native_cell_size"]
        scale = cell / max(cw, ch)
        scaled_size = [round(cw * scale), round(ch * scale)]
        source.update(uniform_raw_cell_scale=scale, normalized_cell_size=[cell, cell],
                      resized_cell_size=scaled_size,
                      cell_padding_xy=[(cell - scaled_size[0]) // 2, (cell - scaled_size[1]) // 2])
    rendered, records = {}, {}
    for direction in args.directions:
        canvas = Image.new("RGBA", (cell * 4, cell * 2), (255, 0, 255, 255))
        frame_records = []
        for phase_index, (source, views) in enumerate(zip(sources, groups)):
            crop, frame_record = views[direction]
            scaled_size = tuple(source["resized_cell_size"])
            if crop.size != scaled_size:
                crop = crop.resize(scaled_size, Image.Resampling.LANCZOS)
            px = phase_index % 4 * cell + source["cell_padding_xy"][0]
            py = phase_index // 4 * cell + source["cell_padding_xy"][1]
            canvas.paste(crop, (px, py))
            frame_record.update(source_path=source["path"], source_sha256=source["sha256"],
                                source_native_size=source["native_size"],
                                uniform_raw_cell_scale=source["uniform_raw_cell_scale"],
                                output_cell_box=[phase_index % 4 * cell, phase_index // 4 * cell,
                                                 (phase_index % 4 + 1) * cell, (phase_index // 4 + 1) * cell],
                                resized_cell_size=list(scaled_size), output_paste_xy=[px, py])
            frame_records.append(frame_record)
        rendered[direction] = canvas
        records[direction] = frame_records
    # Finish validation and rendering before creating output files. Do not
    # delete other directions when the caller requests a diagnostic subset.
    for direction in rendered:
        target = output_dir / f"walk-{direction}.png"
        if target in source_paths:
            raise ValueError(f"Output must not overwrite an original phase sheet: {target}")
    output_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for direction, canvas in rendered.items():
        output = output_dir / f"walk-{direction}.png"
        canvas.save(output)
        record = {"version": 12, "operation": "phase-by-view transpose; isotropic raw-cell geometry normalization only",
                  "output_path": str(output), "output_sha256": sha(output), "output_size": list(canvas.size),
                  "output_grid": [4, 2], "direction": direction, "output_phase_order": list(range(1, 9)),
                  "source_direction_order": list(DIRECTIONS), "sources": sources, "frames": records[direction],
                  "new_poses_generated_by_script": False, "per_frame_body_fit": False,
                  "mirrored_frames": False, "repeated_or_interpolated_poses": False,
                  "resolution_note": "Reassembled export geometry is derived; native generation sizes are listed per source."}
        write_json(output.with_suffix(".assembly.json"), record)
        files.append({"direction": direction, "path": str(output), "sha256": record["output_sha256"]})
    report = {"version": 12, "status": "transposed_pending_directional_qc_and_visual_review",
              "input_phase_count": 8, "input_view_count_per_phase": 8, "output_directions": args.directions,
              "source_direction_order": list(DIRECTIONS), "output_phase_order": list(range(1, 9)),
              "output_cell_size": [cell, cell], "output_grid": [4, 2],
              "cell_geometry_strategy": "one normalization factor per native sheet shared by its eight views; no pose fitting",
              "sources": sources, "files": files,
              "visual_requirement": "Each input must freeze one true gait phase across eight views; every output needs eight real phases and a coherent loop."}
    write_json(output_dir / "phase-transpose.json", report)
    print(json.dumps({key: report[key] for key in ("status", "input_phase_count", "output_directions", "output_cell_size")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
