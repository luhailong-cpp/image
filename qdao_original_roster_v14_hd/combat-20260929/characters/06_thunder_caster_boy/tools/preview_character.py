#!/usr/bin/env python3
"""Build a six-segment offline player; never certifies visual acceptance."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from export_character import ROOT, CHARACTER, ACTIONS, DIRECTIONS, inside, local, write_new


def write_preview(destination, frames_root, technical_status="not_checked"):
    destination, frames_root = inside(destination), inside(frames_root)
    sets = []
    for action, (count, ms) in ACTIONS.items():
        for direction in DIRECTIONS:
            paths = [frames_root / action / direction / f"{n:02d}.png" for n in range(1, count + 1)]
            present = [p for p in paths if p.is_file()]
            sets.append({"name": f"{action}/{direction}", "ms": ms, "expected": count,
                         "complete": len(present) == count,
                         "frames": [{"number": int(p.stem), "url": Path(os.path.relpath(p, destination)).as_posix()} for p in present]})
    manifest = {"character": CHARACTER, "sets": sets, "technicalStatus": technical_status,
                "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}
    data = json.dumps(manifest, ensure_ascii=False).replace("<", "\\u003c")
    template = Path(__file__).with_name("player_template.html").read_text(encoding="utf-8")
    write_new(destination / "index.html", template.replace("__MANIFEST__", data).encode("utf-8"))
    write_new(destination / "player-manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--frames-root", default="runtime")
    args = parser.parse_args()
    write_preview(local(args.out), local(args.frames_root))
    print(str(local(args.out) / "index.html"))


if __name__ == "__main__":
    main()
