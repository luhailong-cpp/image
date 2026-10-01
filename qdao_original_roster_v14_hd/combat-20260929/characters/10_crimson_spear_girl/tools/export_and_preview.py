#!/usr/bin/env python3
"""Character-private explicit-selection export; never overwrite an existing file.

Default is a read-only preflight. No automatic selection, pose synthesis,
alpha repair, per-frame repositioning, or visual-approval claim occurs here.
All write destinations must be inside this character directory.
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
BATCH = CHARACTER.parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def local_path(value):
    path = Path(value)
    if not path.is_absolute():
        path = (BATCH if path.parts[0] == "characters" else CHARACTER) / path
    path = path.resolve()
    if not path.is_relative_to(CHARACTER):
        raise ValueError(f"Path outside character directory: {path}")
    return path


def relative(path):
    return path.relative_to(CHARACTER).as_posix()


def write_new(path, raw):
    path = local_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def as_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def image_geometry(image):
    pixels = np.asarray(image)
    alpha = pixels[:, :, 3]
    ys, xs = np.where(alpha > 8)
    if not len(xs):
        raise ValueError("Fully invisible image")
    if not np.any(alpha == 0):
        raise ValueError("No fully transparent pixels")
    visible = pixels.copy()
    visible[alpha == 0] = 0
    return {
        "visibleBBox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "transparentPixels": int(np.count_nonzero(alpha == 0)),
        "visiblePixels": int(len(xs)),
        "touchesCanvasEdge": bool(np.any(alpha[0] > 8) or np.any(alpha[-1] > 8)
                                   or np.any(alpha[:, 0] > 8) or np.any(alpha[:, -1] > 8)),
        "visiblePixelSha256": digest(visible.tobytes()),
        "mirrorVisiblePixelSha256": digest(visible[:, ::-1].tobytes()),
    }


def selected_rows(allow_partial):
    paths = sorted(set(CHARACTER.glob("*selection.json"))
                   | set((CHARACTER / "staging").glob("*selection.json"))
                   | set((CHARACTER / "selections").glob("*selection.json")))
    rows, seen_keys, seen_sources = [], set(), set()
    for selection in paths:
        data = read_json(selection)
        action, direction = data.get("action"), data.get("direction")
        if action not in ACTIONS or direction not in DIRECTIONS:
            raise ValueError(f"Invalid selection action/direction: {selection}")
        count = ACTIONS[action][0]
        entries = data.get("frames", [])
        indices = [entry.get("frame") for entry in entries]
        if indices != sorted(set(indices)) or any(type(i) is not int or not 1 <= i <= count for i in indices):
            raise ValueError(f"Invalid or duplicate selection indices: {selection}")
        if len(entries) != count and data.get("status") != "partial":
            raise ValueError(f"Incomplete selection must explicitly say status=partial: {selection}")
        if not allow_partial and len(entries) != count:
            raise ValueError(f"Partial selection requires --allow-partial: {selection}")
        for entry in entries:
            key = (action, direction, entry["frame"])
            source = local_path(entry["file"])
            record_path = local_path(entry["generationRecord"])
            if key in seen_keys or source in seen_sources:
                raise ValueError(f"Slot/source selected more than once: {key} {source}")
            seen_keys.add(key)
            seen_sources.add(source)
            raw = source.read_bytes()
            sha = digest(raw)
            record = read_json(record_path)
            if entry.get("sha256", "").lower() != sha or record.get("sha256", "").lower() != sha:
                raise ValueError(f"Selection/source/receipt SHA mismatch: {source}")
            required = ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot",
                        "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references")
            missing = [k for k in required if k not in record]
            if missing or not record.get("prompt") or not record.get("references"):
                raise ValueError(f"Missing source provenance {missing}: {record_path}")
            if (record["actualModel"] is None or record["actualQuality"] is None) and not record.get("unverifiedReason"):
                raise ValueError(f"Unknown model/quality without explanation: {record_path}")
            with Image.open(source) as native:
                native.load()
                if native.format != "PNG" or native.mode != "RGBA" or min(native.size) < 1024:
                    raise ValueError(f"Expected native PNG RGBA at least 1024 in both dimensions: {source}")
                image = native.copy()
            geometry = image_geometry(image)
            if geometry["touchesCanvasEdge"]:
                raise ValueError(f"Source subject touches canvas edge: {source}")
            rows.append({"key": key, "source": source, "sourceSha256": sha, "sourceRecord": record,
                         "sourceRecordPath": record_path, "sourceRecordSha256": digest(record_path.read_bytes()),
                         "selectionPath": selection, "selectionSha256": digest(selection.read_bytes()),
                         "image": image, "nativeGeometry": geometry})
    if not allow_partial and len(rows) != 68:
        raise ValueError(f"Require all 68 explicitly selected slots; found {len(rows)}")
    return sorted(rows, key=lambda row: (list(ACTIONS).index(row["key"][0]), row["key"][1], row["key"][2]))


def transformations(rows, path):
    sizes = {row["image"].size for row in rows}
    if not rows:
        return {}
    if path:
        transforms = read_json(local_path(path))
    elif sizes == {(1024, 1024)}:
        transforms = {d: {"nativeCanvas": [1024, 1024], "scaledWholeCanvas": [1024, 1024],
                          "offset": [0, 0], "note": "Identity whole-canvas export; generated root retained."}
                      for d in DIRECTIONS}
    else:
        raise ValueError(f"Non-1024 native canvas {sizes}: supply explicit --transform-json; no automatic fitting")
    for row in rows:
        t = transforms[row["key"][1]]
        w, h = row["image"].size
        tw, th = t["scaledWholeCanvas"]
        if t["nativeCanvas"] != [w, h] or min(tw, th) <= 0 or tw > w or th > h:
            raise ValueError("Invalid fixed transform or attempted upscale")
        if abs(tw / w - th / h) > 1 / min(w, h):
            raise ValueError("Fixed transform is not uniform scale")
        if len(t["offset"]) != 2 or any(type(i) is not int for i in [tw, th, *t["offset"]]):
            raise ValueError("Transform sizes/offsets must be integers")
    return transforms


def render(rows, transforms):
    hashes, mirrored, output = {}, {}, []
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        action, direction, number = row["key"]
        transform = transforms[direction]
        image = row["image"]
        size = tuple(transform["scaledWholeCanvas"])
        if image.size != size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        bbox = image.getbbox()
        x, y = transform["offset"]
        if bbox and (bbox[0] + x < 0 or bbox[1] + y < 0 or bbox[2] + x > 1024 or bbox[3] + y > 1024):
            raise ValueError(f"Fixed transform would crop alpha content: {row['key']}")
        final = Image.new("RGBA", (1024, 1024))
        final.paste(image, (x, y))
        geometry = image_geometry(final)
        if geometry["touchesCanvasEdge"]:
            raise ValueError(f"Export touches canvas edge: {row['key']}")
        sha = geometry["visiblePixelSha256"]
        if sha in hashes:
            raise ValueError(f"Duplicate visible pixels: {hashes[sha]} / {row['key']}")
        if sha in mirrored:
            raise ValueError(f"Exact mirrored visible pixels: {mirrored[sha]} / {row['key']}")
        hashes[sha] = row["key"]
        mirrored[geometry["mirrorVisiblePixelSha256"]] = row["key"]
        buffer = io.BytesIO()
        final.save(buffer, "PNG")
        raw = buffer.getvalue()
        destination = CHARACTER / "runtime" / action / direction / f"{number:02d}.png"
        receipt = CHARACTER / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{number:02d}.json"
        original = row["sourceRecord"]
        record = {k: original.get(k) for k in ("generatedAt", "generatedAtEvidence", "configSnapshot",
                                              "actualModel", "actualQuality", "unverifiedReason", "prompt", "references")}
        record.update({"file": relative(destination), "sha256": digest(raw), "derivedAt": now,
                       "width": 1024, "height": 1024, "format": "PNG RGBA", "tool": "Pillow whole-canvas export",
                       "route": "derived", "submittedParameters": {"model": None, "quality": None},
                       "evidence": {"selection": relative(row["selectionPath"]), "selectionSha256": row["selectionSha256"]},
                       "derivedFrom": {"file": relative(row["source"]), "sha256": row["sourceSha256"],
                                       "generationRecord": relative(row["sourceRecordPath"]),
                                       "generationRecordSha256": row["sourceRecordSha256"]},
                       "operation": {"kind": "whole_canvas_fixed_transform", "transform": transform,
                                     "filter": "none" if row["image"].size == size else "Pillow LANCZOS",
                                     "noPoseSynthesis": True, "noFramewiseFitOrRecentering": True},
                       "nativeGeometry": row["nativeGeometry"], "outputGeometry": geometry,
                       "visualApproval": "pending", "clientIntegration": "not_integrated"})
        output.append({"key": row["key"], "destination": destination, "receipt": receipt,
                       "png": raw, "record": record})
    return output


def preview_html(output, preview):
    existing = {row["key"] for row in output}
    sequences = [{"action": a, "direction": d, "frameMs": ms, "expectedFrames": count,
                  "frames": [{"frame": n, "exists": (a, d, n) in existing,
                              "url": f"frames/{a}/{d}/{n:02d}.png"}
                             for n in range(1, count + 1)]}
                 for a, (count, ms) in ACTIONS.items() for d in DIRECTIONS]
    data = json.dumps(sequences).replace("<", "\\u003c")
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>赤枪少女 · 六段离线连播</title>
<style>body{background:#eef1f2;color:#223;font:16px system-ui;margin:24px}h1{font-size:24px}button,select{font:inherit;margin:4px;padding:6px}#stage{display:flex;gap:16px}.tile{position:relative;width:min(42vw,560px);aspect-ratio:1}.tile.light{background:#fff}.tile.dark{background:#10151d}.tile img{width:100%;height:100%}.missing{position:absolute;inset:0;display:grid;place-content:center;color:#b54}.dark .missing{color:#ffbda6}#status{font-variant-numeric:tabular-nums}#error{color:#b22}</style>
<h1>赤枪少女 · 六段离线连播</h1><p>技术预览；美术验收待完成；未接入客户端、未运行验证。深浅底同时显示相同帧。</p>
<select id="seq"></select><select id="speed"><option value="1">正常速度 1×</option><option value="0.25">慢放 0.25×（每帧4倍时长）</option></select>
<button id="once">本段播放</button><button id="all">六段顺序连播</button><button id="stop">停止</button><button id="prev">上一帧</button><button id="next">下一帧</button>
<p id="status"></p><p id="error"></p><div id="stage"><div class="tile light"><img id="light"><span class="missing"></span></div><div class="tile dark"><img id="dark"><span class="missing"></span></div></div>
<p>严格按原序显示缺槽；不会跨过缺槽、重复填充或插值。浏览器计时用于离线观察。像素唯一不证明姿态独立或持手正确。</p><p><a href="technical-report.json">技术清单</a></p>
<script>const sequences=__DATA__;const $=id=>document.getElementById(id);let s=0,f=0,playing=false,chain=false,raf=0,start=0,preloaded=false;
sequences.forEach((x,i)=>{const o=document.createElement('option');o.value=i;o.textContent=x.action+'/'+x.direction+' · '+x.expectedFrames+'帧';$('seq').append(o)});
function stop(){playing=false;cancelAnimationFrame(raf)}
function show(){const q=sequences[s],v=q.frames[f];$('seq').value=s;$('status').textContent=q.action+'/'+q.direction+' · '+(f+1)+'/'+q.frames.length+' · '+$('speed').value+'× · 每帧 '+(q.frameMs/Number($('speed').value))+' ms · 本段正常时长 '+q.frameMs*q.frames.length+' ms';for(const id of ['light','dark']){const im=$(id);im.style.visibility=v.exists?'visible':'hidden';if(v.exists)im.src=v.url;else im.removeAttribute('src')}document.querySelectorAll('.missing').forEach(x=>{x.style.display=v.exists?'none':'grid';x.textContent='缺少 '+q.action+'/'+q.direction+'/'+String(v.frame).padStart(2,'0')})}
async function preload(){if(preloaded)return;const errors=[];await Promise.all(sequences.flatMap(q=>q.frames.filter(v=>v.exists).map(v=>new Promise(resolve=>{const im=new Image;im.onload=resolve;im.onerror=()=>{errors.push(v.url);resolve()};im.src=v.url}))));if(errors.length){$('error').textContent='无法读取：'+errors.join(', ');throw Error('Image preload failed')}preloaded=true}
function tick(now){if(!playing)return;const q=sequences[s],interval=q.frameMs/Number($('speed').value),index=Math.floor((now-start)/interval);if(index>=q.frames.length){if(chain&&s<sequences.length-1){start+=q.frames.length*interval;s++;f=0;show();raf=requestAnimationFrame(tick);return}f=q.frames.length-1;show();stop();return}if(f!==index){f=index;show()}raf=requestAnimationFrame(tick)}
async function play(all){stop();await preload();chain=all;if(all)s=0;f=0;show();playing=true;start=performance.now();raf=requestAnimationFrame(tick)}
$('once').onclick=()=>play(false);$('all').onclick=()=>play(true);$('stop').onclick=stop;$('prev').onclick=()=>{stop();f=Math.max(0,f-1);show()};$('next').onclick=()=>{stop();f=Math.min(sequences[s].frames.length-1,f+1);show()};$('seq').onchange=()=>{stop();s=Number($('seq').value);f=0;show()};$('speed').onchange=()=>{stop();show()};show();
</script></html>'''.replace("__DATA__", data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-partial", action="store_true", help="Report missing slots honestly; permit partial previews/export")
    parser.add_argument("--transform-json", help="Character-relative JSON of E/W fixed transforms for non-1024 native sources")
    parser.add_argument("--preview-dir", help="New character-relative directory; never overwrite")
    parser.add_argument("--publish", action="store_true", help="Write selected runtime PNGs and derived receipts")
    args = parser.parse_args()
    rows = selected_rows(args.allow_partial)
    transforms = transformations(rows, args.transform_json)
    output = render(rows, transforms)
    counts = {f"{a}/{d}": sum(row["key"][:2] == (a, d) for row in output) for a in ACTIONS for d in DIRECTIONS}
    missing = {f"{a}/{d}": [n for n in range(1, count + 1) if (a, d, n) not in {r["key"] for r in output}]
               for a, (count, _) in ACTIONS.items() for d in DIRECTIONS}
    report = {"character": CHARACTER.name, "status": "selection_complete_technical_preflight_visual_pending" if len(output) == 68 else "partial",
              "generatedAt": datetime.now(timezone.utc).isoformat(), "expectedSlots": 68, "selectedSlots": len(output),
              "counts": counts, "missingSlots": missing, "selectedFramePreflightPassed": True,
              "completeTechnicalPreflightPassed": len(output) == 68, "runtimeWriteRequested": args.publish, "visualApproval": "pending",
              "clientIntegration": "not_integrated", "runtimeAcceptance": "not_tested", "transforms": transforms,
              "note": "Hashes test exact duplicates/mirrors only. Independent poses, continuity, anatomy and art require visual review.",
              "frames": [row["record"] for row in output]}
    preview = local_path(args.preview_dir) if args.preview_dir else None
    if preview and preview.exists():
        raise ValueError(f"Refuse to overwrite preview directory: {preview}")
    if args.publish:
        for row in output:
            if row["destination"].exists() or row["receipt"].exists():
                raise ValueError(f"Refuse to overwrite runtime/receipt: {row['destination']}")
    if preview:
        for row in output:
            a, d, n = row["key"]
            write_new(preview / "frames" / a / d / f"{n:02d}.png", row["png"])
        write_new(preview / "technical-report.json", as_json(report))
        write_new(preview / "index.html", preview_html(output, preview).encode("utf-8"))
    if args.publish:
        for row in output:
            write_new(row["receipt"], as_json(row["record"]))
            write_new(row["destination"], row["png"])
    print(json.dumps({k: v for k, v in report.items() if k != "frames"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"export_and_preview: {error}", file=sys.stderr)
        raise SystemExit(2)
