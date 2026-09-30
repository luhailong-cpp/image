#!/usr/bin/env python3
"""Non-destructive export of explicitly selected combat poses.

Defaults to a read-only preflight. --preview-dir writes an isolated technical
preview; --publish adds runtime frames and derived receipts only when all
preflight checks pass. No mode overwrites an existing file.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image


BATCH = Path(__file__).resolve().parents[1]
ACTIONS = {"hit": 6, "attack": 12, "cast": 16}
DIRECTIONS = ("E", "W")
CANVAS = 1024
COMMON_SCALE = 0.88
ROOT_X, ROOT_Y = 512, 942
REFERENCE = {"E": "staging/attack-E-01-v1.png", "W": "staging/cast-W-01-v1.png"}


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return result


def within(path: Path, parent: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(parent.resolve()):
        raise ValueError(f"Path escapes character directory: {path}")
    return resolved


def selected_path(value: str, character_dir: Path) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("Selection file or generationRecord path is missing")
    relative = Path(value)
    candidate = BATCH / relative if relative.parts[0] == "characters" else character_dir / relative
    result = within(candidate, character_dir)
    if not result.is_file():
        raise ValueError(f"Selected input missing: {result}")
    return result


def alpha_geometry(rgba: Image.Image) -> dict:
    alpha = np.asarray(rgba.getchannel("A"))
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        raise ValueError("No visible subject (alpha > 8)")
    top, bottom = int(ys.min()), int(ys.max())
    upper = ys < top + max(1, int((bottom - top) * 0.42))
    axis_x = float(np.median(xs[upper]))
    return {
        "visibleBBox": [int(xs.min()), top, int(xs.max()) + 1, bottom + 1],
        "upperBodyAxisX": axis_x,
        "lowestVisibleY": bottom,
        "transparentPixels": int(np.count_nonzero(alpha == 0)),
        "visiblePixels": int(len(xs)),
        "visibleTouchesEdge": bool(
            np.any(alpha[0] > 8) or np.any(alpha[-1] > 8)
            or np.any(alpha[:, 0] > 8) or np.any(alpha[:, -1] > 8)
        ),
    }


def open_native(path: Path) -> tuple[Image.Image, dict]:
    with Image.open(path) as source:
        if source.format != "PNG" or source.mode != "RGBA":
            raise ValueError(f"Expected original RGBA PNG: {path}")
        image = source.copy()
    if image.size[0] < 1024 or image.size[1] < 1024:
        raise ValueError(f"Native input smaller than 1024×1024: {path}")
    geometry = alpha_geometry(image)
    if geometry["visibleTouchesEdge"]:
        raise ValueError(f"Original visible subject touches canvas edge: {path}")
    return image, geometry


def discover_selections(character_dir: Path) -> list[Path]:
    paths = sorted(character_dir.glob("*selection.json"))
    paths += sorted((character_dir / "staging").glob("*selection.json"))
    return paths


def load_selections(character_dir: Path) -> list[dict]:
    selected = []
    seen_keys, seen_sources = set(), set()
    for path in discover_selections(character_dir):
        data = read_json(path)
        action, direction = data.get("action"), data.get("direction")
        if action not in ACTIONS or direction not in DIRECTIONS:
            raise ValueError(f"Unknown action or direction in {path}")
        frames = data.get("frames")
        if not isinstance(frames, list) or len(frames) != ACTIONS[action]:
            raise ValueError(f"Incomplete explicit selection in {path}")
        indices = [entry.get("frame") for entry in frames]
        if indices != list(range(1, ACTIONS[action] + 1)):
            raise ValueError(f"Selection frames must be ordered 1..{ACTIONS[action]}: {path}")
        for entry in frames:
            key = (action, direction, entry["frame"])
            if key in seen_keys:
                raise ValueError(f"Duplicate selected runtime slot: {key}")
            seen_keys.add(key)
            source = selected_path(entry["file"], character_dir)
            receipt = selected_path(entry["generationRecord"], character_dir)
            if source in seen_sources:
                raise ValueError(f"One native image selected for multiple poses: {source}")
            seen_sources.add(source)
            receipt_data = read_json(receipt)
            source_sha = sha_file(source)
            if receipt_data.get("sha256", "").lower() != source_sha:
                raise ValueError(f"Source/receipt SHA mismatch: {source} / {receipt}")
            if entry.get("sha256") and entry["sha256"].lower() != source_sha:
                raise ValueError(f"Source/selection SHA mismatch: {source} / {path}")
            if not (receipt_data.get("prompt") and receipt_data.get("references")):
                raise ValueError(f"Generation record lacks prompt/references: {receipt}")
            image, geometry = open_native(source)
            selected.append({
                "key": key, "image": image, "source": source, "sourceSha256": source_sha,
                "sourceReceipt": receipt, "sourceReceiptSha256": sha_file(receipt),
                "sourceRecord": receipt_data, "selection": path,
                "selectionSha256": sha_file(path), "nativeGeometry": geometry,
            })
    return selected


def reference_transforms(character_dir: Path, selected: list[dict]) -> dict:
    if not selected:
        return {}
    sizes = {entry["image"].size for entry in selected}
    if len(sizes) != 1:
        raise ValueError(f"Mixed native canvases need an explicit common transform: {sizes}")
    width, height = next(iter(sizes))
    factor = COMMON_SCALE * CANVAS / max(width, height)
    target = (round(width * factor), round(height * factor))
    if factor > 1 or target[0] >= CANVAS or target[1] >= CANVAS:
        raise ValueError("Common scale would upscale or exceed canvas")
    transforms = {}
    for direction in {entry["key"][1] for entry in selected}:
        reference = within(character_dir / REFERENCE[direction], character_dir)
        ref_image, geom = open_native(reference)
        if ref_image.size != (width, height):
            raise ValueError(f"Reference canvas differs from selected sources: {reference}")
        transforms[direction] = {
            "nativeCanvas": [width, height],
            "commonScale": COMMON_SCALE,
            "wholeCanvasFactor": factor,
            "scaledWholeCanvas": list(target),
            "offset": [
                round(ROOT_X - geom["upperBodyAxisX"] * factor),
                round(ROOT_Y - geom["lowestVisibleY"] * factor),
            ],
            "reference": reference.relative_to(BATCH).as_posix(),
            "referenceSha256": sha_file(reference),
            "referenceUpperBodyAxisX": geom["upperBodyAxisX"],
            "referenceLowestVisibleY": geom["lowestVisibleY"],
            "targetAnchor": [ROOT_X, ROOT_Y],
            "note": "One fixed transform per direction, shared by every attack/cast/hit frame. No framewise bbox fitting or recentering.",
        }
    return transforms


def export_image(image: Image.Image, transform: dict) -> tuple[Image.Image, dict]:
    # Remove only extremely faint alpha noise before and after downsampling.
    array = np.array(image)
    faint = array[:, :, 3] <= 8
    array[faint] = 0
    cleaned = Image.fromarray(array, "RGBA")
    scaled = cleaned.resize(tuple(transform["scaledWholeCanvas"]), Image.Resampling.LANCZOS)
    array = np.array(scaled)
    array[array[:, :, 3] <= 8] = 0
    scaled = Image.fromarray(array, "RGBA")
    final = Image.new("RGBA", (CANVAS, CANVAS))
    final.paste(scaled, tuple(transform["offset"]))
    geom = alpha_geometry(final)
    if geom["visibleTouchesEdge"]:
        raise ValueError("Exported subject touches canvas boundary")
    return final, geom


def derived_record(entry: dict, destination: Path, png_sha: str, transform: dict,
                   output_geom: dict, derived_at: str) -> dict:
    source = entry["sourceRecord"]
    return {
        "file": destination.relative_to(BATCH).as_posix(),
        "sha256": png_sha,
        "generatedAt": source.get("generatedAt"),
        "derivedAt": derived_at,
        "width": CANVAS, "height": CANVAS, "format": "PNG RGBA",
        "tool": "Pillow deterministic whole-canvas export",
        "route": "derived",
        "configSnapshot": source.get("configSnapshot"),
        "submittedParameters": {"model": None, "quality": None},
        "actualModel": source.get("actualModel"),
        "actualQuality": source.get("actualQuality"),
        "unverifiedReason": source.get("unverifiedReason"),
        "prompt": source.get("prompt"),
        "references": source.get("references"),
        "evidence": {
            "selection": entry["selection"].relative_to(BATCH).as_posix(),
            "selectionSha256": entry["selectionSha256"],
            "sourceGenerationRecord": entry["sourceReceipt"].relative_to(BATCH).as_posix(),
            "sourceGenerationRecordSha256": entry["sourceReceiptSha256"],
        },
        "derivedFrom": {
            "file": entry["source"].relative_to(BATCH).as_posix(),
            "sha256": entry["sourceSha256"],
            "generationRecord": entry["sourceReceipt"].relative_to(BATCH).as_posix(),
            "generationRecordSha256": entry["sourceReceiptSha256"],
        },
        "operation": {
            "kind": "whole_canvas_uniform_downsample_and_fixed_direction_anchor",
            "filter": "Pillow LANCZOS",
            "faintAlphaThreshold": 8,
            "transform": transform,
            "noFramewiseBoundingBoxScale": True,
            "noFramewiseRecentering": True,
            "noMirrorOrPoseSynthesis": True,
        },
        "nativeGeometry": entry["nativeGeometry"],
        "outputGeometry": output_geom,
        "visualApproval": "pending",
        "clientIntegration": "not_integrated",
    }


def render(selected: list[dict], transforms: dict, character_dir: Path) -> list[dict]:
    derived_at = datetime.now(timezone.utc).isoformat()
    rows = []
    output_hashes = set()
    for entry in selected:
        action, direction, frame = entry["key"]
        destination = character_dir / "runtime" / action / direction / f"{frame:02d}.png"
        receipt = character_dir / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{frame:02d}.json"
        image, geometry = export_image(entry["image"], transforms[direction])
        import io
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        png = buffer.getvalue()
        digest = sha_bytes(png)
        if digest in output_hashes:
            raise ValueError(f"Duplicate exported PNG: {entry['key']}")
        output_hashes.add(digest)
        rows.append({
            "entry": entry, "destination": destination, "receipt": receipt,
            "png": png, "record": derived_record(entry, destination, digest,
                                                 transforms[direction], geometry, derived_at),
        })
    return rows


def write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def preview_html(rows: list[dict], root: Path) -> str:
    options = []
    for action in ACTIONS:
        for direction in DIRECTIONS:
            images = [
                f"characters/{row['entry']['key'][0]}/{row['entry']['key'][1]}/{row['entry']['key'][2]:02d}.png"
                for row in rows if row["entry"]["key"][:2] == (action, direction)
            ]
            if images:
                options.append({"label": f"{action}/{direction} ({len(images)})", "images": images})
    data = json.dumps(options, ensure_ascii=False)
    return f"""<!doctype html><html lang="zh"><meta charset="utf-8">
