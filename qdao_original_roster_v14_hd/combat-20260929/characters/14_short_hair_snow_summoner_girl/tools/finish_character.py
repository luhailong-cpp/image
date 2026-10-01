#!/usr/bin/env python3
"""Character-14-only explicit selection preflight, uniform export, and QA preview.

Default invocation is read-only. Pass exactly six selection JSON paths, relative
to the character directory (absolute character-local paths also work).
--preview-dir creates a NEW character-local technical-preview directory.
--publish creates runtime PNGs and derived receipts; never overwrites a file.
No operation fills a missing slot or grants visual/client acceptance.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image


CHARACTER = Path(__file__).resolve().parents[1]
CHARACTER_ID = "14_short_hair_snow_summoner_girl"
BATCH = CHARACTER.parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
SIZE = 1024


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def local_path(value: str | Path, must_exist: bool = True) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = BATCH / path if path.parts and path.parts[0] == "characters" else CHARACTER / path
    path = path.resolve()
    if not path.is_relative_to(CHARACTER.resolve()):
        raise ValueError(f"Path escapes this character: {value}")
    if must_exist and not path.is_file():
        raise ValueError(f"Required input missing: {path}")
    return path


def relative(path: Path) -> str:
    return path.relative_to(BATCH).as_posix()


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_object(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return data, digest(raw)


def image_info(image: Image.Image) -> dict:
    array = np.asarray(image)
    alpha = array[:, :, 3]
    ys, xs = np.where(alpha > 8)
    if not len(xs):
        raise ValueError("Image has no visible subject above alpha=8")
    if not np.any(alpha == 0):
        raise ValueError("Image has no fully transparent pixels")
    if np.any(alpha[0] > 8) or np.any(alpha[-1] > 8) or np.any(alpha[:, 0] > 8) or np.any(alpha[:, -1] > 8):
        raise ValueError("Visible subject touches canvas boundary")
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    canonical = array.copy()
    canonical[alpha == 0, :3] = 0
    # QA hashes only: do not modify the pixels being exported. Ignoring faint
    # alpha noise prevents invisible changes from making a copied pose unique.
    robust = array.copy()
    robust[alpha <= 8] = 0
    crop = robust[bbox[1]:bbox[3], bbox[0]:bbox[2]]
    return {
        "width": image.width, "height": image.height, "mode": image.mode,
        "alpha_min": int(alpha.min()), "alpha_max": int(alpha.max()),
        "transparent_pixels": int(np.count_nonzero(alpha == 0)),
        "opaque_pixels": int(np.count_nonzero(alpha == 255)),
        "visible_bbox": bbox, "visible_touches_edge": False,
        "pixel_sha256": digest(array.tobytes()),
        "visible_pixel_sha256": digest(canonical.tobytes()),
        "alpha8_pixel_sha256": digest(robust.tobytes()),
        "alpha8_horizontal_mirror_sha256": digest(robust[:, ::-1].tobytes()),
        "alpha8_crop_size": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
        "alpha8_crop_sha256": digest(crop.tobytes()),
        "alpha8_crop_horizontal_mirror_sha256": digest(crop[:, ::-1].tobytes()),
    }


def read_native(path: Path, raw: bytes) -> tuple[Image.Image, dict]:
    with Image.open(io.BytesIO(raw)) as source:
        if source.format != "PNG" or source.mode != "RGBA":
            raise ValueError(f"Expected an RGBA PNG: {path}")
        source.verify()
    with Image.open(io.BytesIO(raw)) as source:
        image = source.copy()
    if image.width != image.height or image.width < SIZE:
        raise ValueError(f"Expected a square native canvas at least 1024 pixels; no stretching/upscaling: {path}")
    return image, image_info(image)


def validate_receipt(receipt: dict, source: Path, source_sha: str, dimensions: tuple[int, int]) -> None:
    if local_path(receipt.get("file", "")) != source:
        raise ValueError(f"Receipt file does not identify selected image: {source}")
    if str(receipt.get("sha256", "")).lower() != source_sha:
        raise ValueError(f"Source/receipt SHA256 mismatch: {source}")
    for key in ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot", "submittedParameters", "evidence", "prompt", "references"):
        if key not in receipt or receipt[key] in (None, "", [], {}):
            raise ValueError(f"Receipt missing {key}: {source}")
    for key in ("actualModel", "actualQuality"):
        if key not in receipt or (receipt[key] is None and not receipt.get("unverifiedReason")):
            raise ValueError(f"Receipt lacks truthful {key} evidence or unknown reason: {source}")
    parameters = receipt["submittedParameters"]
    if not isinstance(parameters, dict) or "model" not in parameters or "quality" not in parameters:
        raise ValueError(f"Receipt must distinguish actual submitted model/quality: {source}")
    if (receipt.get("width"), receipt.get("height")) != dimensions:
        raise ValueError(f"Receipt/native dimension mismatch: {source}")
    if not isinstance(receipt["references"], list) or any(not isinstance(ref, dict) or not ref.get("path") or not ref.get("role") for ref in receipt["references"]):
        raise ValueError(f"Receipt references must contain path and role: {source}")
    local_path(receipt["prompt"])


def load_selections(paths: list[str]) -> list[dict]:
    selected, groups, sources, source_hashes = [], set(), set(), set()
    for value in paths:
        path = local_path(value)
        data, selection_sha = read_object(path)
        action, direction = data.get("action"), data.get("direction")
        if action not in ACTIONS or direction not in DIRECTIONS:
            raise ValueError(f"Unknown action/direction: {path}")
        group = (action, direction)
        if group in groups:
            raise ValueError(f"Duplicate selection group: {group}")
        groups.add(group)
        if data.get("partial") or data.get("status") == "partial":
            raise ValueError(f"Partial selection cannot be exported: {path}")
        frames = data.get("frames")
        count = ACTIONS[action][0]
        if not isinstance(frames, list) or len(frames) != count or any(not isinstance(frame, dict) for frame in frames):
            raise ValueError(f"Selection requires all {count} explicit frames: {path}")
        if [frame.get("frame") for frame in frames] != list(range(1, count + 1)):
            raise ValueError(f"Frames must be ordered 1..{count}: {path}")
        for frame in frames:
            if type(frame["frame"]) is not int:
                raise ValueError(f"Frame number must be an integer: {path}")
            source = local_path(frame.get("file", ""))
            source_bytes = source.read_bytes()
            source_sha = digest(source_bytes)
            if str(frame.get("sha256", "")).lower() != source_sha:
                raise ValueError(f"Selection SHA256 missing or mismatched: {source}")
            if source in sources or source_sha in source_hashes:
                raise ValueError(f"One source image cannot serve multiple slots: {source}")
            sources.add(source)
            source_hashes.add(source_sha)
            receipt_path = local_path(frame.get("generationRecord", ""))
            receipt, receipt_sha = read_object(receipt_path)
            image, geometry = read_native(source, source_bytes)
            validate_receipt(receipt, source, source_sha, image.size)
            selected.append({
                "action": action, "direction": direction, "frame": frame["frame"],
                "source": source, "sourceSha256": source_sha, "image": image,
                "sourceReceipt": receipt_path, "sourceReceiptSha256": receipt_sha,
                "sourceRecord": receipt, "selection": path, "selectionSha256": selection_sha,
                "nativeGeometry": geometry,
            })
    expected = {(action, direction) for action in ACTIONS for direction in DIRECTIONS}
    if groups != expected or len(selected) != 68:
        raise ValueError("Exactly six complete explicit groups and 68 slots are required")
    sizes = {entry["image"].size for entry in selected}
    if len(sizes) != 1:
        raise ValueError(f"Mixed native canvas sizes require a separately reviewed common transform: {sorted(sizes)}")
    order = {action: i for i, action in enumerate(ACTIONS)}
    return sorted(selected, key=lambda item: (order[item["action"]], DIRECTIONS.index(item["direction"]), item["frame"]))


def reject_copies(rows: list[dict], geometry_key: str) -> None:
    seen_whole, seen_crops = {}, {}
    for row in rows:
        geometry = row[geometry_key]
        label = f"{row['action']}/{row['direction']}/{row['frame']:02d}"
        keys = (geometry["alpha8_pixel_sha256"], geometry["alpha8_horizontal_mirror_sha256"])
        for kind, key in zip(("duplicate visible pixels", "horizontal mirror"), keys):
            if key in seen_whole:
                raise ValueError(f"{geometry_key}: {kind}: {seen_whole[key]} and {label}")
        crop_size = tuple(geometry["alpha8_crop_size"])
        for kind, key in (("translated duplicate", geometry["alpha8_crop_sha256"]), ("translated horizontal mirror", geometry["alpha8_crop_horizontal_mirror_sha256"])):
            crop_key = (crop_size, key)
            if crop_key in seen_crops:
                raise ValueError(f"{geometry_key}: {kind}: {seen_crops[crop_key]} and {label}")
        seen_whole[keys[0]] = label
        seen_crops[(crop_size, geometry["alpha8_crop_sha256"])] = label


def render(selected: list[dict]) -> tuple[list[dict], dict]:
    reject_copies(selected, "nativeGeometry")
    native_size = selected[0]["image"].width
    transform = {
        "nativeCanvas": [native_size, native_size], "outputCanvas": [SIZE, SIZE],
        "wholeCanvasFactor": SIZE / native_size, "offset": [0, 0],
        "filter": "Pillow LANCZOS" if native_size != SIZE else "identity",
        "sameTransformForAll68Frames": True,
        "noFramewiseBoundingBoxScale": True, "noFramewiseRecentering": True,
        "noMirrorOrPoseSynthesis": True, "noAlphaCleanup": True,
    }
    rows = []
    derived_at = datetime.now(timezone.utc).isoformat()
    for entry in selected:
        image = entry["image"]
        output = image.copy() if native_size == SIZE else image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        geometry = image_info(output)
        buffer = io.BytesIO()
        output.save(buffer, format="PNG")
        png = buffer.getvalue()
        action, direction, frame = entry["action"], entry["direction"], entry["frame"]
        destination = CHARACTER / "runtime" / action / direction / f"{frame:02d}.png"
        receipt_path = CHARACTER / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{frame:02d}.json"
        source = entry["sourceRecord"]
        record = {
            "file": relative(destination), "sha256": digest(png),
            "generatedAt": source["generatedAt"], "generatedAtEvidence": source["generatedAtEvidence"],
            "derivedAt": derived_at, "width": SIZE, "height": SIZE, "format": "PNG RGBA",
            "tool": "Pillow deterministic whole-canvas export", "route": "derived",
            "configSnapshot": source["configSnapshot"],
            "submittedParameters": {"model": None, "quality": None},
            "actualModel": source["actualModel"], "actualQuality": source["actualQuality"],
            "unverifiedReason": source.get("unverifiedReason"),
            "prompt": source["prompt"], "references": source["references"],
            "evidence": {"selection": relative(entry["selection"]), "selectionSha256": entry["selectionSha256"]},
            "derivedFrom": {
                "file": relative(entry["source"]), "sha256": entry["sourceSha256"],
                "generationRecord": relative(entry["sourceReceipt"]),
                "generationRecordSha256": entry["sourceReceiptSha256"],
            },
            "operation": {"kind": "whole_canvas_uniform_downsample", "transform": transform},
            "nativeGeometry": entry["nativeGeometry"], "outputGeometry": geometry,
            "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested",
        }
        rows.append(dict(entry, png=png, destination=destination, receipt=receipt_path, record=record, outputGeometry=geometry))
    reject_copies(rows, "outputGeometry")
    return rows, transform


def manifest(rows: list[dict], transform: dict) -> dict:
    return {
        "schema_version": 1, "character": CHARACTER_ID, "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "technical_preflight_only", "visual_approval": "pending",
        "client_integration": "not_integrated", "runtime_acceptance": "not_tested",
        "note": "Technical checks and exact mirror checks cannot establish unique pose quality, continuity, anatomical correctness, or visual acceptance. Preview creation/playback does not grant approval.",
        "frame_size": [SIZE, SIZE], "transform": transform,
        "actions": {action: {"frames_per_direction": count, "frame_duration_ms": ms, "duration_ms": count * ms} for action, (count, ms) in ACTIONS.items()},
        "summary": {"expected": 68, "selected": 68, "missing": 0, "duplicate_groups": 0, "exact_horizontal_mirror_pairs": 0, "technical_preflight_passed": True},
        "frames": [row["record"] for row in rows],
    }


def preview_html(rows: list[dict]) -> str:
    sets = [{"action": action, "direction": direction, "ms": ms,
             "frames": [{"number": row["frame"], "url": f"frames/{action}/{direction}/{row['frame']:02d}.png"}
                        for row in rows if (row["action"], row["direction"]) == (action, direction)]}
            for action, (_, ms) in ACTIONS.items() for direction in DIRECTIONS]
    data = json.dumps(sets, ensure_ascii=False).replace("<", "\\u003c")
    return HTML_TEMPLATE.replace("__SETS_JSON__", data)


HTML_TEMPLATE = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><title>14 唤雪少女 · 战斗动作技术预览</title>
<style>
*{box-sizing:border-box}body{font:16px system-ui,sans-serif;background:#17222d;color:#f3f4f6;margin:24px}
button,select,input{font:inherit;margin:5px}button,select{padding:6px}button:disabled{opacity:.4}
.layout{display:flex;gap:24px;flex-wrap:wrap}.stage{width:min(76vw,650px);aspect-ratio:1;background:#fff;position:relative}
.stage img{width:100%;height:100%;object-fit:contain;display:block}.stage.checker{background-color:#ddd;background-image:linear-gradient(45deg,#999 25%,transparent 25%),linear-gradient(-45deg,#999 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#999 75%),linear-gradient(-45deg,transparent 75%,#999 75%);background-size:32px 32px;background-position:0 0,0 16px,16px -16px,-16px 0}
aside{max-width:430px;line-height:1.6}.status{white-space:pre-wrap;color:#ffe2ab}#counter{font-variant-numeric:tabular-nums}#frame{width:min(70vw,620px)}
</style>
<h1>14 唤雪少女 · 六段战斗动作</h1>
<p>技术预览；视觉验收待人工逐段记录。客户端未接入，运行未测试。缺帧或加载失败会停止播放，绝不补帧。</p>
<div>
<label>片段 <select id="sequence"><option value="all">六段连续播放</option></select></label>
<label>速度 <select id="speed"><option value="1">正常 1×</option><option value="0.25">慢放 0.25×（每帧时长 4 倍）</option></select></label>
<label>背景 <select id="background"><option value="light">浅色白底</option><option value="dark">深色黑底</option><option value="checker">透明网格</option></select></label>
<button id="play" disabled>从头播放</button><button id="pause" disabled>暂停</button><button id="prev" disabled>上一帧</button><button id="next" disabled>下一帧</button>
</div>
<input id="frame" type="range" min="0" max="67" value="0" disabled><span id="counter"></span>
<div class="layout"><div class="stage" id="stage"><img id="sprite" alt="当前动作帧"></div><aside>
<p>受击：40ms/帧，240ms/段；普攻：30ms/帧，360ms/段；施法：45ms/帧，720ms/段。</p>
<p>连续顺序：hit/E → hit/W → attack/E → attack/W → cast/E → cast/W。六段总长正常 2640ms，0.25× 慢放 10560ms。</p>
<p>重点观察：起止衔接、狐与雪晶持手、头身比例、脚根与脚滑、毛边透明、衣饰闪变、轮廓裁切。切换深浅底分别播放正常和慢放。</p>
<p>计时采用单一播放时钟，按每段真实帧时长选择当前帧；浏览器调度可能漏显示帧，下方如实计数。页面不自动判定验收通过。</p>
<div class="status" id="status">正在预加载全部 68 张帧……</div>
</aside></div>
<script>
'use strict';
const sets=__SETS_JSON__;
const $=id=>document.getElementById(id);
let ready=false,position=0,playing=false,start=0,raf=0,lastShown=-1,skipped=0,timeline=[];
const cache=new Map();
sets.forEach((s,i)=>{const option=document.createElement('option');option.value=String(i);option.textContent=s.action+'/'+s.direction+' ('+s.frames.length+'帧)';$('sequence').append(option)});
function rebuild(){const choice=$('sequence').value;const chosen=choice==='all'?sets:[sets[Number(choice)]];timeline=[];let end=0;chosen.forEach(s=>s.frames.forEach(f=>{end+=s.ms;timeline.push({url:f.url,number:f.number,action:s.action,direction:s.direction,ms:s.ms,end:end,count:s.frames.length})}));position=0;$('frame').max=timeline.length-1;show()}
function show(){if(!timeline.length)return;position=Math.max(0,Math.min(position,timeline.length-1));const f=timeline[position];$('sprite').src=f.url;$('frame').value=String(position);$('counter').textContent=f.action+'/'+f.direction+' '+String(f.number).padStart(2,'0')+'/'+f.count+'；'+f.ms+'ms/帧；当前 '+$('speed').value+'×'}
function stop(){playing=false;cancelAnimationFrame(raf);$('pause').disabled=true}
function tick(now){if(!playing)return;const elapsed=(now-start)*Number($('speed').value);let index=timeline.findIndex(f=>elapsed<f.end);if(index<0){index=timeline.length-1;if(index>lastShown+1)skipped+=index-lastShown-1;position=index;show();stop();$('status').textContent='播放结束。速度 '+$('speed').value+'×；当前背景 '+$('background').selectedOptions[0].text+'；未显示中间帧 '+skipped+'。\n视觉验收仍待记录，未自动通过。';return}if(index!==lastShown){if(index>lastShown+1)skipped+=index-lastShown-1;position=index;show();lastShown=index}raf=requestAnimationFrame(tick)}
$('play').onclick=()=>{if(!ready)return;stop();position=0;lastShown=0;skipped=0;show();start=performance.now();playing=true;$('pause').disabled=false;$('status').textContent='播放中：'+$('speed').value+'×，'+$('background').selectedOptions[0].text+'。';raf=requestAnimationFrame(tick)};
$('pause').onclick=()=>{stop();$('status').textContent='已暂停；未显示中间帧 '+skipped+'。视觉验收待记录。'};
$('prev').onclick=()=>{stop();position--;show()};$('next').onclick=()=>{stop();position++;show()};$('frame').oninput=()=>{stop();position=Number($('frame').value);show()};
$('sequence').onchange=()=>{stop();rebuild()};$('speed').onchange=()=>{stop();show()};
$('background').onchange=()=>{const mode=$('background').value;$('stage').classList.toggle('checker',mode==='checker');$('stage').style.backgroundColor=mode==='dark'?'#080b12':mode==='light'?'#ffffff':'#dddddd'};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing){stop();$('status').textContent='页面隐藏，已停止播放；重新从头播放后再验收。'}});
rebuild();
Promise.all(sets.flatMap(s=>s.frames).map(f=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{if(im.naturalWidth!==1024||im.naturalHeight!==1024){reject(new Error('尺寸错误 '+f.url));return}cache.set(f.url,im);resolve()};im.onerror=()=>reject(new Error('缺帧或加载失败 '+f.url));im.src=f.url}))).then(()=>{ready=true;['play','prev','next','frame'].forEach(id=>$(id).disabled=false);$('status').textContent='68/68 张已加载。请选择背景、正常速度或 0.25× 慢放，再播放。\n视觉验收待记录。'}).catch(error=>{stop();$('status').textContent=String(error)+'；未填补、未跳过，播放被禁用。'});
</script></html>'''


def write_new(path: Path, raw: bytes) -> None:
    local_path(path, must_exist=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selections", nargs=6, required=True, metavar="JSON", help="Exactly six explicit selection files")
    parser.add_argument("--preview-dir", help="New character-local directory for all 68 preview frames, HTML, and technical report")
    parser.add_argument("--publish", action="store_true", help="Publish all 68 runtime PNGs, derived receipts, and runtime technical manifest")
    args = parser.parse_args(argv)
    if CHARACTER.name != CHARACTER_ID:
        raise ValueError("This private tool may only run from the character-14 tools directory")
    selected = load_selections(args.selections)
    rows, transform = render(selected)
    report = manifest(rows, transform)
    preview = local_path(args.preview_dir, must_exist=False) if args.preview_dir else None
    if preview and preview.exists():
        raise ValueError(f"Refuse to overwrite an existing preview directory: {preview}")
    targets = []
    if args.publish:
        targets = [path for row in rows for path in (row["destination"], row["receipt"])]
        targets.append(CHARACTER / "runtime" / "technical-manifest.json")
        for path in targets:
            local_path(path, must_exist=False)
            if path.exists():
                raise ValueError(f"Refuse to overwrite existing runtime or receipt: {path}")
    # Every selection, source, receipt, image, and output collision is checked
    # before any writes. Failure before this point leaves the workspace alone.
    if preview:
        for row in rows:
            write_new(preview / "frames" / row["action"] / row["direction"] / f"{row['frame']:02d}.png", row["png"])
        write_new(preview / "technical-report.json", json_bytes(report))
        write_new(preview / "index.html", preview_html(rows).encode("utf-8"))
    if args.publish:
        for row in rows:
            write_new(row["receipt"], json_bytes(row["record"]))
            write_new(row["destination"], row["png"])
        published = dict(report, status="runtime_exported_technical_only")
        write_new(CHARACTER / "runtime" / "technical-manifest.json", json_bytes(published))
    print(json.dumps({"character": CHARACTER_ID, **report["summary"], "transform": transform,
                      "preview": str(preview / "index.html") if preview else None,
                      "runtime_exported": bool(args.publish), "visual_approval": "pending",
                      "client_integration": "not_integrated", "runtime_acceptance": "not_tested"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"finish_character: {error}", file=sys.stderr)
        raise SystemExit(2)
