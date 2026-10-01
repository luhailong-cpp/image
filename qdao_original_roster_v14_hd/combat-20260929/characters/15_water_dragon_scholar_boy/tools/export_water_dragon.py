#!/usr/bin/env python3
"""Private water-dragon export. Default: read-only, complete 68-slot preflight.

--publish adds only absent runtime PNGs and derived receipts after all checks.
--preview [directory] writes a new HTML player referencing the existing runtime.
Neither successful export nor recorded playback constitutes visual acceptance.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import sys

import numpy as np
from PIL import Image


CHARACTER = Path(__file__).resolve().parents[1]
BATCH = CHARACTER.parent.parent
REPO = BATCH.parent.parent
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
CANVAS = 1024
VISIBLE_ALPHA = 8


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return result


def within(path: Path, parent: Path = CHARACTER) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(parent.resolve()):
        raise ValueError(f"Path escapes allowed directory {parent}: {path}")
    return resolved


def resolve_file(value: str, local: bool = True) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing file path")
    path = Path(value)
    if not path.is_absolute():
        if path.parts[0] == "characters":
            path = BATCH / path
        elif path.parts[0] in ("qdao_original_roster_v14_hd", "designs", "q_daoist_character_pack_4096"):
            path = REPO / path
        else:
            path = CHARACTER / path
    path = within(path) if local else path.resolve()
    if not path.is_file():
        raise ValueError(f"Missing referenced file: {path}")
    return path


def relative(path: Path) -> str:
    return path.resolve().relative_to(BATCH.resolve()).as_posix()


def image_info(path: Path, exact_size: bool = False) -> tuple[Image.Image, dict]:
    with Image.open(path) as source:
        if source.format != "PNG" or source.mode != "RGBA":
            raise ValueError(f"Require native PNG RGBA: {path}")
        source.load()
        image = source.copy()
    width, height = image.size
    if width != height or width < CANVAS or (exact_size and width != CANVAS):
        raise ValueError(f"Require {'1024' if exact_size else 'at least 1024'} square canvas: {path}, {image.size}")
    array = np.asarray(image)
    alpha = array[:, :, 3]
    visible = alpha > VISIBLE_ALPHA
    ys, xs = np.nonzero(visible)
    if not len(xs) or not np.any(alpha == 0):
        raise ValueError(f"Require visible subject and fully transparent pixels: {path}")
    if any(np.any(edge > VISIBLE_ALPHA) for edge in (alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1])):
        raise ValueError(f"Visible subject touches canvas edge: {path}")
    canonical = np.array(image)
    canonical[canonical[:, :, 3] <= VISIBLE_ALPHA] = 0
    return image, {
        "width": width, "height": height, "mode": "RGBA", "format": "PNG",
        "visibleBBox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "transparentPixels": int(np.count_nonzero(alpha == 0)),
        "visiblePixels": int(len(xs)), "edgeAlphaThreshold": VISIBLE_ALPHA,
        "visiblePixelSha256": sha_bytes(canonical.tobytes()),
        "mirroredVisiblePixelSha256": sha_bytes(canonical[:, ::-1].tobytes()),
    }


def register_unique(info: dict, name: str, pixels: dict, mirrored: dict) -> None:
    key = (info["width"], info["height"], info["visiblePixelSha256"])
    mirror_key = (info["width"], info["height"], info["mirroredVisiblePixelSha256"])
    if key in pixels:
        raise ValueError(f"Repeated visible pixels: {name} and {pixels[key]}")
    if key in mirrored or mirror_key in pixels:
        other = mirrored.get(key, pixels.get(mirror_key))
        raise ValueError(f"Exact horizontal mirror pair: {name} and {other}")
    pixels[key] = name
    mirrored[mirror_key] = name


def verify_record(receipt: Path, source: Path, source_sha: str, info: dict) -> dict:
    record = read_json(receipt)
    if resolve_file(record.get("file")) != source:
        raise ValueError(f"Receipt file does not identify selected source: {receipt}")
    if str(record.get("sha256", "")).lower() != source_sha:
        raise ValueError(f"Source/receipt SHA mismatch: {source}, {receipt}")
    for field in ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot", "submittedParameters", "evidence"):
        if field not in record or record[field] in (None, "", {}):
            raise ValueError(f"Missing provenance field {field}: {receipt}")
    for field in ("actualModel", "actualQuality"):
        if field not in record or (record[field] is None and not record.get("unverifiedReason")):
            raise ValueError(f"Missing truthful {field} evidence: {receipt}")
    if record.get("width") != info["width"] or record.get("height") != info["height"]:
        raise ValueError(f"Receipt native dimensions differ from image: {receipt}")
    prompt = resolve_file(record.get("prompt"))
    if not prompt.read_text(encoding="utf-8-sig").strip():
        raise ValueError(f"Prompt file is empty: {prompt}")
    references = record.get("references")
    if not isinstance(references, list) or not references:
        raise ValueError(f"Missing reference list: {receipt}")
    for ref in references:
        if not isinstance(ref, dict) or not ref.get("role"):
            raise ValueError(f"Reference must record a path and purpose: {receipt}")
        ref_path = resolve_file(ref.get("path"), local=False)
        if ref.get("sha256") and ref["sha256"].lower() != sha_file(ref_path):
            raise ValueError(f"Reference SHA mismatch: {ref_path}")
    record["_prompt_path"] = prompt
    return record


def load_selected() -> list[dict]:
    paths = sorted(CHARACTER.glob("*selection.json"))
    if len(paths) != 6:
        raise ValueError(f"Require exactly six character-root *selection.json files; found {len(paths)}")
    selected, groups, sources, pixel_hashes, mirror_hashes, sizes = [], set(), set(), {}, {}, set()
    for path in paths:
        selection = read_json(path)
        action, direction = selection.get("action"), selection.get("direction")
        if action not in ACTIONS or direction not in DIRECTIONS:
            raise ValueError(f"Invalid action/direction: {path}")
        group = (action, direction)
        if group in groups:
            raise ValueError(f"Repeated selection group: {group}")
        groups.add(group)
        if selection.get("partial") or selection.get("status") == "partial":
            raise ValueError(f"Partial selection cannot export: {path}")
        frames = selection.get("frames")
        count = ACTIONS[action][0]
        if not isinstance(frames, list) or len(frames) != count:
            raise ValueError(f"Require {count} frames: {path}")
        if any(not isinstance(frame, dict) or type(frame.get("frame")) is not int for frame in frames):
            raise ValueError(f"Frame indices must be integers: {path}")
        if [frame["frame"] for frame in frames] != list(range(1, count + 1)):
            raise ValueError(f"Selection must be ordered 1..{count}: {path}")
        for frame in frames:
            source = resolve_file(frame.get("file"))
            receipt = resolve_file(frame.get("generationRecord"))
            if source in sources:
                raise ValueError(f"One source selected for multiple slots: {source}")
            sources.add(source)
            digest = sha_file(source)
            if str(frame.get("sha256", "")).lower() != digest:
                raise ValueError(f"Mandatory source/selection SHA mismatch: {source}")
            if frame.get("generationRecordSha256") and frame["generationRecordSha256"].lower() != sha_file(receipt):
                raise ValueError(f"Selected generation-record SHA mismatch: {receipt}")
            image, info = image_info(source)
            image.close()
            sizes.add((info["width"], info["height"]))
            register_unique(info, str(source), pixel_hashes, mirror_hashes)
            record = verify_record(receipt, source, digest, info)
            selected.append({"key": (action, direction, frame["frame"]), "source": source,
                             "sourceSha256": digest, "sourceReceipt": receipt,
                             "sourceReceiptSha256": sha_file(receipt), "sourceRecord": record,
                             "selection": path, "selectionSha256": sha_file(path), "nativeGeometry": info})
    if groups != {(action, direction) for action in ACTIONS for direction in DIRECTIONS} or len(selected) != 68:
        raise ValueError("Require complete six-group 68-slot selection")
    if len(sizes) != 1:
        raise ValueError(f"Mixed native canvases are rejected; require a single whole-canvas transform: {sorted(sizes)}")
    order = {action: index for index, action in enumerate(ACTIONS)}
    return sorted(selected, key=lambda entry: (order[entry["key"][0]], entry["key"][1], entry["key"][2]))


def render(selected: list[dict]) -> tuple[list[dict], dict]:
    native = selected[0]["nativeGeometry"]["width"]
    transform = {"nativeCanvas": [native, native], "outputCanvas": [CANVAS, CANVAS],
                 "wholeCanvasFactor": CANVAS / native, "offset": [0, 0],
                 "sharedByAll68Frames": True, "perFrameBoundingBoxScale": False,
                 "perFrameRecentering": False, "mirrorOrPoseSynthesis": False,
                 "filter": "identity" if native == CANVAS else "Pillow LANCZOS"}
    derived_at = datetime.now(timezone.utc).isoformat()
    rows, pixels, mirrors = [], {}, {}
    for entry in selected:
        if sha_file(entry["source"]) != entry["sourceSha256"] or sha_file(entry["sourceReceipt"]) != entry["sourceReceiptSha256"]:
            raise ValueError(f"Source or receipt changed during preflight: {entry['source']}")
        with Image.open(entry["source"]) as source:
            output = source.copy() if native == CANVAS else source.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        output.save(buffer, format="PNG")
        png = buffer.getvalue()
        # Use the same exact checks on in-memory output without creating a file.
        array = np.asarray(output)
        alpha = array[:, :, 3]
        if any(np.any(edge > VISIBLE_ALPHA) for edge in (alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1])):
            raise ValueError(f"Resampled subject touches boundary: {entry['key']}")
        ys, xs = np.nonzero(alpha > VISIBLE_ALPHA)
        if not len(xs) or not np.any(alpha == 0):
            raise ValueError(f"Invalid output transparency: {entry['key']}")
        canonical = np.array(output)
        canonical[canonical[:, :, 3] <= VISIBLE_ALPHA] = 0
        info = {"width": CANVAS, "height": CANVAS, "mode": "RGBA", "format": "PNG",
                "visibleBBox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
                "transparentPixels": int(np.count_nonzero(alpha == 0)),
                "edgeAlphaThreshold": VISIBLE_ALPHA,
                "visiblePixelSha256": sha_bytes(canonical.tobytes()),
                "mirroredVisiblePixelSha256": sha_bytes(canonical[:, ::-1].tobytes())}
        register_unique(info, str(entry["key"]), pixels, mirrors)
        output.close()
        action, direction, frame = entry["key"]
        destination = CHARACTER / "runtime" / action / direction / f"{frame:02d}.png"
        receipt = CHARACTER / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{frame:02d}.json"
        source_record = entry["sourceRecord"]
        record = {"file": relative(destination), "sha256": sha_bytes(png), "derivedAt": derived_at,
                  "generatedAt": source_record["generatedAt"], "width": CANVAS, "height": CANVAS,
                  "format": "PNG RGBA", "tool": "Pillow deterministic whole-canvas export", "route": "derived",
                  "configSnapshot": source_record["configSnapshot"],
                  "actualModel": source_record["actualModel"], "actualQuality": source_record["actualQuality"],
                  "unverifiedReason": source_record.get("unverifiedReason"),
                  "submittedParameters": source_record["submittedParameters"],
                  "prompt": source_record["prompt"], "references": source_record["references"],
                  "evidence": {"selection": relative(entry["selection"]), "selectionSha256": entry["selectionSha256"],
                               "sourceGenerationRecord": relative(entry["sourceReceipt"]),
                               "sourceGenerationRecordSha256": entry["sourceReceiptSha256"],
                               "promptSha256": sha_file(source_record["_prompt_path"])},
                  "derivedFrom": {"file": relative(entry["source"]), "sha256": entry["sourceSha256"],
                                  "generationRecord": relative(entry["sourceReceipt"]),
                                  "generationRecordSha256": entry["sourceReceiptSha256"]},
                  "operation": {"kind": "shared_uniform_whole_canvas_downsample", "transform": transform,
                                "noAlphaCleanupOrPoseEditing": True},
                  "nativeGeometry": entry["nativeGeometry"], "outputGeometry": info,
                  "frameDurationMs": ACTIONS[action][1], "visualApproval": "pending",
                  "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}
        rows.append({"destination": destination, "receipt": receipt, "png": png, "record": record})
    return rows, transform


def write_new(path: Path, value: bytes) -> None:
    within(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(value)


def publish(rows: list[dict]) -> None:
    destinations = [path for row in rows for path in (row["destination"], row["receipt"])]
    for path in destinations:
        within(path)
        if path.exists():
            raise ValueError(f"Refuse to overwrite runtime or receipt: {path}")
    for row in rows:
        write_new(row["receipt"], (json.dumps(row["record"], ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        write_new(row["destination"], row["png"])


def preview_sets(destination: Path) -> list[dict]:
    sets, pixels, mirrors = [], {}, {}
    expected = set()
    for action, (count, duration) in ACTIONS.items():
        for direction in DIRECTIONS:
            frames = []
            for frame in range(1, count + 1):
                path = CHARACTER / "runtime" / action / direction / f"{frame:02d}.png"
                expected.add(path.resolve())
                image, info = image_info(path, exact_size=True)
                image.close()
                register_unique(info, str(path), pixels, mirrors)
                receipt = CHARACTER / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{frame:02d}.json"
                record = read_json(receipt)
                if record.get("sha256") != sha_file(path) or resolve_file(record.get("file")) != path.resolve():
                    raise ValueError(f"Runtime/derived receipt mismatch: {path}")
                frames.append({"url": Path(os.path.relpath(path, destination.parent)).as_posix(),
                               "sha256": record["sha256"], "frame": frame})
            sets.append({"action": action, "direction": direction, "interval": duration, "frames": frames})
    unexpected = {path.resolve() for path in (CHARACTER / "runtime").rglob("*.png")} - expected
    if unexpected:
        raise ValueError(f"Unexpected runtime PNGs: {sorted(map(str, unexpected))}")
    return sets


HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>水龙书生 · 六段动作离线验收</title>
<style>
*{box-sizing:border-box}body{margin:24px;background:#f4f2ea;color:#183846;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif}
main{max-width:1100px;margin:auto}h1{font-size:25px}.layout{display:grid;grid-template-columns:minmax(300px,620px) 1fr;gap:22px}
.stage{aspect-ratio:1;background:white;border:1px solid #aaa;position:relative}.stage.dark{background:#11151d}.stage img{display:block;width:100%;height:100%;object-fit:contain}
.stage:after{content:"";position:absolute;inset:0;pointer-events:none;border-bottom:1px dashed #708090}
button,select,input{font:inherit}button,select{padding:6px 9px;margin:3px}button:disabled{opacity:.45}input[type=range]{width:100%}
.note{background:#fff0cb;padding:10px;border-radius:6px}.controls{margin:10px 0}pre{font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:320px;overflow:auto;background:#fff;padding:12px}
#state{font-weight:600}small{color:#52616a}@media(max-width:850px){.layout{grid-template-columns:1fr}}
</style><main><h1>水龙书生 · 六段动作离线验收</h1>
<p class="note">1024 透明 PNG 离线播放。视觉验收待审阅；未接入客户端，未做客户端运行验收。播放记录仅证明页面播放事件，不自动证明美术通过。</p>
<p id="load">正在预载并解码全部 68 张图片…</p><div class="layout"><section>
<div id="stage" class="stage"><img id="sprite" alt="水龙书生动作帧"></div>
<div class="controls"><button id="one" disabled>播放本段</button><button id="all" disabled>六段连续循环</button><button id="pause" disabled>暂停</button><button id="previous" disabled>上一帧</button><button id="next" disabled>下一帧</button></div>
<input id="scrub" type="range" min="1" max="6" value="1" disabled><p id="counter"></p>
</section><aside><label>动作段 <select id="segment" disabled></select></label>
<label>速度 <select id="speed" disabled><option value="1">1× 正常速度</option><option value="0.25">0.25× 慢放（时长4倍）</option></select></label>
<div class="controls"><button id="background">深色背景</button></div>
<p id="timing"></p><p id="state">预载中，未开始播放</p><small>受击40ms/帧、普通攻击30ms/帧、施法45ms/帧。浏览器刷新率影响实际显示时刻。检查比例、脚根、持手、衣服闪变与透明边缘。</small>
<details open><summary>本次页面播放记录（不构成视觉通过）</summary><pre id="log">[]</pre></details>
<details><summary>当前图片</summary><pre id="metadata"></pre></details>
</aside></div></main>
<script id="data" type="application/json">__DATA__</script>
<script>
"use strict";
const sets=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id);
const names={hit:'受击',attack:'普通攻击',cast:'施法'};
let si=0,fi=0,playing=false,continuous=false,segmentStart=0,raf=0,decoded=[],history=[],lap=0;
function record(event,source,detail={}){history.push({at:new Date().toISOString(),event,source,segment:sets[si].action+'/'+sets[si].direction,frame:fi+1,speed:Number($('speed').value),...detail});$('log').textContent=JSON.stringify(history.slice(-80),null,2);}
sets.forEach((s,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`${names[s.action]} / ${s.direction} · ${s.frames.length}帧`;$('segment').append(o)});
function show(){const s=sets[si],f=s.frames[fi],speed=Number($('speed').value);$('segment').value=si;$('scrub').max=s.frames.length;$('scrub').value=fi+1;$('sprite').src=f.url;$('sprite').alt=`水龙书生 ${names[s.action]} ${s.direction} 第${fi+1}帧`;$('counter').textContent=`${names[s.action]} ${s.direction} · ${fi+1}/${s.frames.length} · ${speed}×`;$('timing').textContent=`契约正常：${s.interval}ms/帧，${s.interval*s.frames.length}ms/段；当前：${s.interval/speed}ms/帧，${s.interval*s.frames.length/speed}ms/段`;$('metadata').textContent=JSON.stringify(f,null,2);}
function stop(source,event='paused'){playing=false;cancelAnimationFrame(raf);$('state').textContent=`${source==='user'?'用户操作':'自动播放'}：已暂停；视觉验收待审阅`;record(event,source);}
function tick(now){if(!playing)return;let s=sets[si],interval=s.interval/Number($('speed').value),elapsed=now-segmentStart;
 while(elapsed>=s.frames.length*interval){fi=s.frames.length-1;record('segment_completed','automatic',{nominalDurationMs:s.frames.length*interval});
  if(!continuous){show();stop('automatic','single_segment_finished');return;}
  segmentStart+=s.frames.length*interval;si=(si+1)%sets.length;fi=0;if(si===0){lap++;record('six_segments_completed','automatic',{lap});}record('segment_started','automatic');s=sets[si];interval=s.interval/Number($('speed').value);elapsed=now-segmentStart;}
 fi=Math.min(s.frames.length-1,Math.floor(elapsed/interval));show();$('state').textContent=`自动播放中：${continuous?'六段连续循环':'本段'} · 已完成整轮 ${lap}；视觉验收待审阅`;raf=requestAnimationFrame(tick);}
function play(all){if(playing)stop('user');continuous=all;fi=0;if(all){si=0;lap=0;}show();playing=true;segmentStart=performance.now();record(all?'six_segment_loop_started':'single_segment_started','user');raf=requestAnimationFrame(tick);}
$('one').onclick=()=>play(false);$('all').onclick=()=>play(true);$('pause').onclick=()=>stop('user');
function step(delta){stop('user','frame_step');fi=Math.max(0,Math.min(sets[si].frames.length-1,fi+delta));show();record('frame_shown','user');}
$('previous').onclick=()=>step(-1);$('next').onclick=()=>step(1);
$('scrub').oninput=()=>{stop('user','scrub');fi=Number($('scrub').value)-1;show();};
$('segment').onchange=()=>{stop('user','segment_selected');si=Number($('segment').value);fi=0;show();record('segment_ready','user');};
$('speed').onchange=()=>{stop('user','speed_changed');show();};
$('background').onclick=()=>{const dark=$('stage').classList.toggle('dark');$('background').textContent=dark?'浅色背景':'深色背景';record('background_changed','user',{background:dark?'dark':'light'});};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing)stop('automatic','hidden_tab_paused');});
async function preload(){try{let count=0;decoded=await Promise.all(sets.flatMap(s=>s.frames).map(async f=>{const image=new Image();image.src=f.url;await image.decode();if(image.naturalWidth!==1024||image.naturalHeight!==1024)throw Error('尺寸不符 '+f.url);$('load').textContent=`已解码 ${++count}/68 张`;return image;}));for(const id of ['one','all','pause','previous','next','scrub','segment','speed'])$(id).disabled=false;$('load').textContent='68/68 张预载解码完成；等待用户开始播放';$('state').textContent='用户尚未播放；视觉验收待审阅';show();record('preload_complete','automatic',{decoded:decoded.length});}catch(error){$('load').textContent='预载失败：'+error.message;$('state').textContent='禁止播放：资源未完整解码';record('preload_failed','automatic',{error:String(error)});}}
preload();
</script></html>'''


def create_preview(value: str) -> Path:
    directory = Path(value)
    if not directory.is_absolute():
        directory = CHARACTER / directory
    directory = within(directory)
    destination = directory / "index.html"
    if destination.exists():
        raise ValueError(f"Refuse to overwrite preview; choose another --preview directory: {destination}")
    if any(directory == CHARACTER / name or directory.is_relative_to(CHARACTER / name)
           for name in ("runtime", "staging", "prompts", "provenance", "tools")):
        raise ValueError("Preview must not be placed in an asset, provenance, prompt or tool directory")
    sets = preview_sets(destination)
    data = json.dumps(sets, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    write_new(destination, HTML.replace("__DATA__", data).encode("utf-8"))
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="Write absent runtime PNGs and derived receipts after full preflight")
    parser.add_argument("--preview", nargs="?", const="preview", metavar="DIRECTORY",
                        help="Create new DIRECTORY/index.html (default: character/preview), referencing existing runtime")
    args = parser.parse_args()
    result = {"character": CHARACTER.name, "visualApproval": "pending", "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested"}
    if args.publish or args.preview is None:
        selected = load_selected()
        rows, transform = render(selected)
        result.update(technicalPreflight="passed", selectedSlots=len(rows), transform=transform,
                      duplicateAndMirrorCheck="passed; pixels with alpha <= 8 ignored for comparison")
        if args.publish:
            publish(rows)
            result["publishedSlots"] = len(rows)
    if args.preview is not None:
        result["preview"] = str(create_preview(args.preview))
        result["previewStatus"] = "created; no playback or visual acceptance inferred"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"export_water_dragon: {error}", file=sys.stderr)
        raise SystemExit(2)