<title>00 battle selected export preview</title>
<style>body{{font:16px system-ui;background:#14272b;color:#f6f1dd;margin:24px}}
button,select,input{{font:inherit;margin:5px}}.stage{{display:grid;place-items:center;width:540px;height:540px;
background-color:#ddd;background-image:linear-gradient(45deg,#aaa 25%,transparent 25%),
linear-gradient(-45deg,#aaa 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#aaa 75%),
linear-gradient(-45deg,transparent 75%,#aaa 75%);background-size:32px 32px;
background-position:0 0,0 16px,16px -16px,-16px 0}}
img{{width:512px;height:512px;object-fit:contain}}</style>
<h1>00 战斗动作选稿导出预览</h1><p>技术预览；尚未完成动态美术审核和客户端接入。</p>
<select id="set"></select><button id="play">播放</button><button id="stop">停止</button>
<button id="prev">上一帧</button><button id="next">下一帧</button>
<input id="frame" type="range" min="0" value="0"><span id="counter"></span>
<div class="stage"><img id="sprite"></div>
<script>const sets={data};let index=0,timer=null;const $=x=>document.getElementById(x);
sets.forEach((s,i)=>{{const o=document.createElement('option');o.value=i;o.textContent=s.label;$('set').append(o)}});
function show(){{const s=sets[+$('set').value];$('frame').max=s.images.length-1;index=Math.max(0,Math.min(index,s.images.length-1));
$('frame').value=index;$('sprite').src=s.images[index];$('counter').textContent=(index+1)+'/'+s.images.length}}
function stop(){{clearInterval(timer);timer=null}}$('set').onchange=()=>{{stop();index=0;show()}};
$('frame').oninput=()=>{{stop();index=+$('frame').value;show()}};
$('prev').onclick=()=>{{stop();index--;show()}};$('next').onclick=()=>{{stop();index++;show()}};
$('play').onclick=()=>{{stop();index=0;show();timer=setInterval(()=>{{index++;
if(index>=sets[+$('set').value].images.length){{stop();return}}show()}},90)}};
$('stop').onclick=stop;if(sets.length)show();</script></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", default="00_reference_topright_boy")
    parser.add_argument("--preview-dir", type=Path, help="New isolated directory for rendered QA preview")
    parser.add_argument("--publish", action="store_true", help="Add runtime and derived receipts, never overwrite")
    parser.add_argument("--min-publish-slots", type=int, default=50)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.character):
        raise ValueError("Invalid character ID")
    character_dir = BATCH / "characters" / args.character
    if not character_dir.is_dir():
        raise ValueError(f"Character missing: {character_dir}")
    selected = load_selections(character_dir)
    transforms = reference_transforms(character_dir, selected)
    rows = render(selected, transforms, character_dir)
    counts = {f"{a}-{d}": sum(row["entry"]["key"][:2] == (a, d) for row in rows)
              for a in ACTIONS for d in DIRECTIONS}
    print(json.dumps({"character": args.character, "selectedSlots": len(rows),
                      "counts": counts, "runtimeExists": (character_dir / "runtime").exists(),
                      "transforms": transforms, "technicalPreflight": "passed"},
                     ensure_ascii=False, indent=2))
    if args.preview_dir:
        preview = args.preview_dir.resolve()
        if preview.exists():
            raise ValueError(f"Refuse to overwrite preview directory: {preview}")
        if not preview.is_relative_to(character_dir.resolve()):
            raise ValueError("Preview directory must be inside this character directory")
        for row in rows:
            action, direction, frame = row["entry"]["key"]
            path = preview / "characters" / action / direction / f"{frame:02d}.png"
            write_new(path, row["png"])
        write_new(preview / "index.html", preview_html(rows, preview).encode("utf-8"))
        write_new(preview / "technical-report.json",
                  (json.dumps({"status": "technical_preview_only", "selectedSlots": len(rows),
                               "counts": counts, "transforms": transforms,
                               "frames": [row["record"] for row in rows]},
                              ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"Preview: {preview / 'index.html'}")
    if args.publish:
        if len(rows) < args.min_publish_slots:
            raise ValueError(f"Only {len(rows)} explicit selected slots; require {args.min_publish_slots}")
        for row in rows:
            if row["destination"].exists() or row["receipt"].exists():
                raise ValueError(f"Refuse to overwrite runtime or receipt: {row['destination']}")
        # All PNGs and records were rendered and validated before any runtime write.
        for row in rows:
            write_new(row["receipt"], (json.dumps(row["record"], ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
            write_new(row["destination"], row["png"])
        print(f"Published {len(rows)} new technical runtime candidates; visual review remains pending.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"export_selected: {exc}", file=sys.stderr)
        raise SystemExit(2)
