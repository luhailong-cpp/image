#!/usr/bin/env python3
"""Rearrange two independently reviewed eight-pose sheets; never change poses."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from PIL import Image

from process_roster import SHEETS, bounds, load_processor, DEFAULT_PROCESSOR, sha, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=SHEETS, required=True)
    parser.add_argument("--first", type=Path, required=True, help="Eight poses for the first direction named in --kind.")
    parser.add_argument("--second", type=Path, required=True)
    parser.add_argument("--first-rows", type=int, choices=(2, 4), default=4)
    parser.add_argument("--first-cols", type=int, choices=(2, 4), default=2)
    parser.add_argument("--second-rows", type=int, choices=(2, 4), default=4)
    parser.add_argument("--second-cols", type=int, choices=(2, 4), default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records, groups = [], []
    processor = load_processor(DEFAULT_PROCESSOR)
    for which, direction in zip(("first", "second"), SHEETS[args.kind]):
        path = getattr(args, which).resolve()
        rows, cols = getattr(args, which + "_rows"), getattr(args, which + "_cols")
        if rows * cols != 8:
            raise ValueError("Each source must contain exactly eight row-major poses")
        raw = Image.open(path).convert("RGBA")
        cw, ch = raw.width // cols, raw.height // rows
        if min(cw, ch) < 64 or max(cw, ch) / min(cw, ch) > 1.03:
            raise ValueError(f"Each source cell must be nearly square: {path}, {cw, ch}")
        clean = processor.remove_bg_magenta(raw.copy(), 50, 80)
        if cols * cw < raw.width and bounds(clean.crop((cols * cw, 0, raw.width, raw.height))):
            raise ValueError(f"Visible subject in excluded column remainder: {path}")
        if rows * ch < raw.height and bounds(clean.crop((0, rows * ch, raw.width, raw.height))):
            raise ValueError(f"Visible subject in excluded row remainder: {path}")
        cells, boxes = [], []
        for index in range(8):
            x, y = index % cols * cw, index // cols * ch
            box = [x, y, x + cw, y + ch]
            cells.append(raw.crop(box))
            boxes.append(box)
        groups.append(cells)
        records.append({"direction": direction, "path": str(path), "sha256": sha(path), "native_size": list(raw.size),
                        "source_grid": [cols, rows], "native_cell_size": [cw, ch], "row_major_source_boxes": boxes})
        upstream = path.with_suffix(".assembly.json")
        if upstream.is_file():
            provenance = json.loads(upstream.read_text(encoding="utf-8"))
            if provenance.get("output_sha256") != records[-1]["sha256"]:
                raise ValueError(f"Upstream assembly provenance does not match source pixels: {path}")
            records[-1].update(upstream_assembly=provenance, upstream_assembly_sha256=sha(upstream))
    cell = max(max(record["native_cell_size"]) for record in records)
    output = Image.new("RGBA", (cell * 4, cell * 4), (255, 0, 255, 255))
    for group_index, cells in enumerate(groups):
        cw, ch = records[group_index]["native_cell_size"]
        scale = cell / max(cw, ch)
        records[group_index]["uniform_raw_cell_scale"] = scale
        records[group_index]["output_cell_size"] = [cell, cell]
        for pose, crop in enumerate(cells):
            width, height = round(cw * scale), round(ch * scale)
            if crop.size != (width, height):
                crop = crop.resize((width, height), Image.Resampling.LANCZOS)
            index = group_index * 8 + pose
            output.paste(crop, (index % 4 * cell + (cell - width) // 2,
                                index // 4 * cell + (cell - height) // 2))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output)
    write_json(args.output.with_suffix(".assembly.json"), {"version": 12, "operation": "row-major grid rearrangement; isotropic raw-cell normalization only",
               "output_path": str(args.output.resolve()), "output_sha256": sha(args.output), "output_size": list(output.size),
               "output_grid": [4, 4], "direction_order": SHEETS[args.kind], "sources": records,
               "new_poses_generated_by_script": False, "mirror_or_interpolation": False})
    print(f"Assembled {args.kind}: {args.output} ({output.width} x {output.height}); original sources recorded")


if __name__ == "__main__":
    main()
