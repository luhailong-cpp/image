#!/usr/bin/env python3
"""Private, opt-in exporter for 01_ice_sword_girl. No AI or client writes.

Default invocation is a read-only dry run. --write materializes the planned
outputs; --overwrite is separately required to replace differing output bytes.
All generated artifacts and atomic temporary files stay inside this role root.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import uuid

sys.dont_write_bytecode = True
from PIL import Image, ImageChops, ImageDraw

ROLE_ID = "01_ice_sword_girl"
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
BASELINE = REPO.parent / "mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV13" / ROLE_ID
CONFIG = REPO / "config/image-generation.json"
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
CANVAS = 1024
GROUND = 942
SCHEMA = 1


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def guarded(path: Path) -> Path:
    resolved = path.resolve()
    if ROOT.name != ROLE_ID or not resolved.is_relative_to(ROOT):
        raise ValueError(f"Output escaped the authorized role directory: {resolved}")
    return resolved


def relative(path: Path) -> str:
    return guarded(path).relative_to(ROOT).as_posix()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def png_bytes(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=False)
    return stream.getvalue()


def file_record(path: Path, inspect_image: bool = False) -> dict:
    data = path.read_bytes()
    record = {
        "path": str(path.resolve()),
        "sha256": sha(data),
        "bytes": len(data),
        "modifiedAtUtc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
    }
    if inspect_image:
        with Image.open(io.BytesIO(data)) as image:
            record.update(size=list(image.size), mode=image.mode, format=image.format)
    return record


def components(mask: Image.Image) -> dict:
    """Eight-connected alpha>8 components. Flags only: nothing is removed."""
    width, height = mask.size
    remaining = bytearray(mask.tobytes())
    found = []
    for start in range(len(remaining)):
        if not remaining[start]:
            continue
        remaining[start] = 0
        stack = [start]
        count = 0
        left = right = start % width
        top = bottom = start // width
        while stack:
            index = stack.pop()
            y, x = divmod(index, width)
            count += 1
            left, right = min(left, x), max(right, x)
            top, bottom = min(top, y), max(bottom, y)
            for ny in range(max(0, y - 1), min(height, y + 2)):
                row = ny * width
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    neighbor = row + nx
                    if remaining[neighbor]:
                        remaining[neighbor] = 0
                        stack.append(neighbor)
        found.append({"pixels": count, "bboxXyxyExclusive": [left, top, right + 1, bottom + 1]})
    found.sort(key=lambda component: component["pixels"], reverse=True)
    small = [component for component in found[1:] if component["pixels"] <= 16]
    return {
        "connectivity": 8,
        "threshold": "alpha > 8",
        "count": len(found),
        "largest": found[0] if found else None,
        "detachedComponents": found[1:],
        "smallDetachedAtMost16PixelsCount": len(small),
        "smallDetachedPixels": sum(component["pixels"] for component in small),
        "interpretation": "Flags may be valid hair, fingers, ornaments or detached artifacts. Human review required; no cleanup performed.",
    }


def image_scan(image: Image.Image) -> dict:
    alpha = image.getchannel("A")
    histogram = alpha.histogram()
    mask = alpha.point(lambda value: 255 if value > 8 else 0)
    width, height = image.size
    boundary = sum(mask.crop((0, 0, width, 1)).histogram()[1:])
    boundary += sum(mask.crop((0, height - 1, width, height)).histogram()[1:])
    boundary += sum(mask.crop((0, 1, 1, height - 1)).histogram()[1:])
    boundary += sum(mask.crop((width - 1, 1, width, height - 1)).histogram()[1:])
    # Possible magenta contamination is reported, never keyed or recolored.
    rgba = image.tobytes()
    magenta_count = 0
    for index in range(0, len(rgba), 4):
        r, g, b, a = rgba[index:index + 4]
        if a > 8 and r > 150 and b > 150 and g < min(r, b) * 0.65:
            magenta_count += 1
    bounds = mask.getbbox()
    return {
        "size": [width, height],
        "mode": image.mode,
        "alphaExtrema": list(alpha.getextrema()),
        "transparentPixels": histogram[0],
        "opaquePixels": histogram[255],
        "partlyTransparentPixels": sum(histogram[1:255]),
        "alphaGt8BboxXyxyExclusive": list(bounds) if bounds else None,
        "alphaGt8LowestRow": bounds[3] - 1 if bounds else None,
        "alphaGt8CanvasBoundaryPixels": boundary,
        "possibleMagentaPixels": magenta_count,
        "possibleMagentaRule": "alpha>8, r>150, b>150, g<0.65*min(r,b); flag only",
        "components": components(mask),
        "decodedRgbaSha256": sha(image.tobytes()),
    }


def premultiplied_channels(image: Image.Image) -> tuple:
    r, g, b, alpha = image.split()
    return (ImageChops.multiply(r, alpha), ImageChops.multiply(g, alpha),
            ImageChops.multiply(b, alpha), alpha)


def adjacent_difference(first: Image.Image, second: Image.Image) -> dict:
    differences = [ImageChops.difference(a, b) for a, b in zip(
        premultiplied_channels(first), premultiplied_channels(second))]
    maximum = differences[0]
    total_absolute = 0
    for difference in differences:
        maximum = ImageChops.lighter(maximum, difference)
        total_absolute += sum(value * count for value, count in enumerate(difference.histogram()))
    histogram = maximum.histogram()
    pixel_count = first.width * first.height
    union = ImageChops.lighter(first.getchannel("A"), second.getchannel("A"))
    visible_union = sum(union.histogram()[9:])
    changed = sum(histogram[1:])
    bounds = maximum.getbbox()
    return {
        "changedPixelsPremultipliedRgba": changed,
        "changedCanvasFraction": changed / pixel_count,
        "meanAbsolutePremultipliedChannelDifference0To255": total_absolute / (pixel_count * 4),
        "alphaGt8UnionPixels": visible_union,
        "differenceBboxXyxyExclusive": list(bounds) if bounds else None,
        "identicalDecodedRgba": first.tobytes() == second.tobytes(),
        "interpretation": "Pixel change or unique SHA does not prove independent poses, correct gait or visual approval.",
    }


def baseline_audit(now: str) -> dict:
    records = []
    for direction in ("E", "SE"):
        for frame in (1, 5, 9, 13):
            path = BASELINE / "walk" / direction / f"{frame:02d}.png"
            record = file_record(path, True)
            with Image.open(path) as image:
                alpha = image.convert("RGBA").getchannel("A")
                bounds = alpha.point(lambda a: 255 if a > 8 else 0).getbbox()
                record["alphaGt8BboxXyxyExclusive"] = list(bounds) if bounds else None
            records.append(record)
    return {
        "schemaVersion": SCHEMA, "characterId": ROLE_ID, "auditedAtUtc": now,
        "scope": "Only E/SE frames 01,05,09,13 of this character; read-only client baseline.",
        "appearance": file_record(BASELINE / "appearance.json"),
        "samples": records,
        "clientWritten": False, "clientStarted": False,
    }


def reference_records(submitted: dict) -> list:
    records = []
    for value in submitted.get("referenced_image_paths", []) or []:
        path = Path(value).resolve()
        if not (path.is_relative_to(REPO) or path.is_relative_to(BASELINE)):
            records.append({"path": str(path), "inspected": False,
                            "reason": "Outside this repository or this character client baseline."})
        elif path.is_file():
            records.append(file_record(path, True))
        else:
            records.append({"path": str(path), "inspected": False, "reason": "Not present at export time."})
    return records


def checkerboard(size: tuple[int, int], cell: int = 16) -> Image.Image:
    image = Image.new("RGBA", size, (224, 227, 233, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=(199, 205, 214, 255))
    return image


def contact_sheet(direction: str, frames: list[dict], images: list[Image.Image]) -> Image.Image:
    cell, label_height, columns = 256, 26, 4
    rows = (len(images) + columns - 1) // columns
    result = Image.new("RGB", (columns * cell, rows * (cell + label_height)), "#202631")
    draw = ImageDraw.Draw(result)
    for index, (frame, image) in enumerate(zip(frames, images)):
        x = (index % columns) * cell
        y = (index // columns) * (cell + label_height)
        draw.text((x + 8, y + 6), f"{direction} {frame['frame']:02d}  | fixed ground y={GROUND}", fill="white")
        preview = checkerboard((cell, cell))
        preview.alpha_composite(image.resize((cell, cell), Image.Resampling.LANCZOS))
        result.paste(preview.convert("RGB"), (x, y + label_height))
        line_y = y + label_height + round(GROUND / CANVAS * cell)
        draw.line((x, line_y, x + cell - 1, line_y), fill="#ee4d63", width=1)
    return result


HTML = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>01 冰剑少女 · __DIRECTION__ 跑步检查</title>
<style>
body{margin:24px;background:#171d27;color:#eef2f8;font:15px system-ui,sans-serif}h1{font-size:24px}
button,select,input{font:inherit}button,select{padding:8px 12px;border:1px solid #536075;border-radius:6px;background:#273245;color:white}
.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:20px 0}.views{display:flex;gap:36px;align-items:flex-start;flex-wrap:wrap}
.stage{position:relative;background:repeating-conic-gradient(#c7cdd6 0 25%,#e0e3e9 0 50%) 0/24px 24px;overflow:hidden}
.stage img{display:block;width:100%;height:100%}.ground{position:absolute;left:0;right:0;top:91.9921875%;border-top:1px solid #ed3d59;pointer-events:none}
.root{position:absolute;width:8px;height:8px;border:1px solid #e63353;border-radius:50%;left:calc(50% - 5px);top:calc(91.9921875% - 5px);pointer-events:none}
.small{width:197px;height:197px}.large{width:512px;height:512px}p{max-width:950px;line-height:1.6}.note{color:#ffcc77}
input[type=range]{width:300px;max-width:80vw}details{max-width:1000px}pre{white-space:pre-wrap;word-break:break-word}label{display:flex;align-items:center;gap:6px}
</style>
<h1>01 冰剑少女 · __DIRECTION__ 跑步检查</h1>
<p class="note">__STATUS__。尺寸、SHA 和像素差异仅为技术检查；此预览没有自动美术通过结论，也没有客户端接入或运行验收。</p>
<div class="controls"><button id="play">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button>
<select id="speed"><option value="30">正常 30 ms/帧</option><option value="120">慢速 120 ms/帧</option></select>
<label><input id="grid" type="checkbox" checked>固定地面线与根点</label><label><input id="slider" type="range" min="0" value="0"><span id="counter"></span></label></div>
<div class="views"><div><p>197 px 整画布 · 静态标定参考</p><div class="stage small"><img id="small" alt="标定显示大小"><div class="ground"></div><div class="root"></div></div></div>
<div><p>512 px 整画布 · 放大检查</p><div class="stage large"><img id="large" alt="放大检查"><div class="ground"></div><div class="root"></div></div></div></div>
<p>地面线固定在原画布 y=942，根点 x=512。腾空时脚底应离开此线。197 px 来自现有客户端静态标定注释，不代表已实测当前游戏窗口。键盘左右方向键逐帧，空格暂停或播放。</p>
<details><summary>导出约束</summary><pre id="metadata"></pre></details>
<script>
const data=__DATA__;
const frames=data.frames.map(f=>({...f,image:new Image()}));for(const f of frames)f.image.src=f.dataUrl;
const q=id=>document.getElementById(id);let index=0,playing=true,last=performance.now(),accumulator=0;
q('slider').max=frames.length-1;q('metadata').textContent=JSON.stringify(data.contract,null,2);
function show(){const f=frames[index];q('small').src=q('large').src=f.dataUrl;q('slider').value=index;q('counter').textContent=`${String(f.frame).padStart(2,'0')} / ${frames.length} 帧`;}
function pause(){playing=false;q('play').textContent='播放';accumulator=0;}
function step(delta){pause();index=(index+delta+frames.length)%frames.length;show();}
q('play').onclick=()=>{playing=!playing;q('play').textContent=playing?'暂停':'播放';accumulator=0;last=performance.now();};
q('prev').onclick=()=>step(-1);q('next').onclick=()=>step(1);q('slider').oninput=()=>{pause();index=Number(q('slider').value);show();};
q('speed').onchange=()=>{accumulator=0;last=performance.now();};q('grid').onchange=()=>document.querySelectorAll('.ground,.root').forEach(e=>e.style.display=q('grid').checked?'':'none');
document.onkeydown=e=>{if(e.code==='ArrowLeft'){e.preventDefault();step(-1);}if(e.code==='ArrowRight'){e.preventDefault();step(1);}if(e.code==='Space'){e.preventDefault();q('play').click();}};
function tick(now){if(playing){accumulator+=Math.min(now-last,250);const duration=Number(q('speed').value),steps=Math.floor(accumulator/duration);if(steps){index=(index+steps)%frames.length;accumulator-=steps*duration;show();}}last=now;requestAnimationFrame(tick);}
show();requestAnimationFrame(tick);
</script></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direction", choices=DIRECTIONS, default="E")
    parser.add_argument("--version", default="v1", help="Source suffix, e.g. v1; selection is explicit, never newest-file guessing.")
    parser.add_argument("--allow-partial", action="store_true", help="Permit fewer than 16 inputs for research preview, with incomplete labels.")
    parser.add_argument("--write", action="store_true", help="Write artifacts inside this role directory. Otherwise dry-run only.")
    parser.add_argument("--overwrite", action="store_true", help="Permit replacing differing generated artifact bytes; never changes source PNG/prompt/receipt.")
    args = parser.parse_args()
    if not re.fullmatch(r"v[1-9][0-9]*", args.version):
        parser.error("--version must be v1, v2, ...")
    now = timestamp()
    source_dir = guarded(ROOT / "generation" / args.direction)
    source_paths = [(n, source_dir / f"{n:02d}-{args.version}.png") for n in range(1, 17)]
    missing = [n for n, path in source_paths if not path.is_file()]
    if missing and not args.allow_partial:
        raise ValueError(f"Missing frames {missing}; no artifacts written. Use --allow-partial only for explicitly incomplete research previews.")
    source_paths = [(n, path) for n, path in source_paths if path.is_file()]
    if not source_paths:
        raise ValueError("No source frames are present; no artifacts written.")
    config_data = CONFIG.read_bytes()
    config = json.loads(config_data)
    config_snapshot = {"path": str(CONFIG), "sha256": sha(config_data), "readAtUtc": now, "contents": config,
                       "limitation": "Snapshot read at export time. It does not prove these settings were actually submitted at generation time."}
    output_plan: dict[Path, bytes] = {}
    frames, images, native_sizes = [], [], set()
    contract = {
        "characterId": ROLE_ID, "direction": args.direction, "canvas": [CANVAS, CANVAS],
        "rootPxTopLeftCoordinates": [512, 942.08], "previewGroundLineY": GROUND,
        "proposedRuntimePivotBottomLeft": [0.5, 0.08], "proposedPixelsPerUnit": 104,
        "frameDurationMs": 30, "slowPreviewFrameDurationMs": 120,
        "completeCycleDurationMs": 480, "frameCountPresent": len(source_paths), "missingFrames": missing,
        "exportTransform": "Same whole-square-canvas LANCZOS downsample to 1024; no crop, translation, per-frame bbox scaling, lowest-foot grounding, mirroring or pose interpolation.",
        "cleanup": "None. Alpha/fringe/component flags are inspection evidence only.",
        "visualApproval": "not_assessed_by_tool", "clientIntegrated": False, "clientRuntimeVerified": False,
    }
    for frame, source_path in source_paths:
        prompt_path = source_path.with_suffix(".prompt.txt")
        receipt_path = source_path.with_suffix(".receipt.json")
        if not prompt_path.is_file() or not receipt_path.is_file():
            raise ValueError(f"Prompt and receipt are both required for {source_path.name}; no artifacts written.")
        source_bytes = source_path.read_bytes()
        receipt_bytes = receipt_path.read_bytes()
        receipt = json.loads(receipt_bytes)
        with Image.open(io.BytesIO(source_bytes)) as original:
            original.load()
            if original.format != "PNG" or original.mode != "RGBA":
                raise ValueError(f"{source_path.name}: native source must be PNG RGBA, got {original.format}/{original.mode}.")
            if original.width != original.height or original.width < CANVAS:
                raise ValueError(f"{source_path.name}: source {original.size} cannot supply a native square >=1024 without enlargement or cropping.")
            native_size = original.size
            native_sizes.add(native_size)
            source_alpha = original.getchannel("A")
            if source_alpha.getextrema()[0] != 0 or source_alpha.getbbox() is None:
                raise ValueError(f"{source_path.name}: missing transparent background or empty alpha.")
            exported = original.copy() if original.size == (CANVAS, CANVAS) else original.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)
        target = guarded(ROOT / "candidate" / "walk" / args.direction / f"{frame:02d}.png")
        exported_bytes = png_bytes(exported)
        output_plan[target] = exported_bytes
        submitted = receipt.get("submittedParameters") or {}
        provenance = {
            "schemaVersion": SCHEMA, "characterId": ROLE_ID, "direction": args.direction, "frame": frame,
            "source": file_record(source_path, True), "prompt": file_record(prompt_path),
            "receipt": {**file_record(receipt_path), "contents": receipt},
            "generationTimeAsReported": receipt.get("generatedAt"), "exportedAtUtc": now,
            "configurationSnapshotAtExport": config_snapshot,
            "submittedParameters": submitted,
            "actualModel": receipt.get("actualModel"), "actualQuality": receipt.get("actualQuality"),
            "actualModelQualityEvidence": "Only explicit receipt values are copied. Null means unconfirmed; config or prompt does not establish the actual model/quality.",
            "references": reference_records(submitted),
            "output": {"path": relative(target), "sha256": sha(exported_bytes), "size": [CANVAS, CANVAS], "mode": "RGBA"},
            "derivation": {"operation": "whole_canvas_LANCZOS_downsample" if native_size != (CANVAS, CANVAS) else "whole_canvas_lossless_reencode",
                           "sourceCanvas": list(native_size), "targetCanvas": [CANVAS, CANVAS],
                           "scale": CANVAS / native_size[0], "translation": [0, 0], "crop": None,
                           "bboxNormalization": False, "perFrameLowestAlphaGrounding": False, "mirrored": False, "poseInterpolation": False},
            "technicalScan": image_scan(exported), "visualApproval": "not_assessed_by_tool",
        }
        provenance_path = source_path.with_suffix(".provenance.json")
        output_plan[guarded(provenance_path)] = json_bytes(provenance)
        frames.append({"frame": frame, "source": relative(source_path), "output": provenance["output"],
                       "provenance": relative(provenance_path), "technicalScan": provenance["technicalScan"]})
        images.append(exported)
    if len(native_sizes) != 1:
        raise ValueError(f"Different native canvas sizes {sorted(native_sizes)} would use different transforms; resolve explicitly before export. No artifacts written.")
    pairs = [(index, index + 1) for index in range(len(frames) - 1)]
    if not missing:
        pairs.append((len(frames) - 1, 0))
    adjacency = [{"fromFrame": frames[a]["frame"], "toFrame": frames[b]["frame"],
                  "consecutiveNumberedFrames": frames[b]["frame"] == frames[a]["frame"] + 1 or (frames[a]["frame"] == 16 and frames[b]["frame"] == 1),
                  "loopSeam": a == len(frames) - 1 and b == 0,
                  **adjacent_difference(images[a], images[b])} for a, b in pairs]
    validation = {"schemaVersion": SCHEMA, "generatedAtUtc": now, "contract": contract,
                  "frames": frames, "adjacentDifferences": adjacency,
                  "uniqueDecodedRgbaCount": len({frame["technicalScan"]["decodedRgbaSha256"] for frame in frames}),
                  "technicalStatus": "complete_inputs_inspected" if not missing else "incomplete_research_inputs_inspected",
                  "visualStatus": "not_assessed_by_tool", "note": "No metric here establishes independent AI poses, running quality, stable grip, correct anatomy or artistic acceptance."}
    preview_data = {"contract": contract, "frames": [
        {"frame": frame["frame"], "dataUrl": "data:image/png;base64," + base64.b64encode(
            output_plan[guarded(ROOT / frame["output"]["path"])]).decode("ascii")}
        for frame in frames]}
    status = "完整16帧输入，等待人工动态验收" if not missing else f"研究预览：仅{len(frames)}/16帧，缺帧 {missing}，不构成完整跑步循环"
    html = HTML.replace("__DIRECTION__", args.direction).replace("__STATUS__", status).replace(
        "__DATA__", json.dumps(preview_data, ensure_ascii=False).replace("</", "<\\/"))
    output_plan[guarded(ROOT / "preview" / f"{args.direction}.html")] = html.encode("utf-8")
    output_plan[guarded(ROOT / "preview" / f"{args.direction}-contact-sheet.png")] = png_bytes(contact_sheet(args.direction, frames, images))
    output_plan[guarded(ROOT / "input" / "baseline-samples.json")] = json_bytes(baseline_audit(now))
    output_plan[guarded(ROOT / "validation" / f"technical-{args.direction}.json")] = json_bytes(validation)
    output_plan[guarded(ROOT / "export" / f"{args.direction}.manifest.json")] = json_bytes({
        "schemaVersion": SCHEMA, "generatedAtUtc": now, "contract": contract,
        "files": [{"frame": frame["frame"], **frame["output"], "provenance": frame["provenance"]} for frame in frames],
        "validation": f"validation/technical-{args.direction}.json", "preview": f"preview/{args.direction}.html",
        "visualReview": "not_assessed_by_tool", "clientIntegrated": False, "clientRuntimeVerified": False})
    collisions = [relative(path) for path, data in output_plan.items() if path.exists() and path.read_bytes() != data]
    summary = {"mode": "write" if args.write else "dry_run_no_files_written", "characterId": ROLE_ID,
               "direction": args.direction, "frames": len(frames), "missingFrames": missing,
               "nativeCanvas": list(next(iter(native_sizes))), "plannedOutputCount": len(output_plan),
               "differingExistingOutputs": collisions, "visualStatus": "not_assessed_by_tool"}
    if not args.write:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if collisions and not args.overwrite:
        raise ValueError("Existing generated outputs differ; review the dry run then explicitly use --overwrite: " + ", ".join(collisions))
    # Preflight every output before any mutation. Atomic temp files use each
    # destination's own directory; no TMP, user-cache, client or shared index.
    for path in output_plan:
        guarded(path)
        if path.exists() and not path.is_file():
            raise ValueError(f"Output is not a regular file: {path}")
    written = []
    for path, data in output_plan.items():
        guarded(path)
        if path.is_file() and path.read_bytes() == data:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = guarded(path.with_name(path.name + ".tmp-" + uuid.uuid4().hex))
        try:
            temporary.write_bytes(data)
            os.replace(temporary, path)
        finally:
            if temporary.is_file():
                temporary.unlink()
        written.append(relative(path))
    summary["written"] = written
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
