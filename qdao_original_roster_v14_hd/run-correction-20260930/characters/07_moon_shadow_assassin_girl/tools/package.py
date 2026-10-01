#!/usr/bin/env python3
"""Private, opt-in exporter for 07 月影少女. Importing never writes files.

Run with the bundled Pillow runtime, preferably with Python's -B switch:
  python -B tools/package.py              # read-only source/output preflight
  python -B tools/package.py --write      # export selected frames + manifest/preview

generation/selection.json examples (paths are relative to generation/):
  {"frames": {"E": {"01": "E/frame-01.png"}}}
  {"frames": {"E/01": {"path": "E/frame-01.png",
                         "record": "E/frame-01.png.generation.json"}}}
  {"frames": [{"direction": "E", "frame": 1, "path": "E/frame-01.png"}]}

Only explicit selections are exported. Missing frames remain missing. Each
source must be an independently generated square RGBA PNG, natively >=1024.
All selected source canvases must have the same dimensions. Full canvases are
resized by one common scale; there is no crop, mirror, interpolation between
poses, per-frame translation, bounding-box normalization, or foot alignment.
All frames receive the same -20px vertical export translation because the
native E01 ground returned near 94% rather than the requested 92% plane.

The fixed export root is (512,942), runtime pivot (.5,.08); the 0.08 pivot's
unrounded root is y=942.08. Source compositions must already use the matching
relative root. This program cannot infer or prove artistic root placement.
It checks structure only and never declares visual or runtime acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

from PIL import Image


CHARACTER = "07_moon_shadow_assassin_girl"
ROLE_ROOT = Path(__file__).resolve().parent.parent
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
SIZE = 1024
ROOT_POINT = [512, 942]
COMMON_TRANSLATION = [0, -20]
PIVOT = [0.5, 0.08]
SCHEMA = "moon-shadow-run-package-v1"


def confined(path: Path) -> Path:
    """Check every read/write target after resolving Windows junctions/symlinks."""
    resolved = path.resolve()
    try:
        resolved.relative_to(ROLE_ROOT)
    except ValueError as exc:
        raise ValueError(f"Path escapes this character: {path}") from exc
    return resolved


def source_path(value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Selected path must be a nonempty relative string")
    normal = value.replace("\\", "/")
    win = PureWindowsPath(value)
    if Path(normal).is_absolute() or win.is_absolute() or win.drive:
        raise ValueError(f"Absolute source paths are forbidden: {value}")
    if any(part in ("..", ".", "") for part in normal.split("/")):
        raise ValueError(f"Traversal/empty path component is forbidden: {value}")
    if ":" in normal or "\x00" in normal:
        raise ValueError(f"Invalid source path: {value}")
    result = confined(ROLE_ROOT / "generation" / normal)
    try:
        result.relative_to(confined(ROLE_ROOT / "generation"))
    except ValueError as exc:
        raise ValueError(f"Selected source escapes generation/: {value}") from exc
    return result


def relative(path: Path) -> str:
    return confined(path).relative_to(ROLE_ROOT).as_posix()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_read(path: Path):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON object key: {key}")
            result[key] = value
        return result
    return json.loads(confined(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)


def atomic_write(path: Path, data: bytes) -> None:
    target = confined(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Recheck after creating ancestors in case an existing ancestor is a link.
    target = confined(path)
    descriptor, temporary = tempfile.mkstemp(prefix=".package-", dir=target.parent)
    temp_path = confined(Path(temporary))
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
        os.replace(temp_path, target)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def json_write(path: Path, value) -> None:
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def frame_key(direction, frame) -> tuple[str, int]:
    if direction not in DIRECTIONS:
        raise ValueError(f"Unknown direction: {direction!r}")
    if isinstance(frame, bool) or not re.fullmatch(r"(?:0?[1-9]|1[0-6])", str(frame)):
        raise ValueError(f"Frame must be 01..16: {frame!r}")
    return direction, int(frame)


def parse_selection(document) -> dict[tuple[str, int], dict]:
    if not isinstance(document, dict) or "frames" not in document:
        raise ValueError("selection.json must be an object with an explicit frames field")
    frames = document["frames"]
    selections = {}

    def add(direction, frame, entry):
        key = frame_key(direction, frame)
        if key in selections:
            raise ValueError(f"Duplicate selection: {key[0]}/{key[1]:02d}")
        if isinstance(entry, str):
            entry = {"path": entry}
        if not isinstance(entry, dict) or "path" not in entry:
            raise ValueError(f"Selection {key} needs a source path")
        source_path(entry["path"])
        if "record" in entry:
            source_path(entry["record"])
        selections[key] = entry

    if isinstance(frames, list):
        for item in frames:
            if not isinstance(item, dict):
                raise ValueError("Frame list entries must be objects")
            add(item.get("direction"), item.get("frame"), item)
    elif isinstance(frames, dict):
        for key, value in frames.items():
            if "/" in key:
                direction, frame = key.split("/", 1)
                add(direction, frame, value)
            elif key in DIRECTIONS and isinstance(value, dict):
                for frame, entry in value.items():
                    add(key, frame, entry)
            else:
                raise ValueError(f"Invalid frame mapping: {key!r}")
    else:
        raise ValueError("frames must be a direction map, flat map, or list")
    return selections


def source_inspection(entry: dict) -> dict:
    source = source_path(entry["path"])
    if source.suffix.lower() != ".png":
        raise ValueError("Selected source must be a PNG file")
    record_path = source_path(entry.get("record", entry["path"] + ".generation.json"))
    raw = source.read_bytes()
    source_hash = digest(raw)
    record = json_read(record_path)
    required = (
        "file", "sha256", "generatedAt", "width", "height", "format", "tool", "route",
        "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "evidence",
        "prompt", "references",
    )
    missing = [field for field in required if field not in record]
    if missing:
        raise ValueError("Source generation record misses: " + ", ".join(missing))
    if str(record["sha256"]).lower() != source_hash:
        raise ValueError("Source SHA does not match generation record")
    generated_at = datetime.fromisoformat(str(record["generatedAt"]).replace("Z", "+00:00"))
    if generated_at.tzinfo is None:
        raise ValueError("generatedAt must include a time zone")
    for field in ("model", "quality"):
        if field not in record["submittedParameters"]:
            raise ValueError(f"submittedParameters.{field} is required (null when undisclosed)")
    for field in ("model", "quality", "builtin_product", "verified_on", "sources"):
        if field not in record["configSnapshot"]:
            raise ValueError(f"configSnapshot.{field} is required")
    if (record["actualModel"] is None or record["actualQuality"] is None) and not record.get("unverifiedReason"):
        raise ValueError("Unknown actual model/quality requires unverifiedReason")
    if not record["evidence"] or not record["prompt"] or not record["references"]:
        raise ValueError("evidence, actual prompt, and references must be recorded")
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        if image.format != "PNG" or image.mode != "RGBA":
            raise ValueError(f"Native source must be PNG RGBA, got {image.format}/{image.mode}")
        width, height = image.size
        if width != height or width < SIZE:
            raise ValueError(f"Native source must be square and >=1024, got {width}x{height}")
        if [record["width"], record["height"]] != [width, height]:
            raise ValueError("Source dimensions do not match generation record")
        if str(record["format"]).upper() not in ("PNG", "IMAGE/PNG"):
            raise ValueError("Source format does not match generation record")
        alpha = image.getchannel("A")
        alpha_min, alpha_max = alpha.getextrema()
        if alpha_min != 0 or alpha_max == 0:
            raise ValueError(f"Source needs visible pixels and true transparent pixels, alpha={alpha_min}..{alpha_max}")
        pixels_hash = digest(image.tobytes())
        histogram = alpha.histogram()
        boundary_alpha_gt8 = sum(
            value > 8
            for edge in (alpha.crop((0, 0, width, 1)), alpha.crop((0, height - 1, width, height)),
                         alpha.crop((0, 1, 1, height - 1)), alpha.crop((width - 1, 1, width, height - 1)))
            for value in edge.getdata()
        )
    return {
        "source": relative(source), "sourceSha256": source_hash,
        "sourcePixelSha256": pixels_hash, "sourceRecord": relative(record_path),
        "sourceRecordSha256": digest(record_path.read_bytes()), "sourceSize": [width, height],
        "alpha": {"min": alpha_min, "max": alpha_max,
                  "transparentPixelCount": histogram[0], "boundaryPixelsAbove8": boundary_alpha_gt8},
        "generation": record,
    }


def render(source: Path, expected_sha256: str) -> bytes:
    raw = confined(source).read_bytes()
    if digest(raw) != expected_sha256:
        raise ValueError(f"Source changed after preflight; rerun after generation finishes: {relative(source)}")
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        # One common canvas scale and translation for the complete batch.
        if image.size != (SIZE, SIZE):
            image = image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        if image.getchannel('A').crop((0, 0, SIZE, 20)).getextrema()[1] > 8:
            raise ValueError('Common translation would clip visible content; source must be redrawn')
        canvas = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
        canvas.paste(image, tuple(COMMON_TRANSLATION))
        image = canvas
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()


def check_existing(row: dict) -> None:
    target = confined(ROLE_ROOT / row["candidate"])
    target_record = confined(ROLE_ROOT / (row["candidate"] + ".generation.json"))
    if not target.exists():
        row["candidateStatus"] = "missing"
        return
    try:
        raw = target.read_bytes()
        record = json_read(target_record)
        with Image.open(io.BytesIO(raw)) as image:
            if image.mode != "RGBA" or image.size != (SIZE, SIZE):
                raise ValueError("Candidate size/mode mismatch")
        if record.get("sha256") != digest(raw):
            raise ValueError("Candidate SHA does not match derived record")
        if record.get("packageSchema") != SCHEMA:
            raise ValueError("Candidate has no matching private package record")
        if record.get("derivedFrom", [{}])[0].get("sha256") != row.get("sourceSha256"):
            raise ValueError("Candidate does not match selected source")
        if row["selectionStatus"] != "valid":
            raise ValueError("Candidate has no valid current selection")
        row["candidateStatus"] = "present_structurally_valid"
        row["candidateSha256"] = digest(raw)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        row["candidateStatus"] = "stale_or_invalid"
        row["candidateIssue"] = str(exc)


HTML = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>07 月影少女 · 独立跑步预览</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#171b25;color:#eef0f8;font:15px system-ui,sans-serif}
main{max-width:1120px;margin:auto;padding:24px}h1{font-size:23px;margin:0 0 8px}p{line-height:1.65}
.warning{padding:12px 16px;background:#4e3d22;border:1px solid #b18b48;border-radius:8px}
.controls{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:18px 0}button,select{font:inherit;background:#31384b;color:inherit;border:1px solid #79849d;border-radius:6px;padding:7px 12px;cursor:pointer}
button.active{background:#596789}label{display:flex;align-items:center;gap:7px}.stage{position:relative;flex:none;background-color:#353c4a;background-image:linear-gradient(45deg,#444c5d 25%,transparent 25%),linear-gradient(-45deg,#444c5d 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#444c5d 75%),linear-gradient(-45deg,transparent 75%,#444c5d 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0;overflow:hidden}
.stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.stage .ground{position:absolute;top:91.9921875%;left:0;width:100%;border-top:1px solid #ffcf65;z-index:2;pointer-events:none}.ground:after{content:'+';position:absolute;left:50%;top:-11px;color:#ffcf65;transform:translateX(-50%)}
.missing{position:absolute;inset:0;display:grid;place-content:center;text-align:center;padding:8px;color:#ffd9ac;background:#222936dd}.hero{display:flex;align-items:flex-start;gap:24px;flex-wrap:wrap}.details{flex:1;min-width:260px}code{overflow-wrap:anywhere}#range{width:300px;max-width:65vw}.strip{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}.tile{cursor:pointer}.caption{padding:7px 0;text-align:center}.foot{color:#b9c2d5;font-size:13px}#details{white-space:pre-wrap;overflow-wrap:anywhere}.issues{white-space:pre-wrap;color:#ffd9ac}
</style><main>
<h1>07 月影少女 · 八方向跑步候选</h1>
<p class="warning" id="status"></p>
<div class="controls" id="directions"></div>
<div class="controls"><button id="play">播放</button><button id="previous">上一帧</button><button id="next">下一帧</button>
<label>速度<select id="speed"><option value="30">正常 · 30ms/帧 · 480ms/圈</option><option value="120">慢速 · 120ms/帧 · 1920ms/圈</option></select></label>
<label>显示尺寸<select id="size"><option>128</option><option selected>256</option><option>512</option></select></label>
<label><input id="ground" type="checkbox" checked>地平线 / 固定根点</label></div>
<div class="controls"><input id="range" type="range" min="1" max="16" value="1"><output id="counter"></output></div>
<div class="hero"><div id="mainStage" class="stage"></div><div class="details"><h2 id="heading"></h2><p id="details"></p><p class="foot">源画布整体等比导出，根点 (512,942)，pivot (0.5,0.08)。保留原始相对位置、腾空与重心起伏。导出器不会判断肢体运动或修正脚底。</p><p class="foot">先看正常尺寸与速度，再放大慢速、拖动逐帧检查。缺帧位置显示缺失，不复用临近帧。</p></div></div>
<div id="strip" class="strip"></div><h2>结构问题与缺帧</h2><div id="issues" class="issues"></div>
<p class="foot">本页离线读取同目录相对路径，不使用 fetch。八方向各16帧；工具成功和不同SHA均不能证明动作美术通过。未接入客户端 / 未运行验收。</p>
</main><script>
const DATA=__DATA__;
const dirs=['N','NE','E','SE','S','SW','W','NW'];
const all=new Map(DATA.frames.map(row=>[row.direction+'/'+row.frame,row]));
let dir=DATA.frames.find(row=>row.candidateStatus==='present_structurally_valid')?.direction||'E',frame=1,playing=false,period=30,base=0,baseFrame=1;
const $=id=>document.getElementById(id),stages=[];
function stage(node,direction){const img=document.createElement('img');img.alt='';const floor=document.createElement('div');floor.className='ground';const absent=document.createElement('div');absent.className='missing';node.append(img,floor,absent);const item={node,img,floor,absent,direction};stages.push(item);return item;}
const mainStage=stage($('mainStage'),null);
for(const direction of dirs){const button=document.createElement('button');button.textContent=direction;button.onclick=()=>{dir=direction;paint()};button.dataset.dir=direction;$('directions').append(button);const tile=document.createElement('div');tile.className='tile';tile.onclick=()=>{dir=direction;paint()};const node=document.createElement('div');node.className='stage';node.style.width=node.style.height='128px';stage(node,direction);const caption=document.createElement('div');caption.className='caption';caption.textContent=direction;tile.append(node,caption);$('strip').append(tile);}
for(const row of DATA.frames){if(row.candidateStatus==='present_structurally_valid'){const preload=new Image();preload.src='../'+row.candidate;}}
function paint(){for(const item of stages){const row=all.get((item.direction||dir)+'/'+frame),available=row?.candidateStatus==='present_structurally_valid';item.img.hidden=!available;item.absent.hidden=available;item.absent.style.display=available?'none':'grid';if(available){const url='../'+row.candidate;if(item.img.getAttribute('src')!==url)item.img.src=url;}else item.absent.textContent=(item.direction||dir)+' / '+String(frame).padStart(2,'0')+'\n缺帧或结构未通过';item.floor.style.display=$('ground').checked?'':'none';}
$('range').value=frame;$('counter').textContent=String(frame).padStart(2,'0')+' / 16';$('heading').textContent=dir+' · 第 '+frame+' 帧';for(const button of $('directions').children)button.classList.toggle('active',button.dataset.dir===dir);const row=all.get(dir+'/'+frame);$('details').textContent=row.candidateStatus==='present_structurally_valid'?`候选：${row.candidate}\n源尺寸：${row.sourceSize.join(' × ')}\n候选 SHA256：${row.candidateSha256}\n来源：${row.sourceRecord}\n视觉验收：未由本工具执行`:`当前状态：${row.selectionStatus}\n${row.issue||row.candidateIssue||'尚未选择生成帧'}`;}
function stop(){playing=false;$('play').textContent='播放';}
function start(){playing=true;base=performance.now();baseFrame=frame;$('play').textContent='暂停';}
$('play').onclick=()=>playing?stop():start();$('previous').onclick=()=>{stop();frame=(frame+14)%16+1;paint()};$('next').onclick=()=>{stop();frame=frame%16+1;paint()};$('range').oninput=()=>{stop();frame=Number($('range').value);paint()};$('speed').onchange=()=>{period=Number($('speed').value);if(playing)start()};$('size').onchange=()=>{mainStage.node.style.width=mainStage.node.style.height=$('size').value+'px'};$('ground').onchange=paint;$('size').onchange();
function tick(now){if(playing){const next=(baseFrame-1+Math.floor((now-base)/period))%16+1;if(next!==frame){frame=next;paint()}}requestAnimationFrame(tick)}
$('status').textContent=`结构可用 ${DATA.counts.candidateValid}/128 帧；${DATA.counts.missing} 帧未选择，${DATA.counts.rejected} 帧选择被拒绝。${DATA.counts.candidateValid===128?'文件齐全，仍须独立动态视觉验收。':'未完整，不能作为完整动画交付。'} 视觉通过不由此工具判定。`;
$('issues').textContent=[...DATA.issues,...DATA.frames.filter(row=>row.candidateStatus!=='present_structurally_valid').map(row=>`${row.direction}/${String(row.frame).padStart(2,'0')}: ${row.issue||row.candidateIssue||row.selectionStatus}`)].join('\n')||'未发现结构问题；这不等于美术验收通过。';paint();requestAnimationFrame(tick);
</script></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="Explicitly write candidates, manifest.json, and offline preview")
    args = parser.parse_args()
    if ROLE_ROOT.name != CHARACTER or ROLE_ROOT.parent.name != "characters":
        parser.error("This script must stay in its assigned character's tools/ directory")
    timestamp = datetime.now(timezone.utc).isoformat()
    selection_path = confined(ROLE_ROOT / "generation/selection.json")
    issues = []
    selections = {}
    if selection_path.exists():
        try:
            selections = parse_selection(json_read(selection_path))
        except (OSError, ValueError, TypeError) as exc:
            issues.append(f"Invalid selection.json: {exc}")
    else:
        issues.append("generation/selection.json is missing; no sources automatically selected")
    rows = []
    inspected = {}
    for direction in DIRECTIONS:
        for frame in range(1, 17):
            key = (direction, frame)
            row = {"direction": direction, "frame": frame,
                   "candidate": f"candidate/walk/{direction}/{frame:02d}.png",
                   "selectionStatus": "missing", "visualStatus": "not_reviewed_by_exporter"}
            if key in selections:
                try:
                    result = source_inspection(selections[key])
                    inspected[key] = result
                    row.update({k: v for k, v in result.items() if k != "generation"})
                    row["selectionStatus"] = "valid"
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    row.update(selectionStatus="rejected", issue=str(exc))
            rows.append(row)
    canvas_sizes = {tuple(row["sourceSize"]) for row in rows if row["selectionStatus"] == "valid"}
    if len(canvas_sizes) > 1:
        issues.append(f"Mixed native canvas sizes are forbidden for a common fixed export scale: {sorted(canvas_sizes)}")
        for row in rows:
            if row["selectionStatus"] == "valid":
                row.update(selectionStatus="rejected", issue="Mixed source canvas sizes; no per-frame scale changes allowed")
    by_pixels = {}
    for row in rows:
        if row["selectionStatus"] == "valid":
            by_pixels.setdefault(row["sourcePixelSha256"], []).append(row)
    for group in by_pixels.values():
        if len(group) > 1:
            labels = ", ".join(f"{row['direction']}/{row['frame']:02d}" for row in group)
            for row in group:
                row.update(selectionStatus="rejected", issue=f"Identical source pixels selected more than once: {labels}")
    for row in rows:
        if args.write and row["selectionStatus"] == "valid":
            info = inspected[(row["direction"], row["frame"])]
            data = render(ROLE_ROOT / info["source"], info["sourceSha256"])
            atomic_write(ROLE_ROOT / row["candidate"], data)
            original = info["generation"]
            derived = {
                "packageSchema": SCHEMA, "file": row["candidate"], "sha256": digest(data),
                "derivedAt": timestamp, "width": SIZE, "height": SIZE, "format": "PNG", "mode": "RGBA",
                "derivedFrom": [{"file": info["source"], "sha256": info["sourceSha256"],
                                 "generationRecord": info["sourceRecord"], "generationRecordSha256": info["sourceRecordSha256"],
                                 "nativeWidth": info["sourceSize"][0], "nativeHeight": info["sourceSize"][1]}],
                "operation": {"type": "fixed_canvas_resize" if info["sourceSize"][0] != SIZE else "lossless_png_reencode",
                              "scale": SIZE / info["sourceSize"][0], "crop": None, "translation": COMMON_TRANSLATION,
                              "mirror": False, "poseInterpolation": False, "alphaBboxNormalization": False,
                              "lowestFootAlignment": False, "exportRoot": ROOT_POINT, "runtimePivot": PIVOT,
                              "resampler": "Pillow LANCZOS" if info["sourceSize"][0] != SIZE else None},
                "sourceConfigSnapshot": original["configSnapshot"],
                "sourceSubmittedParameters": original["submittedParameters"],
                "sourceActualModel": original["actualModel"], "sourceActualQuality": original["actualQuality"],
                "sourceUnverifiedReason": original.get("unverifiedReason"),
                "visualStatus": "not_reviewed_by_exporter",
            }
            json_write(ROLE_ROOT / (row["candidate"] + ".generation.json"), derived)
        check_existing(row)
    valid = sum(row["selectionStatus"] == "valid" for row in rows)
    rejected = sum(row["selectionStatus"] == "rejected" for row in rows)
    candidate_valid = sum(row["candidateStatus"] == "present_structurally_valid" for row in rows)
    planned = {row["candidate"] for row in rows}
    candidate_dir = confined(ROLE_ROOT / "candidate/walk")
    if candidate_dir.exists():
        unexpected = [relative(path) for path in candidate_dir.rglob("*.png") if relative(path) not in planned]
        if unexpected:
            issues.append("Unexpected candidate PNGs remain untouched: " + ", ".join(unexpected))
    manifest = {
        "schema": SCHEMA, "character": CHARACTER, "createdAt": timestamp,
        "mode": "write" if args.write else "read_only_check", "expectedFrameCount": 128,
        "frameMilliseconds": 30, "loopMilliseconds": 480, "slowFrameMilliseconds": 120,
        "directions": list(DIRECTIONS), "exportSize": [SIZE, SIZE], "exportRoot": ROOT_POINT, "runtimePivot": PIVOT,
        "runtimePixelsPerUnit": 104,
        "rootNote": "Fixed canvas/root contract; ALL frames shifted upward 20px after common full-canvas resize, mapping native ~94% plane to runtime ~92%. No per-frame bbox/foot alignment. Source root placement still requires visual review.",
        "commonTranslation": COMMON_TRANSLATION,
        "commonSourceSize": list(next(iter(canvas_sizes))) if len(canvas_sizes) == 1 else None,
        "counts": {"selected": len(selections), "sourceValid": valid, "missing": 128 - len(selections),
                   "rejected": rejected, "candidateValid": candidate_valid},
        "structureComplete": candidate_valid == 128 and not issues and rejected == 0,
        "visualAcceptance": "not_performed_by_exporter", "clientIntegration": "not_performed",
        "selection": "generation/selection.json", "selectionSha256": digest(selection_path.read_bytes()) if selection_path.exists() else None,
        "issues": issues, "frames": rows,
    }
    if args.write:
        json_write(ROLE_ROOT / "manifest.json", manifest)
        embedded = json.dumps(manifest, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        atomic_write(ROLE_ROOT / "preview/index.html", HTML.replace("__DATA__", embedded).encode("utf-8"))
    summary = {"mode": manifest["mode"], "counts": manifest["counts"], "structureComplete": manifest["structureComplete"],
               "visualAcceptance": manifest["visualAcceptance"], "issues": issues,
               "rejectedFrames": [{"direction": row["direction"], "frame": row["frame"], "issue": row["issue"]}
                                  for row in rows if row["selectionStatus"] == "rejected"]}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    # Incomplete is a distinct nonzero result; never print or return a false PASS.
    return 0 if manifest["structureComplete"] else 2 if rejected or issues else 1


if __name__ == "__main__":
    sys.exit(main())
