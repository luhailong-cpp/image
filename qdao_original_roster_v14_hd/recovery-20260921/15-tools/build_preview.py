#!/usr/bin/env python3
"""Inventory role 15 PNGs and rebuild its offline review HTML; never change PNGs.

Default:
  python 15-tools/build_preview.py
Optional derived previews (only complete, valid directions):
  python 15-tools/build_preview.py --derived
The runtime contract is 15-delivery-preview/runtime/{walk/<DIR>/01..16.png,idle/<DIR>.png}.
Run again after importing frames. SHA, dimensions and alpha checks are evidence of
the file contract only: they do not establish original generation or art approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "15-delivery-preview"
RUNTIME = PREVIEW / "runtime"
SIZE = (1024, 1024)
FRAME_MS = 30


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def inspect_png(path: Path) -> dict:
    relative = path.relative_to(PREVIEW).as_posix()
    result = {"path": relative, "exists": path.is_file(), "usable": False, "issues": []}
    if not result["exists"]:
        result["issues"].append("missing")
        return result
    result.update(sha256=sha256(path), bytes=path.stat().st_size)
    try:
        with Image.open(path) as image:
            image.load()
            result.update(format=image.format, dimensions=list(image.size), mode=image.mode)
            if image.format != "PNG":
                result["issues"].append("not-png")
            if image.size != SIZE:
                result["issues"].append("size-not-1024")
            if "A" not in image.getbands() and "transparency" not in image.info:
                result["issues"].append("no-alpha")
            alpha = image.convert("RGBA").getchannel("A")
            extrema = alpha.getextrema()
            result.update(alpha_extrema=list(extrema), alpha_bbox=alpha.getbbox())
            if extrema[0] == 255:
                result["issues"].append("no-transparent-pixels")
            if extrema[1] == 0:
                result["issues"].append("fully-transparent")
    except Exception as error:
        result["issues"].append("decode-error")
        result["error"] = str(error)
    result["usable"] = not result["issues"]
    return result


def inventory() -> dict:
    data = {
        "role": "15_water_dragon_scholar_boy",
        "label": "水龙书生",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "frame_ms": FRAME_MS,
        "walk_cycle_ms": 16 * FRAME_MS,
        "runtime_root": str(RUNTIME),
        "visual_acceptance": "not-evaluated-by-tool",
        "client_acceptance": "not-tested",
        "directions": {},
        "duplicate_sha_groups": [],
    }
    by_sha: dict[str, list[dict]] = {}
    for direction in DIRECTIONS:
        frames = [inspect_png(RUNTIME / "walk" / direction / f"{n:02}.png") for n in range(1, 17)]
        idle = inspect_png(RUNTIME / "idle" / f"{direction}.png")
        data["directions"][direction] = {"walk": frames, "idle": idle}
        for frame in [*frames, idle]:
            if frame.get("sha256"):
                by_sha.setdefault(frame["sha256"], []).append(frame)
    # Identical bytes across slots cannot count as independent action frames.
    for digest, frames in by_sha.items():
        if len(frames) > 1:
            data["duplicate_sha_groups"].append({"sha256": digest, "paths": [x["path"] for x in frames]})
            for frame in frames:
                frame["issues"].append("duplicate-sha256")
                frame["usable"] = False
    all_walk = [frame for entry in data["directions"].values() for frame in entry["walk"]]
    all_idle = [entry["idle"] for entry in data["directions"].values()]
    data["counts"] = {
        "walk_present": sum(x["exists"] for x in all_walk),
        "walk_file_contract_valid": sum(x["usable"] for x in all_walk),
        "idle_present": sum(x["exists"] for x in all_idle),
        "idle_file_contract_valid": sum(x["usable"] for x in all_idle),
        "walk_expected": 128,
        "idle_expected": 8,
    }
    return data


def derive_previews(data: dict) -> None:
    """Create labeled contact sheets and 30ms GIFs; record every source SHA.

    Preview resizing is display-only; these files never enter runtime. No GIF is
    exported for a direction with missing/invalid/duplicate slots. Runtime input
    content is checked against the captured inventory before and after export.
    """
    destination = PREVIEW / "derived"
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_at_utc": data["generated_at_utc"],
        "purpose": "derived-review-only-not-runtime-or-art-approval",
        "frame_ms": FRAME_MS,
        "exports": [],
        "skipped": [],
    }
    for direction, entry in data["directions"].items():
        frames = entry["walk"]
        if not all(frame["usable"] for frame in frames):
            manifest["skipped"].append({"direction": direction, "reason": "incomplete-or-invalid-walk"})
            continue
        sources = [{"path": x["path"], "sha256": x["sha256"]} for x in frames]
        for source in sources:
            if sha256(PREVIEW / source["path"]) != source["sha256"]:
                raise RuntimeError(f"Source changed during inventory: {source['path']}")
        rgba_frames = []
        for source in sources:
            with Image.open(PREVIEW / source["path"]) as im:
                rgba_frames.append(im.convert("RGBA"))
        for background, rgb in (("light", (242, 235, 214)), ("dark", (26, 40, 48))):
            composited = []
            for im in rgba_frames:
                view = Image.new("RGBA", SIZE, (*rgb, 255))
                view.alpha_composite(im)
                composited.append(view.convert("RGB").resize((256, 256), Image.Resampling.LANCZOS))
            sheet = Image.new("RGB", (4 * 256, 4 * 282), rgb)
            draw = ImageDraw.Draw(sheet)
            text_color = "#23352d" if background == "light" else "#f5eddb"
            for n, view in enumerate(composited):
                x, y = (n % 4) * 256, (n // 4) * 282
                sheet.paste(view, (x, y))
                draw.text((x + 8, y + 260), f"{direction} {n + 1:02}", fill=text_color)
            sheet_path = destination / f"{direction}-16frames-{background}.png"
            sheet.save(sheet_path)
            seam = Image.new("RGB", (4 * 256, 282), rgb)
            seam_draw = ImageDraw.Draw(seam)
            for col, n in enumerate((14, 15, 0, 1)):
                seam.paste(composited[n], (col * 256, 0))
                seam_draw.text((col * 256 + 8, 260), f"{direction} {n + 1:02}", fill=text_color)
            seam_path = destination / f"{direction}-seam-15-16-01-02-{background}.png"
            seam.save(seam_path)
            gif_path = destination / f"{direction}-walk-30ms-{background}.gif"
            composited[0].save(gif_path, save_all=True, append_images=composited[1:],
                               duration=FRAME_MS, loop=0, disposal=2, optimize=False)
            # GIF may collapse byte-identical display frames. Do not misreport a
            # 16-frame 480ms export when the encoder changed the timing structure.
            with Image.open(gif_path) as gif:
                durations = []
                for n in range(gif.n_frames):
                    gif.seek(n)
                    durations.append(gif.info.get("duration"))
            timing_valid = len(durations) == 16 and durations == [FRAME_MS] * 16
            for path, kind in ((sheet_path, "contact-sheet"), (seam_path, "seam-sheet"), (gif_path, "gif")):
                export = {"path": path.relative_to(PREVIEW).as_posix(), "sha256": sha256(path),
                          "kind": kind, "sources": sources, "background": background,
                          "display_resizing_only": True}
                if kind == "gif":
                    export.update(encoded_frame_ms=durations, timing_contract_valid=timing_valid)
                manifest["exports"].append(export)
        for source in sources:
            if sha256(PREVIEW / source["path"]) != source["sha256"]:
                raise RuntimeError(f"Source changed during preview build: {source['path']}")
    (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>15 水龙书生 · 离线动作审阅</title>
<style>
:root{font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif;color:#253e38;background:#f0eadc;--line:#ceba89;--paper:#fffaf0;--jade:#246154;--stage:#f2ebd6}
*{box-sizing:border-box}body{margin:0}main{max-width:1440px;margin:auto;padding:24px}h1{font-size:25px;margin:0;color:#1d5045}h2{font-size:18px;margin:0 0 10px}p{margin:6px 0}.subtle{color:#66756a;font-size:13px}.panel{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:18px;margin:16px 0;box-shadow:0 4px 16px #594b2310}.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center}label{display:flex;gap:6px;align-items:center}button,select,input{font:inherit}button,select{border:1px solid #bbae88;background:#f8f0dc;border-radius:9px;padding:7px 12px;color:#25483e}button{cursor:pointer}button:hover{border-color:#246154}button.primary,button[aria-pressed=true]{background:var(--jade);color:white}button:disabled{opacity:.45;cursor:not-allowed}.warning{color:#973d24;background:#fff1da;border-left:4px solid #ba7851;padding:10px 14px}.summary{font-weight:600}.view-area{overflow:auto;max-height:1180px;margin-top:16px}.stage{position:relative;width:256px;height:256px;margin:auto;background:var(--stage);background-image:linear-gradient(45deg,#87988c15 25%,transparent 25%),linear-gradient(-45deg,#87988c15 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#87988c15 75%),linear-gradient(-45deg,transparent 75%,#87988c15 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}.stage img{display:block;width:100%;height:100%;object-fit:contain}.stage.large{width:1024px;height:1024px}.empty{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;white-space:pre-wrap;color:#9b4e37;background:#f6eadbe8;padding:12px;font-size:13px}.hidden{display:none!important}.stage:after{content:"";position:absolute;inset:0;border:1px solid #9b9c8880;pointer-events:none}.phasebar{display:flex;gap:5px;flex-wrap:wrap;margin-top:12px}.phasebar button{padding:4px 11px}.phasebar .missing{border-style:dashed;color:#a65b41}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}.card{border:1px solid #d7c8a9;border-radius:10px;padding:10px;overflow:hidden}.card .stage{width:min(100%,256px);height:auto;aspect-ratio:1}.card-title{display:flex;justify-content:space-between;margin-bottom:6px}.badge{font-size:12px;color:#836c44}.filmstrip{display:grid;grid-template-columns:repeat(4,minmax(220px,1fr));gap:10px;overflow:auto}.filmstrip .stage{width:100%;height:auto;aspect-ratio:1}.filmstrip>div{min-width:220px}details{margin:8px 0}summary{cursor:pointer}pre{white-space:pre-wrap;word-break:break-word;font:12px/1.5 ui-monospace,Consolas,monospace;max-height:480px;overflow:auto}.review-list{display:flex;flex-wrap:wrap;gap:8px 20px}.review-list label{font-size:14px}.monospace{font-family:ui-monospace,Consolas,monospace}@media(max-width:650px){main{padding:12px}.panel{padding:12px}.filmstrip{grid-template-columns:repeat(4,220px)}}
</style></head><body><main>
<h1>水龙书生 · 八方向动作审阅</h1>
<p class="subtle">15_water_dragon_scholar_boy · 独立离线预览 · 1024 × 1024 透明 PNG</p>
<div class="panel"><p id="counts" class="summary"></p><p id="inventoryWarning" class="warning"></p>
<p>正常行走目标 <strong>30 毫秒 / 帧 · 16 帧 · 480 毫秒 / 圈</strong>。按单调时钟选择相位；浏览器刷新率和后台调度可能跳过显示相位，不代表每帧实际呈现均为 30 毫秒。</p>
<p class="subtle">文件数量、尺寸、Alpha 与 SHA 只是文件核查。真实交替迈腿、支撑脚、身份、比例、脚底锚点、残边和首尾衔接需要逐帧审阅。此页面不自动给出美术通过，也不代表 Unity 或正式客户端验收。</p>
<p id="buildTime" class="subtle"></p></div>
<section class="panel"><div class="toolbar">
<label>方向 <select id="direction"></select></label><label>动作 <select id="mode"><option value="walk">行走 16 帧</option><option value="idle">独立站立</option></select></label>
<button id="play" class="primary">播放</button><button id="previous">上一帧</button><button id="next">下一帧</button>
<label>背景 <select id="background"><option value="light">浅色底</option><option value="dark">深色底</option></select></label>
<label>显示 <select id="zoom"><option value="normal">正常 256 px</option><option value="large">放大 1024 px</option></select></label>
<button id="seam" aria-pressed="false">只看接缝 15 → 16 → 01 → 02</button></div>
<p id="playStatus" role="status"></p><div id="phasebar" class="phasebar"></div>
<div class="view-area"><div id="mainStage" class="stage"><img id="mainImage" alt="当前帧"><div id="mainEmpty" class="empty"></div></div></div>
<p id="frameEvidence" class="subtle monospace"></p>
</section>
<section class="panel"><h2>八方向同步相位</h2><p class="subtle">使用相同相位查看各方向。缺少任何行走帧的方向暂停显示检查项，不缩短循环、不重复已有图片补齐。</p><div id="overview" class="grid"></div></section>
<section class="panel"><h2>当前方向首尾接缝</h2><p class="subtle">固定顺序 15 → 16 → 01 → 02；此处保持四张静态图便于检查。主视图可切换接缝循环，接缝循环为 120 毫秒。</p><div id="filmstrip" class="filmstrip"></div></section>
<section class="panel"><h2>审阅提示</h2><div class="review-list">
<span>□ 左右腿真实交替</span><span>□ 支撑脚与脚底锚点</span><span>□ 身体比例与身份</span><span>□ 深浅底透明残边</span><span>□ 正常与 1024 px 放大</span><span>□ 15 → 16 → 01 → 02 衔接</span><span>□ 八张独立站立</span>
</div><p class="subtle">此清单为检查提示，不保存为验收结果。请在角色交接记录中写明实际看过的方向、帧号、问题与结论。</p>
<details><summary>使用说明与来源边界</summary><p>将实际交付图导入 runtime/walk/方向/01.png 至 16.png，以及 runtime/idle/方向.png 后，重新运行 15-tools/build_preview.py，再重新打开此文件。无需联网或启动服务器。方向固定 N、NE、E、SE、S、SW、W、NW。</p><p>空库、缺帧、尺寸或 Alpha 不合格及完全相同 SHA 的动作槽均单独报出；不以其他方向、站立图、镜像或已有相位替补。图片重新导入后必须重建清单；浏览器无法自行保证本页内嵌 SHA 与后来改动文件一致。</p><p>按空格播放或暂停，左右箭头逐帧。可选 --derived 输出深浅底 16 帧联系表、接缝联系表和 30 ms GIF，并把每个派生文件及其原图 SHA 写入 derived/manifest.json。派生缩略图仅供审阅，不进入 runtime。</p></details>
<details><summary>库存、尺寸、Alpha、SHA 与缺帧清单</summary><pre id="manifest"></pre></details></section>
</main>
<script id="inventory" type="application/json">__INVENTORY__</script>
<script>
'use strict';
const data = JSON.parse(document.getElementById('inventory').textContent);
const dirs = Object.keys(data.directions);
const $ = id => document.getElementById(id);
const images = new Map();
const failures = new Set();
let dir = 'S', mode = 'walk', playing = false, seam = false, position = 0, origin = performance.now(), ready = false;
const sequence = () => seam ? [14,15,0,1] : Array.from({length:16}, (_,i)=>i);
const currentFrame = () => sequence()[position];
const records = Object.values(data.directions).flatMap(d => [...d.walk, d.idle]);
const why = record => record.issues.join(', ') || (failures.has(record.path) ? 'browser-load-failed' : '');
const good = record => record.usable && !failures.has(record.path);
const complete = d => data.directions[d].walk.every(good);
const currentRecord = () => mode === 'idle' ? data.directions[dir].idle : data.directions[dir].walk[currentFrame()];
function show(img, empty, record, extra) {
  if (!good(record) || extra) {
    img.classList.add('hidden'); img.removeAttribute('src'); delete img.dataset.path; empty.classList.remove('hidden');
    empty.textContent = extra || (record.exists ? '文件待处理\n'+why(record) : '缺少图片\n'+record.path);
  } else {
    if (img.dataset.path !== record.path) { img.src = record.path; img.dataset.path = record.path; }
    img.classList.remove('hidden'); empty.classList.add('hidden');
  }
}
function card(parent, id, title) {
  const element=document.createElement('div'); element.className='card';
  const heading=document.createElement('div'); heading.className='card-title'; heading.textContent=title;
  const status=document.createElement('span'); status.id=id+'Status'; status.className='badge'; heading.append(status);
  const stage=document.createElement('div'); stage.className='stage';
  const img=document.createElement('img'); img.id=id+'Image'; img.alt=title;
  const empty=document.createElement('div'); empty.id=id+'Empty'; empty.className='empty';
  stage.append(img,empty); element.append(heading,stage); parent.append(element);
}
dirs.forEach(d => { const option=document.createElement('option');option.value=d;option.textContent=d;$('direction').append(option);card($('overview'),'overview'+d,d); });
$('direction').value=dir;
[14,15,0,1].forEach((n,i)=>card($('filmstrip'),'seam'+i,String(n+1).padStart(2,'0')));
for(let n=0;n<16;n++) {const b=document.createElement('button');b.textContent=String(n+1).padStart(2,'0');b.title='查看第 '+(n+1)+' 帧';b.onclick=()=>{playing=false;seam=false;position=n;render();};$('phasebar').append(b);}
function render() {
  const frame=currentFrame(), record=currentRecord();
  const canPlay=ready && mode==='walk' && complete(dir);
  if (!canPlay) playing=false;
  $('play').disabled=!canPlay;$('play').textContent=playing?'暂停':'播放';
  $('previous').disabled=mode==='idle';$('next').disabled=mode==='idle';$('seam').disabled=mode==='idle';
  $('seam').setAttribute('aria-pressed',String(seam));
  $('phasebar').classList.toggle('hidden',mode==='idle');
  [...$('phasebar').children].forEach((b,n)=>{b.setAttribute('aria-pressed',String(n===frame));b.classList.toggle('missing',!good(data.directions[dir].walk[n]));});
  show($('mainImage'),$('mainEmpty'),record);
  const stage=mode==='idle'?'独立站立':`第 ${String(frame+1).padStart(2,'0')} / 16 帧`;
  const transport=mode==='idle'?'静态检查':!ready?'正在验证图片读取':!complete(dir)?'库存不齐或存在文件问题，循环已锁定':playing?'播放中':'已暂停';
  $('playStatus').textContent=`${dir} · ${stage} · ${transport}`+(mode==='walk'?` · ${seam?'接缝 4 帧 / 120 ms':'完整 16 帧 / 480 ms'} · 30 ms/帧`:'');
  $('frameEvidence').textContent=record.path+(record.sha256?' · SHA256 '+record.sha256:' · missing');
  dirs.forEach(d=>{const r=mode==='idle'?data.directions[d].idle:data.directions[d].walk[frame];
    const ok=mode==='idle'?good(r):complete(d);const count=data.directions[d].walk.filter(good).length;
    $('overview'+d+'Status').textContent=mode==='idle'?(ok?'站立':'缺失/待处理'):`${count}/16 · ${String(frame+1).padStart(2,'0')}`;
    show($('overview'+d+'Image'),$('overview'+d+'Empty'),r,ok?'':mode==='walk'?`${d} ${count}/16 可读合规帧\n整组循环未启用`:undefined);});
  [14,15,0,1].forEach((n,i)=>show($('seam'+i+'Image'),$('seam'+i+'Empty'),data.directions[dir].walk[n]));
}
function pause(){playing=false;render();}
function togglePlay(){if(mode!=='walk'||!ready||!complete(dir))return;playing=!playing;if(playing)origin=performance.now()-position*30;render();}
function step(delta){playing=false;const seq=sequence();position=(position+delta+seq.length)%seq.length;render();}
$('play').onclick=togglePlay;$('previous').onclick=()=>step(-1);$('next').onclick=()=>step(1);
$('direction').onchange=e=>{dir=e.target.value;playing=false;position=0;render();};
$('mode').onchange=e=>{mode=e.target.value;playing=false;position=0;render();};
$('seam').onclick=()=>{playing=false;seam=!seam;position=0;render();};
$('background').onchange=e=>document.documentElement.style.setProperty('--stage',e.target.value==='dark'?'#1a2830':'#f2ebd6');
$('zoom').onchange=e=>$('mainStage').classList.toggle('large',e.target.value==='large');
document.addEventListener('keydown',e=>{if(['SELECT','INPUT','BUTTON','TEXTAREA'].includes(document.activeElement.tagName))return;
  if(e.code==='Space'){e.preventDefault();togglePlay();}else if(e.code==='ArrowRight'){e.preventDefault();step(1);}else if(e.code==='ArrowLeft'){e.preventDefault();step(-1);}});
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
function tick(now){if(playing){const phase=Math.floor((now-origin)/30)%sequence().length;if(phase!==position){position=phase;render();}}requestAnimationFrame(tick);}
const c=data.counts;
$('counts').textContent=`行走：${c.walk_present} / 128 文件，${c.walk_file_contract_valid} 通过文件核查；独立站立：${c.idle_present} / 8 文件，${c.idle_file_contract_valid} 通过文件核查。`;
$('inventoryWarning').textContent=c.walk_file_contract_valid===128&&c.idle_file_contract_valid===8?'文件合同已齐；美术审阅结论仍须由实际检查单独记录。':'库存未齐或存在文件问题：不能视为完成，也不能重复已有帧补齐。详见底部库存清单。';
$('buildTime').textContent='库存快照 UTC：'+data.generated_at_utc+'。导入或更换任何图片后请重建预览。';
$('manifest').textContent=JSON.stringify(data,null,2);
render();requestAnimationFrame(tick);
Promise.all(records.filter(r=>r.usable).map(r=>new Promise(resolve=>{const img=new Image();images.set(r.path,img);
  img.onload=()=>{if(img.naturalWidth!==1024||img.naturalHeight!==1024)failures.add(r.path);resolve();};img.onerror=()=>{failures.add(r.path);resolve();};img.src=r.path;
}))).then(()=>{ready=true;if(failures.size){$('inventoryWarning').textContent+=' 浏览器读取失败或尺寸变化：'+[...failures].join('、');}render();});
</script></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derived", action="store_true", help="also write review contact sheets, GIFs and SHA manifest")
    args = parser.parse_args()
    data = inventory()
    encoded = json.dumps(data, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    PREVIEW.mkdir(parents=True, exist_ok=True)
    target = PREVIEW / "index.html"
    target.write_text(HTML.replace("__INVENTORY__", encoded), encoding="utf-8")
    if args.derived:
        derive_previews(data)
    print(json.dumps({"html": str(target), "counts": data["counts"],
                      "visual_acceptance": data["visual_acceptance"],
                      "derived_requested": args.derived}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
