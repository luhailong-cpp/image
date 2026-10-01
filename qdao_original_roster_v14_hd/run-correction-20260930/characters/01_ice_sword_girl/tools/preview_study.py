#!/usr/bin/env python3
"""Build a diagnostic 16-cell study preview, never deliverable animation frames.

The source is split with floor(i * actual_dimension / 4). Native 313/314-pixel
crops are preserved. APNG uses transparent right/bottom padding to 314 square;
there is no resize, alignment, cleanup, interpolation or artistic approval.
Default is a dry run. --write only writes preview/study16 under this character.
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
import sys
import uuid

sys.dont_write_bytecode = True
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZED_ROOT = Path("D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/run-correction-20260930/characters/01_ice_sword_girl").resolve()
OUTPUT = ROOT / "preview/study16"
SOURCE = ROOT / "generation/E/study16-v1.png"


def guarded_output(path: Path) -> Path:
    resolved = path.resolve()
    if ROOT != AUTHORIZED_ROOT or not OUTPUT.resolve().is_relative_to(ROOT) or not resolved.is_relative_to(OUTPUT.resolve()):
        raise ValueError(f"Output escaped preview/study16: {resolved}")
    return resolved


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def as_png(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=False)
    return stream.getvalue()


def as_apng(images: list[Image.Image], duration: int) -> bytes:
    stream = io.BytesIO()
    images[0].save(stream, format="PNG", save_all=True, append_images=images[1:],
                   duration=[duration] * len(images), loop=0,
                   disposal=[0] * len(images), blend=[0] * len(images),
                   default_image=False, optimize=False)
    data = stream.getvalue()
    # Decode each APNG frame and check both actual timing and retained pixels.
    with Image.open(io.BytesIO(data)) as animation:
        if animation.n_frames != len(images):
            raise ValueError("APNG frame count mismatch")
        for index, expected in enumerate(images):
            animation.seek(index)
            if animation.info.get("duration") != duration:
                raise ValueError(f"APNG duration mismatch at frame {index + 1}")
            if animation.convert("RGBA").tobytes() != expected.tobytes():
                raise ValueError(f"APNG decoded pixels mismatch at frame {index + 1}")
    return data


HTML = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>01 冰剑少女 · 16格跑步研究诊断</title>
<style>
body{margin:24px;background:#18202b;color:#edf3fa;font:15px system-ui,sans-serif;line-height:1.6}h1{font-size:23px}
p{max-width:1000px}.warning{color:#ffca78}.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:18px 0}
button,select{font:inherit;padding:7px 12px;background:#29364a;color:white;border:1px solid #63728a;border-radius:5px}
input[type=range]{width:280px}.stage{position:relative;width:__CANVAS_W__px;height:__CANVAS_H__px;background:repeating-conic-gradient(#c7cdd6 0 25%,#e0e3e9 0 50%) 0/20px 20px;overflow:hidden}
.stage img{position:absolute;left:0;top:0;max-width:none;image-rendering:auto}.readout{font-family:monospace}a{color:#97c8ff}
pre{white-space:pre-wrap;word-break:break-word;max-width:1000px}.status{padding:10px;border:1px solid #bd8747;max-width:970px}
</style>
<h1>01 冰剑少女 · 16格跑步研究诊断</h1>
<p class="warning status">仅供研究：原生整图 __SOURCE_W__×__SOURCE_H__，4×4 名义等分切片只有 313/314 像素，不是原生 HD 帧。格界会切断部分人物，也可能带入邻格碎片。未纠正构图、未补画、未验收、未导出正式动画、未接入客户端。</p>
<p>此处按原图行优先顺序显示 01–16，用于检查重复摆臂、持物手归属与腿部变化。格子顺序不证明它们构成正确的两步跑循环。没有虚构的地面线或根点。</p>
<div class="controls"><button id="play">暂停</button><button id="prev">上一格</button><button id="next">下一格</button>
<select id="speed"><option value="30">原速 30 ms/格 · 480 ms/圈</option><option value="120">慢速 120 ms/格 · 1920 ms/圈</option></select>
<input id="slider" type="range" min="0" max="15" value="0"><span id="counter"></span></div>
<div class="stage"><img id="frame" alt="原生尺寸研究切片"></div><p class="readout" id="dimensions"></p>
<p>画面以原生切片尺寸 1:1 显示；313 像素格只在右侧或底部留透明空白，未放大至 314。左右方向键逐格，空格暂停/播放。以上预览自包含，离线打开有效。</p>
<p><a href="normal-30ms.png">APNG 原速</a> · <a href="slow-120ms.png">APNG 慢速</a> · <a href="derived.json">逐格裁切来源</a></p>
<details><summary>诊断边界</summary><pre id="metadata"></pre></details>
<script>
const data=__DATA__,q=id=>document.getElementById(id);let index=0,playing=true,last=performance.now(),accumulator=0;
for(const f of data.frames){const preload=new Image();preload.src=f.dataUrl;}
q('metadata').textContent=JSON.stringify(data.contract,null,2);
function show(){const f=data.frames[index];q('frame').src=f.dataUrl;q('frame').width=f.width;q('frame').height=f.height;q('slider').value=index;q('counter').textContent=`${String(f.frame).padStart(2,'0')} / 16`;q('dimensions').textContent=`原生 ${f.width}×${f.height} · crop [${f.cropBox.join(', ')}] · 边界 alpha>8 像素 ${f.boundaryAlphaGt8Pixels}`;}
function pause(){playing=false;q('play').textContent='播放';accumulator=0;}
function step(n){pause();index=(index+n+16)%16;show();}
q('play').onclick=()=>{playing=!playing;q('play').textContent=playing?'暂停':'播放';accumulator=0;last=performance.now();};
q('prev').onclick=()=>step(-1);q('next').onclick=()=>step(1);q('slider').oninput=()=>{pause();index=Number(q('slider').value);show();};
q('speed').onchange=()=>{accumulator=0;last=performance.now();};
document.onkeydown=e=>{if(e.code==='ArrowLeft'){e.preventDefault();step(-1);}if(e.code==='ArrowRight'){e.preventDefault();step(1);}if(e.code==='Space'){e.preventDefault();q('play').click();}};
function tick(now){if(playing){accumulator+=Math.min(now-last,250);const duration=Number(q('speed').value),steps=Math.floor(accumulator/duration);if(steps){index=(index+steps)%16;accumulator-=steps*duration;show();}}last=now;requestAnimationFrame(tick);}
show();requestAnimationFrame(tick);
</script></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    guarded_output(OUTPUT)
    if not SOURCE.resolve().is_relative_to(ROOT):
        raise ValueError("Source path escapes character root")
    source_bytes = SOURCE.read_bytes()
    source_sha = sha(source_bytes)
    with Image.open(io.BytesIO(source_bytes)) as image:
        image.load()
        if image.format != "PNG" or image.mode != "RGBA":
            raise ValueError("Study source must be native RGBA PNG")
        source = image.copy()
    if source.size != (1254, 1254):
        raise ValueError(f"This explicit study recipe expects 1254 square; got {source.size}")
    xs = [i * source.width // 4 for i in range(5)]
    ys = [i * source.height // 4 for i in range(5)]
    canvas = (max(xs[i + 1] - xs[i] for i in range(4)), max(ys[i + 1] - ys[i] for i in range(4)))
    outputs, records, frames, playback_images = {}, [], [], []
    for row in range(4):
        for column in range(4):
            number = row * 4 + column + 1
            box = (xs[column], ys[row], xs[column + 1], ys[row + 1])
            crop = source.crop(box)
            data = as_png(crop)
            path = guarded_output(OUTPUT / f"{number:02d}.png")
            outputs[path] = data
            alpha = crop.getchannel("A")
            border = alpha.crop((0, 0, crop.width, 1)).tobytes() + alpha.crop((0, crop.height - 1, crop.width, crop.height)).tobytes()
            border += alpha.crop((0, 1, 1, crop.height - 1)).tobytes() + alpha.crop((crop.width - 1, 1, crop.width, crop.height - 1)).tobytes()
            boundary_count = sum(value > 8 for value in border)
            record = {"frame": number, "file": path.name, "sha256": sha(data),
                      "width": crop.width, "height": crop.height, "mode": crop.mode,
                      "sourceFile": "generation/E/study16-v1.png", "sourceSHA256": source_sha,
                      "cropBoxXyxyExclusive": list(box), "operation": "integer_crop_only",
                      "boundaryAlphaGt8Pixels": boundary_count,
                      "boundaryInterpretation": "Occupied crop boundary flags a possible cut silhouette or neighbor fragment; no pixels removed.",
                      "researchOnly": True, "nativeHDFrame": False, "visualPassed": False,
                      "formalExported": False, "fillsCandidateSlot": False}
            records.append(record)
            frames.append({"frame": number, "width": crop.width, "height": crop.height,
                           "cropBox": list(box), "boundaryAlphaGt8Pixels": boundary_count,
                           "dataUrl": "data:image/png;base64," + base64.b64encode(data).decode("ascii")})
            padded = Image.new("RGBA", canvas, (0, 0, 0, 0))
            padded.paste(crop, (0, 0))
            playback_images.append(padded)
    animation_records = []
    for duration, name in ((30, "normal-30ms.png"), (120, "slow-120ms.png")):
        data = as_apng(playback_images, duration)
        outputs[guarded_output(OUTPUT / name)] = data
        animation_records.append({"file": name, "sha256": sha(data), "format": "APNG",
                                  "frameCount": 16, "frameDurationMs": duration,
                                  "cycleDurationMs": duration * 16, "loop": "infinite",
                                  "canvas": list(canvas), "placement": "native crop at top-left, transparent padding only on right/bottom",
                                  "resampled": False, "decodedFramesAndTimingVerified": True})
    contract = {"characterId": "01_ice_sword_girl", "purpose": "Research diagnosis of repeated arms and gait in a generated 4x4 sheet, not accepted HD frames.",
                "sourceSHA256": source_sha, "sourceDimensions": list(source.size),
                "xBoundaries": xs, "yBoundaries": ys, "boundaryFormula": "floor(i * actualDimension / 4)",
                "groundOrRootInvented": False, "resizeOrAlignment": False,
                "normalFrameDurationMs": 30, "normalCycleDurationMs": 480,
                "slowFrameDurationMs": 120, "slowCycleDurationMs": 1920,
                "visualPassed": 0, "formalExported": 0, "clientIntegrated": False,
                "limitation": "Equal grid cuts through some characters. Small cells and truncated silhouettes are retained as diagnostic evidence, never upscaled or promoted to candidate/walk."}
    html = HTML.replace("__CANVAS_W__", str(canvas[0])).replace("__CANVAS_H__", str(canvas[1]))
    html = html.replace("__SOURCE_W__", str(source.width)).replace("__SOURCE_H__", str(source.height))
    html = html.replace("__DATA__", json.dumps({"contract": contract, "frames": frames}, ensure_ascii=False).replace("</", "<\\/"))
    html_bytes = html.encode("utf-8")
    outputs[guarded_output(OUTPUT / "index.html")] = html_bytes
    derived = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
               "source": {"file": str(SOURCE), "sha256": source_sha, "width": source.width, "height": source.height, "mode": source.mode},
               "contract": contract, "crops": records, "animations": animation_records,
               "preview": {"file": "index.html", "sha256": sha(html_bytes), "selfContained": True},
               "tool": {"file": "tools/preview_study.py", "sha256": sha(Path(__file__).read_bytes())}}
    outputs[guarded_output(OUTPUT / "derived.json")] = encoded(derived)
    # Validate every output destination before the first mutation.
    for path in outputs:
        guarded_output(path)
        if path.exists() and not path.is_file():
            raise ValueError(f"Not a regular output file: {path}")
    if args.write:
        for path, data in outputs.items():
            guarded_output(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = guarded_output(path.with_name(path.name + ".tmp-" + uuid.uuid4().hex))
            try:
                temporary.write_bytes(data)
                os.replace(temporary, path)
            finally:
                if temporary.is_file():
                    temporary.unlink()
    print(json.dumps({"mode": "write" if args.write else "dry-run", "outputDirectory": str(OUTPUT),
                      "outputCount": len(outputs), "cropCount": len(records), "cropSizes": sorted({(r['width'], r['height']) for r in records}),
                      "apngCanvas": canvas, "normalCycleMs": 480, "slowCycleMs": 1920,
                      "boundaryOccupiedCells": [r['frame'] for r in records if r['boundaryAlphaGt8Pixels']],
                      "visualPassed": 0, "formalExported": 0, "clientIntegrated": False}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
