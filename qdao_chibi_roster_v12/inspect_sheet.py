#!/usr/bin/env python3
"""Inspect one authored sheet before the full eight-direction bundle is ready."""
import argparse
import json
from pathlib import Path

from process_roster import DEFAULT_PROCESSOR, DIRECTIONS, SHEETS, compose, run_sheet, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=(*SHEETS, "idle", *DIRECTIONS), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--prompt", type=Path)
    parser.add_argument("--processor", type=Path, default=DEFAULT_PROCESSOR)
    parser.add_argument("--component-padding", type=int, default=2)
    parser.add_argument("--rows", type=int, choices=(2, 4))
    parser.add_argument("--cols", type=int, choices=(2, 4))
    args = parser.parse_args()
    frames, meta, source, errors = run_sheet(args.input, args.kind, args.output_dir, args.processor,
                                            args.component_padding, args.prompt, rows=args.rows, cols=args.cols)
    preview_cols = args.cols or (2 if args.kind in DIRECTIONS else 4)
    compose(frames, preview_cols).save(args.output_dir / "inspection.png")
    write_json(args.output_dir / "source.json", source)
    print(json.dumps({"status": "failed" if errors else "passed_numeric_pending_visual",
                      "errors": errors, "directions": meta["direction_qc"],
                      "inspection": str(args.output_dir / "inspection.png")}, ensure_ascii=False))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
