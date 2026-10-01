#!/usr/bin/env python3
"""Private, deterministic Lotus Healer export; no artistic approval is inferred.

Run with the bundled Python that provides Pillow. Inputs and outputs must remain
inside this character directory. --check-only validates without writing anything.
Source records may be <image>.png.generation.json or <image>.generation.json.
The script owns candidate/walk, preview, and manifest.json only. It never writes
review.json, STATUS.md, CLIENT_HANDOFF.md, shared indices, or client assets.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PureWindowsPath
import sys

from PIL import Image, ImageDraw, __version__ as PILLOW_VERSION


ROOT = Path(__file__).resolve().parent.parent
CHARACTER = "03_lotus_healer_girl"
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
FRAMES = tuple(f"{n:02d}" for n in range(1, 17))
SIZE = 1024
PIVOT = [512, 942]
ROOT_DEFINITION = {
    "canvasPixels": [SIZE, SIZE],
    "pointPixelsTopLeftOrigin": PIVOT,
    "normalizedTopLeftOrigin": [0.5, 942 / 1024],
    "normalizedBottomLeftOrigin": [0.5, 82 / 1024],
    "meaning": "fixed virtual character root and ground, NOT the lowest alpha pixel",
    "perFrameTranslation": [0, 0],
    "perFrameBoundingBoxScaling": False,
    "lowestFootAlignment": False,
    "airborneOffsets": "preserved from source whole-canvas coordinates",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def confined(value: str | Path, *, exists: bool = False) -> Path:
    """Resolve junctions/symlinks and reject every path outside this character."""
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve(strict=exists)
    if not resolved.is_relative_to(ROOT) or resolved == ROOT:
        raise ValueError(f"Path is outside the character directory: {value}")
    return resolved


def input_path(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("Every selected source must be a nonempty relative PNG path")
    if Path(value).is_absolute() or PureWindowsPath(value).drive:
        raise ValueError(f"Selections must use character-relative paths: {value}")
    if ".." in value.replace("\\", "/").split("/"):
        raise ValueError(f"Parent traversal is forbidden: {value}")
    path = confined(value, exists=True)
    if not path.is_file() or path.suffix.lower() != ".png":
        raise ValueError(f"Selected source is not a PNG file: {value}")
    return path


def load_json(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {relative(path)}")
    return value, raw


def image_facts(image: Image.Image) -> dict:
    alpha = image.getchannel("A")
    histogram = alpha.histogram()
    bounds = alpha.point(lambda a: 255 if a > 8 else 0).getbbox()
    return {
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "alphaExtrema": list(alpha.getextrema()),
        "transparentPixelCount": histogram[0],
        "nontransparentPixelCount": sum(histogram[1:]),
        "partiallyTransparentPixelCount": sum(histogram[1:255]),
        "alphaGt8Bounds": list(bounds) if bounds else None,
    }


def inspect_source(path: Path) -> dict:
    raw = path.read_bytes()
    sha = digest(raw)
    with Image.open(io.BytesIO(raw)) as original:
        original.load()
        if original.format != "PNG":
            raise ValueError(f"Source encoding is not PNG: {relative(path)}")
        if original.width != original.height or min(original.size) < SIZE:
            raise ValueError(f"Native source must be square and at least 1024: {relative(path)} {original.size}")
        if "A" not in original.getbands() and "transparency" not in original.info:
            raise ValueError(f"Source has no encoded transparency: {relative(path)}")
        facts = image_facts(original.convert("RGBA"))
        facts["originalMode"] = original.mode
        facts["format"] = original.format
        if not facts["transparentPixelCount"] or not facts["nontransparentPixelCount"]:
            raise ValueError(f"Source must contain real transparent and visible pixels: {relative(path)}")
    possible = (Path(str(path) + ".generation.json"), path.with_suffix(".generation.json"))
    records = [confined(p, exists=True) for p in possible if p.exists()]
    if not records:
        raise ValueError(f"Missing per-image source generation record: {relative(path)}")
    if len(records) > 1:
        raise ValueError(f"Ambiguous source generation records: {relative(path)}")
    record, record_raw = load_json(records[0])
    recorded_sha = record.get("sha256")
    if not isinstance(recorded_sha, str) or recorded_sha.lower() != sha:
        raise ValueError(f"Source receipt SHA does not match PNG: {relative(path)}")
    declared = record.get("native")
    if not isinstance(declared, dict) or declared.get("width") != facts["width"] or declared.get("height") != facts["height"]:
        raise ValueError(f"Receipt native dimensions do not match PNG: {relative(path)}")
    return {
        "path": relative(path), "sha256": sha, "native": facts,
        "generationRecordPath": relative(records[0]),
        "generationRecordSha256": digest(record_raw), "generationRecord": record,
    }


def atomic_write(path: Path, data: bytes) -> None:
    path = confined(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    confined(path.parent, exists=True)
    temporary = confined(path.with_name(path.name + ".export-tmp"))
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def save_json(path: Path, value: dict) -> None:
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def encode_png(image: Image.Image) -> bytes:
    target = io.BytesIO()
    image.save(target, format="PNG", compress_level=9, optimize=False)
    return target.getvalue()


def export_frame(direction: str, frame: str, source: dict) -> dict:
    raw = confined(source["path"], exists=True).read_bytes()
    if digest(raw) != source["sha256"]:
        raise ValueError(f"Source changed after validation: {source['path']}")
    record_raw = confined(source["generationRecordPath"], exists=True).read_bytes()
    if digest(record_raw) != source["generationRecordSha256"]:
        raise ValueError(f"Source receipt changed after validation: {source['path']}")
    with Image.open(io.BytesIO(raw)) as opened:
        image = opened.convert("RGBA")
        if image.size != (SIZE, SIZE):
            image = image.resize((SIZE, SIZE), resample=Image.Resampling.LANCZOS)
        facts = image_facts(image)
        output = encode_png(image)
    target = confined(f"candidate/walk/{direction}/{frame}.png")
    output_sha = digest(output)
    metadata = {
        "schemaVersion": 1, "kind": "deterministic-derived-frame",
        "characterId": CHARACTER, "direction": direction, "frame": int(frame),
        "file": relative(target), "sha256": output_sha, "output": facts,
        "derivedFrom": source,
        "operation": {
            "software": "Pillow", "version": PILLOW_VERSION,
            "name": "whole-canvas RGBA conversion and uniform downscale",
            "inputSize": [source["native"]["width"], source["native"]["height"]],
            "outputSize": [SIZE, SIZE],
            "uniformScale": SIZE / source["native"]["width"],
            "resample": "LANCZOS" if source["native"]["width"] != SIZE else "none",
            "crop": None, "translatePixels": [0, 0], "mirror": False,
            "interpolateBetweenFrames": False, "alphaPreserved": True,
            "pixelPreservation": "same pixels at 1024; whole-canvas filtered reduction above 1024",
        },
        "root": ROOT_DEFINITION,
        "visualAcceptance": "not-assessed-by-exporter",
        "clientIntegration": "not-performed-by-exporter",
    }
    atomic_write(target, output)
    record_target = confined(str(target) + ".generation.json")
    save_json(record_target, metadata)
    return {
        "direction": direction, "frame": int(frame), "path": relative(target),
        "sha256": output_sha, **facts,
        "generationRecordPath": relative(record_target),
        "generationRecordSha256": digest(record_target.read_bytes()),
        "nativeSource": {key: source[key] for key in ("path", "sha256", "native", "generationRecordPath", "generationRecordSha256")},
    }


HTML = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>03 莲花医者 · 跑步候选检查</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif}body{margin:0;background:#101b20;color:#edf3f1}main{max-width:1100px;margin:auto;padding:24px}h1{font-size:24px;margin:0 0 12px}p{line-height:1.6}.notice{background:#343023;border:1px solid #776847;padding:12px;border-radius:10px}.controls{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0;align-items:center}button,select{font:inherit;padding:8px 11px;border-radius:7px;border:1px solid #607079;background:#24353d;color:white}button:disabled{opacity:.35;cursor:not-allowed}button.active{background:#366e65}.missing{border-color:#d97777!important;color:#ff9e9e}.stage{position:relative;width:512px;height:512px;max-width:100%;background-color:#2e3b40;background-image:linear-gradient(45deg,#35474a 25%,transparent 25%),linear-gradient(-45deg,#35474a 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#35474a 75%),linear-gradient(-45deg,transparent 75%,#35474a 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0;flex:none}.stage img{position:absolute;width:100%;height:100%;inset:0}.ground{position:absolute;left:0;right:0;top:91.9921875%;border-top:1px solid #e7ad64;pointer-events:none}.root{position:absolute;left:50%;top:91.9921875%;width:13px;height:13px;transform:translate(-50%,-50%);pointer-events:none}.root:before,.root:after{content:"";position:absolute;background:#ff7171}.root:before{left:6px;top:0;width:1px;height:13px}.root:after{top:6px;left:0;height:1px;width:13px}.blank{position:absolute;inset:0;display:grid;place-items:center;text-align:center;background:#301e22;color:#ffb6b6}.viewer{display:flex;align-items:flex-start;gap:24px;flex-wrap:wrap}.status{max-width:450px;overflow-wrap:anywhere}.frames{display:grid;grid-template-columns:repeat(8,1fr);gap:6px;max-width:512px}.frames button{min-width:0;padding:8px 4px}a{color:#8de5ca}.subtle{color:#a6b9be;font-size:13px}#slider{width:min(512px,100%)}pre{white-space:pre-wrap;word-break:break-word;font-size:12px}#warning{color:#ffacac;font-weight:bold}.links{line-height:1.9}
.blank[hidden]{display:none}
.stage{height:auto!important;aspect-ratio:1}
</style><main><h1>03 莲花医者 · 跑步候选检查</h1>
<p class="notice">此页用于人工动态、慢速与逐帧检查。文件齐全或播放成功不代表美术通过。固定地面/根点为 (512, 942)，保留来源画布中的腾空与重心偏移。导出未接入客户端。</p>
<div id="directions" class="controls"></div>
<div class="controls"><button id="play" disabled>播放</button><label>速度 <select id="speed"><option value="30">正常：30 ms/帧 · 480 ms/圈</option><option value="120">慢速：120 ms/帧 · 1920 ms/圈</option></select></label><label>显示 <select id="display"><option value="512">512 px 放大检查</option><option value="128">128 px 近似游戏大小</option></select></label></div>
<p id="warning"></p><div class="viewer"><div id="stage" class="stage"><img id="sprite" alt="候选帧"><div id="blank" class="blank" hidden></div><div class="ground"></div><div class="root"></div></div><div class="status"><p id="status"></p><p class="subtle">128 px 仅是检查近似值，实际客户端显示大小尚未验证。橙线为虚拟地面，红十字为固定根点，不是本帧最低脚位置。</p><pre id="details"></pre><p id="sourceLinks" class="links"></p><p><a href="../manifest.json">技术清单</a> · <a id="contact">方向接触表</a></p></div></div>
<div class="controls"><button id="previous">上一帧</button><button id="next">下一帧</button></div><input id="slider" type="range" min="1" max="16" value="1" aria-label="逐帧"><div id="frames" class="frames"></div>
<p class="subtle">每方向必须拥有并成功读取 16 张有效候选，才能启用动态循环。方向或帧缺失时不会复制上一帧补足。</p></main>
<script id="preview-data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('preview-data').textContent),$=id=>document.getElementById(id);
let direction=data.directions.find(d=>Object.keys(data.frames[d]).length)||'E',frame=1,running=false,start=0,startFrame=1,loaded={},buttons={},frameButtons=[];
const key=f=>String(f).padStart(2,'0'),entry=()=>data.frames[direction][key(frame)],url=p=>'../'+p.split('/').map(encodeURIComponent).join('/');
function playable(){return Array.from({length:16},(_,i)=>key(i+1)).every(f=>data.frames[direction][f]&&loaded[direction+'/'+f]===true)}
function stop(){running=false;$('play').textContent='播放'}
function render(){const e=entry();$('slider').value=frame;$('status').textContent=direction+' · 第 '+frame+' / 16 帧';$('sprite').hidden=!e;$('blank').hidden=!!e;if(e){$('sprite').src=url(e.path);$('sprite').alt=direction+' frame '+frame;$('details').textContent='SHA-256\n'+e.sha256+'\n原生来源 '+e.nativeSource.native.width+' × '+e.nativeSource.native.height+'\n透明像素 '+e.transparentPixelCount+'\n根点 (512, 942) · 固定虚拟地面';$('sourceLinks').replaceChildren();for(const [label,path] of [['候选 PNG',e.path],['逐图来源',e.generationRecordPath],['原生输入',e.nativeSource.path]]){const a=document.createElement('a');a.textContent=label;a.href=url(path);a.target='_blank';$('sourceLinks').append(a,document.createElement('br'))}}else{$('blank').textContent=direction+' / '+key(frame)+' 缺帧';$('details').textContent='当前帧未导出。';$('sourceLinks').replaceChildren()}
const missing=Array.from({length:16},(_,i)=>key(i+1)).filter(f=>!data.frames[direction][f]);const failed=Array.from({length:16},(_,i)=>key(i+1)).filter(f=>loaded[direction+'/'+f]===false);$('warning').textContent=missing.length?'缺少 '+missing.join(', ')+'：动态循环已禁用。':failed.length?'图片读取失败 '+failed.join(', ')+'：动态循环已禁用。':playable()?'16 帧可播放；等待人工视觉验收。':'图片载入中，动态循环暂禁用。';$('play').disabled=!playable();if(!playable())stop();for(const d of data.directions)buttons[d].classList.toggle('active',d===direction);frameButtons.forEach((b,i)=>{b.classList.toggle('active',i+1===frame);b.classList.toggle('missing',!data.frames[direction][key(i+1)])});$('contact').href='contact-'+direction+'.png'}
for(const d of data.directions){const b=document.createElement('button');b.textContent=d+' ('+Object.keys(data.frames[d]).length+'/16)';b.onclick=()=>{stop();direction=d;frame=1;render()};buttons[d]=b;$('directions').append(b);for(const [f,e] of Object.entries(data.frames[d])){const image=new Image();image.onload=()=>{loaded[d+'/'+f]=true;render()};image.onerror=()=>{loaded[d+'/'+f]=false;render()};image.src=url(e.path)}}
for(let f=1;f<=16;f++){const b=document.createElement('button');b.textContent=key(f);b.onclick=()=>{stop();frame=f;render()};frameButtons.push(b);$('frames').append(b)}
$('play').onclick=()=>{if(running)stop();else if(playable()){running=true;start=performance.now();startFrame=frame;$('play').textContent='暂停'}};$('speed').onchange=()=>{start=performance.now();startFrame=frame};$('display').onchange=()=>{$('stage').style.width=$('display').value+'px';$('stage').style.height=$('display').value+'px'};$('slider').oninput=()=>{stop();frame=Number($('slider').value);render()};$('previous').onclick=()=>{stop();frame=(frame+14)%16+1;render()};$('next').onclick=()=>{stop();frame=frame%16+1;render()};
function tick(t){if(running){const next=((startFrame-1+Math.floor((t-start)/Number($('speed').value)))%16)+1;if(frame!==next){frame=next;render()}}requestAnimationFrame(tick)}render();requestAnimationFrame(tick);
</script></html>'''


def make_contact(direction: str, entries: dict[str, dict]) -> None:
    tile, label = 256, 26
    sheet = Image.new("RGBA", (tile * 4, (tile + label) * 4), "#172a30")
    draw = ImageDraw.Draw(sheet)
    dependencies = []
    for n, frame in enumerate(FRAMES):
        x, y = (n % 4) * tile, (n // 4) * (tile + label)
        draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill="#304249")
        entry = entries.get(frame)
        if entry:
            with Image.open(confined(entry["path"], exists=True)) as image:
                sheet.alpha_composite(image.convert("RGBA").resize((tile, tile), Image.Resampling.LANCZOS), (x, y))
            dependencies.append({"path": entry["path"], "sha256": entry["sha256"]})
        else:
            draw.text((x + 85, y + 118), "MISSING", fill="#ff9b9b")
        gy, gx = y + round(PIVOT[1] * tile / SIZE), x + tile // 2
        draw.line((x, gy, x + tile - 1, gy), fill="#e0a361", width=1)
        draw.line((gx - 5, gy, gx + 5, gy), fill="#ff7373", width=1)
        draw.line((gx, gy - 5, gx, gy + 5), fill="#ff7373", width=1)
        draw.text((x + 8, y + tile + 6), f"{direction} / {frame}" + ("  MISSING" if not entry else ""), fill="white")
    target = confined(f"preview/contact-{direction}.png")
    png = encode_png(sheet)
    atomic_write(target, png)
    save_json(confined(str(target) + ".generation.json"), {
        "schemaVersion": 1, "kind": "derived-review-contact-sheet", "file": relative(target),
        "sha256": digest(png), "derivedFrom": dependencies,
        "operation": "4x4 whole-canvas 256px thumbnails; fixed-root overlays and explicit missing cells",
        "root": ROOT_DEFINITION, "artAcceptance": "not-assessed", "notForGameUse": True,
    })


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selections", default="selections.json", help="Character-relative selection JSON")
    parser.add_argument("--check-only", action="store_true", help="Validate every source and receipt; write nothing")
    args = parser.parse_args()
    if ROOT.name != CHARACTER or ROOT.parent.name != "characters":
        raise ValueError("This private script may only run from the 03_lotus_healer_girl character directory")
    selection_path = confined(args.selections, exists=True)
    selections, selection_raw = load_json(selection_path)
    unknown_directions = set(selections) - set(DIRECTIONS)
    if unknown_directions:
        raise ValueError(f"Unknown directions: {sorted(unknown_directions)}")
    sources: dict[str, dict[str, dict]] = {d: {} for d in DIRECTIONS}
    used_paths: dict[str, str] = {}
    used_hashes: dict[str, str] = {}
    for direction in DIRECTIONS:
        selected = selections.get(direction, {})
        if not isinstance(selected, dict) or set(selected) - set(FRAMES):
            raise ValueError(f"Direction {direction} must map keys 01..16 to source paths")
        for frame in FRAMES:
            if frame not in selected:
                continue
            path = input_path(selected[frame])
            source = inspect_source(path)
            identity = direction + "/" + frame
            if source["path"] in used_paths or source["sha256"] in used_hashes:
                previous = used_paths.get(source["path"], used_hashes.get(source["sha256"]))
                raise ValueError(f"Duplicate source cannot count as an independent pose: {identity} and {previous}")
            used_paths[source["path"]] = identity
            used_hashes[source["sha256"]] = identity
            sources[direction][frame] = source
    selected_count = sum(map(len, sources.values()))
    output_paths = set()
    for direction in DIRECTIONS:
        for frame in sources[direction]:
            output_paths.add(confined(f"candidate/walk/{direction}/{frame}.png"))
            output_paths.add(confined(f"candidate/walk/{direction}/{frame}.png.generation.json"))
    for group in sources.values():
        for source in group.values():
            if confined(source["path"]) in output_paths or confined(source["generationRecordPath"]) in output_paths:
                raise ValueError(f"An output would overwrite a selected source or its receipt: {source['path']}")
    summary = {"selectedValidatedFrames": selected_count, "expectedFrames": 128,
               "byDirection": {d: len(sources[d]) for d in DIRECTIONS},
               "visualAcceptance": "not-assessed", "clientIntegration": "not-performed"}
    if args.check_only:
        print(json.dumps({"mode": "read-only-preflight", **summary}, ensure_ascii=False, indent=2))
        return 0
    if digest(selection_path.read_bytes()) != digest(selection_raw):
        raise ValueError("Selections changed during validation; retry with stable selections")
    # Preflight all output locations before writing, including existing junctions.
    for value in ("candidate/walk", "preview", "preview/index.html", "manifest.json"):
        confined(value)
    for direction in DIRECTIONS:
        confined(f"preview/contact-{direction}.png")
        confined(f"preview/contact-{direction}.png.generation.json")
        for frame in sources[direction]:
            confined(f"candidate/walk/{direction}/{frame}.png")
            confined(f"candidate/walk/{direction}/{frame}.png.generation.json")
    entries = {d: {} for d in DIRECTIONS}
    for direction in DIRECTIONS:
        for frame, source in sources[direction].items():
            entries[direction][frame] = export_frame(direction, frame, source)
        make_contact(direction, entries[direction])
    active_paths = {entry["path"] for group in entries.values() for entry in group.values()}
    physical_inventory = []
    for direction in DIRECTIONS:
        for frame in FRAMES:
            path = confined(f"candidate/walk/{direction}/{frame}.png")
            if path.exists():
                raw = path.read_bytes()
                with Image.open(io.BytesIO(raw)) as image:
                    facts = image_facts(image.convert("RGBA"))
                physical_inventory.append({"path": relative(path), "sha256": digest(raw),
                                           "selectedThisRun": relative(path) in active_paths, **facts})
    unselected = [item["path"] for item in physical_inventory if not item["selectedThisRun"]]
    manifest = {
        "schemaVersion": 1, "characterId": CHARACTER, "kind": "technical-export-inventory",
        "selections": {"path": relative(selection_path), "sha256": digest(selection_raw)},
        "tool": {"path": relative(Path(__file__).resolve()), "sha256": digest(Path(__file__).read_bytes()),
                 "pillowVersion": PILLOW_VERSION},
        **summary, "exportedSelectedFrames": len(active_paths),
        "physicalOnDiskFrameCount": len(physical_inventory),
        "unselectedExistingFramesExcludedFromPreview": unselected,
        "root": ROOT_DEFINITION,
        "timing": {"normalFrameMs": 30, "normalCycleMs": 480,
                   "slowFrameMs": 120, "slowCycleMs": 1920, "framesPerDirection": 16},
        "missing": {d: [f for f in FRAMES if f not in entries[d]] for d in DIRECTIONS},
        "frames": [e for group in entries.values() for e in group.values()],
        "physicalInventory": physical_inventory,
        "limitations": ["Technical validation does not establish pose, anatomy, grip, timing, or artistic acceptance.",
                        "Source PNG dimensions are verified; upstream native-render authenticity relies on its preserved receipt.",
                        "128px preview is an approximation, not verified client display size.",
                        "Unselected old files are retained but excluded from animation; reconcile before handoff."],
    }
    save_json(confined("manifest.json"), manifest)
    embedded = json.dumps({"directions": DIRECTIONS, "frames": entries}, ensure_ascii=False).replace("</", "<\\/")
    atomic_write(confined("preview/index.html"), HTML.replace("__DATA__", embedded).encode("utf-8"))
    print(json.dumps({"mode": "exported", **summary, "preview": str(confined("preview/index.html")),
                      "manifest": str(confined("manifest.json")), "unselectedExistingFrameCount": len(unselected)},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
