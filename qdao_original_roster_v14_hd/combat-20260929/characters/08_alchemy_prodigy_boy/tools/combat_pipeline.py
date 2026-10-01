#!/usr/bin/env python3
"""08-only evidence registration, explicit export, provenance audit and animation preview.

All writes are exclusive creation inside this character directory. No generation,
automatic selection, pose editing, mirror generation or framewise fitting occurs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image

CHARACTER = "08_alchemy_prodigy_boy"
ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT.parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
EXPECTED = {(a, d, i) for a, (n, _) in ACTIONS.items() for d in DIRECTIONS for i in range(1, n + 1)}
LABEL = re.compile(r"(hit|attack|cast)-(E|W)-(\d{2})-v([1-9]\d*)$")


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def local_path(value):
    p = Path(value)
    if not p.is_absolute():
        p = BATCH / p if p.parts and p.parts[0] == "characters" else ROOT / p
    p = p.resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError(f"Path escapes {CHARACTER}: {p}")
    return p


def relative(path):
    return path.resolve().relative_to(ROOT).as_posix()


def write_many(items):
    """Preflight every destination before first write; xb also rejects races."""
    resolved = [(local_path(path), data) for path, data in items]
    if len({p for p, _ in resolved}) != len(resolved):
        raise ValueError("Duplicate destination in write batch")
    for path, _ in resolved:
        if path.exists():
            raise ValueError(f"Refuse to overwrite: {path}")
    for path, data in resolved:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)


def field_at(data, pointer):
    if not pointer:
        return None
    current = data
    for key in pointer.strip("/").split("/"):
        key = key.replace("~1", "/").replace("~0", "~")
        current = current[int(key)] if isinstance(current, list) else current[key]
    if current is not None and not isinstance(current, (str, int, float)):
        raise ValueError(f"Expected scalar at response pointer {pointer}")
    return current


def inspect(path, need_runtime=False):
    with Image.open(path) as original:
        if original.format != "PNG" or original.mode != "RGBA":
            raise ValueError(f"Expected RGBA PNG: {path}")
        original.load()
        image = original.copy()
    if need_runtime and image.size != (1024, 1024):
        raise ValueError(f"Runtime must be 1024x1024: {path}")
    array = np.asarray(image)
    alpha = array[:, :, 3]
    if not np.any(alpha == 0):
        raise ValueError(f"No transparent pixels: {path}")
    ys, xs = np.where(alpha > 8)
    if not len(xs):
        raise ValueError(f"No visible subject: {path}")
    visible = array.copy()
    visible[alpha <= 8] = 0
    # Comparison normalizes hidden RGB and very faint noise; it never edits PNGs.
    stats = {
        "sha256": sha(path), "width": image.width, "height": image.height,
        "format": "PNG", "mode": "RGBA", "nativeCanvas": list(image.size),
        "visibleBBox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "transparentPixels": int(np.count_nonzero(alpha == 0)),
        "visibleTouchesEdge": bool(np.any(alpha[0] > 8) or np.any(alpha[-1] > 8)
                                   or np.any(alpha[:, 0] > 8) or np.any(alpha[:, -1] > 8)),
        "pixelSha256": digest(array.tobytes()),
        "visiblePixelSha256": digest(visible.tobytes()),
        "horizontalMirrorPixelSha256": digest(visible[:, ::-1].tobytes()),
        "comparisonAlphaThreshold": 8,
    }
    return image, stats


def register(args):
    match = LABEL.fullmatch(args.label)
    if not match or not 1 <= int(match[3]) <= ACTIONS[match[1]][0]:
        raise ValueError("Label must identify a valid slot and new version, e.g. hit-E-03-v1")
    request_raw = Path(args.request).read_bytes()
    response_raw = Path(args.response).read_bytes()
    prompt_raw = Path(args.prompt).read_bytes()
    config_raw = Path(args.config).read_bytes()
    refs_raw = Path(args.references).read_bytes()
    request, response = json.loads(request_raw), json.loads(response_raw)
    config, references = json.loads(config_raw), json.loads(refs_raw)
    if not isinstance(request, dict) or not isinstance(config, dict):
        raise ValueError("Request and config must be JSON objects")
    prompt = prompt_raw.decode("utf-8-sig")
    if request.get("prompt") != prompt:
        raise ValueError("Prompt file must match the actual submitted request.prompt exactly")
    if not isinstance(references, list) or not references:
        raise ValueError("References must be a nonempty list of {path, role}")
    request_refs = request.get("referenced_image_paths")
    if not isinstance(request_refs, list):
        raise ValueError("This local-reference registrar requires actual referenced_image_paths")
    if [str(Path(ref["path"]).resolve()) for ref in references] != [str(Path(p).resolve()) for p in request_refs]:
        raise ValueError("Reference roles must describe exactly the submitted references in order")
    for ref in references:
        if not ref.get("role"):
            raise ValueError("Each reference needs a concrete role")
        ref["sha256AtRegistration"] = sha(Path(ref["path"]))
    evidence_dir = ROOT / "provenance" / "evidence" / args.label
    documents = {"request.json": request_raw, "response.json": response_raw,
                 "prompt.txt": prompt_raw, "config.json": config_raw, "references.json": refs_raw}
    items = [(evidence_dir / name, raw) for name, raw in documents.items()]
    actual_model = field_at(response, args.model_pointer)
    actual_quality = field_at(response, args.quality_pointer)
    submitted = dict(request)
    submitted.setdefault("model", None)
    submitted.setdefault("quality", None)
    record = {
        "schemaVersion": 1, "character": CHARACTER, "label": args.label,
        "recordedAt": utc(), "tool": "image_gen.imagegen", "route": "builtin",
        "configSnapshot": config, "submittedParameters": submitted,
        "actualModel": actual_model, "actualQuality": actual_quality,
        "unverifiedReason": "Host managed. Any null actual model/quality was not verified from returned metadata; prompt/config targets are not return evidence.",
        "prompt": relative(evidence_dir / "prompt.txt"), "references": references,
        "evidence": {name: {"file": relative(evidence_dir / name), "sha256": digest(raw)}
                     for name, raw in documents.items()},
        "actualFieldPointers": {"model": args.model_pointer, "quality": args.quality_pointer},
        "review": {"status": "pending"}, "clientIntegration": "not_integrated",
    }
    if args.source:
        source = Path(args.source).resolve()
        _, stats = inspect(source)
        if stats["width"] < 1024 or stats["height"] < 1024:
            raise ValueError("Native source is below 1024 in one dimension; do not label enlarged cells as HD")
        dest = ROOT / "staging" / (args.label + ".png")
        raw = source.read_bytes()
        record.update(file=relative(dest), sha256=digest(raw), width=stats["width"],
                      height=stats["height"], format="PNG", pngColorType=6,
                      nativeGeometry=stats, status="candidate_pending_visual_review",
                      generatedAt=datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
                      generatedAtEvidence="Source file mtime in UTC; not a tool-supplied generation timestamp.",
                      source={"kind": "generated", "generated_image_path": str(source),
                              "registeredCopyOperation": "byte-identical copy", "originalSha256": digest(raw)})
        items.append((dest, raw))
        record_path = ROOT / "provenance" / "receipts" / (args.label + ".json")
    else:
        if not args.failure:
            raise ValueError("Use --source for success or --failure for a failed attempt")
        record.update(status="failed_attempt", failure=args.failure)
        record_path = ROOT / "provenance" / "attempts" / (args.label + ".json")
    items.append((record_path, json_bytes(record)))
    write_many(items)
    print(json.dumps({"receipt": str(record_path), "status": record["status"],
                      "actualModel": actual_model, "actualQuality": actual_quality}, ensure_ascii=False))


def verify_evidence(record):
    for name, item in record.get("evidence", {}).items():
        if isinstance(item, dict) and "file" in item and "sha256" in item:
            p = local_path(item["file"])
            if not p.is_file() or sha(p) != item["sha256"]:
                raise ValueError(f"Evidence missing/hash mismatch: {name}: {p}")


def verify_generation(source, receipt):
    data = read_json(receipt)
    if local_path(data["file"]) != source:
        raise ValueError(f"Generation record identifies a different source: {receipt}")
    if data.get("sha256") != sha(source):
        raise ValueError(f"Source receipt hash mismatch: {receipt}")
    for key in ("generatedAt", "generatedAtEvidence", "tool", "route", "configSnapshot",
                "submittedParameters", "evidence", "prompt", "references", "actualModel", "actualQuality"):
        if key not in data:
            raise ValueError(f"Generation record lacks {key}: {receipt}")
    if not data["prompt"] or not data["references"]:
        raise ValueError(f"Empty generation prompt/references: {receipt}")
    if (data["actualModel"] is None or data["actualQuality"] is None) and not data.get("unverifiedReason"):
        raise ValueError(f"Unverified model/quality needs reason: {receipt}")
    verify_evidence(data)
    if isinstance(data.get("evidence", {}).get("request.json"), dict):
        actual_request = read_json(local_path(data["evidence"]["request.json"]["file"]))
        submitted = dict(actual_request)
        submitted.setdefault("model", None)
        submitted.setdefault("quality", None)
        if data["submittedParameters"] != submitted:
            raise ValueError(f"Recorded parameters differ from original request: {receipt}")
        prompt_path = local_path(data["prompt"])
        if actual_request.get("prompt") != prompt_path.read_text(encoding="utf-8-sig"):
            raise ValueError(f"Prompt differs from original request: {receipt}")
    return data


def selections(paths):
    result, seen_slots, seen_sources = [], set(), set()
    for value in paths:
        selection_path = local_path(value)
        data = read_json(selection_path)
        groups = data["groups"] if isinstance(data, dict) and "groups" in data else [data]
        if isinstance(data, dict) and data.get("status") == "partial":
            raise ValueError(f"Partial selection cannot be exported: {selection_path}")
        for group in groups:
            action, direction = group.get("action"), group.get("direction")
            if action not in ACTIONS or direction not in DIRECTIONS:
                raise ValueError(f"Unknown selection group: {selection_path}")
            count = ACTIONS[action][0]
            frames = group.get("frames", [])
            if group.get("status") == "partial" or [x.get("frame") for x in frames] != list(range(1, count + 1)):
                raise ValueError(f"Require explicit complete ordered frames 1..{count}: {selection_path}")
            for frame in frames:
                key = (action, direction, frame["frame"])
                source = local_path(frame["file"])
                receipt = local_path(frame["generationRecord"])
                if key in seen_slots or source in seen_sources:
                    raise ValueError(f"Duplicate selected slot or source: {key}")
                seen_slots.add(key)
                seen_sources.add(source)
                source_sha = sha(source)
                if frame.get("sha256") != source_sha:
                    raise ValueError(f"Selection must include matching source SHA256: {key}")
                generation = verify_generation(source, receipt)
                image, stats = inspect(source)
                if image.width < 1024 or image.height < 1024 or stats["visibleTouchesEdge"]:
                    raise ValueError(f"Native input too small or visible content touches edge: {source}")
                result.append({"key": key, "source": source, "receipt": receipt, "image": image,
                               "stats": stats, "generation": generation, "selection": selection_path})
    if seen_slots != EXPECTED:
        raise ValueError(f"Export requires all 68 explicit slots; present={len(seen_slots)}, missing={sorted(EXPECTED-seen_slots)}")
    return result


def transform_config(value):
    if value == "identity":
        return {d: {"nativeCanvas": [1024, 1024], "scale": 1.0, "offset": [0, 0]} for d in DIRECTIONS}
    data = read_json(local_path(value))
    if set(data) != set(DIRECTIONS):
        raise ValueError("Fixed transform JSON requires exactly E and W; each applies to all three actions")
    for d in DIRECTIONS:
        t = data[d]
        if not (isinstance(t.get("nativeCanvas"), list) and len(t["nativeCanvas"]) == 2
                and all(isinstance(n, int) and n >= 1024 for n in t["nativeCanvas"])):
            raise ValueError("Each transform needs nativeCanvas [width,height] >=1024")
        if not 0 < t.get("scale", 0) <= 1:
            raise ValueError("Scale must be >0 and <=1; no upscaling")
        if not (isinstance(t.get("offset"), list) and len(t["offset"]) == 2
                and all(isinstance(n, int) for n in t["offset"])):
            raise ValueError("Each transform needs fixed integer offset [x,y]")
    return data


def render_frame(image, transform):
    if list(image.size) != transform["nativeCanvas"]:
        raise ValueError("Native size differs from explicit fixed transform")
    scale, offset = transform["scale"], transform["offset"]
    target = (round(image.width * scale), round(image.height * scale))
    scaled = image if scale == 1 else image.resize(target, Image.Resampling.LANCZOS)
    box = scaled.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    if box is None or box[0]+offset[0] < 0 or box[1]+offset[1] < 0 or box[2]+offset[0] > 1024 or box[3]+offset[1] > 1024:
        raise ValueError("Fixed transform would clip visible content")
    output = Image.new("RGBA", (1024, 1024))
    output.paste(scaled, tuple(offset))
    raw = io.BytesIO()
    output.save(raw, format="PNG")
    array = np.asarray(output).copy()
    array[array[:, :, 3] <= 8] = 0
    return raw.getvalue(), digest(array.tobytes()), digest(array[:, ::-1].tobytes())


def export(args):
    frames = selections(args.selection)
    transforms = transform_config(args.transform)
    items, pixel_hashes, mirror_hashes = [], {}, {}
    for row in frames:
        action, direction, number = row["key"]
        raw, pixel_sha, mirror_sha = render_frame(row["image"], transforms[direction])
        if pixel_sha in pixel_hashes or pixel_sha in mirror_hashes:
            raise ValueError(f"Duplicate or exact mirrored rendered content at {row['key']}")
        pixel_hashes[pixel_sha] = row["key"]
        mirror_hashes[mirror_sha] = row["key"]
        dest = ROOT / "runtime" / action / direction / f"{number:02d}.png"
        receipt = ROOT / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{number:02d}.json"
        source = row["generation"]
        record = {
            "schemaVersion": 1, "file": relative(dest), "sha256": digest(raw), "derivedAt": utc(),
            "generatedAt": source["generatedAt"], "width": 1024, "height": 1024, "format": "PNG RGBA",
            "tool": "Pillow deterministic export", "route": "derived",
            "actualModel": source["actualModel"], "actualQuality": source["actualQuality"],
            "unverifiedReason": source.get("unverifiedReason"), "configSnapshot": source["configSnapshot"],
            "prompt": source["prompt"], "references": source["references"],
            "derivedFrom": {"file": relative(row["source"]), "sha256": row["stats"]["sha256"],
                            "generationRecord": relative(row["receipt"]), "generationRecordSha256": sha(row["receipt"])},
            "selection": {"file": relative(row["selection"]), "sha256": sha(row["selection"])},
            "operation": {"kind": "fixed_whole_canvas_export", "transform": transforms[direction],
                          "filter": "identity" if transforms[direction]["scale"] == 1 else "Pillow LANCZOS",
                          "alphaCleanup": "none", "framewiseFitting": False, "poseSynthesis": False, "mirror": False},
            "nativeGeometry": row["stats"], "visualApproval": "pending", "clientIntegration": "not_integrated",
        }
        items.extend([(dest, raw), (receipt, json_bytes(record))])
    for path, _ in items:
        if path.exists():
            raise ValueError(f"Refuse to overwrite runtime or receipt: {path}")
    if args.publish:
        write_many(items)
    print(json.dumps({"character": CHARACTER, "selectedSlots": len(frames), "technicalPreflight": "passed",
                      "export": "written" if args.publish else "dry_run", "transforms": transforms,
                      "visualApproval": "pending", "clientIntegration": "not_integrated"}, ensure_ascii=False, indent=2))


def verify_chain(path, receipt):
    data = read_json(receipt)
    if local_path(data["file"]) != path or data.get("sha256") != sha(path):
        raise ValueError("Derived record target path/hash mismatch")
    origin = data["derivedFrom"]
    source, source_record = local_path(origin["file"]), local_path(origin["generationRecord"])
    if sha(source) != origin["sha256"] or sha(source_record) != origin["generationRecordSha256"]:
        raise ValueError("Derived source/source-record hash mismatch")
    generation = verify_generation(source, source_record)
    choice = data["selection"]
    if sha(local_path(choice["file"])) != choice["sha256"]:
        raise ValueError("Explicit selection hash mismatch")
    if not data.get("operation"):
        raise ValueError("Derived record has no operation")
    if data.get("actualModel") != generation.get("actualModel") or data.get("actualQuality") != generation.get("actualQuality"):
        raise ValueError("Derived model/quality differs from original evidence")
    source_image, _ = inspect(source)
    recreated, _, _ = render_frame(source_image, data["operation"]["transform"])
    if digest(recreated) != data["sha256"]:
        raise ValueError("Derived PNG does not reproduce from recorded fixed transform")
    return data


def preview_html(manifest, destination):
    groups = []
    for action, (count, ms) in ACTIONS.items():
        for direction in DIRECTIONS:
            rows = [r for r in manifest["frames"] if r["action"] == action and r["direction"] == direction]
            groups.append({"label": f"{action}/{direction}", "ms": ms, "count": count,
                           "frames": [Path(os.path.relpath(local_path(r["file"]), destination)).as_posix() if r["exists"] else None for r in rows]})
    data = json.dumps(groups, ensure_ascii=False).replace("<", "\\u003c")
    return PREVIEW.replace("__SETS__", data)


def audit(args):
    frames, seen_pixels, seen_mirrors, issues, transforms = [], {}, {}, [], {}
    for action, (count, ms) in ACTIONS.items():
        for direction in DIRECTIONS:
            for number in range(1, count + 1):
                path = ROOT / "runtime" / action / direction / f"{number:02d}.png"
                receipt = ROOT / "provenance" / "receipts" / "derived" / f"{action}-{direction}-{number:02d}.json"
                row = {"action": action, "direction": direction, "frame": number, "file": relative(path),
                       "exists": path.is_file(), "frameDurationMs": ms, "issues": []}
                if not path.is_file():
                    row["issues"].append("missing_frame")
                else:
                    try:
                        _, stats = inspect(path, need_runtime=True)
                        row.update(stats)
                        if stats["visibleTouchesEdge"]:
                            row["issues"].append("visible_content_touches_edge")
                        key = stats["visiblePixelSha256"]
                        if key in seen_pixels:
                            row["issues"].append("duplicate_visible_pixels:" + seen_pixels[key])
                        if key in seen_mirrors:
                            row["issues"].append("exact_horizontal_mirror:" + seen_mirrors[key])
                        seen_pixels[key] = row["file"]
                        seen_mirrors[stats["horizontalMirrorPixelSha256"]] = row["file"]
                        record = verify_chain(path, receipt)
                        transform = record["operation"]["transform"]
                        if direction in transforms and transforms[direction] != transform:
                            raise ValueError("Direction does not use one fixed transform across all actions")
                        transforms[direction] = transform
                        row.update(generationRecord=relative(receipt), actualModel=record.get("actualModel"),
                                   actualQuality=record.get("actualQuality"), derivedFrom=record["derivedFrom"])
                    except (ValueError, OSError, KeyError, TypeError) as error:
                        row["issues"].append(str(error))
                frames.append(row)
    expected_paths = {local_path(r["file"]) for r in frames}
    for p in (ROOT / "runtime").rglob("*.png"):
        if p.resolve() not in expected_paths:
            issues.append("unexpected_runtime_png:" + relative(p))
    passed = not issues and not any(r["issues"] for r in frames)
    manifest = {"schemaVersion": 1, "character": CHARACTER, "recordedAt": utc(),
                "summary": {"expected": 68, "present": sum(r["exists"] for r in frames),
                            "framesWithIssues": sum(bool(r["issues"]) for r in frames), "technicalAuditPassed": passed},
                "technicalStatus": "passed" if passed else "incomplete_or_invalid", "visualApproval": "pending",
                "clientIntegration": "not_integrated", "clientRuntimeAcceptance": "not_tested",
                "limitations": "Distinct pixels and exact-mirror checks do not prove distinct poses, correct anatomy, fixed handedness or animation continuity. Playback must be watched.",
                "issues": issues, "frames": frames}
    if args.out:
        out = local_path(args.out)
        if out.exists():
            raise ValueError(f"Audit output must be a new directory: {out}")
        checklist = {"status": "pending", "reviewer": None, "reviewedAt": None,
                     "sequences": [{"action": a, "direction": d, "normalFrameMs": ms,
                                    "normalSequenceMs": n*ms, "normalDark": "pending", "normalLight": "pending",
                                    "slow0_25xDark": "pending", "slow0_25xLight": "pending",
                                    "identityHandednessProps": "pending", "scaleRootFootSlide": "pending",
                                    "limbsClippingEdges": "pending", "startEndContinuity": "pending", "notes": ""}
                                   for a, (n, ms) in ACTIONS.items() for d in DIRECTIONS],
                     "suggestedContactReleaseFrames": "pending_actual_visual_review",
                     "clientIntegration": "not_integrated", "clientRuntimeAcceptance": "not_tested"}
        write_many([(out / "manifest.json", json_bytes(manifest)),
                    (out / "index.html", preview_html(manifest, out).encode("utf-8")),
                    (out / "visual-review-pending.json", json_bytes(checklist))])
    print(json.dumps({"output": str(local_path(args.out)) if args.out else None, **manifest["summary"],
                      "visualApproval": "pending", "clientIntegration": "not_integrated"}, ensure_ascii=False))
    return 0 if passed or args.allow_incomplete else 2


PREVIEW = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>08 炼丹童子 · 六段动作连播验收</title>
<style>body{font:16px system-ui;margin:24px;background:#20272c;color:#edf4f1}h1{font-size:24px}
button,select,input{font:inherit;padding:6px;margin:4px}#stages{display:flex;gap:18px;flex-wrap:wrap}
.stage{width:min(42vw,620px);height:min(42vw,620px);min-width:290px;min-height:290px;position:relative}
.stage img{width:100%;height:100%;object-fit:contain}.light{background:#fff}.dark{background:#0b0f14}
.stage:after{content:attr(data-label);position:absolute;top:7px;left:8px;color:#79858c;font-size:12px}
#status{font-variant-numeric:tabular-nums;padding:14px 0}small{display:block;line-height:1.6}</style>
<h1>08 炼丹童子：六段动作连播</h1>
<p>技术预览；视觉审核 pending，客户端未接入、未运行测试。深浅底同时显示。</p>
<select id="group"></select><select id="speed"><option value="1">正常 1.00x</option><option value="0.25">慢放 0.25x（每帧时长×4）</option></select>
<button id="all">六段顺序连播</button><button id="single">当前段循环</button><button id="stop">暂停</button>
<button id="prev">上一帧</button><button id="next">下一帧</button><input id="frame" type="range" min="0" value="0">
<div id="status"></div><div id="stages"><div class="stage light" data-label="白底"><img id="light"></div><div class="stage dark" data-label="深底"><img id="dark"></div></div>
<small>正常速度：受击40ms/帧（240ms），普攻30ms/帧（360ms），施法45ms/帧（720ms）。<br>
审阅起止衔接、身体比例、地根和脚滑、解剖右手丹炉/左手药瓶、背篓卷轴、服装闪变、轮廓裁切及透明边缘。
浏览器刷新频率会量化显示时刻；本页按累计时间计算目标帧，显示实际播放状态，不能自行证明美术通过。</small>
<script>const sets=__SETS__;const $=id=>document.getElementById(id);let gi=0,fi=0,running=false,all=false,start=0,raf=0;
sets.forEach((s,i)=>{const o=document.createElement('option');o.value=i;o.textContent=s.label;$('group').append(o)});
function show(){const s=sets[gi],url=s.frames[fi];$('group').value=gi;$('frame').max=s.count-1;$('frame').value=fi;
['light','dark'].forEach(id=>{if(url){$(id).src=url;$(id).style.visibility='visible'}else $(id).style.visibility='hidden'});
const speed=+$('speed').value;$('status').textContent=`${running?'播放中':'暂停'} · ${s.label} · ${fi+1}/${s.count} · ${speed.toFixed(2)}x · ${s.ms/speed}ms/帧 · ${s.ms*s.count/speed}ms/段${url?'':' · 缺帧，未通过'}`;}
function stop(){running=false;cancelAnimationFrame(raf);show()}
function tick(now){if(!running)return;const speed=+$('speed').value;let elapsed=now-start;
while(elapsed>=sets[gi].count*sets[gi].ms/speed){const duration=sets[gi].count*sets[gi].ms/speed;start+=duration;elapsed-=duration;if(all)gi=(gi+1)%sets.length;}
fi=Math.min(sets[gi].count-1,Math.floor(elapsed/(sets[gi].ms/speed)));show();raf=requestAnimationFrame(tick)}
async function play(playAll){stop();all=playAll;if(all)gi=0;fi=0;show();
const chosen=all?sets:[sets[gi]];if(chosen.some(s=>s.frames.some(p=>!p))){$('status').textContent+=' · 所选范围缺帧，拒绝播放';return;}
try{await Promise.all(chosen.flatMap(s=>s.frames).map(src=>new Promise((ok,no)=>{const i=new Image();i.onload=ok;i.onerror=()=>no(Error(src));i.src=src})));}
catch(e){$('status').textContent='图片读取失败：'+e.message;return}running=true;start=performance.now();raf=requestAnimationFrame(tick)}
$('all').onclick=()=>play(true);$('single').onclick=()=>play(false);$('stop').onclick=stop;
$('group').onchange=()=>{const value=+$('group').value;stop();gi=value;fi=0;show()};$('speed').onchange=()=>{const was=running;stop();if(was)play(all);else show()};
$('frame').oninput=()=>{const value=+$('frame').value;stop();fi=value;show()};$('prev').onclick=()=>{stop();fi=(fi+sets[gi].count-1)%sets[gi].count;show()};
$('next').onclick=()=>{stop();fi=(fi+1)%sets[gi].count;show()};document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});show();</script></html>'''


def main():
    if ROOT.name != CHARACTER:
        raise ValueError("Tool must remain in its 08 character/tools directory")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("register", help="Preserve actual request/response and register an unchanged built-in PNG")
    for key in ("label", "request", "response", "prompt", "config", "references"):
        r.add_argument("--" + key, required=True)
    mode = r.add_mutually_exclusive_group(required=True)
    mode.add_argument("--source", help="Exact local PNG returned by image_gen")
    mode.add_argument("--failure", help="Actual failure description; registers no candidate")
    r.add_argument("--model-pointer", help="JSON pointer to an actual returned model field; omit if undisclosed")
    r.add_argument("--quality-pointer", help="JSON pointer to an actual returned quality field; omit if undisclosed")
    r.set_defaults(func=register)
    e = sub.add_parser("export", help="Read all 68 explicit slots; dry-run unless --publish")
    e.add_argument("--selection", nargs="+", required=True)
    e.add_argument("--transform", default="identity", help="identity or character-local fixed E/W transform JSON")
    e.add_argument("--publish", action="store_true")
    e.set_defaults(func=export)
    a = sub.add_parser("audit", help="Read runtime+full source chain; optional fresh output dir")
    a.add_argument("--out", help="New character-local output directory; omit for read-only summary")
    a.add_argument("--allow-incomplete", action="store_true", help="Only changes exit status, never report")
    a.set_defaults(func=audit)
    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"combat_pipeline: {error}", file=sys.stderr)
        raise SystemExit(2)
